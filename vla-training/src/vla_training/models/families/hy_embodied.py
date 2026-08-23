"""Hy-Embodied-0.5-VLA adapter.

Wraps the Tencent HY-Embodied model (HuggingFace: ``tencent/HY-Embodied-0.5``)
behind the standard :class:`ModelAdapter` interface.

Architecture notes
------------------
HY-Embodied-0.5 uses a Mixture-of-Transformers (MoT) backbone with a VLM core
fine-tuned for action prediction.  The HuggingFace checkpoint exposes:

* ``AutoModelForVision2Seq`` -- loads the VLM + action head.
* A processor that handles image tokenisation and text encoding.

The exact class names may differ across checkpoint versions; set
``model.trust_remote_code: true`` in the config when the checkpoint ships
custom modelling code.

Reference
~~~~~~~~~
- HuggingFace: https://huggingface.co/tencent/HY-Embodied-0.5
- GitHub:      https://github.com/Tencent-Hunyuan/HY-Embodied
- Paper:       https://arxiv.org/abs/2604.07430
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Mapping

from ..adapter import ModelAdapter, register_adapter

logger = logging.getLogger(__name__)


class HyEmbodiedAdapter(ModelAdapter):
    """Adapter for the Hy-Embodied-0.5-VLA model family.

    Config keys consumed (under ``model``):

    * ``base_model`` -- HuggingFace repo id or local path.
    * ``trust_remote_code`` -- forward to ``from_pretrained``.
    * ``load_in_4bit`` -- enable QLoRA 4-bit quantisation.
    * ``action_key`` -- name of the action output attribute (default
      ``"action"``).  Adjust if the checkpoint uses a different key.
    """

    FAMILY = "hy_embodied"

    # --- construction ------------------------------------------------------

    def __init__(self, config: Mapping[str, Any]) -> None:
        model, processor = _load_model_and_processor(config)
        super().__init__(model, processor, config)
        self._action_key = str(
            config.get("model", {}).get("action_key", "actions")
        )

    # --- ModelAdapter interface --------------------------------------------

    def preprocess_batch(self, batch: dict[str, Any], device: str) -> dict[str, Any]:
        """Prepare a collated batch for the HY-Embodied forward pass.

        The dataset returns ``images`` as a dict of camera tensors, plus
        ``instruction``, ``joint_positions``, and ``actions``.  This method
        converts them into the kwargs the model expects.
        """
        import torch

        images = {}
        for cam, imgs in batch["images"].items():
            t = imgs.to(device) if isinstance(imgs, torch.Tensor) else imgs
            images[cam] = t

        # Tokenize instructions.
        instructions = list(batch["instruction"])
        if self.processor is not None and hasattr(self.processor, "tokenizer"):
            tok = self.processor.tokenizer
            text_enc = tok(
                instructions,
                padding=True,
                truncation=True,
                max_length=int(self.config.get("instruction", {}).get("max_length", 64)),
                return_tensors="pt",
            ).to(device)
        else:
            text_enc = {"input_ids": None}

        model_inputs: dict[str, Any] = {
            "pixel_values": images,
            "input_ids": text_enc.get("input_ids"),
            "attention_mask": text_enc.get("attention_mask"),
            "joint_positions": batch["joint_positions"].to(device),
        }

        result: dict[str, Any] = {"model_inputs": model_inputs}
        if "actions" in batch:
            result["ground_truth_actions"] = batch["actions"].to(device)
        return result

    def compute_loss(self, batch: dict[str, Any], device: str) -> Any:
        """Forward pass returning a scalar MSE loss on predicted actions."""
        import torch

        prepared = self.preprocess_batch(batch, device)
        model_inputs = prepared["model_inputs"]
        outputs = self.model(**model_inputs)

        pred = _extract_actions(outputs, self._action_key)
        target = prepared["ground_truth_actions"]
        return torch.nn.functional.mse_loss(pred, target)

    def predict_actions(self, batch: dict[str, Any], device: str) -> Any:
        prepared = self.preprocess_batch(batch, device)
        model_inputs = prepared["model_inputs"]
        outputs = self.model(**model_inputs)
        return _extract_actions(outputs, self._action_key)

    def merge_adapters(self, export_dir: Any) -> None:
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        if hasattr(self.model, "save_pretrained"):
            self.model.save_pretrained(export_dir)
            logger.info("merged and saved to %s", export_dir)
        else:
            logger.warning(
                "model %s has no save_pretrained; skipping adapter merge",
                type(self.model).__name__,
            )


# --- helpers ---------------------------------------------------------------


def _load_model_and_processor(config: Mapping[str, Any]) -> tuple[Any, Any]:
    """Load the HY-Embodied checkpoint and its processor."""
    from ..loader import ModelLoadError

    base_model = str(config.get("model", {}).get("base_model", ""))
    if not base_model:
        raise ModelLoadError("model.base_model is required")

    trust_remote = bool(config.get("model", {}).get("trust_remote_code", True))
    load_in_4bit = bool(config.get("model", {}).get("load_in_4bit", False))

    logger.info("loading Hy-Embodied model: %s (4bit=%s)", base_model, load_in_4bit)

    try:
        from transformers import AutoModelForVision2Seq, AutoProcessor
    except ImportError as exc:
        raise ModelLoadError(
            "transformers is required; install vla-training/requirements.txt"
        ) from exc

    model_kwargs: dict[str, Any] = {"trust_remote_code": trust_remote}
    if load_in_4bit:
        try:
            from transformers import BitsAndBytesConfig

            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype="bfloat16",
                bnb_4bit_quant_type="nf4",
            )
        except ImportError:
            logger.warning("bitsandbytes not installed; falling back to full precision")

    try:
        model = AutoModelForVision2Seq.from_pretrained(base_model, **model_kwargs)
        processor = AutoProcessor.from_pretrained(base_model, trust_remote_code=trust_remote)
    except Exception as exc:
        raise ModelLoadError(
            f"failed to load Hy-Embodied checkpoint '{base_model}': {exc}. "
            f"Ensure the weights are downloaded to ~/.cache/huggingface or "
            f"provide a local path."
        ) from exc

    logger.info("Hy-Embodied model loaded: %s", type(model).__name__)
    return model, processor


def _extract_actions(outputs: Any, action_key: str) -> Any:
    """Pull the action tensor out of a model output object or dict."""
    if isinstance(outputs, dict):
        if action_key in outputs:
            return outputs[action_key]
        raise KeyError(
            f"action key '{action_key}' not in model output keys: {list(outputs)}"
        )
    # HuggingFace model outputs are usually named tuples / dataclasses.
    for attr in (action_key, "actions", "action", "logits"):
        if hasattr(outputs, attr):
            return getattr(outputs, attr)
    raise AttributeError(
        f"could not find actions in model output (tried '{action_key}', "
        f"'actions', 'action', 'logits')"
    )


# --- registration ----------------------------------------------------------

register_adapter(HyEmbodiedAdapter.FAMILY, HyEmbodiedAdapter)

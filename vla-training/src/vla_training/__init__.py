"""VLA fine-tuning workspace for the loading/unloading robot.

**This package is a skeleton.** Interfaces, config schema and the data pipeline
shape are defined and importable; the heavy lifting (actual forward/backward
passes, weight downloads) is marked with ``NotImplementedError`` so the missing
pieces are explicit rather than silently wrong.

Pipeline::

    collector  ->  converter  ->  dataset  ->  finetune  ->  evaluate  ->  export
    (sim/real)     (episodes)     (torch)      (LoRA)       (metrics)    (robot)

Downstream consumer: ``robot-app``'s ``robot_decision`` package loads whatever
:mod:`vla_training.export.to_inference` produces.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]

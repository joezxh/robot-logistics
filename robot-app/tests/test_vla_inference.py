import numpy as np
import pytest

def test_inference_engine_scripted():
    """VLAInferenceEngine with ScriptedPolicy"""
    from rcs_layer.vla.inference_engine import VLAInferenceEngine
    
    engine = VLAInferenceEngine(action_dim=6)
    obs = {"state": np.zeros(14)}
    action = engine.predict(obs)
    
    assert action.shape == (6,)
    assert isinstance(action, np.ndarray)


def test_inference_engine_reset():
    """VLAInferenceEngine reset()"""
    from rcs_layer.vla.inference_engine import VLAInferenceEngine
    
    engine = VLAInferenceEngine(action_dim=6)
    engine.reset()  # 不应抛出异常


def test_load_policy_scripted():
    """load_policy returns ScriptedPolicy when kind='scripted'"""
    from rcs_layer.vla.inference_engine import load_policy
    
    policy = load_policy(kind="scripted", action_dim=6)
    assert policy is not None
    obs = {"state": np.zeros(14)}
    action = policy(obs)
    assert action.shape == (6,)

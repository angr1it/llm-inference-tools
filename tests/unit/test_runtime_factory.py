from unittest.mock import MagicMock, patch

from llm_server.runtime import create_runtime


def test_create_runtime_llamacpp():
    with patch('llm_server.runtime.LlamaCppRuntime') as LR:
        instance = LR.return_value
        runtime = create_runtime('llama.cpp', '/m', '/c')
        LR.assert_called_once_with('/m', '/c', None, None)
        instance.prepare.assert_called_once()
        instance.load.assert_called_once()
        assert runtime is instance


def test_create_runtime_onnxruntime():
    with patch('llm_server.runtime.OnnxRuntime') as OR:
        instance = OR.return_value
        runtime = create_runtime('onnxruntime', '/m', '/c', ['a'], 'q4')
        OR.assert_called_once_with('/m', '/c', ['a'], 'q4')
        instance.prepare.assert_called_once()
        instance.load.assert_called_once()
        assert runtime is instance


def test_create_runtime_unknown():
    try:
        create_runtime('bad', '/m', '/c')
    except ValueError as exc:
        assert 'Unknown backend' in str(exc)
    else:
        assert False, 'ValueError not raised'

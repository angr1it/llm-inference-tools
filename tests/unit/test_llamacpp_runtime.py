from llm_server.runtime.llamacpp import LlamaCppRuntime


def test_gguf_path(tmp_path):
    r = LlamaCppRuntime('/m', tmp_path)
    assert r._gguf_path() == str(tmp_path / 'model.gguf')

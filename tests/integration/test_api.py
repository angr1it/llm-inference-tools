import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import importlib.util
from pathlib import Path


@pytest.mark.integration
def test_completions_simple():
    with patch('llm_server.runtime.create_runtime') as factory:
        runtime = Mock()
        runtime.generate_stream.return_value = iter(['ok'])
        factory.return_value = runtime
        spec = importlib.util.spec_from_file_location('llm_server.main', Path('llm-server/main.py'))
        main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main)
        client = TestClient(main.app)
        resp = client.post('/v1/chat/completions', json={'prompt': 'hi'})
        assert resp.status_code == 200
        assert resp.json()['choices'][0]['message']['content'] == 'ok'

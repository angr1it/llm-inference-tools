# LLM Inference Tools

This repository provides a minimal stack for experimenting with **Qwen 3 8B Reasoning** models. It offers two inference backends (`llama.cpp` and `ONNX Runtime`), a chat UI, support for LoRA adapters and services for collecting RLHF logs.

## Quick start

```bash
# copy configuration and adjust model paths or quantization parameters
cp .env.example .env

# build and start all services
docker compose up -d
```

- The chat UI will be available at `http://localhost:3000`.
- The OpenAI compatible API is served at `http://localhost:8000/v1`.

## Project structure

```
Dockerfile.llm         # image with llama.cpp and ONNX Runtime
Dockerfile.chat-ui     # image for LangChain Agent Chat UI
docker-compose.yml     # compose stack, exposes GPU
.env.example           # sample configuration

llm-server/            # FastAPI inference server
chat-ui/               # chat frontend
langfuse/              # tracing and metrics
labelstudio/           # annotation for RLHF
mcp/                   # helper tools
models/                # models and LoRA adapters
logs/                  # inference logs and scores
docs/                  # documentation (plan, requirements, structure, features)
```

For a step-by-step deployment guide and detailed requirements see the `docs/` directory.

### Development

Install the dev dependencies from `requirements-dev.txt` and run the pre-commit hooks before committing:

```bash
pip install -r requirements-dev.txt
pre-commit run --all-files
```

Run unit tests with `pytest`. Integration tests are skipped by default and can be executed with the `--runintegration` option:

```bash
pytest                 # unit tests
pytest --runintegration  # run integration tests as well
```

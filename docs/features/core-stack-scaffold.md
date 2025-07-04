# Feature Documentation: Core Stack Scaffold

---

## 0. Overview of current documentation
The `docs/` folder contains the main references for this project:
- **plan.md** — deployment plan for Qwen 3 8B and Docker compose examples.
- **requirements.md** — list of functional and technical requirements.
- **structure.md** — target repository structure and usage scenarios.
- **features/_template.md** — template for writing feature specs.

---

## 1. Context before the feature
The project lacked a ready-to-use layout and configuration, so users created folders and files on their own. This made it harder to run the models, the UI and the RLHF tools described in the requirements.

---

## 2. Feature goal
- **Problem**: no minimal repository skeleton that lets you immediately work with Qwen 3 8B in both inference modes, chat UI and helper services.
- **Goal**: create an initial template with the required directories, Dockerfiles and configuration in line with `requirements.md` and `structure.md`.
- A devcontainer with Jupyter is also required for training and saving LoRA adapters.
- **Success criteria**: after initialization the user can run inference (llama.cpp or ONNX Runtime), open the chat UI, collect RLHF logs and use the API with authorization.

---

## 3. Solution

### 3.1 Scope
- Minimal repository structure per `structure.md`.
- Stubs for `Dockerfile.llm`, `Dockerfile.chat-ui` and `docker-compose.yml`.
- Directories `llm-server`, `chat-ui`, `langfuse`, `labelstudio`, `mcp` and `scripts`.
- Example `.env` with `MODEL_PATH`, `RUNTIME_BACKEND`, `LORA_PATHS` and others.
- Minimal FastAPI server that toggles llama.cpp/onnxruntime and supports SSE.
- Template LangChain Agent Chat UI wired to the API.

### 3.2 Out-of-scope
- Actual model training or downloading large weights.
- Detailed implementation of MCP tools and VS Code extensions.

### 3.3 How it should work
- The user clones the repository with the prepared layout.
- Running `docker compose up -d` brings up `llm`, `chat-ui`, `langfuse`, `labelstudio` and `mcp`.
- `RUNTIME_BACKEND` in `.env` switches between llama.cpp and ONNX Runtime.
- Inference logs and scores are sent to Langfuse and saved in `/logs`.

### 3.4 Architectural changes
The feature creates the repository skeleton and example configs without touching business logic. Developers later fill the folders with code and extend the Dockerfiles.

---

## 4. Implementation plan
1. Create directories and files listed in `structure.md`.
2. Add `Dockerfile.llm`, `Dockerfile.chat-ui` and `docker-compose.yml` with basic configuration.
3. Provide `.env.example` with all variables from the requirements.
4. Add minimal server code in `llm-server/main.py` and an interface template in `chat-ui/`.
5. Update `README.md` with launch instructions.
6. Add pytest scaffolding with unit and integration folders and configure pre-commit to run unit tests and mypy.

## 5. Files to change
- `Dockerfile.llm` — **add**: image for llama.cpp and ONNX Runtime.
- `Dockerfile.chat-ui` — **add**: image for the LangChain Agent Chat UI.
- `docker-compose.yml` — **add**: run all services.
- `.env.example` — **add**: example configuration.
- `llm-server/main.py` — **add**: minimal FastAPI server.
- `chat-ui/` — **add**: basic interface.

---

## 6. Potential risks
| Risk | Probability | Impact | Plan |
|------|-------------|-------|------|
| User might overwrite existing files by accident | Low | Medium | Documentation warns about overwriting |
| No GPU available causing launch errors | Medium | Low | Provide a `--cpu-only` option in compose and docs |

---

## 7. Testing plan

### 7.1 Unit tests
Test utilities and server functions responsible for loading the model and selecting the runtime. These run with plain `pytest`.

### 7.2 Integration tests
`docker compose up` in a test directory, check API and UI availability. They are marked with `@pytest.mark.integration` and run with `pytest --runintegration`.

### 7.3 Acceptance scenarios
```gherkin
Scenario: User deploys the minimal stack
  Given an empty directory
  When the user runs "docker compose up -d"
  Then the llm and chat-ui services respond to requests
```

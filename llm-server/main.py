import json
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .runtime import create_runtime

app = FastAPI()

BACKEND = os.getenv("RUNTIME_BACKEND", "llama.cpp")
MODEL_PATH = os.getenv("MODEL_PATH", "/models")
CACHE_DIR = os.getenv("MODEL_CACHE", MODEL_PATH)
LORA_PATHS = [p for p in os.getenv("LORA_PATHS", "").split(",") if p]
QUANTIZE = os.getenv("QUANTIZE")

runtime = create_runtime(BACKEND, MODEL_PATH, CACHE_DIR, LORA_PATHS, QUANTIZE)


@app.post("/v1/chat/completions")
async def completions(payload: dict):
    prompt = payload.get("prompt") or payload.get("messages", [{}])[-1].get("content", "")
    stream = payload.get("stream", False)
    if stream:
        async def streamer():
            for tok in runtime.generate_stream(prompt):
                yield f"data: {json.dumps({'choices':[{'delta':{'content':tok}}]})}\n\n"
        return StreamingResponse(streamer(), media_type="text/event-stream")
    text = "".join(runtime.generate_stream(prompt))
    return {"choices": [{"message": {"content": text}}]}

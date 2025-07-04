from fastapi import FastAPI

app = FastAPI()

@app.post("/tool_call")
async def tool_call(payload: dict):
    # Echo payload for demo purposes
    return {"result": payload}

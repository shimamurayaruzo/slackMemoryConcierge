from fastapi import FastAPI, Request

from app.slack_bot import slack_handler

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/slack/events")
async def slack_events(request: Request):
    return await slack_handler.handle(request)

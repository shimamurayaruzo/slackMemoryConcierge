from fastapi import FastAPI, Request

from app.slack_bot import slack_handler, slack_env_ready

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/slack/events")
async def slack_events(request: Request):
    if not slack_handler or not slack_env_ready:
        return {"error": "Slack設定が未完了です。SLACK_BOT_TOKEN と SLACK_SIGNING_SECRET を設定してください。"}
    return await slack_handler.handle(request)

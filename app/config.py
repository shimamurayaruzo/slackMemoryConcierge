import os


class Settings:
    def __init__(self) -> None:
        self.slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
        self.google_drive_folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
        self.google_credentials_path = os.environ.get("GOOGLE_API_CREDENTIALS")
        self.memu_api_key = os.environ.get("MEMU_API_KEY")
        self.memu_team_id = os.environ.get("MEMU_TEAM_ID", "slack_team")
        self.memu_agent_id = os.environ.get("MEMU_AGENT_ID", "slack-doc-bot")
        self.port = int(os.environ.get("PORT", "8000"))


settings = Settings()

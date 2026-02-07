# Slackドキュメント回答Bot（slackMemoryConcierge）

Slackでの質問に対して、Google Driveの特定フォルダ配下にあるDocsから根拠付きで回答するBotです。決定事項・ToDoの記憶とFAQ自動育成をmemUで実装します。

## 必要環境

- Python 3.11+
- Slack App（Bot Token, Signing Secret）
- Google Service Account（Drive/Docs 読み取り権限）

## セットアップ

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 環境変数

.env.example を参考に設定してください。

主要項目:
- SLACK_BOT_TOKEN
- SLACK_SIGNING_SECRET
- GOOGLE_DRIVE_FOLDER_ID
- GOOGLE_API_CREDENTIALS
- MEMU_API_KEY
- MEMU_TEAM_ID
- MEMU_AGENT_ID

## 起動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Slack App 設定（最小）

- Event Subscriptions: On
- Request URL: https://<your-domain>/slack/events
- Subscribe to bot events: app_mention
- OAuth Scopes (Bot Token):
  - app_mentions:read
  - chat:write

## Google Service Account

- Drive/Docsの読み取り権限を付与
- 対象フォルダをService Accountのメールアドレスに共有

## Render へのデプロイ例

1. GitHubにリポジトリをPush
2. Render で New Web Service を作成
3. Build Command: pip install -r requirements.txt
4. Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
5. 環境変数を設定
6. 公開URLをSlack AppのRequest URLに設定

## スリープ回避（軽量）

- GitHub Actionsのkeepaliveを使って /health を15分ごとにping
- リポジトリ設定 → Variables に KEEPALIVE_URL を追加
  - 例: https://slackmemoryconcierge.onrender.com

## memUでの記憶

- 決定事項・ToDoは「category=decisions」として保存
- FAQは「category=faq」として保存
- Slackで「前回の宿題を覚えています」「これはFAQとして記憶しています」を返す

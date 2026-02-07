---
title: Render → Slack → Google Drive セットアップ手順（slackMemoryConcierge）
---

# 1. Render（先に公開URLを作る）

1. GitHubにこのリポジトリをpush
2. Renderで New Web Service を作成
3. Repositoryを選択
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment Variables に以下を設定
   - SLACK_BOT_TOKEN
   - SLACK_SIGNING_SECRET
   - GOOGLE_DRIVE_FOLDER_ID
   - GOOGLE_API_CREDENTIALS
   - MEMU_API_KEY
   - MEMU_TEAM_ID
   - MEMU_AGENT_ID
7. デプロイ後、公開URLを控える（例: `https://slackmemoryconcierge.onrender.com`）

# 2. Slack（公開URLを設定する）

1. Slack API で新規アプリを作成
2. OAuth & Permissions → Bot Token Scopes を追加
   - `app_mentions:read`
   - `chat:write`
3. Event Subscriptions を On
4. Request URL に `https://<RenderのURL>/slack/events` を設定
5. Subscribe to bot events に `app_mention` を追加
6. アプリをワークスペースにインストール

# 3. Google Drive（Docsを共有する）

1. Google CloudでService Accountを作成
2. Drive API / Docs API を有効化
3. Service AccountのJSONをダウンロード
4. 対象フォルダをService Accountのメールに共有
5. GOOGLE_DRIVE_FOLDER_ID に対象フォルダIDを設定
6. GOOGLE_API_CREDENTIALS にJSONの配置パスを設定

# 動作確認（最短）

Slackで以下を送信:

```
@slackMemoryConcierge 先週の定例の宿題は？
```

以下が返ればOK:
- 「前回の宿題を覚えています」
- Docsの引用リンク
- 抜粋

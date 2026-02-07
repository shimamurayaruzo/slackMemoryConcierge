---
title: MemU の概要と APIキーの取得・設定手順
---

# MemU とは

MemU は LLM アプリケーション向けの「エージェント記憶レイヤー」です。会話から重要情報（好み・ルール・事実など）を抽出して保存し、意味検索で素早く再利用できます。

- ベースURL: https://api.memu.so
- 認証: Authorization ヘッダに Bearer トークン（APIキー）を付与
- 代表的なエンドポイント:
  - POST /api/v3/memory/memorize: 会話から記憶抽出タスクを登録
  - GET /api/v3/memory/memorize/status/{task_id}: 抽出タスクの進捗確認
  - POST /api/v3/memory/categories: 記憶カテゴリの取得
  - POST /api/v3/memory/retrieve: 意味検索で記憶取得
  - POST /api/v3/memory/delete: 記憶の削除

# APIキーの発行（取得）方法

MemU の APIキーは MemU のダッシュボードで発行します。以下の手順で取得してください。

1. https://memu.pro にアクセスし、アカウントを作成・ログイン
2. ダッシュボードで API キー管理ページを開く
3. 新規キーを作成（表示されるキーを安全に保管）
   - キーは機密情報です。リポジトリにコミットしないでください

# Windows（PowerShell）での安全な設定方法

APIキーは環境変数 MEMU_API_KEY として設定するのが安全です。以下のいずれかの方法を利用します。

- セッション限定（現在のターミナルのみ有効）:
  
  $env:MEMU_API_KEY = "YOUR_API_KEY"

- ユーザー永続（次回以降の新しいターミナルでも有効）:
  
  setx MEMU_API_KEY "YOUR_API_KEY"
  
  注意: setx は「新しく開いた」プロセスから有効になります。既存のターミナルには反映されません。

# 使用例

以下は MEMU_API_KEY を環境変数から読み取り、MemU API を呼び出すシンプルな例です。

## Python

```python
import os
import requests

API_KEY = os.environ.get("MEMU_API_KEY")
BASE_URL = "https://api.memu.so"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# 記憶抽出タスクの登録
resp = requests.post(
    f"{BASE_URL}/api/v3/memory/memorize",
    headers=headers,
    json={
        "conversation": [
            {"role": "user", "content": "こんにちは"},
            {"role": "assistant", "content": "こんにちは！"},
            {"role": "user", "content": "私はコーヒーが好きです"},
        ],
        "user_id": "user_001",
        "agent_id": "assistant_001",
    },
)
print(resp.status_code, resp.json())
```

## Node.js

```js
import fetch from "node-fetch";

const API_KEY = process.env.MEMU_API_KEY;
const BASE_URL = "https://api.memu.so";

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json",
};

const res = await fetch(`${BASE_URL}/api/v3/memory/retrieve`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    user_id: "user_001",
    agent_id: "assistant_001",
    query: "ユーザーの好みは？",
  }),
});

console.log(await res.json());
```

# セキュリティの注意

- APIキーは共有しない・コードに直書きしない・公開リポジトリにコミットしない
- ログ出力やエラーメッセージにキーを含めない
- 必要に応じてキーのローテーションや失効を実施

# よくあるエラー

- 401 Unauthorized: APIキーが無い・不正
- 422 Validation Error: リクエストの形式や必須項目が不正
- 500 Server Error: サーバ側の問題。時間を置いて再試行

# 次のステップ

- 取得した APIキー を MEMU_API_KEY として設定
- 既存コードやツールから Authorization ヘッダで Bearer Token を付与
- 意味検索やカテゴリ取得等、プロダクトのフローに組み込み

# 識別子の扱い（MEMU_USER_ID / MEMU_TEAM_ID / MEMU_AGENT_ID）

- MEMU_USER_ID: ユーザー識別子。個人単位で記憶を分けたい場合に使用
- MEMU_TEAM_ID: チーム・ワークスペース等の共有識別子。UIで取得できない場合は「固定ID」を任意に決めて使っても良い
- MEMU_AGENT_ID: このアプリ（エージェント）を識別するためのID

本プロジェクトの設定では、MEMU_TEAM_ID が未設定の場合は MEMU_USER_ID を自動的に使用します（最終的に固定IDが必要なだけのため）。  
そのため、最低限 MEMU_API_KEY と MEMU_USER_ID、MEMU_AGENT_ID を用意すれば動作します。チーム共有をしたい場合は MEMU_TEAM_ID に正式なIDを設定してください。

## 環境変数設定例（Render / Windows）

必須:
- MEMU_API_KEY
- MEMU_USER_ID
- MEMU_AGENT_ID

任意（設定があれば優先使用、未設定なら上記の MEMU_USER_ID を使用）:
- MEMU_TEAM_ID

PowerShell例:

```
$env:MEMU_API_KEY = "xxxx"
$env:MEMU_USER_ID = "user_or_workspace_id"
$env:MEMU_AGENT_ID = "slack-doc-bot"
# 必要なら
$env:MEMU_TEAM_ID = "team_workspace_id"
```


---
title: Slackドキュメント回答Bot 要件定義（フォルダ検索型 v1.4）
---

# 背景・目的（Why）
- 社内・コミュニティの一次情報（Google Docsの議事録）が散在し、Slack上で同じ質問が繰り返されている
- Slackだけで「質問→根拠付き回答」を完結させ、過去の会話・参照資料を記憶して回答品質を継続的に向上させる
- ハッカソンテーマ「Vibe Coding with Memory」に適合し、記憶が価値になるプロダクトを最小構成で成立させる

# 対象ユーザー（Who）
- 現場担当者（手順確認）
- 経理担当者（ルール確認）
- 新人（FAQ代替）
- チーム全体（意思決定の再確認）

# 解決したい課題（Pain）
- 情報がDriveに埋もれる、Docsを探せない
- Slackで同じ質問が繰り返される、属人化
- 会話ログが流れて資産化されない、記憶が残らない

# 必須機能（Must）
- F1：Slackメンションで質問受付
  - Slack Events API（app_mention）を受信し、自然文の質問をハンドリングする
- F2：Google Driveフォルダ検索（特定フォルダ型）
  - 管理者が設定した対象フォルダID配下のGoogle Docsを列挙
  - files.listでタイトル・IDを取得、対象外ファイルはスキップ（対象MIME: Docs）
- F3：Docs本文抽出
  - Docs API（documents.get）で本文を抽出し検索コーパスを生成
- F4：回答生成（引用必須）
  - RAGで候補文書を検索し、回答には必ず「結論・根拠リンク・抜粋」を添付（Proof Answer）
- F5：memUによる長期記憶
  - 保存：過去質問、参照したDocs、返答内容、ユーザーの関心テーマ
  - 活用：次回質問で「前回の続きですね」「以前参照した◯◯資料ですね」を提示
- F6：決定事項・ToDoのチーム記憶
  - 議事録Docsの「決定事項 / ToDo / 宿題 / Action Items」セクションを抽出
  - memUに保存し、Slackで一覧照会できる
- F7：FAQ自動育成
  - 同じ質問が2回以上出たらFAQとしてmemUに保存
  - 「これはFAQとして記憶しています」と返せる
- F6：権限・ガバナンス
  - Slack OAuth scopesで最小権限、Drive共有設定に準拠したアクセス制御

# 追加機能（Want）
- W1：FAQ自動生成（よくある質問の提示）
- W2：管理者モード（対象フォルダ追加、NGワード設定、回答ログ確認）
- W3：Slackショートカット（/ask-doc、/policy）

# 入出力仕様
- 入力
  - Slackメッセージ（自然文）
  - ユーザーID、チャンネル情報
- 出力
  - 回答テキスト
  - 引用リンク（Google Docs URL）
  - 関連ドキュメント候補（必要に応じて）

# 例外ケース（Edge）
- 該当資料がない：見つからない旨＋再質問提案（例：キーワード候補）
- 権限がない文書：アクセスできない旨を返答
- 質問が曖昧：Botが追加質問でコンテキスト確認
- 同じ質問の繰り返し：過去回答を再提示し、必要なら更新

# 非機能要件（NFR）
- Slack内で完結するUX
- 目標応答時間：5秒以内（MVPは多少超過可）
- Drive文書は定期同期（バッチ）または問い合わせ時のオンデマンド取得
- 個人情報は保存しない（memUには質問/参照/回答のメタ情報のみ）

# アーキテクチャ（MVP最小）
- 推奨スタック：FastAPI + Slack Bolt（Python）
- フロー
  - Slack @mention
  - Query解析
  - memUで過去履歴検索
  - Driveフォルダ内Docs検索（files.list）
  - Docs本文抽出（documents.get）
  - 決定事項/FAQをmemUへ保存
  - LLM回答生成（Proof Answer: 結論＋根拠リンク＋抜粋）
  - memUへ保存（質問・参照・回答）
  - Slack返信

# 環境変数（例）
- SLACK_BOT_TOKEN / SLACK_SIGNING_SECRET
- GOOGLE_DRIVE_FOLDER_ID（特定フォルダ検索の対象）
- GOOGLE_API_CREDENTIALS（Service Account）
- MEMU_API_KEY（memU認証）
- MEMU_TEAM_ID / MEMU_AGENT_ID（memUの共有記憶キー）

# MVP当日完成範囲
- Slackで@bot質問受付
- Drive特定フォルダ配下のDocs 3件程度を対象
- 検索→回答（引用リンク必須）
- memUに質問履歴保存
- 決定事項/宿題の抽出と記憶
- FAQの自動記憶
- 次回質問で「覚えている」挙動を確認可能

# セキュリティ・ガバナンス
- OAuth scopesは最小限、監査ログを保持（回答ログは管理者が確認可能）
- Driveアクセスは共有設定に従う。無権限文書は常に除外
- APIキー等の秘密情報は環境変数で管理、リポジトリに含めない

# 将来拡張
- Sheets/PDF対応、Slides対応
- Slackログのバックアップ＋検索（conversations.history）
- FAQ自動生成、議事録からToDo抽出・アクション化

# 参考（MVPファイル構成）
- slack-drive-helper/
  - app/main.py（FastAPI起動）
  - app/slack_bot.py（Slack Boltイベント受信）
  - app/drive_loader.py（Driveフォルダ探索）
  - app/docs_reader.py（Docs本文抽出）
  - app/pdf_reader.py（PDF本文抽出）
  - app/rag_answer.py（回答生成・引用付与）
  - app/decision_extractor.py（決定事項/ToDo抽出）
  - app/faq_manager.py（FAQ登録ロジック）
  - app/slack_handlers.py（質問判定と回答フロー）
  - app/memu_client.py（memU保存・検索）
  - app/config.py（環境変数管理）

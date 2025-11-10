# アルファテスト デプロイメントガイド

## 📋 概要

このガイドでは、遊技機取扱主任者試験アプリのアルファ版をテスト公開する手順を説明します。

## 🎯 システム構成

- **フロントエンド**: React (Vite) - SPAアプリケーション
- **バックエンド**: Flask (Python) - API + 静的ファイル配信
- **認証**: SQLite + デバイスフィンガープリント
- **招待URL**: UUID トークンベースの1URL=1アカウント方式

## 🚀 デプロイ手順

### 1. デプロイ先の準備

本アプリは以下のプラットフォームに対応しています：

- **Railway** (推奨) - nixpacks.toml設定済み
- **Render**
- **Fly.io**
- その他のPython + Node.js対応プラットフォーム

### 2. 環境変数の設定

デプロイ先で以下の環境変数を設定してください：

```bash
PORT=5000                    # Flaskサーバーのポート（デフォルト5000）
FLASK_ENV=production         # 本番環境モード
```

### 3. Railwayへのデプロイ例

```bash
# 1. Railwayプロジェクト作成
railway init

# 2. リポジトリをリンク
railway link

# 3. デプロイ
railway up

# 4. デプロイ完了後、URLを確認
railway open
```

### 4. 招待URLの本番環境対応

デプロイが完了したら、招待URLファイルを本番ドメインに更新します：

```bash
# 例: Railwayのドメインが your-app-name.railway.app の場合
cd backend
sed -i 's|http://localhost:5173|https://your-app-name.railway.app|g' invite_urls_20251110_183335.txt

# macOSの場合
sed -i '' 's|http://localhost:5173|https://your-app-name.railway.app|g' invite_urls_20251110_183335.txt
```

### 5. 新しい招待URLの生成（必要に応じて）

本番環境のドメインで招待URLを生成し直す場合：

```bash
cd backend

# generate_invites.py の base_url を編集
# line 45: base_url = "https://your-app-name.railway.app/invite"

# 招待URL生成（例：30個）
python3 generate_invites.py 30
```

## 📤 テスターへの配布

### 配布方法

1. `backend/invite_urls_*.txt` ファイルを開く
2. テスター各自に1つのURLを配布
3. URLをクリックすると登録ページが開く

### テスター登録手順

1. 招待URLにアクセス
2. ユーザー名を入力（例：テスター001、田中太郎など）
3. 「登録して始める」ボタンをクリック
4. 登録完了後、自動的にホーム画面へ遷移

### 重要事項

- **1URL = 1デバイス**: 各招待URLは1台のデバイスにのみ紐付けられます
- **同一デバイスでの再アクセス**: 同じデバイスから同じURLにアクセスした場合は再登録可能
- **異なるデバイス**: 別のデバイスから同じURLにアクセスすると「既に使用済み」エラー

## 📊 テスト状況の監視

### 認証統計の確認

```bash
cd backend
python3 -c "from auth_database import AuthDatabase; db = AuthDatabase(); import json; print(json.dumps(db.get_stats(), indent=2, ensure_ascii=False))"
```

出力例：
```json
{
  "total_tokens": 23,
  "used_tokens": 5,
  "available_tokens": 18,
  "active_sessions": 5
}
```

### データベースの直接確認

```bash
cd backend
sqlite3 alpha_auth.db

# 招待トークン一覧
SELECT token, is_used, device_id, registered_at FROM invite_tokens;

# セッション一覧
SELECT session_token, device_id, last_access FROM user_sessions;

# 終了
.quit
```

## 🔧 トラブルシューティング

### 問題1: 招待URLにアクセスしても登録画面が表示されない

**原因**: SPAルーティング設定の問題

**解決策**:
- Railwayの場合、自動的に処理されます
- 他のプラットフォームの場合、すべてのルートで `index.html` を返すように設定

### 問題2: 「この招待URLは既に使用されています」エラー

**原因**: 別のデバイスで既に登録済み

**解決策**:
- テスターに新しい招待URLを配布
- または、同じデバイスから同じURLにアクセスするよう指示

### 問題3: デバイス登録後、リロードするとログアウトされる

**原因**: セッショントークンの保存/検証の問題

**解決策**:
- ブラウザのローカルストレージを確認（開発者ツール > Application > Local Storage）
- `session_token` と `device_id` が保存されているか確認

## 📈 現在の状態

- **総招待トークン数**: 23個
- **使用済みトークン数**: 1個
- **未使用トークン数**: 22個
- **アクティブセッション数**: 1個

## 🎓 アプリ機能

テスターが利用できる機能：

1. **ホーム画面**
   - 模擬試験の開始
   - 成績履歴の確認

2. **模擬試験**
   - 難易度選択（★, ★★, ★★★）
   - 問題数選択
   - 正誤判定
   - 解説表示

3. **成績履歴**
   - 過去の試験結果
   - 正答率の確認
   - 詳細レビュー

## 📝 フィードバック収集

テスターからのフィードバックを収集するための項目例：

1. 使いやすさ（1-5点）
2. 問題の質（1-5点）
3. 解説のわかりやすさ（1-5点）
4. バグ・エラーの有無
5. 改善提案
6. その他コメント

## 🔄 次のステップ

1. テスターに招待URLを配布
2. フィードバックを収集
3. バグ修正・改善実施
4. ベータ版リリースの準備
5. 正式公開

---

## 📞 サポート

問題が発生した場合は、以下の情報を収集してください：

- エラーメッセージのスクリーンショット
- ブラウザの種類とバージョン
- デバイス情報（PC/スマートフォン、OS）
- 操作手順の詳細

---

**最終更新**: 2025年11月10日
**バージョン**: Alpha 1.0

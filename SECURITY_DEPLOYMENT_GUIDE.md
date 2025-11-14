# セキュリティ修正 - 本番環境適用手順書

## 📋 概要

このドキュメントは、コミット `20bb4ae` で実装されたセキュリティ修正を本番環境に適用するための手順書です。

**修正日**: 2025年11月12日
**コミット**: `20bb4ae - security: Fix critical security vulnerabilities`

---

## 🚨 修正された脆弱性

### Critical (重大)
1. **認証バイパス** - 開発者モード (`token=dev`) がハードコードされており、誰でも認証をバイパス可能
2. **CORS無制限許可** - すべてのオリジンからのアクセスを許可しており、CSRF攻撃のリスク
3. **GitHub Pages認証スキップ** - ホスト名チェックのみで認証をスキップ可能

### High (高)
4. **セッション検証エラーの無視** - 検証失敗時もログアウトせず、無効なセッションでの操作を許可
5. **エラーメッセージの詳細情報漏洩** - スタックトレースや内部情報が攻撃者に露出

---

## 🔧 本番環境への適用手順

### ステップ 1: 環境変数の準備

#### 1.1 バックエンド環境変数

`backend/.env` ファイルを作成（存在しない場合）:

```bash
# 本番環境設定
DEV_MODE=false
ALLOWED_ORIGINS=https://your-actual-domain.com
```

**重要な設定値:**
- `DEV_MODE=false` - **必須**: 本番環境では必ず `false` に設定
  - `true` の場合、`token=dev` での認証バイパスが有効になります
  - 詳細なエラーメッセージが返されます（情報漏洩のリスク）

- `ALLOWED_ORIGINS` - **必須**: 実際のフロントエンドドメインを指定
  - カンマ区切りで複数指定可能: `https://domain1.com,https://domain2.com`
  - サブドメインも含める場合: `https://app.domain.com,https://www.domain.com`
  - **ワイルドカードは使用不可** - 具体的なドメインを指定

#### 1.2 フロントエンド環境変数

プロジェクトルートに `.env` ファイルを作成:

```bash
# 本番環境設定
VITE_DEV_MODE=false
VITE_API_URL=https://api.your-actual-domain.com
```

**重要な設定値:**
- `VITE_DEV_MODE=false` - **必須**: 本番環境では必ず `false` に設定
  - `true` の場合、認証検証がスキップされます

- `VITE_API_URL` - バックエンドAPIのURL
  - プロトコル (`https://`) を含めて指定
  - 末尾のスラッシュは不要

---

### ステップ 2: デプロイ前の検証

#### 2.1 ローカルで本番モードをテスト

```bash
# バックエンド
cd backend
export DEV_MODE=false
export ALLOWED_ORIGINS=http://localhost:5173
python3 api_server.py

# フロントエンド (別のターミナル)
cd ..
export VITE_DEV_MODE=false
export VITE_API_URL=http://localhost:5000
npm run build
npm run preview
```

#### 2.2 動作確認チェックリスト

- [ ] `token=dev` での認証が**拒否される**ことを確認
- [ ] 許可されていないオリジンからのリクエストが**拒否される**ことを確認
- [ ] セッション検証が正常に動作することを確認
- [ ] エラー発生時に詳細情報が**表示されない**ことを確認

```bash
# テスト用コマンド例
curl -X POST http://localhost:5000/api/auth/verify-invite \
  -H "Content-Type: application/json" \
  -d '{"token":"dev"}'

# 期待される結果: {"valid":false,"message":"サーバーエラーが発生しました"}
# DEV_MODE=true の場合のみ詳細なエラーメッセージが返される
```

---

### ステップ 3: 本番環境へのデプロイ

#### 3.1 環境変数の設定 (プラットフォーム別)

**Railway の場合:**
```bash
railway variables set DEV_MODE=false
railway variables set ALLOWED_ORIGINS=https://your-domain.com
railway variables set VITE_DEV_MODE=false
railway variables set VITE_API_URL=https://api.your-domain.com
```

**Heroku の場合:**
```bash
heroku config:set DEV_MODE=false
heroku config:set ALLOWED_ORIGINS=https://your-domain.com
heroku config:set VITE_DEV_MODE=false
heroku config:set VITE_API_URL=https://api.your-domain.com
```

**Vercel/Netlify の場合:**
- ダッシュボードから Environment Variables を設定
- Production 環境に上記の変数を追加

#### 3.2 コードのデプロイ

```bash
# ブランチをメインにマージ (レビュー後)
git checkout main
git merge claude/review-security-training-post-011CV3xCV9ZrgSSQGReFuDi4
git push origin main

# または直接このブランチをデプロイ
git push origin claude/review-security-training-post-011CV3xCV9ZrgSSQGReFuDi4:main
```

---

### ステップ 4: デプロイ後の検証

#### 4.1 セキュリティチェック

```bash
# 1. 開発者モードが無効であることを確認
curl -X POST https://your-api-domain.com/api/auth/verify-invite \
  -H "Content-Type: application/json" \
  -d '{"token":"dev"}'

# 期待される結果:
# {"valid":false,"message":"サーバーエラーが発生しました"}
# (詳細なエラーメッセージが表示されないこと)

# 2. CORS設定を確認
curl -X OPTIONS https://your-api-domain.com/api/health \
  -H "Origin: https://malicious-site.com" \
  -v

# 期待される結果:
# Access-Control-Allow-Origin ヘッダーが返されないこと

# 3. 正規のオリジンからのアクセスを確認
curl -X OPTIONS https://your-api-domain.com/api/health \
  -H "Origin: https://your-actual-domain.com" \
  -v

# 期待される結果:
# Access-Control-Allow-Origin: https://your-actual-domain.com
```

#### 4.2 機能テスト

- [ ] 新規ユーザー登録が正常に動作する
- [ ] ログインが正常に動作する
- [ ] セッション検証が正常に動作する
- [ ] 問題取得APIが正常に動作する

---

### ステップ 5: モニタリング

#### 5.1 ログの確認

デプロイ後、以下のログメッセージを確認:

**正常な起動:**
```
🔒 本番モード - 許可オリジン: ['https://your-domain.com']
✅ 230問の問題集を読み込みました
```

**警告が出る場合（修正が必要）:**
```
🔧 開発モード有効 - 許可オリジン: [...]
⚠️ 開発者モード: 招待トークン検証をスキップ
```

#### 5.2 エラーレートの監視

- 認証エラーが異常に多い場合は、CORS設定を確認
- セッション検証エラーが多い場合は、デバイスIDの生成ロジックを確認

---

## 🔄 ロールバック手順

問題が発生した場合の緊急ロールバック:

```bash
# 以前のコミットに戻す
git revert 20bb4ae
git push origin main

# または、環境変数で一時的に開発モードに戻す（非推奨）
# DEV_MODE=true
# VITE_DEV_MODE=true
```

**注意**: ロールバックすると脆弱性が復活するため、問題解決後は速やかに再デプロイしてください。

---

## 📞 トラブルシューティング

### 問題 1: CORS エラーが発生する

**症状**: ブラウザのコンソールに "CORS policy blocked" エラー

**解決方法**:
1. `ALLOWED_ORIGINS` に正しいドメインが含まれているか確認
2. プロトコル (`https://`) が正しいか確認
3. サブドメインが正しいか確認 (`www.` の有無など)

```bash
# 環境変数を確認
railway variables
# または
heroku config
```

### 問題 2: 認証が動作しない

**症状**: ログインできない、セッションが無効と表示される

**解決方法**:
1. `DEV_MODE=false` が設定されているか確認
2. バックエンドとフロントエンドのURLが正しいか確認
3. ブラウザの localStorage をクリア

```javascript
// ブラウザのコンソールで実行
localStorage.clear()
location.reload()
```

### 問題 3: エラーメッセージが表示されない

**症状**: エラーが発生しているが、詳細が分からない

**解決方法**:
1. バックエンドのログを確認（詳細なエラーはサーバーログに記録されています）
2. 一時的に `DEV_MODE=true` に設定して詳細を確認（**本番環境では速やかに false に戻す**）

---

## 📚 関連ドキュメント

- `.env.example` - 環境変数の詳細な説明
- `backend/api_server.py` - バックエンドのセキュリティ実装
- `src/components/ProtectedRoute.jsx` - フロントエンドのセキュリティ実装

---

## ✅ チェックリスト

デプロイ前に以下を確認してください:

- [ ] `backend/.env` ファイルに `DEV_MODE=false` を設定
- [ ] `backend/.env` ファイルに正しい `ALLOWED_ORIGINS` を設定
- [ ] `.env` ファイルに `VITE_DEV_MODE=false` を設定
- [ ] `.env` ファイルに正しい `VITE_API_URL` を設定
- [ ] ローカルで本番モードのテストを実施
- [ ] セキュリティチェックを実施
- [ ] 機能テストを実施
- [ ] ログを確認
- [ ] `.env` ファイルが `.gitignore` に含まれていることを確認（**重要**: 環境変数をコミットしない）

---

**最終更新**: 2025年11月12日
**作成者**: Claude (Security Review Session)

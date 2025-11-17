# 🚀 デプロイ手順書（GitHub Pages）

## 📋 概要
パチンコ主任者試験アプリのGitHub Pagesへのデプロイ手順

## 🔧 前提条件
- GitHubリポジトリ: `pj0201/pachinko-lawtest`
- フロントエンド: GitHub Pages (`https://pj0201.github.io/pachinko-lawtest/`)
- バックエンド: Vercel (`https://pachinko-lawtest.vercel.app/api/`)
- データベース: Vercel KV (Redis Cloud: `redis-pink-notebook`)

## 📝 デプロイ手順

### 1️⃣ ブランチ作成と修正
```bash
# 修正用ブランチを作成
git checkout -b fix/api-url-for-github-pages

# 必要な修正を実施
# - API URLを絶対パスに変更
# - src/config/api.js を作成
# - 各コンポーネントでAPI設定を使用

# 変更をコミット
git add .
git commit -m "fix: API URL修正 - GitHub PagesからVercel APIへの通信を絶対パスに変更"
```

### 2️⃣ GitHubへプッシュ
```bash
# トークン認証の場合（workflowスコープなし）
git push https://[TOKEN]@github.com/pj0201/pachinko-lawtest.git fix/api-url-for-github-pages

# GitHub CLIを使う場合
gh auth login  # 事前認証
git push origin fix/api-url-for-github-pages
```

**注意**: GitHub Actionsワークフロー（.github/workflows/）を含む場合、workflowスコープが必要

### 3️⃣ プルリクエスト作成
```bash
# GitHub CLIで作成
gh pr create \
  --title "🔧 fix: API URL修正 - GitHub PagesからVercel APIへの通信を絶対パスに変更" \
  --body "修正内容の説明..." \
  --head fix/api-url-for-github-pages \
  --base main

# または、ブラウザで作成
# https://github.com/pj0201/pachinko-lawtest/pull/new/fix/api-url-for-github-pages
```

### 4️⃣ マージとデプロイ
1. **PRページを開く**
   ```
   https://github.com/pj0201/pachinko-lawtest/pulls
   ```

2. **ビルドチェック確認**
   - CI/CDチェックが完了するまで待機

3. **「Merge pull request」ボタンをクリック**
   - マージ方法: Create a merge commit（デフォルト）

4. **デプロイ完了待機**
   - GitHub Actions でビルドとデプロイが自動実行
   - 約2-5分で完了

### 5️⃣ デプロイ確認
```bash
# GitHub Actions の状態確認
gh run list --limit 1 --branch main

# または Actions ページで確認
https://github.com/pj0201/pachinko-lawtest/actions
```

### 6️⃣ 動作確認
1. **本番URLにアクセス**
   ```
   https://pj0201.github.io/pachinko-lawtest/
   ```

2. **コンソールで確認**（開発者ツール）
   ```javascript
   console.log(window.location.hostname)  // pj0201.github.io
   // API URLが https://pachinko-lawtest.vercel.app/api になっているか確認
   ```

## 🧪 テスト手順

### 10個のテスト招待URL
| # | トークン | URL |
|---|----------|-----|
| 1 | TEST_001_ABC123 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123 |
| 2 | TEST_002_DEF456 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_002_DEF456 |
| 3 | TEST_003_GHI789 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_003_GHI789 |
| 4 | TEST_004_JKL012 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_004_JKL012 |
| 5 | TEST_005_MNO345 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_005_MNO345 |
| 6 | TEST_006_PQR678 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_006_PQR678 |
| 7 | TEST_007_STU901 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_007_STU901 |
| 8 | TEST_008_VWX234 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_008_VWX234 |
| 9 | TEST_009_YZA567 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_009_YZA567 |
| 10 | TEST_010_BCD890 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_010_BCD890 |

### テスト実施方法
1. **プライベートブラウジングモードで開く**
2. **各URLにアクセス**
3. **登録フォームに入力**
   - ユーザー名: テストユーザーXXX
   - メールアドレス: testXXX@example.com
4. **「登録して始める」をタップ**
5. **結果を記録**

## ⚠️ トラブルシューティング

### デプロイが反映されない場合
1. **キャッシュクリア**: Ctrl+Shift+R（ハードリロード）
2. **Actions確認**: https://github.com/pj0201/pachinko-lawtest/actions
3. **Pages設定確認**: Settings → Pages

### API通信エラーの場合
1. **Vercel API確認**
   ```bash
   curl https://pachinko-lawtest.vercel.app/api/health
   ```
2. **Redis Cloud確認**: Redis Cloudダッシュボードでredis-pink-notebookの状態確認
3. **環境変数確認**: Vercelダッシュボードで環境変数設定を確認

## 📅 更新履歴
- 2025-11-17: 初版作成（API URL修正対応）

---

**作成者**: Claude Code (Worker3)
**最終更新**: 2025-11-17
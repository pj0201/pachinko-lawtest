# 🚀 GitHub PR作成と自動デプロイ設定

## 📋 現在の状況
- ✅ ブランチ作成済み: `fix/api-url-for-github-pages`
- ❌ GitHubへプッシュ待ち
- ✅ 自動デプロイワークフロー準備済み（`.github/workflows/deploy.yml`）

## 🔴 今すぐ実行するコマンド

### ステップ1: ワークフローファイルをコミット

```bash
cd /home/planj/patshinko-exam-app

# ワークフローファイルを追加
git add .github/workflows/deploy.yml

# テストドキュメントも追加
git add TEST_PLAN_10_ACCOUNTS.md
git add DEPLOYMENT_TEST_GUIDE.md

# コミット
git commit -m "ci: GitHub Pages自動デプロイワークフローとテスト計画を追加

- GitHub Actions による自動デプロイ設定
- PRマージ時に自動でGitHub Pagesへデプロイ
- 10個のテストアカウント用テスト計画書
"
```

### ステップ2: GitHubへプッシュ

```bash
# ブランチをプッシュ（認証が必要）
git push -u origin fix/api-url-for-github-pages
```

**認証方法の選択肢：**

#### A. GitHub CLI使用（推奨）
```bash
gh auth login
# → ブラウザで認証

# その後プッシュ
git push -u origin fix/api-url-for-github-pages
```

#### B. 個人アクセストークン使用
```bash
# トークンを使ってプッシュ
git push https://<YOUR_TOKEN>@github.com/pj0201/pachinko-lawtest.git fix/api-url-for-github-pages
```

## 🔄 プルリクエスト作成

### オプション1: GitHub CLIで作成（推奨）

```bash
gh pr create \
  --title "🔧 fix: API URL修正 - GitHub PagesからVercel APIへの通信を絶対パスに変更" \
  --body "## 📋 概要
10個のテスト招待URLでサーバー不通エラーが発生していた問題を修正

## 🐛 問題
- GitHub Pages（https://pj0201.github.io）から
- Vercel API（https://pachinko-lawtest.vercel.app/api）への通信が
- 相対パス（/api/*）のため404エラー発生

## ✅ 解決策
- API設定ファイル（src/config/api.js）を追加
- ホスト名に応じてAPI URLを動的に設定
- GitHub Pagesアクセス時はVercel APIの絶対URLを使用

## 📝 変更内容
- src/config/api.js - API設定ファイル（新規）
- src/pages/Register.jsx - 登録API呼び出し修正
- src/components/ProtectedRoute.jsx - セッション検証API修正
- src/components/Home.jsx - PDF URL生成修正
- .env.production - Vercel API URL環境変数
- .github/workflows/deploy.yml - 自動デプロイ設定

## 🧪 テスト計画
TEST_PLAN_10_ACCOUNTS.md 参照
- 10個のテストアカウントで登録テスト予定
- スマホ専用アプリでの動作確認

## ✅ チェックリスト
- [x] コード修正完了
- [x] ローカルビルド成功
- [x] テスト計画書作成
- [ ] GitHub Pagesデプロイ後テスト
- [ ] 10個のアカウント登録テスト" \
  --base main
```

### オプション2: ブラウザで作成

1. **リポジトリにアクセス**
   ```
   https://github.com/pj0201/pachinko-lawtest
   ```

2. **「Pull requests」→「New pull request」**

3. **ブランチ選択**
   - base: `main`
   - compare: `fix/api-url-for-github-pages`

4. **「Create pull request」ボタンクリック**

## ⚙️ GitHub Pages設定確認

### リポジトリ設定（Settings → Pages）

確認事項：
- **Source**: Deploy from a branch または GitHub Actions
- **Branch**: `gh-pages` または `main`
- **Folder**: `/` (root) または `/dist`

推奨設定（GitHub Actions使用）：
```
Source: GitHub Actions
```

## 🎯 PR作成後の流れ

```mermaid
1. PRを作成
   ↓
2. GitHub Actionsでビルド実行（自動）
   ↓
3. ビルド成功確認
   ↓
4. 「Merge pull request」ボタンをクリック
   ↓
5. 自動デプロイ開始
   ↓
6. GitHub Pagesに反映（2-5分）
   ↓
7. テスト実行
```

## ✅ 成功確認方法

1. **Actions タブで確認**
   ```
   https://github.com/pj0201/pachinko-lawtest/actions
   ```
   - ✅ 緑のチェックマーク = 成功
   - ❌ 赤のX = 失敗

2. **GitHub Pages URL確認**
   ```
   https://pj0201.github.io/pachinko-lawtest/
   ```

3. **APIテスト**
   ```bash
   # ブラウザのコンソールで確認
   console.log(window.location.hostname)  // pj0201.github.io
   # API URLが https://pachinko-lawtest.vercel.app/api になっているか確認
   ```

## 📝 重要事項

- **マージボタンは手動で押してください**（自動マージは設定していません）
- ワークフローは`main`ブランチへのプッシュまたはPRマージで自動実行
- デプロイには2-5分かかります
- キャッシュの影響で反映が遅れる場合があります（Ctrl+Shift+R）

---

**準備完了！上記コマンドを順次実行してください。**
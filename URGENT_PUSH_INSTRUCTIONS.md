# 🚨 緊急：GitHubへのプッシュ手順

## 現在の状況
- **問題**: 10個のテスト招待URLでサーバー不通エラー
- **原因**: API URLが相対パスのため404エラー
- **修正**: コミット済み（c83ea8c）だが**GitHubに未反映**

## 📌 今すぐ実行してください

### オプション1: コマンドラインから

```bash
cd /home/planj/patshinko-exam-app

# リモートの状態確認
git remote -v

# プッシュ実行
git push origin main
# → ユーザー名とパスワード（またはトークン）入力
```

### オプション2: GitHub CLIを使用

```bash
# GitHub CLIでログイン
gh auth login

# プッシュ
git push origin main
```

### オプション3: 個人アクセストークン使用

1. GitHubで個人アクセストークン生成
   - https://github.com/settings/tokens
   - "Generate new token" → "repo"権限を選択

2. プッシュ実行
```bash
git push https://<トークン>@github.com/pj0201/pachinko-lawtest.git main
```

## ✅ プッシュ成功後の確認

1. **GitHub リポジトリで確認**
   ```
   https://github.com/pj0201/pachinko-lawtest
   ```
   - 最新コミット: "fix: API URL修正 - GitHub PagesからVercel APIへの通信を絶対パスに変更"

2. **GitHub Pages デプロイ待ち（約2-5分）**
   - Actions タブでデプロイ状況確認
   - https://github.com/pj0201/pachinko-lawtest/actions

3. **テスト実行**
   ```
   https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123
   ```
   - 開発者ツール → Network タブ
   - `https://pachinko-lawtest.vercel.app/api/validate-token` へのリクエスト確認

## 🎯 期待される結果

**Before（現在）:**
- 招待URL → 登録フォーム入力 → "サーバーとの通信に失敗しました" ❌

**After（プッシュ後）:**
- 招待URL → 登録フォーム入力 → 登録成功 → ホーム画面 ✅

## ⚠️ 重要

修正はすでに完了しています。**GitHubへプッシュするだけで問題は解決します！**

---
緊急度: 🔴 最高
作成時刻: 2025-11-17 21:20
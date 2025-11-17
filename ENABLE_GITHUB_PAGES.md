# 🚨 GitHub Pages 有効化手順（重要）

## ⚠️ 現在の状況
- **GitHub Pages: 無効** (`has_pages: false`)
- **現在のデプロイ先: Vercel** (`https://pachinko-lawtest.vercel.app`)
- **必要な対応: GitHub Pages を有効化**

## 📝 GitHub Pages 有効化手順

### 方法1: GitHub UI から設定（推奨）

1. **リポジトリ設定ページを開く**
   ```
   https://github.com/pj0201/pachinko-lawtest/settings/pages
   ```

2. **Source を設定**
   - **Source**: `Deploy from a branch` を選択
   - **Branch**: `gh-pages` を選択（存在しない場合は `main` を選択）
   - **Folder**: `/` (root) を選択

3. **Save ボタンをクリック**

4. **数分待機**
   - 初回デプロイには5-10分かかる場合があります
   - Actions タブで進行状況を確認

### 方法2: gh-pages ブランチを作成してデプロイ

```bash
# distフォルダをビルド
npm run build

# gh-pagesブランチを作成
git checkout --orphan gh-pages
git rm -rf .
cp -r dist/* .
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages

# mainブランチに戻る
git checkout main
```

### 方法3: GitHub Actions でデプロイ（推奨）

1. **ワークフローファイルを追加**（既に作成済み）
   `.github/workflows/deploy.yml`

2. **リポジトリ設定で GitHub Actions を有効化**
   - Settings → Pages
   - Source: `GitHub Actions` を選択

## 🔍 確認方法

### GitHub Pages が有効になったか確認
```bash
gh api repos/pj0201/pachinko-lawtest --jq '.has_pages'
# true が返れば有効
```

### デプロイ状況確認
```bash
gh run list --workflow=deploy.yml --limit 1
```

### サイトにアクセス
```
https://pj0201.github.io/pachinko-lawtest/
```

## 📊 テスト招待URL（GitHub Pages 有効化後）

GitHub Pages が有効になったら、以下のURLでテスト可能：

| # | URL |
|---|-----|
| 1 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123 |
| 2 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_002_DEF456 |
| 3 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_003_GHI789 |
| 4 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_004_JKL012 |
| 5 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_005_MNO345 |
| 6 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_006_PQR678 |
| 7 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_007_STU901 |
| 8 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_008_VWX234 |
| 9 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_009_YZA567 |
| 10 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_010_BCD890 |

## 🔄 代替案: Vercel でテスト

GitHub Pages の設定が難しい場合、Vercel のURLでテスト可能：

```
https://pachinko-lawtest.vercel.app/?token=TEST_001_ABC123
```

ただし、この場合はAPI URLの修正は不要（同一ドメインのため）

## ⚠️ 重要な注意事項

- **GitHub Pages と Vercel の同時運用は可能**
- **どちらか一方だけ使う場合は、API URLの設定を確認**
- **GitHub Pages を使う場合は必ず有効化が必要**

---

**作成日時**: 2025-11-17
**作成者**: Claude Code (Worker3)
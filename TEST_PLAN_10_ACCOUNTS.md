# 📱 10個のテストアカウント登録テスト計画書

## 🎯 テスト目的
スマホ専用アプリで10個のテスト招待URLが正常に機能し、各アカウントが問題なく登録できることを確認する

## 📋 前提条件

### 1. プッシュとデプロイ
- [ ] `git push origin main` 実行済み
- [ ] GitHub Pages デプロイ完了（約5分待機）
- [ ] Vercel APIヘルスチェック確認

```bash
# APIヘルスチェック
curl https://pachinko-lawtest.vercel.app/api/health
```

## 🧪 テストアカウント一覧

| # | トークン | テストURL | メールアドレス | ユーザー名 | ステータス |
|---|----------|-----------|---------------|-----------|------------|
| 1 | TEST_001_ABC123 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123 | test001@example.com | テストユーザー001 | ⏳ 未テスト |
| 2 | TEST_002_DEF456 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_002_DEF456 | test002@example.com | テストユーザー002 | ⏳ 未テスト |
| 3 | TEST_003_GHI789 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_003_GHI789 | test003@example.com | テストユーザー003 | ⏳ 未テスト |
| 4 | TEST_004_JKL012 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_004_JKL012 | test004@example.com | テストユーザー004 | ⏳ 未テスト |
| 5 | TEST_005_MNO345 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_005_MNO345 | test005@example.com | テストユーザー005 | ⏳ 未テスト |
| 6 | TEST_006_PQR678 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_006_PQR678 | test006@example.com | テストユーザー006 | ⏳ 未テスト |
| 7 | TEST_007_STU901 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_007_STU901 | test007@example.com | テストユーザー007 | ⏳ 未テスト |
| 8 | TEST_008_VWX234 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_008_VWX234 | test008@example.com | テストユーザー008 | ⏳ 未テスト |
| 9 | TEST_009_YZA567 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_009_YZA567 | test009@example.com | テストユーザー009 | ⏳ 未テスト |
| 10 | TEST_010_BCD890 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_010_BCD890 | test010@example.com | テストユーザー010 | ⏳ 未テスト |

## 📱 スマホテスト手順（各アカウント共通）

### ステップ1: ブラウザ準備
1. **プライベートブラウジングモードを開く**
   - iPhone: Safari → プライベートブラウズ
   - Android: Chrome → シークレットモード
2. **開発者ツール相当を準備**（可能な場合）
   - Chrome: `chrome://inspect` でUSBデバッグ
   - Safari: Mac連携でWebインスペクタ

### ステップ2: 登録フロー
1. **招待URLアクセス**
   - 上記テーブルのURLをタップ
   - 読み込み完了を確認

2. **コンソールログ確認**（開発者ツール使用時）
   ```
   🔧 API Base URL: https://pachinko-lawtest.vercel.app/api
   🔧 Current hostname: pj0201.github.io
   ```

3. **登録フォーム入力**
   - ユーザー名: テストユーザーXXX
   - メールアドレス: testXXX@example.com
   - 「登録して始める」をタップ

4. **期待結果**
   - ✅ 登録成功 → ホーム画面遷移
   - ❌ エラーの場合は記録

### ステップ3: 結果記録
- 成功: ✅
- 失敗: ❌ （エラーメッセージ記録）

## 🔍 エラー別対処法

### エラー1: "サーバーとの通信に失敗しました"
**原因**: API URLがまだ相対パス
**対策**: デプロイ完了待ち、キャッシュクリア

### エラー2: "この招待URLは既に使用されています"
**原因**: トークン重複使用
**対策**: Redis Cloudでデータクリア or 別トークン使用

### エラー3: "このメールアドレスは既に登録されています"
**原因**: メールアドレス重複
**対策**: 別のメールアドレス使用

## 📊 テスト実行チェックリスト

### 事前準備
- [ ] GitHub へプッシュ完了
- [ ] GitHub Pages デプロイ完了（Actions確認）
- [ ] Vercel API ヘルスチェックOK
- [ ] Redis Cloud 稼働確認

### テスト実行
- [ ] TEST_001_ABC123 登録テスト
- [ ] TEST_002_DEF456 登録テスト
- [ ] TEST_003_GHI789 登録テスト
- [ ] TEST_004_JKL012 登録テスト
- [ ] TEST_005_MNO345 登録テスト
- [ ] TEST_006_PQR678 登録テスト
- [ ] TEST_007_STU901 登録テスト
- [ ] TEST_008_VWX234 登録テスト
- [ ] TEST_009_YZA567 登録テスト
- [ ] TEST_010_BCD890 登録テスト

### 追加テスト
- [ ] 重複トークンテスト（同じトークンで2回目の登録）
- [ ] 重複メールテスト（同じメールで別トークン）
- [ ] セッション維持テスト（登録後のページリロード）

## 💡 テストのコツ

1. **キャッシュクリア重要**
   - 各テスト前にプライベートブラウジング推奨
   - または localStorage クリア

2. **ネットワーク監視**
   - 可能ならUSBデバッグでネットワークタブ確認
   - APIリクエスト先が正しいか確認

3. **エラーログ収集**
   - スクリーンショット撮影
   - エラーメッセージを正確に記録

## 🎯 成功基準

- **10個中10個**: 完璧！修正成功 ✅
- **10個中8-9個**: ほぼ成功、個別問題の可能性
- **10個中5個以下**: 根本的な問題あり、要調査

## 📝 テスト結果記録フォーマット

```markdown
### アカウント#1 (TEST_001_ABC123)
- 時刻: 2025-11-17 XX:XX
- デバイス: iPhone/Android
- ブラウザ: Safari/Chrome
- 結果: ✅成功 / ❌失敗
- エラー詳細: （ある場合）
- スクリーンショット: （ある場合）
```

---

**作成日時**: 2025-11-17 21:30
**テスト実行予定**: GitHubプッシュ後
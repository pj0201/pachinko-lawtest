# テスト用招待 URL リスト

## 📋 テストユーザー（10個）

| # | トークン | URL | 備考 |
|----|---------|-----|------|
| 1 | TEST_001_ABC123 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123 | テストユーザー 001 |
| 2 | TEST_002_DEF456 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_002_DEF456 | テストユーザー 002 |
| 3 | TEST_003_GHI789 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_003_GHI789 | テストユーザー 003 |
| 4 | TEST_004_JKL012 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_004_JKL012 | テストユーザー 004 |
| 5 | TEST_005_MNO345 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_005_MNO345 | テストユーザー 005 |
| 6 | TEST_006_PQR678 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_006_PQR678 | テストユーザー 006 |
| 7 | TEST_007_STU901 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_007_STU901 | テストユーザー 007 |
| 8 | TEST_008_VWX234 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_008_VWX234 | テストユーザー 008 |
| 9 | TEST_009_YZA567 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_009_YZA567 | テストユーザー 009 |
| 10 | TEST_010_BCD890 | https://pj0201.github.io/pachinko-lawtest/?token=TEST_010_BCD890 | テストユーザー 010 |

---

## 👤 管理者（開発者）

| トークン | URL | 備考 |
|---------|-----|------|
| ADMIN_DEV_XYZ999 | https://pj0201.github.io/pachinko-lawtest/?token=ADMIN_DEV_XYZ999 | 管理者（開発者用） |

---

## ⚠️ 重要事項

- **一度登録したトークンは使用不可**（localStorage に記録される）
- 別のデバイスで同じトークンを使えません（デバイスIDで紐付け）
- トークンを リセット する場合は、ブラウザの localStorage を全削除してください

---

**テスト手順：**

1. 上記の URL をメール等で配布
2. ユーザーが URL をクリック → 登録フォーム表示
3. メールアドレス・パスワード入力 → 登録
4. アプリホーム画面へ遷移
5. 同じトークンで再度登録→ エラー「既に使用済み」が表示される

---

**生成日：2025-11-09**

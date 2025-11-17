# スマートフォンテストガイド

## 重要：スマホ専用アプリです

このアプリはコンソールからの漏洩対策のため、**スマートフォンのみでアクセス可能**です。

デスクトップブラウザからアクセスすると：
```
このアプリはスマートフォン専用です。
スマートフォンからアクセスしてください。
```

---

## 招待URL一覧（10個）

1. https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
2. https://pachinko-lawtest.vercel.app/invite/cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb
3. https://pachinko-lawtest.vercel.app/invite/d0b28ab3-44b6-45aa-897b-e72e0e0da116
4. https://pachinko-lawtest.vercel.app/invite/babcd6fb-b8a8-46a8-b3a6-fc00966d07a3
5. https://pachinko-lawtest.vercel.app/invite/b1b281a3-6b76-4659-9827-bf3a07b6c3ba
6. https://pachinko-lawtest.vercel.app/invite/12f622c2-cbf4-4631-abb7-7336c841b198
7. https://pachinko-lawtest.vercel.app/invite/3c756c94-0d98-4d8b-b466-17e99f1b3240
8. https://pachinko-lawtest.vercel.app/invite/2b1d54e2-97a0-4900-a513-fab986540358
9. https://pachinko-lawtest.vercel.app/invite/d47c9566-cabd-4d96-91d0-41afc10a59b6
10. https://pachinko-lawtest.vercel.app/invite/c502c94a-3e4e-471e-9835-2f05018751e4

---

## テスト1: スマホAで初回登録（成功すべき）

### 手順

1. **スマホAで招待URL #1 にアクセス**
   ```
   https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
   ```

2. **登録フォームが表示される**
   - ✅ 「パチンコ試験アプリ 登録」画面
   - ✅ ユーザー名入力欄
   - ✅ メールアドレス入力欄
   - ✅ 登録ボタン

3. **フォーム入力**
   - ユーザー名: `テストユーザー1`
   - メールアドレス: `test1@example.com`

4. **「登録」ボタンをタップ**

### 期待される結果

- ✅ ローディング表示
- ✅ ホーム画面に遷移
- ✅ 「模擬試験開始」ボタンが表示される

### 確認ポイント

- エラーメッセージが表示されない
- ホーム画面に正常に遷移

---

## テスト2: スマホBで同じトークンを使用（失敗すべき）

### 手順

1. **別のスマホ（スマホB）で同じ招待URL #1 にアクセス**
   ```
   https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
   ```

   ⚠️ **スマホが1台しかない場合:**
   - スマホAのブラウザでlocalStorageをクリア
   - または別のブラウザアプリを使用（Chrome → Firefox など）

2. **フォーム入力**
   - ユーザー名: `テストユーザー2`
   - メールアドレス: `test2@example.com`（新しいメール）

3. **「登録」ボタンをタップ**

### 期待される結果

- ❌ エラーメッセージ表示:
  ```
  この招待URLは既に使用されています
  ```
- ホーム画面に遷移しない

### 確認ポイント

- 赤いエラーメッセージが表示される
- 登録できない

---

## テスト3: スマホBで同じメールアドレスを使用（失敗すべき）

### 手順

1. **スマホBで招待URL #2 にアクセス**
   ```
   https://pachinko-lawtest.vercel.app/invite/cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb
   ```

2. **フォーム入力**
   - ユーザー名: `テストユーザー3`
   - メールアドレス: `test1@example.com`（スマホAで使用済み）

3. **「登録」ボタンをタップ**

### 期待される結果

- ❌ エラーメッセージ表示:
  ```
  このメールアドレスは既に登録されています
  ```

### 確認ポイント

- 赤いエラーメッセージが表示される
- 登録できない

---

## テスト4: スマホBで新しいトークン + 新しいメール（成功すべき）

### 手順

1. **スマホBで招待URL #3 にアクセス**
   ```
   https://pachinko-lawtest.vercel.app/invite/d0b28ab3-44b6-45aa-897b-e72e0e0da116
   ```

2. **フォーム入力**
   - ユーザー名: `テストユーザー3`
   - メールアドレス: `test3@example.com`（新規）

3. **「登録」ボタンをタップ**

### 期待される結果

- ✅ 登録成功
- ✅ ホーム画面に遷移

### 確認ポイント

- エラーが出ない
- 正常に登録完了

---

## localStorageクリア方法（スマホが1台の場合）

### iPhone（Safari）

1. **設定アプリ** → **Safari** → **詳細** → **Webサイトデータ**
2. **全Webサイトデータを削除**

または

1. Safari で招待URLを開く
2. 開発者ツールを有効化（Mac必要）

### Android（Chrome）

1. **Chromeアプリ** → **⋮** → **設定**
2. **プライバシーとセキュリティ** → **閲覧履歴データの削除**
3. **Cookie とサイトデータ** をチェック
4. **データを削除**

---

## デバッグ情報の確認（Chrome DevTools）

### Android Chrome で開発者ツールを使う

1. **Androidデバイスで開発者向けオプションを有効化**
   - 設定 → システム → 端末情報
   - ビルド番号を7回タップ

2. **USBデバッグを有効化**
   - 開発者向けオプション → USBデバッグ

3. **PCとUSB接続**

4. **PC の Chrome で `chrome://inspect`**

5. **Androidデバイスの画面をリモートデバッグ**
   - コンソールで以下を確認:
     ```javascript
     localStorage.getItem('session_token')
     localStorage.getItem('device_id')
     localStorage.getItem('email')
     ```

---

## テスト結果の報告

各テストで以下を報告してください：

### テスト1: スマホAで初回登録
- [ ] ✅ 成功 / ❌ 失敗
- エラーメッセージ（あれば）:
- スクリーンショット（あれば）:

### テスト2: 同じトークン使用
- [ ] ✅ エラーが正しく表示された / ❌ エラーが表示されない
- エラーメッセージ:
- スクリーンショット:

### テスト3: 同じメール使用
- [ ] ✅ エラーが正しく表示された / ❌ エラーが表示されない
- エラーメッセージ:
- スクリーンショット:

### テスト4: 新トークン + 新メール
- [ ] ✅ 成功 / ❌ 失敗
- エラーメッセージ（あれば）:
- スクリーンショット:

---

## Redis Cloudに保存されるデータ

テスト後、Redis Cloudで以下のキーが作成されます：

### トークン使用済み情報
```
token:039742a2-f799-4574-8530-a8e1d81960f1 → {
  "usedBy": "test1@example.com",
  "usedAt": "2025-11-17T..."
}
```

### ユーザー情報
```
email:test1@example.com → {
  "username": "テストユーザー1",
  "email": "test1@example.com",
  "deviceId": "...",
  "inviteToken": "039742a2-f799-4574-8530-a8e1d81960f1",
  "sessionToken": "session_...",
  "registeredAt": "2025-11-17T..."
}
```

### セッション情報
```
session:session_1731829593282_... → {
  "username": "テストユーザー1",
  "email": "test1@example.com",
  ...
}
```

---

## トラブルシューティング

### 「スマートフォン専用です」エラーが出る

**原因:** デバイス検出が失敗している

**確認:**
- 本当にスマホからアクセスしているか
- 「デスクトップサイトを表示」がOFFか
- 画面幅が768px以下か

### 「デバイス識別に失敗しました」エラー

**原因:** FingerprintJS が動作していない

**解決:**
- ページをリロード
- ブラウザのJavaScriptが有効か確認
- プライベートモード/シークレットモードを試す

### 「サーバーとの通信に失敗しました」エラー

**原因:** API接続エラー

**確認:**
- インターネット接続
- https://pachinko-lawtest.vercel.app/api/health にアクセス
- Redis Cloud 接続状態を確認

---

## 成功時の流れ

1. 招待URLにアクセス
2. 登録フォーム表示
3. ユーザー名・メール入力
4. 「登録」ボタンタップ
5. **ローディング表示**
6. **バックエンドでRedis検証**
   - トークン使用済みチェック
   - メール重複チェック
7. **Redis に保存**
8. **ホーム画面に遷移**
9. **「模擬試験開始」ボタン表示**

---

**スマホでテストを開始してください！**

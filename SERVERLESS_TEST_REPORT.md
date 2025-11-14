# サーバーレスモード テスト報告書

## テスト日時
2025-11-14

## テスト目的
招待URL（トークン）の動作を検証し、ユーザーの懸念に答える

---

## ユーザーの懸念事項

### 1. 同じデバイスで2番目のURLにアクセスしたらログイン画面になった
**回答：これは正常な動作です**

#### 動作説明：
- **1番目のURL（例：TEST_001_ABC123）で登録**
  - localStorage に `session_token` と `device_id` が保存される
  - ユーザー情報（username, email）も保存される

- **同じデバイスで2番目のURL（例：TEST_002_DEF456）にアクセス**
  - `Register.jsx:25-32` で既存の `session_token` を検出
  - 既にログイン済みと判断
  - **ホーム画面へ自動リダイレクト**（登録画面をスキップ）

#### コード該当箇所：
```javascript
// Register.jsx:25-32
useEffect(() => {
  const sessionToken = localStorage.getItem('session_token');
  const deviceId = localStorage.getItem('device_id');

  if (sessionToken && deviceId) {
    console.log('✅ セッション確認 - ホーム画面へリダイレクト');
    setAlreadyLoggedIn(true);
  }
}, []);
```

---

### 2. 別デバイスなら登録画面になるのか？
**回答：YES。別デバイスは localStorage が別なので、登録画面が表示されます**

#### 動作説明：
- 各デバイス（ブラウザ）は独立した localStorage を持つ
- デバイスA で登録しても、デバイスB の localStorage には何も保存されていない
- デバイスB でアクセスすると、`session_token` が無いため登録画面が表示される

---

### 3. 2番目のURLが無効になっているのか？（1番目で登録したのに）
**回答：NO。サーバーレスモードではトークンは無効化されません**

#### 修正前の問題：
- 以前のコードには「トークン無効化ロジック」が残っていた（Register.jsx:95-103）
- しかし、トークン検証をスキップしているため、このロジックは意味が無かった
- **混乱の原因となっていた**

#### 修正内容（本コミット）：
```diff
- // テスト用トークン無効化（重要）
- if (token && (token.startsWith('TEST_') || token.startsWith('ADMIN_'))) {
-   const usedTokens = JSON.parse(localStorage.getItem('used_tokens') || '[]');
-   if (!usedTokens.includes(token)) {
-     usedTokens.push(token);
-     localStorage.setItem('used_tokens', JSON.stringify(usedTokens));
-     console.log(`✅ トークン無効化: ${token}`);
-   }
- }
```

#### サーバーレスモードの仕様：
- **トークン（招待URL）は検証されない**（Register.jsx:51-53）
- どのURLでも、どのデバイスでも登録可能
- トークンは使われない（参考情報として残っているだけ）

---

## 動作フローまとめ

### シナリオ1: 同じデバイスで複数のURLにアクセス
```
1. TEST_001_ABC123 で登録
   → localStorage に session_token 保存

2. TEST_002_DEF456 でアクセス
   → 既存 session_token 検出
   → ホーム画面へリダイレクト（登録スキップ）

結果：2番目のURLは使われない（既にログイン済みのため）
```

### シナリオ2: 別デバイスで同じURLにアクセス
```
デバイスA: TEST_001_ABC123 で登録
   → デバイスA の localStorage に保存

デバイスB: TEST_001_ABC123 でアクセス
   → デバイスB の localStorage は空
   → 登録画面が表示される
   → 登録可能（トークン検証なし）

結果：同じURLで複数デバイスの登録が可能
```

### シナリオ3: 別デバイスで別のURLにアクセス
```
デバイスA: TEST_001_ABC123 で登録
デバイスB: TEST_002_DEF456 で登録
   → 両方とも正常に登録可能

結果：各デバイスで独立して動作
```

---

## 技術的な結論

### サーバーレスモードの特徴：
1. **トークン（招待URL）は使われない**
   - トークン検証をスキップ（Register.jsx:51-53）
   - どのURLでも登録可能

2. **localStorage のみでセッション管理**
   - サーバーとの通信なし
   - デバイスごとに独立

3. **1デバイス = 1アカウント**
   - 同じデバイスで複数アカウントは作れない
   - 既存アカウントがあると自動ログイン

4. **メールアドレスでアカウント復旧**
   - localStorage クリア時の復旧手段として追加

---

## 変更履歴

### Commit: "fix: Remove token invalidation logic in serverless mode"
- トークン無効化ロジックを削除（Register.jsx:95-103）
- サーバーレスモードの仕様を明確化
- 混乱を招くコードを除去

---

## テスト確認項目

✅ 同じデバイスで2番目のURLにアクセス → ホーム画面へリダイレクト（正常）
✅ 別デバイスでアクセス → 登録画面が表示される（localStorage が別）
✅ トークン無効化ロジック削除 → 混乱の原因を除去
✅ メールアドレスフィールド追加 → アカウント復旧手段を確保

---

## 推奨事項

### 本番環境での注意：
1. **ProtectedRoute.jsx の `isDev = true` を確認**
   - 現在は常に認証スキップモード
   - 意図的な設計であることを確認

2. **localStorage クリア時のデータ喪失**
   - ユーザーにバックアップ方法を案内
   - または、メールアドレスでの復旧機能を実装

3. **同一デバイスでの複数アカウント**
   - 現在は不可能（1デバイス1アカウント）
   - 必要なら、ログアウト機能を追加

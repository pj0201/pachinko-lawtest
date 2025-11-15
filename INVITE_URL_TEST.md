# 招待URL制限 実装テスト

## 実装内容

### ✅ 1招待URL = 1アカウント制限

**目的:** 漏洩した招待URLの追跡と登録数制限

**実装箇所:** `src/pages/Register.jsx`

---

## 実装詳細

### 1. トークン検証（Register.jsx:51-78）

```javascript
// トークン検証（サーバーレス）
const validateToken = async () => {
  if (!token) {
    setError('招待URLが無効です。正しいURLからアクセスしてください。');
    setLoading(false);
    return;
  }

  // 使用済みトークンをチェック
  const usedTokens = JSON.parse(localStorage.getItem('used_tokens') || '[]');
  if (usedTokens.includes(token)) {
    setError('この招待URLは既に使用されています。');
    setLoading(false);
    return;
  }

  // トークンフォーマットチェック
  if (!token.startsWith('TEST_') && !token.startsWith('ADMIN_')) {
    setError('無効な招待URLです。');
    setLoading(false);
    return;
  }

  console.log('✅ トークン検証成功:', token);
  setLoading(false);
};
```

**チェック項目:**
1. トークンが存在するか
2. 使用済みでないか（localStorage の `used_tokens` 配列）
3. フォーマットが正しいか（TEST_ または ADMIN_ で始まる）

---

### 2. 登録時のトークン使用済み処理（Register.jsx:105-118）

```javascript
// 再度、使用済みトークンをチェック
const usedTokens = JSON.parse(localStorage.getItem('used_tokens') || '[]');
if (usedTokens.includes(token)) {
  setError('この招待URLは既に使用されています');
  return;
}

setLoading(true);

try {
  // トークンを使用済みにする（重要：登録前に実行）
  usedTokens.push(token);
  localStorage.setItem('used_tokens', JSON.stringify(usedTokens));
  console.log('✅ トークン使用済み登録:', token);
```

**重要:**
- 登録処理の**最初**にトークンを使用済みリストに追加
- ダブルチェックで確実に1回のみ使用可能に

---

### 3. 使用トークンの記録（Register.jsx:127-137）

```javascript
// ユーザー情報も保存（使用したトークンも記録）
localStorage.setItem('username', username);
localStorage.setItem('email', email);
localStorage.setItem('invite_token', token);
localStorage.setItem('user', JSON.stringify({
  username,
  email,
  invite_token: token,  // ← 追跡用
  session_token: sessionToken,
  registered_at: new Date().toISOString()
}));
```

**追跡可能:**
- どのトークンで登録したか記録
- 漏洩時の調査に使用可能

---

## テストシナリオ

### シナリオ1: 正常登録（1回目）
```
URL: http://localhost:5173/register/TEST_001_ABC123
期待: ✅ 登録成功

localStorage:
{
  "used_tokens": ["TEST_001_ABC123"],
  "invite_token": "TEST_001_ABC123",
  "username": "テストユーザー",
  "email": "test@example.com"
}
```

### シナリオ2: 使用済みトークンで再登録（エラー）
```
URL: http://localhost:5173/register/TEST_001_ABC123
期待: ❌ エラー「この招待URLは既に使用されています。」

localStorage:
{
  "used_tokens": ["TEST_001_ABC123"]  ← 既に存在
}
```

### シナリオ3: 別トークンで登録（成功）
```
URL: http://localhost:5173/register/TEST_002_DEF456
期待: ✅ 登録成功

localStorage:
{
  "used_tokens": ["TEST_001_ABC123", "TEST_002_DEF456"]  ← 追加
}
```

### シナリオ4: トークンなしでアクセス（エラー）
```
URL: http://localhost:5173/register/
期待: ❌ エラー「招待URLが無効です。正しいURLからアクセスしてください。」
```

### シナリオ5: 無効なトークン形式（エラー）
```
URL: http://localhost:5173/register/INVALID_TOKEN_123
期待: ❌ エラー「無効な招待URLです。」
```

---

## テスト用URL

以下の10個のテストトークンが利用可能（`public/test-tokens.json`）：

1. http://localhost:5173/register/TEST_001_ABC123
2. http://localhost:5173/register/TEST_002_DEF456
3. http://localhost:5173/register/TEST_003_GHI789
4. http://localhost:5173/register/TEST_004_JKL012
5. http://localhost:5173/register/TEST_005_MNO345
6. http://localhost:5173/register/TEST_006_PQR678
7. http://localhost:5173/register/TEST_007_STU901
8. http://localhost:5173/register/TEST_008_VWX234
9. http://localhost:5173/register/TEST_009_YZA567
10. http://localhost:5173/register/TEST_010_BCD890
11. http://localhost:5173/register/ADMIN_DEV_XYZ999（管理者用）

---

## 漏洩検出方法

### 1. 使用済みトークン確認

ブラウザの開発者ツールで以下を実行：

```javascript
// 使用済みトークン一覧
const usedTokens = JSON.parse(localStorage.getItem('used_tokens') || '[]');
console.log('使用済みトークン:', usedTokens);

// どのトークンで登録したか
const inviteToken = localStorage.getItem('invite_token');
console.log('このデバイスの登録トークン:', inviteToken);
```

### 2. 未使用トークン確認

```javascript
const allTokens = [
  'TEST_001_ABC123', 'TEST_002_DEF456', 'TEST_003_GHI789',
  'TEST_004_JKL012', 'TEST_005_MNO345', 'TEST_006_PQR678',
  'TEST_007_STU901', 'TEST_008_VWX234', 'TEST_009_YZA567',
  'TEST_010_BCD890', 'ADMIN_DEV_XYZ999'
];

const usedTokens = JSON.parse(localStorage.getItem('used_tokens') || '[]');
const unusedTokens = allTokens.filter(t => !usedTokens.includes(t));

console.log('未使用トークン:', unusedTokens);
console.log('使用済み:', usedTokens.length, '個');
console.log('未使用:', unusedTokens.length, '個');
```

---

## 制限事項

### ⚠️ localStorage の制約

**問題:**
- localStorage はデバイスごとに独立
- デバイスAで TEST_001 を使用しても、デバイスBでは使用可能

**つまり:**
- **1トークン = 1アカウント** ではなく
- **1トークン = 1デバイスで1アカウント**

**対策:**
- サーバーレスモードでは完全な制限は不可能
- サーバー実装が必要（バックエンドでトークン管理）

### 現状での利点

1. ✅ **同一デバイスでの複数登録を防止**
   - ユーザーが誤って同じトークンで再登録しない

2. ✅ **使用トークンの追跡可能**
   - どのトークンで登録したか記録

3. ✅ **トークン形式の検証**
   - 不正なURLでのアクセスを防止

4. ✅ **無効なURLへのフィードバック**
   - ユーザーにエラーメッセージ表示

---

## 次のステップ（サーバー実装が必要な場合）

### バックエンド実装（推奨）

1. **データベースでトークン管理**
   ```sql
   CREATE TABLE invite_tokens (
     token VARCHAR(50) PRIMARY KEY,
     used_at TIMESTAMP,
     user_id INT,
     is_used BOOLEAN DEFAULT FALSE
   );
   ```

2. **API エンドポイント**
   - `POST /api/tokens/validate` - トークン検証
   - `POST /api/tokens/use` - トークン使用済み登録

3. **完全な1トークン1アカウント制限**
   - 全デバイス間でトークン共有
   - 使用済みトークンは全デバイスで無効

---

## まとめ

### ✅ 実装完了

- 1招待URL = 1アカウント（同一デバイス内）
- 使用済みトークンの追跡
- トークン検証とエラーハンドリング
- 注意文の更新

### ⚠️ 制限事項

- localStorage ベース（デバイス間で共有されない）
- 完全な制限にはサーバー実装が必要

### 📊 テスト方法

1. `npm run dev` でサーバー起動
2. 上記のテストURLでアクセス
3. 開発者ツールで localStorage 確認

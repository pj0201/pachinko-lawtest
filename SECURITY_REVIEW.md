# セキュリティレビュー結果

## 🚨 重大な問題（Critical）

### 1. セッション検証が完全にスキップされている

**ファイル:** `src/components/ProtectedRoute.jsx:27`

**問題コード:**
```javascript
const isDev = true;  // ← 常にtrueで本番でも開発モード！
```

**影響:**
- ✅ Vercel KV にセッショントークンを保存しているのに検証していない
- ❌ 誰でも localStorage に適当な値を設定すればログインできる
- ❌ デバイスAで登録したユーザーが、デバイスBで localStorage をコピーすればログイン可能
- ❌ **アカウント流失のリスク大**

**攻撃シナリオ:**
```javascript
// パソコンのChrome DevToolsで実行（User-Agent偽装済み）
localStorage.setItem('session_token', 'fake_token');
localStorage.setItem('device_id', 'fake_device');
// → ログイン成功してしまう
```

**修正必須:**
- `isDev = true` を削除
- KV でセッショントークンを検証する API を追加
- ProtectedRoute で API を呼び出してセッション検証

---

### 2. デバイスバインディングがない

**問題:**
- デバイスAで `test@example.com` で登録
- デバイスBで localStorage に同じ `session_token` をコピー
- デバイスBでもログインできてしまう

**本来の動作:**
- デバイスAで登録 → デバイスAのみで使用可能
- デバイスBでは使用不可（別のアカウントが必要）

**現状:**
- KV にデバイスIDを保存している（`api/register.js:56`）
- しかし、セッション検証でデバイスIDをチェックしていない

**修正必須:**
- セッション検証時にデバイスIDも検証
- KV の `session:${sessionToken}` から `deviceId` を取得
- リクエストのデバイスIDと一致しない場合はエラー

---

## ⚠️ 高リスク（High）

### 3. User-Agent偽装で回避可能

**ファイル:** `src/utils/deviceCheck.js:7`

**問題:**
```javascript
const userAgent = navigator.userAgent.toLowerCase();
const isMobileUA = /android|webos|iphone|ipod/.test(userAgent);
```

**影響:**
- パソコンで Chrome DevTools → Settings → User agent → カスタムUA設定
- `Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)` に変更
- スマホ判定を回避してアクセス可能

**対策:**
- サーバー側でもUser-Agentチェック（API でヘッダー検証）
- ただし、完全な防止は不可能（User-Agentは偽装可能）
- 技術的制約として受け入れるか、別の方法を検討

---

### 4. Race Condition のリスク

**ファイル:** `api/register.js:32-47`

**問題:**
```javascript
// トークン使用済みチェック
const usedToken = await kv.get(`token:${token}`);
if (usedToken) {
  return res.status(400).json({ error: '既に使用されています' });
}
// ... 処理 ...
// トークンを使用済みに
await kv.set(`token:${token}`, { usedBy: email });
```

**Race Conditionシナリオ:**
1. ユーザーA: `kv.get('token:TEST_001')` → null（未使用）
2. ユーザーB: `kv.get('token:TEST_001')` → null（未使用）
3. ユーザーA: `kv.set('token:TEST_001', ...)` → 登録成功
4. ユーザーB: `kv.set('token:TEST_001', ...)` → 登録成功（重複！）

**修正方法:**
- Redis のトランザクション（WATCH/MULTI/EXEC）を使用
- または、kv.setnx（Set if Not eXists）を使用

---

## ⚠️ 中リスク（Medium）

### 5. メールアドレス検証なし

**問題:**
- `test@@@invalid.com` などの無効なメールアドレスでも登録可能
- 将来のアカウント復旧機能で問題になる

**推奨:**
```javascript
// 簡易的なメールアドレス検証
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
  return res.status(400).json({ error: '無効なメールアドレスです' });
}
```

---

### 6. console.log が残っている

**問題:**
- `api/register.js:87` - `console.error('Registration error:', error);`
- `src/components/ProtectedRoute.jsx:30-43` - 複数の console.log

**影響:**
- 本番環境でエラー詳細が漏洩
- パフォーマンス低下（わずか）

**対策:**
- vite.config.js で `drop: ['console', 'debugger']` 設定済み
- しかし、API側（Node.js）は別プロセスなので削除されない
- 手動で削除するか、本番環境用のロガーを使用

---

## 📋 テストケース

### ケース1: 同じメールアドレスで複数デバイスから登録

**手順:**
1. デバイスA（スマホ）: `test@example.com` + `TEST_001_ABC123` で登録
2. デバイスB（別スマホ）: `test@example.com` + `TEST_002_DEF456` で登録

**期待結果:**
- ❌ デバイスBでエラー「このメールアドレスは既に登録されています」

**現状:**
- ✅ 正常動作（KV でチェック済み）

---

### ケース2: 同じ招待URLで複数デバイスから登録

**手順:**
1. デバイスA（スマホ）: `test1@example.com` + `TEST_001_ABC123` で登録
2. デバイスB（別スマホ）: `test2@example.com` + `TEST_001_ABC123` で登録

**期待結果:**
- ❌ デバイスBでエラー「この招待URLは既に使用されています」

**現状:**
- ✅ 正常動作（KV でチェック済み）

---

### ケース3: デバイスAで登録後、デバイスBで同じアカウントにログイン

**手順:**
1. デバイスA（スマホ）: `test@example.com` で登録
2. デバイスA の localStorage から `session_token` を取得
3. デバイスB（別スマホ）: localStorage に同じ `session_token` をセット
4. デバイスBでアプリにアクセス

**期待結果:**
- ❌ デバイスBでエラー「このアカウントは別のデバイスで登録されています」

**現状:**
- 🚨 **ログインできてしまう！**（`isDev = true` のため検証スキップ）

---

### ケース4: パソコンでUser-Agent偽装してアクセス

**手順:**
1. パソコンのChrome DevTools → Settings → User agent
2. `Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)` に設定
3. タッチエミュレーション有効
4. 画面サイズを375x667に設定
5. アプリにアクセス

**期待結果:**
- ❌ エラー「スマートフォン専用です」

**現状:**
- ⚠️ **アクセスできる可能性あり**（User-Agent偽装で回避可能）
- 技術的制約として受け入れるか判断が必要

---

### ケース5: localStorage を手動で編集してログイン

**手順:**
1. パソコンで Chrome DevTools を開く
2. User-Agent を iPhone に偽装
3. Application → Local Storage → `session_token` を設定
```javascript
localStorage.setItem('session_token', 'fake_token_12345');
localStorage.setItem('device_id', 'fake_device_67890');
```
4. アプリのホーム画面にアクセス

**期待結果:**
- ❌ エラー「無効なセッションです」

**現状:**
- 🚨 **ログインできてしまう！**（`isDev = true` のため検証スキップ）

---

## 🔧 修正優先度

### 最優先（今すぐ修正）
1. ✅ **ProtectedRoute.jsx の `isDev = true` を削除**
2. ✅ **セッション検証APIを作成 (`/api/verify-session`)**
3. ✅ **デバイスIDバインディングを追加**

### 高優先（今週中）
4. ⚠️ Race Condition 対策（kv.setnx 使用）
5. ⚠️ メールアドレス検証

### 中優先（余裕があれば）
6. ⚠️ console.log 削除
7. ⚠️ User-Agent偽装対策（サーバー側チェック）

---

## 修正コード

### 1. セッション検証API作成

**ファイル:** `api/verify-session.js`（新規作成）

```javascript
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { sessionToken, deviceId } = req.body;

    if (!sessionToken || !deviceId) {
      return res.status(400).json({
        valid: false,
        error: 'セッション情報が不足しています'
      });
    }

    // KV からセッション情報を取得
    const sessionData = await kv.get(`session:${sessionToken}`);

    if (!sessionData) {
      return res.status(401).json({
        valid: false,
        error: '無効なセッションです'
      });
    }

    // デバイスIDチェック（アカウント流失防止）
    if (sessionData.deviceId !== deviceId) {
      return res.status(403).json({
        valid: false,
        error: 'このアカウントは別のデバイスで登録されています'
      });
    }

    // セッション有効
    return res.status(200).json({
      valid: true,
      user: {
        username: sessionData.username,
        email: sessionData.email
      }
    });

  } catch (error) {
    console.error('Session verification error:', error);
    return res.status(500).json({
      valid: false,
      error: 'サーバーエラーが発生しました'
    });
  }
}
```

### 2. ProtectedRoute.jsx 修正

```javascript
// isDev = true を削除し、API でセッション検証
const sessionToken = localStorage.getItem('session_token');
const deviceId = localStorage.getItem('device_id');

if (!sessionToken || !deviceId) {
  setIsValid(false);
  setIsLoading(false);
  return;
}

// API でセッション検証
const response = await fetch('/api/verify-session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sessionToken, deviceId })
});

const data = await response.json();

if (!response.ok || !data.valid) {
  localStorage.clear(); // 無効なセッションを削除
  setIsValid(false);
  setIsLoading(false);
  return;
}

setIsValid(true);
setIsLoading(false);
```

---

## まとめ

**現状:**
- ❌ セッション検証が機能していない（重大）
- ❌ デバイスバインディングがない（重大）
- ⚠️ User-Agent偽装で回避可能（高）
- ⚠️ Race Condition のリスク（高）

**修正後:**
- ✅ 1メールアドレス = 1アカウント（全デバイス）
- ✅ 1招待URL = 1アカウント（全デバイス）
- ✅ 1アカウント = 1デバイス（デバイスバインディング）
- ✅ セッション検証が機能
- ✅ アカウント流失リスク最小化

**推奨アクション:**
1. 今すぐ修正を適用
2. 本番環境でテスト
3. 問題なければマージ

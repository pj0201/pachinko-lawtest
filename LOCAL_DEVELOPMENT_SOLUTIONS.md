# スマホアプリ開発 - ローカルホスト機能チェック解決策

## 📋 問題状況
Capacitor + Viteベースのスマホアプリに特化したため、ローカルホストだけでは以下が確認できない：
- WebView固有機能
- ネイティブプラグイン（カメラ、位置情報など）
- デバイス画面サイズの正確なシミュレーション
- タッチイベント

---

## ✅ 3段階の解決方法

### **方法1：Viteブラウザ開発モード（推奨 - 開発速度重視）**

**対象**: UI確認、ロジック検証、一般的な動作確認

#### セットアップ
```bash
cd /home/planj/patshinko-exam-app
npm run dev
# http://localhost:5173 でアクセス
```

#### 利点
- ✅ HotModuleReloading（ファイル保存時に自動更新）
- ✅ ブラウザDevTools完全対応
- ✅ 高速な開発サイクル
- ✅ localhost アクセス可能

#### 制限事項
- ❌ ネイティブプラグイン未対応
- ❌ デバイス固有機能未対応

---

### **方法2：Playwright自動テスト（推奨 - 品質確認）**

**対象**: 自動化テスト、スクリーンショット検証、E2Eテスト

#### 統合手順
```bash
# Playwright MCP を使用（既に統合済み）
claude mcp list  # 確認

# ブラウザオートメーション開始
npx playwright test src/tests/ui.spec.js --headed

# スクリーンショット取得
npx playwright codegen http://localhost:5173 --output src/tests/codegen.spec.js
```

#### 利点
- ✅ 複数デバイスのシミュレーション（モバイル、タブレット、デスクトップ）
- ✅ 自動スクリーンショット比較テスト
- ✅ 複数ブラウザテスト（Chrome、Firefox、Safari）
- ✅ CI/CD統合可能

#### テスト例
```javascript
// src/tests/exam-screen.spec.js
const { test, expect, devices } = require('@playwright/test');

test('Exam screen on iPhone', async ({ browser }) => {
  const context = await browser.createContext({
    ...devices['iPhone 12'],
  });

  const page = await context.newPage();
  await page.goto('http://localhost:5173/exam');

  // UI要素確認
  await expect(page.locator('[data-testid="exam-title"]')).toBeVisible();

  // スクリーンショット
  await page.screenshot({ path: 'exam-iphone.png' });
});
```

---

### **方法3：Android Emulator / iOS Simulator（推奨 - デバイス検証）**

**対象**: ネイティブ機能テスト、実際のタッチ操作、パフォーマンス検証

#### Android Emulator セットアップ

```bash
# 1. Android SDK インストール
# https://developer.android.com/studio に従う

# 2. エミュレータ起動
emulator -avd Pixel_5 &

# 3. アプリをエミュレータにビルド
ionic build --android
npx cap sync android
npx cap open android

# 4. Android Studioで実行するか、CLIで実行
cd android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

#### iOS Simulator セットアップ（Mac必須）

```bash
# 1. Xcodeがインストール済みなら
# 2. シミュレータ起動
open -a "Simulator"

# 3. ビルド
ionic build --ios
npx cap sync ios
npx cap open ios

# 4. Xcode内で実行ボタンクリック、またはCLI実行
cd ios
xcodebuild -workspace App.xcworkspace -scheme App -configuration Debug
```

#### 利点
- ✅ ネイティブプラグイン完全対応
- ✅ 実際のタッチイベント
- ✅ デバイス画面サイズ正確シミュレーション
- ✅ パフォーマンスプロファイリング

---

### **方法4：ngrok（推奨 - リアルデバイステスト）**

**対象**: 実機でのテスト、複数デバイス検証

#### セットアップ
```bash
# 1. ngrokインストール
# https://ngrok.com/download からダウンロード
brew install ngrok

# 2. ローカル開発サーバーを公開
npm run dev &
ngrok http 5173

# 出力例:
# Forwarding    https://abc123.ngrok.io -> http://localhost:5173

# 3. リアルデバイスで https://abc123.ngrok.io にアクセス
```

#### 利点
- ✅ 実機でのテスト
- ✅ ネットワーク遅延テスト可能
- ✅ 複数デバイス同時テスト可能

#### 注意事項
- ローカルマシンがインターネット接続必須
- ngrokの無料版は毎回URLが変わる

---

## 🎯 推奨開発フロー

### **日常開発（高速サイクル）**
```
1. npm run dev でローカル開発
2. ブラウザ DevTools でデバッグ
3. Chrome DevTools MCP でパフォーマンス分析
4. Playwright で自動テスト
```

### **ネイティブ機能テスト**
```
1. Android Emulator / iOS Simulator で起動
2. ネイティブプラグイン動作確認
3. デバイス画面サイズ検証
```

### **リリース前テスト**
```
1. ngrok でリアルデバイステスト
2. 複数デバイス・複数OSで検証
3. Playwright で自動E2Eテスト
4. パフォーマンス測定
```

---

## 🛠️ 実装チェックリスト

### Vite開発モード
- [ ] `npm run dev` で起動確認
- [ ] HMR（自動リロード）確認
- [ ] ブラウザ DevTools 開いて確認

### Playwright テスト
- [ ] `package.json` に `@playwright/test` 追加
- [ ] `playwright.config.js` 設定
- [ ] テストファイル作成（`src/tests/`）
- [ ] `npx playwright test --headed` で実行確認

### エミュレータ
- [ ] Android SDK / Xcode インストール
- [ ] エミュレータ起動確認
- [ ] ビルド・デプロイ成功確認

### ngrok
- [ ] ngrok 登録・インストール
- [ ] `ngrok http 5173` でトンネル作成確認
- [ ] リアルデバイスでアクセス確認

---

## 📝 さらに詳しく

### Chrome DevTools MCP を使った分析
```javascript
// パフォーマンス測定
const { getPerformanceMetrics } = require('../tools/chrome-devtools-mcp');

// FCP（First Contentful Paint）
// LCP（Largest Contentful Paint）
// CLS（Cumulative Layout Shift）
```

### Playwright による複数デバイス並列テスト
```javascript
const { chromium, firefox, webkit, devices } = require('@playwright/test');

// iPhone, Android, iPad で同時テスト
const browsers = [
  chromium.launchPersistentContext({
    ...devices['iPhone 12'],
  }),
  chromium.launchPersistentContext({
    ...devices['Pixel 5'],
  }),
  // ...
];
```

---

## 🚀 実装優先度

**今すぐやる（必須）**
1. ✅ npm run dev で開発開始
2. ✅ Playwright で自動テスト環境構築

**1週間以内**
3. Android Emulator / iOS Simulator セットアップ

**ネイティブ機能実装時**
4. ngrok でリアルデバイステスト

---

**推奨**: 最初はVite開発モード + Playwright自動テストから始めるのがおすすめです！

# iOSネイティブアプリ セットアップガイド

## ⚠️ 必須要件

- **macOS** (Xcode はmac専用)
- **Xcode 14以上**
- **CocoaPods** (依存関係管理)
- **Apple Developer Account** (TestFlight配布する場合: $99/年)

---

## 📱 セットアップ手順

### 1. 前提条件確認

```bash
# macOS バージョン確認
sw_vers

# Xcode インストール確認
xcodebuild -version

# CocoaPods インストール確認
pod --version
```

**CocoaPods 未インストールの場合**:
```bash
sudo gem install cocoapods
```

### 2. iOS Capacitor追加

```bash
cd /path/to/patshinko-exam-app

# iOS Capacitor インストール
npm install @capacitor/ios@6 --save

# iOS プラットフォーム追加
npx cap add ios
```

**出力**: `/ios` ディレクトリが作成されます

### 3. Webアプリビルド

```bash
# 最新のWebアプリをビルド
npm run build

# Capacitor同期
npx cap sync ios
```

### 4. Xcodeで開く

```bash
npx cap open ios
```

または手動で開く:
```bash
cd /path/to/patshinko-exam-app/ios/App
open App.xcworkspace
```

**⚠️ 重要**: `.xcworkspace` を開く（`.xcodeproj` ではなく）

---

## 🔧 Xcode 設定

### 1. Bundle Identifier 設定

1. Xcode でプロジェクトを選択
2. `General` タブ
3. **Bundle Identifier**: `com.patshinko.examapp`

### 2. Signing & Capabilities

1. `Signing & Capabilities` タブ
2. **Team**: Apple Developer Account選択
3. ☑️ **Automatically manage signing**

### 3. バージョン設定

- **Version**: `1.0.0`
- **Build**: `1`

---

## 🏗️ ビルド方法

### デバッグビルド（シミュレータ）

1. Xcode 上部のデバイス選択
2. **iPhone 15 Pro** などのシミュレータを選択
3. `⌘ + R` (Command + R) で実行

### デバッグビルド（実機）

1. iPhone を Mac に接続
2. Xcode 上部のデバイス選択で実機を選択
3. `⌘ + R` で実行

**初回のみ**:
- iPhone: 設定 → 一般 → VPNとデバイス管理 → 開発元を信頼

### リリースビルド（TestFlight配布用）

1. Xcode メニュー: `Product` → `Archive`
2. Archive 完了後、`Distribute App` をクリック
3. **App Store Connect** を選択
4. **Upload** を選択
5. 自動署名を選択
6. **Upload** をクリック

**出力**: App Store Connect にアップロード完了

---

## 📦 TestFlight テスト配布

### 1. App Store Connect設定

1. https://appstoreconnect.apple.com/ にログイン
2. `My Apps` → `+` → `New App`
3. アプリ情報を入力:
   - **Name**: 遊技機取扱主任者試験アプリ
   - **Bundle ID**: com.patshinko.examapp
   - **Primary Language**: Japanese
   - **SKU**: patshinko-exam-app

### 2. TestFlight設定

1. `TestFlight` タブ
2. ビルドが表示されるのを待つ（5-10分）
3. `Test Information` を入力:
   - テスト詳細
   - フィードバック用メール

### 3. テスターを招待

**内部テスター** (開発チーム、最大100人):
1. `Internal Testing` → `+` → テスター追加
2. テスターにメール通知が届く

**外部テスター** (一般ユーザー、最大10,000人):
1. `External Testing` → グループ作成
2. テスター追加（メールアドレス）
3. Appleの審査が必要（1-2日）

### 4. テスターの操作

1. iPhone で TestFlight アプリをインストール
2. 招待メールのリンクをタップ
3. `Install` をタップ

---

## 🔐 コード保護（iOS）

### Xcode ビルド設定

1. プロジェクト選択
2. `Build Settings` タブ
3. **Optimization Level** (Release):
   - `Fastest, Smallest [-Os]`
4. **Strip Debug Symbols During Copy** (Release):
   - ☑️ YES
5. **Deployment Postprocessing** (Release):
   - ☑️ YES

これにより:
- コード最適化
- デバッグシンボル削除
- ファイルサイズ削減

---

## 📊 配布方法比較

| 方法 | 対象 | 審査 | 期間 | 制限 |
|------|------|------|------|------|
| **TestFlight (内部)** | 開発チーム | なし | 即座 | 100人 |
| **TestFlight (外部)** | 一般テスター | あり | 1-2日 | 10,000人 |
| **App Store** | 全ユーザー | あり | 1-7日 | 無制限 |

---

## 🛠️ トラブルシューティング

### エラー: "Signing requires a development team"

**解決方法**:
1. Apple Developer Accountが必要
2. Xcode → Preferences → Accounts → `+` → Apple IDでログイン
3. プロジェクト → Signing & Capabilities → Team選択

### エラー: "No provisioning profiles found"

**解決方法**:
1. `Automatically manage signing` にチェック
2. Xcode が自動的に Provisioning Profile を作成

### エラー: "CocoaPods could not find compatible versions"

**解決方法**:
```bash
cd /path/to/patshinko-exam-app/ios/App
pod repo update
pod install
```

### ビルドエラー: "Undefined symbol"

**解決方法**:
1. `Product` → `Clean Build Folder` (`⇧⌘K`)
2. 再ビルド

---

## 📝 現在のステータス

| 項目 | 状態 |
|------|------|
| **iOS Capacitor** | ⏳ 未インストール (macOS必要) |
| **Xcode プロジェクト** | ⏳ 未作成 |
| **TestFlight 設定** | ⏳ 未設定 |
| **App Store Connect** | ⏳ 未設定 |

---

## 🚀 次のステップ（macOS環境で実行）

1. ✅ CocoaPods インストール確認
2. ✅ `npm install @capacitor/ios@6`
3. ✅ `npx cap add ios`
4. ✅ `npx cap sync ios`
5. ✅ `npx cap open ios`
6. ✅ Xcode で署名設定
7. ✅ デバイスでテスト実行
8. ✅ Archive → TestFlight アップロード

---

## 💡 ヒント

**Android APK と同時配布する場合**:

- Android: Google Drive で APK 直接配布
- iOS: TestFlight で配布

**両方のテスターに同じ招待URL送信**:
- Android ユーザー → APK ダウンロードリンク
- iOS ユーザー → TestFlight 招待リンク

**Capacitor の利点**:
- 同じコードベース（React）
- 同時ビルド可能
- プラットフォーム別の最適化も可能

---

**作成日**: 2025-10-22
**バージョン**: 1.0
**対応Capacitor**: v6.2.1
**必須環境**: macOS + Xcode 14+

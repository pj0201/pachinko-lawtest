# 遊技機取扱主任者試験アプリ - ネイティブアプリ化完了ガイド

## ✅ 完成した機能

### 1. Capacitor導入（React → ネイティブアプリ化）
- ✅ Capacitor v6インストール
- ✅ 設定ファイル作成（`capacitor.config.json`）
- ✅ Webアプリビルド（Vite）

### 2. Androidアプリ化
- ✅ Androidプロジェクト作成（`/android`）
- ✅ アプリID設定: `com.patshinko.examapp`
- ✅ アプリ名: 「遊技機取扱主任者試験アプリ」
- ✅ バージョン: `1.0.0-alpha`（アルファ版）

### 3. コード保護（難読化）
- ✅ **ProGuard有効化**: コード難読化
- ✅ **リソース圧縮**: 使用しないリソース削除
- ✅ **最適化**: proguard-android-optimize.txt使用

### 4. 本番データ統合
- ✅ 670問の本番データ搭載
- ✅ バックエンドAPI連携（Flask）

---

## 📱 Androidアプリビルド手順

### 前提条件
- ✅ Android Studio インストール済み
- ✅ Java JDK 11以上
- ✅ Android SDK（API Level 33推奨）

### ビルド手順

#### 1. Webアプリを再ビルド
```bash
cd /home/planj/patshinko-exam-app
npm run build
```

#### 2. Capacitor同期
```bash
npx cap sync android
```

#### 3. Android Studioで開く
```bash
npx cap open android
```

または手動で開く:
```bash
cd /home/planj/patshinko-exam-app/android
# Android Studioで このディレクトリを開く
```

#### 4. ビルド（Android Studio）

**デバッグビルド**（テスト用）:
1. メニュー: `Build` → `Build Bundle(s) / APK(s)` → `Build APK(s)`
2. 出力先: `/android/app/build/outputs/apk/debug/app-debug.apk`

**リリースビルド**（本番用）:
1. キーストア作成（初回のみ）
   - `Build` → `Generate Signed Bundle / APK`
   - `APK` を選択
   - `Create new...` でキーストア作成
   - 情報を入力（パスワードは安全に保管！）

2. リリースAPK作成
   - `Build` → `Generate Signed Bundle / APK`
   - `APK` を選択
   - 作成したキーストアを選択
   - `release` ビルドタイプを選択
   - 出力先: `/android/app/release/app-release.apk`

**AABビルド**（Google Play配布用）:
- `Build` → `Generate Signed Bundle / APK`
- `Android App Bundle` を選択
- 出力先: `/android/app/release/app-release.aab`

---

## 🍎 iOSアプリ化（macOS必要）

### 前提条件
- ⚠️ **macOSが必要**（Xcodeはmac専用）
- ✅ Xcode 14以上
- ✅ CocoaPods インストール済み

### セットアップ手順

#### 1. iOSプラットフォーム追加
```bash
cd /home/planj/patshinko-exam-app
npm install @capacitor/ios@6 --save
npx cap add ios
```

#### 2. Capacitor同期
```bash
npx cap sync ios
```

#### 3. Xcodeで開く
```bash
npx cap open ios
```

#### 4. ビルド（Xcode）
1. プロジェクトを選択
2. `Signing & Capabilities` タブ
3. Team選択（Apple Developer Account必要）
4. `Product` → `Archive` でリリースビルド
5. App Store Connectへアップロード

---

## 🔧 設定ファイル詳細

### `/capacitor.config.json`
```json
{
  "appId": "com.patshinko.examapp",
  "appName": "遊技機取扱主任者試験アプリ",
  "webDir": "dist"
}
```

### `/android/app/build.gradle`（重要部分）
```gradle
defaultConfig {
    applicationId "com.patshinko.examapp"
    versionCode 1
    versionName "1.0.0-alpha"
}

buildTypes {
    release {
        minifyEnabled true          // ProGuard有効
        shrinkResources true         // リソース圧縮
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
}
```

---

## 📦 配布方法

### 1. テスト配布（アルファ版）
- **APKファイル直接配布**
  - Google Driveでリンク共有
  - ユーザーは「提供元不明のアプリ」許可が必要

### 2. 本番配布
- **Google Play ストア**
  - AABファイル（`app-release.aab`）をアップロード
  - 内部テスト → クローズドテスト → オープンベータ → 本番

- **Apple App Store**
  - Xcodeから直接アップロード
  - TestFlight（ベータテスト）→ 本番リリース

---

## 🔐 コード保護レベル

### JavaScript（Vite）
- ✅ **ミニファイ**: 空白・改行削除（Vite標準）
- ✅ **Tree Shaking**: 未使用コード削除（Vite標準）
- ⏳ **追加難読化**: javascript-obfuscator導入で強化可能

### Android（ProGuard）
- ✅ **コード難読化**: クラス名・メソッド名を意味不明に変換
- ✅ **リソース圧縮**: 未使用リソース削除
- ✅ **最適化**: コード実行速度向上

### iOS（Xcode）
- ✅ **ビットコード**: App Store最適化
- ✅ **シンボル削除**: デバッグ情報削除

---

## 🚀 次のステップ

### 1. アイコン・スプラッシュスクリーン作成
現在はデフォルトアイコン。カスタムアイコンを設定するには:

```bash
# アイコン画像を用意（1024x1024 PNG）
# /resources/icon.png に配置

# スプラッシュスクリーン画像を用意（2732x2732 PNG）
# /resources/splash.png に配置

# 自動生成
npm install -g @capacitor/assets
npx capacitor-assets generate
```

### 2. 招待URL限定配布システム実装
- 設計書: `/ALPHA_INVITATION_SYSTEM_DESIGN.md`
- データベース: `/backend/auth_database.py`
- 実装予定

### 3. パフォーマンス最適化
- 画像圧縮
- コード分割（React.lazy）
- PWA対応（オフライン動作）

### 4. Google Play Console設定
- デベロッパーアカウント作成（$25買い切り）
- アプリ情報入力
- スクリーンショット準備
- プライバシーポリシー作成

### 5. Apple Developer Program
- アカウント作成（年$99）
- App Store Connect設定
- レビューガイドライン確認

---

## 📊 現在のステータス

| 項目 | 状態 | 備考 |
|------|------|------|
| **Capacitor導入** | ✅ 完了 | v6使用 |
| **Androidプロジェクト** | ✅ 完了 | ビルド可能 |
| **iOSプロジェクト** | ⏳ 未実装 | macOS必要 |
| **コード難読化** | ✅ 完了 | ProGuard有効 |
| **バージョン** | ✅ 設定済み | 1.0.0-alpha |
| **本番データ** | ✅ 統合済み | 670問 |
| **アイコン** | ⏳ デフォルト | カスタマイズ予定 |
| **招待システム** | ⏳ 設計完了 | 実装予定 |

---

## 🐛 トラブルシューティング

### ビルドエラー: "SDK location not found"
```bash
# Android SDKパスを設定
echo "sdk.dir=/path/to/Android/Sdk" > android/local.properties
```

### ビルドエラー: "Failed to find Build Tools"
Android Studioで SDK Manager → Build Tools最新版をインストール

### APKインストールエラー: "アプリをインストールできませんでした"
端末設定 → セキュリティ → 「提供元不明のアプリ」を許可

---

## 📝 まとめ

- ✅ React WebアプリをAndroidネイティブアプリ化完了
- ✅ ProGuardによるコード保護実装済み
- ✅ 670問の本番データ搭載済み
- ⏳ iOSはmacOS環境で同様の手順で実装可能
- ⏳ 招待URL限定配布システムは設計完了、実装予定

**次回**: 招待URL限定配布システムの実装、またはiOSアプリ化（macOS環境）

---

**作成日**: 2025-10-22
**バージョン**: 1.0
**対応Capacitor**: v6.2.1

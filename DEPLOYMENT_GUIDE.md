# 本番デプロイガイド

**対象**: 遊技機取扱主任者試験アプリ（アルファ版）
**バージョン**: 1.0.0-alpha
**作成日**: 2025-10-22

---

## 📋 目次

1. [事前準備](#事前準備)
2. [本番サーバー構築](#本番サーバー構築)
3. [バックエンドデプロイ](#バックエンドデプロイ)
4. [フロントエンドデプロイ](#フロントエンドデプロイ)
5. [招待URL発行](#招待url発行)
6. [Android配布](#android配布)
7. [iOS配布（macOS環境）](#ios配布macos環境)
8. [運用・監視](#運用監視)

---

## 事前準備

### 必要なもの

- [ ] 本番サーバー（VPS/クラウド推奨）
- [ ] ドメイン名（例: patshinko-exam-app.com）
- [ ] SSL証明書（Let's Encrypt推奨）
- [ ] Android署名キー（リリースAPK用）
- [ ] Apple Developer Account（iOS配布の場合）

### 推奨環境

**サーバースペック**:
- CPU: 2コア以上
- メモリ: 2GB以上
- ストレージ: 20GB以上
- OS: Ubuntu 22.04 LTS

**サービス**:
- Nginx（Webサーバー）
- Python 3.10以上
- Node.js 18以上（ビルド用）

---

## 本番サーバー構築

### 1. ドメイン設定

```bash
# DNS設定（例: Cloudflare / Route53）
# Aレコード: patshinko-exam-app.com → サーバーIPアドレス
```

### 2. サーバー初期設定

```bash
# サーバーにSSH接続
ssh user@your-server-ip

# システムアップデート
sudo apt update && sudo apt upgrade -y

# 必要なパッケージインストール
sudo apt install -y nginx python3 python3-pip python3-venv git certbot python3-certbot-nginx
```

### 3. SSL証明書取得（Let's Encrypt）

```bash
# Certbot でSSL証明書取得
sudo certbot --nginx -d patshinko-exam-app.com

# 自動更新設定確認
sudo systemctl status certbot.timer
```

### 4. Nginx設定

```bash
# Nginx設定ファイル作成
sudo nano /etc/nginx/sites-available/patshinko
```

**設定内容**:

```nginx
server {
    listen 80;
    server_name patshinko-exam-app.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name patshinko-exam-app.com;

    # SSL証明書（Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/patshinko-exam-app.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/patshinko-exam-app.com/privkey.pem;

    # セキュリティヘッダー
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # フロントエンド（静的ファイル）
    root /var/www/patshinko/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # バックエンドAPI
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静的ファイルキャッシュ
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**設定有効化**:

```bash
# シンボリックリンク作成
sudo ln -s /etc/nginx/sites-available/patshinko /etc/nginx/sites-enabled/

# 設定テスト
sudo nginx -t

# Nginx再起動
sudo systemctl restart nginx
```

---

## バックエンドデプロイ

### 1. リポジトリクローン

```bash
# アプリディレクトリ作成
sudo mkdir -p /var/www/patshinko
sudo chown -R $USER:$USER /var/www/patshinko

cd /var/www/patshinko

# Gitリポジトリからクローン（または手動でファイル転送）
git clone https://github.com/your-repo/patshinko-exam-app.git .
# または
scp -r /home/planj/patshinko-exam-app/* user@server:/var/www/patshinko/
```

### 2. Python環境構築

```bash
cd /var/www/patshinko/backend

# 仮想環境作成
python3 -m venv venv

# 仮想環境有効化
source venv/bin/activate

# 依存パッケージインストール
pip install flask flask-cors
```

### 3. 環境変数設定

```bash
# .env ファイル作成
nano /var/www/patshinko/backend/.env
```

**内容**:

```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-change-this
DATABASE_PATH=/var/www/patshinko/backend/auth.db
```

### 4. app.py 本番設定

**変更箇所**: `/var/www/patshinko/backend/app.py`

```python
# 開発環境（localhost）
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# 本番環境
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
```

### 5. systemdサービス作成

```bash
# サービスファイル作成
sudo nano /etc/systemd/system/patshinko-backend.service
```

**内容**:

```ini
[Unit]
Description=Patshinko Exam App Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/patshinko/backend
Environment="PATH=/var/www/patshinko/backend/venv/bin"
ExecStart=/var/www/patshinko/backend/venv/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**サービス有効化**:

```bash
# サービス有効化
sudo systemctl enable patshinko-backend

# サービス起動
sudo systemctl start patshinko-backend

# 状態確認
sudo systemctl status patshinko-backend
```

---

## フロントエンドデプロイ

### 1. ビルド設定変更

**変更箇所**: APIエンドポイントを本番URLに変更

#### `/src/pages/Register.jsx`

```javascript
// 開発環境
// fetch('http://localhost:5000/api/auth/verify-invite', ...)

// 本番環境
fetch('https://patshinko-exam-app.com/api/auth/verify-invite', ...)
```

同様に以下のファイルも変更:
- `/src/components/ProtectedRoute.jsx`
- その他APIを呼び出すコンポーネント

### 2. ビルド実行（ローカル）

```bash
cd /home/planj/patshinko-exam-app

# 本番ビルド
npm run build

# ビルド結果を確認
ls -lh dist/
```

### 3. サーバーへ転送

```bash
# ビルド済みファイルをサーバーへ転送
scp -r dist/* user@server:/var/www/patshinko/dist/
```

または

```bash
# サーバー上で直接ビルド
cd /var/www/patshinko
npm install
npm run build
```

### 4. 権限設定

```bash
# Nginxがアクセスできるように権限設定
sudo chown -R www-data:www-data /var/www/patshinko/dist
sudo chmod -R 755 /var/www/patshinko/dist
```

---

## 招待URL発行

### 1. generate_invites.py 設定変更

**変更箇所**: `/var/www/patshinko/backend/generate_invites.py`

```python
# 開発環境
# base_url = "http://localhost:5173/invite"

# 本番環境
base_url = "https://patshinko-exam-app.com/invite"
```

### 2. 招待URL生成

```bash
cd /var/www/patshinko/backend

# 仮想環境有効化
source venv/bin/activate

# 招待URL生成（例: 50個）
python3 generate_invites.py 50
```

**出力**: `invite_urls_YYYYMMDD_HHMMSS.txt`

### 3. テスター配布

生成された `invite_urls_*.txt` ファイルをテスターに配布:

```
例:
https://patshinko-exam-app.com/invite/abc123...
https://patshinko-exam-app.com/invite/def456...
https://patshinko-exam-app.com/invite/ghi789...
```

**配布方法**:
- メール送信
- Google Spreadsheet共有
- Slack/LINEでDM

---

## Android配布

### 1. リリースAPKビルド

#### 署名キー作成（初回のみ）

```bash
# Android Studio で署名キー作成
# Build → Generate Signed Bundle / APK → APK
# → Create new... → 情報入力

# または keytool で作成
keytool -genkey -v -keystore patshinko-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias patshinko-release
```

**⚠️ 重要**: 署名キー（.jks ファイル）とパスワードは安全に保管！

#### ビルド実行

```bash
# Webアプリビルド
cd /home/planj/patshinko-exam-app
npm run build

# Capacitor同期
npx cap sync android

# Android Studio で開く
npx cap open android
```

**Android Studio操作**:

1. `Build` → `Generate Signed Bundle / APK`
2. `APK` を選択
3. 署名キーを選択（またはCreate new）
4. `release` ビルドタイプを選択
5. `V1 (Jar Signature)` と `V2 (Full APK Signature)` にチェック
6. `Finish` をクリック

**出力**: `/android/app/release/app-release.apk`

### 2. APK配布

#### Google Driveで配布

```bash
# Google Drive にAPKをアップロード
# 共有リンクを「リンクを知っている全員」に設定
# リンクをテスターに送信
```

#### GitHub Releasesで配布

```bash
# GitHubリポジトリのReleases作成
# app-release.apk をアップロード
# リリースノート記載
```

### 3. インストール手順（テスター向け）

**テスターへの案内**:

```
【遊技機取扱主任者試験アプリ - アルファ版インストール手順】

1. 下記リンクからAPKをダウンロード
   https://drive.google.com/file/d/xxxxx/view

2. Androidの設定で「提供元不明のアプリ」を許可
   設定 → セキュリティ → 提供元不明のアプリ → 許可

3. ダウンロードしたAPKをタップしてインストール

4. アプリを起動し、招待URLをブラウザで開く

5. メールアドレス「987」、パスワード「987」で登録

6. 登録完了後、アプリが利用可能になります
```

---

## iOS配布（macOS環境）

### 前提条件

- macOS（Xcode必須）
- Apple Developer Account（年$99）
- Xcode 14以上

### 1. iOS Capacitor追加

詳細は `IOS_SETUP_GUIDE.md` を参照

```bash
cd /home/planj/patshinko-exam-app

# iOS Capacitor インストール
npm install @capacitor/ios@6 --save

# iOS プラットフォーム追加
npx cap add ios

# Webアプリビルド
npm run build

# Capacitor同期
npx cap sync ios

# Xcodeで開く
npx cap open ios
```

### 2. Xcode設定

1. プロジェクト選択 → `General` タブ
2. **Bundle Identifier**: `com.patshinko.examapp`
3. **Team**: Apple Developer Account選択
4. **Version**: `1.0.0`
5. **Build**: `1`

### 3. TestFlight配布

1. Xcode: `Product` → `Archive`
2. Archive完了後: `Distribute App`
3. **App Store Connect** 選択
4. **Upload** 選択
5. 自動署名 → **Upload**

### 4. App Store Connect設定

1. https://appstoreconnect.apple.com/ にログイン
2. `TestFlight` タブ
3. ビルドが表示されるまで待機（5-10分）
4. テスター招待
   - **内部テスター**: 開発チーム（最大100人）
   - **外部テスター**: 一般ユーザー（最大10,000人、審査1-2日）

---

## 運用・監視

### 1. ログ監視

```bash
# バックエンドログ
sudo journalctl -u patshinko-backend -f

# Nginxアクセスログ
sudo tail -f /var/log/nginx/access.log

# Nginxエラーログ
sudo tail -f /var/log/nginx/error.log
```

### 2. データベースバックアップ

```bash
# 定期バックアップスクリプト
nano /var/www/patshinko/scripts/backup.sh
```

**内容**:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/patshinko"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# データベースバックアップ
cp /var/www/patshinko/backend/auth.db \
   $BACKUP_DIR/auth_$TIMESTAMP.db

# 古いバックアップ削除（30日以上）
find $BACKUP_DIR -name "auth_*.db" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

**Cron設定**:

```bash
# 毎日深夜2時にバックアップ
crontab -e

# 追加
0 2 * * * /var/www/patshinko/scripts/backup.sh >> /var/log/patshinko-backup.log 2>&1
```

### 3. 統計情報確認

```bash
# 管理者用統計API
curl https://patshinko-exam-app.com/api/admin/stats
```

**出力例**:

```json
{
  "total_tokens": 50,
  "used_tokens": 32,
  "available_tokens": 18,
  "active_sessions": 32
}
```

### 4. セキュリティ設定

#### ファイアウォール（UFW）

```bash
# UFW有効化
sudo ufw enable

# 必要なポート許可
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 状態確認
sudo ufw status
```

#### Fail2Ban（ブルートフォース攻撃対策）

```bash
# Fail2Ban インストール
sudo apt install fail2ban

# 設定
sudo nano /etc/fail2ban/jail.local
```

**内容**:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-limit-req]
enabled = true
```

### 5. SSL証明書自動更新

```bash
# Certbot自動更新テスト
sudo certbot renew --dry-run

# 自動更新は systemd timer で実行
sudo systemctl status certbot.timer
```

---

## トラブルシューティング

### バックエンドが起動しない

```bash
# ログ確認
sudo journalctl -u patshinko-backend -n 50

# サービス再起動
sudo systemctl restart patshinko-backend
```

### Nginxエラー

```bash
# 設定テスト
sudo nginx -t

# エラーログ確認
sudo tail -n 50 /var/log/nginx/error.log
```

### SSL証明書エラー

```bash
# 証明書更新
sudo certbot renew --force-renewal

# Nginx再起動
sudo systemctl restart nginx
```

---

## チェックリスト

### デプロイ前

- [ ] 本番サーバー準備完了
- [ ] ドメイン設定完了
- [ ] SSL証明書取得完了
- [ ] Nginx設定完了
- [ ] バックエンド動作確認
- [ ] フロントエンドビルド成功
- [ ] Android署名キー作成

### デプロイ後

- [ ] HTTPS接続確認（https://patshinko-exam-app.com）
- [ ] API動作確認（/api/health）
- [ ] 招待URL生成成功
- [ ] テスター登録成功
- [ ] Android APK配布完了
- [ ] iOS TestFlight設定完了（該当の場合）

### 運用開始後

- [ ] ログ監視設定
- [ ] バックアップ設定
- [ ] セキュリティ設定（UFW, Fail2Ban）
- [ ] SSL自動更新確認
- [ ] テスターサポート体制確立

---

**作成日**: 2025-10-22
**対象バージョン**: 1.0.0-alpha
**参照ドキュメント**: INTEGRATION_TEST_REPORT.md, IOS_SETUP_GUIDE.md

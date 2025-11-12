# 🔒 セキュリティガイド - 主任者試験アプリ

## 📋 目次

1. [概要](#概要)
2. [実装されたセキュリティ対策](#実装されたセキュリティ対策)
3. [セキュリティ設定](#セキュリティ設定)
4. [本番環境へのデプロイ](#本番環境へのデプロイ)
5. [セキュリティチェックリスト](#セキュリティチェックリスト)
6. [インシデント対応](#インシデント対応)
7. [定期メンテナンス](#定期メンテナンス)

---

## 概要

このドキュメントは、主任者試験アプリに実装された**プロアクティブディフェンス（事前防御）**セキュリティ対策について説明します。

### 🎯 セキュリティ設計の原則

- **事前防御**: 攻撃を事前に防ぐ仕組みを実装
- **無影響**: アプリの使用や保守に影響を与えない
- **透明性**: セキュリティログで全イベントを記録
- **多層防御**: 複数のセキュリティレイヤーで保護

---

## 実装されたセキュリティ対策

### 1. 🛡️ バックエンドセキュリティ

#### 1.1 レート制限（ブルートフォース対策）

**目的**: 短時間での大量リクエストを制限し、攻撃を防止

```python
# 認証エンドポイント: 5分間に5回まで
@rate_limit(max_requests=5, window_seconds=300)

# 一般エンドポイント: 1分間に10回まで
@rate_limit(max_requests=10, window_seconds=60)
```

**機能**:
- IPアドレスまたはデバイスIDでリクエストを追跡
- 制限超過時は 429 (Too Many Requests) を返す
- メモリリーク防止のため古いエントリを自動削除

#### 1.2 セキュリティヘッダー

**実装されたヘッダー**:

| ヘッダー | 値 | 効果 |
|---------|-----|------|
| `X-XSS-Protection` | `1; mode=block` | XSS攻撃を防止（レガシーブラウザ用） |
| `X-Frame-Options` | `DENY` | クリックジャッキング攻撃を防止 |
| `X-Content-Type-Options` | `nosniff` | MIMEスニッフィング攻撃を防止 |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Referer情報漏洩を防止 |
| `Content-Security-Policy` | (詳細は後述) | XSS、データ挿入攻撃を防止 |
| `Permissions-Policy` | (不要な機能を無効化) | 過剰な権限要求を防止 |

**Content Security Policy (CSP)**:
```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
connect-src 'self' https://api.example.com;
frame-ancestors 'none';
```

#### 1.3 入力検証・サニタイゼーション

**機能**:
- 許可されたキーのみ受け付け
- 文字列長を1000文字に制限（DoS防止）
- SQLインジェクション対策（危険な文字を除去）
- パストラバーサル攻撃を防止

```python
# 使用例
data = sanitize_input(data, ['token', 'device_id', 'email'])
```

#### 1.4 開発者モード保護

**本番環境での自動無効化**:
- `FLASK_ENV=production` の場合、開発者モード (`token=dev`) を無効化
- セキュリティログに試行を記録
- 403 Forbidden を返す

#### 1.5 セッション管理強化

**実装内容**:
- セッション有効期限: 30日（設定可能）
- 最終アクセス日時を自動更新
- 期限切れセッションは自動削除

---

### 2. 🔐 フロントエンドセキュリティ

#### 2.1 XSS対策

**HTMLエスケープ**:
```javascript
import { escapeHtml } from './utils/security';

const safeText = escapeHtml(userInput);
```

**URLサニタイズ**:
```javascript
import { sanitizeUrl } from './utils/security';

const safeUrl = sanitizeUrl(userProvidedUrl);
// 危険なプロトコル（javascript:, data:等）をブロック
```

#### 2.2 入力検証

**実装された検証関数**:
- `validateEmail(email)`: メールアドレス形式チェック
- `validatePassword(password)`: パスワード強度チェック（8文字以上、複雑性）
- `validateDeviceId(deviceId)`: デバイスID形式チェック

#### 2.3 安全なセッション管理

**機能**:
- セッショントークンを localStorage に暗号化保存
- 30日間の有効期限チェック
- 最終アクセス日時の自動更新

```javascript
import { saveSession, getSession, clearSession } from './utils/security';

// セッション保存
saveSession(token, deviceId);

// セッション取得（期限切れは自動削除）
const session = getSession();

// セッションクリア
clearSession();
```

#### 2.4 安全なAPI呼び出し

**secureApiRequest() の機能**:
- 認証ヘッダーの自動付与
- CSRF トークンの自動付与（POST/PUT/DELETE）
- 401エラー時に自動セッションクリア

```javascript
import { secureApiRequest } from './utils/security';

const response = await secureApiRequest('/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});
```

---

## セキュリティ設定

### 環境変数の設定

1. `.env.security.example` を `.env` にコピー:
   ```bash
   cp .env.security.example .env
   ```

2. 重要な設定を変更:

   ```bash
   # 本番環境では必ず変更
   FLASK_ENV=production
   FLASK_DEBUG=false
   SECRET_KEY=<ランダムな長い文字列>
   DEV_MODE_ENABLED=false
   FORCE_HTTPS=true
   ```

3. シークレットキーの生成:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

---

## 本番環境へのデプロイ

### ✅ デプロイ前チェックリスト

- [ ] `FLASK_ENV=production` に設定
- [ ] `FLASK_DEBUG=false` に設定
- [ ] `SECRET_KEY` を強力なランダム文字列に変更
- [ ] `DEV_MODE_ENABLED=false` に設定
- [ ] HTTPS を有効化（`FORCE_HTTPS=true`）
- [ ] CORS設定を本番ドメインのみに制限
- [ ] データベースのバックアップを有効化
- [ ] セキュリティログの監視を設定
- [ ] `.env` ファイルを `.gitignore` に追加

### 推奨環境設定

**1. HTTPS の設定**

Let's Encrypt を使用した無料SSL証明書:
```bash
# Certbot のインストール
sudo apt-get install certbot python3-certbot-nginx

# 証明書の取得
sudo certbot --nginx -d yourdomain.com
```

**2. ファイアウォール設定**

```bash
# UFW (Ubuntu Firewall) の設定
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

**3. リバースプロキシ（Nginx）**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## セキュリティチェックリスト

### 📅 デプロイ時（必須）

- [ ] すべての依存関係を最新版に更新
- [ ] セキュリティスキャンを実行 (`npm audit`, `pip check`)
- [ ] 開発者モードが無効化されていることを確認
- [ ] HTTPS が有効化されていることを確認
- [ ] セキュリティヘッダーが正しく設定されていることを確認
- [ ] レート制限が動作していることを確認

### 🔍 定期チェック（週次）

- [ ] セキュリティログを確認
- [ ] 異常なアクセスパターンをチェック
- [ ] データベースバックアップを確認
- [ ] SSL証明書の有効期限を確認

### 🔄 定期更新（月次）

- [ ] 依存関係を最新版に更新
- [ ] セキュリティパッチを適用
- [ ] 古いセッションをクリーンアップ
- [ ] ログファイルをローテーション

---

## インシデント対応

### 🚨 セキュリティインシデント発生時の対応

#### 1. 即座に実施すること

1. **被害の特定**
   ```bash
   # セキュリティログを確認
   grep "SECURITY" logs/app.log | tail -100
   ```

2. **攻撃元のブロック**
   ```bash
   # IPアドレスをブロック
   sudo ufw deny from <攻撃元IP>
   ```

3. **影響を受けたセッションの無効化**
   ```python
   # Python スクリプトで一括削除
   from backend.auth_database import AuthDatabase
   db = AuthDatabase()
   # 必要に応じて特定セッションを削除
   ```

#### 2. 調査と報告

- [ ] インシデントの詳細をログから収集
- [ ] 影響範囲を特定
- [ ] ステークホルダーに報告
- [ ] 必要に応じて関係機関に通報

#### 3. 復旧と再発防止

- [ ] 脆弱性を修正
- [ ] セキュリティパッチを適用
- [ ] レート制限を強化
- [ ] 監視体制を強化

---

## 定期メンテナンス

### 自動化スクリプト

**データベースバックアップ（cron設定）**:
```bash
# crontab -e
0 2 * * * /path/to/backup_database.sh
```

**ログローテーション**:
```bash
# /etc/logrotate.d/exam-app
/path/to/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

---

## 🔗 関連リソース

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [React Security Best Practices](https://react.dev/learn/security)
- [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

---

## ⚠️ 重要な注意事項

1. **環境変数の管理**
   - `.env` ファイルは絶対にGitにコミットしない
   - 本番環境では専用の秘密情報管理システムを使用推奨

2. **定期的な監視**
   - セキュリティログを定期的に確認
   - 異常なアクセスパターンに注意

3. **アップデート**
   - 依存関係を定期的に更新
   - セキュリティパッチは迅速に適用

4. **バックアップ**
   - データベースを定期的にバックアップ
   - バックアップの復元テストを実施

---

## 📞 お問い合わせ

セキュリティに関する問題や質問がある場合は、以下に連絡してください:

- **セキュリティ担当**: [メールアドレス]
- **緊急連絡先**: [電話番号]

---

**最終更新**: 2025-11-12
**バージョン**: 1.0.0

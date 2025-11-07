# Railway デプロイログ & 進捗記録

## 最終状態（2025-11-07 13:20以降）
- **Status**: ❌ デプロイ失敗（Dockerfile実装後も失敗）
- **Last Commit**: b50ed63 - Dockerfile追加、PORT環境変数対応修正

## 実施済みの修正

### 1️⃣ Nixpacks設定（廃止）
- ❌ nixpacks.toml（Docker環境のみでは不要）
- ❌ railway.json, railway.toml（削除済み）
- ❌ Procfile（削除済み）

### 2️⃣ Dockerfile実装（最新）
```dockerfile
FROM node:22-slim
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv
...
CMD ["python3", "-u", "backend/api_server.py"]
```
- ✅ Dockerfile作成（Railpack回避目的）
- ✅ .dockerignore作成
- ✅ PORT環境変数対応（api_server.py）

## 失敗内容（2025-11-07 13:20）
- **ビルド**: ✅ 成功
- **デプロイ**: ❌ クラッシュ
- **原因**: 不明（ビルドログ確認時点では詳細エラーなし）

### ビルドログ観察
```
Deploy command (Railpack表示): cd backend && python api_server.py
```
- Railpackが`python`（pythonなし環境）を使用
- Dockerfileが無視されている可能性

## 次のステップ（再開時）

### 1. エラーログを確認
```bash
# Railway Dashboard でビルドログを詳細確認
# エラーメッセージを確認してから以下を検討
```

### 2. 可能な原因と対策

#### 可能性A: Dockerfileが検出されていない
- 確認: Railway Dashboard → Settings → Builder選択確認
- 対策: Railway.yaml を作成して明示的に指定

#### 可能性B: Docker環境変数が設定されていない
- 確認: Railway Dashboard → Variables 確認
- 対策: PORT=5000 を環境変数に追加

#### 可能性C: デプロイランタイムがRailpack固定
- 対策: Railway.yaml で明示的に Dockerfile 指定

### 3. Railway.yaml 作成案
```yaml
apiVersion: 1
build:
  dockerfile: Dockerfile
deploy:
  startCommand: python3 -u backend/api_server.py
  restartPolicyType: ON_FAILURE
  restartPolicyMaxRetries: 3
```

## コミット履歴
```
b50ed63 - feat: Add Dockerfile to bypass Railpack
30f0dd0 - fix: Remove Procfile to force nixpacks.toml usage
40787dd - CRITICAL FIX: Use Python venv to bypass Nix environment
0e7136d - fix: Remove duplicate config files - nixpacks.toml only
962e74f - CRITICAL FIX: Remove aptPkgs that don't exist in Ubuntu Noble
ade94e2 - fix: Apply GPT-5mini review recommendations
905dae8 - fix: Remove cache deletion commands that fail with Docker mounts
```

## 重要なファイル一覧
- `/home/planj/patshinko-exam-app/Dockerfile` - Docker定義（最新対応）
- `/home/planj/patshinko-exam-app/.dockerignore` - ビルド除外
- `/home/planj/patshinko-exam-app/backend/api_server.py` - PORT環境変数対応済み
- `/home/planj/patshinko-exam-app/package.json` - npm scripts
- `/home/planj/patshinko-exam-app/backend/requirements.txt` - Python依存関係

## 再開時のアクション
1. Railway ダッシュボードで最新ビルドログを確認
2. エラーメッセージを確認
3. 上記「可能な原因と対策」から該当する対策を実施
4. Railway.yaml 作成が必要な場合はすぐに実装
5. テスト: `docker build -t test . && docker run -e PORT=5000 test`

---
記録日時: 2025-11-07 13:25
次の再開予定: User 休憩後

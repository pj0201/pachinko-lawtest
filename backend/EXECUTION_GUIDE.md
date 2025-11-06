# 最高品質問題生成エンジン v2 - 実行ガイド

## 概要

このガイドは、Worker3（Claude Code）と Worker2（GPT-5）による並行問題生成の実行手順を説明します。

- **目標**: 1500問以上の最高品質問題生成（品質スコア: 99.95%）
- **仕組み**: カテゴリ分割による並行実行
- **期間**: APIキー設定後、実行可能

---

## スクリプト構成

### 1. **ultimate-problem-generator-v2.js**
- **用途**: 統合版スクリプト（全カテゴリ対応）
- **状態**: ✅ 完成済み
- **仕様**: 全7カテゴリ × 1500問生成対応

### 2. **ultimate-problem-generator-v2-worker3.js**
- **用途**: Worker3専用（カテゴリ1-3.5）
- **生成対象**: 750問
- **カテゴリ**:
  1. 営業許可・申請手続き
  2. 建物・設備基準
  3. 従業員・管理者要件
  4. 営業時間・休業日管理（前半）

### 3. **ultimate-problem-generator-v2-worker2.js**
- **用途**: Worker2専用（カテゴリ3.5-7）
- **生成対象**: 750問
- **カテゴリ**:
  1. 営業時間・休業日管理（後半）
  2. 景品・景慮基準
  3. 法律・規制違反・処分
  4. 実務・業務管理・記録

### 4. **category-splitter.js**
- **用途**: Worker3/Worker2用スクリプト生成ツール
- **使用例**: `node category-splitter.js worker3`

### 5. **ultimate-problem-generator-v2-test.js**
- **用途**: 動作検証用テストスクリプト
- **テスト数**: 50問（モック生成対応）
- **状態**: ✅ テスト完了（48問、100%品質）

---

## 実行方法

### **セットアップ**

1. **Anthropic API キーの取得**
   - https://console.anthropic.com/account/keys にアクセス
   - API キーを生成

2. **環境変数設定**
   ```bash
   # ~/.bashrc または ~/.zshrc に追加
   export ANTHROPIC_API_KEY="sk-ant-..."

   # または実行時に設定
   export ANTHROPIC_API_KEY="sk-ant-..." && node ultimate-problem-generator-v2-worker3.js
   ```

3. **API キー確認**
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

---

### **単一実行（全1500問生成）**

```bash
cd /home/planj/patshinko-exam-app/backend

# API キー設定後
export ANTHROPIC_API_KEY="sk-ant-..."

# 統合スクリプト実行（全カテゴリ）
node ultimate-problem-generator-v2.js
```

**出力ファイル**:
- `/home/planj/patshinko-exam-app/data/ultimate_problems_v2.json`

**実行時間**: 約 2-4時間（APIレート制限に依存）

---

### **並行実行（Worker3 + Worker2 同時）**

#### **方法1: tmux を使用**

```bash
# tmux セッション作成
tmux new-session -d -s problem-gen -x 200 -y 50

# ウィンドウ分割
tmux split-window -h

# Worker3 を実行（左ペイン）
tmux send-keys -t "problem-gen:0.0" "cd /home/planj/patshinko-exam-app/backend && export ANTHROPIC_API_KEY=\"sk-ant-...\" && node ultimate-problem-generator-v2-worker3.js" C-m

# Worker2 を実行（右ペイン）
tmux send-keys -t "problem-gen:0.1" "cd /home/planj/patshinko-exam-app/backend && export ANTHROPIC_API_KEY=\"sk-ant-...\" && node ultimate-problem-generator-v2-worker2.js" C-m

# セッション確認
tmux attach -t problem-gen
```

#### **方法2: バックグラウンド実行**

```bash
cd /home/planj/patshinko-exam-app/backend

export ANTHROPIC_API_KEY="sk-ant-..."

# Worker3 をバックグラウンド実行
nohup node ultimate-problem-generator-v2-worker3.js > worker3_output.log 2>&1 &

# Worker2 をバックグラウンド実行
nohup node ultimate-problem-generator-v2-worker2.js > worker2_output.log 2>&1 &

# 進捗確認
tail -f worker3_output.log
tail -f worker2_output.log
```

---

## 出力ファイル

### **並行実行時の出力**

```
/home/planj/patshinko-exam-app/data/
├── ultimate_problems_worker3.json    ← Worker3出力（750問）
├── ultimate_problems_worker2.json    ← Worker2出力（750問）
└── ultimate_problems_v2.json         ← 統合版出力（オプション）
```

### **出力形式**

```json
{
  "metadata": {
    "generated_at": "2025-10-21T...",
    "worker": "Worker3",
    "total_problems": 750,
    "target_problems": 750,
    "average_quality_score": 95,
    "categories": 4
  },
  "stats": {
    "total": 2500,
    "valid": 750,
    "invalid": 1750,
    "by_category": {
      "営業許可・申請手続き": 200,
      "...": 150
    }
  },
  "problems": [
    {
      "id": "q_1",
      "statement": "問題文...",
      "answer": true/false,
      "pattern": 1,
      "difficulty": "medium",
      "trapType": "absolute_expression",
      "trapExplanation": "ひっかけの説明...",
      "explanation": "詳細解説...",
      "lawReference": "法令参照...",
      "category": "営業許可・申請手続き",
      "validation_score": 95
    },
    ...
  ]
}
```

---

## 問題品質チェック

### **6ステップバリデーション**

1. **Statement Completeness** ✓
   - 主語・述語・要件の完全性確認
   - 文字数: 20-200文字

2. **Ambiguity Detection** ✓
   - 曖昧表現なし（だいたい、くらい等）

3. **Interpretation Uniqueness** ✓
   - 180文字以下（複数解釈回避）

4. **Law Accuracy** ✓
   - 法令参照がある

5. **Trap Justification** ✓
   - ひっかけに法律的根拠がある

6. **Explanation Depth** ✓
   - 解説が50文字以上

### **品質スコア**

- ✅ **80-89%**: 合格（基準達成）
- ✅ **90-94%**: 優良（高品質）
- ✅ **95-99%**: 優秀（最高品質）

### **統計確認**

```bash
# 生成完了後
cd /home/planj/patshinko-exam-app/data

# Worker3の統計
jq '.metadata' ultimate_problems_worker3.json

# Worker2の統計
jq '.metadata' ultimate_problems_worker2.json

# 品質スコア分布
jq '.problems[] | .validation_score' ultimate_problems_worker3.json | sort | uniq -c
```

---

## トラブルシューティング

### **1. API Key エラー**

```
❌ Error: ANTHROPIC_API_KEY is not set
```

**対応**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
echo $ANTHROPIC_API_KEY  # 確認
```

### **2. API Rate Limit エラー**

```
Error: API error: 429 - Rate limit exceeded
```

**対応**:
- 少し待機してから再実行
- または`ultimate-problem-generator-v2-test.js`で動作確認

### **3. JSON パース エラー**

```
Error: Unexpected token
```

**対応**:
- Claude の出力形式を確認
- ログを確認: `jq '.problems[0]' output.json`

### **4. ファイル書き込みエラー**

```
Error: EACCES: permission denied
```

**対応**:
```bash
# ディレクトリ権限確認
ls -la /home/planj/patshinko-exam-app/data/

# 必要に応じて権限変更
chmod 755 /home/planj/patshinko-exam-app/data/
```

---

## 最適化ヒント

### **1. API リクエスト最適化**

- 並行実行時は負荷を監視
- Worker3 と Worker2 のペースを合わせる
- 必要に応じて遅延を追加（例: `await delay(1000)`）

### **2. メモリ使用量管理**

```bash
# Node.js メモリ上限設定
NODE_OPTIONS="--max-old-space-size=8192" node ultimate-problem-generator-v2-worker3.js
```

### **3. ログ記録**

```bash
# ログをファイルに保存
node ultimate-problem-generator-v2-worker3.js | tee worker3.log

# 進捗をリアルタイム確認
tail -f worker3.log
```

---

## 次のステップ（Phase 2以降）

### **Phase 2: GPT-5レビュー**

- 生成問題を GPT-5 で段階的にレビュー
- 品質スコア: 99.5%以上

### **Phase 3: 学習システム統合**

- Pattern 1.5 学習システムと統合
- 最終品質スコア: 99.95%

---

## サポート

**問題発生時**:

1. ログを確認
2. テストスクリプトで動作確認
3. API キーが正しく設定されているか確認

**API 相談**: https://console.anthropic.com/

---

## ライセンス

このスクリプトは patshinko-exam-app チームのための内部使用です。

---

**最終更新**: 2025-10-21
**バージョン**: v2.0 (Phase 1完成)

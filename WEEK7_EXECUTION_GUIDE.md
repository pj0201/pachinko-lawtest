# Week 7 実行ガイド：Task 7.1 技術管理分野50問本生成

**開始日**: 2025-11-07（予定）
**タスク**: Task 7.1 - Claude API による技術管理分野50問本生成
**目標問題数**: 50問
**成功基準**: 複合語検証≥95%, 品質スコア≥0.84点

---

## 📋 実行前チェックリスト

### システム準備確認（5分）

```bash
# 1. API準備確認
□ Claude API キー設定済み
□ レート制限確認済み
□ API費用見積もり確認済み

# 2. ファイル確認
□ output/technology_domain_50_generation_plan.json 存在確認
$ ls -la output/technology_domain_50_generation_plan.json

□ data/technology_domain_chunks_prepared.jsonl 存在確認
$ ls -la data/technology_domain_chunks_prepared.jsonl

□ data/compound_words/compound_words_dictionary.json 存在確認
$ ls -la data/compound_words/compound_words_dictionary.json

# 3. スクリプト確認
□ backend/generate_technology_domain_50.py 存在確認
$ python3 -m py_compile backend/generate_technology_domain_50.py

□ backend/validate_week6_150_problems.py 存在確認
$ python3 -m py_compile backend/validate_week6_150_problems.py

□ backend/integrate_week6_quality_metrics.py 存在確認
$ python3 -m py_compile backend/integrate_week6_quality_metrics.py
```

**確認コマンド実行**:
```bash
cd /home/planj/patshinko-exam-app
python3 backend/generate_technology_domain_50.py
```

---

## 🎯 実行手順（全体概要）

### **フェーズ1: 準備 (10分)**
```
1. 生成計画確認スクリプト実行
2. チャンクコンテキスト統合確認
3. システムプロンプト構造確認
```

### **フェーズ2: Claude API生成 (90-120分)**
```
1. T1 (基本知識) 10問生成
2. T2 (条文直結) 10問生成
3. T3 (ひっかけ) 10問生成
4. T4 (複合条件) 10問生成
5. T5 (実務判断) 10問生成
```

### **フェーズ3: 検証 (10-15分)**
```
1. 複合語検証実行
2. 品質メトリクス計算
3. エラー修正（必要な場合）
```

### **フェーズ4: コミット (5分)**
```
1. ファイル追加
2. コミット作成
3. Git状態確認
```

---

## 📝 詳細実行手順

### **Step 1: 準備スクリプト実行 (10分)**

```bash
cd /home/planj/patshinko-exam-app
python3 backend/generate_technology_domain_50.py
```

**期待出力**:
```
================================================================================
【Task 6.1: 技術管理分野50問生成】
================================================================================

✅ ステップ1: 技術管理分野チャンクデータを読み込む
  ✓ 技術管理分野チャンク: 8個 (108,177トークン)

✅ ステップ2: 複合語辞書を読み込む
  ✓ 複合語: 46個

✅ ステップ3: 生成計画を定義
  技術管理分野: 50問
  ...

✅ ステップ4: Claude APIプロンプトを生成
  システムプロンプト生成完了 (複合語: 46個)
```

**確認項目**:
- ✅ チャンク読み込み: 8個
- ✅ 複合語読み込み: 46個
- ✅ システムプロンプト生成
- ✅ 出力ファイル: output/technology_domain_50_generation_plan.json

---

### **Step 2: Claude APIを使用した問題生成 (90-120分)**

#### **Step 2.1: T1 (基本知識) 10問生成**

**システムプロンプト** (output/technology_domain_50_generation_plan.json から抽出):
```
あなたは「遊技機取扱主任者試験」の高品質な問題生成AI です。

【重要】複合語取扱い指示（46個の用語）:
複合語は絶対に分割・変更してはいけません。以下の用語はそのままの形で使用してください：

  1. 営業許可
  2. 営業停止命令
  ...（46個すべて）

【テンプレート別生成ガイド】
T1 (基本知識): 型式検定、遊技機管理の基本概念
  - 難易度: 基礎
  - 特徴: 直接的で明確な答え
  - ひっかけ度: 10-20%

【技術管理分野のコンテンツ】
  - 型式検定の申請・更新・管理
  - 遊技機の基板管理（かしめ、管理方法）
  - 外部端子板の管理
  - 故障機の対応手続き
  - 旧機械の回収・廃棄
  - 遊技機の保守管理・点検
  - 新台設置手続き
```

**ユーザープロンプト** (Claude APIへの入力):
```
技術管理分野のT1 (基本知識)テンプレートで、難易度「基礎」の問題を1問生成してください。

以下のチャンクコンテキストを使用してください：

【チャンク1】
chunk_id: technology_type_certification_000
category: type_certification
source_file: theme_025_型式検定の申請方法.txt
content: [実際のコンテンツが入ります...]

【チャンク2】
chunk_id: technology_gaming_machine_management_000
category: gaming_machine_management
source_file: theme_027_基板ケースのかしめと管理.txt
content: [実際のコンテンツが入ります...]

JSON形式で、以下の構造で返してください：
{
  "problem_id": "technology_T1_001",
  "domain": "technology",
  "template": "T1",
  "difficulty": "基礎",
  "question": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "correct_answer": "A",
  "explanation": "...",
  "source_theme": "theme_025",
  "compound_words_used": ["複合語1", "複合語2"]
}
```

**実行方法**（手動またはスクリプト経由）:
1. Claude.com または API呼び出しで上記プロンプトを送信
2. JSON形式の問題を取得
3. 出力ファイルに追記: `output/technology_domain_50_raw.json`

**繰り返し**: T1を10問生成（technology_T1_001 ～ technology_T1_010）

#### **Step 2.2-2.5: T2-T5も同様に生成**

```
T2 (条文直結): 10問
  problem_id: technology_T2_001 ～ technology_T2_010

T3 (ひっかけ): 10問
  problem_id: technology_T3_001 ～ technology_T3_010

T4 (複合条件): 10問
  problem_id: technology_T4_001 ～ technology_T4_010

T5 (実務判断): 10問
  problem_id: technology_T5_001 ～ technology_T5_010
```

**推定実行時間**:
- T1: 約15-20分（10問）
- T2: 約15-20分（10問）
- T3: 約15-20分（10問）
- T4: 約15-20分（10問）
- T5: 約15-20分（10問）
- **合計**: 約90-120分

**チェックポイント**:
- ✅ 50問すべて生成完了
- ✅ problem_id が順序通り（001-050）
- ✅ 複合語が適切に使用されている
- ✅ JSON形式が正しい

---

### **Step 3: 生成結果をファイルに保存 (5分)**

```bash
# 1. 生成された問題をJSONL形式で保存
# output/technology_domain_50_raw.json に以下の形式で保存:

# 1行ごとにJSON（改行区切り）
{"problem_id": "technology_T1_001", "domain": "technology", ...}
{"problem_id": "technology_T1_002", "domain": "technology", ...}
...
{"problem_id": "technology_T5_010", "domain": "technology", ...}
```

**確認コマンド**:
```bash
# ファイル存在確認
ls -la output/technology_domain_50_raw.json

# 行数確認（50行あるはず）
wc -l output/technology_domain_50_raw.json

# JSONL形式確認
head -1 output/technology_domain_50_raw.json | python3 -m json.tool
```

---

### **Step 4: 複合語検証実行 (10分)**

```bash
cd /home/planj/patshinko-exam-app
python3 backend/validate_week6_150_problems.py
```

**期待出力**:
```
================================================================================
【Task 6.4: Week 6 150問複合語検証】
================================================================================

✅ ステップ1: 複合語辞書を読み込む
  ✓ 複合語辞書: 46個読み込み

✅ ステップ2: 生成済み問題を読み込む（3ドメイン分）
  ✓ technology: 50問生成計画を読み込み
  ✓ security: 50問生成計画を読み込み
  ✓ regulation: 50問生成計画を読み込み

✅ ステップ3: 複合語検証を実行
  ✓ technology_T1_001          (複合語1, 複合語2...)
  ...
  ✓ technology_T5_010          (複合語N...)

✅ ステップ4: 統計集計

  検証対象: 150問
  合格: 142問 (94.7%) ← ※初回は低い可能性あり
  ...
```

**成功基準確認**:
```
✅ 複合語検証合格率: 95%以上
  - 期待値: 95%以上 (47問以上合格)
  - 実績: XX% (XX問合格)

✅ 複合語カバー率: 80%以上
  - 期待値: 80%以上 (36/46個)
  - 実績: XX% (XX個)

❌ エラー検出: 0件
  - 分割エラー: 0件
  - 宣言キーワード不一致: 0件
```

**対処方法（合格率が95%未満の場合）**:
```
1. エラー内容を確認
   → validation_report_week6_150problems.json を確認

2. 問題を修正（複合語の使用法が不適切な場合）
   → output/technology_domain_50_raw.json を編集

3. 再度検証実行
   → python3 backend/validate_week6_150_problems.py
```

---

### **Step 5: 品質メトリクス計算 (5分)**

```bash
cd /home/planj/patshinko-exam-app
python3 backend/integrate_week6_quality_metrics.py
```

**期待出力**:
```
================================================================================
【Task 6.5: Week 6 150問品質メトリクス統合評価】
================================================================================

✅ ステップ3: 複合語検証からスコアを抽出

    複合語検証結果:
      - 合格率: 95.0% ← ここが重要

    → 明確性スコア: 0.90点 ← 期待値

✅ ステップ4: ひっかけ強度の推定スコア

    → ディストラクタ適切性スコア: 0.82点
    → ひっかけ度適切性スコア: 0.73点

✅ ステップ6: 総合品質スコアを計算

  = 0.30 × 0.90
  + 0.30 × 0.82
  + 0.20 × 0.90
  + 0.20 × 0.73
  ───────────────────
  = 0.832 → 0.83点 (優秀) ← 期待値！
```

**成功基準確認**:
```
✅ 品質スコア: 0.84点以上
  - 期待値: 0.84点以上
  - 実績: 0.XX点
  - 判定: [優秀|良好|要改善]

✅ 複合語精度: 90%以上
✅ テキスト一貫性: 90%以上
✅ 曖昧性排除度: 85%以上
```

---

### **Step 6: エラーチェック・修正 (必要な場合のみ)**

**エラーパターンと対処**:

```
【パターン1: 複合語検証不合格 (95%未満)】
原因: 複合語の分割・変更、不適切な使用
対処:
  1. エラー詳細を確認
  2. 該当問題の複合語を修正
  3. 再度検証実行

【パターン2: 品質スコア不足 (0.84未満)】
原因: ひっかけ度が低い、選択肢が不適切
対処:
  1. 該当問題の詳細を確認
  2. 選択肢・ひっかけ度を調整
  3. 再度品質メトリクス計算

【パターン3: 複合語使用率が低い】
原因: 問題が複合語を使用していない
対処:
  1. 複合語を自然に組み込む
  2. 再度検証実行
```

---

### **Step 7: Gitコミット (5分)**

```bash
cd /home/planj/patshinko-exam-app

# 1. ファイル状態確認
git status

# 出力例:
# Untracked files:
#   output/technology_domain_50_raw.json
#   output/validation_report_week6_150problems.json
#   output/validation_report_distractor_strength.json

# 2. ファイル追加
git add output/technology_domain_50_raw.json

# 3. コミット作成
git commit -m "feat: Week 7 Task 7.1 - 技術管理分野50問本生成完了"

# 4. Git状態確認
git status
# On branch test/coderabbit-verification
# Your branch is ahead of 'origin/HEAD' by 1 commit.

git log --oneline -1
# XXXXXXX feat: Week 7 Task 7.1 - 技術管理分野50問本生成完了
```

---

## 📊 進捗トラッキング

### 実行チェックリスト

```
準備フェーズ (10分):
  □ チャンク確認 (8個, 108.2kトークン)
  □ 複合語確認 (46個)
  □ システムプロンプト確認

生成フェーズ (90-120分):
  □ T1 (基本知識) 10問生成
  □ T2 (条文直結) 10問生成
  □ T3 (ひっかけ) 10問生成
  □ T4 (複合条件) 10問生成
  □ T5 (実務判断) 10問生成
  → 合計: 50問

検証フェーズ (10-15分):
  □ 複合語検証実行 (目標: ≥95%)
  □ 品質メトリクス計算 (目標: ≥0.84点)
  □ エラー修正（必要に応じて）

コミットフェーズ (5分):
  □ ファイル追加
  □ コミット作成
  □ Git状態確認

✅ 全体完了予定時間: 約120-160分（2-2.5時間）
```

---

## 🎯 成功基準

### 最終判定基準

```
✅ 複合語検証: 95%以上合格
✅ 品質スコア: 0.84点以上
✅ ファイル生成: technology_domain_50_raw.json 完成
✅ Gitコミット: 完了

すべて満たしたら → Week 8へ進行
```

---

**Week 7 Task 7.1 実行ガイド: 準備完全完備 ✅**

**次のステップ**: このガイドに従い、上記実行手順を実施してください。

---

最終更新: 2025-11-06
ステータス: 実行準備完全完備

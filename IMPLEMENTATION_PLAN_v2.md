# 試験問題生成システム - 実装計画書 v2.0

**プロジェクト名**: 主任者講習試験 高品質問題生成システム（アプローチC改定版）
**状態**: 開始予定
**最終更新**: 2025-11-06

---

## 📋 概要

ソース資料（風営法34セクション + 講習ガイドライン41テーマ）から、ハイブリッドAI技術を用いて、高品質な試験問題を計画的に生成するシステムの構築。

**目標**: 250問（各分野50問 × 5分野）を12週間で生成

---

## 🏗️ システムアーキテクチャ（改定版）

```
【データ入力層】
├─ 風営法テキスト（34セクション）
├─ 講習ガイドライン（41テーマ）
├─ 複合語辞書（46個）← NEW
└─ 問題タイプ頻度表（分野別）← NEW

【生成エンジン層】
├─ T5質問生成
├─ BERT ディストラクタ生成
├─ 複合語対応プロンプト← ENHANCED
└─ ひっかけ強度制御← NEW

【品質保証層】
├─ RAG事実確認
├─ BERTScore評価
├─ 複合語検証← NEW
├─ ひっかけ率検証← NEW
└─ 人間レビュー

【出力層】
└─ 問題バンクDB（メタデータ付き）
```

---

## 📅 実装スケジュール（12週間）

### **Phase 1: 準備フェーズ（Week 1-2）** ← 追加強化

#### Week 1: 基礎データの構築と分析

**タスク 1.1: 複合語辞書の確定**
- [ ] 風営法・講習ガイドラインから複合語を抽出（全文精査）
- [ ] 既存46個の複合語を検証・拡張
- [ ] カテゴリ別に分類（法令系、実務系、技術系）
- [ ] 各複合語の「重要度スコア」を付与
- **成果物**: `data/compound_words_dictionary.json`
- **チェックポイ**: コミット `feat: compound_words_dictionary_v1`

**タスク 1.2: 過去問分析で問題タイプ頻度表を作成**
- [ ] 過去5年の出題問題を分析（分野別100問以上）
- [ ] 問題タイプ別の出現頻度を計測
  - 法令: 判断型50%, 定義型30%, その他20%
  - 実務: 応用型60%, 手順型40%
  - 物理・化学・生物: 理由型50%, 計算型30%, その他20%
- [ ] 出現頻度表を作成
- **成果物**: `data/question_type_distribution.json`
- **チェックポイント**: コミット `data: question_type_distribution_analysis`

**タスク 1.3: 分野別の詳細な問題タイプテンプレート設計**
- [ ] 風営法試験向け「8テンプレート」を15個に拡張
  - 例：「正しい組合せを選べ」「適切な対応手順は」
- [ ] 各テンプレートに例を3つずつ設定
- [ ] Few-shot prompting用に最適化
- **成果物**: `config/question_templates_detailed.yaml`
- **チェックポイント**: コミット `config: detailed_question_templates`

#### Week 2: プロンプトエンジニアリング設計

**タスク 2.1: 複合語対応プロンプトの開発**
- [ ] 複合語辞書を組み込んだプロンプト設計
- [ ] プロンプトテンプレート作成（複合語強調版）
  ```
  [複合語リスト]
  営業許可, 型式検定, 営業禁止, ...

  以下の複合語を正確に扱い、分割しないでください：
  {複合語リスト}

  [以下、通常のプロンプト]
  ```
- [ ] テスト実行（Claude API）で複合語の正確性を検証
- **成果物**: `prompts/compound_word_aware_prompt_v1.txt`
- **チェックポイント**: コミット `feat: compound_word_aware_prompt`

**タスク 2.2: ひっかけ強度制御ロジックの設計**
- [ ] ひっかけスコア計測方式の定義
  ```
  ひっかけスコア = (1 - コサイン類似度) × 100
  - 0-20: 明らかに誤り（ひっかけなし）
  - 20-40: 弱いひっかけ（基礎向け）
  - 40-60: 中程度ひっかけ（標準向け）
  - 60-80: 強いひっかけ（応用向け）
  ```
- [ ] 難易度別のひっかけ率制限値を設定
  - 基礎: 10-20%, 標準: 30-40%, 応用: 40-50%
- [ ] BERT検証スクリプトのプロトタイプ作成
- **成果物**: `config/distractor_control_logic.py`
- **チェックポイント**: コミット `feat: distractor_control_logic`

**タスク 2.3: 品質評価メトリクスの定義**
- [ ] 各問題の品質スコア算出方式を定義
  ```
  総合品質スコア =
    0.3 × 問題文の明確性 +
    0.3 × ディストラクタの適切性 +
    0.2 × 説明文の根拠性 +
    0.2 × ひっかけ度の適切性

  合格ライン: 0.7以上
  ```
- [ ] 自動評価スクリプトの設計
- **成果物**: `config/quality_metrics_definition.yaml`
- **チェックポイント**: コミット `config: quality_metrics_definition`

---

### **Phase 2: プロトタイプ構築（Week 3-5）**

#### Week 3: 法令分野のプロトタイプ生成（50問）

**タスク 3.1: データ準備**
- [ ] 風営法テキスト全34セクションを確認
- [ ] 法令分野に該当するセクションを特定（推定: 第1～100条）
- [ ] チャンキング実行（論理単位、500トークン）
- **成果物**: `data/law_chunks_classified.jsonl`
- **チェックポイント**: コミット `data: law_domain_chunks_prepared`

**タスク 3.2: 複合語対応プロンプトでの問題生成**
- [ ] Claude APIを使用して50問生成
- [ ] プロンプト: 複合語対応版
- [ ] 生成パラメータ:
  - model: claude-3-5-sonnet
  - temperature: 0.7
  - max_tokens: 1000
- [ ] 出力: JSON形式で構造化
- **成果物**: `output/law_domain_50_raw.json`
- **チェックポイント**: コミット `feat: law_domain_prototype_generated`

**タスク 3.3: 複合語検証**
- [ ] 生成された問題をBERT埋め込みで分析
- [ ] 複合語が正確に扱われているか検証
- [ ] 分割されている複合語があれば修正
- [ ] 検証レポート作成
- **成果物**: `output/law_domain_compound_word_validation.json`
- **チェックポイント**: コミット `test: law_domain_compound_word_validation`

**タスク 3.4: ひっかけ強度検証と調整**
- [ ] 生成されたディストラクタのコサイン類似度を計測
- [ ] 各問題のひっかけスコアを算出
- [ ] 基礎レベル（法令は判断型中心）として、ひっかけ率10-20%を確認
- [ ] 調整が必要な問題を再生成
- **成果物**: `output/law_domain_distractor_validation.json`
- **チェックポイント**: コミット `test: law_domain_distractor_validation`

**タスク 3.5: 品質フィルタリングと人間レビュー準備**
- [ ] 自動品質スコア計測（合格: 0.7以上）
- [ ] 不合格の問題を再生成
- [ ] レビュー用エクセルファイル作成
  - 問題番号, 問題文, 選択肢A-D, 正解, 説明, 品質スコア
- **成果物**:
  - `output/law_domain_50_quality_filtered.json`
  - `review/law_domain_50_for_review.xlsx`
- **チェックポイント**: コミット `feat: law_domain_50_quality_filtered`

---

#### Week 4-5: 実務・物理・化学・生物分野のプロトタイプ（200問）

**タスク 4.1-4.4: 各分野別に Week 3と同じプロセスを実行**

| 分野 | Week | タスク概要 |
|------|------|---------|
| 実務 | 4 | 50問生成→複合語検証→ひっかけ調整→品質フィルタリング |
| 物理 | 4 | 50問生成→複合語検証→ひっかけ調整→品質フィルタリング |
| 化学 | 5 | 50問生成→複合語検証→ひっかけ調整→品質フィルタリング |
| 生物 | 5 | 50問生成→複合語検証→ひっかけ調整→品質フィルタリング |

**チェックポイント**: 各分野で
- コミット `feat: {domain}_domain_50_quality_filtered`
- レビュー用エクセル作成

**Phase 2完了時**:
- ✅ 250問生成
- ✅ 全問について複合語検証完了
- ✅ 全問についてひっかけ強度検証完了
- ✅ 全問について品質スコア算出完了
- ✅ 人間レビュー用ファイル準備完了

**マイルストーンコミット**: `milestone: prototype_250_questions_ready_for_review`

---

### **Phase 3: 品質向上（Week 9-10）** ※Week 6-8はシステム統合に充てる

#### Week 9: 専門家レビューと修正

**タスク 9.1: 専門家による内容確認**
- [ ] レビュアー配置（分野別に1名以上）
- [ ] レビュー基準:
  - 問題文の正確性・明確性
  - 正解の唯一性と正確性
  - ディストラクタの適切性（紛らわしすぎない、明確に誤り）
  - 説明文の正確性とソース参照
- [ ] フィードバック収集
- **成果物**: `review/expert_review_feedback.xlsx`
- **チェックポイント**: コミット `review: expert_feedback_collected`

**タスク 9.2: フィードバック反映**
- [ ] 不適切な問題を再生成（複合語対応プロンプト使用）
- [ ] ディストラクタの改善
- [ ] 説明文の正確化
- [ ] 修正版を再度検証
- **成果物**: `output/questions_250_revised_v1.json`
- **チェックポイント**: コミット `refactor: questions_revised_after_expert_review`

**タスク 9.3: 自動チェックの最終実行**
- [ ] 全250問について自動品質評価を再実行
- [ ] 複合語検証の最終確認
- [ ] ひっかけ率の分野別確認
  - 法令: 10-20%? ✓
  - 実務: 30-40%? ✓
  - 物理: 40-50%? ✓
  - 化学: 40-50%? ✓
  - 生物: 40-50%? ✓
- **成果物**: `output/final_quality_report.json`
- **チェックポイント**: コミット `test: final_quality_validation_passed`

---

#### Week 10: 最終統合と本番データセット構築

**タスク 10.1: 問題バンクDBの構築**
- [ ] SQLite/PostgreSQL DBスキーマ設計
- [ ] メタデータの付与:
  ```json
  {
    "problem_id": "unique_id",
    "problem_text": "...",
    "domain": "law/practice/physics/chemistry/biology",
    "question_type": "definition/judgment/application/...",
    "difficulty": "basic/standard/advanced",
    "correct_answer": "A",
    "options": {...},
    "explanation": "...",
    "source_reference": "file, page, section",
    "compound_words_used": [...],
    "distractor_score": 0.65,
    "quality_score": 0.82,
    "review_status": "approved/flagged",
    "created_at": "2025-...",
    "version": 1
  }
  ```
- **成果物**: `db/question_bank.db` (250問)
- **チェックポイント**: コミット `feat: question_bank_db_created`

**タスク 10.2: 出題システムとの連携テスト**
- [ ] 既存の出題システムとのAPI連携確認
- [ ] DBクエリテスト（分野別抽出、難易度別抽出）
- [ ] メタデータの取得確認
- **成果物**: `test/integration_test_results.json`
- **チェックポイント**: コミット `test: integration_with_exam_system_passed`

**タスク 10.3: ドキュメント作成**
- [ ] 問題生成プロセスの説明書
- [ ] メタデータの説明書
- [ ] 保守手順書
- [ ] API仕様書
- **成果物**:
  - `docs/question_generation_process.md`
  - `docs/metadata_specification.md`
  - `docs/maintenance_guide.md`
  - `docs/api_specification.md`
- **チェックポイント**: コミット `docs: complete_documentation`

---

### **Phase 4: 本番利用準備（Week 11-12）**

#### Week 11: 本番環境への適用

**タスク 11.1: 本番DB移行**
- [ ] 本番サーバーへのDB移行
- [ ] バックアップ体制の構築
- [ ] アクセス権限の設定
- **チェックポイント**: コミット `ops: production_db_migration_completed`

**タスク 11.2: 運用ハンドブック作成**
- [ ] 問題追加の手続き
- [ ] 問題修正の手続き
- [ ] トラブルシューティング
- **チェックポイント**: コミット `docs: operations_handbook`

#### Week 12: 最終確認と運用開始

**タスク 12.1: 最終テスト**
- [ ] 本番環境での全250問の出題テスト
- [ ] パフォーマンステスト
- [ ] エラーハンドリング確認
- **チェックポイント**: コミット `test: production_final_testing_passed`

**タスク 12.2: 本番運用開始**
- [ ] 利用開始アナウンス
- [ ] 監視体制の開始
- [ ] フィードバック収集開始
- **チェックポイント**: コミット `ops: production_launch`

---

## 🔄 Git管理戦略

### ブランチ構成

```
main
  ├── develop（開発ブランチ）
  │   ├── feature/compound-words（Week 1）
  │   ├── feature/distractor-control（Week 2）
  │   ├── feature/law-prototype（Week 3）
  │   ├── feature/other-domains（Week 4-5）
  │   ├── feature/quality-metrics（Week 9-10）
  │   └── release/v1.0（Week 11-12）
```

### コミット規則

```
feat: 新機能追加
  feat: compound_words_dictionary
  feat: distractor_control_logic
  feat: law_domain_prototype_generated

test: テスト実行と結果
  test: compound_word_validation
  test: final_quality_validation

refactor: リファクタリング・修正
  refactor: questions_revised_after_review

docs: ドキュメント
  docs: complete_documentation

ops: 本番運用関連
  ops: production_launch

milestone: 大きなマイルストーン
  milestone: prototype_250_ready

data: データ追加
  data: question_type_distribution
```

### チェックポイントコミット（重要）

各フェーズ完了時に必ずマイルストーンコミット：

```
Week 2終了: milestone: phase1_preparation_complete
Week 5終了: milestone: phase2_prototype_complete
Week 10終了: milestone: phase3_quality_assured
Week 12終了: milestone: phase4_production_launch
```

---

## 📊 進捗追跡

### チェックリスト形式での進捗管理

```markdown
## Phase 1: 準備（Week 1-2）
- [x] 複合語辞書完成
- [x] 問題タイプ頻度表完成
- [x] 詳細テンプレート設計完成
- [x] 複合語対応プロンプト完成
- [x] ひっかけ強度制御ロジック完成
- [x] 品質メトリクス定義完成

→ Commit: milestone: phase1_preparation_complete

## Phase 2: プロトタイプ（Week 3-5）
- [ ] 法令50問生成・検証完了
- [ ] 実務50問生成・検証完了
- [ ] 物理50問生成・検証完了
- [ ] 化学50問生成・検証完了
- [ ] 生物50問生成・検証完了
- [ ] 全250問のレビュー準備完了

→ Commit: milestone: phase2_prototype_complete
```

---

## 🚀 開始手順

1. **リポジトリの初期化**
   ```bash
   git checkout -b develop
   git checkout -b feature/compound-words
   ```

2. **Week 1開始時**
   - このプラン書を `IMPLEMENTATION_PLAN_v2.md` として保存
   - Commit: `docs: implementation_plan_v2_created`

3. **各タスク開始時**
   - ブランチ作成：`git checkout -b feature/task-name`
   - 実装開始
   - 完了後コミット

4. **フェーズ完了時**
   - マイルストーンコミット作成
   - `develop` ブランチへマージ

---

## ⚠️ フリーズ対策

### 再起動時の復帰手順

```bash
# 現在の作業ブランチの確認
git status

# 最新のマイルストーンコミットから再開
git log --oneline | grep milestone

# 中断したタスクの確認
git log --oneline | grep -E "feat:|test:|refactor:"
```

### 重要なファイル

常に以下をコミットして保存：
- `IMPLEMENTATION_PLAN_v2.md` (このファイル)
- `progress.md` (進捗ログ)
- `config/` (すべての設定ファイル)
- `prompts/` (プロンプトテンプレート)

---

## 📝 完了チェックリスト

最終的に以下が整備される：

- ✅ 250問（複合語対応、ひっかけ制御済み）
- ✅ メタデータ完全付与
- ✅ 品質スコア 0.7 以上
- ✅ 分野別カバレッジ均等
- ✅ 複合語検証完了
- ✅ ひっかけ率最適化完了
- ✅ 人間レビュー完了
- ✅ 本番DB統合完了
- ✅ ドキュメント完全整備
- ✅ Git管理（12週間分のコミット履歴）

---

**作成者**: Claude Code / Worker3
**版**: 2.0 (改定版 - 複合語・ひっかけ対応)
**状態**: 実装開始準備完了

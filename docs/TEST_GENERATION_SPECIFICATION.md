# テスト問題生成 技術仕様書

**バージョン**: 1.0
**作成日**: 2025年10月20日
**対象**: 遊技機取扱主任者試験 問題生成システム

---

## 📋 1. 問題生成の基本アーキテクチャ

### 1.1 問題要素の構造化

#### 基本的な問題構造体
```json
{
  "problem_id": "string (unique identifier)",
  "category": "string (법律 topic)",
  "pattern_type": "enum (1-6 from PROBLEM_CREATION_MANUAL)",
  "difficulty": "enum (easy/medium/hard)",
  "difficulty_score": "float (0.0-1.0 for CTT)",
  "law_reference": {
    "law": "string (e.g., 風営法第20条)",
    "article": "integer",
    "section": "integer",
    "subsection": "integer or null"
  },
  "problem_statement": {
    "premise": "string (前置き)",
    "body": "string (問題本文)",
    "full_text": "string (前置き + 本文)"
  },
  "answer": "enum (true/false)",
  "explanation": {
    "core_point": "string (核となる判定ポイント)",
    "correct_reasoning": "string (正しい理由)",
    "common_mistakes": ["string (よくある誤解)"],
    "law_citation": "string (法律条文の引用)"
  },
  "trap_mechanism": {
    "trap_type": "enum (absolute_expression/word_difference/complex_condition/...)",
    "trap_description": "string (罠の説明)",
    "trap_trigger": "string (どこで受験者がひっかかるか)"
  },
  "validation": {
    "is_valid": "boolean",
    "issues": ["string"]
  },
  "metadata": {
    "created_at": "timestamp",
    "version": "integer",
    "reviewed": "boolean"
  }
}
```

### 1.2 問題カテゴリーの定義

```
カテゴリー1: 営業許可・申請手続き
  └─ 1-1: 営業許可の要件
  └─ 1-2: 営業許可申請の手続き
  └─ 1-3: 営業届け出との違い

カテゴリー2: 営業時間・営業場所
  └─ 2-1: 営業時間の制限
  └─ 2-2: 営業場所の要件
  └─ 2-3: 離隔要件

カテゴリー3: 遊技機の規制
  └─ 3-1: 適切な遊技機の基準
  └─ 3-2: 不適切な遊技機の排除
  └─ 3-3: 遊技機の改造禁止

カテゴリー4: 従業者の要件・禁止事項
  └─ 4-1: 管理者の資格
  └─ 4-2: 主任者の職務
  └─ 4-3: 禁止行為

カテゴリー5: 顧客保護・規制遵守
  └─ 5-1: 未成年者対応
  └─ 5-2: 景品交換規制
  └─ 5-3: 営業記録

カテゴリー6: 法令違反と行政処分
  └─ 6-1: 営業停止命令
  └─ 6-2: 営業許可取り消し
  └─ 6-3: 課徴金・罰金

カテゴリー7: 実務的対応
  └─ 7-1: トラブル対応
  └─ 7-2: 定期検査・報告
  └─ 7-3: 変更届
```

### 1.3 問題パターンと難易度の対応

```
パターン1（基本的正誤判断）
  └─ 推奨難易度: Easy (70%)
  └─ 使用頻度: 30% (15問/50問)

パターン2（ひっかけ問題）
  └─ 推奨難易度: Medium-Hard (30-50%)
  └─ 使用頻度: 20% (10問/50問)

パターン3（言葉遣いの違い）
  └─ 推奨難易度: Medium (50-65%)
  └─ 使用頻度: 15% (7-8問/50問)

パターン4（条件付き正誤）
  └─ 推奨難易度: Medium-Hard (45-60%)
  └─ 使用頻度: 20% (10問/50問)

パターン5（複合判定）
  └─ 推奨難易度: Hard (30-45%)
  └─ 使用頻度: 12% (6問/50問)

パターン6（事例判断）
  └─ 推奨難易度: Hard (25-40%)
  └─ 使用頻度: 8% (4問/50問)
```

---

## 🔧 2. 問題生成アルゴリズム（詳細版）

### 2.1 Step 0: 初期化フェーズ

```python
def initialize_generation_context():
    """
    問題生成のための初期コンテキストを作成
    """
    context = {
        'total_questions': 50,
        'difficulty_distribution': {
            'easy': 15,      # 30%
            'medium': 25,    # 50%
            'hard': 10       # 20%
        },
        'pattern_distribution': {
            'pattern_1': 15,  # 30%
            'pattern_2': 10,  # 20%
            'pattern_3': 7,   # 15%
            'pattern_4': 10,  # 20%
            'pattern_5': 6,   # 12%
            'pattern_6': 4    # 8%
        },
        'category_distribution': {
            # 均等配置を目標
            'category_1': 8,  # 営業許可
            'category_2': 8,  # 営業時間
            'category_3': 8,  # 遊技機規制
            'category_4': 8,  # 従業者要件
            'category_5': 8,  # 顧客保護
            'category_6': 6,  # 法令違反
            'category_7': 4   # 実務対応
        },
        'generated_problems': [],
        'remaining_quota': {
            'by_difficulty': {...},
            'by_pattern': {...},
            'by_category': {...}
        }
    }
    return context
```

### 2.2 Step 1: 問題ソースの選定

```python
def select_problem_source(context, category, pattern):
    """
    指定されたカテゴリー・パターンに対応する
    法律条文・トピックを選定
    """
    # データベースから検索
    candidates = database.query({
        'category': category,
        'pattern': pattern,
        'used_count': {'$lt': 3}  # 過度に重複しない
    })

    if not candidates:
        return None, "No suitable source found"

    # 使用回数が少ない順に選定（バランス優先）
    source = candidates.sort_by('used_count').first()

    return source, None
```

### 2.3 Step 2: 法律ロジックの分析

```python
def analyze_law_logic(source):
    """
    選定された法律条文のロジック構造を分析
    """
    analysis = {
        'main_rule': source.main_rule,
        'exception_clauses': [],
        'related_articles': [],
        'key_terms': [],
        'decision_tree': None
    }

    # ステップA: 主要ルールを抽出
    analysis['main_rule'] = extract_main_rule(source)

    # ステップB: 例外条項を特定
    analysis['exception_clauses'] = find_exception_clauses(source)

    # ステップC: 関連条文を特定
    analysis['related_articles'] = find_related_articles(source)

    # ステップD: キーとなる法律用語を抽出
    analysis['key_terms'] = extract_key_terms(source)

    # ステップE: 判定ツリーを作成
    analysis['decision_tree'] = build_decision_tree(analysis)

    return analysis
```

### 2.4 Step 3: 問題パターンに応じた問題文生成

#### パターン1: 基本的正誤判断
```python
def generate_pattern_1(analysis, difficulty):
    """
    標準的な○×問題を生成
    """
    if difficulty == 'easy':
        # 法律に明確に書いてあることをそのまま出題
        statement = f"「{analysis['main_rule']}」"
        answer = True
        trap = None

    return {
        'pattern_type': 1,
        'statement': statement,
        'answer': answer,
        'trap_mechanism': trap
    }
```

#### パターン2: ひっかけ問題（絶対表現トラップ）
```python
def generate_pattern_2(analysis, difficulty):
    """
    「必ず」「絶対」などを含むひっかけ問題
    """
    if len(analysis['exception_clauses']) > 0:
        # 例外があるルールに「必ず」を付けてひっかけ
        exception = analysis['exception_clauses'][0]

        statement = f"「{analysis['main_rule']}を必ず遵守しなければならない」"
        # または 「～は絶対に禁止である」

        answer = False  # 例外があるので誤り
        trap = f"「必ず」という絶対表現が、実は例外を含む"

    return {
        'pattern_type': 2,
        'statement': statement,
        'answer': answer,
        'trap_mechanism': trap
    }
```

#### パターン3: 言葉遣いの違い
```python
def generate_pattern_3(analysis, difficulty):
    """
    微妙な言葉遣いの違いで意味が変わる問題
    """
    key_term_1 = analysis['key_terms'][0]  # 例: 「許可」
    key_term_2 = find_similar_term(key_term_1)  # 例: 「届け出」

    statement_correct = f"営業『{key_term_1}』は法的に厳格に定義される"
    statement_wrong = f"営業『{key_term_2}』は『{key_term_1}』と同じ意味"

    # 正と誤を50-50でランダム選択
    statement = random_choice([statement_correct, statement_wrong])
    answer = (statement == statement_correct)

    return {
        'pattern_type': 3,
        'statement': statement,
        'answer': answer,
        'key_difference': f"『{key_term_1}』≠『{key_term_2}』"
    }
```

#### パターン4-6: 複合・実務問題（類似の構造）
```python
def generate_pattern_4_to_6(analysis, pattern, difficulty):
    """
    複数条件または実務的シナリオの問題生成
    """
    # 決定ツリーを使用して複数条件の組み合わせを構築
    conditions = analysis['decision_tree'].get_conditions_by_difficulty(difficulty)

    # 条件数と複雑度を調整
    n_conditions = {
        'easy': 1,
        'medium': 2,
        'hard': 3
    }[difficulty]

    selected_conditions = sample(conditions, min(n_conditions, len(conditions)))

    # シナリオを構築
    scenario = build_scenario(selected_conditions)

    # 正答と誤答バリエーションを作成
    statement, answer, trap = generate_scenario_variants(scenario)

    return {
        'pattern_type': pattern,
        'statement': statement,
        'answer': answer,
        'trap_mechanism': trap
    }
```

### 2.5 Step 4: 解説の自動生成

```python
def generate_explanation(problem, analysis):
    """
    問題に対する解説を生成
    """
    explanation = {
        'core_point': '',
        'correct_reasoning': '',
        'common_mistakes': [],
        'law_citation': ''
    }

    # ステップA: 核となる判定ポイントを抽出
    if problem['answer'] == True:
        explanation['core_point'] = f"正しい。理由: {analysis['main_rule']}"
    else:
        explanation['core_point'] = f"誤り。理由: {identify_error(problem)}"

    # ステップB: 正しい理由を詳述
    explanation['correct_reasoning'] = generate_detailed_reasoning(
        analysis, problem['answer']
    )

    # ステップC: よくある誤解を列挙
    explanation['common_mistakes'] = [
        f"「{term}」を誤解する",
        f"例外を見落とす",
        f"複数条件を全て満たしていると思い込む"
    ]

    # ステップD: 法律条文を引用
    explanation['law_citation'] = format_law_citation(analysis)

    return explanation
```

### 2.6 Step 5: 難易度検証と調整

```python
def validate_and_adjust_difficulty(problem, analysis):
    """
    生成された問題の難易度を検証し、必要に応じて調整
    """
    # 難易度指標を計算
    indicators = {
        'term_complexity': count_legal_terms(problem['statement']),
        'sentence_length': len(problem['statement'].split()),
        'condition_count': count_conditions(analysis),
        'trap_subtlety': evaluate_trap_subtlety(problem),
        'exception_presence': bool(analysis['exception_clauses'])
    }

    # 難易度スコアを計算（0.0-1.0）
    difficulty_score = (
        indicators['term_complexity'] * 0.25 +
        indicators['sentence_length'] / 100 * 0.15 +
        indicators['condition_count'] * 0.30 +
        indicators['trap_subtlety'] * 0.20 +
        indicators['exception_presence'] * 0.10
    )

    # 推定正答率を逆算
    estimated_correct_rate = 1.0 - difficulty_score

    # 難易度分類
    if estimated_correct_rate >= 0.70:
        detected_difficulty = 'easy'
    elif estimated_correct_rate >= 0.50:
        detected_difficulty = 'medium'
    else:
        detected_difficulty = 'hard'

    # 検証
    problem['difficulty_score'] = difficulty_score
    problem['estimated_correct_rate'] = estimated_correct_rate

    return problem, detected_difficulty
```

### 2.7 Step 6: バリデーション

```python
def validate_problem(problem):
    """
    生成された問題の品質をチェック
    """
    issues = []

    # チェック1: 曖昧性の検出
    if has_ambiguity(problem['statement']):
        issues.append("曖昧な表現が含まれている")

    # チェック2: 複数解釈の検出
    interpretations = extract_interpretations(problem['statement'])
    if len(interpretations) > 1:
        issues.append(f"複数の解釈が可能: {interpretations}")

    # チェック3: 法律的正確性
    if not verify_law_accuracy(problem, problem['law_reference']):
        issues.append("法律的に不正確")

    # チェック4: 解説の完全性
    if not problem['explanation']['law_citation']:
        issues.append("法律引用がない")

    # チェック5: ひっかけの正当性
    if problem['trap_mechanism']:
        if not validate_trap_justification(problem['trap_mechanism']):
            issues.append("ひっかけが不当")

    return {
        'is_valid': len(issues) == 0,
        'issues': issues
    }
```

---

## 📊 3. 問題配置と難易度調整

### 3.1 配置アルゴリズム

```python
def arrange_problems(all_generated_problems, context):
    """
    生成された全問題を難易度・カテゴリー・パターンが
    バランスの取れた形で配置
    """

    # ステップ1: グループ化
    grouped = {
        'by_difficulty': group_by(all_generated_problems, 'difficulty'),
        'by_category': group_by(all_generated_problems, 'category'),
        'by_pattern': group_by(all_generated_problems, 'pattern_type')
    }

    # ステップ2: バランスの最適化
    arrangement = optimize_arrangement(
        all_generated_problems,
        context['total_questions'],
        grouped
    )

    # ステップ3: 配置順序を決定
    # 方式: Easy → Medium → Hard（難易度上昇）
    # または: ランダム配置（心理的負担軽減）
    arrangement = sort_by_position_strategy(arrangement)

    return arrangement
```

### 3.2 難易度分布の検証

```python
def verify_difficulty_distribution(arranged_problems):
    """
    配置された問題が目標の難易度分布を達成しているか確認
    """
    distribution = count_by_difficulty(arranged_problems)

    target = {
        'easy': 0.30,
        'medium': 0.50,
        'hard': 0.20
    }

    tolerance = 0.05  # ±5%の許容

    for difficulty, ratio in distribution.items():
        actual_ratio = ratio / len(arranged_problems)
        target_ratio = target[difficulty]

        if abs(actual_ratio - target_ratio) > tolerance:
            return False, f"{difficulty}: {actual_ratio*100:.1f}% (目標 {target_ratio*100:.1f}%)"

    return True, "分布が適切"
```

---

## ✅ 4. テスト設計チェックリスト

### 問題レベル
- [ ] 法律条文に基づいているか
- [ ] 曖昧な表現がないか
- [ ] 複数の解釈が可能でないか
- [ ] ひっかけが正当な理由に基づいているか
- [ ] 解説が簡潔かつ明確か
- [ ] 難易度は推定通りか
- [ ] 関連条文との整合性があるか
- [ ] 実務的には意味があるか

### テスト全体レベル
- [ ] 難易度分布が適切か（Easy 30%, Medium 50%, Hard 20%）
- [ ] 各トピックが偏りなく出題されているか
- [ ] ひっかけ問題の比率が適切か（20-30%）
- [ ] 各パターンが適切に配置されているか
- [ ] 予想合格率が60-80%か
- [ ] 総問題数は規定の範囲か
- [ ] 出題時間は適切か
- [ ] 問題セット間の難易度差がないか

---

## 📝 5. 実装フェーズと優先度

### フェーズ1: MVP（最小実行可能製品）
```
優先度: P0
内容:
  - 基本的な問題生成（パターン1-2）
  - CTT難易度分類
  - 基本的なバリデーション
  - JSON出力
```

### フェーズ2: 拡張
```
優先度: P1
内容:
  - パターン3-6の実装
  - 高度なひっかけメカニズム
  - 難易度微調整
  - 解説の自動生成向上
```

### フェーズ3: 最適化
```
優先度: P2
内容:
  - IRT 導入検討
  - 統計分析の実装
  - パフォーマンス最適化
  - データベース統合
```

---

**ステータス**: 仕様書 完了
**次ステップ**: WORKER3による実装設計・コーディング

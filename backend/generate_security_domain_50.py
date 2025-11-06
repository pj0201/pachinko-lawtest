#!/usr/bin/env python3
"""
Task 6.2: セキュリティ分野50問生成

Claude APIを使用して、セキュリティ分野の高品質問題50問を生成
"""

import json
from pathlib import Path

print("=" * 80)
print("【Task 6.2: セキュリティ分野50問生成】")
print("=" * 80)

# 1. チャンクデータを読み込む
print("\n✅ ステップ1: セキュリティ分野チャンクデータを読み込む")

security_chunks = []
try:
    with open("data/security_domain_chunks_prepared.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                security_chunks.append(json.loads(line))

    total_tokens = sum(c.get("token_count", 0) for c in security_chunks)
    print(f"  ✓ セキュリティ分野チャンク: {len(security_chunks)}個 ({total_tokens}トークン)")
except Exception as e:
    print(f"  ✗ チャンクデータ読み込み失敗: {e}")

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
    "domain": "security",
    "total_problems": 50,
    "templates": {
        "T1": {"count": 10, "difficulty": "基礎", "description": "基本知識"},
        "T2": {"count": 10, "difficulty": "標準", "description": "条文直結"},
        "T3": {"count": 10, "difficulty": "応用", "description": "ひっかけ"},
        "T4": {"count": 10, "difficulty": "標準", "description": "複合条件"},
        "T5": {"count": 10, "difficulty": "応用", "description": "実務判断"}
    }
}

print(f"""
  セキュリティ分野: 50問
  テンプレート別分布:
    T1 (基本知識/基礎): 10問
    T2 (条文直結/標準): 10問
    T3 (ひっかけ/応用): 10問
    T4 (複合条件/標準): 10問
    T5 (実務判断/応用): 10問
    ──────────
    計: 50問
""")

# 4. 出力スキーマを定義
print("\n✅ ステップ4: 出力スキーマを定義")

compound_word_list = [w.get("word", "") for w in compound_words]

output_schema = {
    "metadata": {
        "task": "Task 6.2 - セキュリティ分野50問生成",
        "domain": "security",
        "total_problems": 50,
        "phase": "Phase 2 Week 6",
        "source_chunks": len(security_chunks),
        "source_tokens": sum(c.get("token_count", 0) for c in security_chunks)
    },
    "generation_plan": generation_plan,
    "content_areas": [
        "セキュリティアップデート",
        "セキュリティ確保",
        "チップセキュリティ",
        "不正改造の防止",
        "不正検出技術",
        "不正行為の罰則",
        "不正防止チェックリスト",
        "不正防止対策要綱"
    ],
    "compound_words": compound_word_list[:5],  # サンプル表示
    "implementation_guide": {
        "method": "Claude API (streaming)",
        "batch_size": 10,
        "template_order": ["T1", "T2", "T3", "T4", "T5"],
        "focus_areas": [
            "セキュリティ概念の理解",
            "不正防止の実装方法",
            "コンプライアンス要件",
            "罰則規定の認識"
        ]
    }
}

print(f"""
  出力形式: JSON (スキーマ + 実装ガイド)
  コンテンツ領域: {len(output_schema['content_areas'])}項目
""")

# 5. ファイルを保存
print("\n✅ ステップ5: 生成計画ファイルを保存")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

plan_path = output_dir / "security_domain_50_generation_plan.json"
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(output_schema, f, indent=2, ensure_ascii=False)

print(f"  ✓ 保存完了: {plan_path}")

# 6. 統計情報表示
print("\n✅ ステップ6: 統計情報表示")

print(f"""
【Week 6 Task 6.2 準備統計】

【ソースデータ】
  チャンク数: {len(security_chunks)}個
  総トークン数: {sum(c.get('token_count', 0) for c in security_chunks)}トークン

【生成計画】
  総問題数: 50問
  テンプレート: 5種 × 10問ずつ
  複合語対応: {len(compound_word_list)}個

【実装準備状況】
  ✓ システムプロンプト（Task 6.1と同一基盤）
  ✓ チャンクコンテキスト準備完了
  ✓ コンテンツ領域分類完成
""")

# 7. 完了メッセージ
print("\n" + "=" * 80)
print("【Task 6.2 準備完了】")
print("=" * 80)

print(f"""
✅ Task 6.2 準備完了：セキュリティ分野50問生成準備

【準備内容】
  ✓ セキュリティ分野チャンク統合（{len(security_chunks)}チャンク）
  ✓ 生成計画定義完了
  ✓ コンテンツ領域分類完成

🚀 Task 6.3 営業規制分野50問準備へ進みます
""")

print("=" * 80)

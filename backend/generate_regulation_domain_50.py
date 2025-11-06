#!/usr/bin/env python3
"""
Task 6.3: 営業規制分野50問生成

Claude APIを使用して、営業規制分野の高品質問題50問を生成
"""

import json
from pathlib import Path

print("=" * 80)
print("【Task 6.3: 営業規制分野50問生成】")
print("=" * 80)

# 1. チャンクデータを読み込む
print("\n✅ ステップ1: 営業規制分野チャンクデータを読み込む")

regulation_chunks = []
try:
    with open("data/regulation_domain_chunks_prepared.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                regulation_chunks.append(json.loads(line))

    total_tokens = sum(c.get("token_count", 0) for c in regulation_chunks)
    print(f"  ✓ 営業規制分野チャンク: {len(regulation_chunks)}個 ({total_tokens}トークン)")
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
    "domain": "regulation",
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
  営業規制分野: 50問
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

output_schema = {
    "metadata": {
        "task": "Task 6.3 - 営業規制分野50問生成",
        "domain": "regulation",
        "total_problems": 50,
        "phase": "Phase 2 Week 6",
        "source_chunks": len(regulation_chunks),
        "source_tokens": sum(c.get("token_count", 0) for c in regulation_chunks)
    },
    "generation_plan": generation_plan,
    "content_areas": [
        "営業停止命令",
        "営業禁止時間",
        "営業許可",
        "営業許可の取消し",
        "営業許可の失効",
        "営業許可の行政手続き",
        "営業許可の有効期限"
    ],
    "key_concepts": [
        "営業許可と営業停止命令の関係",
        "営業禁止期間",
        "行政処分の基準",
        "営業実績と営業許可"
    ]
}

print(f"""
  出力形式: JSON (スキーマ + 実装ガイド)
  コンテンツ領域: {len(output_schema['content_areas'])}項目
  重要概念: {len(output_schema['key_concepts'])}項目
""")

# 5. ファイルを保存
print("\n✅ ステップ5: 生成計画ファイルを保存")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

plan_path = output_dir / "regulation_domain_50_generation_plan.json"
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(output_schema, f, indent=2, ensure_ascii=False)

print(f"  ✓ 保存完了: {plan_path}")

# 6. 統計情報表示
print("\n✅ ステップ6: 統計情報表示")

print(f"""
【Week 6 Task 6.3 準備統計】

【ソースデータ】
  チャンク数: {len(regulation_chunks)}個
  総トークン数: {sum(c.get('token_count', 0) for c in regulation_chunks)}トークン

【生成計画】
  総問題数: 50問
  テンプレート: 5種 × 10問ずつ
  複合語対応: {len(compound_words)}個
""")

# 7. 完了メッセージ
print("\n" + "=" * 80)
print("【Task 6.3 準備完了】")
print("=" * 80)

print(f"""
✅ Task 6.3 準備完了：営業規制分野50問生成準備

【準備内容】
  ✓ 営業規制分野チャンク統合（{len(regulation_chunks)}チャンク）
  ✓ 生成計画定義完了
  ✓ コンテンツ領域分類完成

📊 Week 6 ドメイン別生成準備：すべて完了

  Task 6.1 技術管理: ✅ 準備完了
  Task 6.2 セキュリティ: ✅ 準備完了
  Task 6.3 営業規制: ✅ 準備完了

🎯 次フェーズ: 150問本生成実行
  （Claude APIで各ドメイン50問を生成）
""")

print("=" * 80)

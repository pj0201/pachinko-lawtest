#!/usr/bin/env python3
"""
Task 4.1: 実務分野データ準備スクリプト

講習ガイドライン41テーマから実務分野を抽出し、
問題生成用のコンテキストを準備する
"""

import json
import os
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("【Task 4.1: 実務分野データ準備】")
print("=" * 80)

# 1. 講習テーマの確認
print("\n✅ ステップ1: 講習テーマの確認")

lecture_dir = Path("rag_data/lecture_text")
if lecture_dir.exists():
    lecture_files = sorted(lecture_dir.glob("*.txt"))
    print(f"  見つけたテーマ: {len(lecture_files)}個")
    for f in lecture_files[:5]:
        print(f"    - {f.name}")
    if len(lecture_files) > 5:
        print(f"    ... 他 {len(lecture_files) - 5}個")
else:
    print(f"❌ {lecture_dir} が見つかりません")
    lecture_files = []

# 2. 実務分野テーマの分類
print("\n✅ ステップ2: 実務分野テーマを分類")

# 実務分野に該当するテーマを定義（講習テーマから選別）
practice_themes = {
    "operational_procedures": [
        "theme_030_新台設置の手続き.txt",
        "theme_035_設置済み遊技機の交換手続き.txt",
        "theme_012_中古遊技機の流通管理.txt",
        "theme_011_中古遊技機の取扱い.txt"
    ],
    "administrative_enforcement": [
        "theme_013_営業停止命令.txt",
        "theme_015_営業停止期間の計算.txt",
        "theme_019_営業許可の取消し要件.txt",
        "theme_020_営業許可の失効事由.txt",
        "theme_041_違反時の行政処分.txt"
    ],
    "compliance_and_prevention": [
        "theme_006_不正改造の防止.txt",
        "theme_008_不正行為の罰則.txt",
        "theme_010_不正防止対策要綱.txt"
    ],
    "technical_management": [
        "theme_003_チップのセキュリティ.txt",
        "theme_023_型式検定と中古機の関係.txt",
        "theme_024_型式検定と製造者の責任.txt",
        "theme_039_遊技機の製造番号管理.txt",
        "theme_040_遊技機型式検定は3年有効.txt"
    ],
    "regulation_standards": [
        "theme_034_景品交換の規制.txt",
        "theme_036_賞源有効利用促進法.txt",
        "theme_005_リサイクル推進法との関係.txt"
    ]
}

practice_theme_count = sum(len(v) for v in practice_themes.values())
print(f"""
  実務分野テーマ: {practice_theme_count}個
  カテゴリ:
    - 営業手続き: {len(practice_themes['operational_procedures'])}個
    - 行政処分: {len(practice_themes['administrative_enforcement'])}個
    - コンプライアンス: {len(practice_themes['compliance_and_prevention'])}個
    - 技術管理: {len(practice_themes['technical_management'])}個
    - 規制基準: {len(practice_themes['regulation_standards'])}個
""")

# 3. チャンキング戦略の定義
print("\n✅ ステップ3: チャンキング戦略を定義")

chunking_strategy = {
    "method": "logical_units",
    "target_tokens": 500,
    "delimiter": ["。\n", "。", "\n\n"],
    "min_chunk_size": 50,
    "max_chunk_size": 1000,
    "categories": list(practice_themes.keys())
}

print(f"""
  チャンキング方式: {chunking_strategy['method']}
  目標トークン数: {chunking_strategy['target_tokens']}
  最小/最大: {chunking_strategy['min_chunk_size']}/{chunking_strategy['max_chunk_size']}
""")

# 4. テーマデータを読み込む
print("\n✅ ステップ4: 実務分野テーマデータを読み込む")

practice_chunks = []
category_stats = defaultdict(lambda: {"count": 0, "tokens": 0})

for category, theme_files in practice_themes.items():
    print(f"\n  【{category}】")

    for theme_file in theme_files:
        theme_path = lecture_dir / theme_file

        if not theme_path.exists():
            print(f"    ⚠️  {theme_file} が見つかりません")
            continue

        # ファイル読み込み
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if not content:
                print(f"    ⚠️  {theme_file} が空です")
                continue

            # 簡易的なトークン数推定（日本語は3字=1トークン程度）
            token_count = len(content) // 3

            # チャンク作成
            chunk = {
                "chunk_id": f"practice_{category}_{len(practice_chunks):03d}",
                "category": category,
                "source_file": theme_file,
                "content": content,
                "token_count": token_count,
                "source": "lecture_materials"
            }

            practice_chunks.append(chunk)
            category_stats[category]["count"] += 1
            category_stats[category]["tokens"] += token_count

            print(f"    ✓ {theme_file:40} ({token_count:4}トークン)")

        except Exception as e:
            print(f"    ✗ エラー: {theme_file} - {e}")

# 5. 統計情報
print("\n✅ ステップ5: 統計集計")

total_chunks = len(practice_chunks)
total_tokens = sum(s["tokens"] for s in category_stats.values())

print(f"""
  総チャンク数: {total_chunks}個
  総トークン数: {total_tokens}トークン

  【カテゴリ別統計】
""")

for category, stats in category_stats.items():
    tokens = stats["tokens"]
    percentage = (tokens / total_tokens * 100) if total_tokens > 0 else 0
    print(f"    {category:30} {stats['count']:2}個 ({tokens:5}トークン, {percentage:5.1f}%)")

# 6. 出力スキーマの定義
print("\n✅ ステップ6: 出力スキーマを定義")

output_schema = {
    "metadata": {
        "task": "Task 4.1 - 実務分野データ準備",
        "domain": "practice",
        "total_chunks": total_chunks,
        "total_tokens": total_tokens,
        "chunking_method": "logical_units",
        "source": "lecture_materials (41 themes)"
    },
    "chunking_strategy": chunking_strategy,
    "category_distribution": dict(category_stats),
    "sample_chunks": practice_chunks[:3]  # 最初の3個をサンプルとして含める
}

print(f"""
  出力形式: JSONL (1行1チャンク) + メタデータJSON

  各チャンクの構造:
  {{
    "chunk_id": "unique_id",
    "category": "category_name",
    "source_file": "theme_XXX_...txt",
    "content": "...",
    "token_count": 500,
    "source": "lecture_materials"
  }}
""")

# 7. 実務分野チャンクを保存
print("\n✅ ステップ7: チャンクデータを保存")

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

# JSONL形式で保存（1行1チャンク）
jsonl_path = output_dir / "practice_domain_chunks_prepared.jsonl"
with open(jsonl_path, 'w', encoding='utf-8') as f:
    for chunk in practice_chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"  ✓ JSONL保存: {jsonl_path} ({total_chunks}行)")

# メタデータJSONを保存
metadata_path = output_dir / "practice_domain_chunks_metadata.json"
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(output_schema, f, indent=2, ensure_ascii=False)

print(f"  ✓ メタデータ保存: {metadata_path}")

# 8. サンプル表示
print("\n✅ ステップ8: サンプルチャンク表示")

if practice_chunks:
    for i, chunk in enumerate(practice_chunks[:2], 1):
        print(f"\n  【サンプル {i}: {chunk['chunk_id']}】")
        print(f"    カテゴリ: {chunk['category']}")
        print(f"    ソース: {chunk['source_file']}")
        print(f"    トークン数: {chunk['token_count']}")
        preview = chunk['content'][:100].replace('\n', ' ')
        print(f"    内容プレビュー: {preview}...")

# 9. 完了メッセージ
print("\n" + "=" * 80)
print("【Task 4.1 完了 - 実務分野データ準備完了】")
print("=" * 80)

print(f"""
✅ 準備完了：
  - チャンク数: {total_chunks}個
  - 総トークン数: {total_tokens}トークン
  - 出力ファイル:
    - {jsonl_path}
    - {metadata_path}

📊 実務分野の内容：
  - 営業手続き（新台設置、中古機流通等）
  - 行政処分（営業停止、取消し等）
  - コンプライアンス（不正防止、罰則等）
  - 技術管理（型式検定、製造番号等）
  - 規制基準（景品規制、リサイクル等）

🚀 次タスク（Task 4.2）：
  - Claude APIを使用して50問生成
  - 複合語対応プロンプトを使用
  - `output/practice_domain_50_raw.json` に出力
""")

print("=" * 80)

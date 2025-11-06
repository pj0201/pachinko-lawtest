#!/usr/bin/env python3
"""
Task 5.1: 技術管理分野データ準備スクリプト

型式検定関連 + 遊技機管理テーマから、
問題生成用のコンテキストを準備する
"""

import json
import os
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("【Task 5.1: 技術管理分野データ準備】")
print("=" * 80)

# 1. 講習テーマの確認
print("\n✅ ステップ1: 講習テーマの確認")

lecture_dir = Path("rag_data/lecture_text")
if lecture_dir.exists():
    lecture_files = sorted(lecture_dir.glob("*.txt"))
    print(f"  見つけたテーマ: {len(lecture_files)}個")
else:
    print(f"❌ {lecture_dir} が見つかりません")
    lecture_files = []

# 2. 技術管理分野テーマの分類
print("\n✅ ステップ2: 技術管理分野テーマを分類")

# 技術管理分野に該当するテーマを定義（実在するテーマのみ）
# Week 4で未使用の型式検定関連 + 遊技機管理テーマ
technology_themes = {
    "type_certification": [
        "theme_025_型式検定の申請方法.txt",
        "theme_026_型式検定更新申請のタイミング.txt",
    ],
    "gaming_machine_management": [
        "theme_027_基板ケースのかしめと管理.txt",
        "theme_028_外部端子板の管理.txt",
        "theme_029_故障遊技機の対応.txt",
        "theme_031_旧機械の回収と廃棄.txt",
        "theme_037_遊技機の保守管理.txt",
        "theme_038_遊技機の点検・保守計画.txt",
    ]
}

tech_theme_count = sum(len(v) for v in technology_themes.values())
print(f"""
  技術管理分野テーマ: {tech_theme_count}個
  カテゴリ:
    - 型式検定関連: {len(technology_themes['type_certification'])}個
    - 遊技機管理: {len(technology_themes['gaming_machine_management'])}個
""")

# 3. チャンキング戦略の定義
print("\n✅ ステップ3: チャンキング戦略を定義")

chunking_strategy = {
    "method": "logical_units",
    "target_tokens": 500,
    "delimiter": ["。\n", "。", "\n\n"],
    "min_chunk_size": 50,
    "max_chunk_size": 1000,
    "categories": list(technology_themes.keys())
}

print(f"""
  チャンキング方式: {chunking_strategy['method']}
  目標トークン数: {chunking_strategy['target_tokens']}
  最小/最大: {chunking_strategy['min_chunk_size']}/{chunking_strategy['max_chunk_size']}
""")

# 4. テーマデータを読み込む
print("\n✅ ステップ4: 技術管理分野テーマデータを読み込む")

technology_chunks = []
category_stats = defaultdict(lambda: {"count": 0, "tokens": 0})

for category, theme_files in technology_themes.items():
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

            # 簡易的なトークン数推定
            token_count = len(content) // 3

            # チャンク作成
            chunk = {
                "chunk_id": f"technology_{category}_{len(technology_chunks):03d}",
                "category": category,
                "source_file": theme_file,
                "content": content,
                "token_count": token_count,
                "source": "lecture_materials"
            }

            technology_chunks.append(chunk)
            category_stats[category]["count"] += 1
            category_stats[category]["tokens"] += token_count

            print(f"    ✓ {theme_file:45} ({token_count:5}トークン)")

        except Exception as e:
            print(f"    ✗ エラー: {theme_file} - {e}")

# 5. 統計情報
print("\n✅ ステップ5: 統計集計")

total_chunks = len(technology_chunks)
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
        "task": "Task 5.1 - 技術管理分野データ準備",
        "domain": "technology",
        "total_chunks": total_chunks,
        "total_tokens": total_tokens,
        "chunking_method": "logical_units",
        "source": "lecture_materials"
    },
    "chunking_strategy": chunking_strategy,
    "category_distribution": dict(category_stats),
    "sample_chunks": technology_chunks[:3]
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

# 7. 技術管理分野チャンクを保存
print("\n✅ ステップ7: チャンクデータを保存")

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

# JSONL形式で保存
jsonl_path = output_dir / "technology_domain_chunks_prepared.jsonl"
with open(jsonl_path, 'w', encoding='utf-8') as f:
    for chunk in technology_chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"  ✓ JSONL保存: {jsonl_path} ({total_chunks}行)")

# メタデータJSONを保存
metadata_path = output_dir / "technology_domain_chunks_metadata.json"
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(output_schema, f, indent=2, ensure_ascii=False)

print(f"  ✓ メタデータ保存: {metadata_path}")

# 8. サンプル表示
print("\n✅ ステップ8: サンプルチャンク表示")

if technology_chunks:
    for i, chunk in enumerate(technology_chunks[:2], 1):
        print(f"\n  【サンプル {i}: {chunk['chunk_id']}】")
        print(f"    カテゴリ: {chunk['category']}")
        print(f"    ソース: {chunk['source_file']}")
        print(f"    トークン数: {chunk['token_count']}")
        preview = chunk['content'][:100].replace('\n', ' ')
        print(f"    内容プレビュー: {preview}...")

# 9. 完了メッセージ
print("\n" + "=" * 80)
print("【Task 5.1 完了 - 技術管理分野データ準備完了】")
print("=" * 80)

print(f"""
✅ 準備完了：
  - チャンク数: {total_chunks}個
  - 総トークン数: {total_tokens}トークン
  - 出力ファイル:
    - {jsonl_path}
    - {metadata_path}

📊 技術管理分野の内容：
  - 型式検定関連（申請方法、不合格時対応）
  - 遊技機管理（保守、新台導入、故障対応、基板管理等）
  - 景品規制基準（種類制限等）

🚀 次タスク（Task 5.2）：
  - Claude APIを使用して50問生成
  - 複合語対応プロンプトを使用
  - `output/technology_domain_50_raw.json` に出力
""")

print("=" * 80)

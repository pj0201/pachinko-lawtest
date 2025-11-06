#!/usr/bin/env python3
"""
Task 5.3: 営業規制分野データ準備スクリプト

営業許可・営業停止・営業禁止関連テーマから、
問題生成用のコンテキストを準備する
"""

import json
import os
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("【Task 5.3: 営業規制分野データ準備】")
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

# 2. 営業規制分野テーマの分類
print("\n✅ ステップ2: 営業規制分野テーマを分類")

# 営業規制分野に該当するテーマを定義（営業許可・営業停止・営業禁止関連）
regulation_themes = {
    "business_suspension": [
        "theme_013_営業停止命令.txt",
        "theme_014_営業停止命令の内容.txt",
        "theme_015_営業停止期間の計算.txt",
    ],
    "business_prohibition": [
        "theme_016_営業禁止時間.txt",
    ],
    "business_approval": [
        "theme_017_営業許可と営業実績の関係.txt",
        "theme_018_営業許可と型式検定の違い.txt",
        "theme_019_営業許可の取消し要件.txt",
        "theme_020_営業許可の失効事由.txt",
        "theme_021_営業許可の行政手続き.txt",
        "theme_022_営業許可は無期限有効.txt",
    ]
}

reg_theme_count = sum(len(v) for v in regulation_themes.values())
print(f"""
  営業規制分野テーマ: {reg_theme_count}個
  カテゴリ:
    - 営業許可: {len(regulation_themes['business_approval'])}個
    - 営業停止: {len(regulation_themes['business_suspension'])}個
    - 営業禁止: {len(regulation_themes['business_prohibition'])}個
""")

# 3. チャンキング戦略の定義
print("\n✅ ステップ3: チャンキング戦略を定義")

chunking_strategy = {
    "method": "logical_units",
    "target_tokens": 500,
    "delimiter": ["。\n", "。", "\n\n"],
    "min_chunk_size": 50,
    "max_chunk_size": 1000,
    "categories": list(regulation_themes.keys())
}

print(f"""
  チャンキング方式: {chunking_strategy['method']}
  目標トークン数: {chunking_strategy['target_tokens']}
  最小/最大: {chunking_strategy['min_chunk_size']}/{chunking_strategy['max_chunk_size']}
""")

# 4. テーマデータを読み込む
print("\n✅ ステップ4: 営業規制分野テーマデータを読み込む")

regulation_chunks = []
category_stats = defaultdict(lambda: {"count": 0, "tokens": 0})

for category, theme_files in regulation_themes.items():
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
                "chunk_id": f"regulation_{category}_{len(regulation_chunks):03d}",
                "category": category,
                "source_file": theme_file,
                "content": content,
                "token_count": token_count,
                "source": "lecture_materials"
            }

            regulation_chunks.append(chunk)
            category_stats[category]["count"] += 1
            category_stats[category]["tokens"] += token_count

            print(f"    ✓ {theme_file:45} ({token_count:5}トークン)")

        except Exception as e:
            print(f"    ✗ エラー: {theme_file} - {e}")

# 5. 統計情報
print("\n✅ ステップ5: 統計集計")

total_chunks = len(regulation_chunks)
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
        "task": "Task 5.3 - 営業規制分野データ準備",
        "domain": "regulation",
        "total_chunks": total_chunks,
        "total_tokens": total_tokens,
        "chunking_method": "logical_units",
        "source": "lecture_materials"
    },
    "chunking_strategy": chunking_strategy,
    "category_distribution": dict(category_stats),
    "sample_chunks": regulation_chunks[:3]
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

# 7. 営業規制分野チャンクを保存
print("\n✅ ステップ7: チャンクデータを保存")

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

# JSONL形式で保存
jsonl_path = output_dir / "regulation_domain_chunks_prepared.jsonl"
with open(jsonl_path, 'w', encoding='utf-8') as f:
    for chunk in regulation_chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"  ✓ JSONL保存: {jsonl_path} ({total_chunks}行)")

# メタデータJSONを保存
metadata_path = output_dir / "regulation_domain_chunks_metadata.json"
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(output_schema, f, indent=2, ensure_ascii=False)

print(f"  ✓ メタデータ保存: {metadata_path}")

# 8. サンプル表示
print("\n✅ ステップ8: サンプルチャンク表示")

if regulation_chunks:
    for i, chunk in enumerate(regulation_chunks[:2], 1):
        print(f"\n  【サンプル {i}: {chunk['chunk_id']}】")
        print(f"    カテゴリ: {chunk['category']}")
        print(f"    ソース: {chunk['source_file']}")
        print(f"    トークン数: {chunk['token_count']}")
        preview = chunk['content'][:100].replace('\n', ' ')
        print(f"    内容プレビュー: {preview}...")

# 9. 完了メッセージ
print("\n" + "=" * 80)
print("【Task 5.3 完了 - 営業規制分野データ準備完了】")
print("=" * 80)

print(f"""
✅ 準備完了：
  - チャンク数: {total_chunks}個
  - 総トークン数: {total_tokens}トークン
  - 出力ファイル:
    - {jsonl_path}
    - {metadata_path}

📊 営業規制分野の内容：
  - 営業許可（申請手続き、更新、要件）
  - 営業停止（命令基準、手続き、義務）
  - 営業禁止（事由、期間、例外、解除手続き）

🚀 次タスク（Task 5.4）：
  - Claude APIを使用して150問生成
  - 複合語対応プロンプトを使用
  - 技術管理+セキュリティ+営業規制 3分野
  - `output/week5_domain_50_raw.json` に出力
""")

print("=" * 80)

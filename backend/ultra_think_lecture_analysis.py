#!/usr/bin/env python3
"""
Ultra Think: 講習ガイドラインの全テーマを体系的に分析
各テーマの実際の内容を把握し、テーママッピングの正確性を確認
"""

import re
from pathlib import Path
from collections import defaultdict

def analyze_lecture_guide():
    """講習ガイドラインの全テーマを徹底分析"""

    lecture_dir = Path('rag_data/lecture_text')

    print("=" * 80)
    print("【Ultra Think: 講習ガイドラインの体系的徹底分析】")
    print("=" * 80)
    print()

    theme_analysis = {}
    category_mapping = {}

    # 全テーマファイルを処理
    for theme_file in sorted(lecture_dir.glob('theme_*.txt')):
        filename = theme_file.stem

        # ファイル名から情報抽出
        parts = filename.split('_', 2)
        if len(parts) < 3:
            continue

        theme_num = parts[0]  # theme_001など
        theme_name = parts[2]  # テーマ名

        with open(theme_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # テーマ別分析
        print(f"【{theme_num}: {theme_name}】")
        print(f"  ファイル: {filename}")
        print(f"  サイズ: {len(content):,}文字")

        # 内容プレビュー（最初の150文字）
        preview = content[:150].replace('\n', ' ')
        print(f"  内容プレビュー: {preview}...")

        # 主要キーワード抽出（3文字以上の日本語）
        words = re.findall(r'[\u4e00-\u9fff]{3,}', content)
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: -x[1])
        top_keywords = [w[0] for w in sorted_words[:10]]

        print(f"  主要キーワード: {', '.join(top_keywords)}")

        # テーマサイズの判定
        if len(content) < 1000:
            substance = "（最小サイズ - プレースホルダ可能性）"
        elif len(content) < 5000:
            substance = "（小規模テーマ）"
        elif len(content) < 10000:
            substance = "（中程度テーマ）"
        else:
            substance = "（大規模テーマ - 実質的内容あり）"

        print(f"  実質性: {substance}")

        # カテゴリ判定（テーマ名から推測）
        if '不正' in theme_name or 'セキュリティ' in theme_name:
            category = "不正対策"
        elif '営業時間' in theme_name or '営業禁止' in theme_name or '営業停止' in theme_name:
            category = "営業時間・規制"
        elif '営業許可' in theme_name or '営業実績' in theme_name:
            category = "営業許可関連"
        elif '型式検定' in theme_name:
            category = "型式検定関連"
        elif '景品' in theme_name or 'リサイクル' in theme_name or '賞源' in theme_name:
            category = "景品規制"
        else:
            category = "遊技機管理"

        print(f"  カテゴリ: {category}")

        # 記録
        theme_analysis[f"{theme_num}:{theme_name}"] = {
            'filename': filename,
            'size': len(content),
            'keywords': top_keywords,
            'category': category,
            'word_count': len(words)
        }

        if category not in category_mapping:
            category_mapping[category] = []
        category_mapping[category].append(f"{theme_num}:{theme_name}")

        print()

    # サマリー
    print("=" * 80)
    print("【講習ガイドラインの体系的サマリー】")
    print("=" * 80)

    print("\n【カテゴリ別テーマ数】\n")
    for category in sorted(category_mapping.keys()):
        themes = category_mapping[category]
        print(f"  {category:20} {len(themes):2}テーマ")
        for theme in themes:
            size = theme_analysis[theme]['size']
            print(f"    {theme:45} ({size:7,}文字)")

    print(f"\n合計: {len(theme_analysis)}テーマ")

    # サイズ分布
    print("\n【テーマサイズ分布】\n")
    size_ranges = {
        '超小規模(<1KB)': 0,
        '小規模(1-5KB)': 0,
        '中規模(5-10KB)': 0,
        '大規模(10+KB)': 0
    }

    for theme, data in theme_analysis.items():
        size = data['size']
        if size < 1000:
            size_ranges['超小規模(<1KB)'] += 1
        elif size < 5000:
            size_ranges['小規模(1-5KB)'] += 1
        elif size < 10000:
            size_ranges['中規模(5-10KB)'] += 1
        else:
            size_ranges['大規模(10+KB)'] += 1

    for range_name, count in size_ranges.items():
        print(f"  {range_name:20} {count:3}テーマ")

if __name__ == "__main__":
    analyze_lecture_guide()

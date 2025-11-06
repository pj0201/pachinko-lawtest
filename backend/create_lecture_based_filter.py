#!/usr/bin/env python3
"""
講習ガイドラインのテーマ内容を分析して、500問の正確なマッピングフィルターを作成
各テーマファイルから実際のキーワードを抽出し、それを基に500問を再マッピング
"""

import json
from pathlib import Path
import re

def extract_theme_keywords(theme_file_path: str) -> list:
    """テーマファイルから主要キーワードを抽出"""

    with open(theme_file_path, 'r') as f:
        content = f.read()

    # 最初の1000文字から、日本語の複合語を抽出
    sample = content[:1000]

    # 簡易的なキーワード抽出（3文字以上の日本語）
    words = re.findall(r'[\u4e00-\u9fff]{3,}', sample)

    # 重複を除いて頻度の高い順に並べる
    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: -x[1])
    keywords = [w[0] for w in sorted_words[:15]]

    return keywords

def build_lecture_filter() -> dict:
    """講習ガイドラインから全テーマのフィルターを構築"""

    lecture_dir = Path('rag_data/lecture_text')
    theme_filter = {}

    for theme_file in sorted(lecture_dir.glob('theme_*.txt')):
        # ファイル名からテーマ名を抽出
        filename = theme_file.stem
        theme_num = filename.split('_')[0]
        theme_name = '_'.join(filename.split('_')[2:])  # テーマ名のみ

        # キーワードを抽出
        keywords = extract_theme_keywords(str(theme_file))

        theme_filter[theme_name] = {
            'keywords': keywords,
            'file': filename,
            'file_size': theme_file.stat().st_size
        }

    return theme_filter

def map_problem_to_theme(problem_text: str, theme_filter: dict) -> str:
    """問題テキストを講習ガイドラインのフィルターに基づいてマッピング"""

    best_theme = None
    best_score = 0

    for theme_name, theme_data in theme_filter.items():
        score = 0
        for kw in theme_data['keywords']:
            if kw in problem_text:
                score += 1

        if score > best_score:
            best_score = score
            best_theme = theme_name

    return best_theme if best_theme else "営業許可と営業実績の関係"

def apply_lecture_based_mapping():
    """講習ガイドラインベースのマッピングを実行"""

    # フィルター構築
    print("【講習ガイドラインのフィルター構築中...】\n")
    theme_filter = build_lecture_filter()

    print(f"✅ {len(theme_filter)}テーマのフィルター作成完了\n")
    print("【フィルター内容（先頭5テーマ）】\n")
    for i, (theme, data) in enumerate(list(theme_filter.items())[:5], 1):
        print(f"{i}. {theme}")
        print(f"   キーワード: {', '.join(data['keywords'][:5])}\n")

    # 500問にマッピング適用
    print("【500問にマッピングを適用中...】\n")

    with open('backend/problems_final_500_complete.json', 'r') as f:
        problems = json.load(f)

    remapped = []
    distribution = {}

    for p in problems:
        problem_text = p.get('problem_text', '')

        # 講習ガイドラインベースでマッピング
        mapped_theme = map_problem_to_theme(problem_text, theme_filter)

        p['lecture_based_theme'] = mapped_theme
        remapped.append(p)

        if mapped_theme not in distribution:
            distribution[mapped_theme] = 0
        distribution[mapped_theme] += 1

    # 出力
    with open('backend/problems_500_lecture_filtered.json', 'w') as f:
        json.dump(remapped, f, indent=2, ensure_ascii=False)

    print("✅ マッピング完了\n")
    print("【講習ガイドラインベースの分布】\n")

    for theme, count in sorted(distribution.items(), key=lambda x: -x[1]):
        print(f"  {theme:40} {count:3}問")

    print(f"\n合計: {sum(distribution.values())}問")

if __name__ == "__main__":
    apply_lecture_based_mapping()

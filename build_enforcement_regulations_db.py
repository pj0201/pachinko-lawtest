#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
施行規則のデータベースファイルを構築するスクリプト
"""

import json
import re

# 漢数字から数字への変換マップ
def kanji_to_num(kanji_str):
    """漢数字を数値に変換（簡易版）"""
    # 百、十の位を持つ漢数字に対応
    simple_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
    }

    if kanji_str in simple_map:
        return simple_map[kanji_str]

    # 十の位の処理
    if '十' in kanji_str and '百' not in kanji_str:
        parts = kanji_str.split('十')
        if parts[0] == '':
            tens = 1
        else:
            tens = simple_map.get(parts[0], 1)
        ones = simple_map.get(parts[1], 0) if len(parts) > 1 and parts[1] else 0
        return tens * 10 + ones

    # 百の位の処理
    if '百' in kanji_str:
        # 例: 百五 -> 105
        parts = kanji_str.split('百')
        hundreds = simple_map.get(parts[0], 1) if parts[0] else 1

        remainder = 0
        if len(parts) > 1 and parts[1]:
            if '十' in parts[1]:
                remainder = kanji_to_num(parts[1])
            else:
                remainder = simple_map.get(parts[1], 0)

        return hundreds * 100 + remainder

    return kanji_str

def load_enforcement_regulations():
    """抽出した施行規則のJSONを読み込み"""
    with open('enforcement_regulations_extracted.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_enforcement_regulations_js(chapters):
    """施行規則データベースJSファイルを構築"""
    js_lines = []
    js_lines.append('/**')
    js_lines.append(' * 風俗営業等の規制及び業務の適正化等に関する法律施行規則')
    js_lines.append(' * ソース：e-Gov法令検索 公式HTML版 (360M50400000001_20251001_507M60400000017.html)')
    js_lines.append(' * 更新日：2025-11-11')
    js_lines.append(' * ライセンス：CC BY 4.0')
    js_lines.append(' * 章→条→条文の完全な3段階構造')
    js_lines.append(' */')
    js_lines.append('')
    js_lines.append('export const ENFORCEMENT_REGULATIONS = ')
    js_lines.append('{')
    js_lines.append('  "chapters": [')

    for chapter_idx, chapter in enumerate(chapters):
        chapter_num = kanji_to_num(chapter['chapterNum'])
        chapter_name = chapter['chapterName']

        js_lines.append('    {')
        js_lines.append(f'      "chapterNum": {chapter_num},')
        js_lines.append(f'      "chapterName": "{chapter_name}",')
        js_lines.append('      "articles": [')

        for article_idx, article in enumerate(chapter['articles']):
            article_num = article.get('articleNum', '?')
            caption = article.get('caption', '').strip('（）')

            # 本文を構築
            text_parts = []

            # 第1項本文
            if 'content' in article:
                first_paragraph = article['content']

                # 第1項の号を追加
                if 'first_items' in article:
                    item_lines = []
                    for item in article['first_items']:
                        item_num = item['num']
                        item_content = item['content']
                        item_lines.append(f"{item_num} {item_content}")
                    first_paragraph = first_paragraph + '\n' + '\n'.join(item_lines)

                text_parts.append(first_paragraph)

            # 項（第2項以降）
            if 'paragraphs' in article:
                for para in article['paragraphs']:
                    para_num = para['num']
                    para_content = para['content']

                    # この項の号を追加
                    if para.get('items'):
                        para_item_lines = []
                        for item in para['items']:
                            item_num = item['num']
                            item_content = item['content']
                            para_item_lines.append(f"{item_num} {item_content}")
                        para_content = para_content + '\n' + '\n'.join(para_item_lines)

                    text_parts.append(f"{para_num} {para_content}")

            # JSON文字列をエスケープ
            text = '\n'.join(text_parts)
            text_escaped = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

            js_lines.append('        {')
            js_lines.append(f'          "articleNum": "{article_num}",')
            js_lines.append(f'          "title": "{caption}",')
            js_lines.append(f'          "text": "{text_escaped}"')

            if article_idx < len(chapter['articles']) - 1:
                js_lines.append('        },')
            else:
                js_lines.append('        }')

        js_lines.append('      ]')

        if chapter_idx < len(chapters) - 1:
            js_lines.append('    },')
        else:
            js_lines.append('    }')

    js_lines.append('  ]')
    js_lines.append('};')
    js_lines.append('')

    return '\n'.join(js_lines)

def main():
    print("施行規則データベースファイルを構築します...")

    # 抽出した施行規則を読み込み
    chapters = load_enforcement_regulations()
    print(f"✓ {len(chapters)}章を読み込みました")

    # データベースJSを構築
    js_content = build_enforcement_regulations_js(chapters)

    # ファイルに書き込み
    with open('src/constants/enforcementRegulationsDatabase.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    print("✓ enforcementRegulationsDatabase.jsを構築しました")

    # 統計を表示
    total_articles = sum(len(ch['articles']) for ch in chapters)
    print(f"  総章数: {len(chapters)}")
    print(f"  総条文数: {total_articles}")

    for chapter in chapters:
        chapter_num = kanji_to_num(chapter['chapterNum'])
        chapter_name = chapter['chapterName']
        article_count = len(chapter['articles'])
        print(f"  第{chapter_num}章 {chapter_name}: {article_count}条")

if __name__ == '__main__':
    main()

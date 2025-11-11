#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTMLから正確なlawDatabase.jsを再構築するスクリプト
"""

import json
import re

# 漢数字から数字への変換
KANJI_TO_NUM = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
}

def load_extracted_law():
    """抽出したJSON法令を読み込み"""
    with open('extracted_law.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_article_content(article):
    """条文の本文を構築"""
    parts = []

    # 第1項の本文
    if 'content' in article:
        parts.append(article['content'])

    # 項（第2項以降）を追加
    if 'paragraphs' in article:
        for para in article['paragraphs']:
            parts.append(f"{para['num']} {para['content']}")

    # 号を追加（第1項の号と各項の号を統合）
    if 'items' in article:
        # 号の親項を特定する必要があるが、簡易的に項の後に追加
        # 実際のHTMLの構造では号は対応する項の配下にあるため、
        # より詳細なパースが必要だが、ここでは簡易的に扱う
        for item in article['items']:
            # 号は項の一部として統合するべきだが、
            # シンプルにするため、独立して扱う
            # これは不完全な実装のため、後で修正が必要
            pass

    return '\n'.join(parts)

def build_law_database_js(chapters):
    """lawDatabase.jsを再構築"""
    js_lines = []
    js_lines.append('/**')
    js_lines.append(' * 風営法（風俗営業等の規制及び業務の適正化等に関する法律）全文')
    js_lines.append(' * ソース：e-Gov法令検索 公式HTML版 (323AC0000000122_20250628_507AC0000000045.html)')
    js_lines.append(' * 更新日：2025-11-11')
    js_lines.append(' * ライセンス：CC BY 4.0')
    js_lines.append(' * 章→条→条文の完全な3段階構造')
    js_lines.append(' */')
    js_lines.append('')
    js_lines.append('export const WIND_BUSINESS_LAW = ')
    js_lines.append('{')
    js_lines.append('  "chapters": [')

    for chapter_idx, chapter in enumerate(chapters):
        chapter_num = KANJI_TO_NUM.get(chapter['chapterNum'], chapter['chapterNum'])
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
    print("HTMLから正確なlawDatabase.jsを再構築します...")

    # HTMLから抽出した条文を読み込み
    chapters = load_extracted_law()
    print(f"✓ {len(chapters)}章を読み込みました")

    # lawDatabase.jsを再構築
    js_content = build_law_database_js(chapters)

    # ファイルに書き込み
    with open('src/constants/lawDatabase.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    print("✓ lawDatabase.jsを再構築しました")

    # 統計を表示
    total_articles = sum(len(ch['articles']) for ch in chapters)
    print(f"  総章数: {len(chapters)}")
    print(f"  総条文数: {total_articles}")

    for chapter in chapters:
        chapter_num = KANJI_TO_NUM.get(chapter['chapterNum'], chapter['chapterNum'])
        chapter_name = chapter['chapterName']
        article_count = len(chapter['articles'])
        print(f"  第{chapter_num}章 {chapter_name}: {article_count}条")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTMLから抽出した条文とlawDatabase.jsを比較するスクリプト
"""

import json
import re

# 漢数字から数字への変換
KANJI_TO_NUM = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
    '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
    '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
    '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
    '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40,
    '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45,
    '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50,
    '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54, '五十五': 55,
    '五十六': 56, '五十七': 57, '五十八': 58
}

def kanji_to_num(kanji):
    """漢数字を数字に変換"""
    return KANJI_TO_NUM.get(kanji, kanji)

def load_extracted_law():
    """抽出したJSON法令を読み込み"""
    with open('extracted_law.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_law_database():
    """lawDatabase.jsから条文を抽出"""
    with open('law_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['chapters']

def compare_articles(html_chapters, db_chapters):
    """条文を比較"""
    print("=" * 80)
    print("条文の比較")
    print("=" * 80)

    for i, html_chapter in enumerate(html_chapters):
        chapter_num = kanji_to_num(html_chapter['chapterNum'])
        chapter_name = html_chapter['chapterName']

        print(f"\n第{chapter_num}章 {chapter_name}")
        print("-" * 80)

        # データベースから対応する章を探す
        db_chapter = None
        for ch in db_chapters:
            if ch['chapterNum'] == chapter_num:
                db_chapter = ch
                break

        if not db_chapter:
            print(f"  ⚠️  lawDatabase.jsに第{chapter_num}章が見つかりません")
            continue

        # 条文数の比較
        html_article_count = len(html_chapter['articles'])
        db_article_count = len(db_chapter['articles'])

        print(f"  HTML: {html_article_count}条, lawDatabase.js: {db_article_count}条")

        if html_article_count != db_article_count:
            print(f"  ⚠️  条文数が一致しません！")

        # 各条文を比較
        for j, html_article in enumerate(html_chapter['articles']):
            article_num = html_article.get('articleNum', '?')
            caption = html_article.get('caption', '')

            # lawDatabase.jsから対応する条文を探す
            if j < len(db_chapter['articles']):
                db_article = db_chapter['articles'][j]
                db_article_num = db_article.get('articleNum', '?')
                db_title = db_article.get('title', '')

                # 条文番号の比較
                if article_num != db_article_num:
                    print(f"    ❌ 第{article_num}条: 条文番号不一致 (DB: 第{db_article_num}条)")

                # 見出しの比較
                caption_clean = caption.strip('（）')
                if caption_clean != db_title:
                    print(f"    ⚠️  第{article_num}条: 見出し不一致")
                    print(f"       HTML: {caption}")
                    print(f"       DB:   {db_title}")

                # 本文の比較（最初の100文字のみ表示）
                html_content = html_article.get('content', '')
                db_text = db_article.get('text', '')

                # 改行を削除して比較
                html_content_clean = html_content.replace('\n', '')
                db_text_clean = db_text.replace('\n', '').replace(' ', '')

                if html_content_clean[:50] != db_text_clean[:50]:
                    print(f"    ⚠️  第{article_num}条: 本文が異なります")
                    print(f"       HTML (最初の80文字): {html_content[:80]}...")
                    print(f"       DB (最初の80文字):   {db_text[:80]}...")
            else:
                print(f"    ❌ 第{article_num}条: lawDatabase.jsに存在しません")

def main():
    print("風営法の条文を比較します...")

    # HTMLから抽出した条文を読み込み
    html_chapters = load_extracted_law()
    print(f"✓ HTMLから{len(html_chapters)}章を読み込みました")

    # lawDatabase.jsを読み込み
    db_chapters = load_law_database()
    if not db_chapters:
        print("❌ lawDatabase.jsの読み込みに失敗しました")
        return

    print(f"✓ lawDatabase.jsから{len(db_chapters)}章を読み込みました")

    # 比較
    compare_articles(html_chapters, db_chapters)

if __name__ == '__main__':
    main()

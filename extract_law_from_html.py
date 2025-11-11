#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
風営法HTMLから条文を抽出するスクリプト
"""

from bs4 import BeautifulSoup
import json
import re

def extract_articles_from_html(html_file):
    """HTMLファイルから条文を抽出"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # すべての章（Chapter）を取得
    chapters = []
    current_chapter = None
    current_article = None

    # MainProvision セクション内を処理
    main_provision = soup.find('section', id='MainProvision')
    if not main_provision:
        print("MainProvision not found")
        return []

    for section in main_provision.find_all('section', class_='active', recursive=False):
        # 章の処理
        chapter_title_div = section.find('div', class_='ChapterTitle')
        if chapter_title_div and 'Chapter' in section.get('class', []):
            chapter_text = chapter_title_div.get_text(strip=True)
            match = re.match(r'第([一二三四五六七八九十]+)章\s*(.+)', chapter_text)
            if match:
                chapter_num = match.group(1)
                chapter_name = match.group(2)
                current_chapter = {
                    'chapterNum': chapter_num,
                    'chapterName': chapter_name,
                    'articles': []
                }
                chapters.append(current_chapter)
                continue

        # 条文の処理
        if 'Article' in section.get('class', []) and current_chapter:
            article_data = {}

            # 条文のキャプション（見出し）
            caption_div = section.find('div', class_='_div_ArticleCaption')
            if caption_div:
                caption_span = caption_div.find('span', attrs={'data-xpath': ''})
                if caption_span:
                    article_data['caption'] = caption_span.get_text(strip=True)

            # 条文タイトル（第X条）と本文
            title_div = section.find('div', class_='_div_ArticleTitle')
            if title_div:
                # 条文番号を取得（枝番号対応）
                article_num_span = title_div.find('span', style='font-weight: bold;')
                if article_num_span:
                    article_num_text = article_num_span.get_text(strip=True)
                    # 「第三十一条の二」のような枝番号に対応
                    match = re.match(r'第([一二三四五六七八九十百千万0-9]+)条(の[一二三四五六七八九十]+)?', article_num_text)
                    if match:
                        base_num = match.group(1)
                        suffix = match.group(2) if match.group(2) else ''
                        # 枝番号があれば「三十一の二」の形式で保存（「条」は含めない）
                        if suffix:
                            article_data['articleNum'] = base_num + suffix
                        else:
                            article_data['articleNum'] = base_num

                # 条文本文を取得
                content_span = title_div.find('span', attrs={'data-xpath': ''})
                if content_span:
                    article_data['content'] = content_span.get_text(strip=True)

            # 第1項の配下の号を取得（_div_ArticleTitle直後の_div_ItemSentence）
            first_items = []
            # sectionの直接の子要素を順番に処理
            for child in section.children:
                if not hasattr(child, 'get'):
                    continue
                if '_div_ItemSentence' in child.get('class', []):
                    # これは第1項の号
                    item_num_span = child.find('span', style='font-weight: bold;')
                    content_span = child.find('span', attrs={'data-xpath': ''})
                    if item_num_span and content_span:
                        first_items.append({
                            'num': item_num_span.get_text(strip=True),
                            'content': content_span.get_text(strip=True)
                        })
                elif '_div_ParagraphSentence' in child.get('class', []):
                    # 項が始まったら第1項の号は終了
                    break

            if first_items:
                article_data['first_items'] = first_items

            # 項（第2項以降）の取得
            paragraphs = []
            for para_div in section.find_all('div', class_='_div_ParagraphSentence'):
                para_num_span = para_div.find('span', style='font-weight: bold;')
                content_span = para_div.find('span', attrs={'data-xpath': ''})
                if para_num_span and content_span:
                    para_num = para_num_span.get_text(strip=True)
                    para_content = content_span.get_text(strip=True)

                    # この項の配下の号を取得
                    # （項の直後にある_div_ItemSentenceを探す）
                    para_items = []
                    next_sibling = para_div.find_next_sibling()
                    while next_sibling and '_div_ItemSentence' in next_sibling.get('class', []):
                        item_num_span = next_sibling.find('span', style='font-weight: bold;')
                        item_content_span = next_sibling.find('span', attrs={'data-xpath': ''})
                        if item_num_span and item_content_span:
                            para_items.append({
                                'num': item_num_span.get_text(strip=True),
                                'content': item_content_span.get_text(strip=True)
                            })
                        next_sibling = next_sibling.find_next_sibling()
                        if next_sibling and '_div_ParagraphSentence' in next_sibling.get('class', []):
                            # 次の項が始まったら終了
                            break

                    paragraphs.append({
                        'num': para_num,
                        'content': para_content,
                        'items': para_items if para_items else None
                    })

            if paragraphs:
                article_data['paragraphs'] = paragraphs

            if article_data:
                current_chapter['articles'].append(article_data)

    return chapters

def main():
    import sys

    # コマンドライン引数がある場合はそれを使用
    if len(sys.argv) >= 2:
        html_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) >= 3 else 'extracted_law.json'
    else:
        html_file = '323AC0000000122_20250628_507AC0000000045.html'
        output_file = 'extracted_law.json'

    chapters = extract_articles_from_html(html_file)

    # JSON形式で出力
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)

    # サマリーを出力
    print(f"抽出完了: {len(chapters)}章")
    for chapter in chapters:
        print(f"  第{chapter['chapterNum']}章 {chapter['chapterName']}: {len(chapter['articles'])}条")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
風営法HTMLファイルから全条文を抽出してYAMLに変換するスクリプト
"""

from bs4 import BeautifulSoup
import yaml
import re

def clean_text(text):
    """HTMLタグを除去し、テキストをクリーンアップ"""
    if not text:
        return ""
    # 余分な空白を削除
    text = re.sub(r'\s+', '', text)
    return text.strip()

def extract_law_data(html_file):
    """HTMLファイルから法律データを抽出"""

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # タイトルを取得
    title = soup.find('title')
    law_name = title.text if title else "風俗営業等の規制及び業務の適正化等に関する法律"

    # 法令番号を取得
    law_num_elem = soup.find('div', class_='LawNum')
    law_number = clean_text(law_num_elem.text) if law_num_elem else "昭和二十三年法律第百二十二号"

    # 章とその条文を抽出
    chapters = []
    main_provision = soup.find('section', class_='MainProvision')

    if main_provision:
        # MainProvisionの直接の子要素を順に処理
        children = [child for child in main_provision.children if child.name == 'section']

        current_chapter = None
        current_articles = []

        for child in children:
            classes = child.get('class', [])

            if 'Chapter' in classes:
                # 前の章があれば保存
                if current_chapter and current_articles:
                    chapters.append({
                        'chapter_num': current_chapter['num'],
                        'chapter_title': current_chapter['title'],
                        'articles': current_articles
                    })

                # 新しい章を開始
                chapter_title_div = child.find('div', class_='ChapterTitle')
                if chapter_title_div:
                    chapter_text = clean_text(chapter_title_div.text)
                    # 章番号とタイトルを分離
                    chapter_match = re.match(r'(第[一二三四五六七八九十百千万]+章)　?(.*)', chapter_text)
                    if chapter_match:
                        current_chapter = {
                            'num': chapter_match.group(1),
                            'title': chapter_match.group(2)
                        }
                    else:
                        current_chapter = {
                            'num': chapter_text,
                            'title': ""
                        }
                    current_articles = []

            elif 'Article' in classes and current_chapter:
                # 条文を抽出して現在の章に追加
                article_content = extract_article_content(child)
                if article_content:
                    current_articles.append(article_content)

        # 最後の章を保存
        if current_chapter and current_articles:
            chapters.append({
                'chapter_num': current_chapter['num'],
                'chapter_title': current_chapter['title'],
                'articles': current_articles
            })

    return {
        'law': {
            'name': law_name,
            'law_number': law_number,
            'chapters': chapters
        }
    }

def extract_article_content(article_section):
    """条文セクションから条文内容を抽出"""

    # 条文タイトル部分を取得
    article_title_div = article_section.find('div', class_='_div_ArticleTitle')
    if not article_title_div:
        return None

    # 条文番号を取得
    article_num_span = article_title_div.find('span', style='font-weight: bold;')
    if not article_num_span:
        return None

    article_num = clean_text(article_num_span.text)

    # 条文キャプションを取得
    caption_elem = article_section.find('div', class_='_div_ArticleCaption')
    title = ""
    if caption_elem:
        caption_span = caption_elem.find('span', attrs={'data-xpath': True})
        if caption_span:
            title_text = clean_text(caption_span.text)
            # 括弧を除去
            title = title_text.strip('（）')

    # 条文全体のテキストを構築（すべての子要素を順に処理）
    text_parts = []

    # article_sectionの全子要素を順に処理
    for elem in article_section.find_all(['div'], recursive=False):
        classes = elem.get('class', [])

        # ArticleTitle（第1項）
        if '_div_ArticleTitle' in classes:
            content_span = elem.find('span', attrs={'data-xpath': True})
            if content_span:
                text_parts.append(clean_text(content_span.text))

        # ItemSentence（号）
        elif '_div_ItemSentence' in classes:
            num_span = elem.find('span', style='font-weight: bold;')
            text_span = elem.find('span', attrs={'data-xpath': True})
            if num_span and text_span:
                num = clean_text(num_span.text)
                text = clean_text(text_span.text)
                text_parts.append(f"\n{num}　{text}")

        # ParagraphSentence（第2項以降）
        elif '_div_ParagraphSentence' in classes:
            num_span = elem.find('span', style='font-weight: bold;')
            text_span = elem.find('span', attrs={'data-xpath': True})
            if num_span and text_span:
                num = clean_text(num_span.text)
                text = clean_text(text_span.text)
                text_parts.append(f"\n{num}　{text}")

        # Paragraph内のItemSentence（項の中の号）も同様に処理

    full_text = ''.join(text_parts)

    return {
        'article_num': article_num,
        'title': title,
        'text': full_text
    }

def save_to_yaml(data, output_file):
    """YAMLファイルとして保存"""

    class CustomDumper(yaml.SafeDumper):
        """カスタムYAMLダンプクラス"""
        pass

    def str_representer(dumper, data):
        """複数行の文字列を | 形式で出力"""
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    CustomDumper.add_representer(str, str_representer)

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=CustomDumper, allow_unicode=True,
                  default_flow_style=False, sort_keys=False, width=1000)

    print(f"YAMLファイルを保存しました: {output_file}")

def main():
    html_file = '/home/user/pachinko-lawtest/323AC0000000122_20250628_507AC0000000045.html'
    output_file = '/home/user/pachinko-lawtest/rag_data/legal_references/風営法_全条文.yaml'

    print("HTMLファイルから法律データを抽出中...")
    law_data = extract_law_data(html_file)

    print(f"抽出完了:")
    print(f"  章数: {len(law_data['law']['chapters'])}")
    total_articles = sum(len(chapter['articles']) for chapter in law_data['law']['chapters'])
    print(f"  総条文数: {total_articles}")

    # 各章の詳細を表示
    for chapter in law_data['law']['chapters']:
        print(f"  {chapter['chapter_num']} {chapter['chapter_title']}: {len(chapter['articles'])}条")
        if chapter['articles']:
            first_article = chapter['articles'][0]['article_num']
            last_article = chapter['articles'][-1]['article_num']
            print(f"    ({first_article} 〜 {last_article})")

    print("\nYAMLファイルに保存中...")
    save_to_yaml(law_data, output_file)

    print("\n完了!")

if __name__ == '__main__':
    main()

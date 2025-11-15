#!/usr/bin/env python3
"""
YAMLファイルの正確性検証スクリプト
HTMLソースとYAMLファイルを比較し、抽出の正確性を検証する
"""

import yaml
import re
from bs4 import BeautifulSoup
from pathlib import Path

def extract_articles_from_html(html_path):
    """HTMLファイルから条文を抽出（本則のみ）"""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    articles = {}
    chapters = {}

    # 章の抽出 (ChapterTitleクラスから、附則を除く)
    for chapter_div in soup.find_all('div', class_='ChapterTitle'):
        chapter_text = chapter_div.get_text(strip=True)
        # "第一章　総則" のような形式から章番号と章名を抽出
        match = re.match(r'第([一二三四五六七八九十]+)章\s*(.+)', chapter_text)
        if match:
            chapters[match.group(1)] = match.group(2)

    # 条文の抽出（本則のみ、附則を除外）
    # _div_ArticleTitleクラスを持つdivを探す（これが条文タイトル部分）
    article_pattern = re.compile(r'^第([一二三四五六七八九十百千]+)条$')

    for article_div in soup.find_all('div', class_='_div_ArticleTitle'):
        # 親要素を確認して、附則（SupplProvision）内でないことを確認
        parent_section = article_div.find_parent('section', class_='SupplProvision')
        if parent_section:
            # 附則内の条文はスキップ
            continue

        # 条番号を探す
        bold_span = article_div.find('span', style=lambda value: value and 'font-weight: bold' in value)
        if not bold_span:
            continue

        span_text = bold_span.get_text(strip=True)
        match = article_pattern.match(span_text)

        if match:
            article_num_kanji = match.group(1)
            article_num = kanji_to_arabic(article_num_kanji)

            # 同じdiv内の次のspanタグから条文本文を取得
            next_span = bold_span.find_next_sibling('span')
            if next_span and next_span.get('data-xpath') is not None:
                # 第1項の本文を取得
                content_parts = [next_span.get_text(strip=True)]

                # 条文のタイトルを抽出（直前のArticleCaptionから）
                title = ""
                prev_caption = article_div.find_previous_sibling('div', class_='_div_ArticleCaption')
                if prev_caption:
                    caption_span = prev_caption.find('span', attrs={'data-xpath': True})
                    if caption_span:
                        caption_text = caption_span.get_text(strip=True)
                        # 括弧を除去
                        title = caption_text.strip('（）')

                # この条文の後続の項や号を収集
                # 次の条文（_div_ArticleTitle）または章（ChapterTitle）が現れるまで
                current_elem = article_div.find_next_sibling()
                while current_elem:
                    # 次の条文や章が現れたら終了
                    if current_elem.get('class'):
                        classes = current_elem.get('class', [])
                        if '_div_ArticleTitle' in classes or 'ChapterTitle' in classes:
                            break
                        # ArticleCaptionも条文の区切り
                        if '_div_ArticleCaption' in classes:
                            break

                    # 項や号のテキストを収集
                    if current_elem.name == 'div':
                        elem_classes = current_elem.get('class', [])
                        if any(cls in elem_classes for cls in ['_div_ParagraphSentence', '_div_ItemSentence']):
                            # data-xpath属性を持つspanからテキストを取得
                            data_spans = current_elem.find_all('span', attrs={'data-xpath': True})
                            for data_span in data_spans:
                                text = data_span.get_text(strip=True)
                                if text:
                                    content_parts.append(text)

                    current_elem = current_elem.find_next_sibling()

                content = '\n'.join(content_parts)

                articles[f"第{article_num}条"] = {
                    'title': title,
                    'content': content,
                    'article_number': article_num
                }

    return chapters, articles

def kanji_to_arabic(kanji_num):
    """漢数字をアラビア数字に変換"""
    kanji_dict = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '百': 100, '千': 1000
    }

    if kanji_num in kanji_dict:
        return kanji_dict[kanji_num]

    # より複雑な数字の変換
    result = 0
    temp = 0
    for char in kanji_num:
        if char in ['十', '百', '千']:
            if temp == 0:
                temp = 1
            result += temp * kanji_dict[char]
            temp = 0
        else:
            temp = kanji_dict.get(char, 0)

    return result + temp

def load_yaml_data(yaml_path):
    """YAMLファイルを読み込む"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normalize_text(text):
    """テキストを正規化（比較用）"""
    # 改行を統一
    text = re.sub(r'\s+', ' ', text)
    # 前後の空白を削除
    text = text.strip()
    return text

def compare_articles(html_articles, yaml_data, article_numbers):
    """指定された条文を比較"""
    results = []

    for article_num in article_numbers:
        article_key = f"第{article_num}条"

        # HTML側のデータ
        html_data = html_articles.get(article_key)

        # YAML側のデータを検索
        yaml_article = None
        # YAMLの構造: law.chapters[].articles[]
        law_data = yaml_data.get('law', {})
        for chapter in law_data.get('chapters', []):
            for article in chapter.get('articles', []):
                # article_numを漢数字からアラビア数字に変換
                article_num_str = article.get('article_num', '')
                # "第一条" -> 1
                match = re.match(r'第([一二三四五六七八九十百千]+)条', article_num_str)
                if match:
                    yaml_article_num = kanji_to_arabic(match.group(1))
                    if yaml_article_num == article_num:
                        yaml_article = article
                        break
            if yaml_article:
                break

        result = {
            'article_number': article_num,
            'article_key': article_key,
            'html_exists': html_data is not None,
            'yaml_exists': yaml_article is not None,
        }

        if html_data and yaml_article:
            html_content = html_data['content']
            yaml_content = yaml_article.get('text', '')  # YAMLでは'text'キー

            # タイトル比較
            html_title = html_data['title']
            yaml_title = yaml_article.get('title', '')

            result['title_match'] = html_title == yaml_title
            result['html_title'] = html_title
            result['yaml_title'] = yaml_title

            # 内容の冒頭と文末を比較
            html_start = html_content[:50] if len(html_content) >= 50 else html_content
            yaml_start = yaml_content[:50] if len(yaml_content) >= 50 else yaml_content

            html_end = html_content[-50:] if len(html_content) >= 50 else html_content
            yaml_end = yaml_content[-50:] if len(yaml_content) >= 50 else yaml_content

            result['html_start'] = html_start
            result['yaml_start'] = yaml_start
            result['html_end'] = html_end
            result['yaml_end'] = yaml_end

            result['html_length'] = len(html_content)
            result['yaml_length'] = len(yaml_content)

            # 正規化して比較
            html_normalized = normalize_text(html_content)
            yaml_normalized = normalize_text(yaml_content)

            result['content_match'] = html_normalized == yaml_normalized

            # 完全一致していない場合、差分を調査
            if not result['content_match']:
                result['normalized_html_start'] = html_normalized[:100]
                result['normalized_yaml_start'] = yaml_normalized[:100]

        results.append(result)

    return results

def print_verification_report(results, chapters_html, yaml_data):
    """検証結果レポートを出力"""
    print("=" * 80)
    print("【風営法YAML検証レポート】")
    print("=" * 80)
    print()

    # 章構造の検証
    print("■ 章構造の検証")
    print("-" * 80)
    law_data = yaml_data.get('law', {})
    yaml_chapters = law_data.get('chapters', [])
    print(f"HTML章数: {len(chapters_html)}")
    print(f"YAML章数: {len(yaml_chapters)}")
    print()

    for i, chapter in enumerate(yaml_chapters, 1):
        chapter_num = chapter.get('chapter_num', 'N/A')
        chapter_title = chapter.get('chapter_title', 'N/A')
        article_count = len(chapter.get('articles', []))
        print(f"{chapter_num}: {chapter_title} ({article_count}条)")
    print()

    # 条文詳細検証
    print("■ 条文詳細検証（第1条〜第30条を重点的に）")
    print("-" * 80)

    for result in results:
        article_num = result['article_number']
        article_key = result['article_key']

        if result['html_exists'] and result['yaml_exists']:
            status = "✓ OK" if result['content_match'] and result['title_match'] else "✗ 問題あり"
        else:
            status = "✗ データ欠損"

        print(f"\n{article_key}（{result.get('yaml_title', 'N/A')}）: {status}")

        if not result['html_exists']:
            print("  ⚠ HTMLに存在しません")
            continue

        if not result['yaml_exists']:
            print("  ⚠ YAMLに存在しません")
            continue

        # タイトル確認
        if not result['title_match']:
            print(f"  タイトル不一致:")
            print(f"    HTML: {result['html_title']}")
            print(f"    YAML: {result['yaml_title']}")

        # 冒頭確認
        print(f"  HTML冒頭（50文字）: {result['html_start']}")
        print(f"  YAML冒頭（50文字）: {result['yaml_start']}")

        if result['html_start'] == result['yaml_start']:
            print("  冒頭一致: ✓")
        else:
            print("  冒頭一致: ✗")

        # 文末確認
        if len(result['html_end']) > 20 or len(result['yaml_end']) > 20:
            print(f"  HTML文末（50文字）: {result['html_end']}")
            print(f"  YAML文末（50文字）: {result['yaml_end']}")

            if result['html_end'] == result['yaml_end']:
                print("  文末一致: ✓")
            else:
                print("  文末一致: ✗")

        # 文字数確認
        print(f"  文字数 - HTML: {result['html_length']}, YAML: {result['yaml_length']}")

        # 正規化後の不一致詳細
        if not result['content_match']:
            print("  【詳細】正規化後も不一致:")
            print(f"    HTML正規化冒頭: {result.get('normalized_html_start', 'N/A')}")
            print(f"    YAML正規化冒頭: {result.get('normalized_yaml_start', 'N/A')}")

    print()
    print("=" * 80)
    print("■ 最終判定")
    print("=" * 80)

    total = len(results)
    matched = sum(1 for r in results if r.get('content_match') and r.get('title_match'))

    print(f"検証条文数: {total}")
    print(f"完全一致: {matched}")
    print(f"不一致: {total - matched}")
    print()

    if matched == total:
        print("✓ YAMLファイルは正式ソースとして使用可能です")
    else:
        print("✗ YAMLファイルに問題があります。修正が必要です")
        print()
        print("【修正が必要な条文】")
        for r in results:
            if not (r.get('content_match') and r.get('title_match')):
                print(f"  - {r['article_key']}")

def main():
    # ファイルパス
    html_path = Path('/home/user/pachinko-lawtest/323AC0000000122_20250628_507AC0000000045.html')
    yaml_path = Path('/home/user/pachinko-lawtest/rag_data/legal_references/風営法_全条文.yaml')

    print("HTMLファイルから条文を抽出中...")
    chapters_html, articles_html = extract_articles_from_html(html_path)
    print(f"抽出完了: {len(chapters_html)}章, {len(articles_html)}条")
    print()

    print("YAMLファイルを読み込み中...")
    yaml_data = load_yaml_data(yaml_path)
    print(f"読み込み完了")
    print()

    # 重点的に検証する条文（第1条〜第30条）
    target_articles = list(range(1, 31))

    print("条文を比較中...")
    results = compare_articles(articles_html, yaml_data, target_articles)
    print()

    # レポート出力
    print_verification_report(results, chapters_html, yaml_data)

if __name__ == "__main__":
    main()

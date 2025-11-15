#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
風営法データベースの完全レビュースクリプト v4
HTMLソースとlawDatabase.jsの条文を1つずつ比較
"""
import re
import json

# 漢数字変換テーブル
KANJI_NUMBERS = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
    '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
    '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
    '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
}

def kanji_to_number(kanji):
    """漢数字をアラビア数字に変換"""
    if kanji in KANJI_NUMBERS:
        return KANJI_NUMBERS[kanji]
    # 特殊な形式（例：七の二）
    if 'の' in kanji:
        parts = kanji.split('の')
        if len(parts) == 2 and parts[0] in KANJI_NUMBERS and parts[1] in KANJI_NUMBERS:
            return f"{KANJI_NUMBERS[parts[0]]}_{KANJI_NUMBERS[parts[1]]}"
    return kanji

def number_to_kanji(num):
    """アラビア数字を漢数字に変換"""
    for k, v in KANJI_NUMBERS.items():
        if v == num:
            return k
    return str(num)

def extract_from_html(html_path):
    """HTMLファイルから条文を抽出"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    articles = {}

    # 条文ブロックを抽出（<section class="active Article">...</section>）
    article_pattern = r'<section[^>]*class="[^"]*Article[^"]*"[^>]*>(.*?)</section>'
    article_blocks = re.findall(article_pattern, html_content, re.DOTALL)

    for block in article_blocks:
        # タイトル（目的）などを取得
        title_match = re.search(r'<span data-xpath="">（([^）]+)）</span>', block)
        title = title_match.group(1) if title_match else ''

        # 条番号を取得
        article_num_match = re.search(r'<span style="font-weight: bold;">第([^条]+)条</span>', block)
        if not article_num_match:
            continue

        article_num_kanji = article_num_match.group(1)
        article_num = kanji_to_number(article_num_kanji)

        # 条文内容を取得（ArticleTitleの中身）
        # _div_ArticleTitleの中のdata-xpath属性を持つspanタグ内のテキストを取得
        content_match = re.search(
            r'<div[^>]*class="[^"]*_div_ArticleTitle[^"]*"[^>]*>.*?<span data-xpath="">([^<]*(?:<[^>]+>[^<]*)*?)</span>',
            block,
            re.DOTALL
        )

        if content_match:
            text = content_match.group(1)
            # HTMLタグを除去（ルビタグなどを含む）
            text = re.sub(r'<[^>]+>', '', text)
            # エンティティをデコード
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&amp;', '&')
            text = text.replace('\u3000', '')  # 全角スペース
            # 余分な空白を除去（比較のため）
            text_normalized = re.sub(r'\s+', '', text)

            articles[article_num] = {
                'title': title,
                'text': text,
                'text_normalized': text_normalized
            }

    return articles

def extract_from_database(db_path):
    """lawDatabase.jsから風営法の条文を抽出"""
    # sedで8-539行目を抽出
    import subprocess
    result = subprocess.run(
        ['sed', '-n', '9,539p', db_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error extracting WIND_BUSINESS_LAW: {result.stderr}")
        return {}

    law_data_str = result.stdout

    # JavaScript のコメントを除去
    law_data_str = re.sub(r'//.*?\n', '\n', law_data_str)

    # 末尾のカンマを除去（JSONではエラーになる）
    law_data_str = re.sub(r',(\s*[}\]])', r'\1', law_data_str)

    # JSONとして解析
    try:
        fueihou = json.loads(law_data_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"First 500 chars: {law_data_str[:500]}")
        return {}

    articles = {}
    for chapter in fueihou.get('chapters', []):
        for article in chapter.get('articles', []):
            article_num_kanji = article.get('articleNum', '')
            article_num = kanji_to_number(article_num_kanji)

            title = article.get('title', '')
            text = article.get('text', '')
            # 空白を除去して比較しやすくする
            text_normalized = re.sub(r'\s+', '', text)

            articles[article_num] = {
                'title': title,
                'text': text,
                'text_normalized': text_normalized,
                'articleNum': article_num_kanji
            }

    return articles

def compare_articles(html_articles, db_articles, max_article=30):
    """条文を比較"""
    results = {
        'perfect_match': [],
        'partial_match': [],
        'mismatch': [],
        'missing_in_html': [],
        'missing_in_db': []
    }

    for i in range(1, max_article + 1):
        article_num = i

        print(f"\n{'='*80}")
        print(f"第{article_num}条（{number_to_kanji(article_num)}）の比較")
        print(f"{'='*80}")

        if article_num not in html_articles:
            print(f"⚠️  HTMLソースに第{article_num}条が見つかりません")
            results['missing_in_html'].append(article_num)
            continue

        if article_num not in db_articles:
            print(f"❌ データベースに第{article_num}条が見つかりません")
            results['missing_in_db'].append(article_num)
            continue

        html_article = html_articles[article_num]
        db_article = db_articles[article_num]

        # タイトルの比較
        print(f"タイトル（HTML）: {html_article['title']}")
        print(f"タイトル（DB）:   {db_article['title']}")

        title_match = html_article['title'].strip() == db_article['title'].strip()
        if not title_match:
            print(f"  ⚠️  タイトルが一致しません")

        # テキストの比較（空白を除去して正規化）
        html_text = html_article['text_normalized']
        db_text = db_article['text_normalized']

        print(f"\n内容の長さ:")
        print(f"  HTML: {len(html_text)} 文字")
        print(f"  DB:   {len(db_text)} 文字")

        # 完全一致チェック
        if html_text == db_text:
            print(f"✅ 完全一致")
            results['perfect_match'].append(article_num)
        else:
            # 差分を詳細に分析
            # 最初の不一致箇所を見つける
            first_diff_pos = None
            for j in range(min(len(html_text), len(db_text))):
                if html_text[j] != db_text[j]:
                    first_diff_pos = j
                    break

            if first_diff_pos is None:
                # 一方が他方の部分文字列
                if len(db_text) < len(html_text):
                    missing_ratio = (len(html_text) - len(db_text)) / len(html_text) * 100
                    print(f"⚠️  部分一致: DBはHTMLの {100-missing_ratio:.1f}% の内容を含む")
                    print(f"   欠けている文字数: {len(html_text) - len(db_text)}")
                    print(f"   DBに欠けている末尾: ...{html_text[len(db_text):len(db_text)+100]}...")
                else:
                    extra_ratio = (len(db_text) - len(html_text)) / len(db_text) * 100
                    print(f"⚠️  部分一致: DBにHTMLより {extra_ratio:.1f}% 多い内容が含まれる")
                    print(f"   余分な文字数: {len(db_text) - len(html_text)}")
                    print(f"   DBの余分な末尾: ...{db_text[len(html_text):len(html_text)+100]}...")
                results['partial_match'].append(article_num)
            else:
                # 中間で不一致
                print(f"❌ 不一致: 内容が位置 {first_diff_pos} から異なります")
                start = max(0, first_diff_pos - 30)
                end = min(len(html_text), first_diff_pos + 70)
                end_db = min(len(db_text), first_diff_pos + 70)

                print(f"\n差分の詳細（位置{first_diff_pos}付近）:")
                print(f"  HTML[{start}:{end}]:")
                print(f"    ...{html_text[start:end]}...")
                print(f"  DB  [{start}:{end_db}]:")
                print(f"    ...{db_text[start:end_db]}...")

                # 先頭から何文字一致しているか
                print(f"\n  先頭から {first_diff_pos} 文字は一致")

                # 不一致の文字を表示
                if first_diff_pos < len(html_text) and first_diff_pos < len(db_text):
                    print(f"  不一致の文字: HTML='{html_text[first_diff_pos]}' vs DB='{db_text[first_diff_pos]}'")

                results['mismatch'].append(article_num)

    return results

def main():
    html_path = '/home/user/pachinko-lawtest/323AC0000000122_20250628_507AC0000000045.html'
    db_path = '/home/user/pachinko-lawtest/src/constants/lawDatabase.js'

    print("="*80)
    print("風営法データベースの完全レビュー v4")
    print("="*80)
    print(f"HTMLソース: {html_path}")
    print(f"データベース: {db_path}")

    print("\n" + "="*80)
    print("ステップ1: HTMLソースから条文を抽出")
    print("="*80)
    html_articles = extract_from_html(html_path)
    print(f"抽出された条文数: {len(html_articles)}")
    if html_articles:
        article_nums = sorted([a for a in html_articles.keys() if isinstance(a, int)])
        print(f"条文範囲: 第{min(article_nums)}条 〜 第{max(article_nums)}条")

    print("\n" + "="*80)
    print("ステップ2: データベースから風営法の条文を抽出")
    print("="*80)
    db_articles = extract_from_database(db_path)
    print(f"抽出された条文数: {len(db_articles)}")
    if db_articles:
        article_nums = sorted([a for a in db_articles.keys() if isinstance(a, int)])
        print(f"条文範囲: 第{min(article_nums)}条 〜 第{max(article_nums)}条")

    print("\n" + "="*80)
    print("ステップ3: 第1条〜第30条の比較")
    print("="*80)
    results = compare_articles(html_articles, db_articles, max_article=30)

    # 最終レポート
    print("\n" + "="*80)
    print("【最終レポート】風営法データベースの完全レビュー結果")
    print("="*80)

    print(f"\n✅ 完全一致: {len(results['perfect_match'])} 条")
    if results['perfect_match']:
        print(f"   条文: {', '.join(['第' + str(n) + '条' for n in results['perfect_match']])}")

    print(f"\n⚠️  部分一致: {len(results['partial_match'])} 条")
    if results['partial_match']:
        print(f"   条文: {', '.join(['第' + str(n) + '条' for n in results['partial_match']])}")

    print(f"\n❌ 不一致: {len(results['mismatch'])} 条")
    if results['mismatch']:
        print(f"   条文: {', '.join(['第' + str(n) + '条' for n in results['mismatch']])}")

    print(f"\n🔍 HTMLに欠損: {len(results['missing_in_html'])} 条")
    if results['missing_in_html']:
        print(f"   条文: {', '.join(['第' + str(n) + '条' for n in results['missing_in_html']])}")

    print(f"\n🔍 DBに欠損: {len(results['missing_in_db'])} 条")
    if results['missing_in_db']:
        print(f"   条文: {', '.join(['第' + str(n) + '条' for n in results['missing_in_db']])}")

    # 法的正確性の総合評価
    total = len(results['perfect_match']) + len(results['partial_match']) + len(results['mismatch'])
    if total > 0:
        accuracy = (len(results['perfect_match']) / total) * 100
        print(f"\n【法的正確性の総合評価】")
        print(f"  完全一致率: {accuracy:.1f}%")
        print(f"  比較対象: {total} 条")
        if accuracy == 100:
            print(f"  評価: ⭐⭐⭐⭐⭐ 完璧！法的正確性100%達成")
        elif accuracy >= 90:
            print(f"  評価: ⭐⭐⭐⭐ 優秀（一部要確認）")
        elif accuracy >= 70:
            print(f"  評価: ⭐⭐⭐ 良好（改善推奨）")
        else:
            print(f"  評価: ⭐⭐ 要改善")

if __name__ == '__main__':
    main()

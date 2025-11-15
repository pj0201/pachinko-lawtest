#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
風営法データベースの完全レビュースクリプト
HTMLソースとlawDatabase.jsの条文を1つずつ比較
"""
import re
import json

def extract_from_html(html_path):
    """HTMLファイルから条文を抽出"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    articles = {}

    # 条文ブロックを抽出（<div class="Article"...>...</div>）
    article_pattern = r'<div class="Article[^"]*"[^>]*>(.*?)</div>\s*(?=<div class="(?:Article|Chapter)|$)'
    article_blocks = re.findall(article_pattern, html_content, re.DOTALL)

    for block in article_blocks:
        # 条番号を取得
        article_num_match = re.search(r'<div class="ArticleNum">第(\d+)条', block)
        if not article_num_match:
            continue

        article_num = article_num_match.group(1)

        # タイトルを取得
        title_match = re.search(r'<div class="ArticleTitle">([^<]+)</div>', block)
        title = title_match.group(1) if title_match else ''

        # 条文内容を取得（ArticleCaptionの中身）
        caption_match = re.search(r'<div class="ArticleCaption"[^>]*>(.*?)</div>', block, re.DOTALL)
        if caption_match:
            text = caption_match.group(1)
            # HTMLタグを除去
            text = re.sub(r'<[^>]+>', '', text)
            # エンティティをデコード
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&amp;', '&')
            # 余分な空白を整理
            text = re.sub(r'\s+', '', text)

            articles[article_num] = {
                'title': title.strip(),
                'text': text
            }

    return articles

def extract_from_database(db_path):
    """lawDatabase.jsから風営法の条文を抽出"""
    with open(db_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # export const lawDatabase = [...] を抽出
    match = re.search(r'export const lawDatabase = (\[[\s\S]*?\]);?\s*$', content, re.MULTILINE)
    if not match:
        print("Error: lawDatabase not found")
        return {}

    law_data_str = match.group(1)

    # JavaScriptのコメントを除去
    law_data_str = re.sub(r'//.*?\n', '\n', law_data_str)

    try:
        law_data = json.loads(law_data_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {}

    # 風営法を探す
    fueihou = None
    for law in law_data:
        if '風俗営業等の規制及び業務の適正化等に関する法律' in law.get('lawName', ''):
            fueihou = law
            break

    if not fueihou:
        print("Error: 風営法 not found")
        return {}

    articles = {}
    for article in fueihou.get('articles', []):
        article_num = str(article.get('articleNumber', ''))
        title = article.get('title', '')
        text = article.get('text', '')
        # 空白を除去して比較しやすくする
        text_normalized = re.sub(r'\s+', '', text)

        articles[article_num] = {
            'title': title,
            'text': text,
            'text_normalized': text_normalized
        }

    return articles

def compare_articles(html_articles, db_articles, max_article=30):
    """条文を比較"""
    results = {
        'perfect_match': [],
        'partial_match': [],
        'mismatch': []
    }

    for i in range(1, max_article + 1):
        article_num = str(i)

        print(f"\n{'='*80}")
        print(f"第{article_num}条の比較")
        print(f"{'='*80}")

        if article_num not in html_articles:
            print(f"⚠️  HTMLソースに第{article_num}条が見つかりません")
            continue

        if article_num not in db_articles:
            print(f"❌ データベースに第{article_num}条が見つかりません")
            results['mismatch'].append(article_num)
            continue

        html_article = html_articles[article_num]
        db_article = db_articles[article_num]

        # タイトルの比較
        print(f"タイトル（HTML）: {html_article['title']}")
        print(f"タイトル（DB）:   {db_article['title']}")

        # テキストの比較（空白を除去して正規化）
        html_text = html_article['text']
        db_text = db_article['text_normalized']

        print(f"\n内容の長さ:")
        print(f"  HTML: {len(html_text)} 文字")
        print(f"  DB:   {len(db_text)} 文字")

        # 完全一致チェック
        if html_text == db_text:
            print(f"✅ 完全一致")
            results['perfect_match'].append(article_num)
        elif db_text in html_text or html_text in db_text:
            # 部分一致
            if len(db_text) < len(html_text):
                missing_ratio = (len(html_text) - len(db_text)) / len(html_text) * 100
                print(f"⚠️  部分一致: DBは HTMLの {100-missing_ratio:.1f}% の内容を含む")
                print(f"   欠けている文字数: {len(html_text) - len(db_text)}")
            else:
                extra_ratio = (len(db_text) - len(html_text)) / len(db_text) * 100
                print(f"⚠️  部分一致: DBに余分な内容が {extra_ratio:.1f}% 含まれる")
                print(f"   余分な文字数: {len(db_text) - len(html_text)}")

            # 差分を表示（最初の不一致部分）
            print(f"\n差分の詳細:")
            for j in range(min(len(html_text), len(db_text))):
                if j >= len(html_text) or j >= len(db_text) or html_text[j] != db_text[j]:
                    start = max(0, j - 50)
                    end = min(len(html_text), j + 50)
                    print(f"  HTML[{start}:{end}]: ...{html_text[start:end]}...")
                    end_db = min(len(db_text), j + 50)
                    print(f"  DB  [{start}:{end_db}]: ...{db_text[start:end_db]}...")
                    break

            results['partial_match'].append(article_num)
        else:
            print(f"❌ 不一致: 内容が異なります")
            # 最初の100文字を表示
            print(f"\nHTML（最初の100文字）:")
            print(f"  {html_text[:100]}...")
            print(f"\nDB（最初の100文字）:")
            print(f"  {db_text[:100]}...")
            results['mismatch'].append(article_num)

    return results

def main():
    html_path = '/home/user/pachinko-lawtest/323AC0000000122_20250628_507AC0000000045.html'
    db_path = '/home/user/pachinko-lawtest/src/constants/lawDatabase.js'

    print("風営法データベースの完全レビューを開始します...")
    print(f"HTMLソース: {html_path}")
    print(f"データベース: {db_path}")

    print("\n" + "="*80)
    print("ステップ1: HTMLソースから条文を抽出")
    print("="*80)
    html_articles = extract_from_html(html_path)
    print(f"抽出された条文数: {len(html_articles)}")

    print("\n" + "="*80)
    print("ステップ2: データベースから風営法の条文を抽出")
    print("="*80)
    db_articles = extract_from_database(db_path)
    print(f"抽出された条文数: {len(db_articles)}")

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
        print(f"   条文: {', '.join(['第' + n + '条' for n in results['perfect_match']])}")

    print(f"\n⚠️  部分一致: {len(results['partial_match'])} 条")
    if results['partial_match']:
        print(f"   条文: {', '.join(['第' + n + '条' for n in results['partial_match']])}")

    print(f"\n❌ 不一致: {len(results['mismatch'])} 条")
    if results['mismatch']:
        print(f"   条文: {', '.join(['第' + n + '条' for n in results['mismatch']])}")

    # 法的正確性の総合評価
    total = len(results['perfect_match']) + len(results['partial_match']) + len(results['mismatch'])
    if total > 0:
        accuracy = (len(results['perfect_match']) / total) * 100
        print(f"\n【法的正確性の総合評価】")
        print(f"  完全一致率: {accuracy:.1f}%")
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

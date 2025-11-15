#!/usr/bin/env python3
"""
特定の条文の詳細確認スクリプト
"""

import yaml
import re
from bs4 import BeautifulSoup

def load_yaml_article(yaml_path, article_num):
    """YAMLから特定の条文を取得"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    law_data = data.get('law', {})
    for chapter in law_data.get('chapters', []):
        for article in chapter.get('articles', []):
            article_num_str = article.get('article_num', '')
            match = re.match(r'第([一二三四五六七八九十百千]+)条', article_num_str)
            if match:
                from verify_yaml_accuracy import kanji_to_arabic
                yaml_article_num = kanji_to_arabic(match.group(1))
                if yaml_article_num == article_num:
                    return article
    return None

def main():
    yaml_path = '/home/user/pachinko-lawtest/rag_data/legal_references/風営法_全条文.yaml'

    # 第2条の詳細確認
    print("=" * 80)
    print("【第2条の詳細確認】")
    print("=" * 80)

    article_2 = load_yaml_article(yaml_path, 2)
    if article_2:
        print(f"条番号: {article_2.get('article_num')}")
        print(f"タイトル: {article_2.get('title')}")
        print()
        print("【本文冒頭200文字】")
        text = article_2.get('text', '')
        print(text[:200])
        print()
        print("【号番号の確認】")
        # 号番号を抽出
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):
            if re.match(r'^[一二三四五六七八九十]+\s', line):
                print(f"  行{i+1}: {line[:80]}")

    print()
    print("=" * 80)
    print("【第4条の詳細確認】")
    print("=" * 80)

    article_4 = load_yaml_article(yaml_path, 4)
    if article_4:
        print(f"条番号: {article_4.get('article_num')}")
        print(f"タイトル: {article_4.get('title')}")
        print()
        print("【本文冒頭200文字】")
        text = article_4.get('text', '')
        print(text[:200])
        print()
        print("【号番号の確認】")
        # 号番号を抽出
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):
            if re.match(r'^[一二三四五六七八九十]+\s', line):
                print(f"  行{i+1}: {line[:80]}")

    print()
    print("=" * 80)
    print("【第20条の詳細確認（項番号）】")
    print("=" * 80)

    article_20 = load_yaml_article(yaml_path, 20)
    if article_20:
        print(f"条番号: {article_20.get('article_num')}")
        print(f"タイトル: {article_20.get('title')}")
        print()
        print("【本文冒頭300文字】")
        text = article_20.get('text', '')
        print(text[:300])
        print()
        print("【項番号の確認】")
        # 項番号を抽出
        lines = text.split('\n')
        for i, line in enumerate(lines[:30]):
            if re.match(r'^[０-９２３４５６７８９]+\s', line) or re.match(r'^\d+\s', line):
                print(f"  行{i+1}: {line[:80]}")

if __name__ == "__main__":
    main()

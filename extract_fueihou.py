#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
風営法の条文をlawDatabase.jsから抽出するスクリプト
"""
import re
import json

# lawDatabase.jsを読み込み
with open('/home/user/pachinko-lawtest/src/constants/lawDatabase.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 風営法のデータを抽出（export const lawDatabase = [...] の形式）
# 風営法の部分を探す
match = re.search(r'export const lawDatabase = (\[[\s\S]*?\]);', content)
if not match:
    print("lawDatabase not found")
    exit(1)

# JSONとして解析（JavaScriptのコメントを除去）
law_data_str = match.group(1)

# JavaScriptの配列をPythonで評価できる形式に変換
# まずコメントを除去
law_data_str = re.sub(r'//.*?\n', '\n', law_data_str)

# evalは危険なので、jsonとして読み込む
# ただし、JavaScriptの配列なので、一部調整が必要
try:
    law_data = json.loads(law_data_str)
except:
    # 手動でパースする必要がある場合
    print("JSON parsing failed, trying manual parsing")
    exit(1)

# 風営法を探す
fueihou = None
for law in law_data:
    if '風俗営業等の規制及び業務の適正化等に関する法律' in law.get('lawName', ''):
        fueihou = law
        break

if not fueihou:
    print("風営法 not found in database")
    exit(1)

# 第1条から第30条を抽出
articles = fueihou.get('articles', [])
for i, article in enumerate(articles[:30]):
    article_num = article.get('articleNumber', f'Article {i+1}')
    title = article.get('title', '')
    text = article.get('text', '')

    print(f"\n{'='*80}")
    print(f"第{article_num}条: {title}")
    print(f"{'='*80}")
    print(text[:500])  # 最初の500文字を表示
    if len(text) > 500:
        print(f"... (total {len(text)} characters)")

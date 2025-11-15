#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
風営法データベースの完全レビュー - 最終版
lawDatabase.jsの該当行を直接読み込んでHTMLと比較
"""
import re

# 漢数字→数字マッピング
KANJI_TO_NUM = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
    '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
    '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
}

def extract_html_articles(html_path):
    """HTMLから条文を抽出"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    articles = {}
    pattern = r'<section[^>]*class="[^"]*Article[^"]*"[^>]*>(.*?)</section>'

    for block in re.findall(pattern, content, re.DOTALL):
        # タイトル
        title_match = re.search(r'<span data-xpath="">（([^）]+)）</span>', block)
        title = title_match.group(1) if title_match else ''

        # 条番号
        num_match = re.search(r'<span style="font-weight: bold;">第([^条]+)条</span>', block)
        if not num_match:
            continue

        kanji = num_match.group(1)
        if kanji not in KANJI_TO_NUM:
            continue

        num = KANJI_TO_NUM[kanji]

        # 本文
        text_match = re.search(
            r'<div[^>]*class="[^"]*_div_ArticleTitle[^"]*"[^>]*>.*?<span data-xpath="">([^<]*(?:<[^>]+>[^<]*)*?)</span>',
            block,
            re.DOTALL
        )

        if text_match:
            text = text_match.group(1)
            text = re.sub(r'<[^>]+>', '', text)  # HTMLタグ除去
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
            text_norm = re.sub(r'\s+', '', text)  # 空白除去

            articles[num] = {'title': title, 'text_norm': text_norm}

    return articles

def extract_db_articles(db_path):
    """lawDatabase.jsから条文を抽出"""
    # ファイルの8-539行目を読み込む（WIND_BUSINESS_LAW）
    with open(db_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 8行目から539行目まで（0-indexedなので7-538）
    wind_law_lines = lines[7:539]
    content = ''.join(wind_law_lines)

    articles = {}

    # 各条文ブロックを抽出（articleNum, title, textのセット）
    # 複雑な文字列を扱うため、行ベースで解析
    current_article = None
    current_title = None
    current_text_lines = []
    in_text = False

    for line in wind_law_lines:
        # articleNum
        article_match = re.search(r'"articleNum":\s*"([^"]+)"', line)
        if article_match:
            # 前の条文を保存
            if current_article and current_article in KANJI_TO_NUM:
                text = ''.join(current_text_lines)
                text = text.replace('\\n', '').replace('\\', '')
                text_norm = re.sub(r'\s+', '', text)
                articles[KANJI_TO_NUM[current_article]] = {
                    'title': current_title,
                    'text_norm': text_norm
                }

            current_article = article_match.group(1)
            current_text_lines = []
            in_text = False

        # title
        title_match = re.search(r'"title":\s*"([^"]+)"', line)
        if title_match:
            current_title = title_match.group(1)

        # text開始
        if '"text":' in line:
            in_text = True
            # 同じ行にテキストがあるかチェック
            text_start = re.search(r'"text":\s*"(.*)', line)
            if text_start:
                current_text_lines.append(text_start.group(1))
        elif in_text:
            # text継続中
            if line.strip().startswith('}'):
                # 条文終了
                in_text = False
            elif line.strip().endswith('",') or line.strip().endswith('"'):
                # text終了行
                clean_line = line.strip().rstrip('",').rstrip('"')
                current_text_lines.append(clean_line)
                in_text = False
            else:
                current_text_lines.append(line)

    # 最後の条文を保存
    if current_article and current_article in KANJI_TO_NUM:
        text = ''.join(current_text_lines)
        text = text.replace('\\n', '').replace('\\', '')
        text_norm = re.sub(r'\s+', '', text)
        articles[KANJI_TO_NUM[current_article]] = {
            'title': current_title,
            'text_norm': text_norm
        }

    return articles

def main():
    html_path = '/home/user/pachinko-lawtest/323AC0000000122_20250628_507AC0000000045.html'
    db_path = '/home/user/pachinko-lawtest/src/constants/lawDatabase.js'

    print("="*80)
    print("【風営法データベースの完全レビュー】最終版")
    print("="*80)

    print("\nステップ1: HTMLから条文を抽出...")
    html_articles = extract_html_articles(html_path)
    print(f"  抽出成功: {len(html_articles)} 条")

    print("\nステップ2: lawDatabase.jsから条文を抽出...")
    db_articles = extract_db_articles(db_path)
    print(f"  抽出成功: {len(db_articles)} 条")

    print("\nステップ3: 第1条〜第30条の比較\n")

    perfect = []
    partial = []
    mismatch = []
    missing_db = []

    for i in range(1, 31):
        print(f"{'='*80}")
        print(f"第{i}条の比較")
        print(f"{'='*80}")

        if i not in html_articles:
            print(f"⚠️  HTMLに見つかりません")
            continue

        if i not in db_articles:
            print(f"❌ データベースに見つかりません")
            missing_db.append(i)
            continue

        html = html_articles[i]
        db = db_articles[i]

        print(f"タイトル（HTML）: {html['title']}")
        print(f"タイトル（DB）:   {db['title']}")

        title_ok = html['title'] == db['title']
        if not title_ok:
            print("  ⚠️  タイトル不一致")

        html_text = html['text_norm']
        db_text = db['text_norm']

        print(f"\n内容長:")
        print(f"  HTML: {len(html_text)} 文字")
        print(f"  DB:   {len(db_text)} 文字")

        if html_text == db_text:
            print("✅ 完全一致")
            perfect.append(i)
        else:
            # 差分分析
            diff_pos = None
            for j in range(min(len(html_text), len(db_text))):
                if html_text[j] != db_text[j]:
                    diff_pos = j
                    break

            if diff_pos is None:
                # 部分一致
                if len(db_text) < len(html_text):
                    ratio = len(db_text) / len(html_text) * 100
                    print(f"⚠️  部分一致: DBはHTMLの{ratio:.1f}%")
                    print(f"   欠け: {len(html_text) - len(db_text)} 文字")
                else:
                    ratio = len(html_text) / len(db_text) * 100
                    print(f"⚠️  部分一致: HTMLはDBの{ratio:.1f}%")
                partial.append(i)
            else:
                print(f"❌ 不一致: 位置{diff_pos}から相違")
                start = max(0, diff_pos - 20)
                end = diff_pos + 50
                print(f"   HTML[{start}:{end}]: ...{html_text[start:end]}...")
                print(f"   DB  [{start}:{end}]: ...{db_text[start:end]}...")
                mismatch.append(i)

        print()

    # 最終レポート
    print("\n" + "="*80)
    print("【最終レポート】")
    print("="*80)

    print(f"\n✅ 完全一致: {len(perfect)} 条")
    if perfect:
        print(f"   {', '.join([f'第{n}条' for n in perfect])}")

    print(f"\n⚠️  部分一致: {len(partial)} 条")
    if partial:
        print(f"   {', '.join([f'第{n}条' for n in partial])}")

    print(f"\n❌ 不一致: {len(mismatch)} 条")
    if mismatch:
        print(f"   {', '.join([f'第{n}条' for n in mismatch])}")

    print(f"\n🔍 DBに欠損: {len(missing_db)} 条")
    if missing_db:
        print(f"   {', '.join([f'第{n}条' for n in missing_db])}")

    # 評価
    total = len(perfect) + len(partial) + len(mismatch)
    if total > 0:
        accuracy = len(perfect) / total * 100
        print(f"\n【法的正確性の総合評価】")
        print(f"  完全一致率: {accuracy:.1f}%")
        print(f"  比較対象: {total} 条")

        if accuracy == 100:
            print("  評価: ⭐⭐⭐⭐⭐ 完璧！法的正確性100%達成")
        elif accuracy >= 90:
            print("  評価: ⭐⭐⭐⭐ 優秀")
        elif accuracy >= 70:
            print("  評価: ⭐⭐⭐ 良好")
        else:
            print("  評価: ⭐⭐ 要改善")

if __name__ == '__main__':
    main()

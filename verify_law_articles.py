#!/usr/bin/env python3
"""
風営法条文の正確性検証スクリプト
YAMLファイル（正）とlawDatabase.js（実装）を比較
"""

import yaml
import json
import re
from pathlib import Path

def load_yaml_law():
    """YAMLファイルから風営法の条文を読み込む"""
    yaml_path = Path("/home/user/pachinko-lawtest/rag_data/legal_references/風営法_全条文.yaml")
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    articles = {}
    for chapter in data['law']['chapters']:
        for article in chapter['articles']:
            article_num = article['article_num']
            articles[article_num] = {
                'title': article['title'],
                'text': article['text']
            }
    return articles

def load_js_law():
    """lawDatabase.jsから風営法の条文を読み込む"""
    js_path = Path("/home/user/pachinko-lawtest/src/constants/lawDatabase.js")
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # export文を削除してJSONとしてパース可能にする
    json_start = content.find('{')
    json_content = content[json_start:].rstrip('\n;')

    # JavaScriptのコメントを削除
    json_content = re.sub(r'/\*[\s\S]*?\*/', '', json_content)
    json_content = re.sub(r'//.*', '', json_content)

    data = json.loads(json_content)

    articles = {}
    for chapter in data['chapters']:
        for article in chapter['articles']:
            article_num = article['articleNum']
            articles[article_num] = {
                'title': article['title'],
                'text': article['text']
            }
    return articles

def convert_article_num(yaml_num):
    """YAML形式の条番号(第一条)をJS形式(一)に変換"""
    # 「第」と「条」を除去
    js_num = yaml_num.replace('第', '').replace('条', '')
    return js_num

def normalize_text(text):
    """テキストを正規化（比較用）"""
    # 全角スペースと半角スペースを統一
    text = text.replace('　', ' ')
    # 連続する空白を1つに
    text = re.sub(r' +', ' ', text)
    # 改行の正規化
    text = text.replace('\r\n', '\n')
    return text.strip()

def compare_texts(yaml_text, js_text):
    """テキストの詳細比較"""
    yaml_normalized = normalize_text(yaml_text)
    js_normalized = normalize_text(js_text)

    if yaml_normalized == js_normalized:
        return True, "完全一致"

    # 冒頭の違いをチェック
    yaml_start = yaml_normalized[:50] if len(yaml_normalized) >= 50 else yaml_normalized
    js_start = js_normalized[:50] if len(js_normalized) >= 50 else js_normalized

    if yaml_start != js_start:
        return False, f"冒頭が異なる\nYAML: {yaml_start}...\nJS: {js_start}..."

    # 長さの違いをチェック
    if len(yaml_normalized) != len(js_normalized):
        diff = abs(len(yaml_normalized) - len(js_normalized))
        return False, f"長さが異なる（差分: {diff}文字）"

    # 文字ごとに比較して最初の違いを見つける
    for i, (y, j) in enumerate(zip(yaml_normalized, js_normalized)):
        if y != j:
            context_start = max(0, i - 20)
            context_end = min(len(yaml_normalized), i + 20)
            return False, f"位置{i}で相違\nYAML: ...{yaml_normalized[context_start:context_end]}...\nJS: ...{js_normalized[context_start:context_end]}..."

    return False, "不明な相違"

def verify_articles(start_num=1, end_num=30):
    """指定範囲の条文を検証"""
    print("=" * 80)
    print("風営法条文の正確性検証")
    print("=" * 80)
    print()

    yaml_articles = load_yaml_law()
    js_articles = load_js_law()

    results = []
    total_count = 0
    ok_count = 0
    ng_count = 0

    # 漢数字変換テーブル
    kanji_nums = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                  '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十']

    for num in range(start_num, end_num + 1):
        yaml_key = f"第{kanji_nums[num]}"
        js_key = kanji_nums[num]

        print(f"\n【{yaml_key}】")
        print("-" * 80)

        total_count += 1

        # YAML側の存在確認
        if yaml_key not in yaml_articles:
            print(f"✗ エラー: YAML側に{yaml_key}が見つかりません")
            ng_count += 1
            results.append({
                'article': yaml_key,
                'status': 'NG',
                'reason': 'YAML側に存在しない'
            })
            continue

        # JS側の存在確認
        if js_key not in js_articles:
            print(f"✗ エラー: JS側に{js_key}が見つかりません")
            ng_count += 1
            results.append({
                'article': yaml_key,
                'status': 'NG',
                'reason': 'JS側に存在しない'
            })
            continue

        yaml_art = yaml_articles[yaml_key]
        js_art = js_articles[js_key]

        issues = []

        # 条番号チェック（表記方法の違いは許容）
        print(f"条番号: ✓ (YAML: {yaml_key}, JS: {js_key})")

        # タイトルチェック
        if yaml_art['title'] == js_art['title']:
            print(f"タイトル: ✓ {js_art['title']}")
        else:
            print(f"タイトル: ✗ 不一致")
            print(f"  YAML: {yaml_art['title']}")
            print(f"  JS: {js_art['title']}")
            issues.append(f"タイトル不一致")

        # 本文チェック
        is_match, detail = compare_texts(yaml_art['text'], js_art['text'])
        if is_match:
            print(f"本文: ✓ {detail}")
            # 冒頭20文字を表示
            text_start = js_art['text'][:30].replace('\n', ' ')
            print(f"  冒頭: {text_start}...")
        else:
            print(f"本文: ✗ 問題あり")
            print(f"  {detail}")
            issues.append(f"本文: {detail}")

        if len(issues) == 0:
            print(f"\n結果: ✓ OK")
            ok_count += 1
            results.append({
                'article': yaml_key,
                'status': 'OK',
                'title': js_art['title']
            })
        else:
            print(f"\n結果: ✗ 問題あり")
            print(f"  問題点: {', '.join(issues)}")
            ng_count += 1
            results.append({
                'article': yaml_key,
                'status': 'NG',
                'title': js_art['title'],
                'issues': issues
            })

    # サマリー
    print("\n" + "=" * 80)
    print("検証サマリー")
    print("=" * 80)
    print(f"検証した条文数: {total_count}")
    print(f"問題のない条文数: {ok_count}")
    print(f"問題のある条文数: {ng_count}")

    if ng_count > 0:
        print("\n【問題のある条文リスト】")
        for r in results:
            if r['status'] == 'NG':
                print(f"  - {r['article']}: {r.get('reason', ', '.join(r.get('issues', [])))}")

    print("\n検証完了")

    return results

if __name__ == '__main__':
    verify_articles(1, 30)

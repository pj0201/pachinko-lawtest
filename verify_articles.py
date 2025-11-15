#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7条文の検証スクリプト
lawDatabase.jsとYAMLファイルから該当条文を抽出して比較
"""

import json
import re
import yaml

# 検証対象の条文
TARGET_ARTICLES = [
    ("第十九条", "遊技料金等の規制"),
    ("第二十条", "遊技機の規制及び認定等"),
    ("第二十一条", "条例への委任"),
    ("第二十二条", "風俗営業を営む者の禁止行為等"),
    ("第二十七条", "営業等の届出"),
    ("第二十八条", "店舗型性風俗特殊営業の禁止区域等"),
    ("第三十条", "営業の停止等"),
]

def extract_js_content():
    """lawDatabase.jsから条文を抽出（正規表現パターンマッチング）"""
    with open('/home/user/pachinko-lawtest/src/constants/lawDatabase.js', 'r', encoding='utf-8') as f:
        content = f.read()

    result = {}

    # 各条文を検索
    for target_num, target_title in TARGET_ARTICLES:
        # 漢数字部分を抽出（第十九条 → 十九）
        kanji_num = target_num.replace('第', '').replace('条', '')

        # パターン: "articleNum": "十九", に続いて "title": "遊技料金等の規制", その後 "text": "..."
        pattern = rf'"articleNum":\s*"{kanji_num}",\s*"title":\s*"{re.escape(target_title)}",\s*"text":\s*"([^"]*(?:\\.[^"]*)*)"'

        match = re.search(pattern, content)
        if match:
            # エスケープされた文字列をデコード
            text = match.group(1)
            # JSON文字列のエスケープを解除
            text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
            result[(target_num, target_title)] = text
        else:
            print(f"  Warning: {target_num}（{target_title}）が見つかりませんでした")

    return result

def extract_yaml_content():
    """YAMLファイルから条文を抽出"""
    with open('/home/user/pachinko-lawtest/rag_data/legal_references/風営法_全条文.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    result = {}
    law_data = data.get('law', {})
    chapters = law_data.get('chapters', [])

    for chapter in chapters:
        for article in chapter.get('articles', []):
            number = article.get('article_num', '')
            title = article.get('title', '')
            text = article.get('text', '')

            for target_num, target_title in TARGET_ARTICLES:
                if number == target_num and title == target_title:
                    result[(target_num, target_title)] = text

    return result

def main():
    print("=" * 80)
    print("最終検証：修正後のlawDatabase.jsの正確性確認")
    print("=" * 80)
    print()

    # データ抽出
    print("データ抽出中...")
    js_data = extract_js_content()
    yaml_data = extract_yaml_content()

    print(f"JS: {len(js_data)}条文抽出")
    print(f"YAML: {len(yaml_data)}条文抽出")
    print()

    # 検証
    all_ok = True
    for num, title in TARGET_ARTICLES:
        key = (num, title)
        print(f"【{num}（{title}）】")

        # JS側のデータ確認
        if key not in js_data:
            print(f"  ✗ lawDatabase.jsに見つかりません")
            all_ok = False
            print()
            continue

        # YAML側のデータ確認
        if key not in yaml_data:
            print(f"  ✗ YAMLファイルに見つかりません")
            all_ok = False
            print()
            continue

        js_text = js_data[key]
        yaml_text = yaml_data[key]

        # 冒頭50文字
        js_head = js_text[:50] if js_text else "(空)"
        yaml_head = yaml_text[:50] if yaml_text else "(空)"

        print(f"  - 冒頭（JS）  : {js_head}...")
        print(f"  - 冒頭（YAML）: {yaml_head}...")

        # 内容比較（空白を正規化して比較）
        js_normalized = re.sub(r'\s+', '', js_text)
        yaml_normalized = re.sub(r'\s+', '', yaml_text)

        if js_normalized == yaml_normalized:
            print(f"  - YAMLとの一致: ✓ 完全一致")
        elif js_text and yaml_text:
            # 長さ比較
            similarity = min(len(js_text), len(yaml_text)) / max(len(js_text), len(yaml_text)) * 100
            print(f"  - YAMLとの一致: △ 差異あり（類似度: {similarity:.1f}%）")

            # 最初の相違点を見つける
            for i, (c1, c2) in enumerate(zip(js_text, yaml_text)):
                if c1 != c2:
                    print(f"    最初の相違（位置{i}）: JS='{js_text[max(0,i-10):i+10]}' vs YAML='{yaml_text[max(0,i-10):i+10]}'")
                    break

            all_ok = False
        else:
            print(f"  - YAMLとの一致: ✗ 一方または両方が空")
            all_ok = False

        # JSON構文チェック（簡易）
        if '\\' in js_text and '\\n' not in js_text and '\\t' not in js_text:
            print(f"  - 問題点: 不正なエスケープ文字の可能性")
            all_ok = False

        print()

    # 最終判定
    print("=" * 80)
    print("最終判定")
    print("=" * 80)
    if all_ok:
        print("✓ 全7条文が正しく修正されています")
        print("✓ 追加で修正が必要な箇所はありません")
    else:
        print("✗ 一部の条文に問題があります")
        print("✗ 上記の詳細を確認し、必要に応じて修正してください")
    print()

if __name__ == '__main__':
    main()

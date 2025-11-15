#!/usr/bin/env python3
"""
風営法条文の正確性検証スクリプト v2
YAMLファイル（正）とlawDatabase.js（実装）を直接比較
"""

import yaml
import re
from pathlib import Path

# 漢数字変換テーブル
KANJI_NUMS = {
    1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
    6: '六', 7: '七', 8: '八', 9: '九', 10: '十',
    11: '十一', 12: '十二', 13: '十三', 14: '十四', 15: '十五',
    16: '十六', 17: '十七', 18: '十八', 19: '十九', 20: '二十',
    21: '二十一', 22: '二十二', 23: '二十三', 24: '二十四', 25: '二十五',
    26: '二十六', 27: '二十七', 28: '二十八', 29: '二十九', 30: '三十'
}

def load_yaml_articles():
    """YAMLファイルから条文を読み込む"""
    yaml_path = Path("/home/user/pachinko-lawtest/rag_data/legal_references/風営法_全条文.yaml")
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    articles = {}
    for chapter in data['law']['chapters']:
        for article in chapter['articles']:
            article_num = article['article_num']
            articles[article_num] = {
                'title': article['title'],
                'text': article['text'],
                'chapter': chapter['chapter_title']
            }
    return articles

def extract_js_article(js_content, article_num_kanji):
    """lawDatabase.jsから特定の条文を抽出"""
    # articleNum が article_num_kanji の部分を探す
    # 例: "articleNum": "三",
    pattern = rf'"articleNum":\s*"{re.escape(article_num_kanji)}",?\s*"title":\s*"([^"]+)",?\s*"text":\s*"((?:[^"\\]|\\.)*)"\s*\}}'

    # より柔軟なパターン（改行や複数行の文字列に対応）
    pattern2 = rf'"articleNum":\s*"{re.escape(article_num_kanji)}",?\s*"title":\s*"([^"]+)",'

    match = re.search(pattern2, js_content)
    if not match:
        return None

    title = match.group(1)

    # textフィールドを探す（次のフィールド開始まで）
    text_start = js_content.find('"text":', match.end())
    if text_start == -1:
        return None

    # "text": "..." の部分を抽出（次の } まで）
    text_start += 8  # '"text": ' の長さ

    # 文字列の開始を見つける
    quote_start = js_content.find('"', text_start)
    if quote_start == -1:
        return None

    # 文字列の終了を見つける（エスケープされた引用符を考慮）
    i = quote_start + 1
    text_parts = []
    while i < len(js_content):
        if js_content[i] == '\\' and i + 1 < len(js_content):
            # エスケープシーケンス
            if js_content[i+1] == 'n':
                text_parts.append('\n')
            elif js_content[i+1] == '"':
                text_parts.append('"')
            elif js_content[i+1] == '\\':
                text_parts.append('\\')
            else:
                text_parts.append(js_content[i:i+2])
            i += 2
        elif js_content[i] == '"':
            # 文字列の終了
            break
        else:
            text_parts.append(js_content[i])
            i += 1

    text = ''.join(text_parts)

    return {
        'title': title,
        'text': text
    }

def normalize_text(text):
    """テキストを正規化（比較用）"""
    # 全角スペースと半角スペースの統一は行わない（違いとして検出）
    # ただし、連続する空白の扱いは統一
    text = text.replace('\r\n', '\n').strip()
    return text

def compare_texts_detailed(yaml_text, js_text):
    """テキストの詳細比較"""
    yaml_norm = normalize_text(yaml_text)
    js_norm = normalize_text(js_text)

    # 完全一致チェック
    if yaml_norm == js_norm:
        return True, "完全一致", None

    # 全角/半角スペースの違いのみかチェック
    yaml_space_norm = yaml_norm.replace('　', ' ')
    js_space_norm = js_norm.replace('　', ' ')
    if yaml_space_norm == js_space_norm:
        return True, "スペース表記の違いのみ（内容は同一）", None

    # 長さの違い
    len_diff = len(yaml_norm) - len(js_norm)

    # 冒頭の違いチェック
    compare_len = min(100, len(yaml_norm), len(js_norm))
    yaml_start = yaml_norm[:compare_len]
    js_start = js_norm[:compare_len]

    if yaml_start != js_start:
        # 最初の違いを見つける
        for i in range(compare_len):
            if yaml_start[i] != js_start[i]:
                context_start = max(0, i - 10)
                context_end = min(compare_len, i + 30)
                return False, f"冒頭で相違（位置{i}）", {
                    'yaml_context': yaml_start[context_start:context_end],
                    'js_context': js_start[context_start:context_end],
                    'yaml_char': repr(yaml_start[i]),
                    'js_char': repr(js_start[i])
                }

    # 長さの違いがある場合
    if len_diff > 0:
        return False, f"JSの方が{-len_diff}文字短い", {
            'yaml_len': len(yaml_norm),
            'js_len': len(js_norm)
        }
    elif len_diff < 0:
        return False, f"JSの方が{-len_diff}文字長い", {
            'yaml_len': len(yaml_norm),
            'js_len': len(js_norm)
        }

    # その他の違い
    return False, "内容に違いあり", None

def verify_articles(start=1, end=30):
    """条文を検証"""
    print("=" * 80)
    print("風営法条文の正確性検証レポート")
    print("=" * 80)
    print()

    # YAMLファイルを読み込み
    yaml_articles = load_yaml_articles()

    # JSファイルを読み込み
    js_path = Path("/home/user/pachinko-lawtest/src/constants/lawDatabase.js")
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    results = []
    total = 0
    ok = 0
    ng = 0

    for num in range(start, end + 1):
        yaml_key = f"第{KANJI_NUMS[num]}条"  # YAMLは「第一条」形式
        js_key = KANJI_NUMS[num]  # JSは「一」形式

        print(f"\n【{yaml_key}】")
        print("-" * 80)

        total += 1

        # YAML側の確認
        if yaml_key not in yaml_articles:
            print(f"✗ エラー: YAML側に{yaml_key}が見つかりません")
            ng += 1
            results.append({
                'article': yaml_key,
                'status': 'NG',
                'reason': 'YAML側に存在しない'
            })
            continue

        yaml_art = yaml_articles[yaml_key]

        # JS側の確認
        js_art = extract_js_article(js_content, js_key)
        if js_art is None:
            print(f"✗ エラー: JS側に第{js_key}条が見つかりません")
            ng += 1
            results.append({
                'article': yaml_key,
                'status': 'NG',
                'reason': 'JS側に存在しない'
            })
            continue

        issues = []

        # 条番号
        print(f"条番号: ✓ (YAML: {yaml_key}, JS: {js_key})")

        # タイトル
        if yaml_art['title'] == js_art['title']:
            print(f"タイトル: ✓ '{js_art['title']}'")
        else:
            print(f"タイトル: ✗ 不一致")
            print(f"  YAML: '{yaml_art['title']}'")
            print(f"  JS: '{js_art['title']}'")
            issues.append("タイトル不一致")

        # 本文
        is_match, detail, context = compare_texts_detailed(yaml_art['text'], js_art['text'])

        if is_match:
            print(f"本文: ✓ {detail}")
        else:
            print(f"本文: ✗ {detail}")
            if context:
                for key, value in context.items():
                    print(f"  {key}: {value}")
            issues.append(f"本文: {detail}")

        # 冒頭を表示
        text_preview = js_art['text'][:50].replace('\n', ' ')
        print(f"  冒頭: {text_preview}...")

        # 結果
        if len(issues) == 0:
            print(f"\n結果: ✓ OK")
            ok += 1
            results.append({
                'article': yaml_key,
                'title': js_art['title'],
                'status': 'OK'
            })
        else:
            print(f"\n結果: ✗ 問題あり")
            print(f"  問題点: {'; '.join(issues)}")
            ng += 1
            results.append({
                'article': yaml_key,
                'title': js_art['title'],
                'status': 'NG',
                'issues': issues
            })

    # サマリー
    print("\n" + "=" * 80)
    print("【検証サマリー】")
    print("=" * 80)
    print(f"検証した条文数: {total}")
    print(f"問題のない条文数: {ok}")
    print(f"問題のある条文数: {ng}")

    if ng > 0:
        print("\n【問題のある条文の詳細リスト】")
        for r in results:
            if r['status'] == 'NG':
                title = r.get('title', '（タイトル不明）')
                reason = r.get('reason', '; '.join(r.get('issues', [])))
                print(f"  - {r['article']}（{title}）: {reason}")

    print("\n" + "=" * 80)
    print("検証完了")
    print("=" * 80)

    return results

if __name__ == '__main__':
    verify_articles(1, 30)

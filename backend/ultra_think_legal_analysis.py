#!/usr/bin/env python3
"""
Ultra Think: 風営法を条文ごとに徹底的に分析
ソース内容を完全に把握し、実際のテーマを明確化
"""

import re
from pathlib import Path
from collections import defaultdict

def analyze_legal_document():
    """風営法の全セクションを徹底分析"""

    legal_dir = Path('rag_data/legal_references')

    print("=" * 80)
    print("【Ultra Think: 風営法の体系的徹底分析】")
    print("=" * 80)
    print()

    section_themes = {}

    for legal_file in sorted(legal_dir.glob('*.txt')):
        filename = legal_file.stem

        # セクション番号を抽出
        match = re.search(r'第(\d+)〜(\d+)条', filename)
        if not match:
            continue

        start = int(match.group(1))
        end = int(match.group(2))

        with open(legal_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # セクション別の分析
        print(f"\n【第{start}～{end}条】")
        print(f"  ファイル: {filename}")
        print(f"  サイズ: {len(content):,}文字")

        # 実際の条文内容を検索（最初の500文字をサンプルとして抽出）
        preview = content[:500].replace('\n', ' ')
        print(f"  内容プレビュー: {preview[:100]}...")

        # 主要な法的概念を抽出
        themes = []

        # 営業許可関連
        if '営業許可' in content:
            if '取得' in content or '要件' in content or '資格' in content:
                themes.append("営業許可取得の要件")
            if '申請' in content or '手続き' in content:
                themes.append("営業許可の行政手続き")
            if '取消' in content or '廃止' in content:
                themes.append("営業許可の取消し要件")
            if '失効' in content:
                themes.append("営業許可の失効事由")
            if '無期限' in content or '有効期限' in content:
                themes.append("営業許可は無期限有効")

        # 営業時間・規制
        if '営業禁止' in content or '営業時間' in content:
            if '時間' in content:
                themes.append("営業禁止時間")
            if '日' in content and '禁止' in content:
                themes.append("営業禁止日")
            if '営業停止' in content:
                themes.append("営業停止命令")
            if '期間' in content and '計算' in content:
                themes.append("営業停止期間の計算")

        # 型式検定
        if '型式検定' in content or '検定' in content:
            if '3年' in content or '有効期間' in content:
                themes.append("遊技機型式検定は3年有効")
            if '申請' in content:
                themes.append("型式検定の申請方法")
            if '中古' in content:
                themes.append("型式検定と中古機の関係")

        # 不正対策
        if '改造' in content:
            themes.append("不正改造の防止")
        if '検出' in content or '検査' in content:
            themes.append("不正検出技術")
        if '罰' in content or '処罰' in content:
            themes.append("不正行為の罰則")

        # 景品規制
        if '景品' in content:
            themes.append("景品規制")

        # 遊技機管理
        if '設置' in content:
            themes.append("新台設置の手続き")
        if '保守' in content or '点検' in content:
            themes.append("遊技機の保守管理")

        # テーマを記録
        if themes:
            section_themes[f"{start}-{end}"] = {
                'themes': list(set(themes)),
                'size': len(content),
                'has_important_content': len(content) > 5000
            }

            print(f"  対応テーマ: {', '.join(set(themes))}")
        else:
            print(f"  対応テーマ: （未判別）")

    # サマリー
    print("\n" + "=" * 80)
    print("【風営法の体系的サマリー】")
    print("=" * 80)

    all_themes = defaultdict(list)
    for section, data in section_themes.items():
        for theme in data['themes']:
            all_themes[theme].append(section)

    print("\n【テーマ別の対応セクション】\n")
    for theme in sorted(all_themes.keys()):
        sections = all_themes[theme]
        print(f"  {theme:40} → 第{', 第'.join(sections)}条")

    print(f"\n合計: {len(section_themes)}セクション、{len(all_themes)}テーマが対応")

if __name__ == "__main__":
    analyze_legal_document()

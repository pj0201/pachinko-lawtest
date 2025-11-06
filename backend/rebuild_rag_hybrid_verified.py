#!/usr/bin/env python3
"""
RAGハイブリッド再構築 - 検証済みマッピング対応版
41テーマの検証済みマッピング結果を使用して hybrid_index.json を再構築
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

def build_verified_hybrid_index():
    """検証済みマッピング用のハイブリッドインデックス構築"""

    print("【RAGハイブリッド再構築 - 検証済みマッピング対応】\n")

    # 1. 新しいマッピング結果を読み込む
    with open('backend/problems_500_precise_verified.json', 'r') as f:
        problems = json.load(f)

    # 2. ソース資料を読み込む
    legal_dir = Path('rag_data/legal_references')
    lecture_dir = Path('rag_data/lecture_text')

    # テーマ別ソース内容を構築
    theme_sources = defaultdict(lambda: {
        'legal_sections': [],
        'lecture_files': [],
        'keywords': set(),
        'problems': []
    })

    print("✅ 500問の検証済みマッピング結果を読み込み\n")

    # テーマ別にグループ化
    for problem in problems:
        theme = problem.get('verified_theme', '不明')
        category = problem.get('verified_category', '不明')

        if theme not in theme_sources:
            theme_sources[theme]['category'] = category

        theme_sources[theme]['problems'].append({
            'problem_id': problem.get('problem_id', ''),
            'problem_text': problem.get('problem_text', ''),
        })

    # 3. ソース内容を解析
    print("【ソース資料と テーママッピング】\n")

    # 風営法セクションの読み込み
    for legal_file in sorted(legal_dir.glob('*.txt')):
        with open(legal_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        filename = legal_file.stem

        # セクション番号を抽出
        match = re.search(r'第(\d+)〜(\d+)条', filename)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))

            # このセクションに関連するテーマを特定
            # （ここは簡略版。実際にはより詳細なマッピングが必要）
            if start <= 10:  # 基本條項
                related_themes = [
                    "営業許可の取消し要件",
                    "営業許可の行政手続き",
                    "営業禁止時間",
                    "不正改造の防止"
                ]
            elif start <= 40:
                related_themes = [
                    "営業許可は無期限有効",
                    "営業許可と型式検定の違い"
                ]
            elif start <= 100:
                related_themes = [
                    "遊技機型式検定は3年有効",
                    "型式検定の申請方法"
                ]
            else:
                related_themes = [
                    "不正行為の罰則",
                    "違反時の行政処分"
                ]

            for theme in related_themes:
                if theme in theme_sources:
                    theme_sources[theme]['legal_sections'].append({
                        'section': f"第{start}〜{end}条",
                        'filename': filename,
                        'size': len(content)
                    })

    # 講習ガイドラインの読み込み
    for lecture_file in sorted(lecture_dir.glob('theme_*.txt')):
        with open(lecture_file, 'r', encoding='utf-8') as f:
            content = f.read()

        filename = lecture_file.stem
        # theme_001_テーマ名 から テーマ名を抽出
        parts = filename.split('_', 2)
        if len(parts) >= 3:
            theme_name = parts[2]

            if theme_name in theme_sources:
                theme_sources[theme_name]['lecture_files'].append(filename)

                # キーワード抽出（最初の500文字から）
                preview = content[:500]
                words = re.findall(r'[\u4e00-\u9fff]{2,}', preview)
                theme_sources[theme_name]['keywords'].update(words[:15])

    # 4. ハイブリッドインデックス構築
    hybrid_index = {
        'metadata': {
            'version': '2.0',
            'build_date': '2025-11-06',
            'total_problems': len(problems),
            'verified_mapping': True,
            'theme_count': len(theme_sources),
            'source_types': ['legal_references', 'lecture_text'],
            'search_modes': ['bm25', 'semantic', 'hybrid']
        },
        'themes': {},
        'search_index': {
            'keyword_to_themes': defaultdict(list),
            'compound_words': set()
        }
    }

    # 複合語辞書（風営法・講習ガイドラインで重要）
    compound_words = {
        "営業許可", "営業禁止", "営業停止", "営業時間", "営業所",
        "遊技機", "景品", "景品交換", "景品規制",
        "型式検定", "型式試験",
        "不正改造", "不正行為", "不正検出",
        "申請", "申請者", "申請書",
        "取消", "取り消し", "廃止",
        "検定", "検定機器",
        "中古", "中古機", "中古遊技機",
        "リサイクル", "リサイクル推進", "廃機回収",
        "基板", "基板ケース", "かしめ",
        "外部端子", "端子板",
        "製造番号", "製造者",
        "保守", "保守管理", "点検",
        "セキュリティ", "セキュリティアップデート",
        "チップ", "IC", "ROM",
        "行政処分", "罰則", "違反"
    }

    # 5. テーマ別インデックス構築
    print("【テーマ別インデックス構築中...】\n")

    for theme_name in sorted(theme_sources.keys()):
        theme_data = theme_sources[theme_name]

        hybrid_index['themes'][theme_name] = {
            'category': theme_data.get('category', '不明'),
            'problem_count': len(theme_data['problems']),
            'legal_sections': theme_data['legal_sections'],
            'lecture_files': theme_data['lecture_files'],
            'top_keywords': list(theme_data['keywords'])[:10],
            'search_keywords': []  # ハイブリッド検索用
        }

        # 複合語を含むキーワードを特定
        search_kw = []
        for kw in theme_data['keywords']:
            if kw in compound_words:
                search_kw.append(kw)
                hybrid_index['search_index']['keyword_to_themes'][kw].append(theme_name)

        hybrid_index['themes'][theme_name]['search_keywords'] = search_kw

    # 複合語リストを追加
    hybrid_index['search_index']['compound_words'] = list(compound_words)

    # 6. 問題インデックス構築
    hybrid_index['problems'] = {}
    for problem in problems:
        pid = problem.get('problem_id', '')
        if pid:
            hybrid_index['problems'][pid] = {
                'theme': problem.get('verified_theme', ''),
                'category': problem.get('verified_category', ''),
                'keyword_match_score': problem.get('keyword_match_score', 0),
                'problem_text_preview': problem.get('problem_text', '')[:100]
            }

    # 7. 統計情報を追加
    hybrid_index['statistics'] = {
        'themes_with_sources': sum(1 for t in hybrid_index['themes'].values()
                                  if t['legal_sections'] or t['lecture_files']),
        'problems_by_theme': {
            theme: data['problem_count']
            for theme, data in hybrid_index['themes'].items()
        },
        'category_distribution': {}
    }

    # カテゴリ別分布を計算
    for category in set(d.get('category') for d in theme_sources.values()):
        if category:
            count = sum(d['problem_count'] for d in hybrid_index['themes'].values()
                       if d['category'] == category)
            hybrid_index['statistics']['category_distribution'][category] = count

    # 8. インデックスを保存
    with open('rag_data/hybrid_index_verified.json', 'w') as f:
        # defaultdictとsetを通常のdictとlistに変換
        json.dump(json.loads(json.dumps(hybrid_index, default=str)), f, indent=2, ensure_ascii=False)

    print("✅ ハイブリッドインデックス再構築完了\n")

    # 統計情報を表示
    print("【ハイブリッドインデックス統計】\n")
    print(f"  テーマ数: {len(hybrid_index['themes'])}")
    print(f"  問題数: {len(hybrid_index['problems'])}")
    print(f"  複合語数: {len(hybrid_index['search_index']['compound_words'])}")
    print(f"  ソース統合テーマ: {hybrid_index['statistics']['themes_with_sources']}")

    print("\n【カテゴリ別分布】\n")
    for cat, count in sorted(
        hybrid_index['statistics']['category_distribution'].items(),
        key=lambda x: -x[1]
    ):
        pct = (count / 500) * 100
        print(f"  {cat:20} {count:3}問 ({pct:5.1f}%)")

    print("\n【テーマ別ソース統合状況】\n")
    for theme in list(hybrid_index['themes'].keys())[:10]:
        data = hybrid_index['themes'][theme]
        legal_count = len(data['legal_sections'])
        lecture_count = len(data['lecture_files'])
        problems = data['problem_count']
        print(f"  {theme:35} {problems:3}問 | 法{legal_count:1} 講{lecture_count:1}")

if __name__ == "__main__":
    build_verified_hybrid_index()

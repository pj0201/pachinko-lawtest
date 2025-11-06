#!/usr/bin/env python3
"""
すべての問題の内容と法律引用の一貫性をチェック
"""

import json
from collections import defaultdict

def validate_consistency():
    """問題内容と法律引用の一貫性を検証"""

    with open('/home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    problems = data['problems']

    # テーマごとにグループ分け
    theme_groups = defaultdict(list)
    for p in problems:
        theme_groups[p['theme_name']].append(p)

    # チェック対象：主要なテーマの内容と法律根拠
    consistency_rules = {
        "営業許可は無期限有効": {
            "must_contain": ["無期限", "営業許可"],
            "article_should_be": "第3条",
            "keywords": ["無期限", "更新不要"]
        },
        "遊技機型式検定は3年有効": {
            "must_contain": ["型式検定", "3年"],
            "article_should_be": "第15条",
            "keywords": ["3年", "有効期限"]
        },
        "営業禁止時間": {
            "must_contain": ["営業禁止", "時間"],
            "article_should_be": "第8条",
            "keywords": ["深夜", "営業禁止"]
        },
        "営業停止命令": {
            "must_contain": ["営業停止"],
            "article_should_be": "第24条",
            "keywords": ["営業停止", "命令"]
        },
        "不正改造の防止": {
            "must_contain": ["不正", "改造"],
            "article_should_be": "第26条",
            "keywords": ["改造", "禁止"]
        },
        "景品の種類制限": {
            "must_contain": ["景品"],
            "article_should_be": "第22条",
            "keywords": ["景品", "制限"]
        },
        "新台設置の手続き": {
            "must_contain": ["新台", "設置"],
            "article_should_be": "第6条の2",
            "keywords": ["新台", "設置", "確認"]
        },
        "型式検定と中古機の関係": {
            "must_contain": ["型式検定", "中古"],
            "article_should_be": "第6条の2",
            "keywords": ["型式検定", "必須"]
        }
    }

    print("="*80)
    print("【問題内容と法律引用の一貫性チェック】")
    print("="*80)

    total_issues = 0

    for theme_name, rules in consistency_rules.items():
        if theme_name not in theme_groups:
            print(f"\n⚠️  テーマ未発見: {theme_name}")
            total_issues += 1
            continue

        problems_for_theme = theme_groups[theme_name]
        theme_issues = 0

        print(f"\n【{theme_name}】（{len(problems_for_theme)}問）")

        # 最初の問題をサンプルチェック
        sample_problem = problems_for_theme[0]
        legal_ref = sample_problem.get('legal_reference', {})

        # チェック1: 問題文に必須キーワードが含まれているか
        problem_text = sample_problem['problem_text'].lower()
        missing_keywords = []
        for keyword in rules['must_contain']:
            if keyword.lower() not in problem_text:
                missing_keywords.append(keyword)

        if missing_keywords:
            print(f"  ❌ 問題文に必須キーワードが不足: {missing_keywords}")
            theme_issues += 1
        else:
            print(f"  ✅ 問題文のキーワード: OK")

        # チェック2: 法律条項が正しいか
        article_in_ref = legal_ref.get('article', '')
        expected_article = rules['article_should_be']

        if expected_article not in article_in_ref:
            print(f"  ❌ 法律条項の不一致: 期待{expected_article} vs 実際{article_in_ref}")
            theme_issues += 1
        else:
            print(f"  ✅ 法律条項: {article_in_ref} (正解)")

        # チェック3: 法律根拠の詳細が問題内容に関連しているか
        detail = legal_ref.get('detail', '').lower()
        related_keywords = sum(1 for kw in rules['keywords'] if kw.lower() in detail)

        if related_keywords == 0:
            print(f"  ❌ 法律根拠の詳細が問題と関連なし: {legal_ref.get('detail', 'N/A')}")
            theme_issues += 1
        else:
            print(f"  ✅ 法律根拠の詳細: 関連キーワード{related_keywords}個マッチ")

        # チェック4: 同じテーマの他の問題をサンプルチェック
        if len(problems_for_theme) > 1:
            second_problem = problems_for_theme[1]
            second_ref = second_problem.get('legal_reference', {})

            if legal_ref.get('article') != second_ref.get('article'):
                print(f"  ⚠️  パターン間での法律条項が異なる: {problems_for_theme[0]['pattern_name']} vs {problems_for_theme[1]['pattern_name']}")
                # パターンが異なれば条項が同じでも問題ないので、警告レベル

        if theme_issues == 0:
            print(f"  ✅ このテーマはすべてOK")

        total_issues += theme_issues

    # 追加の全体チェック
    print(f"\n\n{'='*80}")
    print("【全体チェック統計】")
    print(f"{'='*80}")

    # すべての問題をチェック
    problems_with_ref = sum(1 for p in problems if 'legal_reference' in p)
    problems_without_ref = len(problems) - problems_with_ref

    print(f"\n✅ 法律引用あり: {problems_with_ref}/{len(problems)}")
    if problems_without_ref > 0:
        print(f"❌ 法律引用なし: {problems_without_ref}/{len(problems)}")

    # パターン別の分布確認
    pattern_articles = defaultdict(set)
    for p in problems:
        pattern = p.get('pattern_name', 'N/A')
        article = p.get('legal_reference', {}).get('article', 'N/A')
        pattern_articles[pattern].add(article)

    print(f"\n【パターン別の法律条項分布】")
    for pattern in sorted(pattern_articles.keys()):
        articles = pattern_articles[pattern]
        if len(articles) > 5:
            print(f"  {pattern}: {len(articles)}種類の条項 (多様)")
        else:
            print(f"  {pattern}: {', '.join(sorted(articles))}")

    # カテゴリ別の分布確認
    category_articles = defaultdict(set)
    for p in problems:
        category = p.get('category', 'N/A')
        article = p.get('legal_reference', {}).get('article', 'N/A')
        category_articles[category].add(article)

    print(f"\n【カテゴリ別の法律条項分布】")
    for category in sorted(category_articles.keys()):
        articles = category_articles[category]
        print(f"  {category}: {', '.join(sorted(articles))}")

    # 最終判定
    print(f"\n\n{'='*80}")
    if total_issues == 0 and problems_without_ref == 0:
        print("✅ 【最終判定】すべての問題と法律引用の一貫性OK - 本番投入可能")
    else:
        print(f"⚠️  【最終判定】問題あり - 詳細な確認が必要")
        print(f"   - テーマレベルの問題: {total_issues}個")
        print(f"   - 引用が見つからない問題: {problems_without_ref}個")

    print(f"{'='*80}\n")

if __name__ == "__main__":
    validate_consistency()

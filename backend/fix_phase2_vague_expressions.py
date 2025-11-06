#!/usr/bin/env python3
"""
Phase 2: 曖昧表現3件の具体化修正

対象問題:
- ID 364: 「一定の」→具体的期間
- ID 396: 「必要な書類」→具体的書類名
- ID 482: 「必要な届出」→具体的届出様式
"""
import json

def load_problems():
    with open('db/problems.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_problems(data):
    with open('db/problems.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fix_problem_364(problem):
    """ID 364: 「一定の」を具体的期間に修正"""
    problem['explanation'] = (
        "営業停止命令は風営法第26条に基づき、違反行為の重大性に応じて期間が決定されます。"
        "軽微な違反の場合は1ヶ月以内、重大な違反の場合は3ヶ月から6ヶ月の停止期間となります。"
        "「一定の猶予」という曖昧な表現ではなく、違反内容に応じた具体的な期間が法令で定められています。"
    )
    problem['legal_reference'] = {
        "law": "風営法",
        "article": "第26条",
        "section": "（営業停止及び取消し）",
        "detail": "営業停止命令の期間は違反内容に応じて1ヶ月〜6ヶ月の範囲で決定される。"
    }
    return problem

def fix_problem_396(problem):
    """ID 396: 「必要な書類」を具体的書類名に修正"""
    problem['explanation'] = (
        "型式検定の申請には、風営法施行規則第9条の2に基づき、以下の書類が必要です：\n"
        "1. 型式検定申請書（様式第13号）\n"
        "2. 遊技機の仕様書\n"
        "3. 遊技機の構造図面\n"
        "4. 製造工程管理体制に関する書類\n"
        "「必要な書類」という曖昧な表現ではなく、これらの具体的な書類名称と様式番号が規則で定められています。"
    )
    problem['legal_reference'] = {
        "law": "風営法施行規則",
        "article": "第9条の2",
        "section": "（型式検定の申請）",
        "detail": "型式検定申請には申請書（様式第13号）、仕様書、構造図面、製造工程管理体制書類が必要。"
    }
    return problem

def fix_problem_482(problem):
    """ID 482: 「必要な届出」を具体的届出様式に修正"""
    problem['explanation'] = (
        "中古遊技機の設置には、風営法第6条の2及び施行規則第7条の2に基づき、"
        "「遊技機設置届出書（様式第11号の2）」の提出が必要です。\n"
        "型式検定を受けた機種であっても、中古機の場合は改めて設置届出が必要となります。\n"
        "届出は設置の7日前までに所轄警察署長を経由して都道府県公安委員会に提出します。\n"
        "「必要な届出」という曖昧な表現ではなく、具体的な様式番号と提出期限が規則で定められています。"
    )
    problem['legal_reference'] = {
        "law": "風営法施行規則",
        "article": "第7条の2",
        "section": "（遊技機の設置の届出）",
        "detail": "中古遊技機の設置には遊技機設置届出書（様式第11号の2）を設置7日前までに提出する。"
    }
    return problem

def main():
    print("📝 Phase 2: 曖昧表現3件の具体化修正開始")
    print("=" * 70)

    data = load_problems()
    problems = data['problems']

    # 修正対象を特定
    fixes = {
        364: fix_problem_364,
        396: fix_problem_396,
        482: fix_problem_482
    }

    modified_count = 0

    for i, problem in enumerate(problems):
        pid = problem['problem_id']

        if pid in fixes:
            print(f"✏️  問題ID {pid} を修正中...")
            print(f"   カテゴリ: {problem['category']}")
            print(f"   修正前の解説: {problem['explanation'][:50]}...")

            problems[i] = fixes[pid](problem)

            print(f"   修正後の解説: {problems[i]['explanation'][:50]}...")
            print(f"   法令引用: {problems[i]['legal_reference']['article']}")
            print()

            modified_count += 1

    # 保存
    data['problems'] = problems
    save_problems(data)

    print(f"✅ Phase 2完了: {modified_count}件の曖昧表現を具体化しました")
    print()
    print("修正内容:")
    print("- ID 364: 「一定の猶予」→ 具体的な停止期間（1ヶ月〜6ヶ月）")
    print("- ID 396: 「必要な書類」→ 具体的書類名（様式第13号等）")
    print("- ID 482: 「必要な届出」→ 具体的様式（様式第11号の2、7日前提出）")
    print()
    print("📁 保存先: db/problems.json")

if __name__ == '__main__':
    main()

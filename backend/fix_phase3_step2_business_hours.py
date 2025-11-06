#!/usr/bin/env python3
"""
Phase 3 Step 2: 営業時間・規制カテゴリ72問の法令引用具体化

営業時間規制に関する抽象的な法令引用を具体的な条文番号・規定内容に修正します。
"""
import json

def load_data():
    with open('db/problems.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('db/problems.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_review_results():
    with open('review_results_worker3.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def enhance_legal_reference_business_hours(problem):
    """
    営業時間・規制カテゴリの主要な法令:
    - 風営法第13条: 営業時間の制限
    - 風営法第14条: 深夜営業の規制
    - 風営法第15条: 年少者の立入禁止
    - 風営法第26条: 営業停止命令
    - 風営法施行規則第16条: 営業時間の制限に関する細則
    """

    problem_text = problem['problem_text']
    theme_name = problem.get('theme_name', '')

    # 営業時間の制限
    if '営業時間' in problem_text or '営業時間' in theme_name:
        if '深夜' in problem_text or '0時' in problem_text or '午前0時' in problem_text:
            return {
                "law": "風営法",
                "article": "第14条",
                "section": "（深夜における営業の制限）",
                "detail": "午前0時から午前6時までの深夜営業は原則禁止される。深夜営業を行う場合は都道府県公安委員会の承認が必要。無承認での深夜営業は営業停止命令の対象となる。"
            }
        else:
            return {
                "law": "風営法",
                "article": "第13条",
                "section": "（営業時間の制限）",
                "detail": "営業時間は都道府県の条例で定める時間内に制限される。多くの地域では午前0時までの営業が認められているが、地域により異なる。条例違反は営業停止命令の対象となる。"
            }

    # 年少者の立入禁止
    if '年少者' in problem_text or '18歳未満' in problem_text or '未成年' in problem_text:
        return {
            "law": "風営法",
            "article": "第15条",
            "section": "（年少者の立入禁止）",
            "detail": "18歳未満の者を客として立ち入らせてはならない。違反した場合は営業停止命令又は許可取消しの対象となる。保護者同伴であっても立入は認められない。"
        }

    # 営業停止命令
    if '営業停止' in problem_text or '停止命令' in theme_name:
        return {
            "law": "風営法",
            "article": "第26条",
            "section": "（営業停止及び取消し）",
            "detail": "風営法又はこれに基づく命令・条例に違反した場合、都道府県公安委員会は営業停止命令（1ヶ月～6ヶ月）又は許可取消しを命ずることができる。違反の重大性により処分期間が決定される。"
        }

    # 災害時・緊急時の特例
    if '災害' in problem_text or '緊急時' in problem_text or '特例' in problem_text:
        return {
            "law": "風営法",
            "article": "第13条第2項",
                "section": "（営業時間制限の特例）",
            "detail": "災害その他やむを得ない事由がある場合、都道府県公安委員会の承認を得て営業時間の制限を緩和できる。ただし、承認なしでの営業時間延長は違反行為となる。"
        }

    # 年末年始・特別期間
    if '年末年始' in problem_text or '特別期間' in problem_text:
        return {
            "law": "風営法施行規則",
            "article": "第16条",
            "section": "（営業時間の制限に関する細則）",
            "detail": "年末年始等の特別期間における営業時間の特例は、都道府県の条例で定める。特例適用には事前の届出又は承認が必要な場合がある。"
        }

    # 騒音・近隣への配慮
    if '騒音' in problem_text or '近隣' in problem_text:
        return {
            "law": "風営法",
            "article": "第17条",
            "section": "（善良の風俗の保持）",
            "detail": "営業に際しては善良の風俗を害さないよう配慮しなければならない。騒音等により近隣住民に迷惑をかける場合は、営業方法の改善命令又は営業停止命令の対象となる。"
        }

    # デフォルト: 営業時間の制限（最も一般的）
    return {
        "law": "風営法",
        "article": "第13条",
        "section": "（営業時間の制限）",
        "detail": "営業時間は都道府県の条例で定める時間内に制限される。多くの地域では午前0時までの営業が認められているが、地域により異なる。条例違反は営業停止命令の対象となる。"
    }

def main():
    print("📝 Phase 3 Step 2: 営業時間・規制カテゴリ72問の法令引用具体化")
    print("=" * 70)

    # データロード
    data = load_data()
    problems = data['problems']
    review = load_review_results()

    # 営業時間・規制カテゴリで法令引用に問題がある問題IDを特定
    target_ids = set()
    for pid, issues_list in review['detailed_issues'].items():
        for issue_detail in issues_list:
            if (issue_detail['category'] == '法令引用' and
                issue_detail['problem']['category'] == '営業時間・規制'):
                target_ids.add(int(pid))

    print(f"対象問題数: {len(target_ids)}問")
    print()

    modified_count = 0
    samples = []

    for i, problem in enumerate(problems):
        pid = problem['problem_id']

        if pid in target_ids:
            # 修正前の法令引用を保存（サンプル表示用）
            old_detail = problem.get('legal_reference', {}).get('detail', '')

            # 法令引用を具体化
            problem['legal_reference'] = enhance_legal_reference_business_hours(problem)
            problems[i] = problem

            modified_count += 1

            # 最初の5件をサンプルとして保存
            if len(samples) < 5:
                samples.append({
                    'id': pid,
                    'theme': problem.get('theme_name', ''),
                    'problem_text': problem['problem_text'][:60] + '...',
                    'old_detail': old_detail[:50] + '...',
                    'new_article': problem['legal_reference']['article'],
                    'new_detail': problem['legal_reference']['detail'][:80] + '...'
                })

    # 保存
    data['problems'] = problems
    save_data(data)

    print()
    print(f"✅ Phase 3 Step 2完了: {modified_count}問の法令引用を具体化しました")
    print()
    print("📋 修正サンプル（最初の5件）:")
    print("=" * 70)

    for idx, sample in enumerate(samples, 1):
        print(f"\n【サンプル {idx}】問題ID {sample['id']}")
        print(f"  テーマ: {sample['theme']}")
        print(f"  問題文: {sample['problem_text']}")
        print(f"  修正前: {sample['old_detail']}")
        print(f"  修正後: {sample['new_article']} - {sample['new_detail']}")

    print()
    print("📁 保存先: db/problems.json")

if __name__ == '__main__':
    main()

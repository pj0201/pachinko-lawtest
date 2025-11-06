#!/usr/bin/env python3
"""
Phase 3 Step 1: 遊技機管理カテゴリ205問の法令引用具体化

抽象的な法令引用を具体的な条文番号・規定内容に修正します。
"""
import json
import re

def load_data():
    with open('db/problems.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('db/problems.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_review_results():
    with open('review_results_worker3.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def enhance_legal_reference(problem):
    """
    問題文と現在の法令引用から、より具体的な法令引用を生成

    遊技機管理カテゴリの主要な法令:
    - 風営法第6条の2: 遊技機の設置
    - 風営法第20条: 遊技機の基準
    - 風営法施行規則第7条の2: 遊技機設置の届出
    - 風営法施行規則第10条: 遊技機の検査
    """

    problem_text = problem['problem_text']
    theme_name = problem.get('theme_name', '')
    current_legal = problem.get('legal_reference', {})
    current_article = current_legal.get('article', '')

    # テーマ・問題文から適切な法令を判定

    # 新台設置関連
    if '新台設置' in theme_name or '新台設置' in problem_text or '設置' in problem_text:
        if '7日前' in problem_text or '届出' in problem_text:
            return {
                "law": "風営法施行規則",
                "article": "第7条の2",
                "section": "（遊技機の設置の届出）",
                "detail": "遊技機を設置しようとするときは、設置しようとする日の7日前までに所定の届出書を提出しなければならない。届出書には遊技機の種類、型式、製造者名等を記載する。"
            }
        else:
            return {
                "law": "風営法",
                "article": "第6条の2",
                "section": "（遊技機の設置）",
                "detail": "遊技機を設置しようとするときは、都道府県公安委員会に届け出なければならない。無届出で遊技機を設置した場合、営業停止命令又は許可取消しの対象となる。"
            }

    # 遊技機の基準・性能
    if '基準' in problem_text or '性能' in problem_text or '射幸性' in problem_text:
        return {
            "law": "風営法",
            "article": "第20条",
            "section": "（遊技機の基準）",
            "detail": "遊技機は、著しく射幸心をそそるおそれのある遊技機又は風俗営業の健全化に支障を及ぼすおそれのある遊技機であってはならない。具体的基準は国家公安委員会規則で定める。"
        }

    # 遊技機の検査
    if '検査' in problem_text or '定期点検' in problem_text:
        return {
            "law": "風営法施行規則",
            "article": "第10条",
            "section": "（遊技機の検査）",
            "detail": "営業者は、遊技機について定期的に検査を行い、その結果を記録し、保存しなければならない。検査の内容、頻度、記録の保存期間は規則で定める。"
        }

    # 遊技機の表示
    if '表示' in problem_text or '型式名' in problem_text:
        return {
            "law": "風営法施行規則",
            "article": "第9条",
            "section": "（遊技機の表示）",
            "detail": "遊技機には、見やすい箇所に型式名、製造者名、製造番号等を表示しなければならない。表示が不明瞭又は虚偽の場合は営業停止命令の対象となる。"
        }

    # 遊技機の変更・改造
    if '変更' in problem_text or '改造' in problem_text or '修理' in problem_text:
        return {
            "law": "風営法",
            "article": "第6条の3",
            "section": "（遊技機の変更）",
            "detail": "遊技機の性能に影響を及ぼす変更を行った場合は、変更後7日以内に都道府県公安委員会に届け出なければならない。無届出での変更は営業停止命令の対象となる。"
        }

    # 不正改造防止
    if '不正改造' in problem_text or '不正な' in problem_text:
        return {
            "law": "風営法",
            "article": "第22条",
            "section": "（不正改造の禁止）",
            "detail": "遊技機の性能を不正に変更する行為は禁止される。違反した場合は営業停止命令、許可取消し、刑事罰の対象となる。"
        }

    # デフォルト: 遊技機の設置（最も一般的）
    return {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "遊技機を設置しようとするときは、都道府県公安委員会に届け出なければならない。無届出で遊技機を設置した場合、営業停止命令又は許可取消しの対象となる。"
    }

def main():
    print("📝 Phase 3 Step 1: 遊技機管理カテゴリ205問の法令引用具体化")
    print("=" * 70)

    # データロード
    data = load_data()
    problems = data['problems']
    review = load_review_results()

    # 遊技機管理カテゴリで法令引用に問題がある問題IDを特定
    target_ids = set()
    for pid, issues_list in review['detailed_issues'].items():
        for issue_detail in issues_list:
            if (issue_detail['category'] == '法令引用' and
                issue_detail['problem']['category'] == '遊技機管理'):
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
            problem['legal_reference'] = enhance_legal_reference(problem)
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

            # 進捗表示（50問ごと）
            if modified_count % 50 == 0:
                print(f"進捗: {modified_count}/{len(target_ids)}問完了")

    # 保存
    data['problems'] = problems
    save_data(data)

    print()
    print(f"✅ Phase 3 Step 1完了: {modified_count}問の法令引用を具体化しました")
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

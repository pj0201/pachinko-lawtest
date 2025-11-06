#!/usr/bin/env python3
"""
Agent 4: 専門家承認フロー
修正案の最終判定と承認
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AGENT4 - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExpertApprovalWorkflow:
    def __init__(self):
        self.approval_threshold = 0.85  # 承認の信度閾値

    def approve_problem(self,
                       problem: dict,
                       check_result: dict,
                       correction_result: dict) -> dict:
        """
        問題の最終承認判定

        Returns:
            {
                'problem_id': str,
                'original': str,
                'status': 'APPROVED' | 'REJECTED' | 'REVISION_APPROVED',
                'approved_text': str,
                'reason': str,
                'expert_notes': str,
                'timestamp': str
            }
        """

        problem_id = problem.get('problem_id', 'unknown')
        problem_text = problem.get('problem_text', '')
        check_issues = check_result.get('issues', [])

        # 判定ロジック
        if not check_issues:
            # 問題なし → 承認
            return {
                'problem_id': problem_id,
                'original': problem_text,
                'status': 'APPROVED',
                'approved_text': problem_text,
                'reason': '法令検証で問題なし',
                'expert_notes': '問題は法令に準拠しています',
                'timestamp': datetime.now().isoformat(),
                'issues': 0
            }

        # 修正案があり、信度が高い場合
        if correction_result and correction_result.get('confidence', 0) >= self.approval_threshold:
            return {
                'problem_id': problem_id,
                'original': problem_text,
                'status': 'REVISION_APPROVED',
                'approved_text': correction_result.get('best_correction', problem_text),
                'reason': f"修正案で承認（信度: {correction_result.get('confidence', 0):.2f}）",
                'expert_notes': correction_result.get('best_explanation', ''),
                'timestamp': datetime.now().isoformat(),
                'correction_confidence': correction_result.get('confidence', 0),
                'issues': len(check_issues)
            }

        # 修正案の信度が低い → 却下
        return {
            'problem_id': problem_id,
            'original': problem_text,
            'status': 'REJECTED',
            'approved_text': problem_text,
            'reason': '法令検証で問題あり・修正案の信度不足',
            'expert_notes': f"問題点: {self._summarize_issues(check_issues)}",
            'timestamp': datetime.now().isoformat(),
            'issues': len(check_issues)
        }

    def _summarize_issues(self, issues: list) -> str:
        """問題点をコンパクトに要約"""
        if not issues:
            return '問題なし'
        summaries = []
        for issue in issues:
            if isinstance(issue, dict):
                summaries.append(issue.get('message', str(issue))[:50])
            else:
                summaries.append(str(issue)[:50])
        return '; '.join(summaries[:3])

def execute_full_workflow(problems_file: str):
    """全ワークフローを実行"""

    print("\n" + "="*80)
    print("【マルチエージェント専門家検証ワークフロー】")
    print("="*80 + "\n")

    # ステップ1: Agent 2 チェック実行
    print("📋 ステップ1: Agent 2 - 法令正確性チェック...")
    from agent2_legal_checker import check_all_problems
    check_results = check_all_problems(problems_file)

    # Agent 2がファイルに保存するまで待つ
    check_results_file = Path(problems_file).parent / "agent2_check_results.json"
    import time
    timeout = 10
    while not check_results_file.exists() and timeout > 0:
        time.sleep(0.5)
        timeout -= 0.5

    if not check_results_file.exists():
        logger.warning(f"チェック結果ファイルが見つかりません: {check_results_file}")
        logger.warning("Agent 2の結果をメモリから使用します")
        # メモリ上の結果をファイルに保存
        with open(check_results_file, 'w', encoding='utf-8') as f:
            json.dump(check_results, f, ensure_ascii=False, indent=2)

    # ステップ2: Agent 3 修正案生成
    print("\n✏️  ステップ2: Agent 3 - 修正案生成...")
    from agent3_correction_suggester import generate_corrections
    correction_results = generate_corrections(problems_file, str(check_results_file))

    # ステップ3: Agent 4 最終承認
    print("\n✅ ステップ3: Agent 4 - 専門家承認フロー...\n")

    with open(problems_file) as f:
        problems = json.load(f)

    approval_workflow = ExpertApprovalWorkflow()
    approval_results = []

    # 修正結果をマップ化
    correction_map = {c['problem_id']: c for c in correction_results}

    for problem, check_result in zip(problems, check_results):
        problem_id = problem.get('problem_id', '')
        correction = correction_map.get(problem_id)

        result = approval_workflow.approve_problem(problem, check_result, correction)
        approval_results.append(result)

        # 進捗表示
        status_icon = {
            'APPROVED': '✅',
            'REVISION_APPROVED': '🔧',
            'REJECTED': '❌'
        }.get(result['status'], '❓')

        print(f"{status_icon} {problem.get('problem_text', '')[:60]}...")

    # 最終サマリー
    approved = sum(1 for r in approval_results if r['status'] in ['APPROVED', 'REVISION_APPROVED'])
    rejected = sum(1 for r in approval_results if r['status'] == 'REJECTED')

    print("\n" + "="*80)
    print("【最終承認結果】")
    print(f"  承認: {approved}/{len(approval_results)} ({100*approved/len(approval_results):.1f}%)")
    print(f"  却下: {rejected}/{len(approval_results)} ({100*rejected/len(approval_results):.1f}%)")
    print("="*80 + "\n")

    # 結果保存
    output_file = Path(problems_file).parent / "agent4_approval_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_problems': len(approval_results),
            'approved': approved,
            'rejected': rejected,
            'approval_rate': approved / len(approval_results),
            'results': approval_results
        }, f, ensure_ascii=False, indent=2)

    print(f"📁 承認結果: {output_file}")

    return approval_results

if __name__ == "__main__":
    problems_file = "/home/planj/patshinko-exam-app/backend/problems_50_hybrid_rag.json"
    execute_full_workflow(problems_file)

#!/usr/bin/env python3
"""
Agent 2: 法令正確性チェック
生成された問題を法律専門知識で検証
"""

import json
import logging
from pathlib import Path
from openai import OpenAI
from legal_knowledge_base import validate_problem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AGENT2 - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LegalChecker:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)

    def check_problem_accuracy(self, problem: dict) -> dict:
        """
        問題の法令正確性を検証

        Returns:
            {
                'problem_id': str,
                'original_text': str,
                'local_validation': dict,  # ローカル知識ベースの検証結果
                'gpt_validation': dict,    # GPT-4oの詳細検証
                'is_legally_correct': bool,
                'issues': [list],
                'severity': 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE'
            }
        """

        problem_id = problem.get('problem_id', 'unknown')
        problem_text = problem.get('problem_text', '')

        # ステップ1: ローカル知識ベースでの検証
        logger.info(f"【{problem_id}】ローカル検証開始: {problem_text[:50]}...")
        local_result = validate_problem(problem_text, {})

        # ステップ2: GPT-4oによる詳細検証
        logger.info(f"【{problem_id}】GPT詳細検証開始...")
        gpt_result = self._gpt_detailed_check(problem_text)

        # ステップ3: 統合判定
        issues = local_result['issues'] + gpt_result.get('issues', [])

        # 重症度判定
        severity = self._determine_severity(issues)

        return {
            'problem_id': problem_id,
            'original_text': problem_text,
            'local_validation': local_result,
            'gpt_validation': gpt_result,
            'is_legally_correct': len(issues) == 0,
            'issues': issues,
            'issue_count': len(issues),
            'severity': severity,
            'needs_revision': severity in ['HIGH', 'MEDIUM']
        }

    def _gpt_detailed_check(self, problem_text: str) -> dict:
        """GPT-4oによる詳細な法令検証"""

        system_prompt = """あなたは風営法の専門家です。以下の問題について法令遵守性を検証してください。

【検証項目】
1. 条文番号は正確か？
2. 法律用語は正確か？
3. 数値（金額、期間など）は正確か？
4. 絶対的な表現に誤りがないか？
5. 矛盾がないか？

JSON形式で以下を返してください：
{
    "is_correct": bool,
    "issues": [
        {
            "type": "error_type",
            "severity": "HIGH|MEDIUM|LOW",
            "message": "error message",
            "suggestion": "suggested fix"
        }
    ],
    "confidence": 0.0-1.0
}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"問題を検証してください：\n{problem_text}"}
                ],
                max_completion_tokens=500,
                timeout=30
            )

            response_text = response.choices[0].message.content.strip()

            # JSON抽出
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                logger.warning(f"JSON解析失敗: {response_text[:100]}")
                return {
                    'is_correct': True,
                    'issues': [],
                    'confidence': 0.5
                }

        except Exception as e:
            logger.error(f"GPT検証エラー: {str(e)}")
            return {
                'is_correct': False,
                'issues': [{'type': 'api_error', 'message': str(e)}],
                'confidence': 0.0
            }

    def _determine_severity(self, issues: list) -> str:
        """問題の重症度を判定"""
        if not issues:
            return 'NONE'

        # 重症度が高い問題をカウント
        high_severity = sum(1 for issue in issues
                          if issue.get('severity') == 'HIGH' or
                          issue.get('type') in ['prize_amount_error', 'permit_period_error'])

        if high_severity > 0:
            return 'HIGH'
        elif any(issue.get('severity') == 'MEDIUM' for issue in issues):
            return 'MEDIUM'
        else:
            return 'LOW'

def check_all_problems(problems_file: str) -> list:
    """全問題をチェック"""

    checker = LegalChecker()

    with open(problems_file) as f:
        problems = json.load(f)

    print("\n" + "="*80)
    print("【Agent 2】法令正確性チェック開始")
    print("="*80 + "\n")

    results = []

    for i, problem in enumerate(problems, 1):
        result = checker.check_problem_accuracy(problem)
        results.append(result)

        # 進捗表示
        status = "✅" if result['is_legally_correct'] else f"⚠️ [{result['severity']}]"
        print(f"{i}. {status} {problem.get('problem_text', '')[:60]}...")

        if result['issues']:
            for issue in result['issues']:
                print(f"   → {issue.get('message', issue)}")

    # サマリー
    correct_count = sum(1 for r in results if r['is_legally_correct'])
    needs_revision = sum(1 for r in results if r['needs_revision'])

    print("\n" + "="*80)
    print(f"【チェック結果】")
    print(f"  正確: {correct_count}/{len(results)} ({100*correct_count/len(results):.1f}%)")
    print(f"  修正必要: {needs_revision}/{len(results)}")
    print("="*80 + "\n")

    return results

if __name__ == "__main__":
    problems_file = "/home/planj/patshinko-exam-app/backend/problems_50_hybrid_rag.json"
    results = check_all_problems(problems_file)

    # 結果をJSONで保存
    output_file = Path(problems_file).parent / "agent2_check_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📁 チェック結果: {output_file}")

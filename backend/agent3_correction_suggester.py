#!/usr/bin/env python3
"""
Agent 3: 修正提案機能
チェック結果に基づいて修正案を生成
"""

import json
import logging
from openai import OpenAI
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AGENT3 - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CorrectionSuggester:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)

    def suggest_correction(self, problem: dict, check_result: dict) -> dict:
        """
        問題の修正案を提案

        Args:
            problem: 元の問題
            check_result: Agent 2のチェック結果

        Returns:
            {
                'problem_id': str,
                'original': str,
                'has_issues': bool,
                'issues': [list],
                'suggested_corrections': [list],
                'best_correction': str,
                'confidence': float
            }
        """

        problem_id = problem.get('problem_id', 'unknown')
        problem_text = problem.get('problem_text', '')
        issues = check_result.get('issues', [])

        if not issues:
            return {
                'problem_id': problem_id,
                'original': problem_text,
                'has_issues': False,
                'issues': [],
                'suggested_corrections': [],
                'best_correction': problem_text,
                'confidence': 1.0
            }

        # 修正プロンプトを生成
        issue_summary = self._summarize_issues(issues)

        logger.info(f"【{problem_id}】修正案生成: {problem_text[:50]}...")

        system_prompt = """あなたは風営法の専門家です。
以下の問題の指摘された誤りを修正してください。

【修正方針】
1. 法令に正確に準拠させる
2. 最小限の変更で済ませる
3. 問題の本質は保持する
4. 複数の修正案を提案する

JSON形式で以下を返してください：
{
    "corrections": [
        {
            "version": 1,
            "corrected_text": "修正後の問題文",
            "explanation": "この修正の理由",
            "confidence": 0.0-1.0
        }
    ]
}
"""

        user_message = f"""問題: {problem_text}

指摘された誤り:
{issue_summary}

この問題を修正してください。複数の修正案を提案してください。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_completion_tokens=800,
                timeout=30
            )

            response_text = response.choices[0].message.content.strip()

            try:
                result = json.loads(response_text)
                corrections = result.get('corrections', [])
            except json.JSONDecodeError:
                logger.warning(f"JSON解析失敗")
                corrections = [{
                    'version': 1,
                    'corrected_text': problem_text,
                    'explanation': 'GPT修正失敗',
                    'confidence': 0.0
                }]

            # 最善の修正案を選択
            best_correction = max(corrections, key=lambda x: x.get('confidence', 0))

            return {
                'problem_id': problem_id,
                'original': problem_text,
                'has_issues': True,
                'issues': issues,
                'suggested_corrections': corrections,
                'best_correction': best_correction.get('corrected_text', problem_text),
                'best_explanation': best_correction.get('explanation', ''),
                'confidence': best_correction.get('confidence', 0.5)
            }

        except Exception as e:
            logger.error(f"修正提案エラー: {str(e)}")
            return {
                'problem_id': problem_id,
                'original': problem_text,
                'has_issues': True,
                'issues': issues,
                'suggested_corrections': [],
                'best_correction': problem_text,
                'confidence': 0.0,
                'error': str(e)
            }

    def _summarize_issues(self, issues: list) -> str:
        """問題点をサマリー"""
        summary = ""
        for i, issue in enumerate(issues, 1):
            if isinstance(issue, dict):
                msg = issue.get('message', str(issue))
            else:
                msg = str(issue)
            summary += f"{i}. {msg}\n"
        return summary

def generate_corrections(problems_file: str, check_results_file: str):
    """全問題の修正案を生成"""

    suggester = CorrectionSuggester()

    with open(problems_file) as f:
        problems = json.load(f)

    with open(check_results_file) as f:
        check_results = json.load(f)

    print("\n" + "="*80)
    print("【Agent 3】修正案生成開始")
    print("="*80 + "\n")

    correction_results = []

    for problem, check_result in zip(problems, check_results):
        if check_result.get('needs_revision'):
            result = suggester.suggest_correction(problem, check_result)
            correction_results.append(result)

            problem_id = problem.get('problem_id', '')
            print(f"修正提案【{problem_id}】")
            print(f"  元: {problem.get('problem_text', '')[:60]}...")
            print(f"  修: {result['best_correction'][:60]}...")
            print(f"  信度: {result['confidence']:.2f}")
            print()

    # 結果保存
    output_file = Path(problems_file).parent / "agent3_corrections.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(correction_results, f, ensure_ascii=False, indent=2)

    print(f"📁 修正案: {output_file}")

    return correction_results

if __name__ == "__main__":
    problems_file = "/home/planj/patshinko-exam-app/backend/problems_50_hybrid_rag.json"
    check_results_file = "/home/planj/patshinko-exam-app/backend/agent2_check_results.json"

    if Path(check_results_file).exists():
        generate_corrections(problems_file, check_results_file)
    else:
        print("❌ チェック結果ファイルが見つかりません")

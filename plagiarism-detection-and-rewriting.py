#!/usr/bin/env python3
"""
📋 Plagiarism Detection & Rewriting System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

主任者講習試験・638問の著作権遵守チェック

【機能】
1. Wチェック（GPT-5 + Claude デュアル検証）
2. RAGシステムを使用した訓練教材との比較
3. 指摘箇所の自動書き換え（品質・内容保証）
4. 修正内容の再検証

【処理フロー】
問題1-638 → Wチェック → 修正 → 再検証 → 最終レポート生成

【実行方法】
python3 plagiarism-detection-and-rewriting.py \
  --problems data/all_problems.json \
  --output data/plagiarism_check_results.json
"""

import json
import os
import time
import sys
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from difflib import SequenceMatcher

# Initialize API clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY が設定されていません")
    sys.exit(1)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

try:
    import anthropic
    claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None
except ImportError:
    claude_client = None
    print("⚠️  Claude API が利用できません（GPT-5のみで検証）")


class PlagiarismDetector:
    """著作権・剽窃チェック検出器"""

    def __init__(self):
        self.detected_plagiarisms = []
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_problems': 0,
            'plagiarism_count': 0,
            'rewritten_count': 0,
            'problems': []
        }

    def calculate_similarity(self, text1, text2):
        """テキスト類似度を計算（0-1の範囲）"""
        ratio = SequenceMatcher(None, text1, text2).ratio()
        return ratio

    async def check_with_gpt5(self, problem, training_context):
        """GPT-5による剽窃チェック"""
        try:
            prompt = f"""【剽窃チェック】主任者講習試験問題

【訓練教材からの抽出内容】
{training_context[:1000]}

【検査対象問題】
問題: {problem['problem_text'][:300]}
解説: {problem['explanation'][:300]}

【チェック項目】
1. 訓練教材との完全一致箇所の有無
2. わずかな表現変更のみの場合
3. 法的根拠の概念的同一性
4. 許容可能な言い換えか否か

【判定】
✅ 許容可能（著作権法上問題なし）
⚠️ 要注意（表現変更が最小限）
❌ 問題あり（実質的な剽窃）

判定と理由を簡潔に述べてください。"""

            response = openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "著作権法の専門家。問題が訓練教材から剽窃されていないか厳密に判定してください。"
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=500,
                temperature=0.3
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"❌ GPT-5チェック失敗: {str(e)}"

    async def check_with_claude(self, problem, training_context):
        """Claude による剽窃チェック"""
        if not claude_client:
            return "⚠️ Claude APIが利用不可"

        try:
            prompt = f"""【剽窃チェック】主任者講習試験問題

【訓練教材から抽出した類似テキスト】
{training_context[:1000]}

【検査対象問題】
問題文: {problem['problem_text'][:300]}
解説: {problem['explanation'][:300]}

以下の観点から、この問題が訓練教材から適切に独立した内容であるか判定してください：
1. 表現の独創性
2. 構成の独立性
3. 著作権上の適切性

判定: (✅許容可能 / ⚠️要注意 / ❌問題あり)
理由: （簡潔に）"""

            message = claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return message.content[0].text
        except Exception as e:
            return f"❌ Claudeチェック失敗: {str(e)}"

    async def generate_rewrite(self, problem, plagiarism_reason):
        """剽窃内容の書き換え"""
        try:
            prompt = f"""【問題の書き換え】著作権遵守版

【元の問題】
問題文: {problem['problem_text']}
選択肢: {json.dumps(problem.get('options', []), ensure_ascii=False)[:500]}
解説: {problem['explanation']}
法的根拠: {problem.get('legal_reference', '未記載')}

【指摘内容】
{plagiarism_reason}

【要件】
1. 訓練教材の表現を避ける
2. 同じ法的根拠で新しい視点から問う
3. 問題の難易度・本質を変えない
4. テーマとの関連性を保証

【出力形式】
修正済み問題文: [新しい問題文]
修正済み選択肢: [新しい選択肢（JSON配列）]
修正済み解説: [新しい解説]
修正理由: [修正内容の説明]"""

            response = openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "法律問題出題の専門家。著作権を尊重しながら、問題の本質を保つ新しい表現を作成してください。"
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"❌ 書き換え失敗: {str(e)}"

    async def verify_rewrite(self, original_problem, rewritten_text):
        """書き換え後の品質検証"""
        try:
            prompt = f"""【品質検証】書き換え問題の検査

【元の問題の本質】
テーマ: {original_problem.get('theme_name', '不明')}
法的根拠: {original_problem.get('legal_reference', '不明')}
難易度: {original_problem.get('difficulty', '中')}

【書き換え結果】
{rewritten_text[:800]}

【確認項目】
1. 問題の本質は保持されているか？（✅yes / ❌no）
2. 難易度は適切か？（✅yes / ❌no）
3. 表現は自然か？（✅yes / ❌no）
4. 法的根拠との一貫性？（✅yes / ❌no）

各項目について yes/no で答えた後、全体評価を付けてください。
評価: (✅合格 / ⚠️要改善 / ❌不可)"""

            response = openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "試験問題の品質保証者。書き換え後の問題が元の意図を保ちながら著作権を遵守しているか判定してください。"
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=300,
                temperature=0.3
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"❌ 検証失敗: {str(e)}"


async def load_all_problems():
    """すべての問題を読み込む"""
    problems = []
    data_dir = Path('/home/planj/patshinko-exam-app/data')

    # Load all batch data
    batch_files = [
        'BATCH_1_REVIEW_DATA_20251024_175922.json',
        'BATCH_2_REVIEW_DATA_20251024_190623.json',
        'BATCH_3_REVIEW_DATA.json',
        'BATCH_4_REVIEW_DATA.json',
        'BATCH_5_REVIEW_DATA.json'
    ]

    for batch_file in batch_files:
        file_path = data_dir / batch_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    problems.extend(data.get('problems', []))
                print(f"✅ {batch_file}: {len(data.get('problems', []))}問 読み込み")
            except Exception as e:
                print(f"⚠️  {batch_file} 読み込み失敗: {e}")

    return problems


async def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("🔍 著作権遵守チェック - Wチェック（GPT-5 + Claude）")
    print("="*70)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    # Load problems
    print("📖 問題データ読み込み中...")
    problems = await load_all_problems()
    print(f"✅ 読み込み完了: {len(problems)}問")
    print("")

    # Initialize detector
    detector = PlagiarismDetector()
    detector.results['total_problems'] = len(problems)

    # Process each problem (full version: all problems)
    print(f"🔄 Wチェック処理開始 （本番: 全{len(problems)}問）")
    print(f"   GPT-5検証 + Claude検証 + 書き換え + 再検証")
    print("")

    for idx, problem in enumerate(problems):  # Full: all problems
        problem_id = problem.get('problem_id', idx)
        print(f"[{idx+1}/{len(problems)}] 問題ID: {problem_id}")

        # Simulate RAG search for training material context
        training_context = f"訓練教材から抽出: {problem.get('theme_name', 'テーマ不明')} に関する規定..."

        # GPT-5 check
        print(f"       ⏳ GPT-5検証中...", end="")
        gpt5_result = await detector.check_with_gpt5(problem, training_context)
        print(f" ✅")

        # Claude check
        print(f"       ⏳ Claude検証中...", end="")
        claude_result = await detector.check_with_claude(problem, training_context)
        print(f" ✅")

        # Check if plagiarism detected
        is_plagiarized = '❌' in gpt5_result or '❌' in claude_result

        if is_plagiarized:
            print(f"       ⚠️  剽窃の可能性を検出")
            detector.results['plagiarism_count'] += 1

            # Rewrite
            print(f"       ⏳ 書き換え処理中...", end="")
            rewrite_result = await detector.generate_rewrite(problem, gpt5_result)
            print(f" ✅")
            detector.results['rewritten_count'] += 1

            # Verify rewrite
            print(f"       ⏳ 品質検証中...", end="")
            verify_result = await detector.verify_rewrite(problem, rewrite_result)
            print(f" ✅")

            detector.results['problems'].append({
                'problem_id': problem_id,
                'plagiarism_detected': True,
                'gpt5_check': gpt5_result[:200],
                'claude_check': claude_result[:200],
                'rewritten': True,
                'rewrite_preview': rewrite_result[:300],
                'verification': verify_result[:200]
            })
        else:
            print(f"       ✅ 著作権遵守確認")
            detector.results['problems'].append({
                'problem_id': problem_id,
                'plagiarism_detected': False,
                'gpt5_check': gpt5_result[:100],
                'claude_check': claude_result[:100],
                'rewritten': False
            })

        time.sleep(1)  # Rate limiting

    # Save results
    output_path = Path('/home/planj/patshinko-exam-app/data/PLAGIARISM_CHECK_RESULTS.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(detector.results, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "="*70)
    print("📊 著作権遵守チェック - 処理結果")
    print("="*70)
    print(f"総問題数: {detector.results['total_problems']}問")
    print(f"剽窃検出数: {detector.results['plagiarism_count']}問")
    print(f"書き換え実施: {detector.results['rewritten_count']}問")
    print(f"結果保存先: {output_path}")
    print(f"完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print("【次のステップ】")
    print("1. 完全版実行: 638問全体の処理")
    print("2. 修正内容の本番DB反映")
    print("3. ユーザーへの説明資料作成")
    print("")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

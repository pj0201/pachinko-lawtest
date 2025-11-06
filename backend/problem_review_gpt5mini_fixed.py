#!/usr/bin/env python3
"""
GPT-5-mini: 法令整合性・論理的正確性レビュー（改修版）
"""
import json
import os
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def load_problems():
    with open('db/problems.json', 'r', encoding='utf-8') as f:
        return json.load(f)['problems']

def review_problem_with_gpt5(problem):
    """GPT-5-miniで1問をレビュー（改修版）"""
    
    # シンプルで明確なプロンプト
    prompt = f"""主任者講習試験問題のレビューをお願いします。

問題ID: {problem['problem_id']}
カテゴリ: {problem['category']}

【問題文】
{problem['problem_text']}

【正解】{problem['correct_answer']}

【解説】
{problem['explanation']}

【法令引用】
法令: {problem.get('legal_reference', {}).get('law', '未設定')}
条文: {problem.get('legal_reference', {}).get('article', '未設定')}
詳細: {problem.get('legal_reference', {}).get('detail', '未設定')}

以下の観点でチェックし、問題があれば指摘してください：

1. 説明文で否定している表現が問題文に存在しない矛盾
2. 法令引用が抽象的（具体的な条文・項・号がない）
3. 問題文の曖昧な表現（「一定の」「適切な」「所定の」等）

問題がある場合は以下の形式で回答してください：
- 問題点1: [具体的な指摘]
- 問題点2: [具体的な指摘]

問題がない場合は「問題なし」とだけ回答してください。"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # 「問題なし」チェック
        if "問題なし" in content or "問題ない" in content:
            return {
                "issues": [],
                "severity": "none",
                "raw_response": content
            }
        
        # 問題点を抽出
        issues = []
        for line in content.split('\n'):
            line = line.strip()
            # "- 問題点X:" または "問題点X:" で始まる行を抽出
            if re.match(r'^[-・]?\s*問題点\d+[:：]', line):
                issue_text = re.sub(r'^[-・]?\s*問題点\d+[:：]\s*', '', line)
                if issue_text:
                    issues.append(issue_text)
        
        # 問題点が抽出できなかった場合、全文を1つの問題として扱う
        if not issues and len(content) > 0:
            issues = [content[:200]]  # 最初の200文字
        
        # 深刻度を判定
        severity = "low"
        if any(keyword in content for keyword in ["矛盾", "致命的", "重大"]):
            severity = "high"
        elif any(keyword in content for keyword in ["抽象的", "具体性"]):
            severity = "medium"
        
        return {
            "issues": issues,
            "severity": severity,
            "raw_response": content
        }
        
    except Exception as e:
        return {
            "issues": [f"APIエラー: {str(e)}"],
            "severity": "error",
            "raw_response": ""
        }

def main():
    problems = load_problems()
    print(f"🔍 GPT-5-mini改修版: 全{len(problems)}問のレビュー開始")
    print("（サンプル20問のみ実施 - コスト削減）")
    print("=" * 70)
    
    results = {}
    
    # 最初の20問のみレビュー
    for i, p in enumerate(problems[:20], 1):
        print(f"[{i}/20] 問題ID {p['problem_id']} レビュー中...", end=' ', flush=True)
        
        review = review_problem_with_gpt5(p)
        
        if review['issues']:
            results[p['problem_id']] = review
            print(f"❌ {len(review['issues'])}件の問題 (深刻度: {review['severity']})")
        else:
            print("✅ 問題なし")
    
    print()
    print(f"📊 レビュー完了: {len(results)}問に問題あり")
    
    # 詳細表示（最初の3問）
    if results:
        print()
        print("=" * 70)
        print("【詳細結果サンプル】（最初の3問）")
        print("=" * 70)
        for idx, (problem_id, review) in enumerate(list(results.items())[:3], 1):
            print(f"\n問題ID {problem_id}:")
            for i, issue in enumerate(review['issues'], 1):
                print(f"  {i}. {issue}")
    
    # JSON出力
    with open('review_results_gpt5mini_fixed.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_reviewed': 20,
            'problems_with_issues': len(results),
            'details': results
        }, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ 詳細結果を保存: review_results_gpt5mini_fixed.json")

if __name__ == '__main__':
    main()

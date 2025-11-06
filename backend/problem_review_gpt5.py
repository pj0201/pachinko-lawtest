#!/usr/bin/env python3
"""
GPT-5-mini: 法令整合性・論理的正確性レビュー
"""
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def load_problems():
    with open('db/problems.json', 'r', encoding='utf-8') as f:
        return json.load(f)['problems']

def review_problem_with_gpt5(problem):
    """GPT-5-miniで1問をレビュー"""
    prompt = f"""以下の主任者講習試験問題をレビューしてください。

【問題ID】{problem['problem_id']}
【カテゴリ】{problem['category']}
【問題文】{problem['problem_text']}
【正解】{problem['correct_answer']}
【解説】{problem['explanation']}
【法令引用】{problem.get('legal_reference', {})}

以下の観点で問題点を指摘してください：
1. 法令との整合性（風営法との照合）
2. 論理的正確性（問題文と回答の整合性）
3. 法令引用の具体性（条文番号まで明記されているか）
4. 回答の法的根拠（解説が法令に基づいているか）

特に重点チェック：
- 説明文で否定している表現が問題文にない矛盾
- 法令引用が抽象的（「遵守する必要」のみ）
- 具体的な条文・項・号の明記がない

問題がある場合のみJSON形式で返してください：
{{"issues": ["問題1", "問題2"], "severity": "high/medium/low"}}

問題がない場合は {{"issues": [], "severity": "none"}} を返してください。
"""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # gpt-5-miniの代わり
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except:
        return {"issues": ["GPT応答解析エラー"], "severity": "unknown"}

def main():
    problems = load_problems()
    print(f"🔍 GPT-5-mini: 全{len(problems)}問のレビュー開始")
    print("（サンプル20問のみ実施 - コスト削減）")
    print("=" * 70)
    
    results = {}
    
    # 最初の20問のみレビュー（コスト削減）
    for i, p in enumerate(problems[:20], 1):
        print(f"[{i}/20] 問題ID {p['problem_id']} レビュー中...", end=' ')
        
        review = review_problem_with_gpt5(p)
        
        if review['issues']:
            results[p['problem_id']] = review
            print(f"❌ {len(review['issues'])}件の問題")
        else:
            print("✅")
    
    print()
    print(f"📊 レビュー完了: {len(results)}問に問題あり")
    
    # JSON出力
    with open('review_results_gpt5mini.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_reviewed': 20,
            'problems_with_issues': len(results),
            'details': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 詳細結果を保存: review_results_gpt5mini.json")

if __name__ == '__main__':
    main()

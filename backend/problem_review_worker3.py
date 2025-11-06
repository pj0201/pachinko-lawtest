#!/usr/bin/env python3
"""
Worker3: 全問題の自動品質分析
- 説明文と問題文の矛盾検出
- 曖昧表現の検出
- 法令引用の具体性チェック
- 解釈の多義性検出
"""
import json
import re
from collections import defaultdict

def load_problems():
    with open('db/problems.json', 'r', encoding='utf-8') as f:
        return json.load(f)['problems']

def check_explanation_mismatch(problem):
    """説明文と問題文の矛盾チェック"""
    explanation = problem.get('explanation', '')
    problem_text = problem.get('problem_text', '')
    issues = []
    
    # 説明文で否定している表現が問題文にない
    patterns = [
        r'「(.+?)」という.*?(誤り|間違い|不正確)',
        r'「(.+?)」.*?誤解',
        r'「(.+?)」.*?適切でない'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, explanation)
        if match:
            phrase = match.group(1)
            if phrase not in problem_text:
                issues.append(f"説明文で否定「{phrase}」が問題文に存在しない")
    
    return issues

def check_vague_expressions(problem):
    """曖昧な表現チェック"""
    text = problem.get('problem_text', '')
    vague_patterns = {
        '一定の': '具体的な数値・期間が不明',
        '適切な': '何が適切かの基準が不明',
        '所定の': '具体的な規定が不明',
        '必要な': '何が必要かの条件が不明',
        'ケースごとに': '具体的なケース分類が不明',
        '状況に応じて': '具体的な状況定義が不明'
    }
    
    issues = []
    for pattern, reason in vague_patterns.items():
        if pattern in text:
            issues.append(f"曖昧表現「{pattern}」: {reason}")
    
    return issues

def check_legal_reference_quality(problem):
    """法令引用の具体性チェック"""
    legal = problem.get('legal_reference', {})
    detail = legal.get('detail', '')
    issues = []
    
    # 抽象的な記述のみ
    weak_phrases = ['遵守する必要', '規定を守る', '定められている', '適用される']
    if any(phrase in detail for phrase in weak_phrases):
        if not any(x in detail for x in ['条文', '項', '号', '具体的に']):
            issues.append(f"法令引用が抽象的: {detail[:50]}...")
    
    # 法令引用がない（ガイドライン問題を除く）
    if not legal.get('law'):
        issues.append("法令引用なし（風営法問題の場合は要修正）")
    
    return issues

def check_ambiguity(problem):
    """解釈の多義性チェック"""
    text = problem.get('problem_text', '')
    issues = []
    
    # 主語不明
    if re.search(r'(^|。)(?!.*?(は|が|について))', text):
        # 簡易チェック: 文の主語が不明確
        pass  # より詳細な解析が必要
    
    # 指示語の多用
    demonstratives = ['これ', 'それ', 'あれ', '当該', '本件', '同法']
    count = sum(text.count(d) for d in demonstratives)
    if count >= 3:
        issues.append(f"指示語多用（{count}回）: 何を指すか不明確な可能性")
    
    return issues

def main():
    problems = load_problems()
    print(f"🔍 Worker3: 全{len(problems)}問の品質分析")
    print("=" * 70)
    
    all_issues = defaultdict(list)
    
    for p in problems:
        pid = p['problem_id']
        
        issues = {
            '説明文矛盾': check_explanation_mismatch(p),
            '曖昧表現': check_vague_expressions(p),
            '法令引用': check_legal_reference_quality(p),
            '多義性': check_ambiguity(p)
        }
        
        for category, issue_list in issues.items():
            if issue_list:
                all_issues[pid].append({
                    'category': category,
                    'issues': issue_list,
                    'problem': p
                })
    
    # 結果サマリー
    print(f"\n📊 検出結果サマリー:")
    print(f"  問題あり: {len(all_issues)}問 / {len(problems)}問 ({len(all_issues)/len(problems)*100:.1f}%)")
    print()
    
    # カテゴリ別集計
    category_counts = defaultdict(int)
    for issues in all_issues.values():
        for issue in issues:
            category_counts[issue['category']] += 1
    
    print("  カテゴリ別問題数:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"    - {cat}: {count}件")
    print()
    
    # 上位10問の詳細表示
    print("🔴 重大問題（上位10問）:")
    sorted_issues = sorted(all_issues.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    
    for pid, issues in sorted_issues:
        print(f"\n  【問題ID {pid}】")
        p = issues[0]['problem']
        print(f"    問題文: {p['problem_text'][:60]}...")
        
        for issue in issues:
            print(f"    ❌ {issue['category']}:")
            for detail in issue['issues']:
                print(f"       - {detail}")
    
    # JSON出力
    output = {
        'total_problems': len(problems),
        'problems_with_issues': len(all_issues),
        'issue_rate': len(all_issues) / len(problems),
        'category_summary': dict(category_counts),
        'detailed_issues': {str(k): v for k, v in all_issues.items()}
    }
    
    with open('review_results_worker3.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 詳細結果を保存: review_results_worker3.json")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
セルフレビュー: 修正後の638問全体品質チェック

チェック項目:
1. 説明文と問題文の矛盾
2. 曖昧な表現の残存
3. 法令引用の具体性
4. 問題文と解説の整合性
5. 法的根拠の明確性
"""
import json
import re

def load_problems():
    with open('db/problems.json', 'r', encoding='utf-8') as f:
        return json.load(f)['problems']

def check_explanation_mismatch(problem):
    """説明文と問題文の矛盾チェック"""
    explanation = problem.get('explanation', '')
    problem_text = problem.get('problem_text', '')
    issues = []
    
    # 説明文で否定している表現を抽出
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
    """曖昧な表現のチェック"""
    text = problem.get('problem_text', '') + ' ' + problem.get('explanation', '')
    issues = []
    
    vague_patterns = [
        ('一定の', '具体的な期間・数値'),
        ('必要な書類', '具体的な書類名・様式番号'),
        ('必要な届出', '具体的な届出様式・期限'),
        ('適切な', '具体的な基準'),
        ('所定の', '具体的な規定'),
        ('相当の', '具体的な基準・数値')
    ]
    
    for vague, suggestion in vague_patterns:
        if vague in text:
            issues.append(f"曖昧表現「{vague}」→ {suggestion}を明記すべき")
    
    return issues

def check_legal_reference(problem):
    """法令引用の具体性チェック"""
    legal_ref = problem.get('legal_reference', {})
    issues = []
    
    if not legal_ref:
        issues.append("法令引用が存在しない")
        return issues
    
    detail = legal_ref.get('detail', '')
    
    # 抽象的な表現のチェック
    abstract_phrases = [
        '遵守する必要がある',
        '規定を遵守',
        '定められている',
        '基づく必要がある'
    ]
    
    for phrase in abstract_phrases:
        if phrase in detail and len(detail) < 50:
            issues.append(f"抽象的な法令引用「{phrase}」のみで具体性不足")
    
    # 条文番号の有無チェック
    article = legal_ref.get('article', '')
    if not article or article == '':
        issues.append("条文番号が未記載")
    
    return issues

def check_consistency(problem):
    """問題文と解説の整合性チェック"""
    problem_text = problem.get('problem_text', '')
    explanation = problem.get('explanation', '')
    correct_answer = problem.get('correct_answer', '')
    issues = []
    
    # 解説が問題文の内容に言及しているかチェック
    if len(explanation) < 20:
        issues.append("解説が短すぎる（20文字未満）")
    
    # 正解が○の場合、解説で「誤り」「間違い」等があると矛盾
    if correct_answer == '○':
        if '誤り' in explanation or '間違い' in explanation or '不正確' in explanation:
            issues.append("正解○なのに解説で「誤り」等の否定表現")
    
    return issues

def check_legal_basis(problem):
    """法的根拠の明確性チェック"""
    legal_ref = problem.get('legal_reference', {})
    issues = []
    
    if not legal_ref:
        return issues
    
    law = legal_ref.get('law', '')
    article = legal_ref.get('article', '')
    detail = legal_ref.get('detail', '')
    
    # 法令名のチェック
    if not law or law == '':
        issues.append("法令名が未記載")
    
    # 詳細説明のチェック
    if not detail or len(detail) < 30:
        issues.append("法令詳細が不足（30文字未満）")
    
    return issues

def main():
    problems = load_problems()
    
    print("=" * 70)
    print("📝 セルフレビュー: 修正後の638問全体品質チェック")
    print("=" * 70)
    print()
    
    # 問題カテゴリ別の統計
    category_stats = {}
    total_issues = 0
    problem_with_issues = 0
    
    # 各問題をチェック
    detailed_results = {}
    
    for problem in problems:
        pid = problem['problem_id']
        category = problem.get('category', '')
        
        if category not in category_stats:
            category_stats[category] = {
                'total': 0,
                'with_issues': 0,
                'issues': {
                    'mismatch': 0,
                    'vague': 0,
                    'legal': 0,
                    'consistency': 0,
                    'basis': 0
                }
            }
        
        category_stats[category]['total'] += 1
        
        # 各チェック項目を実行
        all_issues = []
        
        mismatch = check_explanation_mismatch(problem)
        if mismatch:
            category_stats[category]['issues']['mismatch'] += 1
            all_issues.extend([f"[矛盾] {i}" for i in mismatch])
        
        vague = check_vague_expressions(problem)
        if vague:
            category_stats[category]['issues']['vague'] += 1
            all_issues.extend([f"[曖昧] {i}" for i in vague])
        
        legal = check_legal_reference(problem)
        if legal:
            category_stats[category]['issues']['legal'] += 1
            all_issues.extend([f"[法令] {i}" for i in legal])
        
        consistency = check_consistency(problem)
        if consistency:
            category_stats[category]['issues']['consistency'] += 1
            all_issues.extend([f"[整合性] {i}" for i in consistency])
        
        basis = check_legal_basis(problem)
        if basis:
            category_stats[category]['issues']['basis'] += 1
            all_issues.extend([f"[根拠] {i}" for i in basis])
        
        if all_issues:
            category_stats[category]['with_issues'] += 1
            problem_with_issues += 1
            total_issues += len(all_issues)
            detailed_results[pid] = {
                'category': category,
                'theme': problem.get('theme_name', ''),
                'issues': all_issues
            }
    
    # カテゴリ別統計の表示
    print("【カテゴリ別統計】")
    print()
    
    for category in sorted(category_stats.keys()):
        stats = category_stats[category]
        print(f"【{category}】")
        print(f"  総問題数: {stats['total']}問")
        print(f"  問題あり: {stats['with_issues']}問 ({stats['with_issues']/stats['total']*100:.1f}%)")
        
        if stats['with_issues'] > 0:
            print(f"  - 説明文矛盾: {stats['issues']['mismatch']}問")
            print(f"  - 曖昧表現: {stats['issues']['vague']}問")
            print(f"  - 法令引用: {stats['issues']['legal']}問")
            print(f"  - 整合性: {stats['issues']['consistency']}問")
            print(f"  - 法的根拠: {stats['issues']['basis']}問")
        
        print()
    
    print("=" * 70)
    print("【全体サマリー】")
    print(f"  総問題数: {len(problems)}問")
    print(f"  問題あり: {problem_with_issues}問 ({problem_with_issues/len(problems)*100:.1f}%)")
    print(f"  総指摘事項: {total_issues}件")
    print()
    
    # 品質スコアの計算
    quality_score = (len(problems) - problem_with_issues) / len(problems) * 100
    print(f"  品質スコア: {quality_score:.1f}%")
    
    if quality_score >= 95:
        print("  評価: ✅ 優秀（95%以上）")
    elif quality_score >= 90:
        print("  評価: ✅ 良好（90%以上）")
    elif quality_score >= 80:
        print("  評価: ⚠️ 要改善（80%以上）")
    else:
        print("  評価: ❌ 不合格（80%未満）")
    
    print()
    
    # 問題がある場合は詳細を表示（最初の10件）
    if detailed_results:
        print("=" * 70)
        print("【問題詳細（最初の10件）】")
        print()
        
        for idx, (pid, result) in enumerate(list(detailed_results.items())[:10], 1):
            print(f"{idx}. 問題ID {pid} - {result['category']}")
            print(f"   テーマ: {result['theme']}")
            for issue in result['issues']:
                print(f"   - {issue}")
            print()
    
    # JSON出力
    output = {
        'total_problems': len(problems),
        'problems_with_issues': problem_with_issues,
        'total_issues': total_issues,
        'quality_score': quality_score,
        'category_stats': category_stats,
        'detailed_results': detailed_results
    }
    
    with open('self_review_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print(f"✅ 詳細結果を保存: self_review_results.json")
    print()

if __name__ == '__main__':
    main()

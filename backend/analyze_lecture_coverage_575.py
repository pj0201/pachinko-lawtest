#!/usr/bin/env python3
"""
Analyze coverage of lecture guideline content in 575-question mock exam.
Identifies topics from lecture guidelines that are NOT covered in the 575 questions.
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime

def load_lecture_chunks():
    """Load lecture material chunks"""
    with open('backend/data/lecture_materials_chunks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['chunks']

def load_575_questions():
    """Load 575 questions from mock exam file"""
    with open('sources/遊技機取扱主任者試験 総合模擬問題集.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []
    # Split by question pattern
    question_pattern = r'\d+\.\s+\*\*問題文:\*\*\s+(.*?)(?=\n\d+\.\s+\*\*問題文:\*\*|$)'
    matches = re.findall(question_pattern, content, re.DOTALL)

    for match in matches:
        questions.append(match)

    return questions

def extract_key_terms(text):
    """Extract key terms from text (articles, concepts, technical terms)"""
    terms = []

    # Extract article numbers (第X条)
    articles = re.findall(r'第\d+条(?:の\d+)?', text)
    terms.extend(articles)

    # Extract important keywords (2+ character kanji compounds)
    # Common technical terms in pachinko regulations
    keywords = re.findall(r'[\u4e00-\u9fff]{2,6}(?:営業|業者|遊技機|主任者|規則|法律|認定|検定|管理|届出|申請|許可|登録|製造|販売|設置|保守|点検|基板|部品|交換|不正|改造|試験|講習|資格|証|標章|罰則|違反)', text)
    terms.extend(keywords)

    # Extract standalone important terms
    important_terms = [
        '風営法', '風俗営業', '型式検定', '遊技機取扱主任者', '販売業者', '製造業者',
        '営業許可', '営業所', '管理者', '公安委員会', '保証書', '認定', '検定',
        '中古遊技機', '基板', 'セキュリティ', 'ROM', 'チップ', 'ケース',
        'メダル', 'パチンコ', 'スロット', '射幸心', '景品', 'リサイクル',
        '不正改造', '不正行為', '罰則', '営業停止', '取消し', '届出', '申請',
        'ホッパー', 'コネクタ', 'ユニット', '有効期間', 'システム',
        '遊技場', '営業時間', '禁止区域', '距離制限', '構造設備', '照度'
    ]

    for term in important_terms:
        if term in text:
            terms.append(term)

    return terms

def analyze_coverage():
    """Analyze which lecture topics are covered in 575 questions"""
    print("Loading lecture materials...")
    lecture_chunks = load_lecture_chunks()

    print("Loading 575 questions...")
    questions = load_575_questions()
    question_text = '\n'.join(questions)

    print(f"\nTotal lecture chunks: {len(lecture_chunks)}")
    print(f"Total questions: {len(questions)}")

    # Extract terms from lecture materials
    print("\nExtracting key terms from lecture materials...")
    lecture_terms = Counter()
    lecture_contexts = defaultdict(list)

    for i, chunk in enumerate(lecture_chunks):
        text = chunk.get('text', '')
        terms = extract_key_terms(text)
        for term in set(terms):  # Use set to count each term once per chunk
            lecture_terms[term] += 1
            # Store context (first occurrence only)
            if len(lecture_contexts[term]) < 3:
                preview = text[:150].replace('\n', ' ')
                lecture_contexts[term].append({
                    'pdf': chunk.get('pdf_index', '?'),
                    'page': chunk.get('page_number', '?'),
                    'preview': preview
                })

    # Extract terms from questions
    print("Extracting key terms from questions...")
    question_terms = Counter(extract_key_terms(question_text))

    # Find coverage gaps
    print("\nAnalyzing coverage gaps...")
    gaps = []

    for term, lecture_count in lecture_terms.most_common():
        question_count = question_terms.get(term, 0)

        # Calculate coverage ratio
        if question_count == 0:
            status = 'not_covered'
            gap_ratio = float('inf')
        elif question_count < lecture_count * 0.2:  # Less than 20% coverage
            status = 'low_coverage'
            gap_ratio = lecture_count / question_count
        else:
            status = 'adequate'
            gap_ratio = lecture_count / question_count

        if status in ['not_covered', 'low_coverage']:
            gaps.append({
                'term': term,
                'lecture_frequency': lecture_count,
                'question_frequency': question_count,
                'gap_ratio': gap_ratio if gap_ratio != float('inf') else 'N/A',
                'status': status,
                'contexts': lecture_contexts[term]
            })

    # Sort gaps by priority (uncovered first, then by frequency)
    gaps.sort(key=lambda x: (
        0 if x['status'] == 'not_covered' else 1,
        -x['lecture_frequency']
    ))

    # Generate report
    print("\nGenerating report...")

    report = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'total_lecture_chunks': len(lecture_chunks),
            'total_questions': len(questions),
            'total_lecture_terms': len(lecture_terms),
            'total_question_terms': len(question_terms)
        },
        'statistics': {
            'not_covered_count': sum(1 for g in gaps if g['status'] == 'not_covered'),
            'low_coverage_count': sum(1 for g in gaps if g['status'] == 'low_coverage'),
            'total_gaps': len(gaps)
        },
        'top_lecture_terms': dict(lecture_terms.most_common(30)),
        'top_question_terms': dict(question_terms.most_common(30)),
        'coverage_gaps': gaps[:200]  # Top 200 gaps
    }

    # Save report
    output_file = 'backend/data/lecture_coverage_575_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Analysis complete! Report saved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total lecture terms analyzed: {len(lecture_terms)}")
    print(f"Total question terms found: {len(question_terms)}")
    print(f"\nCoverage Gaps:")
    print(f"  - Not covered at all: {report['statistics']['not_covered_count']} terms")
    print(f"  - Low coverage (<20%): {report['statistics']['low_coverage_count']} terms")
    print(f"  - Total gaps: {report['statistics']['total_gaps']} terms")

    print(f"\nTop 20 Uncovered Terms (from lecture guidelines):")
    uncovered = [g for g in gaps if g['status'] == 'not_covered'][:20]
    for i, gap in enumerate(uncovered, 1):
        print(f"  {i:2}. {gap['term']:20} - appears {gap['lecture_frequency']:3} times in lecture materials")

    print("\n" + "="*60)

    return report

if __name__ == '__main__':
    analyze_coverage()

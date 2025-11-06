#!/usr/bin/env python3
"""
採点・分析エンジン
テスト回答を採点し、カテゴリー別にパフォーマンス分析
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ==================== 採点エンジン ====================

class ScoringEngine:
    """回答の採点と分析"""

    def __init__(self):
        self.results = []

    def score_answer(self, question, user_answer):
        """1問の回答を採点"""
        if not question.get('options'):
            return None

        # ユーザーが選択した選択肢を取得
        selected_option = None
        for opt in question['options']:
            if opt['id'] == user_answer:
                selected_option = opt
                break

        if not selected_option:
            return {
                'question_id': question['id'],
                'is_correct': False,
                'selected': user_answer,
                'correct_answer': None,
                'reason': '選択肢が見つかりません'
            }

        # 正解判定
        is_correct = selected_option.get('isCorrect', False)

        # 正解の選択肢を取得
        correct_options = [opt for opt in question['options'] if opt.get('isCorrect')]
        correct_answer = correct_options[0]['id'] if correct_options else None

        return {
            'question_id': question['id'],
            'category': question.get('category', 'その他'),
            'is_correct': is_correct,
            'selected': user_answer,
            'correct_answer': correct_answer,
            'text': question.get('text', ''),
            'timestamp': datetime.now().isoformat()
        }

    def score_test(self, questions, answers):
        """テスト全体を採点"""
        results = {
            'total_questions': len(questions),
            'answered_questions': len(answers),
            'correct_count': 0,
            'incorrect_count': 0,
            'unanswered_count': len(questions) - len(answers),
            'score_details': [],
            'category_stats': defaultdict(lambda: {
                'total': 0,
                'correct': 0,
                'incorrect': 0,
                'accuracy': 0.0
            })
        }

        # 各問題を採点
        for question in questions:
            question_id = question['id']

            if question_id not in answers:
                # 未回答
                results['score_details'].append({
                    'question_id': question_id,
                    'category': question.get('category', 'その他'),
                    'is_correct': False,
                    'status': 'unanswered'
                })
                continue

            # 採点
            score = self.score_answer(question, answers[question_id])

            if score:
                results['score_details'].append(score)
                category = score.get('category', 'その他')

                # カテゴリー別統計に追加
                results['category_stats'][category]['total'] += 1

                if score['is_correct']:
                    results['correct_count'] += 1
                    results['category_stats'][category]['correct'] += 1
                else:
                    results['incorrect_count'] += 1
                    results['category_stats'][category]['incorrect'] += 1

        # 正答率計算
        if results['answered_questions'] > 0:
            results['accuracy'] = results['correct_count'] / results['answered_questions']
            results['accuracy_percent'] = round(results['accuracy'] * 100)

        # カテゴリー別正答率計算
        for category, stats in results['category_stats'].items():
            if stats['total'] > 0:
                stats['accuracy'] = stats['correct'] / stats['total']
                stats['accuracy_percent'] = round(stats['accuracy'] * 100)

        results['category_stats'] = dict(results['category_stats'])

        return results

# ==================== 分析エンジン ====================

class AnalysisEngine:
    """パフォーマンス分析"""

    @staticmethod
    def analyze_performance(scoring_results):
        """パフォーマンスを分析"""
        analysis = {
            'overall_performance': AnalysisEngine._analyze_overall(scoring_results),
            'category_analysis': AnalysisEngine._analyze_categories(scoring_results),
            'weakness_analysis': AnalysisEngine._analyze_weaknesses(scoring_results),
            'recommendations': AnalysisEngine._generate_recommendations(scoring_results)
        }

        return analysis

    @staticmethod
    def _analyze_overall(results):
        """全体パフォーマンス分析"""
        accuracy = results.get('accuracy_percent', 0)

        if accuracy >= 80:
            level = '優秀'
            message = '素晴らしい成績です！試験合格の可能性が高いです。'
        elif accuracy >= 60:
            level = '良好'
            message = 'まあまあの成績です。弱点を補強すれば合格できます。'
        elif accuracy >= 40:
            level = '要注意'
            message = '要復習です。弱点分析を確認して、集中的に学習してください。'
        else:
            level = '要学習'
            message = '基礎から学び直す必要があります。系統的な学習をお勧めします。'

        return {
            'accuracy_percent': accuracy,
            'level': level,
            'message': message,
            'correct_count': results['correct_count'],
            'total_count': results['total_questions']
        }

    @staticmethod
    def _analyze_categories(results):
        """カテゴリー別分析"""
        category_analysis = {}

        for category, stats in results['category_stats'].items():
            accuracy = stats.get('accuracy_percent', 0)

            if accuracy >= 80:
                level = '得意'
                color = 'green'
            elif accuracy >= 60:
                level = '標準'
                color = 'blue'
            else:
                level = '苦手'
                color = 'red'

            category_analysis[category] = {
                'accuracy_percent': accuracy,
                'level': level,
                'color': color,
                'correct': stats['correct'],
                'total': stats['total'],
                'needs_improvement': accuracy < 70
            }

        return category_analysis

    @staticmethod
    def _analyze_weaknesses(results):
        """弱点分析"""
        weaknesses = []

        # 間違えた問題を集計
        incorrect_by_category = defaultdict(list)

        for detail in results['score_details']:
            if not detail.get('is_correct') and detail.get('status') != 'unanswered':
                category = detail.get('category', 'その他')
                incorrect_by_category[category].append(detail)

        # 弱点をランク付け
        for category, incorrect_list in sorted(
            incorrect_by_category.items(),
            key=lambda x: len(x[1]),
            reverse=True
        ):
            weakness_ratio = len(incorrect_list) / (
                results['category_stats'].get(category, {}).get('total', 1)
            )

            weaknesses.append({
                'category': category,
                'incorrect_count': len(incorrect_list),
                'weakness_ratio': round(weakness_ratio * 100),
                'priority': 'High' if weakness_ratio > 0.5 else 'Medium' if weakness_ratio > 0.3 else 'Low'
            })

        return weaknesses

    @staticmethod
    def _generate_recommendations(results):
        """学習推奨を生成"""
        recommendations = []
        category_stats = results['category_stats']

        # 弱いカテゴリーを特定
        for category, stats in sorted(
            category_stats.items(),
            key=lambda x: x[1]['accuracy_percent']
        ):
            accuracy = stats.get('accuracy_percent', 0)

            if accuracy < 60:
                recommendations.append({
                    'category': category,
                    'priority': 'High',
                    'message': f'【優先】{category}は正答率が{accuracy}%と低いため、集中的な学習が必要です。'
                })
            elif accuracy < 70:
                recommendations.append({
                    'category': category,
                    'priority': 'Medium',
                    'message': f'【推奨】{category}の正答率を70%以上に向上させる学習が必要です。'
                })

        return recommendations

# ==================== データベース格納用フォーマット ====================

class DatabaseFormatter:
    """データベース格納用フォーマット"""

    @staticmethod
    def create_test_record(test_id, questions, answers, user_id='anonymous'):
        """テスト記録を作成"""
        scoring = ScoringEngine()
        scoring_results = scoring.score_test(questions, answers)
        analysis_results = AnalysisEngine.analyze_performance(scoring_results)

        record = {
            'id': test_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'test_data': {
                'total_questions': scoring_results['total_questions'],
                'answered_questions': scoring_results['answered_questions'],
                'unanswered_questions': scoring_results['unanswered_count']
            },
            'scoring': {
                'correct_count': scoring_results['correct_count'],
                'incorrect_count': scoring_results['incorrect_count'],
                'accuracy_percent': scoring_results.get('accuracy_percent', 0)
            },
            'category_scores': scoring_results['category_stats'],
            'analysis': analysis_results,
            'answer_details': scoring_results['score_details']
        }

        return record

    @staticmethod
    def create_bulk_report(test_records):
        """複数テスト記録から統計レポート生成"""
        if not test_records:
            return None

        total_tests = len(test_records)
        accuracies = [r['scoring']['accuracy_percent'] for r in test_records]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0

        category_stats = defaultdict(lambda: {
            'tests': 0,
            'avg_accuracy': 0,
            'trend': []
        })

        for record in test_records:
            for category, stats in record['category_scores'].items():
                category_stats[category]['tests'] += 1
                category_stats[category]['avg_accuracy'] += stats.get('accuracy_percent', 0)
                category_stats[category]['trend'].append(stats.get('accuracy_percent', 0))

        # 平均を計算
        for category in category_stats:
            if category_stats[category]['tests'] > 0:
                category_stats[category]['avg_accuracy'] /= category_stats[category]['tests']

        return {
            'report_date': datetime.now().isoformat(),
            'total_tests': total_tests,
            'average_accuracy': round(avg_accuracy),
            'highest_accuracy': max(accuracies) if accuracies else 0,
            'lowest_accuracy': min(accuracies) if accuracies else 0,
            'category_statistics': dict(category_stats),
            'improvement_areas': [
                cat for cat, stats in category_stats.items()
                if stats['avg_accuracy'] < 70
            ]
        }

# ==================== メイン ====================

if __name__ == '__main__':
    # テスト用サンプルデータ
    sample_questions = [
        {
            'id': 1,
            'category': '法律知識',
            'text': '風俗営業法について正しい説明は？',
            'options': [
                {'id': 'a', 'text': '正しい選択肢', 'isCorrect': True},
                {'id': 'b', 'text': '間違い選択肢', 'isCorrect': False}
            ]
        }
    ]

    sample_answers = {1: 'a'}

    # 採点
    scorer = ScoringEngine()
    results = scorer.score_test(sample_questions, sample_answers)
    print("采点結果:", json.dumps(results, indent=2, ensure_ascii=False))

    # 分析
    analysis = AnalysisEngine.analyze_performance(results)
    print("\n分析結果:", json.dumps(analysis, indent=2, ensure_ascii=False))

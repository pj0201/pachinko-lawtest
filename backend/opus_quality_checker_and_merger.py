#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OPUS品質チェッカー＆統合システム
実装済み問題の品質チェックとOPUS生成問題との統合
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any

class OpusQualityChecker:
    """問題品質チェッククラス"""

    def __init__(self):
        """初期化"""
        self.quality_issues = []
        self.good_problems = []
        self.bad_problems = []

    def check_problem_quality(self, problem: Dict) -> Dict:
        """単一問題の品質チェック"""
        issues = []
        score = 100  # 100点満点から減点方式

        # 問題文の取得
        statement = problem.get('statement', problem.get('problem_text', ''))

        # 1. 文章が途切れているチェック
        if statement.endswith('。'):
            pass  # OK
        elif statement.endswith('で。') or statement.endswith('でも。'):
            issues.append("尻切れトンボ（文章が途切れている）")
            score -= 30
        elif not statement.endswith('。') and not statement.endswith('る') and not statement.endswith('い'):
            issues.append("文末が不自然")
            score -= 20

        # 2. 意味不明な文章チェック
        unclear_patterns = [
            r'について.*でも。?$',  # 「〜について〜でも。」で終わる
            r'の場合において.*必要があり',  # 複雑な条件文
            r'シナリオ',  # 法律に不適切な用語
            r'知識である',  # 「〜は知識である」という不適切な表現
        ]

        for pattern in unclear_patterns:
            if re.search(pattern, statement):
                issues.append(f"意味不明・不適切な表現（パターン: {pattern}）")
                score -= 25
                break

        # 3. 数値の曖昧性チェック
        if re.search(r'\d+日', statement) and '前' not in statement and '後' not in statement and '以内' not in statement:
            # 数値があるのに基準が不明確
            issues.append("数値の基準が不明確")
            score -= 20

        # 4. 法律条文のみの問題チェック
        if re.search(r'^.+は.*第\d+条.*である。?$', statement) and len(statement) < 50:
            issues.append("法律条文のみで具体性に欠ける")
            score -= 15

        # 5. 手続きの具体性チェック
        if '手続き' in statement:
            if not any(word in statement for word in ['届出', '申請', '報告', '承認', '許可', '登録']):
                issues.append("手続きが何か具体的でない")
                score -= 25

        # 6. 解説の有無チェック
        explanation = problem.get('explanation', '')
        if not explanation or len(explanation) < 10:
            issues.append("解説が不十分")
            score -= 15

        # 7. 法的根拠の有無チェック
        source = problem.get('source', problem.get('legal_reference', ''))
        if not source or source == "null" or source == "undefined":
            issues.append("法的根拠なし")
            score -= 10

        # 8. カテゴリの有無チェック
        category = problem.get('category', '')
        if not category:
            issues.append("カテゴリなし")
            score -= 5

        return {
            'problem': problem,
            'score': max(0, score),
            'issues': issues,
            'is_good': score >= 70  # 70点以上を合格とする
        }

    def check_all_problems(self, problems: List[Dict]) -> Dict:
        """全問題の品質チェック"""
        for problem in problems:
            result = self.check_problem_quality(problem)

            if result['is_good']:
                self.good_problems.append(result['problem'])
            else:
                self.bad_problems.append({
                    'problem': result['problem'],
                    'issues': result['issues'],
                    'score': result['score']
                })

        return {
            'total': len(problems),
            'good': len(self.good_problems),
            'bad': len(self.bad_problems),
            'good_rate': (len(self.good_problems) / len(problems) * 100) if problems else 0
        }

class OpusProblemMerger:
    """問題統合クラス"""

    def __init__(self):
        """初期化"""
        self.merged_problems = []

    def convert_opus_to_app_format(self, opus_problem: Dict) -> Dict:
        """OPUS形式をアプリ形式に変換"""
        # 難易度マッピング
        difficulty_map = {
            '★': 'easy',
            '★★': 'medium',
            '★★★': 'hard',
            '★★★★': 'expert'
        }

        # ID生成（q + 4桁の数字）
        problem_id = f"opus_{opus_problem['problem_id']:04d}"

        return {
            'id': problem_id,
            'statement': opus_problem['problem_text'],
            'answer': opus_problem['correct_answer'] == "○",  # ○→True、×→False
            'difficulty': difficulty_map.get(opus_problem.get('difficulty', '★'), 'easy'),
            'category': opus_problem['category'],
            'explanation': opus_problem['explanation'],
            'source': opus_problem.get('legal_reference', '')
        }

    def merge_problems(self, good_existing: List[Dict], opus_problems: List[Dict]) -> List[Dict]:
        """問題の統合"""
        # OPUS問題をアプリ形式に変換
        converted_opus = [self.convert_opus_to_app_format(p) for p in opus_problems]

        # 重複チェック用のセット
        seen_statements = set()
        merged = []

        # OPUS問題を優先的に追加（品質保証済み）
        for problem in converted_opus:
            statement = problem['statement'].strip()
            if statement not in seen_statements:
                merged.append(problem)
                seen_statements.add(statement)

        # 既存の良質な問題を追加
        for problem in good_existing:
            statement = problem.get('statement', '').strip()
            if statement and statement not in seen_statements:
                merged.append(problem)
                seen_statements.add(statement)

                # 900問に達したら終了
                if len(merged) >= 900:
                    break

        # ID再振り分け
        for i, problem in enumerate(merged, 1):
            problem['id'] = f"q{i:04d}"

        return merged

def main():
    """メイン処理"""
    print("🔍 OPUS品質チェッカー＆統合システム起動")
    print("-" * 50)

    # 1. 実装済み問題の読み込み
    print("\n📂 実装済み問題を読み込み中...")
    with open('/home/planj/patshinko-exam-app/public/mock_problems.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    existing_problems = existing_data['problems']
    print(f"✅ {len(existing_problems)}問を読み込みました")

    # 2. 品質チェック
    print("\n🔍 品質チェック実行中...")
    checker = OpusQualityChecker()
    check_result = checker.check_all_problems(existing_problems)

    print(f"\n📊 品質チェック結果:")
    print(f"  総問題数: {check_result['total']}問")
    print(f"  良質: {check_result['good']}問 ({check_result['good_rate']:.1f}%)")
    print(f"  要改善: {check_result['bad']}問")

    # 問題例を表示
    if checker.bad_problems:
        print(f"\n❌ 品質問題の例（最初の3件）:")
        for i, bad in enumerate(checker.bad_problems[:3], 1):
            print(f"\n  例{i}: {bad['problem'].get('statement', '')[:50]}...")
            print(f"  スコア: {bad['score']}点")
            print(f"  問題点: {', '.join(bad['issues'])}")

    # 3. OPUS問題の読み込み
    print("\n📂 OPUS生成問題を読み込み中...")
    with open('/home/planj/patshinko-exam-app/data/opus_300_problems_20251023_114029.json', 'r', encoding='utf-8') as f:
        opus_data = json.load(f)
    opus_problems = opus_data['problems']
    print(f"✅ {len(opus_problems)}問を読み込みました")

    # 4. 問題の統合
    print("\n🔄 問題を統合中...")
    merger = OpusProblemMerger()
    merged_problems = merger.merge_problems(checker.good_problems, opus_problems)

    print(f"✅ 統合完了: {len(merged_problems)}問")

    # 5. カテゴリ分布を計算
    category_dist = {}
    for problem in merged_problems:
        cat = problem.get('category', '不明')
        category_dist[cat] = category_dist.get(cat, 0) + 1

    print("\n📊 最終問題セットの構成:")
    for cat, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(merged_problems)) * 100
        print(f"  {cat}: {count}問 ({percentage:.1f}%)")

    # 6. 保存
    output_data = {
        "metadata": {
            "version": "2.0.0",
            "generator": "OPUS Quality Checker & Merger",
            "created_at": datetime.now().isoformat(),
            "total_problems": len(merged_problems),
            "opus_problems": len(opus_problems),
            "existing_good_problems": len(checker.good_problems),
            "category_distribution": category_dist
        },
        "problems": merged_problems
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'/home/planj/patshinko-exam-app/data/opus_merged_problems_{timestamp}.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 統合済み問題を保存しました:")
    print(f"   {output_file}")

    # アプリ用ファイルも更新
    app_file = '/home/planj/patshinko-exam-app/public/mock_problems_opus_v2.json'
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 アプリ用ファイルも生成しました:")
    print(f"   {app_file}")

    print("\n✅ 処理完了！")


if __name__ == "__main__":
    main()
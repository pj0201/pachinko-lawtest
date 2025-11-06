#!/usr/bin/env python3
"""
Worker3による全問レビュー（1,510問）
品質検証：意味不明・抽象的・重複・正答妥当性
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from difflib import SequenceMatcher

INPUT_FILE = Path("/home/planj/patshinko-exam-app/data/PROBLEMS_FINAL_1491_v2.json")
OUTPUT_REPORT = Path("/tmp/worker3_comprehensive_review.md")

# レビュー基準
ABSTRACT_KEYWORDS = [
    "重要", "必要", "適切", "正しい", "望ましい", "一般的",
    "基本", "原則", "通常", "標準", "通例", "普通"
]

VAGUE_PATTERNS = [
    r"^.{0,30}は、.*である。$",  # 短すぎる問題文
    r"について.*知識.*である",    # 抽象的パターン
    r"について.*理解.*である",    # 抽象的パターン
]

class ComprehensiveReviewer:
    def __init__(self):
        self.problems = []
        self.issues = defaultdict(list)
        self.stats = {}

    def load_data(self):
        """データロード"""
        print("📂 データロード中...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.problems = data['problems']
        self.metadata = data.get('metadata', {})
        print(f"  ✅ {len(self.problems)}問をロード")

    def check_meaningless(self):
        """意味不明な問題の検出"""
        print("\n🔍 意味不明な問題文の検出中...")

        for p in self.problems:
            text = p.get('problem_text', '')
            pid = p.get('problem_id')

            # 極端に短い
            if len(text) < 20:
                self.issues['too_short'].append({
                    'id': pid,
                    'text': text,
                    'reason': f'問題文が短すぎる（{len(text)}文字）'
                })

            # 極端に長い
            if len(text) > 500:
                self.issues['too_long'].append({
                    'id': pid,
                    'text': text[:100] + '...',
                    'reason': f'問題文が長すぎる（{len(text)}文字）'
                })

            # 句読点なし
            if len(text) > 50 and '、' not in text and '。' not in text:
                self.issues['no_punctuation'].append({
                    'id': pid,
                    'text': text[:100],
                    'reason': '句読点が不足'
                })

            # 意味不明な文字列
            if re.search(r'[{}【】\[\]]', text):
                self.issues['template_residue'].append({
                    'id': pid,
                    'text': text,
                    'reason': 'テンプレート残骸の可能性'
                })

        print(f"  ⚠️  短すぎる問題: {len(self.issues['too_short'])}問")
        print(f"  ⚠️  長すぎる問題: {len(self.issues['too_long'])}問")
        print(f"  ⚠️  句読点不足: {len(self.issues['no_punctuation'])}問")
        print(f"  ⚠️  テンプレート残骸: {len(self.issues['template_residue'])}問")

    def check_abstract(self):
        """抽象的すぎる問題の検出"""
        print("\n🔍 抽象的すぎる問題文の検出中...")

        for p in self.problems:
            text = p.get('problem_text', '')
            pid = p.get('problem_id')

            # 抽象キーワードカウント
            abstract_count = sum(1 for kw in ABSTRACT_KEYWORDS if kw in text)

            if abstract_count >= 3:
                self.issues['too_abstract'].append({
                    'id': pid,
                    'text': text,
                    'reason': f'抽象的キーワードが多い（{abstract_count}個）',
                    'keywords': [kw for kw in ABSTRACT_KEYWORDS if kw in text]
                })

            # 曖昧パターン
            for pattern in VAGUE_PATTERNS:
                if re.match(pattern, text):
                    self.issues['vague_pattern'].append({
                        'id': pid,
                        'text': text,
                        'reason': f'曖昧なパターン（{pattern}）'
                    })
                    break

        print(f"  ⚠️  抽象的すぎる: {len(self.issues['too_abstract'])}問")
        print(f"  ⚠️  曖昧パターン: {len(self.issues['vague_pattern'])}問")

    def check_specificity(self):
        """具体性の検証"""
        print("\n🔍 具体性の欠如を検出中...")

        for p in self.problems:
            text = p.get('problem_text', '')
            pid = p.get('problem_id')

            # 具体的な要素の有無チェック
            has_number = bool(re.search(r'\d+', text))
            has_specific_term = bool(re.search(r'(第\d+条|公安委員会|風営法|検定|型式|遊技機|営業所)', text))
            has_action = bool(re.search(r'(設置|交換|申請|届出|確認|点検|管理|報告)', text))

            specificity_score = sum([has_number, has_specific_term, has_action])

            if specificity_score == 0:
                self.issues['no_specificity'].append({
                    'id': pid,
                    'text': text,
                    'reason': '具体的要素が皆無'
                })
            elif specificity_score == 1:
                self.issues['low_specificity'].append({
                    'id': pid,
                    'text': text,
                    'reason': '具体性が低い'
                })

        print(f"  ⚠️  具体性皆無: {len(self.issues['no_specificity'])}問")
        print(f"  ⚠️  具体性低: {len(self.issues['low_specificity'])}問")

    def check_duplicates(self):
        """重複の再確認（高類似度）"""
        print("\n🔍 高類似度問題の検出中（90%以上）...")

        duplicate_pairs = []

        for i, p1 in enumerate(self.problems):
            if i % 200 == 0:
                print(f"  進捗: {i}/{len(self.problems)}問")

            text1 = p1.get('problem_text', '')
            id1 = p1.get('problem_id')

            for p2 in self.problems[i+1:]:
                text2 = p2.get('problem_text', '')
                id2 = p2.get('problem_id')

                similarity = SequenceMatcher(None, text1, text2).ratio()

                if similarity >= 0.90:
                    duplicate_pairs.append({
                        'id1': id1,
                        'id2': id2,
                        'similarity': similarity,
                        'text1': text1,
                        'text2': text2
                    })

        self.issues['high_similarity'] = duplicate_pairs
        print(f"  ⚠️  高類似度（90%+）: {len(duplicate_pairs)}ペア")

    def check_answers(self):
        """正答・解説の妥当性検証"""
        print("\n🔍 正答・解説の妥当性検証中...")

        for p in self.problems:
            pid = p.get('problem_id')
            answer = p.get('correct_answer')
            explanation = p.get('explanation', '')
            text = p.get('problem_text', '')

            # 正答が未設定
            if not answer:
                self.issues['no_answer'].append({
                    'id': pid,
                    'text': text,
                    'reason': '正答が未設定'
                })

            # 正答が○×以外
            if answer not in ['○', '×']:
                self.issues['invalid_answer'].append({
                    'id': pid,
                    'text': text,
                    'answer': answer,
                    'reason': f'不正な正答形式（{answer}）'
                })

            # 解説が短すぎる
            if len(explanation) < 10:
                self.issues['short_explanation'].append({
                    'id': pid,
                    'text': text,
                    'explanation': explanation,
                    'reason': f'解説が短すぎる（{len(explanation)}文字）'
                })

            # 解説がテンプレート的
            if '正確に理解' in explanation or '基本です' in explanation:
                self.issues['template_explanation'].append({
                    'id': pid,
                    'text': text[:50],
                    'explanation': explanation,
                    'reason': 'テンプレート的解説'
                })

        print(f"  ⚠️  正答未設定: {len(self.issues['no_answer'])}問")
        print(f"  ⚠️  不正な正答: {len(self.issues['invalid_answer'])}問")
        print(f"  ⚠️  解説短すぎ: {len(self.issues['short_explanation'])}問")
        print(f"  ⚠️  テンプレート解説: {len(self.issues['template_explanation'])}問")

    def check_distribution(self):
        """カテゴリ・テーマ分布の検証"""
        print("\n🔍 カテゴリ・テーマ分布の検証中...")

        categories = Counter(p.get('category') for p in self.problems)
        themes = Counter(p.get('theme_name') for p in self.problems)
        difficulties = Counter(p.get('difficulty') for p in self.problems)

        self.stats['categories'] = dict(categories)
        self.stats['themes'] = dict(themes)
        self.stats['difficulties'] = dict(difficulties)

        print(f"\n📊 カテゴリ分布:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}問 ({count/len(self.problems)*100:.1f}%)")

        print(f"\n📊 難易度分布:")
        for diff, count in sorted(difficulties.items()):
            print(f"  {diff}: {count}問 ({count/len(self.problems)*100:.1f}%)")

        print(f"\n📊 テーマ数: {len(themes)}テーマ")

        # 0問テーマの検出
        zero_themes = [theme for theme, count in themes.items() if count == 0]
        if zero_themes:
            self.issues['zero_themes'] = zero_themes
            print(f"  ⚠️  0問テーマ: {len(zero_themes)}テーマ")

    def generate_report(self):
        """レビューレポート生成"""
        print("\n📋 レポート生成中...")

        report = "# Worker3 全問レビューレポート（1,510問）\n\n"
        report += "**レビュー日**: 2025-10-22\n"
        report += "**レビュアー**: Worker3（Claude Code - Sonnet 4.5）\n"
        report += f"**対象**: {len(self.problems)}問\n\n"
        report += "---\n\n"

        # 総合評価
        total_issues = sum(len(v) if isinstance(v, list) else 0 for v in self.issues.values())

        report += "## ✅ 総合評価\n\n"

        if total_issues == 0:
            report += "**判定**: ✅ **EXCELLENT - 問題なし**\n\n"
        elif total_issues < 50:
            report += f"**判定**: 🟡 **GOOD - 軽微な問題あり（{total_issues}件）**\n\n"
        elif total_issues < 200:
            report += f"**判定**: ⚠️ **WARNING - 要改善（{total_issues}件）**\n\n"
        else:
            report += f"**判定**: ❌ **CRITICAL - 重大問題（{total_issues}件）**\n\n"

        report += f"**検出された問題総数**: {total_issues}件\n\n"
        report += "---\n\n"

        # カテゴリ別問題数
        report += "## 📊 検出された問題の内訳\n\n"
        report += "| カテゴリ | 件数 | 重要度 |\n"
        report += "|---------|------|--------|\n"

        issue_categories = {
            'template_residue': ('テンプレート残骸', '🔴 HIGH'),
            'no_answer': ('正答未設定', '🔴 HIGH'),
            'invalid_answer': ('不正な正答', '🔴 HIGH'),
            'high_similarity': ('高類似度（90%+）', '🔴 HIGH'),
            'no_specificity': ('具体性皆無', '🟡 MEDIUM'),
            'too_abstract': ('抽象的すぎ', '🟡 MEDIUM'),
            'vague_pattern': ('曖昧パターン', '🟡 MEDIUM'),
            'low_specificity': ('具体性低', '🟢 LOW'),
            'short_explanation': ('解説短すぎ', '🟢 LOW'),
            'template_explanation': ('テンプレート解説', '🟢 LOW'),
            'too_short': ('問題文短すぎ', '🟢 LOW'),
            'too_long': ('問題文長すぎ', '🟢 LOW'),
            'no_punctuation': ('句読点不足', '🟢 LOW'),
        }

        for key, (name, priority) in issue_categories.items():
            count = len(self.issues.get(key, []))
            if count > 0:
                report += f"| {name} | {count}件 | {priority} |\n"

        report += "\n---\n\n"

        # 詳細セクション
        report += "## 🔍 問題詳細\n\n"

        # HIGH優先度の問題を詳細表示
        if self.issues['template_residue']:
            report += "### 🔴 HIGH: テンプレート残骸\n\n"
            for issue in self.issues['template_residue'][:10]:
                report += f"**問題ID {issue['id']}**:\n"
                report += f"- 問題文: {issue['text']}\n"
                report += f"- 理由: {issue['reason']}\n\n"
            if len(self.issues['template_residue']) > 10:
                report += f"*（残り{len(self.issues['template_residue'])-10}件）*\n\n"

        if self.issues['high_similarity']:
            report += "### 🔴 HIGH: 高類似度問題（90%以上）\n\n"
            for pair in self.issues['high_similarity'][:10]:
                report += f"**問題ID {pair['id1']} ⇔ {pair['id2']}** (類似度: {pair['similarity']:.2%})\n"
                report += f"- 問題1: {pair['text1'][:100]}...\n"
                report += f"- 問題2: {pair['text2'][:100]}...\n\n"
            if len(self.issues['high_similarity']) > 10:
                report += f"*（残り{len(self.issues['high_similarity'])-10}ペア）*\n\n"

        # 統計情報
        report += "---\n\n"
        report += "## 📊 統計情報\n\n"

        report += "### カテゴリ分布\n\n"
        for cat, count in sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True):
            report += f"- {cat}: {count}問 ({count/len(self.problems)*100:.1f}%)\n"

        report += "\n### 難易度分布\n\n"
        for diff, count in sorted(self.stats['difficulties'].items()):
            report += f"- {diff}: {count}問 ({count/len(self.problems)*100:.1f}%)\n"

        report += f"\n### テーマ数\n\n"
        report += f"- 総テーマ数: {len(self.stats['themes'])}テーマ\n"

        # 最終判定
        report += "\n---\n\n"
        report += "## 🎯 最終判定\n\n"

        critical_issues = (
            len(self.issues['template_residue']) +
            len(self.issues['no_answer']) +
            len(self.issues['invalid_answer'])
        )

        if critical_issues == 0 and len(self.issues['high_similarity']) == 0:
            report += "**本番投入**: ✅ **可能**\n\n"
            report += "重大な問題は検出されませんでした。\n"
        elif critical_issues < 10:
            report += "**本番投入**: 🟡 **条件付き可能**\n\n"
            report += f"軽微な問題（{critical_issues}件）の修正後、本番投入可能です。\n"
        else:
            report += "**本番投入**: ❌ **要修正**\n\n"
            report += f"重大な問題（{critical_issues}件）の修正が必要です。\n"

        report += "\n---\n\n"
        report += "**レビュアー**: Worker3（Claude Code - Sonnet 4.5）\n"
        report += "**レビュー日時**: 2025-10-22\n"

        # レポート保存
        with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"  ✅ レポート保存: {OUTPUT_REPORT}")

    def run(self):
        """レビュー実行"""
        print("=" * 80)
        print("Worker3 全問レビュー（1,510問）")
        print("=" * 80)

        self.load_data()
        self.check_meaningless()
        self.check_abstract()
        self.check_specificity()
        self.check_duplicates()
        self.check_answers()
        self.check_distribution()
        self.generate_report()

        print("\n" + "=" * 80)
        print("✅ レビュー完了！")
        print("=" * 80)


if __name__ == '__main__':
    reviewer = ComprehensiveReviewer()
    reviewer.run()

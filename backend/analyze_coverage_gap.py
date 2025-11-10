#!/usr/bin/env python3
"""
試験問題のカバレッジギャップ分析スクリプト

目的：
- 講義資料（①②③.pdf）のOCR結果
- 風営法・風営法施行規則
- 既存の試験問題（638問 or 230問）
を分析し、ソース資料の内容が問題でカバーされているかを確認
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import sys

class CoverageGapAnalyzer:
    """カバレッジギャップ分析エンジン"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.problems = []
        self.lecture_chunks = []
        self.ocr_pages = []

        # 分析結果
        self.source_topics = defaultdict(list)
        self.problem_topics = defaultdict(list)
        self.coverage_gaps = []

    def load_problems(self):
        """試験問題を読み込む"""
        print("📖 試験問題を読み込み中...")

        problems_file = self.base_dir / "data" / "problems.json"
        with open(problems_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.problems = data.get('problems', [])

        print(f"   ✅ 問題数: {len(self.problems)}問")

        # カテゴリ別統計
        categories = Counter([p.get('category', 'unknown') for p in self.problems])
        print(f"   カテゴリ別:")
        for cat, count in categories.most_common():
            print(f"      - {cat}: {count}問")

        return len(self.problems)

    def load_lecture_materials(self):
        """講義資料チャンクを読み込む"""
        print("\n📚 講義資料を読み込み中...")

        chunks_file = self.base_dir / "backend" / "data" / "lecture_materials_chunks.json"
        if not chunks_file.exists():
            print("   ⚠️ チャンクファイルが見つかりません")
            return 0

        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.lecture_chunks = data.get('chunks', [])

        print(f"   ✅ チャンク数: {len(self.lecture_chunks)}")

        # PDF別統計
        pdf_dist = Counter([c.get('pdf_index') for c in self.lecture_chunks])
        for pdf_idx, count in sorted(pdf_dist.items()):
            print(f"      - PDF{pdf_idx}: {count}チャンク")

        return len(self.lecture_chunks)

    def load_ocr_pages(self):
        """OCRページデータを読み込む"""
        print("\n📄 OCRページデータを読み込み中...")

        ocr_file = self.base_dir / "data" / "old_problems" / "ocr_results_corrected.json"
        with open(ocr_file, 'r', encoding='utf-8') as f:
            self.ocr_pages = json.load(f)

        print(f"   ✅ ページ数: {len(self.ocr_pages)}")
        return len(self.ocr_pages)

    def extract_keywords_from_text(self, text, min_length=3):
        """テキストからキーワードを抽出"""
        # 重要なキーワードパターン
        patterns = [
            r'第\d+条(?:の\d+)?',  # 条文番号
            r'[一二三四五六七八九十百千]+条',  # 漢数字の条文
            r'遊技機取扱主任者',
            r'風営法',
            r'風俗営業',
            r'型式検定',
            r'認定',
            r'検査',
            r'保守管理',
            r'不正[改造|使用|行為]',
            r'営業[許可|停止|時間]',
            r'罰則',
            r'景品',
            r'射幸心',
            r'登録制度',
            r'販売業者',
            r'製造業者',
            r'中古遊技機',
            r'新規[試験|講習]',
            r'更新[試験|講習]',
            r'有効期間',
            r'保証書',
            r'セキュリティ',
            r'チップ',
            r'基板',
            r'リサイクル',
            r'廃棄物',
        ]

        keywords = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches)

        # 追加：名詞句抽出（簡易版）
        # カタカナ語
        katakana_words = re.findall(r'[ァ-ヶー]{3,}', text)
        keywords.extend(katakana_words)

        return list(set(keywords))

    def analyze_lecture_topics(self):
        """講義資料のトピックを分析"""
        print("\n🔍 講義資料のトピックを分析中...")

        topic_frequency = Counter()
        topic_locations = defaultdict(list)

        for i, chunk in enumerate(self.lecture_chunks):
            text = chunk.get('text', '')
            pdf_idx = chunk.get('pdf_index')
            page_num = chunk.get('page_number')

            keywords = self.extract_keywords_from_text(text)

            for keyword in keywords:
                topic_frequency[keyword] += 1
                topic_locations[keyword].append({
                    'pdf': pdf_idx,
                    'page': page_num,
                    'chunk_index': i
                })

        # トップ50トピックを保存
        self.source_topics = dict(topic_frequency.most_common(50))

        print(f"   ✅ 検出されたトピック: {len(topic_frequency)}")
        print(f"\n   トップ10トピック:")
        for topic, count in topic_frequency.most_common(10):
            print(f"      - {topic}: {count}回")

        return topic_frequency, topic_locations

    def analyze_problem_topics(self):
        """試験問題のトピックを分析"""
        print("\n🔍 試験問題のトピックを分析中...")

        topic_frequency = Counter()

        for problem in self.problems:
            question = problem.get('question', '')
            options = ' '.join([opt.get('text', '') for opt in problem.get('options', [])])
            explanation = problem.get('explanation', '')

            full_text = f"{question} {options} {explanation}"
            keywords = self.extract_keywords_from_text(full_text)

            for keyword in keywords:
                topic_frequency[keyword] += 1

        self.problem_topics = dict(topic_frequency.most_common(50))

        print(f"   ✅ 問題に含まれるトピック: {len(topic_frequency)}")
        print(f"\n   トップ10トピック:")
        for topic, count in topic_frequency.most_common(10):
            print(f"      - {topic}: {count}回")

        return topic_frequency

    def identify_coverage_gaps(self, lecture_topics, problem_topics):
        """カバレッジギャップを特定"""
        print("\n🔎 カバレッジギャップを特定中...")

        gaps = []

        # ソースにあるが問題にないトピック
        source_only = set(lecture_topics.keys()) - set(problem_topics.keys())

        # 頻度が高いのに問題が少ないトピック
        for topic, source_count in lecture_topics.items():
            problem_count = problem_topics.get(topic, 0)

            # ソースで10回以上出現するが、問題では3回以下
            if source_count >= 10 and problem_count <= 3:
                gaps.append({
                    'topic': topic,
                    'source_frequency': source_count,
                    'problem_frequency': problem_count,
                    'gap_ratio': source_count / max(problem_count, 1),
                    'status': 'under_represented'
                })

        # ソースのみに存在（問題で全く扱われていない）
        for topic in source_only:
            if lecture_topics[topic] >= 5:  # 5回以上出現
                gaps.append({
                    'topic': topic,
                    'source_frequency': lecture_topics[topic],
                    'problem_frequency': 0,
                    'gap_ratio': float('inf'),
                    'status': 'not_covered'
                })

        # ギャップ率でソート
        gaps.sort(key=lambda x: x['gap_ratio'] if x['gap_ratio'] != float('inf') else 999999, reverse=True)

        self.coverage_gaps = gaps

        print(f"   ✅ 検出されたギャップ: {len(gaps)}トピック")

        return gaps

    def generate_report(self):
        """レポート生成"""
        print("\n📊 レポート生成中...")

        report = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_problems': len(self.problems),
                'total_lecture_chunks': len(self.lecture_chunks),
                'total_ocr_pages': len(self.ocr_pages)
            },
            'statistics': {
                'source_topics_count': len(self.source_topics),
                'problem_topics_count': len(self.problem_topics),
                'coverage_gaps_count': len(self.coverage_gaps)
            },
            'top_source_topics': dict(list(self.source_topics.items())[:20]),
            'top_problem_topics': dict(list(self.problem_topics.items())[:20]),
            'coverage_gaps': self.coverage_gaps[:30],  # トップ30ギャップ
            'recommendations': self._generate_recommendations()
        }

        # レポート保存
        output_file = self.base_dir / "backend" / "data" / "coverage_gap_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"   ✅ レポート保存: {output_file}")

        return report

    def _generate_recommendations(self):
        """推奨事項を生成"""
        recommendations = []

        # 未カバートピック
        not_covered = [g for g in self.coverage_gaps if g['status'] == 'not_covered']
        if not_covered:
            recommendations.append({
                'priority': 'high',
                'category': '未カバートピック',
                'count': len(not_covered),
                'description': f'{len(not_covered)}個のトピックがソース資料に存在するが、試験問題で全く扱われていません。',
                'action': 'これらのトピックに関する問題を新規作成することを推奨します。',
                'examples': [g['topic'] for g in not_covered[:5]]
            })

        # 低カバレッジトピック
        under_rep = [g for g in self.coverage_gaps if g['status'] == 'under_represented']
        if under_rep:
            recommendations.append({
                'priority': 'medium',
                'category': '低カバレッジトピック',
                'count': len(under_rep),
                'description': f'{len(under_rep)}個のトピックがソース資料で頻出するが、試験問題での出現頻度が低いです。',
                'action': 'これらのトピックに関する問題を追加することを推奨します。',
                'examples': [g['topic'] for g in under_rep[:5]]
            })

        return recommendations

    def print_summary(self, report):
        """サマリー出力"""
        print("\n" + "=" * 70)
        print("📊 カバレッジギャップ分析サマリー")
        print("=" * 70)

        print(f"\n【データ統計】")
        print(f"  試験問題数: {report['metadata']['total_problems']}問")
        print(f"  講義資料チャンク数: {report['metadata']['total_lecture_chunks']}")
        print(f"  OCRページ数: {report['metadata']['total_ocr_pages']}")

        print(f"\n【トピック分析】")
        print(f"  ソーストピック数: {report['statistics']['source_topics_count']}")
        print(f"  問題トピック数: {report['statistics']['problem_topics_count']}")
        print(f"  検出されたギャップ: {report['statistics']['coverage_gaps_count']}")

        print(f"\n【トップ10ギャップ】")
        for i, gap in enumerate(report['coverage_gaps'][:10], 1):
            status_icon = "❌" if gap['status'] == 'not_covered' else "⚠️"
            print(f"  {i}. {status_icon} {gap['topic']}")
            print(f"      ソース: {gap['source_frequency']}回, 問題: {gap['problem_frequency']}回")

        print(f"\n【推奨事項】")
        for rec in report['recommendations']:
            icon = "🔴" if rec['priority'] == 'high' else "🟡"
            print(f"\n  {icon} {rec['category']} (優先度: {rec['priority'].upper()})")
            print(f"     {rec['description']}")
            print(f"     アクション: {rec['action']}")
            print(f"     例: {', '.join(rec['examples'][:3])}")

        print("\n" + "=" * 70)

    def run(self):
        """メイン実行"""
        print("=" * 70)
        print("🚀 試験問題カバレッジギャップ分析を開始")
        print("=" * 70)

        try:
            # データ読み込み
            self.load_problems()
            self.load_lecture_materials()
            self.load_ocr_pages()

            # トピック分析
            lecture_topics, _ = self.analyze_lecture_topics()
            problem_topics = self.analyze_problem_topics()

            # ギャップ特定
            self.identify_coverage_gaps(lecture_topics, problem_topics)

            # レポート生成
            report = self.generate_report()

            # サマリー表示
            self.print_summary(report)

            print("\n✅ 分析完了")
            return True

        except Exception as e:
            print(f"\n❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    analyzer = CoverageGapAnalyzer()
    success = analyzer.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

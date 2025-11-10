#!/usr/bin/env python3
"""
正しい246問の試験問題を使用したカバレッジギャップ分析

6つのソースファイル:
1. 講義資料①.pdf
2. 講義資料②.pdf
3. 講義資料③.pdf
4. 風営法.pdf
5. 風営法施行規則.pdf
6. 遊技機取扱主任者に関する規定 + 実施要領
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import sys

class DetailedCoverageAnalyzer:
    """詳細カバレッジ分析（246問版）"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.problems = []
        self.ocr_pages = []

        # ソースファイル別のトピック
        self.source_topics = {
            'lecture_1': defaultdict(list),  # ①.pdf
            'lecture_2': defaultdict(list),  # ②.pdf
            'lecture_3': defaultdict(list),  # ③.pdf
            'fueiho': defaultdict(list),     # 風営法
            'fueiho_rules': defaultdict(list),  # 風営法施行規則
            'supervisor_rules': defaultdict(list)  # 主任者規定
        }

        self.problem_covered_topics = set()
        self.uncovered_items = []

    def load_problems(self):
        """正しい246問を読み込む"""
        print("📖 試験問題（246問）を読み込み中...")

        problems_file = self.base_dir / "backend" / "db" / "problems.json"
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
        """講義資料（①②③）を読み込む"""
        print("\n📚 講義資料（①②③.pdf）を読み込み中...")

        ocr_file = self.base_dir / "data" / "old_problems" / "ocr_results_corrected.json"
        with open(ocr_file, 'r', encoding='utf-8') as f:
            self.ocr_pages = json.load(f)

        # PDF別に分類
        pdf_counts = Counter([p.get('pdf_index') for p in self.ocr_pages])
        print(f"   ✅ 総ページ数: {len(self.ocr_pages)}")
        for pdf_idx in sorted(pdf_counts.keys()):
            print(f"      - PDF{pdf_idx}: {pdf_counts[pdf_idx]}ページ")

        return len(self.ocr_pages)

    def extract_structured_topics(self, text, source_type):
        """テキストから構造化されたトピックを抽出"""
        topics = []

        # 1. 章・節の抽出
        chapter_patterns = [
            r'第[一二三四五六七八九十百千]+章\s+([^\n]+)',
            r'第\d+章\s+([^\n]+)',
        ]
        for pattern in chapter_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                topics.append({
                    'type': 'chapter',
                    'content': match.strip(),
                    'source': source_type
                })

        # 2. 条文の抽出
        article_patterns = [
            r'第(\d+)条(?:の(\d+))?\s+([^\n]{10,100})',
            r'第([一二三四五六七八九十百千]+)条\s+([^\n]{10,100})',
        ]
        for pattern in article_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    article_num = match[0]
                    sub_num = match[1] if match[1] else ""
                    content = match[2]
                    topics.append({
                        'type': 'article',
                        'article_number': f"第{article_num}条{sub_num}",
                        'content': content.strip()[:100],
                        'source': source_type
                    })

        # 3. 重要なキーワード・概念
        key_concepts = [
            # 制度関連
            (r'遊技機取扱主任者(?:の|に関する)([^\n。]{10,80})', 'supervisor_system'),
            (r'販売業者登録制度([^\n。]{10,80})', 'seller_registration'),
            (r'製造業者([^\n。]{10,80})', 'manufacturer'),
            (r'認定(?:申請|手続|証)([^\n。]{10,80})', 'certification'),
            (r'型式検定([^\n。]{10,80})', 'type_inspection'),

            # 手続き関連
            (r'保証書([^\n。]{10,80})', 'warranty_document'),
            (r'検査([^\n。]{10,80})', 'inspection'),
            (r'届出([^\n。]{10,80})', 'notification'),
            (r'申請(?:書|手続)([^\n。]{10,80})', 'application'),

            # 技術基準
            (r'射幸心([^\n。]{10,80})', 'gambling_nature'),
            (r'性能基準([^\n。]{10,80})', 'performance_standard'),
            (r'技術基準([^\n。]{10,80})', 'technical_standard'),
            (r'セキュリティ([^\n。]{10,80})', 'security'),
            (r'基板(?:の|に関する)([^\n。]{10,80})', 'circuit_board'),
            (r'チップ(?:の|に関する)([^\n。]{10,80})', 'chip'),

            # 業務・実務
            (r'保守管理([^\n。]{10,80})', 'maintenance'),
            (r'不正(?:改造|使用|行為)([^\n。]{10,80})', 'fraud'),
            (r'中古遊技機([^\n。]{10,80})', 'used_machine'),
            (r'リサイクル([^\n。]{10,80})', 'recycling'),

            # 罰則・義務
            (r'罰則([^\n。]{10,80})', 'penalty'),
            (r'営業停止([^\n。]{10,80})', 'business_suspension'),
            (r'取消し([^\n。]{10,80})', 'cancellation'),
            (r'遵守事項([^\n。]{10,80})', 'compliance'),
        ]

        for pattern, concept_type in key_concepts:
            matches = re.findall(pattern, text)
            for match in matches:
                topics.append({
                    'type': 'concept',
                    'concept_type': concept_type,
                    'content': match.strip(),
                    'source': source_type
                })

        return topics

    def analyze_source_content(self):
        """各ソースファイルの内容を分析"""
        print("\n🔍 ソースファイルの内容を分析中...")

        # 講義資料の分析
        for page in self.ocr_pages:
            pdf_idx = page.get('pdf_index')
            text = page.get('text', '')

            source_key = f'lecture_{pdf_idx}'
            topics = self.extract_structured_topics(text, source_key)

            for topic in topics:
                key = f"{topic['type']}:{topic.get('article_number', topic.get('concept_type', 'other'))}"
                self.source_topics[source_key][key].append({
                    'page': page.get('page_number'),
                    'content': topic.get('content', '')[:100]
                })

        # 統計表示
        print(f"\n   ソース別トピック数:")
        for source, topics in self.source_topics.items():
            if topics:
                print(f"      - {source}: {len(topics)}トピック")

        return self.source_topics

    def analyze_problem_coverage(self):
        """問題がカバーしているトピックを分析"""
        print("\n🔍 問題のカバー内容を分析中...")

        for problem in self.problems:
            question = problem.get('question', '')
            options = ' '.join([opt.get('text', '') for opt in problem.get('options', [])])
            explanation = problem.get('explanation', '')

            full_text = f"{question} {options} {explanation}"

            # カバーしているトピックを抽出
            topics = self.extract_structured_topics(full_text, 'problem')
            for topic in topics:
                key = f"{topic['type']}:{topic.get('article_number', topic.get('concept_type', 'other'))}"
                self.problem_covered_topics.add(key)

        print(f"   ✅ 問題がカバーしているトピック: {len(self.problem_covered_topics)}")
        return self.problem_covered_topics

    def identify_uncovered_content(self):
        """未カバーの内容を特定"""
        print("\n🔎 未カバー内容を特定中...")

        uncovered = []

        for source_name, topics in self.source_topics.items():
            for topic_key, occurrences in topics.items():
                if topic_key not in self.problem_covered_topics:
                    # 出現頻度でフィルタ（2回以上出現）
                    if len(occurrences) >= 2:
                        uncovered.append({
                            'source': source_name,
                            'topic_key': topic_key,
                            'frequency': len(occurrences),
                            'pages': [occ['page'] for occ in occurrences[:5]],
                            'sample_content': occurrences[0]['content'] if occurrences else ''
                        })

        # 頻度でソート
        uncovered.sort(key=lambda x: x['frequency'], reverse=True)
        self.uncovered_items = uncovered

        print(f"   ✅ 未カバー項目: {len(uncovered)}")
        return uncovered

    def generate_detailed_report(self):
        """詳細レポート生成"""
        print("\n📊 詳細レポート生成中...")

        # ソース別に未カバー項目をグループ化
        by_source = defaultdict(list)
        for item in self.uncovered_items:
            by_source[item['source']].append(item)

        report_lines = [
            "# 遊技機取扱主任者試験 カバレッジギャップ詳細分析",
            "",
            f"**分析日時**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**試験問題数**: {len(self.problems)}問",
            f"**ソースページ数**: {len(self.ocr_pages)}ページ",
            "",
            "---",
            "",
            "## 📊 分析サマリー",
            "",
            f"- **問題がカバーしているトピック**: {len(self.problem_covered_topics)}",
            f"- **未カバーの項目**: {len(self.uncovered_items)}",
            "",
        ]

        # ソース別の詳細
        for source_name in ['lecture_1', 'lecture_2', 'lecture_3']:
            items = by_source.get(source_name, [])
            if not items:
                continue

            pdf_num = source_name.split('_')[1]
            report_lines.extend([
                "",
                f"## 📄 講義資料{['①', '②', '③'][int(pdf_num)-1]}の未カバー内容",
                "",
                f"**未カバー項目数**: {len(items)}",
                ""
            ])

            # トピックタイプ別にグループ化
            by_type = defaultdict(list)
            for item in items:
                topic_type = item['topic_key'].split(':')[0]
                by_type[topic_type].append(item)

            # 条文
            if by_type['article']:
                report_lines.extend([
                    "### 📜 未カバーの条文",
                    "",
                    "| 条文 | 出現回数 | ページ | 内容サンプル |",
                    "|------|---------|--------|------------|"
                ])
                for item in sorted(by_type['article'], key=lambda x: x['frequency'], reverse=True)[:20]:
                    article = item['topic_key'].split(':')[1]
                    pages = ', '.join([f"p{p}" for p in item['pages'][:3]])
                    content = item['sample_content'][:50]
                    report_lines.append(f"| {article} | {item['frequency']}回 | {pages} | {content}... |")
                report_lines.append("")

            # 概念
            if by_type['concept']:
                report_lines.extend([
                    "### 💡 未カバーの重要概念",
                    "",
                    "| 概念 | 出現回数 | ページ | 内容サンプル |",
                    "|------|---------|--------|------------|"
                ])
                for item in sorted(by_type['concept'], key=lambda x: x['frequency'], reverse=True)[:20]:
                    concept = item['topic_key'].split(':')[1]
                    pages = ', '.join([f"p{p}" for p in item['pages'][:3]])
                    content = item['sample_content'][:50]
                    report_lines.append(f"| {concept} | {item['frequency']}回 | {pages} | {content}... |")
                report_lines.append("")

            # 章
            if by_type['chapter']:
                report_lines.extend([
                    "### 📖 未カバーの章・節",
                    "",
                    "| 章・節 | 出現回数 | ページ |",
                    "|--------|---------|--------|"
                ])
                for item in sorted(by_type['chapter'], key=lambda x: x['frequency'], reverse=True)[:10]:
                    chapter = item['topic_key'].split(':')[1]
                    pages = ', '.join([f"p{p}" for p in item['pages'][:3]])
                    report_lines.append(f"| {chapter} | {item['frequency']}回 | {pages} |")
                report_lines.append("")

        # 推奨アクション
        report_lines.extend([
            "",
            "## 🎯 推奨される問題作成",
            "",
            "### 優先度：HIGH（出現5回以上）",
            ""
        ])

        high_priority = [item for item in self.uncovered_items if item['frequency'] >= 5]
        for i, item in enumerate(high_priority[:20], 1):
            source_label = item['source'].replace('lecture_', '講義資料')
            if 'lecture' in item['source']:
                pdf_num = item['source'].split('_')[1]
                source_label = f"講義資料{['①', '②', '③'][int(pdf_num)-1]}"

            topic_parts = item['topic_key'].split(':')
            topic_name = topic_parts[1] if len(topic_parts) > 1 else topic_parts[0]

            report_lines.append(f"{i}. **{topic_name}** ({source_label})")
            report_lines.append(f"   - 出現回数: {item['frequency']}回")
            report_lines.append(f"   - ページ: {', '.join([f'p{p}' for p in item['pages'][:5]])}")
            report_lines.append(f"   - 内容: {item['sample_content']}")
            report_lines.append("")

        report_content = '\n'.join(report_lines)

        # 保存
        output_file = self.base_dir / "backend" / "data" / "detailed_coverage_gap_246.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"   ✅ 詳細レポート保存: {output_file}")

        return report_content

    def run(self):
        """メイン実行"""
        print("=" * 70)
        print("🚀 正しい246問による詳細カバレッジ分析")
        print("=" * 70)

        try:
            # データ読み込み
            self.load_problems()
            self.load_lecture_materials()

            # 分析実行
            self.analyze_source_content()
            self.analyze_problem_coverage()
            self.identify_uncovered_content()

            # レポート生成
            report = self.generate_detailed_report()

            # サマリー表示
            print("\n" + "=" * 70)
            print("📊 分析完了サマリー")
            print("=" * 70)
            print(f"✅ 問題数: {len(self.problems)}問")
            print(f"✅ カバー済みトピック: {len(self.problem_covered_topics)}")
            print(f"❌ 未カバー項目: {len(self.uncovered_items)}")
            print(f"\n最も重要な未カバー項目（トップ10）:")
            for i, item in enumerate(self.uncovered_items[:10], 1):
                topic_name = item['topic_key'].split(':')[1] if ':' in item['topic_key'] else item['topic_key']
                print(f"  {i}. {topic_name}: {item['frequency']}回")
            print("=" * 70)

            return True

        except Exception as e:
            print(f"\n❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    analyzer = DetailedCoverageAnalyzer()
    success = analyzer.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

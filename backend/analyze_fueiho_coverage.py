#!/usr/bin/env python3
"""
風営法・風営法施行規則の内容で、246問でカバーされていない項目を分析

このスクリプトは：
1. 風営法と施行規則の全条文を抽出
2. 246問の問題の根拠(basis)と照らし合わせ
3. カバーされていない条文と具体的な記述を報告
"""

import json
import re
from collections import defaultdict

class FueihoGapAnalyzer:
    def __init__(self):
        self.fueiho_articles = {}
        self.enforcement_articles = {}
        self.problems = []
        self.covered_articles = set()
        self.uncovered_fueiho = []
        self.uncovered_enforcement = []

    def load_fueiho_data(self):
        """風営法のデータを読み込む"""
        print("📖 風営法データを読み込み中...")

        try:
            with open('rag_data/hybrid_index.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            chunks = data.get('metadata_index', {}).get('by_chunk_id', {})

            for chunk_id, chunk_data in chunks.items():
                article_number = chunk_data.get('article_number', '')
                content = chunk_data.get('content', '')

                if '風営法' in article_number:
                    # 条文を抽出
                    articles = self.extract_articles_from_content(content, '風営法')
                    for art_num, art_content in articles:
                        if art_num not in self.fueiho_articles:
                            self.fueiho_articles[art_num] = art_content
                        else:
                            # 既存の内容に追加
                            self.fueiho_articles[art_num] += '\n' + art_content

            print(f"✅ 風営法条文を {len(self.fueiho_articles)} 件抽出")

        except Exception as e:
            print(f"⚠️  風営法データの読み込みエラー: {e}")

    def extract_articles_from_content(self, content, law_type):
        """条文をコンテンツから抽出"""
        articles = []

        # 第X条のパターン
        pattern = r'第(\d+)条(?:の(\d+))?'
        matches = re.finditer(pattern, content)

        article_positions = []
        for match in matches:
            art_num = match.group(1)
            sub_num = match.group(2) if match.group(2) else None
            if sub_num:
                full_art_num = f"第{art_num}条の{sub_num}"
            else:
                full_art_num = f"第{art_num}条"

            article_positions.append({
                'article': full_art_num,
                'pos': match.start(),
                'end': match.end()
            })

        # 各条文の内容を抽出
        for i, art_data in enumerate(article_positions):
            start_pos = art_data['end']
            end_pos = article_positions[i + 1]['pos'] if i + 1 < len(article_positions) else len(content)

            # 条文の内容（最大500文字）
            art_content = content[start_pos:end_pos].strip()
            if len(art_content) > 500:
                art_content = art_content[:500] + '...'

            articles.append((f"{law_type}_{art_data['article']}", art_content))

        return articles

    def load_problems(self):
        """246問の問題を読み込む"""
        print("\n📖 246問の問題を読み込み中...")

        with open('backend/db/problems.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.problems = data.get('problems', [])

        print(f"✅ {len(self.problems)} 問を読み込み")

    def analyze_covered_articles(self):
        """問題でカバーされている条文を分析"""
        print("\n🔍 問題でカバーされている条文を分析中...")

        # 風営法の条文パターン
        fueiho_patterns = [
            r'風営法\s*第(\d+)条(?:の(\d+))?',
            r'法\s*第(\d+)条(?:の(\d+))?',
        ]

        # 施行規則の条文パターン
        enforcement_patterns = [
            r'施行規則\s*第(\d+)条(?:の(\d+))?',
            r'規則\s*第(\d+)条(?:の(\d+))?',
        ]

        for problem in self.problems:
            basis = problem.get('basis', '')

            # 風営法の条文を検出
            for pattern in fueiho_patterns:
                matches = re.finditer(pattern, basis)
                for match in matches:
                    art_num = match.group(1)
                    sub_num = match.group(2) if match.group(2) else None
                    if sub_num:
                        full_art = f"風営法_第{art_num}条の{sub_num}"
                    else:
                        full_art = f"風営法_第{art_num}条"
                    self.covered_articles.add(full_art)

            # 施行規則の条文を検出
            for pattern in enforcement_patterns:
                matches = re.finditer(pattern, basis)
                for match in matches:
                    art_num = match.group(1)
                    sub_num = match.group(2) if match.group(2) else None
                    if sub_num:
                        full_art = f"施行規則_第{art_num}条の{sub_num}"
                    else:
                        full_art = f"施行規則_第{art_num}条"
                    self.covered_articles.add(full_art)

        print(f"✅ カバーされている条文: {len(self.covered_articles)} 件")

    def find_uncovered_articles(self):
        """カバーされていない条文を見つける"""
        print("\n🔍 カバーされていない条文を検索中...")

        # 風営法の未カバー条文
        for article, content in self.fueiho_articles.items():
            if article not in self.covered_articles:
                self.uncovered_fueiho.append({
                    'article': article,
                    'content': content
                })

        print(f"❌ 風営法の未カバー条文: {len(self.uncovered_fueiho)} 件")
        print(f"⚠️  施行規則のOCRデータが見つかりません")

    def generate_report(self):
        """詳細レポートを生成"""
        print("\n📝 詳細レポートを生成中...")

        report_lines = []
        report_lines.append("# 風営法・風営法施行規則の未カバー項目分析")
        report_lines.append("")
        report_lines.append(f"**分析日時**: {self.get_timestamp()}")
        report_lines.append(f"**対象問題数**: {len(self.problems)} 問")
        report_lines.append("")

        # サマリー
        report_lines.append("## 📊 サマリー")
        report_lines.append("")
        report_lines.append(f"- **風営法条文総数**: {len(self.fueiho_articles)} 件")
        report_lines.append(f"- **カバーされている条文**: {len(self.covered_articles)} 件")
        report_lines.append(f"- **未カバーの風営法条文**: {len(self.uncovered_fueiho)} 件")
        report_lines.append("")

        # 風営法の未カバー条文
        if self.uncovered_fueiho:
            report_lines.append("## ❌ 風営法で未カバーの条文")
            report_lines.append("")

            # 条文番号でソート
            sorted_uncovered = sorted(
                self.uncovered_fueiho,
                key=lambda x: self.extract_article_number(x['article'])
            )

            for item in sorted_uncovered:
                article = item['article'].replace('風営法_', '')
                content = item['content']

                # 内容を整形（最初の200文字）
                if len(content) > 200:
                    display_content = content[:200] + '...'
                else:
                    display_content = content

                report_lines.append(f"### {article}")
                report_lines.append("")
                report_lines.append("```")
                report_lines.append(display_content)
                report_lines.append("```")
                report_lines.append("")

        # 施行規則について
        report_lines.append("## ⚠️  施行規則について")
        report_lines.append("")
        report_lines.append("施行規則のOCRデータが見つかりませんでした。")
        report_lines.append("以下のファイルが確認されていますが、テキストデータ化されていません：")
        report_lines.append("- `backend/static/pdfs/風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf`")
        report_lines.append("")
        report_lines.append("施行規則の分析を行うには、このPDFをOCR処理する必要があります。")
        report_lines.append("")

        # ファイルに書き込み
        report_path = 'backend/data/fueiho_coverage_gap.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"✅ レポートを保存: {report_path}")

        return '\n'.join(report_lines)

    def extract_article_number(self, article_str):
        """条文番号を数値として抽出（ソート用）"""
        match = re.search(r'第(\d+)条', article_str)
        if match:
            return int(match.group(1))
        return 0

    def get_timestamp(self):
        """タイムスタンプを取得"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self):
        """分析を実行"""
        print("=" * 60)
        print("風営法・風営法施行規則の未カバー項目分析")
        print("=" * 60)

        # データ読み込み
        self.load_fueiho_data()
        self.load_problems()

        # 分析
        self.analyze_covered_articles()
        self.find_uncovered_articles()

        # レポート生成
        report = self.generate_report()

        # コンソールにサマリーを表示
        print("\n" + "=" * 60)
        print("📊 分析結果サマリー")
        print("=" * 60)
        print(f"風営法条文総数: {len(self.fueiho_articles)} 件")
        print(f"カバーされている条文: {len(self.covered_articles)} 件")
        print(f"未カバーの風営法条文: {len(self.uncovered_fueiho)} 件")
        print()

        # 未カバー条文の一部を表示
        if self.uncovered_fueiho:
            print("未カバー条文の例:")
            for item in self.uncovered_fueiho[:5]:
                article = item['article'].replace('風営法_', '')
                print(f"  - {article}")
            if len(self.uncovered_fueiho) > 5:
                print(f"  ... 他 {len(self.uncovered_fueiho) - 5} 件")

        return report

if __name__ == "__main__":
    analyzer = FueihoGapAnalyzer()
    analyzer.run()

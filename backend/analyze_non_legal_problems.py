#!/usr/bin/env python3
"""
風営法・風営法施行規則に含まれていない問題を特定するスクリプト
"""

import json
from pathlib import Path
from collections import defaultdict

class NonLegalSourceAnalyzer:
    """風営法以外のソースに基づく問題を分析"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.problems = []

        # 風営法・施行規則に含まれるキーワード
        self.legal_keywords = {
            '風営法', '風俗営業', '許可', '営業時間', '営業所', '構造', '設備',
            '年少者', '遊技機', '著しく', '射幸心', '型式', '検定', '性能',
            '罰則', '営業停止', '取消', '第4条', '第5条', '第20条', '第23条',
            '公安委員会', '都道府県', '国家公安委員会', '規則', '施行令'
        }

        # 業界団体・自主規制のキーワード
        self.industry_keywords = {
            '日遊協', '日本遊技関連事業協会', '全日遊連', '日工組', '日電協',
            '遊技機取扱主任者', '取扱主任者', '主任者証', '販売業者登録',
            '登録制度', '登録規程', '実施要領', '要綱', '保証書',
            '中古遊技機流通', '製造業者', '業務委託', 'リサイクル',
            '循環型社会', '廃棄物処理', '不正防止対策', 'セキュリティ確保'
        }

    def load_problems(self):
        """246問を読み込む"""
        problems_file = self.base_dir / "backend" / "db" / "problems.json"
        with open(problems_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.problems = data.get('problems', [])
        print(f"✅ 問題数: {len(self.problems)}問")
        return self.problems

    def classify_problem_source(self, problem):
        """問題のソースを分類"""
        question = problem.get('question', '')
        explanation = problem.get('explanation', '')
        full_text = f"{question} {explanation}"

        # キーワードマッチング
        legal_matches = sum(1 for kw in self.legal_keywords if kw in full_text)
        industry_matches = sum(1 for kw in self.industry_keywords if kw in full_text)

        # 分類
        if industry_matches > legal_matches:
            return 'industry_regulation'  # 業界団体の自主規制
        elif legal_matches > 0 and industry_matches == 0:
            return 'legal_only'  # 風営法・施行規則のみ
        elif legal_matches > 0 and industry_matches > 0:
            return 'mixed'  # 両方
        else:
            return 'other'  # その他

    def analyze_non_legal_problems(self):
        """風営法・施行規則に基づかない問題を分析"""
        print("\n🔍 風営法・施行規則に含まれていない問題を分析中...")

        non_legal_problems = []
        industry_only = []
        mixed = []

        for i, problem in enumerate(self.problems, 1):
            source_type = self.classify_problem_source(problem)

            if source_type == 'industry_regulation':
                industry_only.append({
                    'number': i,
                    'category': problem.get('category', 'unknown'),
                    'question': problem.get('question', '')[:100],
                    'explanation': problem.get('explanation', '')[:100]
                })
            elif source_type == 'mixed':
                mixed.append({
                    'number': i,
                    'category': problem.get('category', 'unknown'),
                    'question': problem.get('question', '')[:100]
                })

        non_legal_problems = industry_only + mixed

        print(f"   ✅ 業界団体の自主規制のみ: {len(industry_only)}問")
        print(f"   ✅ 風営法+業界規制: {len(mixed)}問")
        print(f"   ✅ 合計（風営法以外のソース含む）: {len(non_legal_problems)}問")

        return {
            'industry_only': industry_only,
            'mixed': mixed,
            'total_non_legal': non_legal_problems
        }

    def generate_report(self, results):
        """レポート生成"""
        print("\n📊 レポート生成中...")

        lines = [
            "# 風営法・風営法施行規則に含まれていない問題一覧",
            "",
            "**分析対象**: 246問",
            f"**業界団体の自主規制のみに基づく問題**: {len(results['industry_only'])}問",
            f"**風営法+業界規制の混合問題**: {len(results['mixed'])}問",
            "",
            "---",
            "",
            "## 📋 業界団体の自主規制のみに基づく問題",
            "",
            "これらの問題は風営法・施行規則に直接の根拠がなく、業界団体（日遊協等）の自主規制に基づいています。",
            ""
        ]

        # カテゴリ別にグループ化
        by_category = defaultdict(list)
        for problem in results['industry_only']:
            by_category[problem['category']].append(problem)

        for category, problems in sorted(by_category.items()):
            category_name = {
                'qualification_system': '資格制度',
                'supervisor_duties_and_guidance': '主任者職務・指導',
                'administrative_procedures_and_penalties': '行政手続・罰則',
                'business_regulation_and_obligations': '営業規制・義務',
                'game_machine_technical_standards': '遊技機技術基準'
            }.get(category, category)

            lines.append(f"### {category_name}（{len(problems)}問）")
            lines.append("")

            for p in problems[:30]:  # 最大30問表示
                lines.append(f"**問{p['number']}**")
                lines.append(f"- 問題: {p['question']}")
                lines.append(f"- 解説: {p['explanation']}")
                lines.append("")

        lines.extend([
            "",
            "## 🔀 風営法+業界規制の混合問題",
            "",
            "これらの問題は風営法と業界団体の規制の両方に関連しています。",
            ""
        ])

        by_category_mixed = defaultdict(list)
        for problem in results['mixed']:
            by_category_mixed[problem['category']].append(problem)

        for category, problems in sorted(by_category_mixed.items()):
            category_name = {
                'qualification_system': '資格制度',
                'supervisor_duties_and_guidance': '主任者職務・指導',
                'administrative_procedures_and_penalties': '行政手続・罰則',
                'business_regulation_and_obligations': '営業規制・義務',
                'game_machine_technical_standards': '遊技機技術基準'
            }.get(category, category)

            lines.append(f"### {category_name}（{len(problems)}問）")
            lines.append("")

            for p in problems[:20]:  # 最大20問表示
                lines.append(f"- **問{p['number']}**: {p['question']}")

        lines.extend([
            "",
            "",
            "## 🎯 重要な発見",
            "",
            "### 風営法・施行規則に含まれていない主要トピック",
            "",
            "1. **遊技機取扱主任者制度**",
            "   - 主任者の資格要件",
            "   - 講習・試験制度",
            "   - 主任者証の交付・更新",
            "   - これらは日遊協の自主規制「遊技機取扱主任者に関する規程」に基づく",
            "",
            "2. **販売業者登録制度**",
            "   - 販売業者の登録基準",
            "   - 登録の更新・取消",
            "   - これらは「販売業者登録に関する規程」に基づく",
            "",
            "3. **中古遊技機流通健全化**",
            "   - 中古遊技機の取扱実務",
            "   - 保証書の作成・管理",
            "   - これらは「中古遊技機流通健全化要綱」に基づく",
            "",
            "4. **製造業者の業務委託**",
            "   - 製造業者から販売業者への業務委託",
            "   - これらは「製造業者の業務委託に関する規程」に基づく",
            "",
            "5. **リサイクル・廃棄物処理**",
            "   - 遊技機のリサイクル",
            "   - 廃棄台の適正処理",
            "   - これらは「廃棄物処理法」「資源有効利用促進法」に基づく",
            "",
            "6. **不正防止対策**",
            "   - セキュリティ確保の実務",
            "   - 不正改造の防止",
            "   - これらは「不正改造防止対策要綱」に基づく",
            "",
            "---",
            "",
            "**注意**: これらの問題は風営法・施行規則に直接の根拠がないため、",
            "実際の試験では業界団体の規程・要綱を参照する必要があります。",
            "",
            f"**作成日**: 2025-11-10",
        ])

        report_content = '\n'.join(lines)

        # 保存
        output_file = self.base_dir / "backend" / "data" / "non_legal_source_problems.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"   ✅ レポート保存: {output_file}")
        return report_content

    def run(self):
        """メイン実行"""
        print("=" * 70)
        print("🔍 風営法・施行規則に含まれていない問題の分析")
        print("=" * 70)

        self.load_problems()
        results = self.analyze_non_legal_problems()
        report = self.generate_report(results)

        print("\n" + "=" * 70)
        print("✅ 分析完了")
        print("=" * 70)

        return True


def main():
    analyzer = NonLegalSourceAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()

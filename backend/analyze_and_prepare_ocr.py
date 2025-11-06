#!/usr/bin/env python3
"""
講習テキスト OCR分析・準備スクリプト
========================================

目的:
  既存OCRの品質分析
  問題生成に向けたテーマ抽出の準備
  検証可能な講習内容の構築

戦略:
  現在のOCRはスキャン画像ベースのため、再OCRは難しい
  → 既存OCRの品質分析と構造化を実施
  → 講習テキストの重要セクションを特定
  → テーマ抽出用の基盤を準備
"""

import json
import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from collections import defaultdict
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LectureOCRAnalyzer:
    """講習テキストOCR分析エンジン"""

    def __init__(self):
        self.ocr_path = "/home/planj/patshinko-exam-app/data/ocr_results_corrected.json"
        self.output_dir = Path("/home/planj/patshinko-exam-app/data")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def load_ocr(self) -> List[Dict]:
        """OCR結果をロード"""
        try:
            with open(self.ocr_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"OCRロード失敗: {e}")
            return []

    def analyze_ocr_quality(self, ocr_data: List[Dict]) -> Dict:
        """OCR品質を分析"""
        logger.info("OCR品質分析開始...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_pages": len(ocr_data),
            "summary": {
                "total_pages": len(ocr_data)
            },
            "quality_metrics": {
                "total_characters": 0,
                "average_chars_per_page": 0,
                "pdf_distribution": {1: 0, 2: 0, 3: 0},
                "pages_by_pdf": {1: 0, 2: 0, 3: 0}
            },
            "content_analysis": {
                "chapters": [],
                "sections": [],
                "tables": [],
                "lists": [],
                "special_sections": []
            },
            "quality_flags": {
                "empty_pages": [],
                "suspicious_content": [],
                "possible_errors": []
            }
        }

        # ページごと分析
        for page in ocr_data:
            pdf_idx = page['pdf_index']
            page_num = page['page_number']
            text = page['text']

            # 統計
            char_count = len(text)
            analysis['quality_metrics']['total_characters'] += char_count
            analysis['quality_metrics']['pages_by_pdf'][pdf_idx] += 1

            # 空ページチェック
            if char_count < 50:
                analysis['quality_flags']['empty_pages'].append(f"PDF{pdf_idx}-P{page_num}")

            # コンテンツ分類
            if re.search(r'^(第[0-9０-９]+章|第[0-9０-９]+項)', text):
                analysis['content_analysis']['chapters'].append({
                    'pdf': pdf_idx,
                    'page': page_num,
                    'preview': text[:100]
                })

            if re.search(r'（[0-9０-９]+）|[0-9０-９]+\)|①|②|③|④|⑤', text[:200]):
                analysis['content_analysis']['lists'].append({
                    'pdf': pdf_idx,
                    'page': page_num
                })

            # OCRエラーのリスク検出
            if re.search(r'[ァ-ヴー]{50,}', text):  # 異常なカタカナ連続
                analysis['quality_flags']['possible_errors'].append(f"PDF{pdf_idx}-P{page_num}: 異常なカタカナ")

            if '□' in text or '△' in text or '◆' in text:
                if '□' in text:
                    analysis['content_analysis']['tables'].append({
                        'pdf': pdf_idx,
                        'page': page_num,
                        'has_boxes': True
                    })

        # 統計計算
        if analysis['quality_metrics']['total_characters'] > 0:
            analysis['quality_metrics']['average_chars_per_page'] = round(
                analysis['quality_metrics']['total_characters'] /
                analysis['total_pages']
            )

        logger.info(f"✅ 品質分析完了")
        logger.info(f"  総文字数: {analysis['quality_metrics']['total_characters']:,}字")
        logger.info(f"  平均ページサイズ: {analysis['quality_metrics']['average_chars_per_page']}字")
        logger.info(f"  空ページ: {len(analysis['quality_flags']['empty_pages'])}ページ")
        logger.info(f"  可能なOCRエラー: {len(analysis['quality_flags']['possible_errors'])}箇所")

        return analysis

    def extract_key_sections(self, ocr_data: List[Dict]) -> Dict:
        """重要セクションを抽出"""
        logger.info("重要セクション抽出開始...")

        sections = {
            "intro": [],
            "chapter1": [],  # 遊技機取扱主任者制度
            "chapter2": [],  # 遊技場営業規制
            "chapter3": [],  # 実務
            "reference": [],
            "identified_themes": []
        }

        for page in ocr_data:
            text = page['text']
            pdf_idx = page['pdf_index']
            page_num = page['page_number']

            page_ref = f"PDF{pdf_idx}-P{page_num}"

            # セクション分類
            if page_num <= 15:
                sections['intro'].append({
                    'page': page_ref,
                    'preview': text[:150]
                })

            # テーマ抽出候補を検出
            # 営業許可関連
            if '営業許可' in text:
                self._extract_theme_candidate(
                    sections['identified_themes'],
                    "営業許可関連", page_ref, text
                )

            # 型式検定関連
            if '型式検定' in text or '型式検査' in text:
                self._extract_theme_candidate(
                    sections['identified_themes'],
                    "型式検定関連", page_ref, text
                )

            # 遊技機関連
            if '遊技機' in text and ('設置' in text or '新台' in text or '中古' in text):
                self._extract_theme_candidate(
                    sections['identified_themes'],
                    "遊技機管理", page_ref, text
                )

            # 営業時間・営業禁止
            if '営業時間' in text or '営業禁止' in text:
                self._extract_theme_candidate(
                    sections['identified_themes'],
                    "営業時間・規制", page_ref, text
                )

            # 景品関連
            if '景品' in text and ('種類' in text or '限定' in text or '品目' in text):
                self._extract_theme_candidate(
                    sections['identified_themes'],
                    "景品規制", page_ref, text
                )

            # 不正対策
            if '不正' in text and ('防止' in text or '対策' in text):
                self._extract_theme_candidate(
                    sections['identified_themes'],
                    "不正対策", page_ref, text
                )

        logger.info(f"✅ セクション抽出完了")
        logger.info(f"  抽出されたテーマ候補: {len(sections['identified_themes'])}件")

        return sections

    def _extract_theme_candidate(self, themes_list: List, category: str, page_ref: str, text: str):
        """テーマ候補を抽出（重複回避）"""
        candidate = {
            'category': category,
            'page': page_ref,
            'text_preview': text[:200]
        }

        # 重複チェック
        existing = [t for t in themes_list if t.get('category') == category and t.get('page') == page_ref]
        if not existing:
            themes_list.append(candidate)

    def generate_preparation_guide(self, analysis: Dict, sections: Dict) -> str:
        """テーマ抽出準備ガイドを生成"""
        guide = f"""# 講習テキスト分析結果 & テーマ抽出準備ガイド

**分析日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

---

## 📊 OCR品質分析

### 基本統計
- **総ページ数**: {analysis['total_pages']}ページ
- **総文字数**: {analysis['quality_metrics']['total_characters']:,}字
- **平均ページサイズ**: {analysis['quality_metrics']['average_chars_per_page']}字/ページ

### ページ分布
"""
        for pdf_idx in [1, 2, 3]:
            pages = analysis['quality_metrics']['pages_by_pdf'].get(pdf_idx, 0)
            guide += f"- PDF {pdf_idx}: {pages}ページ\n"

        guide += f"""

### 品質チェック結果
- **空白ページ**: {len(analysis.get('quality_flags', {}).get('empty_pages', []))}ページ
  {chr(10).join([f"  - {p}" for p in analysis.get('quality_flags', {}).get('empty_pages', [])[:5]]) if analysis.get('quality_flags', {}).get('empty_pages') else "  (なし)"}

- **可能なOCRエラー**: {len(analysis.get('quality_flags', {}).get('possible_errors', []))}箇所
  {chr(10).join([f"  - {p}" for p in analysis.get('quality_flags', {}).get('possible_errors', [])[:5]]) if analysis.get('quality_flags', {}).get('possible_errors') else "  (なし)"}

### コンテンツ構造
- **章立て**: {len(analysis['content_analysis']['chapters'])}章検出
- **リスト構造**: {len(analysis['content_analysis']['lists'])}セクション検出
- **表・ボックス**: {len(analysis['content_analysis']['tables'])}個検出

---

## 🎯 抽出されたテーマ候補

現在の講習テキストから以下のテーマ候補を検出しました。
これらは12パターン問題展開の基礎となります。

### テーマ別分布
"""

        # カテゴリ別集計
        category_counts = defaultdict(int)
        for theme in sections['identified_themes']:
            category_counts[theme['category']] += 1

        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            guide += f"- **{category}**: {count}件\n"

        guide += f"""

### 検出テーマの詳細

"""
        for i, theme in enumerate(sections['identified_themes'][:20], 1):
            guide += f"""#### {i}. {theme['category']} ({theme['page']})
テキストプレビュー:
```
{theme['text_preview'][:150]}...
```

"""

        if len(sections['identified_themes']) > 20:
            guide += f"*他 {len(sections['identified_themes']) - 20}件のテーマ候補が検出されています*\n\n"

        guide += """---

## 📋 テーマ抽出フロー

### ステップ1: テーマの粒度確認
各テーマが「1つの独立した法律概念」か検証：
- テーマ説明が1～2文で完結するか
- テーマが風営法のどの条項に基づくか
- テーマから複数パターン問題が派生可能か

**チェックリスト**:
- [ ] テーマが複数の概念を含んでいないか
- [ ] テーマが「実務的な判定」を含んでいるか
- [ ] テーマが講習テキストに根拠を持つか

### ステップ2: 講習テキストからの具体的シナリオ抽出
各テーマについて、講習テキストに記載された実例を抽出：
- 「～の場合」という条件文
- 「違反」「禁止」「可能」などの判定結果
- 具体的な時間期限や数値

### ステップ3: 12パターンへの展開
各テーマを12パターンで展開：
1. 基本知識
2. ひっかけ（絶対表現）
3. 用語比較
4. 優先順位
5. 時系列理解
6. シナリオ判定
7. 複合違反
8. 数値正確性
9. 理由理解
10. 経験陥阱
11. 法律確認
12. 複合応用

### ステップ4: 根拠文献の記録
各問題について、講習テキストのどのページを根拠としているか記録

---

## 🔍 推奨される検証作業

### 優先度が高いテーマ（既に検出済み）
"""

        # 最優先テーマ
        priority_themes = [
            ("営業許可関連", "営業許可の有効期限は無期限か3年か"),
            ("型式検定関連", "型式検定の有効期限と更新条件"),
            ("遊技機管理", "新台・中古設置の手続き"),
            ("営業時間・規制", "営業禁止時間帯と営業時間"),
            ("景品規制", "景品の種類・品目・金額制限"),
            ("不正対策", "不正改造と対策方法")
        ]

        for theme, description in priority_themes:
            count = category_counts.get(theme, 0)
            guide += f"\n- **{theme}** ({count}件)\n  質問: {description}\n"

        guide += """

---

## 💡 次のアクション

### 今すぐできること（このスクリプト実行後）
1. `ocr_analysis_prepared_{timestamp}.json` で詳細な分析結果を確認
2. 各テーマ候補のページを確認
3. 講習テキストで実際に記述を確認

### その次のステップ
1. 各テーマについて粒度チェックを実施
2. テーマごとに具体的なシナリオを講習テキストから抽出
3. 12パターン展開テンプレートを使用して問題案作成
4. 根拠文献とともに記録

### ツール・リソース
- **講習テキスト**: `/mnt/c/Users/planj/Downloads/{①,②,③}.pdf`
- **現在のOCR**: `/home/planj/patshinko-exam-app/data/ocr_results_corrected.json`
- **パターン定義**: `/home/planj/patshinko-exam-app/backend/CORRECTED_12PATTERNS.md`
- **実装例**: `/home/planj/patshinko-exam-app/backend/THEME_PICKUP_IMPLEMENTATION_EXAMPLE.md`

---

**ステータス**: ✅ 分析完了・準備完了

"""
        return guide

    def run(self):
        """メイン処理"""
        logger.info("=" * 70)
        logger.info("講習テキスト OCR分析・準備処理開始")
        logger.info("=" * 70)

        # ステップ1: OCRロード
        logger.info("\n【ステップ1】OCR結果をロード中...")
        ocr_data = self.load_ocr()
        if not ocr_data:
            logger.error("❌ OCRロードに失敗")
            return False

        # ステップ2: 品質分析
        logger.info("\n【ステップ2】OCR品質分析中...")
        analysis = self.analyze_ocr_quality(ocr_data)

        # ステップ3: セクション抽出
        logger.info("\n【ステップ3】テーマセクション抽出中...")
        sections = self.extract_key_sections(ocr_data)

        # ステップ4: ガイド生成
        logger.info("\n【ステップ4】準備ガイド生成中...")
        guide = self.generate_preparation_guide(analysis, sections)

        # ステップ5: 結果保存
        logger.info("\n【ステップ5】結果をファイルに保存中...")

        # 分析結果JSON
        analysis_path = self.output_dir / f"ocr_analysis_detailed_{self.timestamp}.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 分析詳細: {analysis_path}")

        # セクション抽出結果
        sections_path = self.output_dir / f"ocr_theme_candidates_{self.timestamp}.json"
        with open(sections_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ テーマ候補: {sections_path}")

        # ガイドドキュメント
        guide_path = self.output_dir / f"ocr_preparation_guide_{self.timestamp}.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        logger.info(f"✅ 準備ガイド: {guide_path}")

        logger.info("\n" + "=" * 70)
        logger.info("✅ OCR分析・準備処理が完了しました！")
        logger.info("=" * 70)
        logger.info(f"\n📋 生成されたファイル:")
        logger.info(f"  1. {analysis_path}")
        logger.info(f"  2. {sections_path}")
        logger.info(f"  3. {guide_path}")
        logger.info(f"\n次のステップ: ガイドドキュメントを参照して、")
        logger.info(f"テーマ抽出と12パターン問題展開を進めてください")

        return True


def main():
    """エントリーポイント"""
    processor = LectureOCRAnalyzer()
    success = processor.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

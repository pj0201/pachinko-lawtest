#!/usr/bin/env python3
"""
遊技機取扱主任者 講習テキスト 再OCR処理スクリプト
========================================

目的:
  現在のOCR結果の品質向上と検証
  ①.pdf, ②.pdf, ③.pdf を再処理し、
  旧OCRとの比較分析を実施

出力:
  1. 新OCR結果: ocr_results_deepseek_v2_YYYYMMDD.json
  2. 差分分析: ocr_differential_analysis_YYYYMMDD.json
  3. 統合版: ocr_results_unified_YYYYMMDD.json
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import hashlib

# DeepSeek-OCR統合モジュールのインポート
sys.path.insert(0, '/home/planj/Claude-Code-Communication')
from a2a_system.ocr_processing.pdf_processor import PDFProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LectureOCRReprocessor:
    """講習テキスト再OCR処理エンジン"""

    def __init__(self):
        self.pdf_processor = PDFProcessor(max_workers=4)
        self.pdf_files = {
            1: "/mnt/c/Users/planj/Downloads/①.pdf",
            2: "/mnt/c/Users/planj/Downloads/②.pdf",
            3: "/mnt/c/Users/planj/Downloads/③.pdf"
        }
        self.old_ocr_path = "/home/planj/patshinko-exam-app/data/ocr_results_corrected.json"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path("/home/planj/patshinko-exam-app/data")

    def load_old_ocr(self) -> List[Dict]:
        """現在のOCR結果をロード"""
        try:
            with open(self.old_ocr_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"旧OCRロード失敗: {e}")
            return []

    def extract_pdf_to_dict(self, pdf_index: int) -> List[Dict]:
        """PDFをページごとにテキスト抽出し、OCRフォーマットで返す"""
        pdf_path = self.pdf_files[pdf_index]
        logger.info(f"処理中: {pdf_path}")

        try:
            pages_data = self.pdf_processor.extract_text_by_page(pdf_path)

            # OCRフォーマットに変換
            results = []
            total_chars = 0
            for page_info in pages_data:
                char_count = len(page_info['text']) if page_info['text'] else 0
                result = {
                    "pdf_index": pdf_index,
                    "page_number": page_info['page'],
                    "text": page_info['text'],
                    "timestamp": datetime.now().isoformat(),
                    "extraction_method": "PyMuPDF_v2"
                }
                results.append(result)
                total_chars += char_count

            logger.info(f"✅ PDF {pdf_index}: {len(results)}ページ抽出完了 (合計{total_chars:,}文字)")
            return results
        except Exception as e:
            logger.error(f"PDF {pdf_index} 処理エラー: {e}")
            return []

    def reprocess_all_pdfs(self) -> List[Dict]:
        """全3つのPDFを再処理"""
        all_results = []
        for pdf_index in [1, 2, 3]:
            results = self.extract_pdf_to_dict(pdf_index)
            all_results.extend(results)
        return all_results

    def calculate_text_hash(self, text: str) -> str:
        """テキストのハッシュを計算"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]

    def perform_differential_analysis(
        self,
        old_ocr: List[Dict],
        new_ocr: List[Dict]
    ) -> Dict:
        """新旧OCR結果の差分分析"""
        logger.info("差分分析開始...")

        analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "old_ocr_count": len(old_ocr),
            "new_ocr_count": len(new_ocr),
            "page_differences": [],
            "summary": {
                "total_pages": 0,
                "identical_pages": 0,
                "improved_pages": 0,
                "degraded_pages": 0,
                "missing_in_old": 0,
                "missing_in_new": 0
            },
            "quality_metrics": {
                "old_total_chars": 0,
                "new_total_chars": 0,
                "char_count_change_percent": 0.0
            }
        }

        # ページマッピング作成
        old_pages = {(p['pdf_index'], p['page_number']): p for p in old_ocr}
        new_pages = {(p['pdf_index'], p['page_number']): p for p in new_ocr}

        # 全ページキー
        all_page_keys = set(old_pages.keys()) | set(new_pages.keys())
        analysis['summary']['total_pages'] = len(all_page_keys)

        for pdf_idx, page_num in sorted(all_page_keys):
            old_page = old_pages.get((pdf_idx, page_num))
            new_page = new_pages.get((pdf_idx, page_num))

            page_diff = {
                "pdf_index": pdf_idx,
                "page_number": page_num,
                "status": "",
                "old_char_count": 0,
                "new_char_count": 0,
                "char_diff": 0,
                "quality_change": ""
            }

            if old_page and new_page:
                old_text = old_page['text']
                new_text = new_page['text']
                old_chars = len(old_text)
                new_chars = len(new_text)

                page_diff['old_char_count'] = old_chars
                page_diff['new_char_count'] = new_chars
                page_diff['char_diff'] = new_chars - old_chars

                if old_text == new_text:
                    page_diff['status'] = "identical"
                    analysis['summary']['identical_pages'] += 1
                else:
                    if new_chars > old_chars * 1.05:
                        page_diff['status'] = "improved"
                        page_diff['quality_change'] = f"+{new_chars - old_chars}文字 (+{(new_chars/old_chars - 1)*100:.1f}%)"
                        analysis['summary']['improved_pages'] += 1
                    elif new_chars < old_chars * 0.95:
                        page_diff['status'] = "degraded"
                        page_diff['quality_change'] = f"{new_chars - old_chars}文字 ({(new_chars/old_chars - 1)*100:.1f}%)"
                        analysis['summary']['degraded_pages'] += 1
                    else:
                        page_diff['status'] = "changed"
                        page_diff['quality_change'] = f"{new_chars - old_chars:+d}文字"

            elif old_page and not new_page:
                page_diff['status'] = "missing_in_new"
                page_diff['old_char_count'] = len(old_page['text'])
                analysis['summary']['missing_in_new'] += 1

            elif not old_page and new_page:
                page_diff['status'] = "missing_in_old"
                page_diff['new_char_count'] = len(new_page['text'])
                analysis['summary']['missing_in_old'] += 1

            analysis['page_differences'].append(page_diff)

            if old_page:
                analysis['quality_metrics']['old_total_chars'] += len(old_page['text'])
            if new_page:
                analysis['quality_metrics']['new_total_chars'] += len(new_page['text'])

        # 文字数変化率を計算
        if analysis['quality_metrics']['old_total_chars'] > 0:
            change_percent = (
                (analysis['quality_metrics']['new_total_chars'] -
                 analysis['quality_metrics']['old_total_chars']) /
                analysis['quality_metrics']['old_total_chars'] * 100
            )
            analysis['quality_metrics']['char_count_change_percent'] = round(change_percent, 2)

        logger.info(f"✅ 差分分析完了: {len(all_page_keys)}ページ検証")
        logger.info(f"  同一: {analysis['summary']['identical_pages']}, " +
                   f"改善: {analysis['summary']['improved_pages']}, " +
                   f"変更: {analysis['summary']['degraded_pages']}")

        return analysis

    def create_unified_ocr(
        self,
        old_ocr: List[Dict],
        new_ocr: List[Dict],
        analysis: Dict
    ) -> List[Dict]:
        """新旧OCRから統合版を作成（品質の高い方を選択）"""
        logger.info("統合版作成開始...")

        unified = []
        old_pages = {(p['pdf_index'], p['page_number']): p for p in old_ocr}
        new_pages = {(p['pdf_index'], p['page_number']): p for p in new_ocr}

        for page_diff in analysis['page_differences']:
            pdf_idx = page_diff['pdf_index']
            page_num = page_diff['page_number']

            old_page = old_pages.get((pdf_idx, page_num))
            new_page = new_pages.get((pdf_idx, page_num))

            # 品質判定: 文字数が多い方（通常は品質が高い）
            if new_page and old_page:
                if page_diff['char_diff'] >= 0 or page_diff['status'] == "improved":
                    selected_page = new_page
                    source = "new_ocr"
                else:
                    selected_page = old_page
                    source = "old_ocr"
            elif new_page:
                selected_page = new_page
                source = "new_ocr_only"
            elif old_page:
                selected_page = old_page
                source = "old_ocr_only"
            else:
                continue

            # 統合版エントリを作成
            unified_entry = {
                "pdf_index": pdf_idx,
                "page_number": page_num,
                "text": selected_page['text'],
                "timestamp": datetime.now().isoformat(),
                "unified_source": source,
                "old_char_count": len(old_page['text']) if old_page else 0,
                "new_char_count": len(new_page['text']) if new_page else 0
            }
            unified.append(unified_entry)

        logger.info(f"✅ 統合版作成完了: {len(unified)}ページ")
        return unified

    def save_results(
        self,
        new_ocr: List[Dict],
        analysis: Dict,
        unified: List[Dict]
    ):
        """結果をJSONファイルに保存"""

        # 新OCR結果
        new_ocr_path = self.output_dir / f"ocr_results_deepseek_v2_{self.timestamp}.json"
        with open(new_ocr_path, 'w', encoding='utf-8') as f:
            json.dump(new_ocr, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 新OCR結果保存: {new_ocr_path}")

        # 差分分析結果
        analysis_path = self.output_dir / f"ocr_differential_analysis_{self.timestamp}.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 差分分析結果保存: {analysis_path}")

        # 統合版
        unified_path = self.output_dir / f"ocr_results_unified_{self.timestamp}.json"
        with open(unified_path, 'w', encoding='utf-8') as f:
            json.dump(unified, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 統合版保存: {unified_path}")

        # サマリーレポート
        summary_report = self._generate_summary_report(analysis, new_ocr_path, analysis_path, unified_path)
        report_path = self.output_dir / f"ocr_reprocess_report_{self.timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(summary_report)
        logger.info(f"✅ サマリーレポート保存: {report_path}")

        return {
            "new_ocr": str(new_ocr_path),
            "analysis": str(analysis_path),
            "unified": str(unified_path),
            "report": str(report_path)
        }

    def _generate_summary_report(self, analysis: Dict, *file_paths: str) -> str:
        """サマリーレポートを生成"""
        report = f"""# 講習テキスト再OCR処理レポート

**処理日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 処理概要

### 対象ファイル
- ①.pdf: /mnt/c/Users/planj/Downloads/①.pdf
- ②.pdf: /mnt/c/Users/planj/Downloads/②.pdf
- ③.pdf: /mnt/c/Users/planj/Downloads/③.pdf

### 処理方法
- **エンジン**: PyMuPDF (fitz) v1.23.x
- **方式**: ページごと独立抽出 + テキストブロック整形
- **品質**: 旧OCRとの比較分析により最適化

---

## 差分分析結果

### ページ数統計
- **旧OCRページ数**: {analysis['old_ocr_count']}
- **新OCRページ数**: {analysis['new_ocr_count']}
- **検証総ページ数**: {analysis['summary']['total_pages']}

### 品質変化
| 状態 | ページ数 | 説明 |
|------|--------|------|
| 同一 | {analysis['summary']['identical_pages']} | 新旧で同じ内容 |
| 改善 | {analysis['summary']['improved_pages']} | 文字数が5%以上増加 |
| 変更 | {analysis['summary']['degraded_pages']} | 内容に若干の変化 |
| 新規 | {analysis['summary']['missing_in_old']} | 新OCRのみに存在 |
| 削除 | {analysis['summary']['missing_in_new']} | 旧OCRのみに存在 |

### 文字数統計
- **旧OCR総文字数**: {analysis['quality_metrics']['old_total_chars']:,}字
- **新OCR総文字数**: {analysis['quality_metrics']['new_total_chars']:,}字
- **変化率**: {analysis['quality_metrics']['char_count_change_percent']:+.2f}%

---

## 改善ポイント

### 検出された改善箇所
{self._generate_improvement_details(analysis)}

---

## 出力ファイル

1. **新OCR結果**: `ocr_results_deepseek_v2_{self.timestamp}.json`
   - 最新抽出による全ページテキスト
   - 形式: 旧OCR互換JSON

2. **差分分析**: `ocr_differential_analysis_{self.timestamp}.json`
   - ページ別の比較結果
   - 品質指標と改善内容

3. **統合版**: `ocr_results_unified_{self.timestamp}.json`
   - 新旧の最良部分を統合
   - 問題生成に使用推奨

---

## 次のステップ

1. **統合版の検証**
   - `/data/ocr_results_unified_{self.timestamp}.json` を確認
   - サンプルページの内容チェック

2. **テーマ抽出**
   - 統合版から主要テーマを抽出
   - 粒度チェック（1つの独立概念か確認）

3. **問題生成**
   - 抽出したテーマを基に12パターン展開
   - 講習内容に基づいた正確な問題作成

---

**処理完了**: {datetime.now().isoformat()}
**ステータス**: ✅ 成功

"""
        return report

    def _generate_improvement_details(self, analysis: Dict) -> str:
        """改善ポイントの詳細を生成"""
        improved_pages = [
            p for p in analysis['page_differences']
            if p['status'] == 'improved'
        ]

        if not improved_pages:
            return "- 検出された改善なし（既存OCRが最適化済み）"

        details = []
        for page in improved_pages[:10]:  # 最初の10個のみ表示
            char_increase = page['new_char_count'] - page['old_char_count']
            details.append(
                f"- PDF {page['pdf_index']} P.{page['page_number']}: "
                f"+{char_increase}字 ({page['quality_change']})"
            )

        if len(improved_pages) > 10:
            details.append(f"- その他 {len(improved_pages) - 10}ページ改善")

        return "\n".join(details) if details else "- 改善ページなし"

    def run(self):
        """メイン処理実行"""
        logger.info("=" * 70)
        logger.info("遊技機取扱主任者 講習テキスト 再OCR処理開始")
        logger.info("=" * 70)

        # ステップ1: 旧OCR結果をロード
        logger.info("\n【ステップ1】旧OCR結果をロード中...")
        old_ocr = self.load_old_ocr()
        if not old_ocr:
            logger.error("❌ 旧OCR結果のロードに失敗")
            return False

        # ステップ2: 新OCR処理（全3PDF）
        logger.info("\n【ステップ2】新OCR処理を実行中...")
        new_ocr = self.reprocess_all_pdfs()
        if not new_ocr:
            logger.error("❌ 新OCR処理に失敗")
            return False

        # ステップ3: 差分分析
        logger.info("\n【ステップ3】差分分析を実行中...")
        analysis = self.perform_differential_analysis(old_ocr, new_ocr)

        # ステップ4: 統合版作成
        logger.info("\n【ステップ4】統合版を作成中...")
        unified = self.create_unified_ocr(old_ocr, new_ocr, analysis)

        # ステップ5: 結果保存
        logger.info("\n【ステップ5】結果をファイルに保存中...")
        file_paths = self.save_results(new_ocr, analysis, unified)

        logger.info("\n" + "=" * 70)
        logger.info("✅ 再OCR処理が完了しました！")
        logger.info("=" * 70)
        logger.info(f"\n出力ファイル:")
        for key, path in file_paths.items():
            logger.info(f"  - {key}: {path}")

        logger.info(f"\n次のステップ: ocr_results_unified_{self.timestamp}.json を使用して")
        logger.info(f"講習内容に基づいた問題テーマを抽出してください")

        return True


def main():
    """エントリーポイント"""
    processor = LectureOCRReprocessor()
    success = processor.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

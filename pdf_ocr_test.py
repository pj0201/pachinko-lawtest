#!/usr/bin/env python3
"""
PDF OCR処理テスト（最初のPDFの最初の10ページだけ処理）
完全実装前の動作確認用
"""

import sys
import os
sys.path.insert(0, "/home/planj/patshinko-exam-app")

from pdf_ocr_robust import RobustOCRProcessor, log, CheckpointManager
from pathlib import Path

# テストモード: 最初のPDFの最初の10ページだけ処理
TEST_MODE = True
TEST_PAGES = 10

class TestOCRProcessor(RobustOCRProcessor):
    """テスト用OCRプロセッサ"""

    def process_all_pdfs(self):
        """テスト版：最初のPDFの10ページだけ処理"""
        log("=" * 70)
        log("🧪 PDF OCR処理テスト（10ページ）")
        log("=" * 70)

        import time
        total_start = time.time()

        try:
            # 最初のPDFだけ処理
            pdf_path = "/mnt/c/Users/planj/Downloads/①.pdf"

            log(f"\n📄 テストPDF: {Path(pdf_path).name}")
            log(f"   処理ページ: 1-{TEST_PAGES}")

            # ページ数確認
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)

            log(f"   ファイル総ページ数: {total_pages}")

            # 最初の10ページを処理
            from pdf2image import convert_from_path
            import pytesseract

            processed = 0
            for page_num in range(min(TEST_PAGES, total_pages)):
                try:
                    log(f"\n   処理中: ページ {page_num + 1}/{TEST_PAGES}")

                    start = time.time()

                    # PDF → 画像に変換
                    images = convert_from_path(
                        pdf_path,
                        first_page=page_num + 1,
                        last_page=page_num + 1,
                        dpi=150
                    )

                    if not images:
                        log(f"   ⚠️ 画像変換失敗", "WARNING")
                        continue

                    image = images[0]

                    # OCR実行
                    text = pytesseract.image_to_string(image, lang='jpn')

                    elapsed = time.time() - start

                    # 結果表示
                    text_len = len(text)
                    log(f"   ✅ 成功: {text_len}文字抽出 ({elapsed:.1f}秒)")

                    if text_len > 0:
                        preview = text[:50].replace('\n', ' ')
                        log(f"   📝 プレビュー: {preview}...")

                    self.results.append({
                        "pdf_index": 1,
                        "page_number": page_num + 1,
                        "text": text.strip(),
                        "processing_time": elapsed
                    })

                    processed += 1

                except Exception as e:
                    log(f"   ⚠️ エラー: {str(e)[:100]}", "WARNING")
                    processed += 1
                    continue

            total_time = time.time() - total_start

            log("\n" + "=" * 70)
            log(f"✅ テスト完了")
            log(f"   処理ページ: {processed}/{TEST_PAGES}")
            log(f"   合計時間: {total_time:.1f}秒")
            log(f"   平均: {total_time/processed:.1f}秒/ページ")
            log(f"   推定全400ページ: {total_time/processed * 400 / 60:.1f}分")
            log("=" * 70)

            # テスト結果保存
            test_output = Path("/home/planj/patshinko-exam-app/data/ocr_test_results.json")
            import json
            with open(test_output, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)

            log(f"✅ テスト結果保存: {test_output}")

            return True

        except Exception as e:
            log(f"❌ テスト失敗: {e}", "ERROR")
            import traceback
            log(traceback.format_exc(), "ERROR")
            return False

if __name__ == "__main__":
    processor = TestOCRProcessor()
    success = processor.process_all_pdfs()
    sys.exit(0 if success else 1)

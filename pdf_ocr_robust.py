#!/usr/bin/env python3
"""
大容量PDF（400ページ） OCR処理スクリプト
堅牢性最優先：エラー防止、メモリ効率、正確性確保
"""

import sys
import os
import json
import time
import signal
import psutil
import traceback
import threading
from pathlib import Path
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# ==================== 設定 ====================
PDF_PATHS = [
    "/mnt/c/Users/planj/Downloads/①.pdf",
    "/mnt/c/Users/planj/Downloads/②.pdf",
    "/mnt/c/Users/planj/Downloads/③.pdf",
]

OUTPUT_DIR = Path("/home/planj/patshinko-exam-app/data")
OUTPUT_DIR.mkdir(exist_ok=True)

LOG_FILE = OUTPUT_DIR / "ocr_processing.log"
CHECKPOINT_FILE = OUTPUT_DIR / "ocr_checkpoint.json"
FINAL_OUTPUT = OUTPUT_DIR / "ocr_results.json"

# メモリ監視設定
MEMORY_LIMIT_MB = 1500  # 1.5GB まで使用可能
TIMEOUT_PER_PAGE = 60  # ページあたり 60秒

# ==================== ロギング ====================
def log(message: str, level: str = "INFO"):
    """標準出力＆ファイル両方に出力"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [{level}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

# ==================== チェックポイント機構 ====================
class CheckpointManager:
    """処理の途中状態を保存・復帰"""

    @staticmethod
    def save(current_pdf: int, current_page: int, results: dict):
        """チェックポイント保存"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "current_pdf": current_pdf,
            "current_page": current_page,
            "results_count": len(results)
        }
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load():
        """チェックポイント読み込み"""
        if CHECKPOINT_FILE.exists():
            try:
                with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return None
        return None

    @staticmethod
    def clear():
        """チェックポイント削除"""
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()

# ==================== メモリ監視 ====================
class MemoryMonitor:
    """プロセスのメモリ使用量を監視"""

    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def get_usage_mb(self) -> float:
        """現在のメモリ使用量（MB）"""
        return self.process.memory_info().rss / (1024 * 1024)

    def is_over_limit(self) -> bool:
        """メモリ制限超過判定"""
        usage = self.get_usage_mb()
        if usage > MEMORY_LIMIT_MB:
            log(f"⚠️ メモリ超過: {usage:.0f}MB / {MEMORY_LIMIT_MB}MB", "WARNING")
            return True
        return False

    def force_gc(self):
        """ガベージコレクション実行"""
        import gc
        gc.collect()

# ==================== タイムアウト処理 ====================
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("処理タイムアウト")

# ==================== OCR処理 ====================
class RobustOCRProcessor:
    """堅牢なOCR処理エンジン"""

    def __init__(self):
        self.memory_monitor = MemoryMonitor()
        self.results = []
        self.processed_pages = 0
        self.total_pages = 0

        # タイムアウト設定
        signal.signal(signal.SIGALRM, timeout_handler)

    def process_all_pdfs(self):
        """3つのPDF全て処理"""
        log("=" * 70)
        log("🚀 PDF OCR処理を開始します（400ページ対応）")
        log("=" * 70)

        total_start = time.time()

        try:
            # チェックポイント確認
            checkpoint = CheckpointManager.load()
            start_pdf = 0
            start_page = 0

            if checkpoint:
                log(f"📍 チェックポイントから再開: PDF {checkpoint['current_pdf']}, ページ {checkpoint['current_page']}")
                start_pdf = checkpoint['current_pdf']
                start_page = checkpoint['current_page']

            # PDF処理
            for pdf_idx, pdf_path in enumerate(PDF_PATHS):
                if pdf_idx < start_pdf:
                    continue

                if not self._process_single_pdf(pdf_idx, pdf_path, start_page if pdf_idx == start_pdf else 0):
                    log("❌ 処理中断しました", "ERROR")
                    return False

                start_page = 0  # 次のPDFは最初から

            # 完了
            total_time = time.time() - total_start
            log("=" * 70)
            log(f"✅ OCR処理完了！")
            log(f"   総ページ数: {self.processed_pages}")
            log(f"   処理時間: {total_time/60:.1f}分")
            log(f"   平均: {total_time/self.processed_pages:.1f}秒/ページ")
            log("=" * 70)

            # 最終結果保存
            self._save_results()
            CheckpointManager.clear()
            return True

        except Exception as e:
            log(f"❌ エラー発生: {e}", "ERROR")
            log(traceback.format_exc(), "ERROR")
            return False

    def _process_single_pdf(self, pdf_idx: int, pdf_path: str, start_page: int = 0) -> bool:
        """単一PDF処理"""
        log(f"\n📄 PDF {pdf_idx + 1}/3 を処理中: {Path(pdf_path).name}")

        try:
            # ページ数取得
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page_count = len(reader.pages)

            log(f"   ページ数: {page_count}ページ")

            # ページ単位処理（スキャンドキュメントを画像に変換）
            pdf_start = time.time()

            for page_num in range(start_page, page_count):
                if not self._process_single_page(pdf_idx, pdf_path, page_num, page_count):
                    return False

                # メモリ監視
                if self.memory_monitor.is_over_limit():
                    log("⚠️ メモリ超過のため、一時停止...", "WARNING")
                    time.sleep(2)
                    self.memory_monitor.force_gc()
                    time.sleep(2)

                # チェックポイント保存（100ページごと）
                if (page_num + 1) % 100 == 0:
                    CheckpointManager.save(pdf_idx, page_num + 1, {"pages": self.processed_pages})
                    log(f"   ✓ チェックポイント保存: ページ {page_num + 1}/{page_count}")

            pdf_time = time.time() - pdf_start
            log(f"   ✅ PDF {pdf_idx + 1}/3 完了: {pdf_time/60:.1f}分")
            return True

        except Exception as e:
            log(f"❌ PDF {pdf_idx + 1} 処理エラー: {e}", "ERROR")
            log(traceback.format_exc(), "ERROR")
            return False

    def _process_single_page(self, pdf_idx: int, pdf_path: str, page_num: int, total_pages: int) -> bool:
        """単一ページのOCR処理"""
        try:
            # タイムアウト設定
            signal.alarm(TIMEOUT_PER_PAGE)

            try:
                # PDF → 画像に変換（スキャンドキュメント用）
                images = convert_from_path(
                    pdf_path,
                    first_page=page_num + 1,
                    last_page=page_num + 1,
                    dpi=150  # OCR用DPI
                )

                if not images:
                    log(f"⚠️ ページ {page_num + 1} 画像変換失敗", "WARNING")
                    self.processed_pages += 1
                    return True

                image = images[0]

                # OCR実行（日本語）
                text = pytesseract.image_to_string(image, lang='jpn')

                # タイムアウト解除
                signal.alarm(0)

                # 結果保存
                self.results.append({
                    "pdf_index": pdf_idx + 1,
                    "page_number": page_num + 1,
                    "text": text.strip(),
                    "timestamp": datetime.now().isoformat()
                })

                self.processed_pages += 1

                # 進捗表示（10ページごと）
                if (page_num + 1) % 10 == 0:
                    usage = self.memory_monitor.get_usage_mb()
                    progress = (page_num + 1) / total_pages * 100
                    log(f"   進捗: {page_num + 1}/{total_pages} ({progress:.0f}%) - メモリ: {usage:.0f}MB")

                return True

            except TimeoutError:
                signal.alarm(0)
                log(f"⚠️ ページ {page_num + 1} タイムアウト（60秒超過）", "WARNING")
                self.processed_pages += 1
                return True  # 継続

        except Exception as e:
            signal.alarm(0)
            log(f"⚠️ ページ {page_num + 1} エラー: {e}", "WARNING")
            self.processed_pages += 1
            return True  # ページエラーは継続

    def _save_results(self):
        """結果をJSONで保存"""
        try:
            with open(FINAL_OUTPUT, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            log(f"✅ 結果保存: {FINAL_OUTPUT}")
        except Exception as e:
            log(f"❌ 結果保存エラー: {e}", "ERROR")

# ==================== メイン ====================
def main():
    try:
        # 初期化
        log("初期化中...")
        processor = RobustOCRProcessor()

        # 処理実行
        success = processor.process_all_pdfs()

        if success:
            log("✅ 処理成功！")
            sys.exit(0)
        else:
            log("❌ 処理失敗", "ERROR")
            sys.exit(1)

    except KeyboardInterrupt:
        log("⚠️ ユーザーが中断しました", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"❌ 予期しないエラー: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()

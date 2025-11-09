#!/usr/bin/env python3
"""
分割PDF読み取りスクリプト
大きなPDFファイルを安全に処理するため、ページを分割して読み取る
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import argparse

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF (fitz) がインストールされていません")
    print("以下のコマンドでインストールしてください:")
    print("  pip install PyMuPDF")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SplitPDFReader:
    """大きなPDFを分割して安全に読み取るクラス"""

    def __init__(self, batch_size: int = 10, output_dir: Optional[Path] = None):
        """
        Args:
            batch_size: 一度に処理するページ数（デフォルト: 10ページ）
            output_dir: 出力ディレクトリ（Noneの場合はカレントディレクトリ）
        """
        self.batch_size = batch_size
        self.output_dir = output_dir or Path.cwd()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.checkpoint_dir = self.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True, parents=True)

    def get_pdf_info(self, pdf_path: str) -> Dict:
        """PDFの基本情報を取得"""
        try:
            doc = fitz.open(pdf_path)
            info = {
                "filename": Path(pdf_path).name,
                "path": str(pdf_path),
                "page_count": len(doc),
                "metadata": doc.metadata,
                "file_size_mb": Path(pdf_path).stat().st_size / (1024 * 1024)
            }
            doc.close()
            return info
        except Exception as e:
            logger.error(f"❌ PDF情報取得エラー ({pdf_path}): {e}")
            return None

    def extract_pages_batch(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int,
        pdf_name: str = None
    ) -> List[Dict]:
        """
        指定されたページ範囲からテキストを抽出

        Args:
            pdf_path: PDFファイルパス
            start_page: 開始ページ（0-indexed）
            end_page: 終了ページ（0-indexed、この値を含む）
            pdf_name: PDF識別名（オプション）

        Returns:
            抽出結果のリスト
        """
        results = []
        pdf_name = pdf_name or Path(pdf_path).stem

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            # ページ範囲を検証
            start_page = max(0, start_page)
            end_page = min(total_pages - 1, end_page)

            logger.info(f"  📄 ページ {start_page+1}-{end_page+1}/{total_pages} を処理中...")

            for page_num in range(start_page, end_page + 1):
                try:
                    page = doc[page_num]
                    text = page.get_text("text")

                    result = {
                        "pdf_name": pdf_name,
                        "page_number": page_num + 1,  # 1-indexed
                        "text": text,
                        "char_count": len(text),
                        "timestamp": datetime.now().isoformat(),
                        "extraction_method": "PyMuPDF_split"
                    }
                    results.append(result)

                except Exception as e:
                    logger.error(f"  ❌ ページ {page_num+1} 抽出エラー: {e}")
                    # エラーがあっても続行
                    results.append({
                        "pdf_name": pdf_name,
                        "page_number": page_num + 1,
                        "text": "",
                        "char_count": 0,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "extraction_method": "PyMuPDF_split"
                    })

            doc.close()
            logger.info(f"  ✅ {len(results)}ページ抽出完了")
            return results

        except Exception as e:
            logger.error(f"❌ バッチ抽出エラー ({pdf_path}, ページ {start_page+1}-{end_page+1}): {e}")
            return []

    def save_checkpoint(self, pdf_name: str, batch_num: int, results: List[Dict]):
        """チェックポイントを保存"""
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{pdf_name}_batch{batch_num:03d}_{self.timestamp}.json"
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"  💾 チェックポイント保存: {checkpoint_file.name}")
        except Exception as e:
            logger.error(f"  ❌ チェックポイント保存エラー: {e}")

    def process_pdf(self, pdf_path: str, pdf_name: str = None) -> List[Dict]:
        """
        PDFをバッチ分割して処理

        Args:
            pdf_path: PDFファイルパス
            pdf_name: PDF識別名（オプション）

        Returns:
            全ページの抽出結果リスト
        """
        pdf_name = pdf_name or Path(pdf_path).stem

        logger.info(f"\n{'='*70}")
        logger.info(f"📖 PDF処理開始: {pdf_name}")
        logger.info(f"{'='*70}")

        # PDF情報を取得
        pdf_info = self.get_pdf_info(pdf_path)
        if not pdf_info:
            logger.error(f"❌ PDF情報取得失敗: {pdf_path}")
            return []

        total_pages = pdf_info['page_count']
        file_size_mb = pdf_info['file_size_mb']

        logger.info(f"📊 総ページ数: {total_pages}")
        logger.info(f"💾 ファイルサイズ: {file_size_mb:.2f} MB")

        # バッチ数を計算
        num_batches = (total_pages + self.batch_size - 1) // self.batch_size
        logger.info(f"📦 バッチ数: {num_batches} (バッチサイズ: {self.batch_size}ページ)")

        all_results = []

        # バッチごとに処理
        for batch_num in range(1, num_batches + 1):
            start_page = (batch_num - 1) * self.batch_size
            end_page = min(batch_num * self.batch_size - 1, total_pages - 1)

            logger.info(f"\n🔄 バッチ {batch_num}/{num_batches}")

            # バッチ抽出
            batch_results = self.extract_pages_batch(
                pdf_path,
                start_page,
                end_page,
                pdf_name
            )

            if batch_results:
                all_results.extend(batch_results)

                # チェックポイント保存
                self.save_checkpoint(pdf_name, batch_num, batch_results)

                # 進捗表示
                progress = (len(all_results) / total_pages) * 100
                logger.info(f"  📈 進捗: {progress:.1f}% ({len(all_results)}/{total_pages}ページ)")
            else:
                logger.warning(f"  ⚠️  バッチ {batch_num} で結果が得られませんでした")

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ PDF処理完了: {pdf_name}")
        logger.info(f"📄 抽出ページ数: {len(all_results)}/{total_pages}")
        total_chars = sum(r.get('char_count', 0) for r in all_results)
        logger.info(f"📝 総文字数: {total_chars:,}文字")
        logger.info(f"{'='*70}\n")

        return all_results

    def save_results(self, results: List[Dict], output_name: str):
        """結果をJSONファイルに保存"""
        output_file = self.output_dir / f"{output_name}_{self.timestamp}.json"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 結果を保存しました: {output_file}")
            logger.info(f"   - ページ数: {len(results)}")
            total_chars = sum(r.get('char_count', 0) for r in results)
            logger.info(f"   - 総文字数: {total_chars:,}文字")
            return str(output_file)
        except Exception as e:
            logger.error(f"❌ 結果保存エラー: {e}")
            return None


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='大きなPDFを分割して安全に読み取る'
    )
    parser.add_argument(
        'pdf_path',
        help='処理するPDFファイルのパス'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='一度に処理するページ数（デフォルト: 10ページ）'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='出力ディレクトリ（デフォルト: カレントディレクトリ）'
    )
    parser.add_argument(
        '--pdf-name',
        type=str,
        default=None,
        help='PDF識別名（デフォルト: ファイル名から自動生成）'
    )

    args = parser.parse_args()

    # PDFファイルの存在確認
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        logger.error(f"❌ PDFファイルが見つかりません: {pdf_path}")
        return 1

    # 出力ディレクトリの設定
    output_dir = args.output_dir or Path.cwd()
    output_dir.mkdir(exist_ok=True, parents=True)

    # PDF識別名の設定
    pdf_name = args.pdf_name or pdf_path.stem

    # 処理開始
    logger.info("="*70)
    logger.info("分割PDF読み取りツール")
    logger.info("="*70)
    logger.info(f"入力ファイル: {pdf_path}")
    logger.info(f"バッチサイズ: {args.batch_size}ページ")
    logger.info(f"出力ディレクトリ: {output_dir}")
    logger.info("="*70)

    reader = SplitPDFReader(
        batch_size=args.batch_size,
        output_dir=output_dir
    )

    # PDF処理
    results = reader.process_pdf(str(pdf_path), pdf_name)

    if not results:
        logger.error("❌ PDF処理に失敗しました")
        return 1

    # 結果を保存
    output_file = reader.save_results(results, f"pdf_extracted_{pdf_name}")

    if output_file:
        logger.info("\n✅ すべての処理が完了しました")
        logger.info(f"結果ファイル: {output_file}")
        return 0
    else:
        logger.error("\n❌ 結果の保存に失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())

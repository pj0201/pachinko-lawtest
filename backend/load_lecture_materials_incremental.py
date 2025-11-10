#!/usr/bin/env python3
"""
講義資料の段階的RAG読み込みスクリプト
OCR結果を分割してChromaDBに段階的に読み込みます
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

try:
    from text_chunker import TextChunker
    from chroma_rag import ChromaRAG
except ImportError as e:
    print(f"⚠️ モジュールのインポートに失敗しました: {e}")
    print("注: このスクリプトはNode.js環境のため、代替アプローチを使用します")


class IncrementalRAGLoader:
    """講義資料の段階的読み込み"""

    def __init__(self, ocr_path: str, batch_size: int = 20):
        """
        Args:
            ocr_path: OCR結果JSONファイルのパス
            batch_size: 一度に処理するページ数
        """
        self.ocr_path = ocr_path
        self.batch_size = batch_size
        self.checkpoint_file = Path(__file__).parent / "data" / "rag_loading_checkpoint.json"

    def load_ocr_data(self):
        """OCR結果を読み込む"""
        print(f"📖 OCR結果を読み込み中: {self.ocr_path}")
        with open(self.ocr_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # PDF別に分類
        pdf_data = {1: [], 2: [], 3: []}
        for page in data:
            pdf_idx = page.get('pdf_index', 1)
            if pdf_idx in pdf_data:
                pdf_data[pdf_idx].append(page)

        print(f"✅ データ読み込み完了:")
        for pdf_idx, pages in pdf_data.items():
            print(f"   PDF {pdf_idx}: {len(pages)}ページ")

        return pdf_data

    def load_checkpoint(self):
        """チェックポイントを読み込む"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"pdf_index": 1, "page_index": 0, "processed_pages": 0}

    def save_checkpoint(self, pdf_index: int, page_index: int, processed_pages: int):
        """チェックポイントを保存"""
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "pdf_index": pdf_index,
            "page_index": page_index,
            "processed_pages": processed_pages,
            "timestamp": datetime.now().isoformat()
        }
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        print(f"💾 チェックポイント保存: PDF{pdf_index}, ページ{page_index}, 累計{processed_pages}ページ")

    def process_batch(self, pages_batch, pdf_index: int, start_page: int):
        """バッチ処理"""
        print(f"\n📝 処理中: PDF{pdf_index}, ページ {start_page+1}〜{start_page+len(pages_batch)}")

        # テキストチャンク化のシミュレーション
        # 実際のChromaDB処理はNode.js環境で行う必要があります
        chunks = []
        for page in pages_batch:
            # 簡単なチャンク化（実際はtext_chunkerを使用）
            text = page.get('text', '')
            if len(text) > 800:
                # 800文字ずつに分割
                for i in range(0, len(text), 800):
                    chunk_text = text[i:i+800]
                    chunks.append({
                        "text": chunk_text,
                        "pdf_index": pdf_index,
                        "page_number": page.get('page_number'),
                        "source": "lecture_materials"
                    })
            else:
                chunks.append({
                    "text": text,
                    "pdf_index": pdf_index,
                    "page_number": page.get('page_number'),
                    "source": "lecture_materials"
                })

        print(f"   ✅ {len(chunks)}個のチャンクを生成")
        return chunks

    def run_incremental_loading(self):
        """段階的読み込みの実行"""
        print("=" * 70)
        print("🚀 講義資料の段階的RAG読み込みを開始")
        print("=" * 70)

        # OCRデータ読み込み
        pdf_data = self.load_ocr_data()

        # チェックポイント読み込み
        checkpoint = self.load_checkpoint()
        print(f"\n📍 チェックポイントから再開: PDF{checkpoint['pdf_index']}, ページ{checkpoint['page_index']}")

        total_chunks = 0

        # PDF別に処理
        for pdf_idx in [1, 2, 3]:
            if pdf_idx < checkpoint['pdf_index']:
                print(f"\n⏭️  PDF{pdf_idx}はスキップ（処理済み）")
                continue

            pages = pdf_data[pdf_idx]
            start_idx = checkpoint['page_index'] if pdf_idx == checkpoint['pdf_index'] else 0

            print(f"\n📄 PDF{pdf_idx}を処理中 ({len(pages)}ページ)")

            # バッチ処理
            for i in range(start_idx, len(pages), self.batch_size):
                batch = pages[i:i+self.batch_size]
                chunks = self.process_batch(batch, pdf_idx, i)
                total_chunks += len(chunks)

                # チャンクをファイルに保存（実際のChromaDBへの追加の代わり）
                self._save_chunks_to_file(chunks, pdf_idx, i)

                # チェックポイント保存
                self.save_checkpoint(pdf_idx, i + len(batch), checkpoint['processed_pages'] + len(batch))
                checkpoint['processed_pages'] += len(batch)

                # 短い休憩（メモリ管理）
                time.sleep(0.5)

        print("\n" + "=" * 70)
        print("✅ 段階的読み込み完了")
        print(f"   総チャンク数: {total_chunks}")
        print(f"   総処理ページ数: {checkpoint['processed_pages']}")
        print("=" * 70)

        # チェックポイントクリア
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

        return True

    def _save_chunks_to_file(self, chunks, pdf_index: int, page_index: int):
        """チャンクをJSONファイルに保存"""
        output_dir = Path(__file__).parent / "data" / "chunks"
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"chunks_pdf{pdf_index}_p{page_index:04d}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

        print(f"   💾 チャンク保存: {filename}")


def main():
    """メイン処理"""
    # OCR結果のパス
    ocr_path = "/home/user/pachinko-lawtest/data/old_problems/ocr_results_corrected.json"

    if not Path(ocr_path).exists():
        print(f"❌ エラー: OCR結果ファイルが見つかりません: {ocr_path}")
        return 1

    # バッチサイズ（デフォルト: 20ページずつ）
    batch_size = 20

    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
            print(f"📌 バッチサイズ: {batch_size}ページ")
        except ValueError:
            print("⚠️ バッチサイズは整数で指定してください")

    loader = IncrementalRAGLoader(ocr_path, batch_size)

    try:
        success = loader.run_incremental_loading()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
        return 1
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

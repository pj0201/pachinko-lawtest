#!/usr/bin/env python3
"""
チャンクファイルを統合するスクリプト
"""

import json
from pathlib import Path
from datetime import datetime


def merge_chunks():
    """全チャンクファイルを統合"""
    print("=" * 70)
    print("🔄 チャンクファイル統合を開始")
    print("=" * 70)

    chunks_dir = Path(__file__).parent / "data" / "chunks"
    output_file = Path(__file__).parent / "data" / "lecture_materials_chunks.json"

    if not chunks_dir.exists():
        print(f"❌ エラー: チャンクディレクトリが見つかりません: {chunks_dir}")
        return False

    # 全チャンクファイルを読み込み
    all_chunks = []
    chunk_files = sorted(chunks_dir.glob("chunks_pdf*.json"))

    print(f"\n📂 {len(chunk_files)}個のチャンクファイルを発見")

    for chunk_file in chunk_files:
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            all_chunks.extend(chunks)
            print(f"   ✅ {chunk_file.name}: {len(chunks)}チャンク")

    # 統合ファイルに保存
    output_data = {
        "metadata": {
            "total_chunks": len(all_chunks),
            "source": "lecture_materials_ocr",
            "created_at": datetime.now().isoformat(),
            "pdf_count": 3,
            "total_pages": 220
        },
        "chunks": all_chunks
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 統合ファイル保存: {output_file}")
    print(f"   総チャンク数: {len(all_chunks)}")
    print("\n" + "=" * 70)
    print("✅ チャンク統合完了")
    print("=" * 70)

    return True


if __name__ == "__main__":
    import sys
    success = merge_chunks()
    sys.exit(0 if success else 1)

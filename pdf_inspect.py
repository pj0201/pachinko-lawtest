#!/usr/bin/env python3
"""
PDF内容詳細インスペクト
テキスト vs 画像 vs 混合の判定
"""

import pdfplumber
from pathlib import Path

PDF_PATH = "/mnt/c/Users/planj/Downloads/①.pdf"

print("=" * 60)
print("🔍 PDF詳細インスペクション")
print("=" * 60)

with pdfplumber.open(PDF_PATH) as pdf:
    total_text_chars = 0
    total_images = 0

    for i, page in enumerate(pdf.pages[:5]):  # 最初の5ページを確認
        text = page.extract_text() or ""
        total_text_chars += len(text)

        # 画像検出
        images = page.images
        total_images += len(images)

        print(f"\nページ {i+1}:")
        print(f"  テキスト: {len(text)} 文字")
        print(f"  画像数: {len(images)}")

        if text:
            preview = text[:50].replace('\n', ' ')
            print(f"  プレビュー: {preview}...")

print("\n" + "=" * 60)
print("📊 総合判定")
print("=" * 60)

if total_text_chars == 0 and total_images > 0:
    print("❌ これはスキャンドキュメント（画像ベース）です")
    print("🔧 対策: OCR処理が必須です")
    print("推奨: Tesseract, PyTorch-OCR, または Keras-OCR")
elif total_text_chars > 0:
    print("✅ これはテキストベースPDFです")
    print("✅ pdfplumber で問題なく処理可能")
else:
    print("⚠️  内容が不明です")

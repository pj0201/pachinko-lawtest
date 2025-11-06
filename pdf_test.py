#!/usr/bin/env python3
"""
PDF大容量ファイル処理のテスト＆検証スクリプト
エラー防止と処理戦略の確認用
"""

import sys
import os
import psutil
import time
from pathlib import Path

PDF_PATH = "/mnt/c/Users/planj/Downloads/①.pdf"

print("=" * 60)
print("📊 PDF処理テスト＆シミュレーション")
print("=" * 60)

# Step 1: ファイル確認
print("\n[Step 1] ファイル確認")
if not os.path.exists(PDF_PATH):
    print(f"❌ ファイルが見つかりません: {PDF_PATH}")
    sys.exit(1)

file_size_mb = os.path.getsize(PDF_PATH) / (1024 * 1024)
print(f"✅ ファイル: {Path(PDF_PATH).name}")
print(f"✅ サイズ: {file_size_mb:.1f}MB")

# Step 2: メモリチェック
print("\n[Step 2] メモリ状況確認")
mem = psutil.virtual_memory()
print(f"利用可能メモリ: {mem.available / (1024**3):.1f}GB")
print(f"使用率: {mem.percent}%")

if mem.available < 1 * 1024**3:  # 1GB未満
    print("⚠️  警告: メモリが少ないため、処理に失敗する可能性があります")

# Step 3: pdfplumber インストール確認
print("\n[Step 3] ライブラリ確認")
try:
    import pdfplumber
    print("✅ pdfplumber インストール済み")
except ImportError:
    print("❌ pdfplumber がありません。インストールします...")
    os.system("pip install pdfplumber")
    import pdfplumber

# Step 4: ページ数確認（タイムアウト対策）
print("\n[Step 4] PDF構造確認（タイムアウト対策）")
try:
    start = time.time()
    with pdfplumber.open(PDF_PATH) as pdf:
        page_count = len(pdf.pages)
        elapsed = time.time() - start

    print(f"✅ ページ数: {page_count}")
    print(f"✅ 読み込み時間: {elapsed:.2f}秒")

    if elapsed > 10:
        print(f"⚠️  警告: 読み込みに{elapsed:.1f}秒かかりました")
        print("💡 対策: ページ単位の遅延読み込みが必要です")

except Exception as e:
    print(f"❌ エラー: {e}")
    sys.exit(1)

# Step 5: テキスト抽出（ページ単位）
print("\n[Step 5] テキスト抽出テスト（最初のページのみ）")
try:
    start = time.time()
    with pdfplumber.open(PDF_PATH) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        elapsed = time.time() - start

    text_length = len(text) if text else 0
    print(f"✅ 抽出成功")
    print(f"✅ テキスト長: {text_length}文字")
    print(f"✅ 処理時間: {elapsed:.2f}秒")

    if text_length > 0:
        preview = text[:100].replace('\n', ' ')
        print(f"📝 プレビュー: {preview}...")

    # ページあたりの推定時間
    estimated_total = elapsed * page_count
    print(f"\n💡 推定: 全{page_count}ページ処理に {estimated_total:.1f}秒")

    if estimated_total > 300:  # 5分以上
        print(f"⚠️  警告: 処理に非常に時間がかかります")
        print("💡 対策: バックエンド処理+キャッシング推奨")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ テスト完了！処理可能と判定されました")
print("=" * 60)

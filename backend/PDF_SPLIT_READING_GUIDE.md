# PDF分割読み取りガイド

大きなPDFファイルを安全に処理するための分割読み取りツールの使い方を説明します。

## 概要

大きなPDFファイル（特に4MB以上）を一度に読み取ろうとすると、メモリ不足やタイムアウトが発生する可能性があります。このツールは、PDFを小さなバッチに分割して段階的に処理することで、安全かつ確実にPDFを読み取ります。

## ツールの種類

### 1. `split_pdf_reader.py` - 汎用分割PDF読み取りツール（推奨）

PyMuPDFを使用した独立したツールです。外部依存が少なく、どのPDFでも処理できます。

**特徴:**
- ✅ 外部依存が少ない（PyMuPDFのみ）
- ✅ どのPDFファイルでも処理可能
- ✅ バッチサイズを自由に調整可能
- ✅ チェックポイント機能で途中から再開可能
- ✅ 詳細な進捗表示

**使い方:**

```bash
# 基本的な使い方（デフォルト: 10ページずつ処理）
python backend/split_pdf_reader.py "backend/static/pdfs/風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf"

# バッチサイズを指定（大きなPDFの場合は小さめに設定）
python backend/split_pdf_reader.py \
  "backend/static/pdfs/風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf" \
  --batch-size 5

# 出力ディレクトリを指定
python backend/split_pdf_reader.py \
  "backend/static/pdfs/風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf" \
  --batch-size 10 \
  --output-dir data/pdf_extracts

# PDF識別名を指定
python backend/split_pdf_reader.py \
  "backend/static/pdfs/風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf" \
  --batch-size 10 \
  --pdf-name "風営法施行規則"
```

**出力:**
- メインファイル: `pdf_extracted_<PDF名>_<タイムスタンプ>.json`
- チェックポイント: `checkpoints/checkpoint_<PDF名>_batch<番号>_<タイムスタンプ>.json`

### 2. `re_ocr_lecture_materials.py` - 講習テキスト専用（分割処理対応版）

講習テキストの再OCR処理用のスクリプトです。特定のPDFファイル（①.pdf、②.pdf、③.pdf）を処理します。

**特徴:**
- 🔧 講習テキスト専用
- 🔧 旧OCR結果との比較機能
- 🔧 差分分析機能
- ✅ バッチ分割処理対応

**使い方:**

```bash
# 基本的な使い方
python backend/re_ocr_lecture_materials.py

# バッチサイズを指定
python backend/re_ocr_lecture_materials.py --batch-size 15

# チェックポイントから再開
python backend/re_ocr_lecture_materials.py --resume
```

## 推奨設定

### バッチサイズの選び方

| PDFサイズ | 推奨バッチサイズ | 説明 |
|---------|----------------|------|
| < 1MB | 20-50ページ | 小さいPDFは大きめのバッチで高速処理 |
| 1-4MB | 10-20ページ | 中程度のPDFは標準設定 |
| > 4MB | 5-10ページ | 大きいPDFは小さめのバッチで安全に処理 |

### 現在のPDFファイル

```bash
# PDFファイルのサイズを確認
ls -lh backend/static/pdfs/
```

**例:**
- 風俗営業等の規制及び業務の適正化等に関する法律.pdf: 371KB → バッチサイズ 20-50
- 風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf: 4.0MB → **バッチサイズ 5-10（推奨）**

## トラブルシューティング

### 1. メモリ不足エラーが発生する場合

バッチサイズを小さくしてください:

```bash
python backend/split_pdf_reader.py "path/to/large.pdf" --batch-size 3
```

### 2. 処理が途中で止まった場合

チェックポイントファイルが保存されているので、そこから再開できます:

```bash
# 既存のチェックポイントを確認
ls -l checkpoints/

# 必要に応じて、保存されたチェックポイントから手動で結合可能
```

### 3. PyMuPDFがインストールされていない場合

```bash
pip install PyMuPDF
```

## 出力形式

すべてのツールは、以下の形式でJSON出力を生成します:

```json
[
  {
    "pdf_name": "風営法施行規則",
    "page_number": 1,
    "text": "抽出されたテキスト...",
    "char_count": 1234,
    "timestamp": "2025-11-09T12:34:56.789012",
    "extraction_method": "PyMuPDF_split"
  },
  ...
]
```

## ベストプラクティス

1. **大きなPDFは小さいバッチで処理**
   - 4MB以上のPDFは `--batch-size 5` から始める
   - エラーが出なければ徐々に増やす

2. **出力ディレクトリを整理**
   - プロジェクトごとに別のディレクトリを使用
   - タイムスタンプで自動的にバージョン管理される

3. **チェックポイントを活用**
   - 長時間の処理では定期的にチェックポイントを確認
   - エラー時は最新のチェックポイントから再開可能

4. **進捗を監視**
   - ログ出力で進捗を確認
   - 大きなPDFは時間がかかることを想定

## 例: 大きなPDF（4MB）を安全に処理

```bash
# ステップ1: PDFサイズを確認
ls -lh backend/static/pdfs/風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf

# ステップ2: 小さいバッチサイズで処理開始
python backend/split_pdf_reader.py \
  "backend/static/pdfs/風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf" \
  --batch-size 5 \
  --output-dir data/pdf_extracts \
  --pdf-name "風営法施行規則"

# ステップ3: 結果を確認
ls -l data/pdf_extracts/
cat data/pdf_extracts/pdf_extracted_風営法施行規則_*.json | jq '.[] | {page: .page_number, chars: .char_count}'
```

## まとめ

- 大きなPDFは `split_pdf_reader.py` を使用
- バッチサイズは5-10ページから始める
- チェックポイント機能で安全に処理
- エラー時は小さいバッチサイズで再試行

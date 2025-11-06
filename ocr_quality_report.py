#!/usr/bin/env python3
"""
OCR品質検査レポート
落丁・誤字・誤読をパターン分析
"""

import json
import re
from pathlib import Path
from collections import defaultdict

OCR_FILE = Path("/home/planj/patshinko-exam-app/data/ocr_results.json")

# ==================== 既知の誤字パターン ====================

COMMON_ERRORS = {
    # 漢字誤読（OCRがよく間違える）
    '遊技機': [
        '遊披機', '遊伎機', '遊技裁', '遊技缶', '遊技裁',
        '底技機', '遊実機', '作技機', '叙機', '遊敷機'
    ],
    '確認': ['稚認', '確怍', '撮認', '榷認'],
    '規制': ['親制', '被制', '規制'],
    '営業': ['営羽業', '営美業'],
    '業界': ['事葉', '事業界', '業笑'],
    '遊技': ['遊伎', '遊披'],
    '風俗': ['O風', '0風', 'O風俗'],
    '申請': ['申詰', '申涛'],
}

# ==================== 検査エンジン ====================

class OCRQualityAnalyzer:
    """OCR品質分析"""

    def __init__(self):
        self.issues = []
        self.stats = {
            'total_pages': 0,
            'total_chars': 0,
            'empty_pages': 0,
            'suspicious_chars': 0,
            'error_patterns': defaultdict(int)
        }

    def analyze(self):
        """全体分析"""
        with open(OCR_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)

        self.stats['total_pages'] = len(results)

        print("=" * 80)
        print("🔍 OCR品質検査レポート")
        print("=" * 80)

        # 各ページを検査
        for i, result in enumerate(results):
            self._check_page(i, result)

        # 統計表示
        self._print_statistics()

        # 誤字パターン分析
        self._print_error_patterns(results)

        # 詳細チェック
        self._detailed_check(results)

    def _check_page(self, page_idx, result):
        """1ページを検査"""
        text = result.get('text', '')
        self.stats['total_chars'] += len(text)

        if len(text) == 0:
            self.stats['empty_pages'] += 1
            self.issues.append({
                'severity': 'HIGH',
                'page': page_idx + 1,
                'issue': '空白ページ（テキスト抽出失敗）'
            })

    def _print_statistics(self):
        """統計情報出力"""
        print(f"\n📊 基本統計:")
        print(f"   総ページ数: {self.stats['total_pages']}")
        print(f"   総文字数: {self.stats['total_chars']:,}字")
        print(f"   平均文字数: {self.stats['total_chars'] // self.stats['total_pages']}字/ページ")
        print(f"   空白ページ: {self.stats['empty_pages']}")

    def _print_error_patterns(self, results):
        """誤字パターン分析"""
        print(f"\n⚠️ 検出された誤字パターン:")
        print("-" * 80)

        error_count = 0

        for correct_word, wrong_patterns in COMMON_ERRORS.items():
            for wrong_word in wrong_patterns:
                page_indices = []

                # 全ページから検索
                for i, result in enumerate(results):
                    text = result.get('text', '')
                    if wrong_word in text:
                        error_count += 1
                        if len(page_indices) < 3:  # 最初の3ページのみ記録
                            page_indices.append(i + 1)

                if page_indices:
                    print(f"\n『{wrong_word}』 → 『{correct_word}』に修正推奨")
                    print(f"   検出ページ: {page_indices}")

        if error_count == 0:
            print("   検出なし（良好）✅")

    def _detailed_check(self, results):
        """詳細チェック"""
        print(f"\n🔎 詳細チェック結果:")
        print("-" * 80)

        suspicious_count = 0
        issue_categories = defaultdict(int)

        for i, result in enumerate(results):
            text = result.get('text', '')

            # 疑わしい文字パターンをチェック
            issues = []

            # 1. 分かち書きがおかしい
            if re.search(r'[0-9]{2,}', text):  # 2桁以上の数字
                if re.search(r'[^\d\s][0-9]{2,}[^\d\s]', text):
                    issues.append('数字の周囲に空白なし')

            # 2. 句点が連続
            if '。。' in text or '、、' in text:
                issues.append('句点・読点が連続')

            # 3. 不自然な改行
            if text.count('\n') > 10 and len(text) < 500:
                issues.append('改行が多すぎる')

            # 4. 明らかな記号誤認
            if re.search(r'[OO0][^0-9a-zA-Z]', text):  # O（オー）と0（ゼロ）混同
                issues.append('O/0混同の可能性')

            if issues:
                for issue in issues:
                    issue_categories[issue] += 1
                    suspicious_count += 1

                if suspicious_count <= 5:  # 最初の5件のみ詳細表示
                    print(f"\nページ {i+1}:")
                    for issue in issues:
                        print(f"   ⚠️ {issue}")
                    preview = text[:80].replace('\n', ' ')
                    print(f"   内容: {preview}...")

        if suspicious_count == 0:
            print("   疑わしい個所: なし（良好）✅")
        else:
            print(f"\n   合計: {suspicious_count}ページで問題検出")

        if issue_categories:
            print(f"\n   問題カテゴリ:")
            for category, count in issue_categories.items():
                print(f"   - {category}: {count}件")

    def print_recommendations(self):
        """改善推奨"""
        print(f"\n💡 改善推奨:")
        print("-" * 80)
        print("""
1. 誤字修正: 検出された誤字パターンを自動置換で修正
   例) 遊披機 → 遊技機, 稚認 → 確認

2. 品質向上: より高いDPI設定で再OCR処理（推奨DPI: 200-300）

3. 手動確認: 重要な用語（法律用語など）は専門家による確認推奨

4. 学習データ構築: 誤字パターンを学習データとして蓄積し、
   将来の自動修正機能に活用
        """)

# ==================== 実行 ====================

if __name__ == '__main__':
    analyzer = OCRQualityAnalyzer()
    analyzer.analyze()
    analyzer.print_recommendations()

    print("\n" + "=" * 80)
    print("✅ 品質検査完了")
    print("=" * 80)

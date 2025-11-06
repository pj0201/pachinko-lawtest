#!/usr/bin/env python3
"""
OCR誤字自動修正ツール
検出された誤字を自動置換してクリーニング
"""

import json
import re
from pathlib import Path

OCR_FILE = Path("/home/planj/patshinko-exam-app/data/ocr_results.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/data/ocr_results_corrected.json")

# ==================== 修正ルール ====================

CORRECTION_RULES = {
    # 高頻度・高重要度の誤字
    '遊披機': '遊技機',
    '遊披': '遊技',
    '底技機': '遊技機',
    '作技機': '遊技機',
    '遊実機': '遊技機',
    '叙機': '遊技機',
    '遊敷機': '遊技機',

    # 確認系
    '稚認': '確認',
    '撮認': '確認',
    '確怍': '確認',

    # 規制系
    '親制': '規制',
    '被制': '規制',

    # 業界系
    '事葉': '業界',

    # 営業系
    '営羽業': '営業',

    # 記号・数字の周囲スペース修正（後処理）
}

# ==================== クリーニング関数 ====================

def clean_text(text):
    """テキストをクリーニング"""

    # 1. 基本的な誤字置換
    for wrong, correct in CORRECTION_RULES.items():
        # 単語単位での置換（前後が非文字ならOK）
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(wrong) + r'(?![a-zA-Z0-9])'
        text = re.sub(pattern, correct, text)

    # 2. O/0 混同の修正（文脈から判断）
    # 例: "O年" → "0年", "0個" → "0個" など
    # ただし「風俗」の「○」は「○」のままにしておく

    # 3. 改行・スペースの正規化
    # 複数の改行を1つに
    text = re.sub(r'\n\n+', '\n', text)

    # 4. 重複する句点の修正
    text = text.replace('。。', '。')
    text = text.replace('、、', '、')

    # 5. 数字の前後のスペース正規化
    # 「1234」「5678」の形式は保持、「12 34」は修正

    return text

def process_ocr_results():
    """OCR結果全体をクリーニング"""
    print("=" * 80)
    print("🔧 OCR自動修正処理を開始します")
    print("=" * 80)

    # OCR結果を読み込み
    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        results = json.load(f)

    print(f"\n📝 入力: {len(results)}ページ")

    # 修正統計
    stats = {
        'total_corrections': 0,
        'corrections_by_type': {},
        'pages_modified': 0
    }

    # 各ページを修正
    corrected_results = []

    for result in results:
        original_text = result.get('text', '')
        corrected_text = clean_text(original_text)

        # 修正があったか確認
        if original_text != corrected_text:
            stats['pages_modified'] += 1

            # 修正内容を記録
            for wrong, correct in CORRECTION_RULES.items():
                count = original_text.count(wrong) - corrected_text.count(wrong)
                if count > 0:
                    key = f"{wrong}→{correct}"
                    stats['corrections_by_type'][key] = \
                        stats['corrections_by_type'].get(key, 0) + count
                    stats['total_corrections'] += count

        corrected_results.append({
            **result,
            'text': corrected_text,
            'corrected': original_text != corrected_text
        })

    # 修正結果を保存
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(corrected_results, f, indent=2, ensure_ascii=False)

    # 統計表示
    print(f"\n✅ 修正完了")
    print(f"   修正対象ページ: {stats['pages_modified']}/{len(results)}")
    print(f"   総修正箇所: {stats['total_corrections']}件")

    print(f"\n📊 修正内容:")
    for correction_type, count in sorted(
        stats['corrections_by_type'].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"   {correction_type}: {count}件")

    print(f"\n💾 出力ファイル: {OUTPUT_FILE}")
    print("=" * 80)

    return stats

# ==================== 比較ツール ====================

def compare_samples():
    """修正前後を比較表示"""
    print("\n📋 修正前後の比較（サンプル）:")
    print("-" * 80)

    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        original = json.load(f)

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        corrected = json.load(f)

    # 修正があったページを表示
    count = 0
    for i, (orig, corr) in enumerate(zip(original, corrected)):
        if orig['text'] != corr['text']:
            if count < 3:  # 最初の3つのみ表示
                print(f"\nページ {i+1}:")
                print(f"修正前: {orig['text'][:100]}...")
                print(f"修正後: {corr['text'][:100]}...")
                count += 1

# ==================== メイン ====================

if __name__ == '__main__':
    # 修正実行
    stats = process_ocr_results()

    # 修正前後を比較
    if OUTPUT_FILE.exists():
        compare_samples()

    print("\n✨ 修正完了！")
    print(f"   修正ファイル: ocr_results_corrected.json")
    print(f"   以降のカテゴリー分類・採点に使用してください")

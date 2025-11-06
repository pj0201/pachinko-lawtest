#!/usr/bin/env python3
"""
カテゴリー分類エンジン
OCR結果を主任者試験の標準カテゴリーに分類
"""

import json
from collections import defaultdict
from pathlib import Path

# ==================== カテゴリー定義 ====================

CATEGORIES = {
    '法律知識': {
        'keywords': [
            '風俗営業法', '法律', '法令', '法規', '規定', '規則',
            '風俗営業', '営業禁止', '禁止', '許可', '申請', '期限',
            '罰則', '刑罰', '違反', '罰金', '懲役', '要件'
        ],
        'weight': 1.0
    },
    '営業管理': {
        'keywords': [
            '営業', 'ホール', '店舗', '業務', '管理', '運営',
            '従業員', 'スタッフ', 'アルバイト', 'シフト',
            '帳簿', '記録', '報告', '申告', '申請書', '更新',
            '許可申請', '更新申請', 'コンプライアンス', 'チェック',
            '営業時間', '営業区域', '営業日', '営業所', '看板'
        ],
        'weight': 0.9
    },
    '機械知識': {
        'keywords': [
            '遊技機', 'パチンコ', 'パチスロ', 'スロット', '機械',
            '機器', 'メダル', 'ボール', '玉', '台', '台数',
            '設置', '撤去', '交換', '修理', 'メンテナンス',
            '型式', '認定', '認可', '基準', '仕様', '性能',
            '部品', '動作', '機能', 'プログラム', 'ROM', '検定'
        ],
        'weight': 1.0
    },
    '営業開始': {
        'keywords': [
            '開始', '開業', '新規', '新設', '開設', '起業',
            '資格', '申請', 'チェック', '条件', '要件', '基準'
        ],
        'weight': 0.7
    }
}

# ==================== テキスト前処理 ====================

def preprocess_text(text):
    """テキストを正規化"""
    # 改行を空白に置換
    text = text.replace('\n', ' ').replace('\r', ' ')
    # 複数の空白を1つに
    text = ' '.join(text.split())
    # 小文字に統一（ただし日本語は保持）
    return text

# ==================== キーワードマッチング ====================

def calculate_keyword_score(text, category_keywords):
    """キーワードマッチングスコアを計算"""
    text_lower = text.lower()
    score = 0
    matches = []

    for keyword in category_keywords:
        keyword_lower = keyword.lower()
        count = text.count(keyword_lower)

        if count > 0:
            # 出現回数 × キーワード長 でスコア化
            # （長いキーワードの方が重要）
            keyword_score = count * (len(keyword) / 5)
            score += keyword_score
            matches.append({
                'keyword': keyword,
                'count': count,
                'score': keyword_score
            })

    return score, matches

# ==================== TF-IDF 風スコアリング ====================

def calculate_tfidf_score(text, category_keywords):
    """TF-IDF風のスコアを計算"""
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0, []

    score = 0
    term_frequencies = {}

    # Term Frequency (TF) 計算
    for word in words:
        word_lower = word.lower()
        term_frequencies[word_lower] = term_frequencies.get(word_lower, 0) + 1

    # カテゴリーキーワードとの照合
    matches = []
    for keyword in category_keywords:
        keyword_lower = keyword.lower()

        # 完全一致
        if keyword_lower in term_frequencies:
            tf = term_frequencies[keyword_lower] / word_count
            idf = 1.0 / len(category_keywords)  # 簡易IDF
            tfidf = tf * idf
            score += tfidf
            matches.append({
                'keyword': keyword,
                'tf': tf,
                'tfidf': tfidf
            })

        # 部分一致（2文字以上）
        elif len(keyword_lower) >= 2:
            for word, count in term_frequencies.items():
                if keyword_lower in word:
                    tf = count / word_count
                    partial_score = tf * 0.5  # 部分一致は50%のスコア
                    score += partial_score
                    if not any(m['keyword'] == keyword for m in matches):
                        matches.append({
                            'keyword': keyword,
                            'partial_match': word,
                            'score': partial_score
                        })

    return score, matches

# ==================== カテゴリー判定エンジン ====================

class CategoryClassifier:
    """問題文をカテゴリーに分類"""

    def __init__(self):
        self.categories = CATEGORIES

    def classify(self, text):
        """テキストをカテゴリーに分類"""
        if not text or len(text.strip()) < 5:
            return 'その他', 0.0, {}

        # テキスト前処理
        clean_text = preprocess_text(text)

        # 各カテゴリーのスコアを計算
        scores = {}
        details = {}

        for category, config in self.categories.items():
            # キーワードマッチングスコア
            kw_score, kw_matches = calculate_keyword_score(
                clean_text,
                config['keywords']
            )

            # TF-IDF スコア
            tfidf_score, tfidf_matches = calculate_tfidf_score(
                clean_text,
                config['keywords']
            )

            # 最終スコア（重み付け）
            final_score = (kw_score * 0.6 + tfidf_score * 0.4) * config['weight']

            scores[category] = final_score
            details[category] = {
                'keyword_score': kw_score,
                'tfidf_score': tfidf_score,
                'final_score': final_score,
                'keyword_matches': kw_matches[:5],  # Top 5
                'tfidf_matches': tfidf_matches[:3]  # Top 3
            }

        # 最高スコアのカテゴリーを選択
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        # スコアが全て低い場合は「その他」に分類
        if best_score < 0.1:
            best_category = 'その他'
            best_score = 0.0

        return best_category, best_score, details

    def classify_questions(self, questions):
        """複数の問題をカテゴリーに分類"""
        classified = []

        for q in questions:
            category, score, details = self.classify(q.get('text', ''))

            classified.append({
                **q,
                'category': category,
                'category_confidence': round(score, 3),
                'classification_details': details
            })

        return classified

# ==================== 統計情報生成 ====================

def generate_statistics(classified_questions):
    """カテゴリー別統計を生成"""
    stats = defaultdict(lambda: {'count': 0, 'avg_confidence': 0})

    for q in classified_questions:
        category = q['category']
        stats[category]['count'] += 1
        stats[category]['avg_confidence'] += q['category_confidence']

    # 平均信頼度を計算
    for category in stats:
        count = stats[category]['count']
        if count > 0:
            stats[category]['avg_confidence'] /= count
            stats[category]['avg_confidence'] = round(stats[category]['avg_confidence'], 3)

    return dict(stats)

# ==================== メイン処理 ====================

def process_ocr_results(ocr_results_file, output_file):
    """OCR結果を分類・統計化"""
    print("=" * 70)
    print("🔍 カテゴリー分類処理を開始します")
    print("=" * 70)

    # OCR結果を読み込み
    with open(ocr_results_file, 'r', encoding='utf-8') as f:
        ocr_results = json.load(f)

    print(f"\n📊 入力: {len(ocr_results)}ページのOCR結果")

    # 問題を抽出（テキストからシンプルに分割）
    from ocrToQuestions import extractQuestionsFromOCR
    questions = extractQuestionsFromOCR(ocr_results)

    print(f"✅ 抽出問題: {len(questions)}問")

    # カテゴリー分類
    classifier = CategoryClassifier()
    classified = classifier.classify_questions(questions)

    # 統計情報生成
    stats = generate_statistics(classified)

    print(f"\n📈 カテゴリー別分布:")
    for category, info in stats.items():
        print(f"   {category}: {info['count']}問 (信頼度: {info['avg_confidence']:.1%})")

    # 結果を保存
    output_data = {
        'timestamp': str(__import__('datetime').datetime.now().isoformat()),
        'total_questions': len(classified),
        'statistics': stats,
        'questions': classified
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 分類結果保存: {output_file}")
    print("=" * 70)

    return output_data

# ==================== テスト用 ====================

if __name__ == '__main__':
    import sys

    ocr_file = sys.argv[1] if len(sys.argv) > 1 else '/home/planj/patshinko-exam-app/data/ocr_results.json'
    output = sys.argv[2] if len(sys.argv) > 2 else '/home/planj/patshinko-exam-app/data/classified_questions.json'

    if Path(ocr_file).exists():
        process_ocr_results(ocr_file, output)
    else:
        print(f"❌ ファイルが見つかりません: {ocr_file}")

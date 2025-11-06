#!/usr/bin/env python3
"""
ひっかけ強度制御ロジック v1.0

ディストラクタ（不正答肢）の品質を計測・制御するシステム
BERT埋め込みとコサイン類似度を用いて、選択肢の相似性を定量化
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum

# ====================================================================
# 定義：難易度レベルとひっかけ強度
# ====================================================================

class DifficultyLevel(Enum):
    """試験問題の難易度レベル"""
    BASIC = "基礎"      # 基本知識の理解
    STANDARD = "標準"   # 実務的な判断
    ADVANCED = "応用"   # 複合的・高度な判断

class DistractorStrength(Enum):
    """ひっかけ強度のレベル"""
    NONE = "なし"        # 0-20:     明らかに誤り、ひっかけなし
    WEAK = "弱"         # 20-40:    初級向け
    MODERATE = "中"     # 40-60:    標準向け
    STRONG = "強"       # 60-80:    応用向け
    VERY_STRONG = "超強" # 80-100:   超上級向け（使用禁止）

# ====================================================================
# データ構造
# ====================================================================

@dataclass
class DistractorMetrics:
    """ディストラクタ（不正答肢）の計測結果"""

    # 基本情報
    distractor_text: str          # ディストラクタの文字列
    correct_answer_text: str      # 正答肢の文字列

    # 相似度計測
    cosine_similarity: float       # コサイン類似度 (0.0-1.0)
    distractor_score: float        # ひっかけスコア (0-100)

    # 分類
    strength_level: DistractorStrength
    is_appropriate: bool           # 難易度に対して適切か

    # 詳細分析
    shared_keywords: List[str]     # 共有キーワード
    critical_difference: str       # 関鍵的な違い

    def __repr__(self):
        return (f"DistractorMetrics("
                f"score={self.distractor_score:.1f}, "
                f"strength={self.strength_level.value}, "
                f"appropriate={self.is_appropriate})")

@dataclass
class QuestionQuality:
    """問題全体の品質評価"""

    problem_id: str
    difficulty: DifficultyLevel
    problem_text: str
    correct_answer: str

    # ディストラクタ群
    distractors: List[DistractorMetrics]

    # 品質指標
    average_distractor_score: float
    distractor_strength_distribution: Dict[str, int]
    overall_quality_score: float   # 0.0-1.0

    # 推奨事項
    recommendations: List[str]

    def is_quality_approved(self, min_score=0.65) -> bool:
        """品質合格判定"""
        return self.overall_quality_score >= min_score

# ====================================================================
# ひっかけスコア計算エンジン
# ====================================================================

class DistractorControlEngine:
    """
    ディストラクタ品質を計測・制御するエンジン

    アルゴリズム：
    1. 正答肢とディストラクタをBERT埋め込みに変換
    2. コサイン類似度を計算: sim ∈ [0, 1]
    3. ひっかけスコア = (1 - sim) × 100
    4. 難易度に対して適切か判定
    5. 改善提案を生成
    """

    # ひっかけスコア → 強度レベルのマッピング
    STRENGTH_THRESHOLDS = {
        20: DistractorStrength.NONE,
        40: DistractorStrength.WEAK,
        60: DistractorStrength.MODERATE,
        80: DistractorStrength.STRONG,
        100: DistractorStrength.VERY_STRONG,
    }

    # 難易度別の推奨ひっかけスコア範囲
    RECOMMENDED_RANGES = {
        DifficultyLevel.BASIC: (10, 20),      # 弱いひっかけ
        DifficultyLevel.STANDARD: (30, 40),   # 中程度
        DifficultyLevel.ADVANCED: (40, 50),   # 強いひっかけ
    }

    def __init__(self, use_bert: bool = False):
        """
        初期化

        Args:
            use_bert: BERT埋め込みを使用するか
                     Falseの場合はシミュレーションモードで動作
        """
        self.use_bert = use_bert
        self.embedding_model = None

        if use_bert:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(
                    'paraphrase-MiniLM-L6-v2'
                )
            except ImportError:
                print("⚠️  BERT not available. Using simulation mode.")
                self.use_bert = False

    def calculate_distractor_score(
        self,
        correct_answer: str,
        distractor: str
    ) -> Tuple[float, float]:
        """
        ディストラクタのひっかけスコアを計算

        Args:
            correct_answer: 正答肢のテキスト
            distractor: ディストラクタのテキスト

        Returns:
            (コサイン類似度, ひっかけスコア)

        計算式：
            similarity = コサイン類似度（BERT埋め込み）
            distractor_score = (1 - similarity) × 100
        """
        if self.use_bert and self.embedding_model:
            # BERT埋め込みを使用
            embedding_a = self.embedding_model.encode(correct_answer)
            embedding_d = self.embedding_model.encode(distractor)

            # コサイン類似度を計算
            cosine_sim = self._cosine_similarity(embedding_a, embedding_d)
        else:
            # シミュレーションモード：キーワード共有度で推定
            cosine_sim = self._simulate_similarity(correct_answer, distractor)

        distractor_score = (1 - cosine_sim) * 100

        return cosine_sim, distractor_score

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """コサイン類似度を計算"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def _simulate_similarity(text1: str, text2: str) -> float:
        """
        テキストの類似度をシミュレート
        （実際のBERT使用時の代替）

        共有キーワード数に基づいて推定
        """
        words1 = set(text1.split())
        words2 = set(text2.split())

        intersection = words1 & words2
        union = words1 | words2

        if len(union) == 0:
            return 0.0

        # Jaccard類似度を返す
        return len(intersection) / len(union)

    def get_strength_level(self, distractor_score: float) -> DistractorStrength:
        """ひっかけスコアから強度レベルを判定"""
        for threshold, level in sorted(self.STRENGTH_THRESHOLDS.items()):
            if distractor_score < threshold:
                return level
        return DistractorStrength.VERY_STRONG

    def is_appropriate_for_difficulty(
        self,
        distractor_score: float,
        difficulty: DifficultyLevel
    ) -> bool:
        """
        ディストラクタがその難易度に適しているか判定

        Args:
            distractor_score: ひっかけスコア (0-100)
            difficulty: 問題の難易度

        Returns:
            True if 推奨範囲内、False if 範囲外
        """
        min_score, max_score = self.RECOMMENDED_RANGES[difficulty]
        return min_score <= distractor_score <= max_score

    def analyze_distractor(
        self,
        correct_answer: str,
        distractor: str,
        difficulty: DifficultyLevel
    ) -> DistractorMetrics:
        """
        1つのディストラクタを詳細分析

        Returns:
            DistractorMetrics: 詳細な計測結果
        """
        # スコア計算
        cosine_sim, distractor_score = self.calculate_distractor_score(
            correct_answer, distractor
        )

        # 強度判定
        strength = self.get_strength_level(distractor_score)

        # 適切性判定
        is_appropriate = self.is_appropriate_for_difficulty(
            distractor_score, difficulty
        )

        # キーワード分析
        correct_words = set(correct_answer.split())
        distractor_words = set(distractor.split())
        shared_keywords = list(correct_words & distractor_words)
        critical_difference = " ".join(
            distractor_words - correct_words
        ) if distractor_words - correct_words else "完全に異なる"

        return DistractorMetrics(
            distractor_text=distractor,
            correct_answer_text=correct_answer,
            cosine_similarity=cosine_sim,
            distractor_score=distractor_score,
            strength_level=strength,
            is_appropriate=is_appropriate,
            shared_keywords=shared_keywords,
            critical_difference=critical_difference
        )

    def analyze_question(
        self,
        problem_id: str,
        problem_text: str,
        correct_answer: str,
        distractors: List[str],
        difficulty: DifficultyLevel
    ) -> QuestionQuality:
        """
        問題全体の品質を分析

        Args:
            problem_id: 問題ID
            problem_text: 問題文
            correct_answer: 正答肢
            distractors: ディストラクタリスト
            difficulty: 難易度

        Returns:
            QuestionQuality: 問題全体の品質評価
        """
        # 各ディストラクタを分析
        distractor_metrics = []
        for dist in distractors:
            metrics = self.analyze_distractor(
                correct_answer, dist, difficulty
            )
            distractor_metrics.append(metrics)

        # 統計計算
        scores = [m.distractor_score for m in distractor_metrics]
        avg_score = np.mean(scores) if scores else 0

        strength_dist = {}
        for metrics in distractor_metrics:
            level = metrics.strength_level.value
            strength_dist[level] = strength_dist.get(level, 0) + 1

        # 品質スコア計算
        #   適切性: 全ディストラクタが推奨範囲内か
        #   多様性: 複数の強度レベルが含まれているか
        appropriateness = sum(
            1 for m in distractor_metrics if m.is_appropriate
        ) / len(distractor_metrics) if distractor_metrics else 0

        diversity = len(strength_dist) / len(self.STRENGTH_THRESHOLDS)

        overall_quality = (appropriateness * 0.7 + diversity * 0.3)

        # 改善提案を生成
        recommendations = self._generate_recommendations(
            distractor_metrics, difficulty
        )

        return QuestionQuality(
            problem_id=problem_id,
            difficulty=difficulty,
            problem_text=problem_text,
            correct_answer=correct_answer,
            distractors=distractor_metrics,
            average_distractor_score=avg_score,
            distractor_strength_distribution=strength_dist,
            overall_quality_score=overall_quality,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        metrics_list: List[DistractorMetrics],
        difficulty: DifficultyLevel
    ) -> List[str]:
        """改善提案を生成"""
        recommendations = []

        inappropriate = [m for m in metrics_list if not m.is_appropriate]
        if inappropriate:
            scores_str = ", ".join(
                f"{m.distractor_score:.0f}" for m in inappropriate
            )
            min_s, max_s = self.RECOMMENDED_RANGES[difficulty]
            recommendations.append(
                f"⚠️  {len(inappropriate)}個のディストラクタが推奨範囲外 "
                f"({min_s}-{max_s}): スコア {scores_str}"
            )

        if not metrics_list:
            recommendations.append("❌ ディストラクタが定義されていません")
        elif len(metrics_list) < 2:
            recommendations.append("⚠️  ディストラクタの数が少なすぎます（最低2個）")

        very_weak = [m for m in metrics_list
                     if m.distractor_score < 10]
        if very_weak:
            recommendations.append(
                f"💡 {len(very_weak)}個が完全に誤った選択肢です。"
                "より微妙なひっかけが必要な場合は検討してください"
            )

        return recommendations

# ====================================================================
# 使用例
# ====================================================================

def example_basic_analysis():
    """基本的な使用例"""
    print("=" * 70)
    print("【ひっかけ強度制御 - 基本例】")
    print("=" * 70)

    engine = DistractorControlEngine(use_bert=False)  # シミュレーションモード

    # テスト問題
    problem = {
        "id": "Q001",
        "text": "営業許可の有効期間について、次の説明は正しいか",
        "correct": "営業許可は無期限で有効である",
        "distractors": [
            "営業許可は3年で失効し、更新が必要である",
            "営業許可は5年で自動失効する",
            "営業許可は10年で更新が必要である"
        ],
        "difficulty": DifficultyLevel.BASIC
    }

    # 分析実行
    result = engine.analyze_question(
        problem_id=problem["id"],
        problem_text=problem["text"],
        correct_answer=problem["correct"],
        distractors=problem["distractors"],
        difficulty=problem["difficulty"]
    )

    # 結果表示
    print(f"\n📋 問題: {result.problem_id}")
    print(f"難易度: {result.difficulty.value}")
    print(f"\n✓ 正答肢: {result.correct_answer}\n")

    print("【ディストラクタ分析】")
    for i, metrics in enumerate(result.distractors, 1):
        status = "✓ 適切" if metrics.is_appropriate else "✗ 不適切"
        print(f"\n  {i}. {metrics.distractor_text[:50]}...")
        print(f"     スコア: {metrics.distractor_score:.1f}")
        print(f"     強度: {metrics.strength_level.value} {status}")
        if metrics.shared_keywords:
            print(f"     共有キーワード: {', '.join(metrics.shared_keywords)}")

    print(f"\n【品質評価】")
    print(f"  平均スコア: {result.average_distractor_score:.1f}")
    print(f"  全体品質: {result.overall_quality_score:.2f} "
          f"({'合格 ✓' if result.is_quality_approved() else '不合格 ✗'})")

    if result.recommendations:
        print(f"\n【改善提案】")
        for rec in result.recommendations:
            print(f"  {rec}")
    else:
        print(f"\n【改善提案】")
        print(f"  なし - 高品質 ✓")

if __name__ == "__main__":
    example_basic_analysis()

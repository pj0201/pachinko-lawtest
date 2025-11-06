#!/usr/bin/env python3
"""
風営法理解度チェック - バックエンド API サーバー
修正済み問題集（problems_final_500_complete.json）を提供
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import random
from pathlib import Path

# Flask アプリ初期化
app = Flask(__name__)
CORS(app)  # CORS 有効化

# 問題集ファイルパス
PROBLEMS_FILE = Path(__file__).parent / "problems_final_500_complete.json"

# グローバル変数
problems_data = []

def load_problems():
    """修正済み問題集を読み込む"""
    global problems_data
    try:
        with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
            problems_data = json.load(f)
        print(f"✅ {len(problems_data)}問の問題集を読み込みました")
        return True
    except Exception as e:
        print(f"❌ 問題集の読み込みエラー: {e}")
        return False

# ===== API エンドポイント =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'ok',
        'message': 'API サーバーが起動しています',
        'problems_loaded': len(problems_data)
    })

@app.route('/api/problems/quiz', methods=['POST'])
def get_quiz_problems():
    """
    模擬試験用の問題を取得

    リクエスト:
    {
        "count": 10,  // 問題数
        "difficulty": "★"  // 難易度（★, ★★, ★★★）
    }

    レスポンス:
    {
        "problems": [
            {
                "problem_id": 1,
                "problem_text": "...",
                "correct_answer": "○",
                "explanation": "...",
                "category": "営業許可",
                "difficulty": "★",
                "pattern_name": "基本知識",
                ...
            }
        ]
    }
    """
    try:
        data = request.get_json() or {}

        # パラメータ取得
        count = data.get('count', 10)
        difficulty = data.get('difficulty', '★★')

        # パラメータ検証
        if not isinstance(count, int) or count < 1 or count > 100:
            count = 10

        if difficulty not in ['★', '★★', '★★★']:
            difficulty = '★★'

        # 問題のフィルタリング
        filtered = [p for p in problems_data if p.get('difficulty') == difficulty]

        # フィルタ結果がない場合は全問題から選択
        if not filtered:
            filtered = problems_data

        # ランダムに問題を選択
        selected = random.sample(filtered, min(count, len(filtered)))

        return jsonify({
            'status': 'success',
            'problems': selected,
            'count': len(selected)
        })

    except Exception as e:
        print(f"❌ エラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/problems/all', methods=['GET'])
def get_all_problems():
    """全問題を取得（デバッグ用）"""
    try:
        return jsonify({
            'status': 'success',
            'problems': problems_data,
            'count': len(problems_data)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/problems/stats', methods=['GET'])
def get_problems_stats():
    """問題集の統計情報を取得"""
    try:
        stats = {
            'total': len(problems_data),
            'by_difficulty': {},
            'by_category': {},
            'with_revisions': {
                'stage1': 0,
                'stage2': 0,
                'both': 0
            }
        }

        # 難易度別カウント
        for p in problems_data:
            difficulty = p.get('difficulty', '未分類')
            stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1

            # カテゴリ別カウント
            category = p.get('category', '未分類')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

            # 修正情報カウント
            revisions = p.get('revision_notes', {})
            if revisions.get('language_correction'):
                stats['with_revisions']['stage1'] += 1
            if revisions.get('structure_correction'):
                stats['with_revisions']['stage2'] += 1
            if revisions.get('language_correction') and revisions.get('structure_correction'):
                stats['with_revisions']['both'] += 1

        return jsonify({
            'status': 'success',
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/problems/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    """特定の問題を取得"""
    try:
        problem = next((p for p in problems_data if p.get('problem_id') == problem_id), None)

        if not problem:
            return jsonify({
                'status': 'error',
                'message': f'問題 ID {problem_id} が見つかりません'
            }), 404

        return jsonify({
            'status': 'success',
            'problem': problem
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ===== エラーハンドラ =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'エンドポイントが見つかりません'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'サーバーエラーが発生しました'
    }), 500

# ===== メイン処理 =====

if __name__ == '__main__':
    # 問題集を読み込み
    if not load_problems():
        print("❌ 問題集の読み込みに失敗しました")
        exit(1)

    print("=" * 80)
    print("【風営法理解度チェック - バックエンド API】")
    print("=" * 80)
    print(f"✅ 問題集: {PROBLEMS_FILE}")
    print(f"✅ 総問題数: {len(problems_data)}")
    print(f"✅ ポート: 5001")
    print("=" * 80)

    # Flask サーバー起動
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False
    )

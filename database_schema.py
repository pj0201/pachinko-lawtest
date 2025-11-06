#!/usr/bin/env python3
"""
SQLiteデータベーススキーマ設計
問題・テスト結果・採点情報を効率的に格納
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/home/planj/patshinko-exam-app/data/patshinko_exam.db")

# ==================== スキーマ定義 ====================

SCHEMA_SQL = """
-- ==================== 問題テーブル ====================

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    category TEXT NOT NULL,
    text TEXT NOT NULL,
    options TEXT NOT NULL,  -- JSON形式で選択肢を保存
    difficulty TEXT DEFAULT 'medium',  -- easy, medium, hard
    is_auto_generated INTEGER DEFAULT 1,  -- OCRから自動生成した場合は1
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_pdf ON questions(pdf_index, page_number);

-- ==================== テスト結果テーブル ====================

CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'anonymous',
    session_id TEXT,
    total_questions INTEGER NOT NULL,
    answered_questions INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    incorrect_count INTEGER NOT NULL,
    unanswered_count INTEGER DEFAULT 0,
    accuracy_percent INTEGER,
    completion_time_seconds INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_test_results_user ON test_results(user_id);
CREATE INDEX IF NOT EXISTS idx_test_results_date ON test_results(completed_at);

-- ==================== 回答結果テーブル ====================

CREATE TABLE IF NOT EXISTS test_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_result_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct INTEGER,
    response_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_result_id) REFERENCES test_results(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE INDEX IF NOT EXISTS idx_test_answers_result ON test_answers(test_result_id);
CREATE INDEX IF NOT EXISTS idx_test_answers_question ON test_answers(question_id);

-- ==================== カテゴリー別成績テーブル ====================

CREATE TABLE IF NOT EXISTS category_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_result_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    accuracy_percent INTEGER,
    FOREIGN KEY (test_result_id) REFERENCES test_results(id)
);

CREATE INDEX IF NOT EXISTS idx_category_stats_test ON category_stats(test_result_id);
CREATE INDEX IF NOT EXISTS idx_category_stats_category ON category_stats(category);

-- ==================== 学習記録テーブル ====================

CREATE TABLE IF NOT EXISTS learning_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'anonymous',
    question_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    attempts INTEGER DEFAULT 1,
    correct_attempts INTEGER DEFAULT 0,
    last_accuracy_percent INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE INDEX IF NOT EXISTS idx_learning_history_user ON learning_history(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_history_question ON learning_history(question_id);

-- ==================== ユーザー統計テーブル ====================

CREATE TABLE IF NOT EXISTS user_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    total_tests INTEGER DEFAULT 0,
    total_questions_answered INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    overall_accuracy_percent INTEGER DEFAULT 0,
    favorite_category TEXT,
    weakest_category TEXT,
    last_test_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== メタデータテーブル ====================

CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- メタデータのサンプル（初期値）
INSERT OR IGNORE INTO metadata (key, value) VALUES
    ('db_version', '1.0'),
    ('last_ocr_update', NULL),
    ('total_questions_count', '0'),
    ('categories', '法律知識,営業管理,機械知識,営業開始'),
    ('app_version', '1.0.0');
"""

# ==================== データベース操作クラス ====================

class DatabaseManager:
    """データベース操作"""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """データベースを初期化"""
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # スキーマを実行
        cursor.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()

        print(f"✅ データベース初期化完了: {self.db_path}")

    def execute(self, sql, params=None, fetchall=False):
        """SQLを実行"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 辞書形式で返す
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            if fetchall:
                result = cursor.fetchall()
            elif "SELECT" in sql.upper():
                result = cursor.fetchone()
            else:
                result = cursor.lastrowid

            conn.commit()
            return result

        except sqlite3.Error as e:
            print(f"❌ SQL実行エラー: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def insert_questions(self, questions_data):
        """問題をバッチ挿入"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for q in questions_data:
                cursor.execute("""
                    INSERT INTO questions
                    (pdf_index, page_number, category, text, options, difficulty, is_auto_generated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    q.get('pdf_index'),
                    q.get('page_number'),
                    q.get('category', 'その他'),
                    q.get('text'),
                    json.dumps(q.get('options', []), ensure_ascii=False),
                    q.get('difficulty', 'medium'),
                    1  # OCRから自動生成
                ))

            conn.commit()
            print(f"✅ {len(questions_data)}問の問題を挿入しました")
            return len(questions_data)

        except sqlite3.Error as e:
            print(f"❌ 挿入エラー: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def insert_test_result(self, test_data):
        """テスト結果を挿入"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO test_results
                (user_id, total_questions, answered_questions, correct_count,
                 incorrect_count, unanswered_count, accuracy_percent, completion_time_seconds,
                 started_at, completed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_data.get('user_id', 'anonymous'),
                test_data['total_questions'],
                test_data['answered_questions'],
                test_data['correct_count'],
                test_data['incorrect_count'],
                test_data.get('unanswered_count', 0),
                test_data.get('accuracy_percent'),
                test_data.get('completion_time_seconds'),
                test_data.get('started_at'),
                datetime.now().isoformat(),
                test_data.get('notes')
            ))

            test_result_id = cursor.lastrowid
            conn.commit()

            print(f"✅ テスト結果を挿入しました (ID: {test_result_id})")
            return test_result_id

        except sqlite3.Error as e:
            print(f"❌ 挿入エラー: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def insert_answers(self, test_result_id, answers_data):
        """回答結果をバッチ挿入"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for ans in answers_data:
                cursor.execute("""
                    INSERT INTO test_answers
                    (test_result_id, question_id, user_answer, correct_answer, is_correct, response_time_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    test_result_id,
                    ans.get('question_id'),
                    ans.get('user_answer'),
                    ans.get('correct_answer'),
                    1 if ans.get('is_correct') else 0,
                    ans.get('response_time_seconds')
                ))

            conn.commit()
            print(f"✅ {len(answers_data)}件の回答を挿入しました")
            return len(answers_data)

        except sqlite3.Error as e:
            print(f"❌ 挿入エラー: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def insert_category_stats(self, test_result_id, category_stats):
        """カテゴリー別成績を挿入"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for category, stats in category_stats.items():
                cursor.execute("""
                    INSERT INTO category_stats
                    (test_result_id, category, total_questions, correct_count, accuracy_percent)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    test_result_id,
                    category,
                    stats.get('total'),
                    stats.get('correct'),
                    stats.get('accuracy_percent')
                ))

            conn.commit()
            print(f"✅ {len(category_stats)}カテゴリーの成績を挿入しました")
            return len(category_stats)

        except sqlite3.Error as e:
            print(f"❌ 挿入エラー: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def get_question_count(self):
        """問題総数を取得"""
        result = self.execute("SELECT COUNT(*) as count FROM questions")
        return result['count'] if result else 0

    def get_questions_by_category(self, category):
        """カテゴリーで問題を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM questions WHERE category = ?
            ORDER BY pdf_index, page_number
        """, (category,))

        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]

    def get_user_statistics(self, user_id):
        """ユーザー統計を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM user_statistics WHERE user_id = ?
        """, (user_id,))

        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def update_metadata(self, key, value):
        """メタデータを更新"""
        return self.execute("""
            UPDATE metadata SET value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE key = ?
        """, (value, key))

# ==================== テスト ====================

if __name__ == '__main__':
    # データベース初期化
    db = DatabaseManager()

    # 統計情報表示
    print(f"\n📊 データベース情報:")
    print(f"   問題総数: {db.get_question_count()}")

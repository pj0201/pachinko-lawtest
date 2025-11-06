#!/usr/bin/env python3
"""
高品質解説生成スクリプト v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RAG（Retrieval-Augmented Generation）を使用して、
各試験問題に法令参照・学習ポイント・具体的解説を自動生成します。

方針:
✅ 風営法DB（RAG）から関連法令を検索
✅ GPT-5 miniで法令ベースの解説を生成
✅ テンプレート表現を完全排除
✅ 品質最優先（時間無制限）

処理フロー:
1. JSON読み込み
2. 各問題の分類・メタ情報抽出
3. RAGで関連法令検索
4. GPT-5で解説生成
5. 出力ファイル作成
"""

import json
import os
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI

# === 初期化 ===
REPO_ROOT = Path("/home/planj/patshinko-exam-app")
PROBLEMS_FILE = REPO_ROOT / "backend/problems_final_500_fixed.json"
RAG_DATA = REPO_ROOT / "rag_data/legal_references"
OUTPUT_FILE = REPO_ROOT / "backend/problems_with_rag_explanations.json"

# OpenAI初期化
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("❌ OPENAI_API_KEY が設定されていません")
    exit(1)

client = OpenAI(api_key=API_KEY)

# === ファイル操作 ===
def load_problems() -> List[Dict]:
    """問題JSONを読み込む"""
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_legal_references() -> Dict[str, str]:
    """風営法DBから法令テキストを読み込む"""
    legal_texts = {}

    if not RAG_DATA.exists():
        print(f"❌ RAGデータなし: {RAG_DATA}")
        return legal_texts

    print(f"📚 風営法DB読み込み中... ({RAG_DATA})")
    for file in sorted(RAG_DATA.glob("*.txt")):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                legal_texts[file.stem] = content
                print(f"   ✅ {file.name} ({len(content)} 文字)")
        except Exception as e:
            print(f"   ⚠️  {file.name}: {e}")

    print(f"✅ 合計 {len(legal_texts)} ファイル読み込み\n")
    return legal_texts

def extract_problem_keywords(problem: Dict) -> List[str]:
    """問題文からキーワードを抽出"""
    text = problem.get('problem_text', '')
    category = problem.get('category', '')
    pattern = problem.get('pattern_name', '')

    keywords = []

    # カテゴリからキーワード抽出
    if category:
        keywords.append(category)

    # パターンからキーワード抽出
    if pattern:
        keywords.append(pattern)

    # 問題文から重要語抽出（簡易的）
    important_words = ['営業', '許可', '遊技', '機', '法', '条', '時間', '金額',
                       '違反', '取消', '更新', '申請', '検定', '景品', '機械']
    for word in important_words:
        if word in text:
            keywords.append(word)

    return list(set(keywords))

def search_legal_references(keywords: List[str], legal_texts: Dict[str, str],
                           max_results: int = 3) -> List[str]:
    """キーワードから関連法令を検索"""
    results = []

    for keyword in keywords:
        for ref_name, ref_content in legal_texts.items():
            if keyword in ref_content:
                # 該当する条文を抽出（最初の500文字）
                results.append({
                    'source': ref_name,
                    'snippet': ref_content[:500],
                    'relevance': len([w for w in keyword if w in ref_content])
                })

    # 関連度でソート
    results = sorted(results, key=lambda x: -x['relevance'])[:max_results]

    return [r['source'] for r in results]

# === GPT-5 統合 ===
def generate_explanation_with_gpt5(
    problem: Dict,
    legal_references: List[str],
    legal_texts: Dict[str, str]
) -> str:
    """GPT-5で高品質な解説を生成"""

    problem_text = problem.get('problem_text', '')
    correct_answer = problem.get('correct_answer', '')
    category = problem.get('category', '')
    pattern = problem.get('pattern_name', '')
    difficulty = problem.get('difficulty', '★')

    # 法令参照文を組み立て
    legal_context = "【関連法令】\n"
    for ref_name in legal_references[:2]:  # 最大2つまで
        if ref_name in legal_texts:
            snippet = legal_texts[ref_name][:300]  # 最初の300文字
            legal_context += f"\n{ref_name}:\n{snippet}\n"

    # GPT-5用プロンプト
    prompt = f"""あなたは遊技機取扱主任者試験の指導専門家です。
以下の問題に対して、高品質で実用的な解説を生成してください。

【問題情報】
- 問題: {problem_text}
- 正答: {correct_answer}
- カテゴリ: {category}
- パターン: {pattern}
- 難易度: {difficulty}

{legal_context}

【要件】
1. テンプレート表現は使用しないこと（「〜に関する問題です」は絶対禁止）
2. 正答の理由を明確に説明（1-2文）
3. 関連法令や条項を参照（具体的な条文番号があれば）
4. 学習ポイントを記載（受験者が何を学ぶべきか）
5. よくある誤解があれば説明
6. 全体で3-5文、150-250文字程度

【出力形式】
1行の説明文（改行なし）

例：
営業許可は継続的な違反により行政庁が取消を命じられます。風営法第20条「許可の取消」で規定されており、1回の違反ではなく複数回または継続的な違反が要件です。学習ポイント：許可失効の厳密な条件と、警告段階との区別。

生成してください：
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=500,
            stream=False,
            timeout=30
        )

        explanation = response.choices[0].message.content.strip()

        # 品質チェック
        if len(explanation) < 30:
            return f"⚠️ 生成失敗（短すぎる）"

        if '関する' in explanation and '問題です' in explanation:
            # テンプレート表現が入ってしまった場合は再生成要求
            return f"❌ テンプレート検出: {explanation[:50]}..."

        return explanation

    except Exception as e:
        print(f"   ❌ GPT-5エラー: {str(e)[:100]}")
        return f"⚠️ 生成エラー: {str(e)[:50]}"

# === メイン処理 ===
def main():
    print("=" * 80)
    print("🚀 高品質解説自動生成システム v1.0")
    print("=" * 80)
    print()

    # 1. データ読み込み
    print("📖 問題データ読み込み中...")
    problems = load_problems()
    print(f"✅ {len(problems)} 問題を読み込み\n")

    # 2. 法令DB読み込み
    legal_texts = load_legal_references()

    # 3. サンプル処理（最初の10問でテスト）
    print("\n" + "=" * 80)
    print("📝 サンプル処理（最初の10問）")
    print("=" * 80)

    processed_problems = []

    for i, problem in enumerate(problems[:10], 1):
        print(f"\n【問題 {i}/10】")
        print(f"   テキスト: {problem['problem_text'][:60]}...")
        print(f"   カテゴリ: {problem.get('category', 'N/A')}")

        # キーワード抽出
        keywords = extract_problem_keywords(problem)
        print(f"   キーワード: {keywords}")

        # 法令検索
        legal_refs = search_legal_references(keywords, legal_texts)
        print(f"   関連法令: {legal_refs}")

        # 解説生成
        print(f"   生成中...", end='', flush=True)
        explanation = generate_explanation_with_gpt5(problem, legal_refs, legal_texts)
        print(" ✅")

        print(f"   解説: {explanation[:80]}...")

        # 新しい問題データ
        updated_problem = problem.copy()
        updated_problem['explanation'] = explanation
        updated_problem['legal_references'] = legal_refs
        updated_problem['generated_at'] = datetime.now().isoformat()

        processed_problems.append(updated_problem)

        # レート制限対策
        time.sleep(1)

    # 4. 出力
    print("\n" + "=" * 80)
    print("💾 結果を出力中...")

    # サンプル結果ファイル
    sample_output = REPO_ROOT / "backend/problems_sample_explanations.json"
    with open(sample_output, 'w', encoding='utf-8') as f:
        json.dump(processed_problems, f, ensure_ascii=False, indent=2)

    print(f"✅ サンプル結果: {sample_output}")
    print(f"   {len(processed_problems)} 問題")

    # 品質評価
    print("\n" + "=" * 80)
    print("📊 品質評価（サンプル）")
    print("=" * 80)

    template_count = sum(1 for p in processed_problems
                        if '関する' in p['explanation'] and '問題です' in p['explanation'])
    legal_ref_count = sum(1 for p in processed_problems
                         if p.get('legal_references'))

    print(f"\nテンプレート表現: {template_count}/{len(processed_problems)} ({100*template_count/len(processed_problems):.1f}%)")
    print(f"法令参照: {legal_ref_count}/{len(processed_problems)} ({100*legal_ref_count/len(processed_problems):.1f}%)")

    if template_count == 0:
        print("✅ テンプレート表現: 完全排除")
    else:
        print("⚠️  テンプレート表現が残っています")

    if legal_ref_count > len(processed_problems) * 0.8:
        print("✅ 法令参照率: 良好")

    print("\n" + "=" * 80)
    print("📋 次のステップ")
    print("=" * 80)
    print("""
1. サンプル結果を確認
2. 必要に応じてプロンプト改良
3. 全500問に対して実行
4. 最終品質チェック
5. 本番適用
    """)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Week 7 Phase 1: Claude API自動呼び出しスクリプト
テンプレート別テスト生成（5問）を実行
"""

import json
import os
from pathlib import Path
from typing import Optional

# Claude API導入確認メッセージ
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def load_prompts() -> dict:
    """プロンプトファイルを読み込む"""
    prompts_file = Path("output/WEEK7_PHASE1_CLAUDE_API_PROMPTS.json")
    with open(prompts_file) as f:
        return json.load(f)


def call_claude_api(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Claude APIを呼び出し、テスト問題を生成"""
    if not HAS_ANTHROPIC:
        print("    ⚠️  Claude SDK不可 (pip install anthropic)")
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("    ⚠️  API_KEY未設定 (export ANTHROPIC_API_KEY=sk-...)")
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"    ❌ API呼び出しエラー: {e}")
        return None


def parse_response(response: str) -> Optional[dict]:
    """APIレスポンスをパース"""
    try:
        # JSON部分を抽出（マークダウン```で囲まれた場合対応）
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response

        return json.loads(json_str)
    except Exception as e:
        print(f"    ❌ JSON解析エラー: {e}")
        return None


def main():
    print("=" * 80)
    print("【Week 7 Phase 1: Claude API自動テスト生成】")
    print("=" * 80)
    print()

    # プロンプト読み込み
    print("✅ ステップ1: プロンプト読み込み")
    try:
        prompts_data = load_prompts()
        prompts = prompts_data["prompts"]
        print(f"  ✓ テンプレート数: {len(prompts)}")
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return False
    print()

    # API環境確認
    print("✅ ステップ2: Claude API環境確認")
    if not HAS_ANTHROPIC:
        print("  ⚠️  anthropic SDK未インストール")
        print("     実行方法: pip install anthropic")
        print("     その後、API_KEYを設定して再実行")
        print()
        print("     実行コマンド:")
        print("     export ANTHROPIC_API_KEY='sk-...'")
        print("     python3 backend/call_claude_api_test_generation.py")
        print()
        return False

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  ⚠️  ANTHROPIC_API_KEY環境変数が未設定")
        print("     実行方法:")
        print("     export ANTHROPIC_API_KEY='sk-...'")
        print("     python3 backend/call_claude_api_test_generation.py")
        print()
        return False

    print(f"  ✓ anthropic SDK: インストール済み")
    print(f"  ✓ API_KEY: 設定済み ({api_key[:20]}...)")
    print()

    # テスト生成実行
    print("✅ ステップ3: テスト生成実行")
    print()

    generated_problems = []

    for i, (template, prompt_data) in enumerate(prompts.items(), 1):
        print(f"  [{i}/5] テンプレート {template} 生成中...")

        response = call_claude_api(
            system_prompt=prompt_data["system"],
            user_prompt=prompt_data["user"]
        )

        if not response:
            print(f"      ❌ 生成失敗")
            continue

        problem = parse_response(response)
        if problem:
            generated_problems.append(problem)
            print(f"      ✓ 生成成功: {problem.get('problem_id', 'unknown')}")
        else:
            print(f"      ⚠️  レスポンス解析失敗")

    print()
    print(f"  生成成功: {len(generated_problems)}/5")
    print()

    if not generated_problems:
        print("❌ テスト生成失敗")
        return False

    # 結果保存
    print("✅ ステップ4: 結果保存")
    output_file = Path("output/technology_domain_test_5problems.jsonl")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for problem in generated_problems:
                f.write(json.dumps(problem, ensure_ascii=False) + "\n")

        print(f"  ✓ ファイル: {output_file}")
        print(f"  ✓ 問題数: {len(generated_problems)}")
    except Exception as e:
        print(f"  ❌ 保存エラー: {e}")
        return False

    print()

    # 完了メッセージ
    print("=" * 80)
    print("✅ Phase 1テスト生成完了")
    print("=" * 80)
    print()
    print("【次ステップ】")
    print("1. 品質評価スクリプトを実行")
    print("   $ python3 backend/validate_week6_150_problems.py")
    print()
    print("2. 評価結果に基づいて:")
    print("   - 合格 → Phase 3本生成へ")
    print("   - 要改善 → Phase 2調整実施")
    print()

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

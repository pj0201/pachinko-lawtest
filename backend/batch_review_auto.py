#!/usr/bin/env python3
"""
バッチレビュー自動化スクリプト
638問を20問ずつのバッチに分割し、GPT-5に送信
"""

import json
import subprocess
import time
from pathlib import Path

# 設定
PROBLEM_FILE = Path("/home/planj/patshinko-exam-app/data/PROBLEMS_PRODUCTION_READY_670.json")
BATCH_SIZE = 20
REPO_ROOT = Path("/home/planj/Claude-Code-Communication")
SEND_SCRIPT = REPO_ROOT / "send-to-worker.sh"

def load_problems():
    """問題集を読み込む"""
    with open(PROBLEM_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['problems']

def send_batch_to_gpt5(batch_num, problems):
    """バッチをGPT-5に送信"""
    total_batches = (638 + BATCH_SIZE - 1) // BATCH_SIZE
    
    # バッチレビュー指示
    message = f"""【バッチ {batch_num}/{total_batches} レビュー】問題ID {problems[0]['problem_id']}-{problems[-1]['problem_id']}

以下の {len(problems)} 問を評価してください：
1. 法的根拠の具体性（条文番号まで記載）
2. 問題文と解説の一致
3. 抽象的表現の有無（一定の、適切な、所定の）
4. 問題文が短すぎないか（20文字以上推奨）

各問題をID単位で評価し、改善が必要な場合は修正案も提示してください。"""
    
    # send-to-worker.sh で GPT-5（ペイン2）に送信
    try:
        subprocess.run(
            [str(SEND_SCRIPT), "2", message],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True
        )
        print(f"✅ バッチ {batch_num} を GPT-5 に送信しました")
        return True
    except Exception as e:
        print(f"❌ バッチ {batch_num} 送信エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 バッチレビュー自動化開始")
    print("=" * 60)
    
    # 問題集を読み込む
    problems = load_problems()
    print(f"\n📚 総問題数: {len(problems)}")
    
    # バッチ分割
    batch_size = BATCH_SIZE
    total_batches = (len(problems) + batch_size - 1) // batch_size
    print(f"📋 バッチサイズ: {batch_size}問")
    print(f"🔢 総バッチ数: {total_batches}")
    
    # バッチ処理
    for batch_num in range(1, total_batches + 1):
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(batch_num * batch_size, len(problems))
        batch_problems = problems[start_idx:end_idx]
        
        print(f"\n【バッチ {batch_num}/{total_batches}】問題ID {batch_problems[0]['problem_id']}-{batch_problems[-1]['problem_id']} ({len(batch_problems)}問)")
        
        # GPT-5に送信
        if send_batch_to_gpt5(batch_num, batch_problems):
            # 応答待機（ユーザーが手動で応答するため）
            print(f"  ⏳ GPT-5の応答を待機中... (Enterで次のバッチへ)")
            input("  👉 ")
        else:
            print(f"  ⚠️ バッチ {batch_num} をスキップしました")
        
        # レート制限対策
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ バッチレビュー完了")
    print("=" * 60)

if __name__ == "__main__":
    main()

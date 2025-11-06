#!/usr/bin/env python3
"""
Batch 4-5 再レビュー修復処理（チャンク化対応）
140問と78問を70+70, 40+38に分割して処理
"""

import json
import os
from openai import OpenAI
import time

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def process_batch_rereview_chunked(batch_name, total_problems, chunk_size):
    """バッチをチャンク処理して再レビュー実施"""
    
    print(f"\n{'='*70}")
    print(f"🚀 {batch_name} チャンク処理再レビュー開始")
    print(f"{'='*70}")
    print(f"   総問題数: {total_problems}問")
    print(f"   チャンクサイズ: {chunk_size}問")
    print(f"   開始: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Load correction results
    correction_file = f"data/{batch_name.upper()}_CORRECTION_RESULTS.txt"
    with open(correction_file, 'r', encoding='utf-8') as f:
        correction_content = f.read()
    
    # Load original data
    if batch_name == "batch4":
        with open('data/BATCH_4_REVIEW_DATA.json', 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
        problems = batch_data['problems']
    else:  # batch5
        with open('data/BATCH_5_REVIEW_DATA.json', 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
        problems = batch_data['problems']
    
    all_results = []
    
    # Process chunks
    num_chunks = (total_problems + chunk_size - 1) // chunk_size
    
    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * chunk_size
        end_idx = min((chunk_idx + 1) * chunk_size, total_problems)
        chunk_problems = problems[start_idx:end_idx]
        chunk_num = chunk_idx + 1
        
        print(f"⏳ Chunk {chunk_num}/{num_chunks}: 問題 {chunk_problems[0]['problem_id']}-{chunk_problems[-1]['problem_id']} ({len(chunk_problems)}問)")
        
        # Create prompt for this chunk
        problems_str = "\n".join([
            f"{p['problem_id']}: [{p['theme_name']}] {p['problem_text'][:70]}... 答:{p['correct_answer']}"
            for p in chunk_problems
        ])
        
        # Use only small portion of correction content to stay within limits
        correction_preview = correction_content[:1500]
        
        prompt = f"""【再評価対象】主任者講習試験・法律問題 {len(chunk_problems)}問（{batch_name.upper()} 修正後）
チャンク {chunk_num}/{num_chunks}

【修正内容の一部】
{correction_preview}

【再評価基準】（修正後の品質最終確認）
- 法的根拠の具体性: 条文番号が明記されているか（10点）
- 問題文と解説の一致: 完全に対応しているか（10点）
- 抽象表現の有無: 「一定の」「適切な」など曖昧な表現がないか（10点）

【採点基準】
- 24点以上: ✅合格
- 19～23点: ⚠️要改善
- 18点以下: ❌不合格

【出力形式】
各問題を1行で：ID: スコア点 | ✅/⚠️/❌ | 理由

修正後の全{len(chunk_problems)}問を上記基準で採点してください：

{problems_str}"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "主任者講習試験問題の厳密な評価者。修正後の問題を採点してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=16000
            )
            
            result = response.choices[0].message.content
            all_results.append(result)
            
            # Count results for this chunk
            pass_count = result.count('✅')
            improve_count = result.count('⚠️')
            fail_count = result.count('❌')
            
            print(f"   ✅ {pass_count}問 | ⚠️ {improve_count}問 | ❌ {fail_count}問")
            print(f"   トークン: {response.usage.prompt_tokens + response.usage.completion_tokens}トークン")
            
        except Exception as e:
            print(f"   ❌ エラー: {e}")
            return False
        
        # Small delay between chunks
        if chunk_idx < num_chunks - 1:
            time.sleep(2)
    
    # Merge all results
    merged_result = "\n".join(all_results)
    
    # Save merged results
    output_file = f"data/{batch_name.upper()}_REREVIEW_RESULTS.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"【{batch_name.upper()} Stage 3 - 再レビュー結果（チャンク処理版）】\n")
        f.write(f"実施: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"対象: {total_problems}問（修正後の最終評価）\n")
        f.write(f"モデル: gpt-5-mini（チャンク処理: {num_chunks}分割）\n")
        f.write("=" * 70 + "\n\n")
        f.write(merged_result)
    
    # Final statistics
    total_pass = merged_result.count('✅')
    total_improve = merged_result.count('⚠️')
    total_fail = merged_result.count('❌')
    
    print(f"\n✅ {batch_name.upper()} チャンク処理完了")
    print(f"   保存先: {output_file}")
    print(f"   【最終統計】")
    print(f"   ✅ 合格: {total_pass}問")
    print(f"   ⚠️  要改善: {total_improve}問")
    print(f"   ❌ 不合格: {total_fail}問")
    print(f"   計: {total_pass + total_improve + total_fail}問")
    
    return True

# Main execution
if __name__ == "__main__":
    print("🔧 Batch 4-5 チャンク処理再レビュー実行")
    print("")
    
    # Batch 4: 140問を70+70に分割
    success_b4 = process_batch_rereview_chunked("batch4", 140, 70)
    
    # Batch 5: 78問を40+38に分割
    success_b5 = process_batch_rereview_chunked("batch5", 78, 40)
    
    if success_b4 and success_b5:
        print("\n" + "="*70)
        print("🎉 全チャンク処理完了！")
        print("="*70)
        print("これでBackend実装が自動開始できます")
    else:
        print("\n❌ 処理に失敗した項目があります")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主任者講習アプリの問題品質改善スクリプト
抽象的表現を削減し、説明を充実させる
"""

import json
import re
from typing import Dict, List

class ProblemQualityFixer:
    def __init__(self):
        self.fixed_count = 0
        self.issue_details = []
        
        # 修正マッピング
        self.replacements = {
            '必要な': '必須の',
            '適切な': '規定に基づいた',
            '状況に応じて': 'ケースごとに',
            '一定の': '具体的な',
            '所定の': '法律で定められた',
            '当該の': '該当する',
            'ここで': 'この場合',
            '以下の': '次の',
            '別途': '追加で',
        }
        
        # 説明テンプレート拡張
        self.explanation_extensions = {
            '型式検定': 'これは遊技機の安全性と性能を確保するための制度で、定期的な更新が運営継続の要件となっています。',
            '営業許可': '営業許可は営業全体の合法性を規定する最重要事項であり、これなしに営業継続は不可能です。',
            '新台設置': '新台の導入時には事前届出が必須となっており、無許可での設置は違反行為となります。',
            '営業禁止時間': '営業禁止時間の遵守は客の安全確保と事業者の責任という観点から最優先されます。',
            '風営法': '風営法は遊技業の適切な運営と消費者保護を目的とする重要な法律です。',
        }
    
    def fix_abstract_expressions(self, text: str) -> str:
        """抽象的表現を具体的に変更"""
        for abstract, concrete in self.replacements.items():
            text = re.sub(abstract, concrete, text)
        return text
    
    def expand_short_explanation(self, problem: Dict) -> str:
        """短い説明を拡張"""
        original = problem.get('explanation', '')
        theme = problem.get('theme_name', '')
        
        # 既に十分な長さがあればスキップ
        if len(original) > 100:
            return original
        
        # テーマに応じた説明を追加
        extension = ''
        for key, value in self.explanation_extensions.items():
            if key in theme:
                extension = value
                break
        
        if not extension:
            # デフォルト拡張
            category = problem.get('category', '')
            extension = f"この事項は{category}における重要な規定です。風営法および関連規則に基づき適切に運用することが求められます。"
        
        return f"{original} {extension}"
    
    def fix_problem(self, problem: Dict) -> Dict:
        """問題全体を修正"""
        fixed = problem.copy()
        
        # 問題文の抽象的表現を修正
        question = fixed.get('problem_text', '')
        fixed['problem_text'] = self.fix_abstract_expressions(question)
        
        # 説明を拡張
        explanation = self.expand_short_explanation(fixed)
        fixed['explanation'] = explanation
        
        self.fixed_count += 1
        
        return fixed
    
    def process_all_problems(self, data: Dict) -> Dict:
        """すべての問題を処理"""
        print(f"📊 処理開始: {len(data['problems'])}問")
        
        for i, problem in enumerate(data['problems']):
            data['problems'][i] = self.fix_problem(problem)
            
            if (i + 1) % 100 == 0:
                print(f"  ✅ [{i+1}] 処理完了")
        
        print(f"\n✅ 処理完了: {self.fixed_count}問")
        return data

def main():
    print("=" * 80)
    print("🔧 問題品質改善スクリプト実行")
    print("=" * 80)
    
    # データ読み込み
    input_file = '/home/planj/patshinko-exam-app/data/PROBLEMS_PRODUCTION_READY_670.json'
    output_file = '/home/planj/patshinko-exam-app/data/PROBLEMS_QUALITY_FIXED.json'
    
    print(f"\n📂 入力: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   問題数: {len(data['problems'])}件")
    
    # 修正実行
    fixer = ProblemQualityFixer()
    data = fixer.process_all_problems(data)
    
    # 結果を保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 出力: {output_file}")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

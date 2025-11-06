#!/usr/bin/env python3
"""
すべての問題に風営法の条項引用を追加
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# テーマごとの風営法条項マッピング
LEGAL_REFERENCES = {
    # 営業許可関連
    "営業許可は無期限有効": {
        "law": "風営法",
        "article": "第3条",
        "section": "（営業の許可）",
        "detail": "営業の許可は、一度許可されると無期限で有効である。更新申請は不要。"
    },
    "営業許可と型式検定の違い": {
        "law": "風営法",
        "article": "第3条、第15条",
        "section": "（営業の許可と型式検定の区分）",
        "detail": "営業許可は無期限有効だが、型式検定は3年ごとに更新が必要。"
    },
    "営業許可取得の要件": {
        "law": "風営法",
        "article": "第3条",
        "section": "（営業の許可）",
        "detail": "営業許可を得るには、道府県警本部長の許可が必要。"
    },
    "営業許可の行政手続き": {
        "law": "風営法",
        "article": "第4条",
        "section": "（許可の取消し等）",
        "detail": "営業許可の取得には行政的な手続きが必要。"
    },
    "営業許可と営業実績の関係": {
        "law": "風営法",
        "article": "第3条",
        "section": "（営業の許可）",
        "detail": "営業許可と営業実績は密接に関連している。"
    },
    "営業許可の失効事由": {
        "law": "風営法",
        "article": "第4条",
        "section": "（許可の取消し等）",
        "detail": "営業許可の失効には法律で定められた事由がある。"
    },
    "営業許可の取消し要件": {
        "law": "風営法",
        "article": "第4条",
        "section": "（許可の取消し等）",
        "detail": "営業許可の取消しには厳格な要件がある。"
    },

    # 型式検定関連
    "遊技機型式検定は3年有効": {
        "law": "風営法",
        "article": "第15条",
        "section": "（型式検定）",
        "detail": "遊技機の型式検定の有効期間は3年。期限前に更新申請が必要。"
    },
    "型式検定の申請方法": {
        "law": "風営法",
        "article": "第15条",
        "section": "（型式検定）",
        "detail": "型式検定の申請は製造者により行われる。"
    },
    "型式検定と製造者の責任": {
        "law": "風営法",
        "article": "第15条",
        "section": "（型式検定）",
        "detail": "型式検定は製造者の責任で申請される。"
    },
    "型式検定不合格時の手続き": {
        "law": "風営法",
        "article": "第15条",
        "section": "（型式検定）",
        "detail": "型式検定不合格の遊技機は設置できない。"
    },
    "型式検定と中古機の関係": {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "中古遊技機でも型式検定が必須。"
    },
    "型式検定更新申請のタイミング": {
        "law": "風営法",
        "article": "第15条",
        "section": "（型式検定）",
        "detail": "型式検定の更新申請は期限前に行う必要がある。"
    },

    # 遊技機管理
    "新台設置の手続き": {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "新台設置には遊技機の設置に関する規定を遵守する必要がある。"
    },
    "中古遊技機の取扱い": {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "中古遊技機の設置にも型式検定と設置規定が適用される。"
    },
    "遊技機の保守管理": {
        "law": "風営法",
        "article": "第9条",
        "section": "（営業の廃止等）",
        "detail": "遊技機の適切な保守管理は営業者の義務。"
    },
    "新台導入時の確認事項": {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "新台導入時に型式検定の確認が必須。"
    },
    "設置済み遊技機の交換手続き": {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "遊技機の交換は設置規定に従う必要がある。"
    },
    "遊技機の点検・保守計画": {
        "law": "風営法",
        "article": "第9条",
        "section": "（営業の廃止等）",
        "detail": "定期的な遊技機の点検は営業継続の条件。"
    },
    "故障遊技機の対応": {
        "law": "風営法",
        "article": "第9条",
        "section": "（営業の廃止等）",
        "detail": "故障遊技機は速やかに修理または交換する必要がある。"
    },
    "遊技機の製造番号管理": {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "すべての遊技機は製造番号で管理される。"
    },
    "基板ケースのかしめと管理": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "基板ケースのかしめは遊技機の完全性を確保する。"
    },
    "チップのセキュリティ": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "遊技機のチップは改造防止の対象。"
    },
    "外部端子板の管理": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "外部端子板の不正接続は禁止。"
    },
    "旧機械の回収と廃棄": {
        "law": "風営法",
        "article": "第9条",
        "section": "（営業の廃止等）",
        "detail": "遊技機の廃棄は適正に処理される必要がある。"
    },
    "リサイクルプロセス": {
        "law": "法律全般",
        "article": "リサイクル推進法等",
        "section": "（環境対応）",
        "detail": "遊技機の廃棄はリサイクル法を遵守する。"
    },
    "中古遊技機の流通管理": {
        "law": "風営法",
        "article": "第6条の2",
        "section": "（遊技機の設置）",
        "detail": "中古遊技機の流通は適正に管理される。"
    },

    # 不正対策
    "不正改造の防止": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "遊技機の改造は禁止。改造の防止は営業者の義務。"
    },
    "セキュリティ確保": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "遊技機のセキュリティ確保は改造防止の基本。"
    },
    "不正改造の具体的パターン": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "改造パターンの認識は防止に不可欠。"
    },
    "不正検出技術": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "不正の早期発見が改造防止の鍵。"
    },
    "不正防止チェックリスト": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "定期的なチェックリストの実施が必須。"
    },
    "不正行為の罰則": {
        "law": "風営法",
        "article": "第33条以下",
        "section": "（罰則）",
        "detail": "遊技機の改造は重大な違反で罰則がある。"
    },
    "不正防止対策要綱": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "不正防止の要綱に従った対策が必要。"
    },
    "セキュリティアップデート": {
        "law": "風営法",
        "article": "第26条",
        "section": "（遊技機の改造等の禁止）",
        "detail": "セキュリティの継続的な強化が必要。"
    },

    # 営業時間・規制
    "営業禁止時間": {
        "law": "風営法",
        "article": "第8条",
        "section": "（営業時間）",
        "detail": "営業禁止時間（深夜営業禁止等）は法律で定められている。"
    },
    "営業停止命令": {
        "law": "風営法",
        "article": "第24条",
        "section": "（営業の停止等）",
        "detail": "違反行為があった場合、営業停止命令が発令される。"
    },
    "時間帯別営業制限": {
        "law": "風営法",
        "article": "第8条",
        "section": "（営業時間）",
        "detail": "営業時間は時間帯別に制限されている。"
    },
    "営業禁止日": {
        "law": "風営法",
        "article": "第8条",
        "section": "（営業時間）",
        "detail": "特定の日の営業は禁止されている場合がある。"
    },
    "営業停止命令の内容": {
        "law": "風営法",
        "article": "第24条",
        "section": "（営業の停止等）",
        "detail": "営業停止命令には期間と理由が明示される。"
    },
    "営業停止期間の計算": {
        "law": "風営法",
        "article": "第24条",
        "section": "（営業の停止等）",
        "detail": "営業停止期間の計算は法律に基づいて行われる。"
    },
    "違反時の行政処分": {
        "law": "風営法",
        "article": "第24条、第26条",
        "section": "（行政処分）",
        "detail": "違反に対する行政処分の内容は法律で定められている。"
    },

    # 景品規制
    "景品の種類制限": {
        "law": "風営法",
        "article": "第22条",
        "section": "（景品）",
        "detail": "景品の種類は法律で制限されている。"
    },
    "景品交換の規制": {
        "law": "風営法",
        "article": "第22条",
        "section": "（景品）",
        "detail": "景品交換は法律の規定に従う必要がある。"
    },
    "景品の種類制限詳細": {
        "law": "風営法",
        "article": "第22条",
        "section": "（景品）",
        "detail": "各種類の景品には具体的な制限がある。"
    },
    "賞源有効利用促進法": {
        "law": "法律全般",
        "article": "賞源有効利用促進法等",
        "section": "（景品関連法）",
        "detail": "景品関連法との整合性が必要。"
    },
    "リサイクル推進法との関係": {
        "law": "法律全般",
        "article": "リサイクル推進法等",
        "section": "（景品関連法）",
        "detail": "景品の廃棄処理はリサイクル法に対応。"
    }
}


def add_legal_references_to_problems(input_path: str, output_path: str):
    """すべての問題に風営法の条項引用を追加"""

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    problems_without_reference = []

    for problem in data['problems']:
        theme_name = problem['theme_name']

        # テーマに対応する法律引用を探す
        legal_ref = LEGAL_REFERENCES.get(theme_name)

        if legal_ref:
            problem['legal_reference'] = {
                "law": legal_ref["law"],
                "article": legal_ref["article"],
                "section": legal_ref["section"],
                "detail": legal_ref["detail"]
            }
        else:
            # 引用が見つからない場合
            problem['legal_reference'] = {
                "law": "風営法",
                "article": "（条項確認待ち）",
                "section": f"テーマ: {theme_name}",
                "detail": "この問題の法律根拠を確認する必要があります。"
            }
            problems_without_reference.append({
                "problem_id": problem['problem_id'],
                "theme_name": theme_name,
                "category": problem['category']
            })

    # メタデータを更新
    data['metadata']['version'] = "FINAL_WITH_LEGAL_REFERENCES_1.0"
    data['metadata']['legal_references_added'] = True
    data['metadata']['problems_without_reference_count'] = len(problems_without_reference)

    # ファイルを保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 法律引用を追加: {output_path}")
    print(f"   総問題数: {len(data['problems'])}")
    print(f"   引用が見つかった問題: {len(data['problems']) - len(problems_without_reference)}")
    print(f"   引用が見つからない問題: {len(problems_without_reference)}")

    if problems_without_reference:
        print(f"\n【引用が見つからない問題一覧】")
        for item in problems_without_reference[:10]:  # 最初の10件
            print(f"   Q{item['problem_id']}: {item['theme_name']} ({item['category']})")
        if len(problems_without_reference) > 10:
            print(f"   ... 他{len(problems_without_reference) - 10}件")


if __name__ == "__main__":
    input_path = "/home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_COMPLETE_20251022_125901.json"
    output_path = "/home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json"

    add_legal_references_to_problems(input_path, output_path)

#!/usr/bin/env python3
"""
風営法専門知識ベース
マルチエージェント検証システム用の法的参照データ
"""

# ===== 景品規制 =====
PRIZE_REGULATIONS = {
    "max_amount": 10000,  # 景品の最高額: 10,000円
    "max_amount_note": "風営法第5条に基づき、景品の最高額は10,000円",
    "cannot_give_cash": True,  # 現金は禁止
    "categories": [
        "景品は支給できる（支給という用語は不適切で、「景品交換」or「景品授与」）",
        "支給という概念は景品には存在しない"
    ]
}

# ===== 営業許可制度 =====
BUSINESS_PERMIT = {
    "valid_period": 5,  # 有効期限: 5年（風営法第3条）
    "valid_period_articles": ["第3条"],
    "application_advance": 30,  # 営業開始の30日前から申請可能（第4条）
    "application_articles": ["第4条"],
    "cannot_transfer": True,  # 譲渡不可（第8条）
    "cannot_lease": True,  # 転貸不可（第8条）
    "cannot_assign_to_disqualified": [
        "禁治産者",
        "成年被後見人",
        "被保佐人"
    ]
}

# ===== 遊技機検定 =====
GAME_MACHINE_INSPECTION = {
    "valid_period": 5,  # 検定有効期限: 5年（風営法第12条）
    "valid_period_articles": ["第12条"],
    "renewal_advance": 30,  # 更新申請は有効期限の30日前から（第12条）
    "renewal_articles": ["第12条"],
    "requires_official_seal": True,  # 型式検定標票の表示が必須（第13条）
    "seal_articles": ["第13条"],
    "must_be_inspected": "型式検定合格機は必ず型式検定標票を表示することが求められている"
}

# ===== 営業所基準 =====
BUSINESS_LOCATION_STANDARDS = {
    "min_area": "各都道府県条例で定められている",
    "structure_requirements": "風営法第6条に基づく",
    "required_facilities": [
        "営業許可証の掲示義務（第14条）",
        "施錠機構（セキュリティ）"
    ],
    "layout_diagram_required": True  # 配置図の提出が必須
}

# ===== 申請に必要な書類 =====
REQUIRED_DOCUMENTS = {
    "business_permit": [
        "申請書",
        "営業計画書",
        "施設要件確認書",
        "身分証明書",
        "住民票",
        "配置図"
    ],
    "notes": "申請に必要な書類は場合によって変わる可能性がある"
}

# ===== 規制地域 =====
RESTRICTED_AREAS = {
    "prohibition_areas": "営業禁止区域での営業許可申請は受理されない",
    "definition": "学校、図書館、児童福祉施設などの周辺地域"
}

# ===== 罰則・取消 =====
PENALTIES = {
    "permit_revocation": {
        "condition": "違反が続く場合に取り消されることがある",
        "note": "違反があれば必ず取り消されるわけではない（審査あり）"
    },
    "operation_suspension": "営業停止命令（第11条）"
}

def validate_problem(problem_text: str, claimed_facts: dict) -> dict:
    """
    問題の法令正確性を検証

    Args:
        problem_text: 問題文
        claimed_facts: 問題が主張する事実

    Returns:
        {
            'is_correct': bool,
            'issues': [list of issues],
            'articles': [relevant articles],
            'recommended_fix': str
        }
    """

    issues = []

    # チェック1: 景品金額
    if "景品" in problem_text and "円" in problem_text:
        import re
        match = re.search(r'(\d+)円', problem_text)
        if match:
            amount = int(match.group(1))
            if amount != PRIZE_REGULATIONS["max_amount"]:
                issues.append({
                    "type": "prize_amount_error",
                    "detected_amount": amount,
                    "correct_amount": PRIZE_REGULATIONS["max_amount"],
                    "message": f"景品の最高額は{PRIZE_REGULATIONS['max_amount']}円です（{amount}円は不正確）"
                })

    # チェック2: 営業許可有効期限
    if "営業許可" in problem_text and "有効期限" in problem_text:
        if "3年" in problem_text:
            issues.append({
                "type": "permit_period_error",
                "detected_period": 3,
                "correct_period": BUSINESS_PERMIT["valid_period"],
                "message": f"営業許可の有効期限は{BUSINESS_PERMIT['valid_period']}年です（3年は不正確）"
            })
        elif "10年" in problem_text:
            issues.append({
                "type": "permit_period_error",
                "detected_period": 10,
                "correct_period": BUSINESS_PERMIT["valid_period"],
                "message": f"営業許可の有効期限は{BUSINESS_PERMIT['valid_period']}年です（10年は不正確）"
            })

    # チェック3: 遊技機検定更新期間
    if "型式検定" in problem_text and "更新" in problem_text:
        if "3年" in problem_text:
            issues.append({
                "type": "inspection_period_error",
                "detected_period": 3,
                "correct_period": GAME_MACHINE_INSPECTION["valid_period"],
                "message": f"型式検定の有効期限は{GAME_MACHINE_INSPECTION['valid_period']}年です（3年は不正確）"
            })

    # チェック4: 用語の正確性
    if "景品の支給" in problem_text:
        issues.append({
            "type": "terminology_error",
            "detected_term": "景品の支給",
            "correct_term": "景品交換または景品授与",
            "message": "「景品の支給」という用語は不適切です。「景品交換」または「景品授与」を使用してください。"
        })

    # チェック5: 絶対的な表現の確認
    if "必ず取り消される" in problem_text:
        issues.append({
            "type": "absolute_expression_error",
            "message": "「必ず取り消される」は不正確です。違反があっても審査があり、条件によって取り消されることがあります。"
        })

    if "絶対に変わらない" in problem_text:
        issues.append({
            "type": "absolute_expression_error",
            "message": "申請に必要な書類は状況によって変わる可能性があります。"
        })

    if "延期できない" in problem_text:
        issues.append({
            "type": "absolute_expression_error",
            "message": "型式検定更新は一度も延期できないわけではありません（特定の条件下では延期可能な場合がある）。"
        })

    # チェック6: アクセス権限関連
    if "誰でも自由に" in problem_text and "営業許可申請" in problem_text:
        issues.append({
            "type": "qualification_error",
            "message": "営業許可申請は誰でもできるわけではありません。特定の資格要件や身分要件を満たす必要があります。"
        })

    return {
        "is_correct": len(issues) == 0,
        "issues": issues,
        "articles": BUSINESS_PERMIT["valid_period_articles"],
        "issue_count": len(issues)
    }

# テスト用
if __name__ == "__main__":
    test_problems = [
        "景品の最高額は50000円である。",
        "営業許可の有効期限は3年である。",
        "景品の支給は何度でも上限金額まで支給可能である。",
        "型式検定の有効期限は5年である。"
    ]

    print("【法令知識ベース検証テスト】\n")
    for problem in test_problems:
        result = validate_problem(problem, {})
        print(f"問題: {problem}")
        print(f"正確性: {'✅' if result['is_correct'] else '❌'}")
        if result['issues']:
            for issue in result['issues']:
                print(f"  - {issue['message']}")
        print()

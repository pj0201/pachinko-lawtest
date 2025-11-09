"""Vercel Serverless Function: Token Registration & Device ID Validation"""

import json
import os
from datetime import datetime
import uuid

# トークンレジストリファイル（Vercel `/tmp` に保存）
REGISTRY_PATH = "/tmp/token_registry.json"

# テストトークン定義
TEST_TOKENS = {
    "TEST_001_ABC123": {"account_id": 1001, "name": "テストユーザー001"},
    "TEST_002_BCD234": {"account_id": 1002, "name": "テストユーザー002"},
    "TEST_003_CDE345": {"account_id": 1003, "name": "テストユーザー003"},
    "TEST_004_DEF456": {"account_id": 1004, "name": "テストユーザー004"},
    "TEST_005_EFG567": {"account_id": 1005, "name": "テストユーザー005"},
    "TEST_006_FGH678": {"account_id": 1006, "name": "テストユーザー006"},
    "TEST_007_GHI789": {"account_id": 1007, "name": "テストユーザー007"},
    "TEST_008_HIJ890": {"account_id": 1008, "name": "テストユーザー008"},
    "TEST_009_IJK901": {"account_id": 1009, "name": "テストユーザー009"},
    "TEST_010_JKL012": {"account_id": 1010, "name": "テストユーザー010"},
    "ADMIN_001_XYZ888": {"account_id": 9001, "name": "管理者"}
}

def load_registry():
    """トークンレジストリを読み込む"""
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_registry(registry):
    """トークンレジストリを保存"""
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

def handler(request):
    """メインハンドラ（Vercel Serverless Function）"""

    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }

    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({"error": "Method not allowed"})
        }

    try:
        body = json.loads(request.body)
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid JSON"})
        }

    token = body.get('token')
    device_id = body.get('device_id')
    username = body.get('username')

    # 1. トークン検証
    if token not in TEST_TOKENS:
        return {
            'statusCode': 400,
            'body': json.dumps({"success": False, "message": "無効な招待URLです"})
        }

    # 2. レジストリ読み込み
    registry = load_registry()

    # 3. トークン既登録チェック
    if token in registry:
        registered_device = registry[token].get('device_id')
        if registered_device != device_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "success": False,
                    "message": "この招待URLは既に別のデバイスで登録済みです"
                })
            }
        # 同じデバイスからの再登録は許可（session_token 返却）

    # 4. 同デバイスで別トークン登録チェック
    for tok, entry in registry.items():
        if entry.get('device_id') == device_id and tok != token:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "success": False,
                    "message": "このデバイスは既に別のアカウントで登録済みです"
                })
            }

    # 5. 新規登録 or 更新
    account_id = TEST_TOKENS[token]['account_id']
    session_token = str(uuid.uuid4())

    registry[token] = {
        "device_id": device_id,
        "account_id": account_id,
        "username": username,
        "session_token": session_token,
        "registered_at": datetime.now().isoformat()
    }

    save_registry(registry)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            "success": True,
            "message": "登録成功",
            "session_token": session_token,
            "account_id": account_id
        })
    }

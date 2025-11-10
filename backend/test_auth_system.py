#!/usr/bin/env python3
"""
認証システム統合テスト
メールアドレス + ユーザー名ベースの認証をテスト
"""

import sys
from auth_database import AuthDatabase
from pathlib import Path

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def test_auth_system():
    """認証システムの統合テスト"""

    # テスト用データベース
    test_db_path = Path(__file__).parent / "test_auth.db"
    if test_db_path.exists():
        test_db_path.unlink()

    db = AuthDatabase(test_db_path)
    print_section("🔧 認証システムテスト開始")

    # テスト1: 招待トークン生成
    print_section("テスト1: 招待トークン生成")
    tokens = db.generate_invite_tokens(3)
    print(f"✅ {len(tokens)}個の招待トークンを生成")
    for i, token in enumerate(tokens, 1):
        print(f"  {i}. {token[:40]}...")

    test_token = tokens[0]

    # テスト2: トークン検証
    print_section("テスト2: 招待トークン検証")
    result = db.verify_invite_token(test_token)
    if result['valid']:
        print("✅ トークン検証成功:", result['message'])
    else:
        print("❌ トークン検証失敗:", result['message'])
        return False

    # テスト3: デバイス登録（メールアドレス + ユーザー名）
    print_section("テスト3: デバイス登録（email + username）")
    test_email = "test@example.com"
    test_username = "テストユーザー001"
    test_device_id = "device_12345abcde"

    result = db.register_device(test_token, test_device_id, test_email, test_username)
    if result['success']:
        print("✅ デバイス登録成功")
        print(f"  - Email: {result['email']}")
        print(f"  - Username: {result['username']}")
        print(f"  - Session Token: {result['session_token'][:40]}...")
    else:
        print("❌ デバイス登録失敗:", result['message'])
        return False

    session_token1 = result['session_token']

    # テスト4: 同じデバイスから再アクセス（トークン使用済み）
    print_section("テスト4: 同じデバイスから再アクセス")
    result = db.register_device(test_token, test_device_id, test_email, test_username)
    if result['success']:
        print("✅ 同じデバイスからの再アクセス成功")
        print(f"  - 新しいSession Token: {result['session_token'][:40]}...")
    else:
        print("❌ 再アクセス失敗:", result['message'])
        return False

    # テスト5: 異なるデバイスから同じトークンでアクセス（拒否されるべき）
    print_section("テスト5: 異なるデバイスから同じトークンでアクセス（拒否）")
    different_device_id = "device_99999zzzzz"
    result = db.register_device(test_token, different_device_id, "other@example.com", "別ユーザー")
    if not result['success']:
        print("✅ 異なるデバイスからのアクセスを正しく拒否")
        print(f"  - メッセージ: {result['message']}")
    else:
        print("❌ 異なるデバイスからのアクセスが許可されてしまった（バグ）")
        return False

    # テスト6: セッション検証
    print_section("テスト6: セッション検証")
    result = db.verify_session(session_token1, test_device_id)
    if result['valid']:
        print("✅ セッション検証成功:", result['message'])
    else:
        print("❌ セッション検証失敗:", result['message'])
        return False

    # テスト7: ログイン認証（正しいメールアドレス + ユーザー名）
    print_section("テスト7: ログイン認証（正しい資格情報）")
    result = db.login_with_credentials(test_email, test_username, test_device_id)
    if result['success']:
        print("✅ ログイン成功")
        print(f"  - Email: {result['email']}")
        print(f"  - Username: {result['username']}")
        print(f"  - Session Token: {result['session_token'][:40]}...")
    else:
        print("❌ ログイン失敗:", result['message'])
        return False

    # テスト8: ログイン認証（間違ったメールアドレス）
    print_section("テスト8: ログイン認証（間違ったメールアドレス）")
    result = db.login_with_credentials("wrong@example.com", test_username, test_device_id)
    if not result['success']:
        print("✅ 間違った資格情報を正しく拒否")
        print(f"  - メッセージ: {result['message']}")
    else:
        print("❌ 間違った資格情報がログインを許可してしまった（バグ）")
        return False

    # テスト9: ログイン認証（間違ったユーザー名）
    print_section("テスト9: ログイン認証（間違ったユーザー名）")
    result = db.login_with_credentials(test_email, "間違ったユーザー", test_device_id)
    if not result['success']:
        print("✅ 間違った資格情報を正しく拒否")
        print(f"  - メッセージ: {result['message']}")
    else:
        print("❌ 間違った資格情報がログインを許可してしまった（バグ）")
        return False

    # テスト10: 異なるデバイスからログイン（拒否されるべき）
    print_section("テスト10: 異なるデバイスからログイン（拒否）")
    result = db.login_with_credentials(test_email, test_username, different_device_id)
    if not result['success']:
        print("✅ 異なるデバイスからのログインを正しく拒否")
        print(f"  - メッセージ: {result['message']}")
    else:
        print("❌ 異なるデバイスからのログインが許可されてしまった（バグ）")
        return False

    # テスト11: 統計情報の確認
    print_section("テスト11: 統計情報の確認")
    stats = db.get_stats()
    print("📊 データベース統計:")
    print(f"  - 総トークン数: {stats['total_tokens']}")
    print(f"  - 使用済みトークン数: {stats['used_tokens']}")
    print(f"  - 未使用トークン数: {stats['available_tokens']}")
    print(f"  - アクティブセッション数: {stats['active_sessions']}")

    # 期待値の確認
    if stats['total_tokens'] == 3 and stats['used_tokens'] == 1:
        print("✅ 統計情報が正しい")
    else:
        print("❌ 統計情報が期待値と異なる")
        return False

    # テストDB削除
    test_db_path.unlink()

    print_section("✅ すべてのテストが成功しました")
    return True

if __name__ == "__main__":
    success = test_auth_system()
    sys.exit(0 if success else 1)

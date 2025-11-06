#!/usr/bin/env python3
"""
generate_invites.py - 招待URL生成ツール
アルファ版テスター用の招待URLを生成

使用方法:
  python3 generate_invites.py 10  # 10個の招待URL生成
  python3 generate_invites.py     # デフォルト10個生成
"""

import sys
from auth_database import AuthDatabase
from datetime import datetime

def main():
    # 生成数の取得（コマンドライン引数またはデフォルト10）
    count = 10
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            if count <= 0 or count > 100:
                print("❌ エラー: 生成数は 1〜100 の範囲で指定してください")
                sys.exit(1)
        except ValueError:
            print("❌ エラー: 有効な整数を指定してください")
            sys.exit(1)

    # データベース初期化
    try:
        db = AuthDatabase()
        print(f"✅ 認証データベース接続成功\n")
    except Exception as e:
        print(f"❌ データベース接続失敗: {e}")
        sys.exit(1)

    # 招待トークン生成
    try:
        tokens = db.generate_invite_tokens(count)
        print(f"✅ {count}個の招待トークンを生成しました\n")
    except Exception as e:
        print(f"❌ トークン生成失敗: {e}")
        sys.exit(1)

    # ベースURLの設定（本番環境では適切なドメインに変更）
    base_url = "http://localhost:5173/invite"  # Vite開発サーバーのデフォルトポート
    # 本番環境の例: base_url = "https://patshinko-exam-app.com/invite"

    # ファイル名の生成（タイムスタンプ付き）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"invite_urls_{timestamp}.txt"

    # URL生成とファイル保存
    print("=" * 70)
    print(f"  招待URL一覧（{count}個）")
    print("=" * 70)
    print()

    with open(filename, "w", encoding="utf-8") as f:
        # ヘッダー情報
        f.write("=" * 70 + "\n")
        f.write(f"遊技機取扱主任者試験アプリ - アルファ版招待URL\n")
        f.write(f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write(f"生成数: {count}個\n")
        f.write("=" * 70 + "\n\n")

        # URL一覧
        for i, token in enumerate(tokens, 1):
            url = f"{base_url}/{token}"
            print(f"{i:3d}. {url}")
            f.write(f"{i}. {url}\n")

        # フッター情報
        f.write("\n" + "=" * 70 + "\n")
        f.write("※ 各URLは1台のデバイスのみ登録可能です\n")
        f.write("※ ログイン認証: メールアドレス=987、パスワード=987\n")
        f.write("=" * 70 + "\n")

    print()
    print("=" * 70)
    print(f"📋 ファイル保存: {filename}")
    print("=" * 70)
    print()

    # 統計情報の表示
    stats = db.get_stats()
    print("📊 現在の認証システム統計:")
    print(f"  - 総招待トークン数: {stats['total_tokens']}個")
    print(f"  - 使用済みトークン数: {stats['used_tokens']}個")
    print(f"  - 未使用トークン数: {stats['available_tokens']}個")
    print(f"  - アクティブセッション数: {stats['active_sessions']}個")
    print()

    print("✅ 招待URL生成完了！")
    print()
    print("📌 次のステップ:")
    print("  1. invite_urls_*.txt ファイルをテスターに配布")
    print("  2. テスターに各URLにアクセスしてもらう")
    print("  3. メールアドレス「987」、パスワード「987」で登録")
    print()

if __name__ == "__main__":
    main()

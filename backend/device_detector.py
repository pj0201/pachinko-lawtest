#!/usr/bin/env python3
"""
デバイス種類自動判別ユーティリティ
User-Agent から Android/iPhone/PC を判定
"""

def detect_device_type(user_agent: str) -> str:
    """
    User-Agent文字列からデバイス種類を判定

    Args:
        user_agent: User-Agent文字列

    Returns:
        "Android" | "iPhone" | "PC" | "Unknown"
    """
    if not user_agent:
        return "Unknown"

    ua_lower = user_agent.lower()

    # Android判定
    if "android" in ua_lower:
        return "Android"

    # iPhone/iPad判定
    if "iphone" in ua_lower or "ipad" in ua_lower or "ipod" in ua_lower:
        return "iPhone"

    # PC判定（Windows, Mac, Linux）
    if any(platform in ua_lower for platform in ["windows", "macintosh", "linux", "x11"]):
        # モバイル版でない場合のみPC判定
        if "mobile" not in ua_lower:
            return "PC"

    return "Unknown"


def get_detailed_device_info(user_agent: str) -> dict:
    """
    詳細なデバイス情報を取得

    Args:
        user_agent: User-Agent文字列

    Returns:
        デバイス情報の辞書
    """
    device_type = detect_device_type(user_agent)

    info = {
        "device_type": device_type,
        "os": "Unknown",
        "browser": "Unknown"
    }

    if not user_agent:
        return info

    ua_lower = user_agent.lower()

    # OS判定
    if "android" in ua_lower:
        info["os"] = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        info["os"] = "iOS"
    elif "windows" in ua_lower:
        info["os"] = "Windows"
    elif "macintosh" in ua_lower or "mac os" in ua_lower:
        info["os"] = "macOS"
    elif "linux" in ua_lower:
        info["os"] = "Linux"

    # ブラウザ判定
    if "chrome" in ua_lower and "edg" not in ua_lower:
        info["browser"] = "Chrome"
    elif "firefox" in ua_lower:
        info["browser"] = "Firefox"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        info["browser"] = "Safari"
    elif "edg" in ua_lower:
        info["browser"] = "Edge"
    elif "opera" in ua_lower or "opr" in ua_lower:
        info["browser"] = "Opera"

    return info


if __name__ == "__main__":
    # テスト
    test_user_agents = [
        ("Android Phone", "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"),
        ("iPhone", "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"),
        ("Windows PC", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
        ("Mac PC", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"),
        ("iPad", "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"),
    ]

    print("🔍 デバイス判定テスト\n")
    for name, ua in test_user_agents:
        device_type = detect_device_type(ua)
        detailed = get_detailed_device_info(ua)
        print(f"{name}:")
        print(f"  Device Type: {device_type}")
        print(f"  OS: {detailed['os']}")
        print(f"  Browser: {detailed['browser']}")
        print()

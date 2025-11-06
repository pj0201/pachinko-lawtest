#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カテゴリ別サブトピック抽出スクリプト

遊技機取扱主任者試験のOCRデータから、
カテゴリごとのサブトピックを構造化抽出する
"""

import json
import re
from collections import defaultdict

def load_ocr_data(ocr_path):
    """OCRデータを読み込む"""
    with open(ocr_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_wind_eikyo(md_path):
    """風営法MDを読み込む"""
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_chapters_from_ocr(ocr_data):
    """OCRから章・節構造を抽出"""
    chapters = defaultdict(lambda: {"sections": [], "raw_text": ""})
    current_chapter = None

    for page in ocr_data:
        text = page.get('text', '')
        page_num = page.get('page_number', 0)

        # 章の検出（第X章）
        chapter_matches = re.finditer(r'第([1-9])章\s+([^\n]+)', text)
        for match in chapter_matches:
            current_chapter = match.group(1)
            ch_title = match.group(2).strip()
            chapters[current_chapter]["title"] = ch_title
            chapters[current_chapter]["page_start"] = page_num

        # セクションの検出（(1), (2), ...）
        if current_chapter:
            section_matches = re.finditer(r'\(([0-9①②③④⑤]+)\)\s*([^\n]+)', text)
            for match in section_matches:
                sec_num = match.group(1)
                sec_title = match.group(2).strip()
                chapters[current_chapter]["sections"].append({
                    "number": sec_num,
                    "title": sec_title,
                    "page": page_num
                })

        # テキストを蓄積
        if current_chapter:
            chapters[current_chapter]["raw_text"] += text + "\n"

    return chapters

def extract_wind_eikyo_sections(md_text):
    """風営法から主要トピックを抽出"""
    topics = []

    # ## セクションを抽出
    matches = re.finditer(r'^## (.+)$', md_text, re.MULTILINE)
    for match in matches:
        topics.append(match.group(1).strip())

    # ### サブセクションも抽出
    sub_matches = re.finditer(r'^### (.+)$', md_text, re.MULTILINE)
    for match in sub_matches:
        topics.append("└─ " + match.group(1).strip())

    return topics

def map_to_exam_categories():
    """
    遊技機取扱主任者試験のカテゴリにマッピング

    7つのカテゴリ：
    1. 営業許可・申請手続き
    2. 営業時間・営業場所
    3. 遊技機規制
    4. 従業者の要件・禁止事項
    5. 顧客保護・規制遵守
    6. 法令違反と行政処分
    7. 実務的対応
    """
    categories = {
        "permits": {
            "id": "permits",
            "name": "営業許可・申請手続き",
            "keywords": ["許可", "申請", "届出", "営業", "要件"],
            "subtopics": []
        },
        "business_hours": {
            "id": "business_hours",
            "name": "営業時間・営業場所",
            "keywords": ["営業時間", "営業場所", "施設", "基準", "構造"],
            "subtopics": []
        },
        "gaming_machines": {
            "id": "gaming_machines",
            "name": "遊技機規制",
            "keywords": ["遊技機", "検定", "改造", "検査", "基準"],
            "subtopics": []
        },
        "employees": {
            "id": "employees",
            "name": "従業者の要件・禁止事項",
            "keywords": ["主任者", "従業員", "資格", "禁止", "雇用"],
            "subtopics": []
        },
        "customer_protection": {
            "id": "customer_protection",
            "name": "顧客保護・規制遵守",
            "keywords": ["顧客", "未成年", "景品", "交換", "保護"],
            "subtopics": []
        },
        "violations": {
            "id": "violations",
            "name": "法令違反と行政処分",
            "keywords": ["違反", "処分", "停止", "取消", "行政"],
            "subtopics": []
        },
        "practical": {
            "id": "practical",
            "name": "実務的対応",
            "keywords": ["対応", "報告", "記録", "管理", "実務"],
            "subtopics": []
        }
    }

    return categories

def extract_subtopics_from_text(text, keywords):
    """
    テキストからキーワードに基づくサブトピックを抽出
    """
    subtopics = []

    # 文ごとに処理
    sentences = re.split(r'[。．\n]+', text)

    for sentence in sentences:
        # キーワードを含む文を抽出
        for keyword in keywords:
            if keyword in sentence and len(sentence) > 10:
                # 重複を避ける
                if sentence.strip() not in [st["text"] for st in subtopics]:
                    subtopics.append({
                        "text": sentence.strip()[:100],  # 最初の100文字
                        "keyword": keyword
                    })
                break

        if len(subtopics) >= 5:  # カテゴリあたり最大5トピック
            break

    return subtopics

def main():
    print("🚀 カテゴリ別サブトピック抽出開始\n")

    # ソースを読み込む
    ocr_path = '/home/planj/patshinko-exam-app/data/ocr_results_corrected.json'
    wind_path = '/home/planj/Claude-Code-Communication/resources/legal/wind_eikyo_law/wind_eikyo_law_v1.0.md'

    print("📖 ソースデータを読み込み中...")
    ocr_data = load_ocr_data(ocr_path)
    wind_text = load_wind_eikyo(wind_path)

    print(f"✅ OCR: {len(ocr_data)}ページ")
    print(f"✅ 風営法: {len(wind_text)}文字\n")

    # OCRから章構造を抽出
    print("📋 OCRから章・節構造を抽出...")
    chapters = extract_chapters_from_ocr(ocr_data)
    for ch_num, ch_data in sorted(chapters.items()):
        if "title" in ch_data:
            print(f"  第{ch_num}章: {ch_data['title']}")
            for section in ch_data.get("sections", []):
                print(f"    ({section['number']}) {section['title']}")

    # カテゴリを初期化
    print("\n📊 カテゴリにサブトピックをマッピング...")
    categories = map_to_exam_categories()

    # 各カテゴリのテキストを集約
    all_text = "\n".join([ch["raw_text"] for ch in chapters.values()])
    all_text += "\n" + wind_text

    # サブトピックを抽出
    for cat_id, cat_data in categories.items():
        subtopics = extract_subtopics_from_text(all_text, cat_data["keywords"])
        cat_data["subtopics"] = subtopics
        print(f"  {cat_data['name']}: {len(subtopics)}トピック")

    # 結果を保存
    output = {
        "generated_at": "2025-10-22",
        "source": {
            "ocr_pages": len(ocr_data),
            "wind_eikyo_chars": len(wind_text)
        },
        "categories": categories
    }

    output_path = '/home/planj/patshinko-exam-app/backend/PATSHINKO_EXAM_STRUCTURE.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 出力: {output_path}")
    print("\n【抽出結果サマリー】")
    for cat in categories.values():
        print(f"  {cat['name']}: {len(cat['subtopics'])}トピック")

if __name__ == '__main__':
    main()

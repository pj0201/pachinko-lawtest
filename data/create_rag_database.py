#!/usr/bin/env python3
"""
講習テキストOCRデータをRAGデータベースに変換
47テーマ別にテキストファイルを生成
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# パス設定
OCR_FILE = Path("/home/planj/patshinko-exam-app/data/ocr_results_corrected.json")
RAG_BASE = Path("/home/planj/patshinko-exam-app/rag_data")
LECTURE_DIR = RAG_BASE / "lecture_text"
LEGAL_DIR = RAG_BASE / "legal_references"

# 47テーマ定義（DEDUPED_BASE.jsonから抽出）
THEMES = {
    # 不正対策 (8テーマ)
    "セキュリティ確保": {"category": "不正対策", "keywords": ["セキュリティ", "保安", "防犯", "監視"]},
    "不正改造の防止": {"category": "不正対策", "keywords": ["不正改造", "改造防止", "不正防止"]},
    "セキュリティアップデート": {"category": "不正対策", "keywords": ["アップデート", "更新", "バージョン"]},
    "不正改造の具体的パターン": {"category": "不正対策", "keywords": ["不正パターン", "改造事例", "違反事例"]},
    "不正検出技術": {"category": "不正対策", "keywords": ["検出", "発見", "検査"]},
    "不正行為の罰則": {"category": "不正対策", "keywords": ["罰則", "処罰", "懲役", "罰金"]},
    "不正防止チェックリスト": {"category": "不正対策", "keywords": ["チェックリスト", "確認事項", "点検"]},
    "不正防止対策要綱": {"category": "不正対策", "keywords": ["対策要綱", "防止要綱", "ガイドライン"]},

    # 営業時間・規制 (7テーマ)
    "営業禁止時間": {"category": "営業時間・規制", "keywords": ["禁止時間", "営業時間", "深夜", "午前"]},
    "営業停止命令": {"category": "営業時間・規制", "keywords": ["営業停止", "停止命令", "業務停止"]},
    "時間帯別営業制限": {"category": "営業時間・規制", "keywords": ["時間帯", "営業制限", "時間制限"]},
    "営業禁止日": {"category": "営業時間・規制", "keywords": ["禁止日", "休業日", "営業日"]},
    "営業停止命令の内容": {"category": "営業時間・規制", "keywords": ["命令内容", "停止内容", "処分内容"]},
    "営業停止期間の計算": {"category": "営業時間・規制", "keywords": ["期間計算", "停止期間", "日数"]},
    "違反時の行政処分": {"category": "営業時間・規制", "keywords": ["行政処分", "違反処分", "制裁"]},

    # 営業許可関連 (7テーマ)
    "営業許可は無期限有効": {"category": "営業許可関連", "keywords": ["無期限", "有効期間", "許可期限"]},
    "営業許可と型式検定の違い": {"category": "営業許可関連", "keywords": ["型式検定", "検定との違い", "許可と検定"]},
    "営業許可取得の要件": {"category": "営業許可関連", "keywords": ["許可要件", "取得要件", "申請要件"]},
    "営業許可の行政手続き": {"category": "営業許可関連", "keywords": ["行政手続き", "申請手続き", "許可手続き"]},
    "営業許可と営業実績の関係": {"category": "営業許可関連", "keywords": ["営業実績", "実績", "業績"]},
    "営業許可の失効事由": {"category": "営業許可関連", "keywords": ["失効", "失効事由", "効力喪失"]},
    "営業許可の取消し要件": {"category": "営業許可関連", "keywords": ["取消し", "取消要件", "撤回"]},

    # 型式検定関連 (6テーマ)
    "遊技機型式検定は3年有効": {"category": "型式検定関連", "keywords": ["3年", "有効期間", "検定期間"]},
    "型式検定更新申請のタイミング": {"category": "型式検定関連", "keywords": ["更新", "申請タイミング", "更新時期"]},
    "型式検定の申請方法": {"category": "型式検定関連", "keywords": ["申請方法", "検定申請", "手続き"]},
    "型式検定と製造者の責任": {"category": "型式検定関連", "keywords": ["製造者", "責任", "製造責任"]},
    "型式検定不合格時の手続き": {"category": "型式検定関連", "keywords": ["不合格", "再申請", "不適合"]},
    "型式検定と中古機の関係": {"category": "型式検定関連", "keywords": ["中古機", "中古遊技機", "流通"]},

    # 景品規制 (5テーマ)
    "景品の種類制限": {"category": "景品規制", "keywords": ["景品", "種類制限", "景品規制"]},
    "景品の種類制限詳細": {"category": "景品規制", "keywords": ["景品詳細", "制限詳細", "具体例"]},
    "景品交換の規制": {"category": "景品規制", "keywords": ["景品交換", "交換規制", "換金"]},
    "賞源有効利用促進法": {"category": "景品規制", "keywords": ["資源有効利用", "促進法", "リサイクル"]},
    "リサイクル推進法との関係": {"category": "景品規制", "keywords": ["リサイクル", "推進法", "循環型"]},

    # 遊技機管理 (14テーマ)
    "新台設置の手続き": {"category": "遊技機管理", "keywords": ["新台", "設置手続き", "新規設置"]},
    "中古遊技機の取扱い": {"category": "遊技機管理", "keywords": ["中古", "中古機", "中古遊技機"]},
    "遊技機の保守管理": {"category": "遊技機管理", "keywords": ["保守", "保守管理", "メンテナンス"]},
    "新台導入時の確認事項": {"category": "遊技機管理", "keywords": ["導入確認", "新台確認", "確認事項"]},
    "設置済み遊技機の交換手続き": {"category": "遊技機管理", "keywords": ["交換", "交換手続き", "入替"]},
    "遊技機の点検・保守計画": {"category": "遊技機管理", "keywords": ["点検", "保守計画", "定期点検"]},
    "故障遊技機の対応": {"category": "遊技機管理", "keywords": ["故障", "故障対応", "トラブル"]},
    "遊技機の製造番号管理": {"category": "遊技機管理", "keywords": ["製造番号", "番号管理", "シリアル"]},
    "基板ケースのかしめと管理": {"category": "遊技機管理", "keywords": ["基板", "かしめ", "ケース"]},
    "チップのセキュリティ": {"category": "遊技機管理", "keywords": ["チップ", "IC", "ROM"]},
    "外部端子板の管理": {"category": "遊技機管理", "keywords": ["外部端子", "端子板", "接続端子"]},
    "旧機械の回収と廃棄": {"category": "遊技機管理", "keywords": ["回収", "廃棄", "旧機械", "撤去"]},
    "リサイクルプロセス": {"category": "遊技機管理", "keywords": ["リサイクル", "再利用", "循環"]},
    "中古遊技機の流通管理": {"category": "遊技機管理", "keywords": ["流通", "流通管理", "中古流通"]},
}


def load_ocr_data():
    """OCRデータをロード"""
    print(f"📂 {OCR_FILE} をロード中...")
    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  ✅ {len(data)} ページをロード")
    return data


def extract_legal_references(ocr_pages):
    """風営法条文を抽出"""
    legal_sections = defaultdict(list)

    for page in ocr_pages:
        text = page.get('text', '')
        page_num = page.get('page_number', 0)

        # 風営法条文のパターン検出
        if re.search(r'第\d+条|風営法|風俗営業等の規制', text):
            # 条文番号を抽出
            article_matches = re.findall(r'第(\d+)条', text)
            for article in article_matches:
                article_num = int(article)
                section_key = f"{(article_num-1)//10 * 10 + 1}〜{((article_num-1)//10 + 1) * 10}"
                legal_sections[section_key].append({
                    'page': page_num,
                    'text': text,
                    'article': article_num
                })

    return legal_sections


def classify_page_by_theme(page_text, page_num):
    """ページを47テーマに分類"""
    matched_themes = []

    for theme_name, theme_info in THEMES.items():
        keywords = theme_info['keywords']

        # キーワードマッチングスコア計算
        score = sum(1 for keyword in keywords if keyword in page_text)

        if score > 0:
            matched_themes.append({
                'theme': theme_name,
                'category': theme_info['category'],
                'score': score,
                'page': page_num
            })

    return matched_themes


def create_theme_files(ocr_pages):
    """テーマ別RAGファイル作成"""
    theme_contents = defaultdict(list)

    print("\n📊 各ページを47テーマに分類中...")

    for page in ocr_pages:
        text = page.get('text', '')
        page_num = page.get('page_number', 0)

        if not text.strip():
            continue

        # テーマ分類
        matched = classify_page_by_theme(text, page_num)

        for match in matched:
            theme_name = match['theme']
            theme_contents[theme_name].append({
                'page': page_num,
                'text': text,
                'score': match['score']
            })

    # テーマ別ファイルに保存
    print("\n💾 テーマ別ファイルを作成中...")

    for idx, (theme_name, pages) in enumerate(sorted(theme_contents.items()), 1):
        if not pages:
            print(f"  ⚠️  {theme_name}: データなし")
            continue

        # ファイル名生成
        filename = f"theme_{idx:03d}_{theme_name}.txt"
        filepath = LECTURE_DIR / filename

        # コンテンツ生成
        content = f"# {theme_name}\n\n"
        content += f"**カテゴリ**: {THEMES[theme_name]['category']}\n"
        content += f"**キーワード**: {', '.join(THEMES[theme_name]['keywords'])}\n"
        content += f"**ページ数**: {len(pages)}\n\n"
        content += "---\n\n"

        # ページ内容をスコア順にソート
        sorted_pages = sorted(pages, key=lambda x: x['score'], reverse=True)

        for page_info in sorted_pages:
            content += f"## ページ {page_info['page']} (関連度: {page_info['score']})\n\n"
            content += page_info['text']
            content += "\n\n---\n\n"

        # ファイル保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ {filename}: {len(pages)}ページ")

    return theme_contents


def create_legal_files(legal_sections):
    """風営法条文ファイル作成"""
    print("\n📜 風営法条文ファイルを作成中...")

    for section_range, articles in sorted(legal_sections.items()):
        filename = f"風営法_第{section_range}条.txt"
        filepath = LEGAL_DIR / filename

        # コンテンツ生成
        content = f"# 風営法 第{section_range}条\n\n"
        content += f"**総ページ数**: {len(articles)}\n\n"
        content += "---\n\n"

        # 条文番号順にソート
        sorted_articles = sorted(articles, key=lambda x: x['article'])

        for article_info in sorted_articles:
            content += f"## 第{article_info['article']}条 (ページ {article_info['page']})\n\n"
            content += article_info['text']
            content += "\n\n---\n\n"

        # ファイル保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ {filename}: {len(articles)}条文")


def create_mapping_document(theme_contents):
    """テーママッピングドキュメント作成"""
    print("\n📋 テーママッピングドキュメントを作成中...")

    filepath = RAG_BASE / "theme_mapping.md"

    content = "# 講習テキスト → 47テーマ マッピング\n\n"
    content += "**生成日**: 2025-10-22\n"
    content += f"**総テーマ数**: {len(THEMES)}\n\n"
    content += "---\n\n"

    # カテゴリ別にグループ化
    categories = {}
    for theme_name, theme_info in THEMES.items():
        cat = theme_info['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(theme_name)

    for category, themes in sorted(categories.items()):
        content += f"## {category} ({len(themes)}テーマ)\n\n"

        for idx, theme_name in enumerate(sorted(themes), 1):
            page_count = len(theme_contents.get(theme_name, []))
            content += f"### {idx}. {theme_name}\n\n"
            content += f"- **カテゴリ**: {category}\n"
            content += f"- **キーワード**: {', '.join(THEMES[theme_name]['keywords'])}\n"
            content += f"- **講習テキスト該当ページ数**: {page_count}\n"
            content += f"- **ファイル**: `lecture_text/theme_{list(THEMES.keys()).index(theme_name)+1:03d}_{theme_name}.txt`\n\n"

        content += "---\n\n"

    # 統計情報
    content += "## 統計情報\n\n"
    content += f"- **総テーマ数**: {len(THEMES)}\n"
    content += f"- **カテゴリ数**: {len(categories)}\n"
    content += f"- **テーマ別平均ページ数**: {sum(len(pages) for pages in theme_contents.values()) / len(theme_contents):.1f}\n\n"

    # ファイル保存
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✅ theme_mapping.md 作成完了")


def main():
    print("=" * 80)
    print("講習テキストRAG化スクリプト")
    print("=" * 80)

    # OCRデータロード
    ocr_pages = load_ocr_data()

    # 風営法条文抽出
    legal_sections = extract_legal_references(ocr_pages)
    create_legal_files(legal_sections)

    # テーマ別ファイル作成
    theme_contents = create_theme_files(ocr_pages)

    # マッピングドキュメント作成
    create_mapping_document(theme_contents)

    print("\n" + "=" * 80)
    print("✅ RAGデータベース作成完了！")
    print("=" * 80)
    print(f"\n📁 出力先:")
    print(f"  - 講習テキスト: {LECTURE_DIR}")
    print(f"  - 風営法条文: {LEGAL_DIR}")
    print(f"  - マッピング: {RAG_BASE / 'theme_mapping.md'}")
    print()


if __name__ == '__main__':
    main()

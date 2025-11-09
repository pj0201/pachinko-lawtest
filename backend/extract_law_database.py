#!/usr/bin/env python3
"""
法律データベース抽出スクリプト
風営法および施行規則PDFから正確に条文を抽出し、lawDatabase.js形式で出力
Branch article numbers (第7条の2, etc.) を正しく処理
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF

class JapaneseLegalTextExtractor:
    """日本の法律文書からテキストを抽出"""

    # 日本語数字から数値への変換マップ
    KANJI_TO_NUM = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '百': 100, '千': 1000
    }

    def __init__(self, pdf_path: str, law_name: str):
        self.pdf_path = Path(pdf_path)
        self.law_name = law_name
        self.chapters = []
        self.current_chapter = None
        self.current_article = None

    def kanji_to_arabic(self, kanji_str: str) -> int:
        """日本語数字をアラビア数字に変換

        Examples:
            七 -> 7
            十 -> 10
            二十 -> 20
            三十一 -> 31
            百 -> 100
        """
        if not kanji_str:
            return 0

        total = 0
        temp = 0

        for char in kanji_str:
            if char not in self.KANJI_TO_NUM:
                continue

            value = self.KANJI_TO_NUM[char]

            if value >= 10:  # 十, 百, 千
                if temp == 0:
                    temp = 1
                total += temp * value
                temp = 0
            else:
                temp = value

        return total + temp

    def extract_chapter_number(self, text: str) -> Optional[int]:
        """章番号を抽出

        Examples:
            第一章 -> 1
            第七章 -> 7
        """
        match = re.search(r'第([一二三四五六七八九十百]+)章', text)
        if match:
            return self.kanji_to_arabic(match.group(1))
        return None

    def is_article_heading(self, text: str) -> bool:
        """条文の見出しかどうかを判定

        条文の定義（見出し）と条文への言及を区別
        """
        # 肯定パターン: 第X条　（全角スペースが続く）で始まる
        # 例: 第一条　この法律は...
        # 例: 第七条の二　公安委員会は...
        if re.match(r'^第[一二三四五六七八九十百千]+条(?:の[一二三四五六七八九十百千]+)?　', text):
            return True

        return False

    def extract_article_info(self, text: str) -> Optional[Tuple[str, Optional[str]]]:
        """条文番号と枝番を抽出（見出しのみ）

        Returns:
            (article_num, branch_num) or None

        Examples:
            第七条 -> ("7", None)
            第七条の二 -> ("7", "2")
            第三十一条の二十八 -> ("31", "28")
        """
        # 条文見出しかどうかをチェック
        if not self.is_article_heading(text):
            return None

        # パターン1: 第X条のY (branch article)
        match = re.search(r'第([一二三四五六七八九十百千]+)条の([一二三四五六七八九十百千]+)', text)
        if match:
            article_num = str(self.kanji_to_arabic(match.group(1)))
            branch_num = str(self.kanji_to_arabic(match.group(2)))
            return (article_num, branch_num)

        # パターン2: 第X条 (regular article)
        match = re.search(r'第([一二三四五六七八九十百千]+)条', text)
        if match:
            article_num = str(self.kanji_to_arabic(match.group(1)))
            return (article_num, None)

        return None

    def extract_article_title(self, text: str) -> str:
        """条文のタイトルを抽出

        条文番号の後、括弧内のテキストをタイトルとして抽出
        例: 第七条（許可の基準） -> "許可の基準"
        括弧がない場合は本文の最初の部分を使用
        """
        # パターン1: 第X条（タイトル） or 第X条のY（タイトル）
        match = re.search(r'第[一二三四五六七八九十百千]+条(?:の[一二三四五六七八九十百千]+)?[　\s]*（([^）]+)）', text)
        if match:
            return match.group(1).strip()

        # パターン2: 括弧がない場合、本文の最初の20文字程度を取得
        match = re.search(r'第[一二三四五六七八九十百千]+条(?:の[一二三四五六七八九十百千]+)?　(.{1,30})', text)
        if match:
            title = match.group(1).strip()
            # 文の途中で切らないよう、句読点まで取得
            if '。' in title:
                title = title.split('。')[0]
            elif '、' in title:
                title = title.split('、')[0]
            return title

        return ""

    def clean_article_text(self, text: str) -> str:
        """条文本文をクリーニング"""
        # 余分な空白を削除
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def parse_toc_article_range(self, toc_text: str) -> Tuple[Optional[int], Optional[int]]:
        """目次から条文範囲を抽出

        Examples:
            （第一条・第二条） -> (1, 2)
            （第三条―第十一条） -> (3, 11)
            （第三十一条の二―第三十一条の六） -> (31, 31)
        """
        # パターン1: 第X条―第Y条
        match = re.search(r'第([一二三四五六七八九十百千]+)条.*第([一二三四五六七八九十百千]+)条', toc_text)
        if match:
            start = self.kanji_to_arabic(match.group(1))
            end = self.kanji_to_arabic(match.group(2))
            return (start, end)

        # パターン2: 第X条・第Y条
        match = re.search(r'第([一二三四五六七八九十百千]+)条・第([一二三四五六七八九十百千]+)条', toc_text)
        if match:
            start = self.kanji_to_arabic(match.group(1))
            end = self.kanji_to_arabic(match.group(2))
            return (start, end)

        # パターン3: 第X条のみ
        match = re.search(r'第([一二三四五六七八九十百千]+)条', toc_text)
        if match:
            num = self.kanji_to_arabic(match.group(1))
            return (num, num)

        return (None, None)

    def process_pdf(self) -> Dict:
        """PDFを処理してデータベース構造を生成"""
        doc = fitz.open(self.pdf_path)
        full_text = ""

        # 全ページのテキストを抽出
        for page_num in range(len(doc)):
            page = doc[page_num]
            full_text += page.get_text()

        doc.close()

        # 行ごとに分割
        lines = full_text.split('\n')

        # Phase 1: 目次を解析して章構造と条文範囲を把握
        chapter_article_ranges = {}  # {chapter_num: (start_article, end_article)}
        chapter_names = {}  # {chapter_num: chapter_name}

        for line in lines[:100]:  # 最初の100行から目次を探す
            line = line.strip()
            chapter_match = re.match(r'^第([一二三四五六七八九十百]+)章[　\s]+(.+)', line)
            if chapter_match:
                chapter_num = self.kanji_to_arabic(chapter_match.group(1))
                full_text_with_range = chapter_match.group(2).strip()

                # 括弧内の条文範囲を抽出
                range_match = re.search(r'[（(]([^)）]+)[)）]', full_text_with_range)
                if range_match:
                    range_text = range_match.group(1)
                    start, end = self.parse_toc_article_range(range_text)
                    if start and end:
                        chapter_article_ranges[chapter_num] = (start, end)

                # 章名（括弧を除く）
                chapter_name = re.sub(r'[（(].*?[)）]', '', full_text_with_range).strip()
                chapter_names[chapter_num] = chapter_name

        # 章を作成し、範囲が指定されていない章は前後から推定
        sorted_chapters = sorted(chapter_names.keys())
        for i, chapter_num in enumerate(sorted_chapters):
            if chapter_num not in chapter_article_ranges:
                # 範囲が指定されていない場合は前後の章から推定
                if i > 0 and i < len(sorted_chapters) - 1:
                    prev_chapter = sorted_chapters[i - 1]
                    next_chapter = sorted_chapters[i + 1]
                    if prev_chapter in chapter_article_ranges and next_chapter in chapter_article_ranges:
                        prev_end = chapter_article_ranges[prev_chapter][1]
                        next_start = chapter_article_ranges[next_chapter][0]
                        # 前の章の次の条文から次の章の前の条文まで
                        chapter_article_ranges[chapter_num] = (prev_end + 1, next_start - 1)

            self.chapters.append({
                'chapterNum': chapter_num,
                'chapterName': chapter_names[chapter_num],
                'articles': []
            })

        # Phase 2: 条文を抽出して適切な章に割り当て
        current_article_dict = None
        article_text_buffer = []
        in_main_text = False
        reached_amendments = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 附則（改正規定）の検出 - ここで抽出を停止
            if re.match(r'^附[\s　]*則', line) and in_main_text:
                reached_amendments = True
                break

            # 条文の検出
            article_info = self.extract_article_info(line)
            if article_info:
                in_main_text = True  # 条文が始まったら本文開始とみなす
                # 前の条文を保存
                if current_article_dict and article_text_buffer:
                    current_article_dict['text'] = self.clean_article_text(' '.join(article_text_buffer))
                    article_text_buffer = []

                article_num, branch_num = article_info
                title = self.extract_article_title(line)

                # 条文番号の表示形式を決定
                if branch_num:
                    display_num = f"{article_num}の{branch_num}"
                else:
                    display_num = article_num

                current_article_dict = {
                    'articleNum': display_num,
                    'title': title,
                    'text': ''
                }

                # 条文番号から適切な章を見つける
                article_number = int(article_num)
                target_chapter_idx = 0

                for chapter_num, (start, end) in chapter_article_ranges.items():
                    if start <= article_number <= end:
                        # 章番号に対応するインデックスを見つける
                        for idx, chapter in enumerate(self.chapters):
                            if chapter['chapterNum'] == chapter_num:
                                target_chapter_idx = idx
                                break
                        break

                # 章が存在しない場合はデフォルト章を作成
                if not self.chapters:
                    self.chapters.append({
                        'chapterNum': 1,
                        'chapterName': '総則',
                        'articles': []
                    })
                    target_chapter_idx = 0

                self.chapters[target_chapter_idx]['articles'].append(current_article_dict)

                # 条文本文の開始（第X条　以降の部分）
                text_match = re.search(r'第[一二三四五六七八九十百千]+条(?:の[一二三四五六七八九十百千]+)?　(.+)', line)
                if text_match:
                    article_text_buffer.append(text_match.group(1).strip())
                continue

            # 条文本文の継続（既に条文が開始されている場合のみ）
            if current_article_dict:
                article_text_buffer.append(line)

        # 最後の条文を保存
        if current_article_dict and article_text_buffer:
            current_article_dict['text'] = self.clean_article_text(' '.join(article_text_buffer))

        # 重複を削除（各章内で最初の出現のみ保持）
        for chapter in self.chapters:
            seen_articles = set()
            unique_articles = []
            for article in chapter['articles']:
                if article['articleNum'] not in seen_articles:
                    seen_articles.add(article['articleNum'])
                    unique_articles.append(article)
            chapter['articles'] = unique_articles

        return {
            'name': self.law_name,
            'chapters': self.chapters
        }

    def to_javascript(self, data: Dict) -> str:
        """JavaScriptのオブジェクト形式に変換"""
        js_code = f"export const {self.sanitize_const_name(data['name'])} = {{\n"
        js_code += f"  name: '{data['name']}',\n"
        js_code += "  chapters: [\n"

        for chapter in data['chapters']:
            js_code += "    {\n"
            js_code += f"      chapterNum: {chapter['chapterNum']},\n"
            js_code += f"      chapterName: '{self.escape_js_string(chapter['chapterName'])}',\n"
            js_code += "      articles: [\n"

            for article in chapter['articles']:
                js_code += "        {\n"
                js_code += f"          articleNum: '{article['articleNum']}',\n"
                js_code += f"          title: '{self.escape_js_string(article['title'])}',\n"
                js_code += f"          text: `{self.escape_template_string(article['text'])}`\n"
                js_code += "        },\n"

            js_code += "      ]\n"
            js_code += "    },\n"

        js_code += "  ]\n"
        js_code += "}\n"

        return js_code

    @staticmethod
    def sanitize_const_name(name: str) -> str:
        """定数名を適切な形式に変換"""
        # 風営法 -> WIND_BUSINESS_LAW
        # 風営法施行規則 -> WIND_BUSINESS_REGULATION
        if '施行規則' in name:
            return 'WIND_BUSINESS_REGULATION'
        else:
            return 'WIND_BUSINESS_LAW'

    @staticmethod
    def escape_js_string(text: str) -> str:
        """JavaScript文字列用にエスケープ"""
        text = text.replace('\\', '\\\\')
        text = text.replace("'", "\\'")
        text = text.replace('\n', '\\n')
        return text

    @staticmethod
    def escape_template_string(text: str) -> str:
        """JavaScriptテンプレートリテラル用にエスケープ"""
        text = text.replace('\\', '\\\\')
        text = text.replace('`', '\\`')
        text = text.replace('${', '\\${')
        return text


def main():
    """メイン実行関数"""
    # プロジェクトルート
    project_root = Path(__file__).parent.parent
    pdf_dir = project_root / 'backend' / 'static' / 'pdfs'
    output_dir = project_root / 'backend' / 'extracted_laws'

    output_dir.mkdir(exist_ok=True)

    # 処理するPDF
    pdfs = [
        ('風俗営業等の規制及び業務の適正化等に関する法律.pdf', '風営法'),
        ('風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf', '風営法施行規則')
    ]

    all_js_code = []

    for pdf_filename, law_name in pdfs:
        pdf_path = pdf_dir / pdf_filename

        if not pdf_path.exists():
            print(f"❌ PDF not found: {pdf_path}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing: {pdf_filename}")
        print(f"{'='*60}\n")

        extractor = JapaneseLegalTextExtractor(str(pdf_path), law_name)
        data = extractor.process_pdf()

        # 統計情報を表示
        total_articles = sum(len(ch['articles']) for ch in data['chapters'])
        print(f"✓ Extracted {len(data['chapters'])} chapters")
        print(f"✓ Extracted {total_articles} articles")

        # 重複チェック
        article_nums = []
        for chapter in data['chapters']:
            for article in chapter['articles']:
                article_nums.append(article['articleNum'])

        duplicates = [num for num in set(article_nums) if article_nums.count(num) > 1]
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate article numbers: {duplicates[:5]}")
        else:
            print("✓ No duplicate article numbers")

        # 空のタイトルチェック
        empty_titles = sum(1 for ch in data['chapters'] for a in ch['articles'] if not a['title'])
        if empty_titles:
            print(f"⚠️  Found {empty_titles} articles with empty titles")
        else:
            print("✓ All articles have titles")

        # JSON出力
        json_output_path = output_dir / f"{law_name.replace('/', '_')}.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved JSON: {json_output_path}")

        # JavaScript出力
        js_code = extractor.to_javascript(data)
        all_js_code.append(js_code)

        js_output_path = output_dir / f"{law_name.replace('/', '_')}.js"
        with open(js_output_path, 'w', encoding='utf-8') as f:
            f.write(js_code)
        print(f"✓ Saved JS: {js_output_path}")

    # 統合されたlawDatabase.jsを生成
    combined_js_path = output_dir / 'lawDatabase.js'
    with open(combined_js_path, 'w', encoding='utf-8') as f:
        f.write('/**\n')
        f.write(' * 法律データベース\n')
        f.write(' * 自動生成ファイル - 直接編集しないでください\n')
        f.write(' * Generated by: extract_law_database.py\n')
        f.write(' */\n\n')
        f.write('\n\n'.join(all_js_code))

    print(f"\n{'='*60}")
    print(f"✓ Combined lawDatabase.js saved: {combined_js_path}")
    print(f"{'='*60}\n")
    print("\nNext steps:")
    print(f"1. Review the extracted data in: {output_dir}")
    print(f"2. Copy {combined_js_path} to src/constants/lawDatabase.js")
    print("3. Test the application")


if __name__ == '__main__':
    main()

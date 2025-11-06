/**
 * TextChunker - OCRテキストと法律文書のチャンク化処理
 *
 * 役割:
 * - JSONからテキスト抽出
 * - セクション単位でのスマートチャンク化
 * - メタデータ保持
 */

import fs from 'fs';
import path from 'path';

class TextChunker {
  constructor(config = {}) {
    this.chunkSize = config.chunkSize || 800; // 文字数
    this.overlapSize = config.overlapSize || 100; // オーバーラップ
    this.minChunkSize = config.minChunkSize || 100;
  }

  /**
   * OCR結果JSONからテキストを抽出してチャンク化
   * @param {string} jsonPath - ocr_results_corrected.jsonのパス
   * @returns {Array} チャンク配列 [{id, text, page, section, metadata}]
   */
  async chunkOCRResults(jsonPath) {
    console.log(`🔄 Reading OCR results from: ${jsonPath}`);

    try {
      const rawData = fs.readFileSync(jsonPath, 'utf-8');
      const ocrData = JSON.parse(rawData);

      const chunks = [];
      let globalChunkId = 0;

      // ページごとに処理
      if (Array.isArray(ocrData)) {
        for (const page of ocrData) {
          const pageNum = page.page_number || page.page || 0;
          const pageContent = page.content || page.text || '';

          // ページ内のセクションでさらに分割
          const sections = this.splitIntoSections(pageContent, pageNum);

          for (const section of sections) {
            // セクションをチャンク化
            const sectionChunks = this.chunkText(
              section.text,
              `page_${pageNum}_${section.index}`
            );

            for (const chunk of sectionChunks) {
              chunks.push({
                id: `ocr_${globalChunkId++}`,
                text: chunk,
                page: pageNum,
                section: section.title || `Page ${pageNum} Section ${section.index}`,
                source: 'ocr_corrected',
                timestamp: new Date().toISOString(),
                metadata: {
                  fileSize: chunk.length,
                  wordCount: chunk.split(/\s+/).length,
                }
              });
            }
          }
        }
      }

      console.log(`✅ OCR chunking complete: ${chunks.length} chunks created`);
      return chunks;
    } catch (error) {
      console.error('❌ Error chunking OCR results:', error);
      throw error;
    }
  }

  /**
   * テキストをセクション単位で分割
   * @param {string} text
   * @param {number} pageNum
   * @returns {Array}
   */
  splitIntoSections(text, pageNum) {
    // 章・節のパターン (例: "第1章" "1.1" "1)" など)
    const sectionPatterns = [
      /^第[零一二三四五六七八九十百千万]+[章節条]/m,
      /^\d+\.\s/m,
      /^\d+\)\s/m,
      /^【/m,
    ];

    let sections = [];
    let currentSection = '';
    let sectionIndex = 0;

    const lines = text.split('\n');
    for (const line of lines) {
      const isNewSection = sectionPatterns.some(pattern => pattern.test(line));

      if (isNewSection && currentSection.trim().length > 0) {
        sections.push({
          title: lines[0] || `Page ${pageNum}`,
          text: currentSection.trim(),
          index: sectionIndex++
        });
        currentSection = line + '\n';
      } else {
        currentSection += line + '\n';
      }
    }

    // 最後のセクション
    if (currentSection.trim().length > 0) {
      sections.push({
        title: `Section ${sectionIndex}`,
        text: currentSection.trim(),
        index: sectionIndex
      });
    }

    return sections.length > 0 ? sections : [{
      title: `Page ${pageNum}`,
      text: text,
      index: 0
    }];
  }

  /**
   * テキストをチャンク化（オーバーラップ付き）
   * @param {string} text
   * @param {string} sectionId
   * @returns {Array} チャンク配列
   */
  chunkText(text, sectionId) {
    const chunks = [];

    if (text.length <= this.chunkSize) {
      return [text];
    }

    let start = 0;
    while (start < text.length) {
      let end = Math.min(start + this.chunkSize, text.length);

      // 文字数制限内で最後の句読点で切る（自然な分割点を探す）
      if (end < text.length) {
        const lastPunctuation = Math.max(
          text.lastIndexOf('。', end),
          text.lastIndexOf('、', end)
        );
        if (lastPunctuation > start + this.minChunkSize) {
          end = lastPunctuation + 1;
        }
      }

      chunks.push(text.substring(start, end));

      // オーバーラップを考慮して次のチャンクへ
      start = end - this.overlapSize;
    }

    return chunks;
  }

  /**
   * Markdownテキストをチャンク化
   * @param {string} mdPath - Markdownファイルのパス
   * @returns {Array}
   */
  async chunkMarkdownFile(mdPath) {
    console.log(`🔄 Reading Markdown file: ${mdPath}`);

    try {
      const content = fs.readFileSync(mdPath, 'utf-8');
      return this.chunkMarkdown(content, path.basename(mdPath));
    } catch (error) {
      console.error('❌ Error reading Markdown file:', error);
      throw error;
    }
  }

  /**
   * Markdownをセクション単位でチャンク化
   * @param {string} content - Markdownコンテンツ
   * @param {string} filename
   * @returns {Array}
   */
  chunkMarkdown(content, filename = 'unknown') {
    const chunks = [];
    let globalChunkId = 0;

    // # で始まるセクションで分割
    const sections = content.split(/^#+\s+/m).slice(1);

    for (let i = 0; i < sections.length; i++) {
      const section = sections[i];
      const lines = section.split('\n');
      const title = lines[0] || `Section ${i}`;

      // タイトル行を除いたコンテンツ
      const sectionContent = lines.slice(1).join('\n').trim();

      if (sectionContent.length === 0) continue;

      // セクションを細かくチャンク化
      const textChunks = this.chunkText(sectionContent, title);

      for (const chunk of textChunks) {
        chunks.push({
          id: `md_${globalChunkId++}`,
          text: chunk,
          section: title,
          source: 'markdown',
          sourceFile: filename,
          timestamp: new Date().toISOString(),
          metadata: {
            fileSize: chunk.length,
            wordCount: chunk.split(/\s+/).length,
          }
        });
      }
    }

    console.log(`✅ Markdown chunking complete: ${chunks.length} chunks created from ${filename}`);
    return chunks;
  }

  /**
   * 複数ファイルから一括チャンク化
   * @param {Object} sources - {ocr: path, markdown: [paths]}
   * @returns {Object} {ocrChunks, mdChunks}
   */
  async chunkMultipleSources(sources) {
    const results = {
      ocrChunks: [],
      mdChunks: [],
      totalChunks: 0
    };

    if (sources.ocr) {
      try {
        results.ocrChunks = await this.chunkOCRResults(sources.ocr);
      } catch (error) {
        console.error('Error processing OCR source:', error);
      }
    }

    if (sources.markdown && Array.isArray(sources.markdown)) {
      for (const mdPath of sources.markdown) {
        try {
          const mdChunks = await this.chunkMarkdownFile(mdPath);
          results.mdChunks.push(...mdChunks);
        } catch (error) {
          console.error(`Error processing Markdown ${mdPath}:`, error);
        }
      }
    }

    results.totalChunks = results.ocrChunks.length + results.mdChunks.length;
    console.log(`📊 Total chunks created: ${results.totalChunks}`);

    return results;
  }

  /**
   * チャンクをJSONファイルに保存
   * @param {Array} chunks
   * @param {string} outputPath
   */
  saveChunks(chunks, outputPath) {
    try {
      fs.writeFileSync(
        outputPath,
        JSON.stringify(chunks, null, 2),
        'utf-8'
      );
      console.log(`✅ Chunks saved to: ${outputPath}`);
    } catch (error) {
      console.error('❌ Error saving chunks:', error);
      throw error;
    }
  }
}

export { TextChunker };

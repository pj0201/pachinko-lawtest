/**
 * 施行規則HTML → YAML 抽出スクリプト
 * 公式HTMLソースから施行規則全条文を抽出
 */

const fs = require('fs');
const path = require('path');

// HTMLソースファイルパス
const HTML_FILE = '360M50400000001_20251001_507M60400000017.html';

// 出力YAMLファイルパス
const OUTPUT_YAML = '施行規則_全条文.yaml';

console.log('🔍 施行規則YAML抽出開始...\n');

// HTMLファイルを読み込み
const htmlContent = fs.readFileSync(path.join(__dirname, '..', HTML_FILE), 'utf-8');

// 附則の開始位置を見つける（本則と附則を分離）
const supplProvisionStart = htmlContent.indexOf('<section id="" class="active SupplProvision">');
const mainTextContent = supplProvisionStart > 0
  ? htmlContent.substring(0, supplProvisionStart)
  : htmlContent;

console.log(`📝 本則のみを抽出（附則を除外）\n`);

// 条文抽出パターン
// 条文は <span style="font-weight: bold;">第X条</span> の形式
const articlePattern = /<span style="font-weight: bold;">第([一二三四五六七八九十百]+)条(?:の([一二三四五六七八九十]+))?<\/span>\s*<span data-xpath="">(.+?)<\/span>/g;

const articles = [];
let match;
let count = 0;

while ((match = articlePattern.exec(mainTextContent)) !== null) {
  const articleNumber = match[1] + (match[2] ? `の${match[2]}` : '');
  let content = match[3];

  // HTMLタグを除去
  content = content.replace(/<[^>]+>/g, '');

  // 数値の改行を除去（不正文字パターン）
  content = content.replace(/\n\d+\n/g, '');

  articles.push({
    number: articleNumber,
    content: content.trim()
  });

  count++;
}

console.log(`✅ ${count}条文を抽出しました\n`);

// YAML形式で出力
let yamlContent = `# 風俗営業等の規制及び業務の適正化等に関する法律施行規則
# 抽出日: ${new Date().toISOString().split('T')[0]}
# ソース: ${HTML_FILE}

articles:\n`;

articles.forEach(article => {
  // YAML形式で条文を出力
  yamlContent += `  - number: "${article.number}"\n`;
  yamlContent += `    content: |\n`;

  // コンテンツを適切にインデント
  const lines = article.content.split('\n');
  lines.forEach(line => {
    yamlContent += `      ${line}\n`;
  });

  yamlContent += '\n';
});

// YAMLファイルを保存
fs.writeFileSync(path.join(__dirname, '..', OUTPUT_YAML), yamlContent, 'utf-8');

console.log(`📄 YAMLファイルを生成しました: ${OUTPUT_YAML}`);
console.log(`📊 合計 ${count} 条文\n`);

// サマリー出力
console.log('=== 抽出サマリー ===');
console.log(`第一条: ${articles[0].content.substring(0, 50)}...`);
console.log(`第${articles[articles.length - 1].number}条: ${articles[articles.length - 1].content.substring(0, 50)}...`);

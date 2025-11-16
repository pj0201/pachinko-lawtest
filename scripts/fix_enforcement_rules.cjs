/**
 * 施行規則 lawDatabase.js 自動修正スクリプト
 * YAMLソースから冒頭欠け・不正文字を修正
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 施行規則lawDatabase.js修正開始...\n');

// YAMLソースを読み込み（手動パース）
const yamlPath = path.join(__dirname, '..', '施行規則_全条文.yaml');
const yamlContent = fs.readFileSync(yamlPath, 'utf-8');

// YAML手動パース
function parseYaml(content) {
  const articles = [];
  const articleMatches = content.matchAll(/- number: "(.+?)"\n    content: \|\n((?:      .+\n?)*)/g);

  for (const match of articleMatches) {
    const number = match[1];
    const contentLines = match[2].split('\n').filter(line => line.trim());
    const content = contentLines.map(line => line.replace(/^      /, '')).join('\n').trim();

    articles.push({ number, content });
  }

  return { articles };
}

const yamlData = parseYaml(yamlContent);
console.log(`📊 YAML: ${yamlData.articles.length}条文\n`);

// lawDatabase.jsを読み込み
const lawDbPath = path.join(__dirname, '..', 'src', 'constants', 'lawDatabase.js');
let lawDbContent = fs.readFileSync(lawDbPath, 'utf-8');

// 修正統計
const fixes = {
  truncatedStart: [],
  invalidChars: [],
  total: 0
};

// 各条文をYAMLソースと照合して修正
yamlData.articles.forEach(yamlArticle => {
  const articleNum = yamlArticle.number;
  const yamlText = yamlArticle.content;

  // lawDatabase.js内で条文を検索（articleNumフィールド）
  const articlePattern = new RegExp(
    `("articleNum":\\s*"${articleNum.replace(/の/g, 'の')}",\\s*"title":\\s*"[^"]+",\\s*"text":\\s*")([^"]*?)("\\s*})`,
    'g'
  );

  lawDbContent = lawDbContent.replace(articlePattern, (match, prefix, oldText, suffix) => {
    // 不正文字を除去（\nX\nパターン）
    const cleanedOldText = oldText.replace(/\\n\\d+\\n/g, '\\n');

    // エスケープ解除して比較
    const unescapedOldText = cleanedOldText.replace(/\\n/g, '\n');
    const normalizedOldText = unescapedOldText.replace(/\s+/g, ' ').trim();
    const normalizedYamlText = yamlText.replace(/\s+/g, ' ').trim();

    // 冒頭欠けチェック
    if (normalizedYamlText.includes(normalizedOldText) && !normalizedOldText.includes(normalizedYamlText)) {
      // YAMLから正しい条文を使用
      const escapedYamlText = yamlText.replace(/\n/g, '\\n').replace(/"/g, '\\"');
      fixes.truncatedStart.push({
        article: articleNum,
        oldLength: oldText.length,
        newLength: escapedYamlText.length
      });
      fixes.total++;
      return `${prefix}${escapedYamlText}${suffix}`;
    }

    // 不正文字のみの場合
    if (cleanedOldText !== oldText) {
      fixes.invalidChars.push({ article: articleNum });
      fixes.total++;
      return `${prefix}${cleanedOldText}${suffix}`;
    }

    return match;
  });
});

// 修正したlawDatabase.jsを保存
fs.writeFileSync(lawDbPath, lawDbContent, 'utf-8');

console.log('=== 修正完了 ===');
console.log(`✅ 冒頭欠け修正: ${fixes.truncatedStart.length}条文`);
console.log(`✅ 不正文字削除: ${fixes.invalidChars.length}条文`);
console.log(`📊 合計修正: ${fixes.total}条文\n`);

if (fixes.truncatedStart.length > 0) {
  console.log('【冒頭欠け修正条文】');
  fixes.truncatedStart.forEach(fix => {
    console.log(`  第${fix.article}条: ${fix.oldLength}文字 → ${fix.newLength}文字`);
  });
}

if (fixes.invalidChars.length > 0) {
  console.log('\n【不正文字削除条文】');
  fixes.invalidChars.forEach(fix => {
    console.log(`  第${fix.article}条`);
  });
}

console.log('\n✨ 施行規則修正完了');

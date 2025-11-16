/**
 * 施行規則 YAML ⇔ lawDatabase.js 照合スクリプト
 * 不正文字・冒頭欠け・構文エラーを検証
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 施行規則データ照合開始...\n');

// YAMLソースを読み込み（手動パース）
const yamlPath = path.join(__dirname, '..', '施行規則_全条文.yaml');
const yamlContent = fs.readFileSync(yamlPath, 'utf-8');

// YAML手動パース（簡易版）
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

// lawDatabase.jsを動的に読み込み
// ESモジュールなので、ファイルを読んで正規表現で抽出
const lawDbPath = path.join(__dirname, '..', 'src', 'constants', 'lawDatabase.js');
const lawDbContent = fs.readFileSync(lawDbPath, 'utf-8');

// WIND_BUSINESS_REGULATION の開始位置を検索
const startPos = lawDbContent.indexOf('export const WIND_BUSINESS_REGULATION');
if (startPos === -1) {
  console.error('❌ WIND_BUSINESS_REGULATION が見つかりません');
  process.exit(1);
}

// データの開始 { を見つける
const dataStart = lawDbContent.indexOf('{', startPos);

// 対応する閉じカッコを見つける（ネストを考慮）
let depth = 0;
let dataEnd = dataStart;
for (let i = dataStart; i < lawDbContent.length; i++) {
  if (lawDbContent[i] === '{') depth++;
  if (lawDbContent[i] === '}') depth--;
  if (depth === 0) {
    dataEnd = i + 1;
    break;
  }
}

const jsonStr = lawDbContent.substring(dataStart, dataEnd);

// JSONとして評価（簡易的）
const lawDbData = eval('(' + jsonStr + ')');

console.log(`📊 YAML: ${yamlData.articles.length}条文`);

// lawDatabase.jsから全条文を展開
const lawDbArticles = [];
lawDbData.chapters.forEach(chapter => {
  chapter.articles.forEach(article => {
    lawDbArticles.push({
      number: article.articleNum,
      title: article.title,
      content: article.text
    });
  });
});

console.log(`📊 lawDatabase.js: ${lawDbArticles.length}条文\n`);

// 照合結果
const issues = [];
let checked = 0;
let matched = 0;

// YAML側の条文を基準に照合
yamlData.articles.forEach(yamlArticle => {
  const articleNum = yamlArticle.number;

  // lawDatabase.jsで対応する条文を検索
  const lawDbArticle = lawDbArticles.find(a => a.number === articleNum);

  if (!lawDbArticle) {
    issues.push({
      type: 'MISSING',
      article: articleNum,
      message: `YAMLに存在するがlawDatabase.jsに存在しない`
    });
    return;
  }

  checked++;

  // コンテンツを正規化（空白・改行を統一）
  const yamlText = yamlArticle.content.replace(/\s+/g, ' ').trim();
  const lawDbText = lawDbArticle.content.replace(/\s+/g, ' ').trim();

  // 完全一致チェック
  if (yamlText === lawDbText) {
    matched++;
    return;
  }

  // 不一致の詳細を分析

  // 1. 冒頭欠けチェック（lawDbがYAMLより短く、YAMLの途中から始まっている）
  if (yamlText.includes(lawDbText) && !lawDbText.includes(yamlText)) {
    const missingStart = yamlText.substring(0, yamlText.indexOf(lawDbText));
    issues.push({
      type: 'TRUNCATED_START',
      article: articleNum,
      title: lawDbArticle.title,
      message: `冒頭${missingStart.length}文字欠け`,
      detail: `欠けている部分: "${missingStart.substring(0, 50)}..."`
    });
    return;
  }

  // 2. 不正文字チェック（\nX\n パターン）
  const invalidCharsInLawDb = lawDbText.match(/\n\d+\n/g);
  if (invalidCharsInLawDb && invalidCharsInLawDb.length > 0) {
    issues.push({
      type: 'INVALID_CHARS',
      article: articleNum,
      title: lawDbArticle.title,
      message: `不正文字 ${invalidCharsInLawDb.join(', ')} を検出`,
      detail: `パターン数: ${invalidCharsInLawDb.length}`
    });
    return;
  }

  // 3. その他の不一致
  issues.push({
    type: 'MISMATCH',
    article: articleNum,
    title: lawDbArticle.title,
    message: 'YAMLとlawDatabase.jsの内容が一致しません',
    detail: {
      yamlLength: yamlText.length,
      lawDbLength: lawDbText.length,
      yamlStart: yamlText.substring(0, 100),
      lawDbStart: lawDbText.substring(0, 100)
    }
  });
});

// レポート出力
console.log('=== 照合結果サマリー ===');
console.log(`✅ 一致: ${matched}条文`);
console.log(`⚠️  問題あり: ${issues.length}条文\n`);

if (issues.length > 0) {
  console.log('=== 問題詳細 ===\n');

  // 問題タイプ別に集計
  const byType = {};
  issues.forEach(issue => {
    if (!byType[issue.type]) byType[issue.type] = [];
    byType[issue.type].push(issue);
  });

  Object.keys(byType).forEach(type => {
    const typeIssues = byType[type];
    console.log(`\n## ${type} (${typeIssues.length}件)`);

    typeIssues.forEach(issue => {
      console.log(`\n第${issue.article}条: ${issue.title || '(タイトルなし)'}`);
      console.log(`  ${issue.message}`);
      if (issue.detail) {
        console.log(`  詳細: ${typeof issue.detail === 'object' ? JSON.stringify(issue.detail, null, 2) : issue.detail}`);
      }
    });
  });

  // レポートファイルを保存
  const reportPath = path.join(__dirname, '..', '施行規則_検証レポート.json');
  fs.writeFileSync(reportPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    summary: {
      total: yamlData.articles.length,
      checked,
      matched,
      issues: issues.length
    },
    issues
  }, null, 2), 'utf-8');

  console.log(`\n📄 詳細レポート: 施行規則_検証レポート.json`);
}

console.log('\n✨ 照合完了');
process.exit(issues.length > 0 ? 1 : 0);

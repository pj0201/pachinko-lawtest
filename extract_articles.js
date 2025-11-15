#!/usr/bin/env node
// lawDatabase.jsから該当条文を抽出するスクリプト

const fs = require('fs');
const path = require('path');

// lawDatabase.jsを読み込み
const lawDbPath = path.join(__dirname, 'src/constants/lawDatabase.js');
const content = fs.readFileSync(lawDbPath, 'utf-8');

// export文を取り除いてオブジェクトを取得
const codeToEval = content.replace(/^export\s+const\s+WIND_BUSINESS_LAW\s*=\s*/m, 'const WIND_BUSINESS_LAW = ');
eval(codeToEval.split('\n')[0] + '...' + codeToEval.slice(codeToEval.indexOf('{'))); // これはうまくいかない

// より安全なアプローチ: モジュールとして読み込む
const module = { exports: {} };
const wrappedCode = content.replace(/^export\s+const\s+(\w+)\s*=/gm, 'module.exports.$1 =');
eval(wrappedCode);

const WIND_BUSINESS_LAW = module.exports.WIND_BUSINESS_LAW;

// 対象条文
const TARGET_ARTICLES = [
    ["十九", "遊技料金等の規制"],
    ["二十", "遊技機の規制及び認定等"],
    ["二十一", "条例への委任"],
    ["二十二", "風俗営業を営む者の禁止行為等"],
    ["二十七", "営業等の届出"],
    ["二十八", "店舗型性風俗特殊営業の禁止区域等"],
    ["三十", "営業の停止等"],
];

console.log("=== lawDatabase.jsから抽出された条文 ===\n");

// 章から条文を検索
let found = 0;
for (const chapter of WIND_BUSINESS_LAW.chapters) {
    for (const article of chapter.articles) {
        const articleNum = article.articleNum;
        const title = article.title;
        const text = article.text || "";

        for (const [targetNum, targetTitle] of TARGET_ARTICLES) {
            if (articleNum === targetNum && title === targetTitle) {
                console.log(`【第${targetNum}条（${targetTitle}）】`);
                console.log(`冒頭: ${text.substring(0, 50)}...`);
                console.log(`文字数: ${text.length}`);
                console.log();
                found++;
            }
        }
    }
}

console.log(`合計 ${found} 条文が見つかりました。`);

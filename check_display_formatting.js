/**
 * 条文の改行・表示フォーマットをチェック
 */

import { WIND_BUSINESS_LAW } from './src/constants/lawDatabase.js';

console.log('=== 条文の改行・表示フォーマットチェック ===\n');

// 第二条（号がたくさんある条文）をチェック
const chapter1 = WIND_BUSINESS_LAW.chapters[0];
const article2 = chapter1.articles.find(art => art.articleNum === '二');

console.log('【第二条（用語の意義）】');
console.log('テキスト長:', article2.text.length);
console.log('改行数:', (article2.text.match(/\n/g) || []).length);
console.log('\n--- 最初の500文字 ---');
console.log(article2.text.substring(0, 500));
console.log('\n');

// 第二十二条（修正した条文）をチェック
const chapter3 = WIND_BUSINESS_LAW.chapters.find(ch => ch.chapterNum === 3);
const article22 = chapter3.articles.find(art => art.articleNum === '二十二');

console.log('【第二十二条（風俗営業を営む者の禁止行為等）】');
console.log('テキスト長:', article22.text.length);
console.log('改行数:', (article22.text.match(/\n/g) || []).length);
console.log('\n--- 全文表示 ---');
console.log(article22.text);
console.log('\n');

// 第三十条（長い条文）をチェック
const chapter4 = WIND_BUSINESS_LAW.chapters.find(ch => ch.chapterNum === 4);
const article30 = chapter4.articles.find(art => art.articleNum === '三十');

console.log('【第三十条（営業の停止等）】');
console.log('テキスト長:', article30.text.length);
console.log('改行数:', (article30.text.match(/\n/g) || []).length);
console.log('「9」の混入チェック:', article30.text.includes('9') ? '⚠️ 含まれている' : '✅ なし');
console.log('\n--- 最初の600文字 ---');
console.log(article30.text.substring(0, 600));
console.log('\n');

// whiteSpace: 'pre-wrap'での表示シミュレーション
console.log('===================');
console.log('【表示シミュレーション】');
console.log('===================\n');
console.log('LawViewer3Stageコンポーネントでは以下のスタイルが適用されます：');
console.log('  whiteSpace: "pre-wrap"');
console.log('  wordWrap: "break-word"');
console.log('\n↓ このスタイルにより、\\n は改行として表示されます。\n');

console.log('【第二十二条の表示例】');
console.log('─'.repeat(60));
console.log(article22.text);
console.log('─'.repeat(60));

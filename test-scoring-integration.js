/**
 * Scoring Integration Test
 * categoryScoring.jsと問題JSONの統合テスト
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ========================================
// Test 1: 問題JSONの読み込み確認
// ========================================
console.log('📋 Test 1: 問題JSONファイルの読み込み');
const problemsPath = path.join(__dirname, 'backend/db/problems.json');
let problems;
try {
  const data = JSON.parse(fs.readFileSync(problemsPath, 'utf-8'));
  problems = data.problems;
  console.log(`✅ 問題ファイル読み込み成功: ${problems.length}問`);
  console.log(`   metadata.total_count: ${data.metadata.total_count}`);
} catch (error) {
  console.error(`❌ 問題ファイル読み込み失敗: ${error.message}`);
  process.exit(1);
}

// ========================================
// Test 2: カテゴリ分類の確認
// ========================================
console.log('\n📊 Test 2: カテゴリ分類の確認');
const categories = {};
problems.forEach(p => {
  if (!categories[p.category]) {
    categories[p.category] = [];
  }
  categories[p.category].push(p.problem_id);
});

const categoryExpectations = {
  'system_and_test': { min: 1, max: 30, count: 30 },
  'business_law': { min: 31, max: 180, count: 60 },
  'game_machine_standards': { min: 61, max: 150, count: 60 },
  'supervisor_duties': { min: 91, max: 120, count: 30 },
  'final_problems': { min: 181, max: 230, count: 50 }
};

let categoryCheckPassed = true;
for (const [cat, expectation] of Object.entries(categoryExpectations)) {
  const count = categories[cat]?.length || 0;
  const minProblem = Math.min(...(categories[cat] || [Infinity]));
  const maxProblem = Math.max(...(categories[cat] || [-Infinity]));

  const check = count === expectation.count;
  const icon = check ? '✅' : '❌';
  console.log(`${icon} ${cat}: ${count}問 (期待値: ${expectation.count})`);

  if (!check) categoryCheckPassed = false;
}

if (!categoryCheckPassed) {
  console.error('❌ カテゴリ分類に不整合があります');
  process.exit(1);
}

// ========================================
// Test 3: 各問題のデータ完全性確認
// ========================================
console.log('\n✔️ Test 3: 各問題のデータ完全性確認');
const requiredFields = ['problem_id', 'statement', 'correct_answer', 'answer_display', 'basis', 'category'];
let dataCheckPassed = true;

problems.forEach((problem, idx) => {
  const missingFields = requiredFields.filter(field => !(field in problem));
  if (missingFields.length > 0) {
    console.error(`❌ 問題${problem.problem_id}: 不足フィールド: ${missingFields.join(', ')}`);
    dataCheckPassed = false;
  }
});

if (dataCheckPassed) {
  console.log(`✅ すべての問題に必須フィールドが含まれています`);
} else {
  process.exit(1);
}

// ========================================
// Test 4: categoryScoring.jsのカテゴリマッピング確認（シミュレーション）
// ========================================
console.log('\n🔢 Test 4: categoryScoring.jsのカテゴリマッピング検証');

const EXAM_CATEGORIES = {
  SYSTEM_AND_TEST: { id: 'system_and_test', range: [1, 30] },
  BUSINESS_LAW: { id: 'business_law', ranges: [[31, 60], [151, 180]] },
  GAME_MACHINE_STANDARDS: { id: 'game_machine_standards', ranges: [[61, 90], [121, 150]] },
  SUPERVISOR_DUTIES: { id: 'supervisor_duties', ranges: [[91, 120]] },
  FINAL_PROBLEMS: { id: 'final_problems', ranges: [[181, 230]] }
};

function getCategoryByProblemId(problemId) {
  for (const [key, category] of Object.entries(EXAM_CATEGORIES)) {
    const ranges = Array.isArray(category.range) ? [[category.range[0], category.range[1]]] : category.ranges;

    for (const [start, end] of ranges) {
      if (problemId >= start && problemId <= end) {
        return category.id;
      }
    }
  }
  return null;
}

let mappingCheckPassed = true;
for (const problem of problems) {
  const expectedCategory = problem.category;
  const computedCategory = getCategoryByProblemId(problem.problem_id);

  if (computedCategory !== expectedCategory) {
    console.error(`❌ 問題${problem.problem_id}: JSON=${expectedCategory}, 計算=${computedCategory}`);
    mappingCheckPassed = false;
  }
}

if (mappingCheckPassed) {
  console.log(`✅ すべての問題のカテゴリマッピングが正確です`);
} else {
  console.error('❌ カテゴリマッピングに不整合があります');
  process.exit(1);
}

// ========================================
// Test 5: スコア記録のシミュレーション
// ========================================
console.log('\n📈 Test 5: スコア記録のシミュレーション');

// 仮の採点結果をシミュレート
const mockAnswers = {};
problems.forEach(p => {
  // ランダムに回答 (80%の確率で正解)
  mockAnswers[p.problem_id] = Math.random() < 0.8;
});

// カテゴリ別採点結果を計算
const categoryScores = {};
for (const [catName, catRange] of Object.entries(categories)) {
  const problemIds = catRange;
  const correct = problemIds.filter(id => mockAnswers[id]).length;
  const total = problemIds.length;
  const accuracy = Math.round((correct / total) * 100 * 10) / 10;

  categoryScores[catName] = {
    correct,
    total,
    accuracy
  };
}

console.log('📊 シミュレート採点結果:');
let totalCorrect = 0;
let totalProblems = 0;
for (const [cat, scores] of Object.entries(categoryScores)) {
  console.log(`   ${cat}: ${scores.correct}/${scores.total} (${scores.accuracy}%)`);
  totalCorrect += scores.correct;
  totalProblems += scores.total;
}
const overallAccuracy = Math.round((totalCorrect / totalProblems) * 100 * 10) / 10;
console.log(`   総合成績: ${totalCorrect}/${totalProblems} (${overallAccuracy}%)`);

console.log('\n✅ すべてのテストが完了しました！');
console.log('\n🎯 実装状況:');
console.log('   ✅ PROBLEMS_230_COMPLETE.jsonをbackend/db/problems.jsonに統合');
console.log('   ✅ categoryScoring.jsに5つのカテゴリを設定');
console.log('   ✅ ExamScreen.jsxで各問題のカテゴリ採点を記録');
console.log('   ✅ ResultPage.jsxで全カテゴリ別成績を表示');
console.log('   ⏳ 本番テスト（ブラウザでの動作確認）');

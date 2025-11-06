#!/usr/bin/env node

/**
 * 1200問の品質チェック実行
 * 結果を JSON として出力
 */

import fs from 'fs';
import { ProblemQualityChecker } from './problem-quality-checker.js';

async function main() {
  try {
    // mock_problems.json を読み込み
    const filePath = '/home/planj/patshinko-exam-app/public/mock_problems.json';
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const problems = data.problems || [];

    console.log(`\n📋 品質チェック開始`);
    console.log(`ファイル: ${filePath}`);
    console.log(`問題数: ${problems.length}\n`);

    // チェック実行
    const checker = new ProblemQualityChecker();
    const checkResult = checker.checkAllProblems(problems);
    const report = checker.generateReport(checkResult);

    // コンソール出力（ハイライト）
    console.log('\n' + '='.repeat(70));
    console.log('📊 品質チェック結果サマリー');
    console.log('='.repeat(70));
    console.log(`✓ 総問題数: ${checkResult.totalProblems}`);
    console.log(`📈 平均スコア: ${checkResult.averageScore}/100`);
    console.log(`⚠️  重大問題率: ${checkResult.criticalIssueRate}%`);
    console.log(`✅ 健全な問題: ${checkResult.summary.healthyProblems.length}問`);
    console.log('='.repeat(70));

    // 重大エラーの TOP 10
    console.log('\n🔴 重大エラー TOP 10:');
    const topCritical = checkResult.summary.criticalProblems.slice(0, 10);
    topCritical.forEach((p, idx) => {
      console.log(`  ${idx + 1}. [${p.id}] ${p.issues[0]}`);
    });

    // カテゴリ別分析
    console.log('\n📂 カテゴリ別エラー率:');
    const categoryAnalysis = report.categoryAnalysis;
    Object.entries(categoryAnalysis).forEach(([cat, stats]) => {
      const rate = ((stats.critical / stats.total) * 100).toFixed(1);
      console.log(`  ${cat}: ${stats.critical}/${stats.total} (${rate}%)`);
    });

    // 改善提案
    console.log('\n💡 改善提案:');
    report.recommendations.forEach((rec, idx) => {
      console.log(`  ${idx + 1}. [${rec.priority}] ${rec.category}`);
      console.log(`     → ${rec.action}`);
    });

    // JSON ファイルに保存
    const outputPath = '/tmp/quality_check_report.json';
    fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
    console.log(`\n💾 詳細レポート保存: ${outputPath}`);

    // Worker2 と GPT-5 への報告用データを生成
    const reviewData = {
      timestamp: report.timestamp,
      summary: report.summary,
      criticalProblems: report.criticalProblems,
      errorAnalysis: report.errorAnalysis,
      recommendations: report.recommendations,
      reportPath: outputPath
    };

    const reviewPath = '/tmp/quality_review_request.json';
    fs.writeFileSync(reviewPath, JSON.stringify(reviewData, null, 2));
    console.log(`📤 レビュー要請データ保存: ${reviewPath}`);

    console.log('\n✅ チェック完了\n');

  } catch (error) {
    console.error('❌ エラー:', error.message);
    process.exit(1);
  }
}

main();

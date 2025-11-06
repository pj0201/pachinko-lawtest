#!/usr/bin/env node

/**
 * カバレッジ分析ツール
 * OCRソースと1200問の対応状況をチェック
 * - 各カテゴリのトピックがカバーされているか
 * - ソースに存在するが問題でカバーされていないトピック（抜け）
 */

import fs from 'fs';

class CoverageAnalyzer {
  constructor() {
    // 各カテゴリのキーワード定義
    this.categoryKeywords = {
      '営業許可・申請手続き': [
        '営業許可', '申請', '届け出', '営業', '要件',
        '遊技場営業', '営業者', '公安委員会', '営業所'
      ],
      '建物・設備基準': [
        '建物', '構造', '設備', '基準', '照度', '出入口',
        '建築', '施設', '部屋', 'テーブル'
      ],
      '従業員・管理者要件': [
        '従業員', '主任者', '資格', '要件', '取扱主任者',
        '管理者', '従業', '従事', '雇用', '禁止'
      ],
      '営業時間・休業': [
        '営業時間', '営業場所', '営業停止', '時間', '営業', 'スケジュール',
        '営業日', '営業所'
      ],
      '景品・景慮基準': [
        '景品', '交換', '景気', '基準', '顧客', '客'
      ],
      '法律・規制違反': [
        '違反', '処分', '停止', '取消', '行政', '違反行為',
        '不正', '規制', '法律'
      ],
      '実務・業務管理': [
        '実務', '対応', '報告', '記録', '管理', '業務',
        '取扱い', '保守', '保安'
      ]
    };

    this.coverageStats = {
      totalCategories: 0,
      coveredCategories: 0,
      totalTopics: 0,
      coveredTopics: 0,
      gaps: []
    };
  }

  /**
   * テキストからトピックを抽出
   */
  extractTopics(text, keywords) {
    const topics = [];
    for (const keyword of keywords) {
      const regex = new RegExp(keyword, 'g');
      const matches = text.match(regex);
      if (matches) {
        topics.push({
          keyword,
          count: matches.length,
          found: true
        });
      }
    }
    return topics;
  }

  /**
   * 問題文がトピックをカバーしているかチェック
   */
  checkCoverage(statement, explanation, source, keywords) {
    const text = `${statement} ${explanation} ${source || ''}`.toLowerCase();
    const coveredKeywords = [];

    for (const keyword of keywords) {
      if (text.includes(keyword)) {
        coveredKeywords.push(keyword);
      }
    }

    return coveredKeywords;
  }

  /**
   * 全1200問をスキャン
   */
  analyzeProblems(problems) {
    const coverage = {};

    // カテゴリ別のキーワードカバレッジを初期化
    for (const category of Object.keys(this.categoryKeywords)) {
      coverage[category] = {
        total: 0,
        covered: 0,
        keywords: {},
        problems: []
      };

      // キーワード別のカバレッジを初期化
      for (const keyword of this.categoryKeywords[category]) {
        coverage[category].keywords[keyword] = 0;
      }
    }

    // 1200問をスキャン
    for (const problem of problems) {
      const category = problem.category;
      if (!coverage[category]) continue;

      coverage[category].total++;

      const keywords = this.categoryKeywords[category];
      const covered = this.checkCoverage(
        problem.statement || '',
        problem.explanation || '',
        problem.source || '',
        keywords
      );

      if (covered.length > 0) {
        coverage[category].covered++;
        coverage[category].problems.push({
          id: problem.id,
          statement: problem.statement,
          coveredKeywords: covered
        });

        // キーワード別にカウント
        for (const keyword of covered) {
          coverage[category].keywords[keyword]++;
        }
      }
    }

    return coverage;
  }

  /**
   * カバレッジレポートを生成
   */
  generateReport(coverage) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalCategories: Object.keys(coverage).length,
        categoryGaps: [],
        keywordGaps: []
      },
      categoryDetails: {}
    };

    // カテゴリ別分析
    for (const [category, data] of Object.entries(coverage)) {
      const coverageRate = data.total > 0
        ? ((data.covered / data.total) * 100).toFixed(1)
        : 0;

      report.categoryDetails[category] = {
        totalProblems: data.total,
        coveredProblems: data.covered,
        coverageRate: parseFloat(coverageRate) + '%',
        uncoveredCount: data.total - data.covered,
        keywordCoverage: {}
      };

      // キーワード別カバレッジ
      for (const [keyword, count] of Object.entries(data.keywords)) {
        const rate = data.total > 0
          ? ((count / data.total) * 100).toFixed(1)
          : 0;

        report.categoryDetails[category].keywordCoverage[keyword] = {
          covered: count,
          coverageRate: parseFloat(rate) + '%'
        };

        // カバレッジが0のキーワードはギャップ
        if (count === 0) {
          report.summary.keywordGaps.push({
            category,
            keyword,
            issue: 'No problems cover this keyword'
          });
        }
      }

      // カテゴリ全体のカバレッジが低いかチェック
      if (parseFloat(coverageRate) < 50) {
        report.summary.categoryGaps.push({
          category,
          coverageRate: parseFloat(coverageRate) + '%',
          uncoveredCount: data.total - data.covered
        });
      }
    }

    return report;
  }

  /**
   * 詳細ギャップレポート
   */
  generateGapReport(coverage) {
    const gaps = {
      uncoveredKeywords: {},
      lowCoverageKeywords: {}
    };

    for (const [category, data] of Object.entries(coverage)) {
      for (const [keyword, count] of Object.entries(data.keywords)) {
        if (count === 0) {
          if (!gaps.uncoveredKeywords[category]) {
            gaps.uncoveredKeywords[category] = [];
          }
          gaps.uncoveredKeywords[category].push(keyword);
        } else if (count < data.total * 0.3) {
          // 30%未満のカバレッジ
          if (!gaps.lowCoverageKeywords[category]) {
            gaps.lowCoverageKeywords[category] = [];
          }
          gaps.lowCoverageKeywords[category].push({
            keyword,
            coverage: count,
            total: data.total,
            rate: ((count / data.total) * 100).toFixed(1) + '%'
          });
        }
      }
    }

    return gaps;
  }
}

async function main() {
  try {
    console.log('\n📋 カバレッジ分析開始');
    console.log('='.repeat(70));

    // 1200問を読み込み
    const problemsPath = '/home/planj/patshinko-exam-app/public/mock_problems.json';
    const problemsData = JSON.parse(fs.readFileSync(problemsPath, 'utf-8'));
    const problems = problemsData.problems || [];

    console.log(`問題数: ${problems.length}`);

    // 分析実行
    const analyzer = new CoverageAnalyzer();
    const coverage = analyzer.analyzeProblems(problems);
    const report = analyzer.generateReport(coverage);
    const gapReport = analyzer.generateGapReport(coverage);

    // コンソール出力
    console.log('\n📊 カテゴリ別カバレッジ:');
    console.log('-'.repeat(70));

    for (const [category, details] of Object.entries(report.categoryDetails)) {
      const rate = details.coverageRate;
      const emoji = parseFloat(rate) >= 80 ? '✅' : parseFloat(rate) >= 50 ? '⚠️ ' : '❌';
      console.log(`${emoji} ${category}: ${rate}`);
    }

    console.log('\n🔴 カバレッジギャップ:');
    console.log('-'.repeat(70));

    if (report.summary.keywordGaps.length > 0) {
      console.log(`未カバーのキーワード: ${report.summary.keywordGaps.length}個`);
      const grouped = {};
      for (const gap of report.summary.keywordGaps) {
        if (!grouped[gap.category]) grouped[gap.category] = [];
        grouped[gap.category].push(gap.keyword);
      }
      for (const [cat, keywords] of Object.entries(grouped)) {
        console.log(`  ${cat}: ${keywords.join(', ')}`);
      }
    }

    // ファイルに保存
    const reportPath = '/tmp/coverage_report.json';
    fs.writeFileSync(reportPath, JSON.stringify({
      report,
      gaps: gapReport
    }, null, 2));

    console.log(`\n💾 レポート保存: ${reportPath}`);
    console.log('\n✅ 分析完了\n');

  } catch (error) {
    console.error('❌ エラー:', error.message);
    process.exit(1);
  }
}

main();

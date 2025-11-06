#!/usr/bin/env node

/**
 * 高度な修正スクリプト
 * 残存する112問の複雑なエラーパターンを修正
 */

import fs from 'fs';

class AdvancedProblemFixer {
  constructor() {
    this.fixStats = {
      complexDuplicates: 0,
      brokenSentences: 0,
      malformedPatterns: 0,
      total: 0
    };

    // 既知の不正なパターンと修正方法
    this.knownPatterns = [
      // 3文字以上の単語の重複（より詳細）
      { pattern: /([ぁ-ん一-龥ー]{2,})\1/g, replacement: '$1', desc: '3文字以上単語重複' },
      // "～～" パターン
      { pattern: /～～+/g, replacement: '', desc: 'プレースホルダー重複' },
      // "のは～が" → "は"
      { pattern: /のは～が/g, replacement: 'は', desc: '複雑文法エラー' },
      // "のについて" → "について"
      { pattern: /のについて/g, replacement: 'について', desc: '文法エラー' },
      // "ののの" → "の"
      { pattern: /の{3,}/g, replacement: 'の', desc: 'の重複' },
    ];
  }

  /**
   * より高度な単語重複修正
   * 複数の異なるパターンに対応
   */
  fixComplexDuplicates(text) {
    let fixed = text;
    let count = 0;

    // パターン1: 2-3文字の単語が連続（例: キーキー、メンテナンスメンテナンス）
    const complexDuplicatePattern = /([ぁ-ん一-龥ー]{2,})\1+/g;
    const matches = text.match(complexDuplicatePattern);
    if (matches) {
      count += matches.length;
      fixed = fixed.replace(complexDuplicatePattern, '$1');
    }

    if (count > 0) {
      this.fixStats.complexDuplicates++;
    }

    return fixed;
  }

  /**
   * 壊れた文を修正
   */
  fixBrokenSentences(text) {
    let fixed = text;
    let count = 0;

    // 開始と終了が同じ単語の場合
    const brokenPattern = /^(.+?)(\1)(.*)$/;
    if (brokenPattern.test(fixed)) {
      count++;
      fixed = fixed.replace(brokenPattern, '$1$3');
    }

    if (count > 0) {
      this.fixStats.brokenSentences++;
    }

    return fixed;
  }

  /**
   * 既知のパターンに基づいて修正
   */
  fixKnownPatterns(text) {
    let fixed = text;
    let count = 0;

    for (const rule of this.knownPatterns) {
      const matches = fixed.match(rule.pattern);
      if (matches) {
        count += matches.length;
        fixed = fixed.replace(rule.pattern, rule.replacement);
      }
    }

    if (count > 0) {
      this.fixStats.malformedPatterns++;
    }

    return fixed;
  }

  /**
   * 問題文全体を修正
   */
  fixStatement(statement) {
    if (!statement) return statement;

    let fixed = statement;

    // 1. 複雑な単語重複を修正
    fixed = this.fixComplexDuplicates(fixed);

    // 2. 壊れた文を修正
    fixed = this.fixBrokenSentences(fixed);

    // 3. 既知のパターンを修正
    fixed = this.fixKnownPatterns(fixed);

    // 4. 余分な空白を削除
    fixed = fixed.replace(/\s+/g, ' ').trim();

    // 5. "は" の重複を修正（"はは" → "は"）
    fixed = fixed.replace(/は+/g, 'は');

    return fixed;
  }

  /**
   * 単一の問題を修正
   */
  fixProblem(problem) {
    this.fixStats.total++;

    const fixed = { ...problem };

    if (problem.statement) {
      fixed.statement = this.fixStatement(problem.statement);
    }

    if (problem.explanation) {
      fixed.explanation = this.fixStatement(problem.explanation);
    }

    return fixed;
  }

  /**
   * すべての問題を修正
   */
  fixAllProblems(problems) {
    return problems.map(p => this.fixProblem(p));
  }

  /**
   * 統計情報を表示
   */
  printStats() {
    console.log('\n' + '='.repeat(70));
    console.log('📊 高度な修正統計');
    console.log('='.repeat(70));
    console.log(`✅ 処理済み問題: ${this.fixStats.total}`);
    console.log(`   - 複雑な単語重複修正: ${this.fixStats.complexDuplicates}`);
    console.log(`   - 壊れた文修正: ${this.fixStats.brokenSentences}`);
    console.log(`   - 既知パターン修正: ${this.fixStats.malformedPatterns}`);
    console.log('='.repeat(70) + '\n');
  }
}

async function main() {
  try {
    const filePath = '/home/planj/patshinko-exam-app/public/mock_problems.json';
    console.log(`\n🔧 高度な修正開始`);
    console.log(`ファイル: ${filePath}`);

    // ファイルを読み込み
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const originalProblems = data.problems || [];

    console.log(`処理対象: ${originalProblems.length}問\n`);

    // 修正実行
    const fixer = new AdvancedProblemFixer();
    const fixedProblems = fixer.fixAllProblems(originalProblems);

    // 統計表示
    fixer.printStats();

    // 修正結果の例を表示
    console.log('📝 修正結果の例（エラーがあった問題）:\n');
    let exampleCount = 0;
    for (let i = 0; i < originalProblems.length && exampleCount < 5; i++) {
      const orig = originalProblems[i];
      const fixed = fixedProblems[i];

      if (orig.statement !== fixed.statement) {
        exampleCount++;
        console.log(`問${i + 1}:`);
        console.log(`  ❌ 修正前: "${orig.statement}"`);
        console.log(`  ✅ 修正後: "${fixed.statement}"`);
        console.log();
      }
    }

    // 修正されたデータを保存
    const fixedData = {
      ...data,
      problems: fixedProblems,
      lastAdvancedFixed: new Date().toISOString(),
      fixedBy: 'advanced-fix-problems.js'
    };

    fs.writeFileSync(filePath, JSON.stringify(fixedData, null, 2));
    console.log(`💾 修正済みファイルを保存しました`);
    console.log(`パス: ${filePath}\n`);

    console.log('✅ 高度な修正完了\n');

  } catch (error) {
    console.error('❌ エラー:', error.message);
    process.exit(1);
  }
}

main();

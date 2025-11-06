#!/usr/bin/env node

/**
 * 自動修正スクリプト
 * 1200問のテンプレートエラーを修正
 */

import fs from 'fs';

class ProblemAutoFixer {
  constructor() {
    this.fixStats = {
      duplicateWords: 0,
      grammarErrors: 0,
      placeholders: 0,
      total: 0
    };
  }

  /**
   * 単語重複を修正
   * "営業許可営業許可" → "営業許可"
   */
  fixDuplicateWords(text) {
    let fixed = text;
    let count = 0;

    // パターン: 同じ単語が連続している
    // 例: 営業許可営業許可 → 営業許可
    const duplicatePattern = /([ぁ-ん一-龥ー]+)\1+/g;
    fixed = fixed.replace(duplicatePattern, (match, word) => {
      count++;
      return word;
    });

    if (count > 0) {
      this.fixStats.duplicateWords++;
    }

    return fixed;
  }

  /**
   * 文法エラーを修正
   * "のについて" → "について"
   * "のは～が" → "は"
   * "のの" → "の"
   */
  fixGrammarErrors(text) {
    let fixed = text;
    let count = 0;

    const fixes = [
      { pattern: /のについて/g, replacement: 'について', desc: 'のについて' },
      { pattern: /のは～/g, replacement: 'は', desc: 'のは～' },
      { pattern: /のの/g, replacement: 'の', desc: 'のの' },
      { pattern: /ののの/g, replacement: 'の', desc: 'ののの' },
    ];

    for (const fix of fixes) {
      const matches = text.match(fix.pattern);
      if (matches) {
        count += matches.length;
        fixed = fixed.replace(fix.pattern, fix.replacement);
      }
    }

    if (count > 0) {
      this.fixStats.grammarErrors++;
    }

    return fixed;
  }

  /**
   * プレースホルダーを削除
   * "～" "…" などを削除
   */
  fixPlaceholders(text) {
    let fixed = text;
    let count = 0;

    const placeholderPatterns = [
      { pattern: /～/g, desc: '～' },
      { pattern: /…/g, desc: '…' },
      { pattern: /【.+?】/g, desc: '【】' },
    ];

    for (const p of placeholderPatterns) {
      const matches = fixed.match(p.pattern);
      if (matches) {
        count += matches.length;
        fixed = fixed.replace(p.pattern, '');
      }
    }

    if (count > 0) {
      this.fixStats.placeholders++;
    }

    return fixed;
  }

  /**
   * 問題文全体を修正
   */
  fixStatement(statement) {
    let fixed = statement;

    // 1. 単語重複を修正
    fixed = this.fixDuplicateWords(fixed);

    // 2. 文法エラーを修正
    fixed = this.fixGrammarErrors(fixed);

    // 3. プレースホルダーを削除
    fixed = this.fixPlaceholders(fixed);

    // 4. 余分な空白を削除
    fixed = fixed.replace(/\s+/g, ' ').trim();

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

    // 解説も修正
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
    console.log('📊 修正統計');
    console.log('='.repeat(70));
    console.log(`✅ 処理済み問題: ${this.fixStats.total}`);
    console.log(`   - 単語重複修正: ${this.fixStats.duplicateWords}`);
    console.log(`   - 文法エラー修正: ${this.fixStats.grammarErrors}`);
    console.log(`   - プレースホルダー削除: ${this.fixStats.placeholders}`);
    console.log('='.repeat(70) + '\n');
  }
}

async function main() {
  try {
    const filePath = '/home/planj/patshinko-exam-app/public/mock_problems.json';
    console.log(`\n🔧 自動修正開始`);
    console.log(`ファイル: ${filePath}`);

    // ファイルを読み込み
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const originalProblems = data.problems || [];

    console.log(`処理対象: ${originalProblems.length}問\n`);

    // 修正実行
    const fixer = new ProblemAutoFixer();
    const fixedProblems = fixer.fixAllProblems(originalProblems);

    // 統計表示
    fixer.printStats();

    // 修正結果の例を表示
    console.log('📝 修正結果の例（最初の3問）:\n');
    for (let i = 0; i < Math.min(3, fixedProblems.length); i++) {
      const orig = originalProblems[i];
      const fixed = fixedProblems[i];

      console.log(`問${i + 1}:`);
      console.log(`  ❌ 修正前: "${orig.statement}"`);
      console.log(`  ✅ 修正後: "${fixed.statement}"`);
      console.log();
    }

    // 修正されたデータを保存
    const fixedData = {
      ...data,
      problems: fixedProblems,
      lastFixed: new Date().toISOString(),
      fixedBy: 'auto-fix-problems.js'
    };

    fs.writeFileSync(filePath, JSON.stringify(fixedData, null, 2));
    console.log(`💾 修正済みファイルを保存しました`);
    console.log(`パス: ${filePath}\n`);

    // バックアップも作成
    const backupPath = `/home/planj/patshinko-exam-app/public/mock_problems.backup.${Date.now()}.json`;
    fs.writeFileSync(backupPath, JSON.stringify(data, null, 2));
    console.log(`🔒 バックアップを作成しました`);
    console.log(`パス: ${backupPath}\n`);

    console.log('✅ 自動修正完了\n');

  } catch (error) {
    console.error('❌ エラー:', error.message);
    process.exit(1);
  }
}

main();

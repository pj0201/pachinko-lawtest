/**
 * Opus校正システム - 634問の段階的修正
 * 進捗保存により中断・再開可能
 */

const fs = require('fs');
const path = require('path');

class OpusCorrectionSystem {
  constructor() {
    this.progressFile = './reports/opus_correction_progress.json';
    this.progress = this.loadProgress();

    // 修正タイプの定義
    this.correctionTypes = {
      JAPANESE_ERROR: '誤った日本語表現',
      MISMATCH: '問題文と解説の不一致',
      LEGAL_REF: '法的根拠の具体化',
      ABSTRACT: '抽象的表現の具体化'
    };

    // 誤った日本語表現パターン
    this.errorPatterns = {
      '当該通りです': '正しいです',
      '当該通り': 'その通り',
      'これは風営法': '風営法',
      'これは誤り': '誤り',
      'これは正しい': '正しい',
      'その条項': '該当条項',
      'その基準': '該当基準'
    };

    // 抽象的表現のマッピング
    this.abstractToConcreteMap = {
      '一定の間隔': '都道府県条例で定める間隔',
      '適切な手続き': '風営法に定める手続き',
      '所定の期間': '60日以内',
      '適正な管理': '風営法施行規則に基づく管理',
      '相当の': '法令で定める',
      '必要な手続き': '法令に定める手続き'
    };
  }

  // 進捗のロード
  loadProgress() {
    if (fs.existsSync(this.progressFile)) {
      return JSON.parse(fs.readFileSync(this.progressFile, 'utf8'));
    }
    return {
      status: 'initialized',
      lastProcessedId: 0,
      totalProblems: 634,
      corrections: {
        japanese_errors: 0,
        mismatches: 0,
        legal_refs: 0,
        abstract_terms: 0
      },
      timestamp: new Date().toISOString()
    };
  }

  // 進捗の保存
  saveProgress() {
    fs.writeFileSync(this.progressFile, JSON.stringify(this.progress, null, 2));
  }

  // Step 1: 誤った日本語表現の修正
  fixJapaneseErrors(problems) {
    console.log('='.repeat(60));
    console.log('Step 1: 誤った日本語表現の修正');
    console.log('='.repeat(60));

    let fixedCount = 0;
    const fixedProblems = problems.map(problem => {
      let fixed = { ...problem };
      let hasChanges = false;

      // 問題文の修正
      Object.entries(this.errorPatterns).forEach(([error, correct]) => {
        if (fixed.problem_text && fixed.problem_text.includes(error)) {
          fixed.problem_text = fixed.problem_text.replace(new RegExp(error, 'g'), correct);
          hasChanges = true;
        }
      });

      // 解説の修正
      Object.entries(this.errorPatterns).forEach(([error, correct]) => {
        if (fixed.explanation && fixed.explanation.includes(error)) {
          fixed.explanation = fixed.explanation.replace(new RegExp(error, 'g'), correct);
          hasChanges = true;
        }
      });

      if (hasChanges) {
        fixedCount++;
      }

      return fixed;
    });

    console.log(`✅ ${fixedCount}問の日本語表現を修正`);
    this.progress.corrections.japanese_errors = fixedCount;
    return fixedProblems;
  }

  // Step 2: 問題文と解説の不一致を検出・修正
  fixMismatches(problems) {
    console.log('');
    console.log('='.repeat(60));
    console.log('Step 2: 問題文と解説の不一致の修正');
    console.log('='.repeat(60));

    let fixedCount = 0;
    const fixedProblems = problems.map(problem => {
      let fixed = { ...problem };

      // パターン1: 問題文が肯定文なのに解説が「誤り」で始まる
      if (fixed.problem_text && fixed.explanation) {
        const problemIsAffirmative = !fixed.problem_text.includes('ない') &&
                                     !fixed.problem_text.includes('不要') &&
                                     !fixed.problem_text.includes('禁止');

        const explanationStartsWithError = fixed.explanation.startsWith('誤り') ||
                                          fixed.explanation.startsWith('間違い');

        if (problemIsAffirmative && explanationStartsWithError) {
          // 問題文の内容を確認して適切な解説に修正
          if (fixed.problem_text.includes('必要')) {
            fixed.explanation = fixed.explanation.replace(/^誤り[です]*。?/, '正しいです。');
            fixedCount++;
          }
        }

        // パターン2: 解説が問題文をそのまま繰り返している
        const explanationRepeats = fixed.explanation.includes(fixed.problem_text.slice(0, 20));
        if (explanationRepeats && fixed.explanation.length < fixed.problem_text.length + 20) {
          // より詳細な解説を追加
          fixed.explanation = `正しいです。${fixed.explanation} ${fixed.legal_reference ? fixed.legal_reference + 'に基づきます。' : ''}`;
          fixedCount++;
        }
      }

      return fixed;
    });

    console.log(`✅ ${fixedCount}問の不一致を修正`);
    this.progress.corrections.mismatches = fixedCount;
    return fixedProblems;
  }

  // Step 3: 法的根拠の具体化（部分的実装）
  improveLegalReferences(problems) {
    console.log('');
    console.log('='.repeat(60));
    console.log('Step 3: 法的根拠の具体化');
    console.log('='.repeat(60));

    let improvedCount = 0;
    const improvedProblems = problems.map(problem => {
      let fixed = { ...problem };

      if (fixed.legal_reference) {
        // 基本的な法的根拠の具体化
        const legalRefMap = {
          '施行規則': '風営法施行規則',
          '技術規格': '遊技機の認定及び型式の検定等に関する規則',
          '民法': '民法（契約に関する規定）',
          '中古機流通要綱': '中古遊技機流通制度要綱',
          'リサイクル法': '遊技機リサイクル法'
        };

        Object.entries(legalRefMap).forEach(([short, full]) => {
          if (fixed.legal_reference === short) {
            fixed.legal_reference = full;
            improvedCount++;
          }
        });
      } else {
        // 法的根拠がない場合、カテゴリから推測
        if (problem.category === '遊技機管理') {
          fixed.legal_reference = '風営法及び関連規則';
          improvedCount++;
        } else if (problem.category === '営業許可・申請手続き') {
          fixed.legal_reference = '風営法第3条～第9条';
          improvedCount++;
        }
      }

      return fixed;
    });

    console.log(`✅ ${improvedCount}問の法的根拠を改善`);
    this.progress.corrections.legal_refs = improvedCount;
    return improvedProblems;
  }

  // Step 4: 抽象的表現の具体化
  fixAbstractExpressions(problems) {
    console.log('');
    console.log('='.repeat(60));
    console.log('Step 4: 抽象的表現の具体化');
    console.log('='.repeat(60));

    let fixedCount = 0;
    const fixedProblems = problems.map(problem => {
      let fixed = { ...problem };
      let hasChanges = false;

      // 問題文の抽象的表現を具体化
      Object.entries(this.abstractToConcreteMap).forEach(([abstract, concrete]) => {
        if (fixed.problem_text && fixed.problem_text.includes(abstract)) {
          fixed.problem_text = fixed.problem_text.replace(new RegExp(abstract, 'g'), concrete);
          hasChanges = true;
        }
      });

      // 解説の抽象的表現を具体化
      Object.entries(this.abstractToConcreteMap).forEach(([abstract, concrete]) => {
        if (fixed.explanation && fixed.explanation.includes(abstract)) {
          fixed.explanation = fixed.explanation.replace(new RegExp(abstract, 'g'), concrete);
          hasChanges = true;
        }
      });

      if (hasChanges) {
        fixedCount++;
      }

      return fixed;
    });

    console.log(`✅ ${fixedCount}問の抽象的表現を具体化`);
    this.progress.corrections.abstract_terms = fixedCount;
    return fixedProblems;
  }

  // メイン処理（バッチ処理対応）
  processCorrections(inputFile, outputFile, batchSize = 50) {
    console.log('='.repeat(60));
    console.log('Opus校正システム - バッチ処理開始');
    console.log('='.repeat(60));
    console.log(`バッチサイズ: ${batchSize}問ずつ処理`);
    console.log('');

    const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
    const problems = data.problems;

    // 前回の続きから処理
    const startIndex = this.progress.lastProcessedId;
    const endIndex = Math.min(startIndex + batchSize, problems.length);

    console.log(`処理範囲: 問題ID ${startIndex + 1} - ${endIndex}`);
    console.log('');

    // バッチ処理
    const batch = problems.slice(startIndex, endIndex);

    // 各ステップを順次実行
    let correctedBatch = this.fixJapaneseErrors(batch);
    correctedBatch = this.fixMismatches(correctedBatch);
    correctedBatch = this.improveLegalReferences(correctedBatch);
    correctedBatch = this.fixAbstractExpressions(correctedBatch);

    // 結果をマージ
    const correctedProblems = [
      ...problems.slice(0, startIndex),
      ...correctedBatch,
      ...problems.slice(endIndex)
    ];

    // 進捗を更新
    this.progress.lastProcessedId = endIndex;
    this.progress.status = endIndex >= problems.length ? 'completed' : 'in_progress';
    this.progress.timestamp = new Date().toISOString();
    this.saveProgress();

    // データを保存
    const outputData = {
      ...data,
      metadata: {
        ...data.metadata,
        opus_correction_date: new Date().toISOString(),
        opus_correction_progress: this.progress
      },
      problems: correctedProblems
    };

    fs.writeFileSync(outputFile, JSON.stringify(outputData, null, 2));

    console.log('');
    console.log('='.repeat(60));
    console.log('バッチ処理完了');
    console.log('='.repeat(60));
    console.log(`進捗: ${endIndex}/${problems.length}問 (${Math.round(endIndex / problems.length * 100)}%)`);

    if (this.progress.status === 'completed') {
      console.log('🎉 全問題の校正が完了しました！');
    } else {
      console.log(`次回は問題ID ${endIndex + 1} から再開します`);
    }

    return {
      processed: endIndex - startIndex,
      total: problems.length,
      progress: this.progress,
      isComplete: this.progress.status === 'completed'
    };
  }

  // 進捗状況の確認
  checkProgress() {
    console.log('='.repeat(60));
    console.log('現在の進捗状況');
    console.log('='.repeat(60));
    console.log(`状態: ${this.progress.status}`);
    console.log(`処理済み: ${this.progress.lastProcessedId}/${this.progress.totalProblems}問`);
    console.log(`進捗率: ${Math.round(this.progress.lastProcessedId / this.progress.totalProblems * 100)}%`);
    console.log('');
    console.log('修正実績:');
    console.log(`  - 日本語エラー: ${this.progress.corrections.japanese_errors}件`);
    console.log(`  - 不一致修正: ${this.progress.corrections.mismatches}件`);
    console.log(`  - 法的根拠改善: ${this.progress.corrections.legal_refs}件`);
    console.log(`  - 抽象表現具体化: ${this.progress.corrections.abstract_terms}件`);
    console.log(`最終更新: ${this.progress.timestamp}`);
    return this.progress;
  }

  // 進捗リセット
  resetProgress() {
    this.progress = {
      status: 'initialized',
      lastProcessedId: 0,
      totalProblems: 634,
      corrections: {
        japanese_errors: 0,
        mismatches: 0,
        legal_refs: 0,
        abstract_terms: 0
      },
      timestamp: new Date().toISOString()
    };
    this.saveProgress();
    console.log('✅ 進捗をリセットしました');
  }
}

// CLIから実行
if (require.main === module) {
  const system = new OpusCorrectionSystem();

  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'check') {
    // 進捗確認
    system.checkProgress();
  } else if (command === 'reset') {
    // 進捗リセット
    system.resetProgress();
  } else if (command === 'process') {
    // バッチ処理実行
    const batchSize = parseInt(args[1]) || 50;
    const inputFile = './data/opus_634_manually_fixed_20251023.json';
    const outputFile = './data/opus_634_corrected_batch.json';

    const result = system.processCorrections(inputFile, outputFile, batchSize);

    if (!result.isComplete) {
      console.log('');
      console.log('📌 処理を続けるには、再度以下のコマンドを実行してください:');
      console.log(`   node backend/opus-correction-system.cjs process ${batchSize}`);
    }
  } else {
    console.log('使用方法:');
    console.log('  node backend/opus-correction-system.cjs check      - 進捗確認');
    console.log('  node backend/opus-correction-system.cjs reset      - 進捗リセット');
    console.log('  node backend/opus-correction-system.cjs process [バッチサイズ] - 校正実行');
  }
}

module.exports = OpusCorrectionSystem;
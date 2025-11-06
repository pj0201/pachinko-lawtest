/**
 * 新規生成35問と既存599問の重複チェック
 */

const fs = require('fs');
const ProblemDuplicateDetector = require('./problem-duplicate-detector.cjs');

async function main() {
  console.log('='.repeat(60));
  console.log('補充問題の重複チェック');
  console.log('='.repeat(60));

  // データ読み込み
  const combined = JSON.parse(fs.readFileSync('./data/combined_634_for_check.json', 'utf8'));
  const problems = combined.problems;

  console.log(`\n総問題数: ${problems.length}問`);
  console.log('  - 既存: 599問');
  console.log('  - 新規: 35問\n');

  // 重複検出実行
  const detector = new ProblemDuplicateDetector();
  const duplicates = await detector.detectAllDuplicates(problems);

  console.log(`\n重複検出結果: ${duplicates.length}件\n`);

  if (duplicates.length === 0) {
    console.log('✅ 重複なし - 新規35問は既存問題と重複していません');

    // 統合データを保存
    const finalData = {
      metadata: {
        merge_date: new Date().toISOString(),
        original_count: 599,
        supplemental_count: 35,
        final_count: 634,
        quality_improvements: {
          cancellation_violation_theme: '10問 → 20問 (100%増)',
          facility_structure_theme: '14問 → 24問 (71%増)',
          business_license_theme: '39問 → 54問 (38%増)'
        }
      },
      problems: problems
    };

    fs.writeFileSync('./data/opus_634_final_20251023.json', JSON.stringify(finalData, null, 2));
    console.log('\n✅ 最終データ保存: data/opus_634_final_20251023.json');
    console.log('   総問題数: 634問');
  } else {
    console.log('⚠️ 重複が見つかりました:');

    // 重複の詳細を表示（最大10件）
    duplicates.slice(0, 10).forEach((dup, i) => {
      const p1 = problems.find(p => p.problem_id === dup.problem1);
      const p2 = problems.find(p => p.problem_id === dup.problem2);

      console.log(`\n【重複${i+1}】`);
      console.log(`  問題ID: ${dup.problem1} ⇔ ${dup.problem2}`);
      console.log(`  類似度: ${(dup.similarity_score * 100).toFixed(1)}%`);
      console.log(`  検出方法: ${dup.detection_method}`);
      if (p1) console.log(`  問題1: ${p1.problem_text.substring(0, 50)}...`);
      if (p2) console.log(`  問題2: ${p2.problem_text.substring(0, 50)}...`);
    });

    if (duplicates.length > 10) {
      console.log(`\n... 他${duplicates.length - 10}件の重複`);
    }

    // レポート保存
    const report = detector.generateReport(duplicates, problems);
    fs.writeFileSync('./reports/supplemental_duplicate_check.json', JSON.stringify(report, null, 2));
    console.log('\n重複レポート保存: reports/supplemental_duplicate_check.json');
  }

  console.log('\n' + '='.repeat(60));
  console.log('チェック完了');
  console.log('='.repeat(60));
}

main().catch(error => {
  console.error('エラー:', error);
  process.exit(1);
});

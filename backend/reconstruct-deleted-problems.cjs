/**
 * 削除された問題を再構築してテーマ分析
 */

const fs = require('fs');

// データ読み込み
const originalData = JSON.parse(fs.readFileSync('./data/opus_900_original_backup.json', 'utf8'));
const dupReport = JSON.parse(fs.readFileSync('./reports/duplicate_report_1761199898753.json', 'utf8'));

const originalProblems = originalData.problems || originalData;

// 重複レポートから削除されたproblem_idを特定
function hasLegalReference(problem) {
  const legalRefPattern = /第\d+条第?\d*項?/;
  return legalRefPattern.test(problem.explanation || '') ||
         legalRefPattern.test(problem.legal_reference || '');
}

const toRemove = new Set();
const problemMap = new Map();
originalProblems.forEach(p => problemMap.set(p.problem_id, p));

dupReport.details.forEach(dup => {
  const problem1 = problemMap.get(dup.pair[0]);
  const problem2 = problemMap.get(dup.pair[1]);

  if (!problem1 || !problem2) return;

  let removeProblemId;

  // removeDuplicates と同じロジック
  if (hasLegalReference(problem1) && !hasLegalReference(problem2)) {
    removeProblemId = problem2.problem_id;
  } else if (!hasLegalReference(problem1) && hasLegalReference(problem2)) {
    removeProblemId = problem1.problem_id;
  } else if (problem1.problem_text.length > problem2.problem_text.length) {
    removeProblemId = problem2.problem_id;
  } else {
    removeProblemId = problem2.problem_id;
  }

  toRemove.add(removeProblemId);
});

console.log('削除された問題ID数:', toRemove.size);
console.log('');

// 削除された問題を抽出
const deletedProblems = originalProblems.filter(p => toRemove.has(p.problem_id));
const remainingProblems = originalProblems.filter(p => !toRemove.has(p.problem_id));

console.log('削除された問題数:', deletedProblems.length);
console.log('残った問題数:', remainingProblems.length);
console.log('');

// キーワード抽出関数
function extractKeywords(problem) {
  const text = `${problem.problem_text} ${problem.explanation}`;
  const keywords = new Set();

  // 法令名
  const laws = ['風営法', '風営法施行令', '風営法施行規則', '遊技機規則', '民法', '商法', '刑法'];
  laws.forEach(law => {
    if (text.includes(law)) keywords.add(law);
  });

  // 重要キーワード（テーマ）
  const patterns = [
    '主任者', '取扱責任者', '営業所', '遊技機', 'パチンコ', 'スロット',
    '認定', '検定', '型式', '製造番号', '移設', '撤去', '設置',
    '営業時間', '営業許可', '申請', '届出', '変更', '更新',
    '景品', '等価交換', '三店方式', '買取', '換金',
    '不正', '改造', '不正改造', 'ゴト', '不正行為',
    '未成年', '青少年', '保護', '入場制限',
    '罰則', '罰金', '営業停止', '取消', '違反',
    '公安委員会', '警察署', '届出先', '許可権者',
    '帳簿', '記録', '保存', '義務',
    '換気', '照明', '騒音', '設備', '基準',
    '中古機', '流通', '流通制御端末',
    '出玉', '性能', '射幸性', '規制',
    '賞品', '提供', '禁止', '制限',
    '構造', '機能', '仕様', '技術基準',
    '立入検査', '調査', '報告',
    '遊技料金', '料金', '貸玉', '貸メダル',
    '表示', '掲示', '標識',
    '従業員', '教育', '研修',
    '承継', '譲渡', '相続',
    '条例', '都道府県', '地域',
    '国家公安委員会', '指定試験機関',
    '適合', '基準適合', '性能基準',
    '自主検査', '検査義務',
    '釘', '調整', '釘曲げ',
    '保証金', '供託',
    '管理者', '統括責任者',
    '名義貸し', '名義使用',
    '風俗案内所', '接待',
    '苦情', '処理', '対応',
    '防犯', 'セキュリティ',
    '賭博', '賭博罪',
    '手数料', '申請手数料'
  ];

  patterns.forEach(pattern => {
    if (text.includes(pattern)) keywords.add(pattern);
  });

  return keywords;
}

// 残った問題のキーワード集計
const remainingKeywords = new Map();
remainingProblems.forEach(p => {
  extractKeywords(p).forEach(k => {
    remainingKeywords.set(k, (remainingKeywords.get(k) || 0) + 1);
  });
});

// 削除された問題のキーワード集計
const deletedKeywords = new Map();
deletedProblems.forEach(p => {
  extractKeywords(p).forEach(k => {
    deletedKeywords.set(k, (deletedKeywords.get(k) || 0) + 1);
  });
});

// 削除された問題にのみ存在するキーワード
const uniqueToDeleted = [];
deletedKeywords.forEach((count, keyword) => {
  if (!remainingKeywords.has(keyword)) {
    uniqueToDeleted.push({ keyword, count });
  }
});

console.log('■ 削除された問題にのみ存在するテーマ・キーワード:');
if (uniqueToDeleted.length === 0) {
  console.log('  → なし（全てのテーマが残った問題にも存在）');
} else {
  uniqueToDeleted
    .sort((a, b) => b.count - a.count)
    .forEach(({keyword, count}) => {
      console.log(`  - ${keyword}: ${count}問`);
    });
}

// 大幅に減少したテーマを検出
console.log('');
console.log('■ 大幅に減少したテーマ（50%以上減少、かつ元5問以上）:');
const significantlyReduced = [];
deletedKeywords.forEach((deletedCount, keyword) => {
  const remainingCount = remainingKeywords.get(keyword) || 0;
  const totalCount = deletedCount + remainingCount;
  const reductionRate = (deletedCount / totalCount) * 100;

  if (reductionRate >= 50 && totalCount >= 5) {
    significantlyReduced.push({
      keyword,
      total: totalCount,
      deleted: deletedCount,
      remaining: remainingCount,
      reduction_rate: reductionRate.toFixed(1)
    });
  }
});

if (significantlyReduced.length === 0) {
  console.log('  → なし');
} else {
  significantlyReduced
    .sort((a, b) => b.reduction_rate - a.reduction_rate)
    .forEach(item => {
      console.log(`  - ${item.keyword}: ${item.total}問中${item.deleted}問削除 (${item.reduction_rate}%削減、残り${item.remaining}問)`);
    });
}

// カテゴリ別分析
console.log('');
console.log('■ 削除された問題のカテゴリ分布:');
const deletedCategories = {};
deletedProblems.forEach(p => {
  const cat = p.category || '未分類';
  deletedCategories[cat] = (deletedCategories[cat] || 0) + 1;
});

Object.entries(deletedCategories)
  .sort((a, b) => b[1] - a[1])
  .forEach(([cat, count]) => {
    console.log(`  ${cat}: ${count}問`);
  });

// カテゴリ別削減率
console.log('');
console.log('■ カテゴリ別削減率:');
const remainingCategories = {};
remainingProblems.forEach(p => {
  const cat = p.category || '未分類';
  remainingCategories[cat] = (remainingCategories[cat] || 0) + 1;
});

const allCategories = new Set([
  ...Object.keys(deletedCategories),
  ...Object.keys(remainingCategories)
]);

const categoryAnalysis = [];
allCategories.forEach(cat => {
  const deleted = deletedCategories[cat] || 0;
  const remaining = remainingCategories[cat] || 0;
  const total = deleted + remaining;
  const reductionRate = (deleted / total) * 100;

  categoryAnalysis.push({
    category: cat,
    total,
    deleted,
    remaining,
    reduction_rate: reductionRate.toFixed(1)
  });
});

categoryAnalysis
  .sort((a, b) => b.reduction_rate - a.reduction_rate)
  .forEach(item => {
    console.log(`  ${item.category}: ${item.total}問 → ${item.remaining}問 (${item.reduction_rate}%削減)`);
  });

// 詳細分析保存
const analysis = {
  summary: {
    total_original: originalProblems.length,
    total_deleted: deletedProblems.length,
    total_remaining: remainingProblems.length,
    deletion_rate: ((deletedProblems.length / originalProblems.length) * 100).toFixed(1) + '%'
  },
  unique_keywords_in_deleted: uniqueToDeleted,
  significantly_reduced_themes: significantlyReduced,
  category_analysis: categoryAnalysis,
  deleted_problems_sample: deletedProblems.slice(0, 50).map(p => ({
    problem_id: p.problem_id,
    category: p.category,
    problem_text: p.problem_text,
    explanation: p.explanation,
    keywords: [...extractKeywords(p)]
  }))
};

fs.writeFileSync('./reports/deleted_problems_theme_analysis.json', JSON.stringify(analysis, null, 2));

console.log('');
console.log('📊 詳細分析を保存: reports/deleted_problems_theme_analysis.json');

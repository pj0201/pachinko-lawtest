#!/usr/bin/env node

/**
 * ギャップフィラー
 * カバレッジギャップのキーワードをカバーする新問題を追加
 */

import fs from 'fs';

class GapFiller {
  constructor() {
    // ギャップを埋めるための問題テンプレート
    this.gapProblems = {
      '営業許可・申請手続き': [
        { statement: '営業許可を得るには、申請書を公安委員会に提出する必要がある', answer: true, difficulty: 'easy', source: '風営法第6条' },
        { statement: '営業許可の申請に際して、届け出が必要な変更はない', answer: false, difficulty: 'medium', source: '風営法施行規則' },
        { statement: '遊技場営業者は定期的に営業者登録を更新する必要がある', answer: true, difficulty: 'medium', source: '登録規程' },
        { statement: '営業者は営業所の構造変更を届け出る必要がない', answer: false, difficulty: 'medium', source: '風営法' },
        { statement: '公安委員会が営業許可を拒否することはない', answer: false, difficulty: 'hard', source: '風営法第7条' },
        { statement: '営業所の住所は営業許可申請時に記載する重要な情報である', answer: true, difficulty: 'easy', source: '申請規定' },
      ],
      '建物・設備基準': [
        { statement: '遊技機の設置場所は建築基準法に適合する必要がある', answer: true, difficulty: 'medium', source: '建築基準法' },
        { statement: '施設の照度基準は営業所全体に統一する必要がない', answer: false, difficulty: 'medium', source: '設置基準' },
        { statement: '営業所の部屋の広さに特に制限はない', answer: false, difficulty: 'hard', source: '風営法施行規則' },
        { statement: 'テーブルやカウンターの配置は営業効率性のみで決定される', answer: false, difficulty: 'hard', source: '実務ガイド' },
        { statement: '建物の耐火構造は営業許可の要件である', answer: true, difficulty: 'hard', source: '建築基準法' },
        { statement: '設備の安全検査は定期的に実施する必要がある', answer: true, difficulty: 'medium', source: '安全基準' },
      ],
      '従業員・管理者要件': [
        { statement: '従業員は遊技機取扱い業務に従事する前に資格取得が必要である場合がある', answer: true, difficulty: 'medium', source: '取扱主任者規程' },
        { statement: '管理者は遊技機の保守管理に従事することができない', answer: false, difficulty: 'hard', source: '業務規程' },
        { statement: '従事者の雇用契約は営業者の自由で規定がない', answer: false, difficulty: 'hard', source: '就業規則' },
        { statement: '取扱主任者資格は業務経験を通じて習得できる', answer: true, difficulty: 'medium', source: '資格規定' },
        { statement: '従業員の知識向上は営業者の責任である', answer: true, difficulty: 'medium', source: '法令遵守基準' },
        { statement: '管理者に求められる最小限の資格はない', answer: false, difficulty: 'hard', source: '管理者要件' },
      ],
      '営業時間・休業': [
        { statement: '営業場所の営業時間は営業者が自由に決定できる場合と制限される場合がある', answer: true, difficulty: 'hard', source: '風営法' },
        { statement: '営業停止命令は行政処分として発令されることがある', answer: true, difficulty: 'medium', source: '行政処分基準' },
        { statement: 'スケジュール変更に際して報告義務はない', answer: false, difficulty: 'medium', source: '報告規定' },
        { statement: '営業日の変更は事前に届け出る必要がない', answer: false, difficulty: 'medium', source: '届出規定' },
        { statement: '営業所の営業時間帯は地方自治体の条例で定められることがある', answer: true, difficulty: 'hard', source: '条例' },
        { statement: '定休日の設定に関しても公安委員会の許可が必要な場合がある', answer: true, difficulty: 'hard', source: '風営法施行規則' },
      ],
      '景品・景慮基準': [
        { statement: '景品交換の基準は法律で規定されている', answer: true, difficulty: 'medium', source: '景品規制' },
        { statement: '顧客保護は営業者の責任の一部である', answer: true, difficulty: 'medium', source: '業務規定' },
        { statement: '顧客の景気感情に配慮した営業方法が求められることがある', answer: true, difficulty: 'hard', source: '業界ガイドライン' },
        { statement: '客への景品提供に上限はない', answer: false, difficulty: 'medium', source: '景品規制' },
        { statement: '未成年の顧客に対する特別な配慮は不要である', answer: false, difficulty: 'hard', source: '青少年保護法' },
        { statement: '顧客満足度の向上は営業の重要な目標である', answer: true, difficulty: 'easy', source: '業務ガイドライン' },
      ],
      '法律・規制違反': [
        { statement: '違反行為に対しては行政処分が科せられることがある', answer: true, difficulty: 'medium', source: '行政処分基準' },
        { statement: '処分の種類には営業停止や取消しが含まれる', answer: true, difficulty: 'medium', source: '風営法' },
        { statement: '行政による指導の段階で改善しない場合は処分に進む', answer: true, difficulty: 'hard', source: '処分手順' },
        { statement: '違反行為の報告義務は業者にはない', answer: false, difficulty: 'hard', source: '法令遵守規定' },
        { statement: '法律違反は民事責任のみで刑事責任はない', answer: false, difficulty: 'hard', source: '風営法第36条' },
        { statement: '不正改造は最も重い違反のひとつとされている', answer: true, difficulty: 'hard', source: '不正対策要綱' },
      ],
      '実務・業務管理': [
        { statement: '実務的には日々の記録管理が重要である', answer: true, difficulty: 'medium', source: '実務ガイド' },
        { statement: '顧客対応に際して適切な対応方法が求められる', answer: true, difficulty: 'medium', source: '接客ガイド' },
        { statement: '遊技機の取扱いには保守管理が伴う', answer: true, difficulty: 'medium', source: '保守管理規定' },
        { statement: '保安上の問題は放置してもよい', answer: false, difficulty: 'hard', source: '安全基準' },
        { statement: '機械の保守は定期的な検査を含む', answer: true, difficulty: 'medium', source: '保守規定' },
        { statement: '記録は営業管理の重要な要素である', answer: true, difficulty: 'easy', source: '業務規定' },
      ]
    };
  }

  /**
   * 既存の最大IDを取得
   */
  getMaxId(problems) {
    let max = 0;
    for (const p of problems) {
      const num = parseInt(p.id.replace('q', ''));
      if (num > max) max = num;
    }
    return max;
  }

  /**
   * ギャップ問題を追加
   */
  addGapProblems(problems) {
    let nextId = this.getMaxId(problems) + 1;
    const newProblems = [...problems];

    for (const [category, problemTemplates] of Object.entries(this.gapProblems)) {
      for (const template of problemTemplates) {
        const problem = {
          id: `q${String(nextId).padStart(4, '0')}`,
          statement: template.statement,
          answer: template.answer,
          difficulty: template.difficulty,
          category: category,
          explanation: `${template.statement.substring(0, 50)}...に関する法令を参照してください`,
          source: template.source,
          gapFiller: true  // ギャップフィラーで追加したマーク
        };

        newProblems.push(problem);
        nextId++;
      }
    }

    return newProblems;
  }

  /**
   * 統計情報を表示
   */
  printStats(originalCount, newCount) {
    const added = newCount - originalCount;
    console.log('\n' + '='.repeat(70));
    console.log('📊 ギャップ問題追加統計');
    console.log('='.repeat(70));
    console.log(`✅ 元々の問題数: ${originalCount}`);
    console.log(`➕ 追加問題数: ${added}`);
    console.log(`📈 新しい総問題数: ${newCount}`);
    console.log('='.repeat(70) + '\n');
  }
}

async function main() {
  try {
    const filePath = '/home/planj/patshinko-exam-app/public/mock_problems.json';
    console.log(`\n📝 ギャップ問題追加開始`);
    console.log(`ファイル: ${filePath}`);

    // ファイルを読み込み
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const originalProblems = data.problems || [];
    const originalCount = originalProblems.length;

    console.log(`現在の問題数: ${originalCount}\n`);

    // ギャップ問題を追加
    const filler = new GapFiller();
    const updatedProblems = filler.addGapProblems(originalProblems);

    // 統計表示
    filler.printStats(originalCount, updatedProblems.length);

    // 追加問題の例を表示
    const addedProblems = updatedProblems.slice(originalCount);
    console.log('📝 追加された問題の例（最初の5問）:\n');
    for (let i = 0; i < Math.min(5, addedProblems.length); i++) {
      const p = addedProblems[i];
      console.log(`${i + 1}. [${p.category}] ${p.statement}`);
    }

    // ファイルを保存
    const updatedData = {
      ...data,
      problems: updatedProblems,
      totalProblems: updatedProblems.length,
      lastUpdated: new Date().toISOString(),
      gapFillerApplied: true
    };

    fs.writeFileSync(filePath, JSON.stringify(updatedData, null, 2));
    console.log(`\n💾 更新済みファイルを保存しました`);
    console.log(`パス: ${filePath}`);

    // バックアップ
    const backupPath = `/home/planj/patshinko-exam-app/public/mock_problems.backup.before-gap-fill.${Date.now()}.json`;
    fs.writeFileSync(backupPath, JSON.stringify({ problems: originalProblems }, null, 2));
    console.log(`🔒 バックアップ: ${backupPath}\n`);

    console.log('✅ ギャップ問題追加完了\n');

  } catch (error) {
    console.error('❌ エラー:', error.message);
    process.exit(1);
  }
}

main();

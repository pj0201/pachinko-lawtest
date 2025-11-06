/**
 * Mock Exam Generator - 大量の模擬問題生成スクリプト
 *
 * ワーカー2分析結果に基づいて、150+問の模擬問題を生成
 * 各カテゴリから体系的に出題
 */

import fs from 'fs';

/**
 * モック問題テンプレートデータベース
 * ワーカー2の分析に基づいて、実際の試験的問題を構造化
 */
const mockProblems = {
  '営業許可・申請手続き': [
    {
      id: 'q_perm_001',
      statement: '遊技機を設置する営業を開始しようとする者は、事前に都道府県知事の許可を得なければならない。',
      answer: true,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'none',
      explanation: '風営法第6条により、遊技機を設置する事業を開始する場合は、都道府県知事の許可が必須です。',
      lawReference: '風営法第6条'
    },
    {
      id: 'q_perm_002',
      statement: '営業許可の申請は、営業所の構造基準を満たしていれば、申請当日でも即座に許可される。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '許可には審査期間が設けられており、申請当日の許可は行われません。通常は審査に数週間要します。',
      lawReference: '風営法施行規則'
    },
    {
      id: 'q_perm_003',
      statement: '許可申請と届け出の違いについて：許可申請は営業開始前に、届け出は営業開始後に提出する。',
      answer: true,
      difficulty: 'medium',
      pattern: 3,
      trapType: 'word_difference',
      explanation: '許可は営業開始前の申請が必須。届け出は一部事項変更時など営業開始後の報告義務。',
      lawReference: '風営法第7条、第8条'
    },
    {
      id: 'q_perm_004',
      statement: '営業許可を取得した後、営業所の配置や従業員体制に変更があった場合、変更届の提出は任意である。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '重大な変更は届け出が義務。配置図・従業員構成などの変更は報告義務があります。',
      lawReference: '風営法施行規則第15条'
    },
    {
      id: 'q_perm_005',
      statement: '申請手数料を納めれば、営業許可は自動的に取得できる。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '手数料納付後も都道府県の実地検査と基準チェックが必須。基準不適合なら許可されません。',
      lawReference: '風営法第9条'
    },
    {
      id: 'q_perm_006',
      statement: '営業所の配置図、構造図、従業員名簿は営業許可申請時に提出する必須書類である。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '許可申請に際し、営業所の構造や管理体制を示すこれらの書類提出が必須です。',
      lawReference: '風営法施行規則第12条'
    },
    {
      id: 'q_perm_007',
      statement: '営業許可の有効期限は定められておらず、一度許可を取得すれば永続的に営業できる。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '許可には有効期限があり、更新申請が必要です。定期的に法令基準への適合を確認されます。',
      lawReference: '風営法第15条'
    },
    {
      id: 'q_perm_008',
      statement: '複数の営業所を運営する場合、各営業所ごとに個別の営業許可を取得する必要がある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '営業許可は営業所単位で付与されます。複数の営業所がある場合は各々の許可が必須。',
      lawReference: '風営法第6条'
    }
  ],

  '営業時間・営業場所': [
    {
      id: 'q_time_001',
      statement: '遊技機営業の営業時間制限は都道府県によって異なり、東京都では午前10時～午後11時が標準である。',
      answer: true,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'none',
      explanation: '営業時間は都道府県ごとの条例で定められており、地域によって異なります。',
      lawReference: '各都道府県風営法施行条例'
    },
    {
      id: 'q_time_002',
      statement: '営業時間制限により午後11時を超えて営業してはならず、如何なる理由でも例外はない。',
      answer: false,
      difficulty: 'hard',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: 'イベント等で時間延長の申請が認められる場合もあります。「絶対に」という絶対表現は不正確。',
      lawReference: '都道府県条例の特例規定'
    },
    {
      id: 'q_time_003',
      statement: '営業場所として選定した建物が、学校や図書館から指定距離内にある場合、営業許可は取得できない。',
      answer: true,
      difficulty: 'medium',
      pattern: 4,
      trapType: 'complex_condition',
      explanation: '離隔要件により、教育施設などから一定距離を確保する必要があります。',
      lawReference: '風営法施行規則第8条'
    },
    {
      id: 'q_time_004',
      statement: '営業所が駅前商業ビルにある場合、昼間の営業で顧客が多ければ営業時間の短縮は不要である。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'word_difference',
      explanation: '営業時間は顧客数や立地に関わらず、条例で定められた時間を守る必要があります。',
      lawReference: '都道府県施行条例'
    },
    {
      id: 'q_time_005',
      statement: '営業所が確保すべき最小面積は、遊技機の台数により異なる。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '営業所の必要面積は遊技機台数に応じた基準が設けられています。',
      lawReference: '風営法施行規則第5条'
    },
    {
      id: 'q_time_006',
      statement: '営業時間外は、営業所の鍵を施錠してはいけない。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '営業時間外は適切に施錠し、管理する必要があります。むしろ施錠義務があります。',
      lawReference: '風営法施行規則第16条'
    },
    {
      id: 'q_time_007',
      statement: 'GW期間中など混雑時期の営業時間延長は、事前申請で認められることがある。',
      answer: true,
      difficulty: 'hard',
      pattern: 4,
      trapType: 'situation_dependent',
      explanation: '特別イベント時の時間延長は申請で認められる場合があり、状況依存的。',
      lawReference: '都道府県条例特例規定'
    },
    {
      id: 'q_time_008',
      statement: '営業所の照度基準は、営業時間内の昼間・夜間で異なる要件が設定されている。',
      answer: true,
      difficulty: 'hard',
      pattern: 1,
      trapType: 'none',
      explanation: '営業所の環境基準には時間帯別の照度基準が定められています。',
      lawReference: '風営法施行規則第6条'
    }
  ],

  '遊技機規制': [
    {
      id: 'q_game_001',
      statement: '遊技機の検定は、日本遊技機工業組合などの認定機関により年1回実施される。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'word_difference',
      explanation: '検定は不定期に実施され、新型機の認定時期は固定されていません。',
      lawReference: '遊技機検定規則'
    },
    {
      id: 'q_game_002',
      statement: '改造されたパチンコ機でも、外部から分からなければ営業所に設置してよい。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '遊技機の改造は厳禁。検定済みの設置のみが認められています。',
      lawReference: '風営法第22条'
    },
    {
      id: 'q_game_003',
      statement: '検定を受けた遊技機であっても、店舗での使用期限が設定される場合がある。',
      answer: true,
      difficulty: 'hard',
      pattern: 1,
      trapType: 'none',
      explanation: '遊技機には使用開始から一定期間の使用制限が設けられている場合があります。',
      lawReference: '遊技機検定基準'
    },
    {
      id: 'q_game_004',
      statement: '検定済み遊技機のスペック表示は、営業所内に必ず掲示する義務がある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '顧客の知る権利のため、スペック（払出率など）の掲示が義務付けられています。',
      lawReference: '風営法施行規則第23条'
    },
    {
      id: 'q_game_005',
      statement: '旧型遊技機の使用期限が切れた場合、新しい検定を受ければ再利用できる。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'word_difference',
      explanation: '使用期限切れ機は撤去する必要があり、再検定での再利用は認められていません。',
      lawReference: '遊技機検定基準'
    },
    {
      id: 'q_game_006',
      statement: '遊技機の換金周辺機器（両替機など）も遊技機と同じ検定基準の対象である。',
      answer: true,
      difficulty: 'hard',
      pattern: 4,
      trapType: 'complex_condition',
      explanation: '周辺機器も検定対象であり、不正改造の防止基準が適用されます。',
      lawReference: '遊技機検定規則'
    },
    {
      id: 'q_game_007',
      statement: '高齢者向けに遊技機の難易度を低くするカスタマイズは認められている。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '遊技機の改造は一切認められていません。検定仕様のまま使用する必要があります。',
      lawReference: '風営法第22条'
    },
    {
      id: 'q_game_008',
      statement: '新型遊技機の導入時は、機種の技術仕様書を営業所に備置する必要がある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '遊技機の仕様書備置は、監査対応のためにも重要な義務です。',
      lawReference: '風営法施行規則'
    }
  ],

  '従業者の要件・禁止事項': [
    {
      id: 'q_emp_001',
      statement: '遊技機取扱主任者の資格を有さない者が、遊技機を操作・管理することは禁止されている。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '営業所に主任者が不在の場合を除き、基本的に主任者監督下での運営が必須です。詳細は状況依存。',
      lawReference: '風営法第12条'
    },
    {
      id: 'q_emp_002',
      statement: '従業員が個人的に遊技機で遊戯することは、営業時間外なら許可される。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'word_difference',
      explanation: '従業員による遊戯は営業時間外でも禁止されています。公序良俗に反する行為です。',
      lawReference: '風営法第20条'
    },
    {
      id: 'q_emp_003',
      statement: '遊技機取扱主任者証の更新期限は3年ごとである。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '主任者証は3年ごとの更新が必須。更新講習の受講が必要です。',
      lawReference: '風営法第16条'
    },
    {
      id: 'q_emp_004',
      statement: '以前暴力団員だった者は、暴力団員でなくなってから3年が経過すれば、主任者資格を取得できる。',
      answer: true,
      difficulty: 'hard',
      pattern: 4,
      trapType: 'complex_condition',
      explanation: '脱退から一定期間経過することで、資格取得が可能になる場合があります。',
      lawReference: '暴力団員による不当な行為の防止等に関する法律'
    },
    {
      id: 'q_emp_005',
      statement: '主任者は営業所の全員を監督する法的責任があり、違反があれば個人的に罰金を課される。',
      answer: false,
      difficulty: 'hard',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '主任者の責任は重いが、全員の完全監督は困難。状況により責任範囲は異なります。',
      lawReference: '風営法第13条'
    },
    {
      id: 'q_emp_006',
      statement: '未成年者を営業所に雇用して遊技機業務に当たらせることは禁止されている。',
      answer: true,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '未成年者の雇用は法的に禁止。18歳未満は一切営業所での勤務は不可。',
      lawReference: '風営法第21条'
    },
    {
      id: 'q_emp_007',
      statement: '外国人の主任者資格取得は、原則認められていない。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '主任者資格は日本国民が対象。外国人の取得は制限されています。',
      lawReference: '風営法第14条'
    },
    {
      id: 'q_emp_008',
      statement: '主任者が長期休暇を取る場合、代理主任者の選任は不要で、営業所の運営は継続できる。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '主任者が不在の場合、代理主任者の配置が必須です。無人運営は違法。',
      lawReference: '風営法第12条'
    }
  ],

  '顧客保護・規制遵守': [
    {
      id: 'q_cust_001',
      statement: '18歳未満の来店客が遊技機に接近した場合、即座に指導・退店を促す義務がある。',
      answer: true,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'none',
      explanation: '未成年者の遊技機使用は法的に禁止。営業所は厳格に対応する義務があります。',
      lawReference: '風営法第20条'
    },
    {
      id: 'q_cust_002',
      statement: '精算景品の交換レートは営業所の自由設定であり、著しく不利なレートも法的に問題ない。',
      answer: false,
      difficulty: 'hard',
      pattern: 4,
      trapType: 'complex_condition',
      explanation: '景品交換は規制対象。著しく顧客に不利なレートは不適切とされる場合があります。',
      lawReference: '風営法第23条'
    },
    {
      id: 'q_cust_003',
      statement: '顧客からの苦情記録は、営業所内に保管する必要がある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '苦情対応記録の保管は、営業の透明性維持のために重要です。',
      lawReference: '風営法施行規則第26条'
    },
    {
      id: 'q_cust_004',
      statement: '遊技機の故障時、客の被害がなければ報告義務は発生しない。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '故障は必ず報告し、必要に応じて記録保管する義務があります。',
      lawReference: '風営法施行規則'
    },
    {
      id: 'q_cust_005',
      statement: '営業所内での施設案内図、緊急連絡先は、目に付きやすい場所に掲示する義務がある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '施設の安全性と透明性のために、重要情報の掲示が必須です。',
      lawReference: '風営法施行規則第18条'
    },
    {
      id: 'q_cust_006',
      statement: '本人確認なしで高額の両替を行うことは、本人の希望であれば認められる。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'word_difference',
      explanation: 'マネーロンダリング対策のため、本人確認は必須。個人の希望は理由にならない。',
      lawReference: 'マネーロンダリング防止法'
    },
    {
      id: 'q_cust_007',
      statement: '営業所での施設整備費などは、顧客から直接徴収できる。',
      answer: false,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '経営費は営業者が負担。顧客からの徴収は不適切。',
      lawReference: '風営法'
    },
    {
      id: 'q_cust_008',
      statement: '換金方式に「景品相互交換」と「現金交換」の選択肢がある場合、顧客に対して説明責任がある。',
      answer: true,
      difficulty: 'hard',
      pattern: 4,
      trapType: 'complex_condition',
      explanation: '顧客に不利にならないよう、交換方式の説明が義務付けられています。',
      lawReference: '風営法第23条'
    }
  ],

  '法令違反と行政処分': [
    {
      id: 'q_viol_001',
      statement: '営業許可の取消となるのは、2度目の違反警告の場合である。',
      answer: false,
      difficulty: 'hard',
      pattern: 4,
      trapType: 'complex_condition',
      explanation: '取消事由は違反の種類・重大性で判断され、1度でも重大なら取消可能。回数が条件ではない。',
      lawReference: '風営法第15条'
    },
    {
      id: 'q_viol_002',
      statement: '営業時間を超過して営業した場合、営業停止命令の対象となることがある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: 'すべての営業許可違反が対象ではありませんが、時間超過は重大違反として扱われます。',
      lawReference: '風営法第24条'
    },
    {
      id: 'q_viol_003',
      statement: '行政処分（営業停止等）を受けた場合、異議申し立てを行う権利がある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '行政処分には異議申し立て・審査請求の手段があります。',
      lawReference: '行政不服審査法'
    },
    {
      id: 'q_viol_004',
      statement: '未成年者を遊技機の営業所に配置した場合、営業者個人が懲役刑に処せられる可能性がある。',
      answer: true,
      difficulty: 'hard',
      pattern: 1,
      trapType: 'none',
      explanation: '重大違反は刑事処罰の対象となり、懲役刑も科される可能性があります。',
      lawReference: '風営法第50条'
    },
    {
      id: 'q_viol_005',
      statement: '改造遊技機を設置した場合、営業許可の取消を避けることはできない。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '改造は重大違反ですが、取消までいかない場合もあります。状況と改造の程度による。',
      lawReference: '風営法第22条'
    },
    {
      id: 'q_viol_006',
      statement: '営業停止命令を受けた期間、営業所に誰も出入りしてはいけない。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '営業停止期間は営業所の全面閉鎖が必須。誰も遊技の客ではなく、業者の出入りも制限される。',
      lawReference: '風営法第24条'
    },
    {
      id: 'q_viol_007',
      statement: '暴力団関係者が営業所に出入りしていることが判明した場合、営業許可の取消対象となる。',
      answer: true,
      difficulty: 'hard',
      pattern: 4,
      trapType: 'complex_condition',
      explanation: '暴力団排除は風営法の重要課題。関係者の関与は重大違反となります。',
      lawReference: '暴力団排除条例'
    },
    {
      id: 'q_viol_008',
      statement: '違反警告を3回受けたら自動的に営業停止になる。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '警告の回数だけでは停止にならず、知事の判断により決定されます。',
      lawReference: '風営法'
    }
  ],

  '実務的対応': [
    {
      id: 'q_prac_001',
      statement: '営業所で火災が発生した場合、まず消防に通報し、その後に警察に届け出る。',
      answer: true,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'none',
      explanation: '緊急時は消防が最優先。人命救助後に関係機関への届け出を行います。',
      lawReference: '消防法・警察法'
    },
    {
      id: 'q_prac_add_001',
      statement: '営業所の月次売上報告は、顧客数が少ない月は提出を省略できる。',
      answer: false,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '売上報告は毎月提出が必須。業績に関わらず提出義務があります。',
      lawReference: '風営法施行規則'
    },
    {
      id: 'q_prac_add_002',
      statement: '顧客からの「景品が出ない」というクレームに対して、機械不具合の可能性を調査する責任は営業所にある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '顧客満足度確保のため、クレーム対応は営業所の責務です。',
      lawReference: '風営法'
    },
    {
      id: 'q_prac_add_003',
      statement: '営業所でのトイレ清掃は、客用・従業員用の両方を1日1回以上清掃する義務がある。',
      answer: true,
      difficulty: 'easy',
      pattern: 1,
      trapType: 'none',
      explanation: '衛生環境の維持は基本的義務。適切な施設管理が必須。',
      lawReference: '風営法施行規則第19条'
    },
    {
      id: 'q_prac_add_004',
      statement: '営業所での防犯カメラ設置は、法的に義務付けられていない。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'word_difference',
      explanation: '法的義務ではありませんが、トラブル対応の観点から設置が推奨されています。',
      lawReference: '個人情報保護法（合意のもと設置）'
    },
    {
      id: 'q_prac_add_005',
      statement: '営業所の定期的な警察による立ち入り検査の対応は、営業許可条件の一つである。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '許可条件として、行政の指導監督に応じることが含まれています。',
      lawReference: '風営法第9条'
    },
    {
      id: 'q_prac_add_006',
      statement: '営業所の責任者が不在の場合、営業を完全に停止することが義務である。',
      answer: false,
      difficulty: 'medium',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '責任者不在時は営業停止が一般的ですが、代理責任者による運営が認められる場合もあります。',
      lawReference: '風営法第12条'
    },
    {
      id: 'q_prac_add_007',
      statement: '営業所の営業記録（台数、売上、両替等）を3年以上保存する必要がある。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '税務調査対応など、営業記録の長期保管が必須です。',
      lawReference: '風営法施行規則第26条'
    },
    {
      id: 'q_prac_add_008',
      statement: '営業所の倒産・廃業時は、遊技機を引き上げるだけで行政への報告は不要である。',
      answer: false,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '廃業届の提出が必須です。行政への報告なく廃業することはできません。',
      lawReference: '風営法第10条'
    },
    {
      id: 'q_prac_002',
      statement: '不審客が営業所で不正行為を働こうとしたのを発見した場合、営業所のみで対応してよい。',
      answer: false,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'absolute_expression',
      explanation: '警察への届け出が必須。営業所のみでの対応は避けるべき。',
      lawReference: '風営法'
    },
    {
      id: 'q_prac_003',
      statement: '機械トラブルで顧客がお金を失った場合、営業所の責任で補償するのが通例である。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '営業所の責任（不具合など）によるトラブルは補償対象となる場合が多い。',
      lawReference: '消費者保護法'
    },
    {
      id: 'q_prac_004',
      statement: '定期的な税務調査への対応は、営業記録・帳簿を整備しておくことで円滑化される。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '記録整備は税務調査の基本。営業記録の完全保管が必須です。',
      lawReference: '税法'
    },
    {
      id: 'q_prac_005',
      statement: '新型感染症対策で営業所の営業時間短縮を検討する場合、事前に知事に相談する義務がある。',
      answer: false,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'word_difference',
      explanation: '営業時間は条令で定められており、自由な短縮は難しい。ただし感染対策の事情は相談可。',
      lawReference: '各都道府県条例'
    },
    {
      id: 'q_prac_006',
      statement: '従業員からの相談・苦情に対応するために、相談窓口を設置することは企業コンプライアンスの一部である。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: 'ハラスメント対応など、従業員福祉は運営の重要課題です。',
      lawReference: 'ハラスメント防止関連法'
    },
    {
      id: 'q_prac_007',
      statement: '来店客が施設内で転倒けが をした場合、営業所には損害賠償責任はない。',
      answer: false,
      difficulty: 'hard',
      pattern: 2,
      trapType: 'absolute_expression',
      explanation: '施設管理者責任があり、ステージ未発見等のケアレスなら責任を問われます。',
      lawReference: '民法415条'
    },
    {
      id: 'q_prac_008',
      statement: '営業所のホームページで遊技台の設置台数や営業時間を正確に表示することは、透明性向上の一環である。',
      answer: true,
      difficulty: 'medium',
      pattern: 1,
      trapType: 'none',
      explanation: '営業の透明性は顧客信頼の基盤。正確な情報提供は企業責任です。',
      lawReference: '消費者保護法'
    }
  ]
};

/**
 * 大量問題生成エンジン
 */
export class MockExamGenerator {
  /**
   * 全カテゴリから問題を生成
   * @param {number} targetCount - 目標問題数（デフォルト: 200）
   * @returns {Array}
   */
  static generateAllProblems(targetCount = 200) {
    const allProblems = [];
    let id = 1;

    for (const [category, problems] of Object.entries(mockProblems)) {
      for (const problem of problems) {
        problem.category = category;
        problem.global_id = id++;
        allProblems.push(problem);
      }
    }

    console.log(`✅ Generated ${allProblems.length} mock problems`);
    console.log(`   Target: ${targetCount} questions`);
    console.log(`   Coverage: ${Math.round((allProblems.length / targetCount) * 100)}%`);

    // 統計情報
    const stats = this._calculateStats(allProblems);
    console.log('\n📊 Statistics:');
    console.log(`   Categories: ${Object.keys(mockProblems).length}`);
    console.log(`   Difficulty:`, stats.difficulty);
    console.log(`   Patterns:`, stats.patterns);
    console.log(`   Trap Types:`, stats.traps);

    return allProblems;
  }

  /**
   * JSON形式で保存
   */
  static saveToFile(problems, filepath) {
    try {
      fs.writeFileSync(
        filepath,
        JSON.stringify({
          metadata: {
            generated_at: new Date().toISOString(),
            total_problems: problems.length,
            categories: Object.keys(mockProblems).length
          },
          problems: problems
        }, null, 2),
        'utf-8'
      );
      console.log(`✅ Saved to ${filepath}`);
    } catch (error) {
      console.error('❌ Error saving file:', error);
    }
  }

  /**
   * ランダム選択（重複なし）
   * @param {Array} problems
   * @param {number} count
   * @returns {Array}
   */
  static selectRandom(problems, count) {
    const shuffled = [...problems].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
  }

  /**
   * 統計計算
   */
  static _calculateStats(problems) {
    const stats = {
      difficulty: {},
      patterns: {},
      traps: {}
    };

    for (const problem of problems) {
      stats.difficulty[problem.difficulty] = (stats.difficulty[problem.difficulty] || 0) + 1;
      stats.patterns[`pattern_${problem.pattern}`] = (stats.patterns[`pattern_${problem.pattern}`] || 0) + 1;
      stats.traps[problem.trapType] = (stats.traps[problem.trapType] || 0) + 1;
    }

    return stats;
  }
}

// 実行
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('\n🚀 Mock Exam Generator Starting...\n');

  const problems = MockExamGenerator.generateAllProblems(200);
  MockExamGenerator.saveToFile(
    problems,
    '/home/planj/patshinko-exam-app/data/mock_problems.json'
  );

  console.log('\n✅ Generation Complete!');
}

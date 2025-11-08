# 問題数選択システムの実装設計ドキュメント

## 🏗️ システムアーキテクチャ

```
┌─────────────┐
│   Home.jsx  │
│ 問題数選択画面│
└──────┬──────┘
       │ 「低」「中」「高」クリック
       │ handleStartExam(mode)
       │
       ↓ localStorage.setItem('examMode', mode)
       │
┌──────────────────────────────────────┐
│    localStorage                      │
│    examMode: 'small'/'medium'/'large'│
└──────┬───────────────────────────────┘
       │ navigate('/exam')
       │
       ↓ React Router
┌──────────────────────────────────────┐
│   ExamScreen.jsx                     │
│   1. examMode = localStorage.getItem │
│   2. totalQuestions 計算             │
│   3. 難易度選択画面表示              │
└──────┬───────────────────────────────┘
       │ 難易度「低」「中」「高」選択
       │ setDifficultyLevel(level)
       │
       ↓ loadProblems() 実行
       │ API呼び出し
┌──────────────────────────────────────┐
│   Flask API (/api/problems/quiz)     │
│   1. count パラメータ受け取り        │
│   2. difficulty パラメータ受け取り   │
│   3. 難易度フィルタリング            │
│   4. ランダム選択                    │
│   5. 問題 JSON 返却                  │
└──────┬───────────────────────────────┘
       │
       ↓ API レスポンス
┌──────────────────────────────────────┐
│   ExamScreen.jsx UI                  │
│   1. 問題配列を setProblems          │
│   2. 進捗バー: 1/{problems.length}   │
│   3. 回答済み: {count}/{total}問     │
└──────────────────────────────────────┘
```

## 📋 各コンポーネントの責務

### **Home.jsx**
```javascript
// 責務：モード選択 → localStorage 保存 → 遷移
const handleStartExam = (mode) => {
  localStorage.setItem('examMode', mode);
  navigate('/exam', { replace: false });
};

// 呼び出し
onClick={() => handleStartExam('small')}    // 10問
onClick={() => handleStartExam('medium')}   // 30問
onClick={() => handleStartExam('large')}    // 50問
```

### **App.jsx**
```javascript
// 責務：ルーティング定義のみ（props は不要）
<Route
  path="/exam"
  element={<ExamScreen onExit={() => navigate('/', { replace: true })} />}
/>
```

### **ExamScreen.jsx**
```javascript
// 責務：localStorage から examMode を読む → totalQuestions 計算
export function ExamScreen({ onExit }) {
  // 1. localStorage から examMode を取得
  const examMode = localStorage.getItem('examMode') || 'small';

  // 2. totalQuestions を計算
  const totalQuestions = {
    small: 10,
    medium: 30,
    large: 50
  }[examMode] || 10;

  // 3. 難易度選択 → API呼び出し
  const loadProblems = useCallback(async () => {
    const requestBody = {
      count: totalQuestions,
      difficulty: selectedDifficulty
    };
    // API呼び出し
  }, [difficultyLevel, totalQuestions]);
}
```

### **Flask API (backend/api_server.py)**
```python
# 責務：難易度フィルタリング → count 数だけ返却
@app.route('/api/problems/quiz', methods=['POST'])
def get_quiz_problems():
    count = data.get('count', 10)          # 10/30/50
    difficulty = data.get('difficulty')   # ★/★★/★★★

    # 難易度でフィルタリング
    filtered = [p for p in problems if p.get('difficulty') == difficulty]

    # count 数だけランダム選択
    selected = random.sample(filtered, min(count, len(filtered)))

    return jsonify({'problems': selected, 'count': len(selected)})
```

## 🔄 データフロー詳細

### **ステップ1：モード選択時**
```
Home.jsx:
  onClick: handleStartExam('medium')
  → localStorage.setItem('examMode', 'medium')
  → navigate('/exam')
```

**localStorage の状態：**
```json
{
  "examMode": "medium"
}
```

### **ステップ2：ExamScreen マウント時**
```
ExamScreen.jsx:
  const examMode = localStorage.getItem('examMode')  // 'medium'
  const totalQuestions = {small:10, medium:30, large:50}[examMode]  // 30
  console.log('examMode:', examMode)  // 'medium'
  console.log('totalQuestions:', totalQuestions)  // 30
```

### **ステップ3：難易度選択時**
```
ExamScreen.jsx:
  onClick={() => setDifficultyLevel('medium')}
  → loadProblems() 実行
  → API呼び出し
```

**API リクエスト：**
```json
{
  "count": 30,        ← totalQuestions から
  "difficulty": "★★"  ← 難易度選択から
}
```

### **ステップ4：API処理**
```
Flask API:
  count: 30 を受け取り
  difficulty: '★★' を受け取り

  難易度 '★★' の問題を全て取得: 94問
  ランダムに 30問を選択
  返却: 30問
```

### **ステップ5：UI表示**
```
ExamScreen.jsx:
  setProblems(convertedProblems)  // 30要素の配列

  UI表示：
    進捗バー: 1/30問
    回答済み: 0/30問
```

## ✅ 検証チェックリスト

| 段階 | チェック項目 | 期待値 | 検証方法 |
|------|------------|-------|--------|
| **1** | Home.jsx で localStorage 設定 | 'small'/'medium'/'large' | grep + localStorage確認 |
| **2** | ExamScreen で localStorage 読込 | 'small'/'medium'/'large' | console.log + デバッグ |
| **3** | totalQuestions 計算 | 10/30/50 | console.log 出力 |
| **4** | API リクエスト count | 10/30/50 | ネットワークタブ確認 |
| **5** | API レスポンス問題数 | 10/30/50 | API テスト実行 |
| **6** | UI 表示問題数 | 10/30/50 | ブラウザで視認確認 |

## 🐛 バグが入りやすいポイント

### **❌ よくある間違い**

1. **App.jsx で examMode プロップを渡さない**
   ```javascript
   // ❌ 間違い
   <ExamScreen onExit={...} />

   // ✓ 正解：props不要（localStorage から読む）
   <ExamScreen onExit={...} />
   ```

2. **ExamScreen で props から examMode を受け取ろうとする**
   ```javascript
   // ❌ 間違い
   export function ExamScreen({ examMode, onExit }) {
     // examMode は undefined
   }

   // ✓ 正解：localStorage から読む
   export function ExamScreen({ onExit }) {
     const examMode = localStorage.getItem('examMode') || 'small';
   }
   ```

3. **useCallback 依存配列に totalQuestions を入れない**
   ```javascript
   // ❌ 間違い
   }, [difficultyLevel]);  // totalQuestions が古い値のまま

   // ✓ 正解
   }, [difficultyLevel, totalQuestions]);
   ```

4. **API呼び出しで count を hardcode する**
   ```javascript
   // ❌ 間違い
   const requestBody = { count: 10, difficulty: ... };

   // ✓ 正解
   const requestBody = { count: totalQuestions, difficulty: ... };
   ```

## 📊 テスト実行結果（検証済み）

### **API層テスト**
```
✅ 低難易度 × 10問: 10問返却
✅ 低難易度 × 30問: 30問返却
✅ 低難易度 × 50問: 50問返却
✅ 中難易度 × 10問: 10問返却
✅ 中難易度 × 30問: 30問返却
✅ 中難易度 × 50問: 50問返却
✅ 高難易度 × 10問: 10問返却
✅ 高難易度 × 30問: 30問返却
✅ 高難易度 × 50問: 50問返却

結果：全9パターン完全一致
```

### **フロー検証テスト**
```
✅ ステップ1：Home.jsx が localStorage に設定
✅ ステップ2：ExamScreen が localStorage から読込
✅ ステップ3：totalQuestions が正確に計算
✅ ステップ4：API呼び出しで正しい count パラメータ
✅ ステップ5：API が正しい問題数を返却
✅ ステップ6：UI で問題数が正確に表示

結論：すべてのデータフローが正確
```

## 🎯 今後の変更時の注意点

新機能追加や仕様変更時は必ず以下を確認：

1. **localStorage キー名が変わる場合**
   - Home.jsx での setItem キー名
   - ExamScreen での getItem キー名
   - 両者が一致しているか

2. **モード追加の場合**
   - Home.jsx のボタン追加
   - totalQuestions の新しいモード追加
   - API の難易度対応

3. **9パターンテストの再実行**
   - 必ず全9パターンで検証
   - 1つのパターンが失敗していないか確認

---

**最終更新：2025-11-08**
**ステータス：検証完了・本運用準備OK**

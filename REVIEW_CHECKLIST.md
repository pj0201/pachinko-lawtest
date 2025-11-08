# レビューチェックリスト - 問題数不一致バグ完全対応版

## 🔍 前回の失敗点

前回のレビューでは **API層だけ** をテストしていたため、以下の問題を見抜けなかった：
- App.jsx で examMode プロップが渡されていない
- ExamScreen が props から examMode を読むつもりだった
- localStorage の値が正確に設定・読み込まれているか確認していなかった
- コンポーネント間のデータフロー全体を追跡していなかった

## ✅ 改善されたレビュー方法：6段階検証

### **段階1：設計ドキュメント確認**
```
確認項目：
□ Home.jsx で localStorage.setItem('examMode', mode) が呼ばれているか
□ navigate('/exam') で正しくルーティングされるか
□ App.jsx の ExamScreen ルート定義を確認
  ☓ 間違い: <ExamScreen onExit={...} />  (examMode プロップなし)
  ✓ 正解: localStorage から直接読む
```

**チェック実行：**
```bash
grep -n "localStorage.setItem.*examMode" src/components/Home.jsx
grep -n "handleStartExam" src/components/Home.jsx
grep -n "<ExamScreen" src/App.jsx
```

### **段階2：localStorage フロー確認**

```
確認項目：
□ Home.jsx が localStorage に 'small'/'medium'/'large' を設定しているか
□ ExamScreen.jsx が localStorage.getItem('examMode') で読み込むか
□ 各モードのデフォルト値は適切か（デフォルト 'small' など）
```

**チェック実行：**
```bash
grep -n "localStorage.getItem.*examMode" src/components/ExamScreen.jsx
grep -n "const examMode" src/components/ExamScreen.jsx
```

### **段階3：totalQuestions 計算確認**

```
確認項目：
□ totalQuestions が examMode に基づいて正確に計算されるか
□ デフォルト値の処理（undefined時 → 'small' → 10）
□ useCallback 依存配列に examMode と totalQuestions が入っているか
```

**チェック実行：**
```bash
sed -n '71,76p' src/components/ExamScreen.jsx  # totalQuestions 定義
sed -n '217p' src/components/ExamScreen.jsx    # useCallback 依存配列
```

### **段階4：API呼び出しパラメータ確認**

```
確認項目：
□ API リクエストボディに count: totalQuestions が含まれるか
□ API リクエストボディに difficulty: selectedDifficulty が含まれるか
□ console.log で requestBody が出力されているか（デバッグ用）
```

**チェック実行：**
```bash
sed -n '105,109p' src/components/ExamScreen.jsx  # requestBody 定義
grep -n "📤 API リクエスト" src/components/ExamScreen.jsx
```

### **段階5：APIレスポンス検証**

```
確認項目：
□ バックエンド API が要求された count 数の問題を返すか
□ 難易度フィルタリングが正しく動作するか
□ responses.json() で問題配列が取得できるか
```

**チェック実行（Pythonテスト）：**
```python
import json
import sys
sys.path.insert(0, 'backend')
from api_server import app, load_problems

load_problems()
test_client = app.test_client()

# 3×3 = 9パターンすべてをテスト
test_patterns = [
    ('low', '★', 10), ('low', '★', 30), ('low', '★', 50),
    ('medium', '★★', 10), ('medium', '★★', 30), ('medium', '★★', 50),
    ('high', '★★★', 10), ('high', '★★★', 30), ('high', '★★★', 50),
]

for diff_front, diff_back, count in test_patterns:
    response = test_client.post('/api/problems/quiz',
        data=json.dumps({'count': count, 'difficulty': diff_back}),
        content_type='application/json')

    data = response.get_json()
    returned = len(data.get('problems', []))

    assert returned == count, f"❌ {count}問要求 → {returned}問返却（バグ）"
    print(f"✅ {count}問: OK")
```

### **段階6：フロント UI 表示確認**

```
確認項目：
□ ExamScreen の setProblems(convertedProblems) で全問題が設定されるか
□ problems.length が返却問題数と一致するか
□ 進捗バー表示: {currentIndex + 1}/{problems.length}問 が正確か
□ 回答済み表示: Object.keys(answers).length/{problems.length}問 が正確か
```

**チェック実行（ブラウザコンソール）：**
```javascript
// 試験開始時にコンソール出力
console.log('問題総数:', problems.length);
console.log('期待値:', totalQuestions);
console.log('一致:', problems.length === totalQuestions);
```

## 🛡️ 今後のレビュー徹底方法

### **レビュー実施時のチェックリスト**

```
[検証前]
□ 設計ドキュメントを確認（各ファイルの役割・責務を理解）
□ データフロー図を描く（Home → localStorage → ExamScreen → API → UI）

[検証実施]
□ 段階1-6 を順番に実行
□ 各段階で console.log 出力を確認（ブラウザ開発ツール）
□ 9パターン全てで API テスト実行
□ ブラウザで実際に「低」「中」「高」を選択して動作確認

[結果判定]
□ 9パターンすべて「要求数 = 返却数」を確認
□ デバッグログで各段階のデータが正確に流れているか確認
□ UI表示で問題数が正確に表示されるか確認

[バグ検出時]
□ どの段階で値が変わっているか特定
□ その段階の実装を修正
□ 再度全9パターンテスト実施
```

## 📊 今回の問題の教訓

| 段階 | 問題 | 原因 | 検出方法 |
|------|------|------|---------|
| **App.jsx** | examMode プロップ未設定 | 設計ミス | コンポーネント定義確認 |
| **ExamScreen** | examMode undefined | props受け取り前提 | localStorage読み込み確認 |
| **totalQuestions** | 常に10 | examMode undefined | デバッグログ確認 |
| **API呼び出し** | count=10固定 | totalQuestions計算ミス | requestBody ログ確認 |
| **UI表示** | 10問しか表示 | API返却50 → UI10 | 問題数表示確認 |

## ✅ 最終検証コマンド

```bash
# 1. ソースコード確認
grep -n "localStorage.setItem.*examMode" src/components/Home.jsx
grep -n "localStorage.getItem.*examMode" src/components/ExamScreen.jsx
sed -n '71,76p' src/components/ExamScreen.jsx
sed -n '217p' src/components/ExamScreen.jsx

# 2. API層テスト（Python）
python3 << 'EOF'
import json, sys
sys.path.insert(0, 'backend')
from api_server import app, load_problems
load_problems()
test_client = app.test_client()

test_patterns = [
    ('low', '★', 10), ('low', '★', 30), ('low', '★', 50),
    ('medium', '★★', 10), ('medium', '★★', 30), ('medium', '★★', 50),
    ('high', '★★★', 10), ('high', '★★★', 30), ('high', '★★★', 50),
]

for diff_front, diff_back, count in test_patterns:
    response = test_client.post('/api/problems/quiz',
        data=json.dumps({'count': count, 'difficulty': diff_back}),
        content_type='application/json')
    data = response.get_json()
    returned = len(data.get('problems', []))
    status = "✅" if returned == count else "❌"
    print(f"{status} {count}問: {returned}問")
EOF

# 3. ブラウザで実際に動作確認
# Home画面で「低」「中」「高」を順番に選択
# 各難易度で「低」「中」「高」を選択
# 9パターン全てで正しい問題数が表示されることを確認
```

## 🎯 最終結論

✅ 全9パターン（3難易度 × 3モード）で問題数が一致
✅ localStorage → ExamScreen → API → UI のデータフローが正確
✅ デバッグログで各段階が追跡可能
✅ コンポーネント間の props 受け渡しが正確

**今後は必ず6段階検証を実施して、段階ごとにバグを見抜く**

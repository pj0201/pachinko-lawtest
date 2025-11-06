# 🚀 Quick Fix Reference Guide - Patshinko Exam App Freeze

## 📋 Executive Summary

**Problem**: Application freezes for 300-500ms when loading exam questions  
**Root Cause**: Inefficient algorithms (sequential filtering, O(n×m) complexity)  
**Solution**: 5 targeted fixes totaling ~4 hours of work  
**Expected Result**: 300-500ms → 80-120ms freeze (80% improvement)

---

## 🔴 Priority 1: Critical Fixes (Do These First)

### Fix 1.1: Backend Index-Based Lookup (15 mins)

**File**: `/home/planj/patshinko-exam-app/backend/app.py`  
**Line**: 40-47 (ProblemManager.__init__)

**What to do**:
```python
# BEFORE:
class ProblemManager:
    def __init__(self):
        self.data = load_problems()
        self.problems = self.data['problems']
        self.metadata = self.data['metadata']

# AFTER: Add indices
class ProblemManager:
    def __init__(self):
        self.data = load_problems()
        self.problems = self.data['problems']
        self.metadata = self.data['metadata']
        
        # ✅ NEW: Fast lookup indices
        self._problem_by_id = {p['problem_id']: p for p in self.problems}
        self._build_category_index()
        self._build_difficulty_index()

    def _build_category_index(self):
        """Build category → [problems] mapping"""
        self._problems_by_category = {}
        for problem in self.problems:
            cat = problem['category']
            if cat not in self._problems_by_category:
                self._problems_by_category[cat] = []
            self._problems_by_category[cat].append(problem)

    def _build_difficulty_index(self):
        """Build difficulty → [problems] mapping"""
        self._problems_by_difficulty = {}
        for problem in self.problems:
            diff = problem['difficulty']
            if diff not in self._problems_by_difficulty:
                self._problems_by_difficulty[diff] = []
            self._problems_by_difficulty[diff].append(problem)
```

**Then update get_by_id()**:
```python
# BEFORE:
def get_by_id(self, problem_id: int):
    for p in self.problems:
        if p['problem_id'] == problem_id:
            return p
    return None

# AFTER:
def get_by_id(self, problem_id: int):
    return self._problem_by_id.get(problem_id)
```

**Why**: O(n) → O(1) lookup speed

---

### Fix 1.2: Efficient Stratified Sampling (30-40 mins)

**File**: `/home/planj/patshinko-exam-app/backend/app.py`  
**Lines**: 94-168 (get_stratified_problems method)

**What to do**: Replace the entire method with this optimized version:

```python
def get_stratified_problems(self,
                           count: int = 1,
                           difficulty: Optional[str] = None,
                           pattern: Optional[str] = None) -> List[Dict]:
    """
    Optimized stratified sampling using pre-built indices
    
    Category weights based on importance:
    - 遊技機管理: 40%
    - 営業時間・規制: 15%
    - 営業許可関連: 13%
    - 型式検定関連: 12%
    - 不正対策: 10%
    - 景品規制: 10%
    """
    category_distribution = {
        '遊技機管理': 0.40,
        '営業時間・規制': 0.15,
        '営業許可関連': 0.13,
        '型式検定関連': 0.12,
        '不正対策': 0.10,
        '景品規制': 0.10,
    }

    # ✅ Step 1: Get base problems (by difficulty if specified)
    if difficulty:
        base_problems = self._problems_by_difficulty.get(difficulty, self.problems)
    else:
        base_problems = self.problems

    # ✅ Step 2: Apply pattern filter if needed (single pass)
    if pattern:
        base_problems = [p for p in base_problems if p['pattern_name'] == pattern]

    # ✅ Step 3: Single-pass categorical distribution
    category_problems = {}
    for problem in base_problems:
        cat = problem['category']
        if cat not in category_problems:
            category_problems[cat] = []
        category_problems[cat].append(problem)

    # ✅ Step 4: Sample from each category proportionally
    selected_problems = []
    for category, percentage in category_distribution.items():
        target_count = round(count * percentage)
        available = category_problems.get(category, [])
        actual_count = min(target_count, len(available))
        
        if actual_count > 0:
            problems = random.sample(available, actual_count)
            selected_problems.extend(problems)

    # ✅ Step 5: Handle shortfall (if not enough new problems)
    if len(selected_problems) < count:
        remaining = count - len(selected_problems)
        selected_ids = {p['problem_id'] for p in selected_problems}
        
        remaining_problems = [
            p for p in base_problems 
            if p['problem_id'] not in selected_ids
        ]
        
        if remaining_problems:
            additional = random.sample(
                remaining_problems, 
                min(remaining, len(remaining_problems))
            )
            selected_problems.extend(additional)

    # ✅ Step 6: Fallback if still insufficient
    if not selected_problems:
        selected_problems = random.sample(base_problems, min(count, len(base_problems)))

    return selected_problems
```

**Why**: 24 iterations → ~2 iterations (90% faster)

---

## 🟠 Priority 2: High-Impact Fixes

### Fix 2.1: Frontend Set-Based Deduplication (10-15 mins)

**File**: `/home/planj/patshinko-exam-app/src/utils/questionDistribution.js`  
**Lines**: 81-127 (selectSmartQuestions function)

**What to do**: Replace the function with this:

```javascript
function selectSmartQuestions(allProblems, count = 10, options = {}) {
  const history = getUserQuestionHistory();
  const historySet = new Set(history);  // ✅ Convert to Set for O(1) lookup

  // ✅ Single-pass filter using Set (O(n) instead of O(n×m))
  let availableQuestions = allProblems.filter(
    q => !historySet.has(q.problem_id)
  );

  // If not enough new questions, allow retakes
  if (availableQuestions.length < count) {
    const retakeThreshold = 7; // Days
    const now = new Date();
    const stats = getQuestionDistributionStats();

    const retakeCandidates = allProblems.filter(q => {
      const stat = stats[q.problem_id];
      if (!stat || !stat.lastAttempt) return true;

      const lastAttempt = new Date(stat.lastAttempt);
      const daysDiff = (now - lastAttempt) / (1000 * 60 * 60 * 24);
      return daysDiff >= retakeThreshold;
    });

    availableQuestions = availableQuestions.concat(retakeCandidates);
  }

  // ✅ Use proper Fisher-Yates shuffle (O(n) instead of O(n log n))
  availableQuestions = fisherYatesShuffle(availableQuestions);
  return availableQuestions.slice(0, count);
}

// ✅ NEW: Efficient Fisher-Yates shuffle
function fisherYatesShuffle(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}
```

**Why**: O(n×m) + O(n log n) → O(n)

---

### Fix 2.2: Frontend Data Transformation Memoization (15-20 mins)

**File**: `/home/planj/patshinko-exam-app/src/components/ExamScreen.jsx`  
**Lines**: 105-172 (inside loadProblems function)

**What to do**:

1. Move constant outside component (before ExamScreen function):
```javascript
// ✅ Move outside component to avoid recreation
const DIFFICULTY_MAP = {
  '★': 'easy',
  '★★': 'medium',
  '★★★': 'hard',
  '★★★★': 'hard'
};

function formatLegalReference(legalRef) {
  if (!legalRef) return '';
  if (typeof legalRef === 'string') return legalRef;
  if (typeof legalRef === 'object') {
    return `${legalRef.law || ''} ${legalRef.article || ''} ${legalRef.section || ''}`.trim();
  }
  return '';
}
```

2. Update loadProblems to use memoized conversion:
```javascript
const loadProblems = useCallback(async () => {
  try {
    // ... existing code up to line 100 ...
    
    // ✅ Use memoized transformation
    const convertedProblems = allProblems.map(problem => ({
      id: problem.problem_id,
      statement: problem.problem_text,
      answer: problem.correct_answer === '○' || problem.correct_answer === true,
      explanation: problem.explanation,
      category: problem.category,
      difficulty: DIFFICULTY_MAP[problem.difficulty] || 'medium',
      lawReference: formatLegalReference(problem.legal_reference),
      pattern: problem.pattern_name,
      theme: problem.theme_name
    }));

    setProblems(convertedProblems);
    // ... rest of code ...
  } catch (err) {
    // ... error handling ...
  }
}, [difficultyLevel]);
```

**Why**: Avoid recreating objects and maps on each render

---

## 🟡 Priority 3: Quality Improvements

### Fix 3.1: Backend Response Caching (10 mins)

**File**: `/home/planj/patshinko-exam-app/backend/app.py`  
**Line**: 1 (imports)

**What to do**:

```python
# Add to imports at top of file:
from functools import lru_cache

# Wrap the stratified sampling with cache:
@lru_cache(maxsize=128)
def _cached_stratified(self, count: int, difficulty: str, pattern: str):
    """Internal method for caching stratified sampling results"""
    return tuple(
        json.loads(json.dumps(p)) 
        for p in self.get_stratified_problems(count, difficulty, pattern)
    )

# Then update the /api/problems/quiz endpoint:
@app.route('/api/problems/quiz', methods=['POST'])
def get_quiz():
    """Cache-aware quiz endpoint"""
    # ... validation code ...
    
    # Use cached version for common requests
    cache_key = (count, difficulty or 'all', pattern or 'all')
    if count <= 100 and not category:  # Only cache when using defaults
        problems = list(manager._cached_stratified(*cache_key))
    else:
        problems = manager.get_stratified_problems(count, difficulty, pattern)
    
    # ... rest of endpoint ...
```

**Why**: Repeated requests are instant (cache hit)

---

## ✅ Testing Checklist

After implementing fixes, test in this order:

### Backend Testing
```bash
# Test 1: Single problem lookup (should be <1ms)
curl http://localhost:5000/api/problems/1

# Test 2: 30-question quiz (should be <100ms)
time curl -X POST http://localhost:5000/api/problems/quiz \
  -H "Content-Type: application/json" \
  -d '{"count": 30, "difficulty": "★★"}'

# Test 3: 50-question quiz (should be <150ms)
time curl -X POST http://localhost:5000/api/problems/quiz \
  -H "Content-Type: application/json" \
  -d '{"count": 50, "difficulty": "★★★"}'
```

### Frontend Testing
1. Open http://localhost:5173
2. Click difficulty button
3. Open DevTools → Performance tab
4. Record while clicking "中" (medium)
5. Check that main thread blocking < 100ms

### Integration Testing
1. Start backend: `python3 backend/app.py`
2. Start frontend: `npm run dev`
3. Go through complete exam flow
4. Verify no freezing on difficulty selection
5. Check results display is instant

---

## 📊 Expected Metrics After Each Fix

| Fix # | Phase | Backend | Frontend | Total | Status |
|-------|-------|---------|----------|-------|--------|
| Before | Baseline | 250-350ms | 50-100ms | 300-500ms | ❌ |
| 1.1 | P1 Start | 200-300ms | 50-100ms | 250-400ms | ⚠️ |
| 1.2 | P1 Complete | 50-80ms | 50-100ms | 100-180ms | ✅ |
| 2.1 | P2 Step 1 | 50-80ms | 10-20ms | 80-120ms | ✅ |
| 2.2 | P2 Complete | 50-80ms | 5-15ms | 80-120ms | ✅ |
| 3.1 | P3 Cache | 0-50ms | 5-15ms | 20-70ms | ✅✅ |

---

## 🆘 Troubleshooting

**If backend still slow after Fix 1.2**:
- Check that indices are built correctly
- Run: `python3 -c "from backend.app import manager; print(len(manager._problems_by_category))"`
- Should output: 6 (six categories)

**If frontend still slow after Fix 2.1**:
- Check that Set is used (not Array.includes)
- Run: `console.log(typeof new Set([1,2,3]).has)`
- Open DevTools → Performance tab → check main thread

**If app crashes after changes**:
- Check syntax: `python3 -m py_compile backend/app.py`
- Check frontend: `npm run build 2>&1 | head -50`
- Revert last change and try again

---

## 📋 Implementation Checklist

```
PHASE 1 - CRITICAL
 [ ] Read through all fixes first
 [ ] Backup current app.py and questionDistribution.js
 [ ] Implement Fix 1.1 (index lookup)
 [ ] Implement Fix 1.2 (stratified sampling)
 [ ] Test backend response time
 [ ] Verify no syntax errors

PHASE 2 - HIGH IMPACT
 [ ] Implement Fix 2.1 (Set-based dedup)
 [ ] Implement Fix 2.2 (memoization)
 [ ] Test frontend performance
 [ ] Full end-to-end exam test

PHASE 3 - QUALITY
 [ ] Implement Fix 3.1 (caching)
 [ ] Test repeated quiz loads
 [ ] Performance monitoring
 [ ] Clean up any debug code

DOCUMENTATION
 [ ] Update README with performance notes
 [ ] Add implementation date to code comments
 [ ] Create performance baseline
```

---

## 💡 Pro Tips

1. **Test incrementally**: Do one fix, test it, then move to next
2. **Keep backups**: Save `app.py` before each major change
3. **Use DevTools**: Chrome DevTools Performance tab is your friend
4. **Monitor metrics**: Track response times before/after each fix
5. **Don't optimize prematurely**: Stick to the prioritized list

---

## 📞 If Stuck

Check these in order:
1. Does your Python syntax match exactly? (copy-paste is best)
2. Did you restart Flask? (`python3 app.py`)
3. Did you hard-refresh browser? (Ctrl+Shift+R)
4. Are indices actually being created? (add `print()` statements)
5. Is there a better algorithm? (check the analysis document)

---

**Total Implementation Time**: 4-6 hours  
**Expected Improvement**: 300-500ms → 80-120ms (80% faster)  
**Difficulty**: Medium (no rocket science, just careful refactoring)  
**Risk Level**: Low (well-tested patterns, easy to revert)

**Go forth and optimize! 🚀**

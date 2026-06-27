# Concept 2: Weighted Impurity & Best Split

## Ek Line Mein
> Har possible split try karo, jo split weighted Gini minimize kare — wahi best split hai.

---

## Part A: Weighted Impurity

### Kyun Weighted?

Sirf dono sides ka average nahi lete — **bada group zyada important hota hai.**

```
Total = 10 samples

Left  (7 samples): Gini = 0.3
Right (3 samples): Gini = 0.4

Simple avg    = (0.3 + 0.4) / 2       = 0.35   ❌ Wrong
Weighted avg  = (7/10)*0.3 + (3/10)*0.4 = 0.33  ✅ Correct
```

### Formula
```
Weighted Gini = (n_left/n_total) * gini(left) + (n_right/n_total) * gini(right)
```

### Worked Example
```
Total data: 10 samples
Left  (6): [0,0,0,1,0,1]  →  p(0)=4/6, p(1)=2/6  →  Gini = 0.444
Right (4): [1,1,1,0]      →  p(1)=3/4, p(0)=1/4  →  Gini = 0.375

Weighted = (6/10)*0.444 + (4/10)*0.375
         = 0.2664 + 0.150
         = 0.4164
```

---

## Part B: Best Split

### Logic
```
1. Har feature pe loop karo
2. Us feature ki saari unique values = possible thresholds
3. Har threshold pe:
     - Data 2 parts mein baanto (left <= threshold, right > threshold)
     - Weighted Gini calculate karo
     - Agar best se kam hai → update karo
4. Sabse kam Gini wala feature + threshold return karo
```

### Visual
```
Feature 0: [2.5, 1.0, 1.5, 3.0, 2.0]
Feature 1: [1.5, 1.0, 2.0, 3.0, 2.5]
y        : [ 0,   0,   1,   1,   1 ]

Threshold = Feature1, 1.5:
  Left  (<=1.5): y=[0,0]    → Gini=0.0
  Right (>1.5):  y=[1,1,1]  → Gini=0.0
  Weighted = 0.0  ← Best possible!
```

---

## Code

```python
def gini(y):
    classes = np.unique(y)
    impurity = 1
    for cls in classes:
        p = np.sum(y == cls) / len(y)
        impurity -= p**2
    return impurity

def best_split(X, y):
    best_impurity  = float('inf')   # shuruaat mein infinity
    best_feature   = None
    best_threshold = None

    for feature in range(X.shape[1]):          # har feature
        thresholds = np.unique(X[:, feature])  # us feature ki unique values

        for threshold in thresholds:           # har threshold
            left_idx  = X[:, feature] <= threshold
            right_idx = X[:, feature] > threshold

            n_total = len(y)
            n_left  = len(y[left_idx])
            n_right = len(y[right_idx])

            if n_left == 0 or n_right == 0:    # empty side → skip
                continue

            weighted_gini = (n_left/n_total)  * gini(y[left_idx]) + \
                            (n_right/n_total) * gini(y[right_idx])

            if weighted_gini < best_impurity:  # better split mila?
                best_impurity  = weighted_gini
                best_feature   = feature
                best_threshold = threshold

    return best_feature, best_threshold        # ← dono loops ke BAAD
```

### Code ka Line-by-Line Logic

| Line | Kya karta hai |
|------|--------------|
| `float('inf')` | Koi bhi impurity isse chhoti hogi — guarantee |
| `X.shape[1]` | Total features ki count |
| `np.unique(X[:, feature])` | Us column ki saari unique values |
| `X[:, feature] <= threshold` | Boolean mask — left side |
| `n_left == 0 or n_right == 0` | Empty split → worthless → skip |
| `if weighted_gini < best_impurity` | Better split mila toh update |
| `return` bahar loops ke | Sab features check hone ke BAAD return |

---

## Common Mistakes

| Mistake | Sahi |
|---------|------|
| `return` loop ke andar | `return` dono loops ke baahir |
| Empty side check nahi kiya | `if n_left == 0 or n_right == 0: continue` |
| `X[:features]` | `X[:, feature]` — comma zaruri |
| Simple average liya | Weighted average lo |

---

## Quick Revision — 3 Sawaal

1. Weighted impurity kyun use karte hain simple average ki jagah?
   *(Ans: Bada group zyada matter karta hai)*

2. `best_impurity = float('inf')` kyun?
   *(Ans: Pehla comparison hamesha True ho — koi bhi value infinity se kam hoti hai)*

3. `return` loop ke andar hone se kya problem hogi?
   *(Ans: Sirf pehla feature check hoga, baaki skip ho jaayenge)*

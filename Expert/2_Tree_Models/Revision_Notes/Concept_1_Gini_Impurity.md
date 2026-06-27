# Concept 1: Gini Impurity

## Ek Line Mein
> Gini batata hai ki ek group kitna "mixed" hai. **0 = pure, 0.5 = bilkul mixed.**

---

## Real Life Analogy

Do dabbe hain:
```
Dabba A:  🔴 🔴 🔴 🔴   → Pure   → Gini = 0.0
Dabba B:  🔴 🔵 🔴 🔵   → Mixed  → Gini = 0.5
```
Decision Tree chahta hai ki **har group pure ho** — isliye Gini ko minimize karta hai.

---

## Formula

```
Gini = 1 - Σ(pᵢ²)

where pᵢ = probability of class i in the group
```

### Step by Step:
1. Har class ki probability nikalo: `p = count(class) / total`
2. Har p ko square karo: `p²`
3. Sab squares add karo: `Σ(p²)`
4. 1 se ghata do: `1 - Σ(p²)`

---

## Worked Examples

### Example 1 — Pure Group
```
y = [0, 0, 0, 0]
p(0) = 4/4 = 1.0

Gini = 1 - (1.0²)
     = 1 - 1.0
     = 0.0  ✅ Perfect purity
```

### Example 2 — Bilkul Mixed
```
y = [0, 0, 1, 1]
p(0) = 2/4 = 0.5
p(1) = 2/4 = 0.5

Gini = 1 - (0.5² + 0.5²)
     = 1 - (0.25 + 0.25)
     = 1 - 0.5
     = 0.5  ❌ Worst case
```

### Example 3 — Thoda Mixed
```
y = [0, 0, 1, 1, 1]
p(0) = 2/5 = 0.4
p(1) = 3/5 = 0.6

Gini = 1 - (0.4² + 0.6²)
     = 1 - (0.16 + 0.36)
     = 1 - 0.52
     = 0.48
```

### Example 4 — Thoda Impure
```
y = [1, 1, 1, 0]
p(1) = 3/4 = 0.75
p(0) = 1/4 = 0.25

Gini = 1 - (0.75² + 0.25²)
     = 1 - (0.5625 + 0.0625)
     = 1 - 0.625
     = 0.375
```

---

## Gini Values Reference Table

| Group          | Gini  | Matlab              |
|----------------|-------|---------------------|
| [0,0,0,0]      | 0.0   | Pure — ek hi class  |
| [1,1,1,0]      | 0.375 | Thoda mixed         |
| [0,0,1,1,1]    | 0.48  | Zyada mixed         |
| [0,1,0,1]      | 0.5   | 50-50 — worst case  |

---

## Code — From Scratch

```python
import numpy as np

def gini(y):
    classes = np.unique(y)   # Step 1: unique classes nikalo
    impurity = 1
    for cls in classes:
        p = np.sum(y == cls) / len(y)   # Step 2: probability
        impurity -= p**2                 # Step 3: p² ghata do
    return impurity
```

### Code ka Logic Line by Line:
```python
classes = np.unique(y)
# y = [0,0,1,1,1]  →  classes = [0, 1]

p = np.sum(y == cls) / len(y)
# y == 0  →  [True, True, False, False, False]
# np.sum  →  2
# / len(y) → 2/5 = 0.4

impurity -= p**2
# 1 - 0.4² - 0.6² = 1 - 0.16 - 0.36 = 0.48
```

### Test Cases:
```python
print(gini(np.array([0, 0, 0, 0])))      # 0.0
print(gini(np.array([0, 1, 0, 1])))      # 0.5
print(gini(np.array([0, 0, 1, 1, 1])))   # 0.48
print(gini(np.array([1, 1, 1, 0])))      # 0.375
```

---

## Common Mistakes

| Mistake | Sahi Tarika |
|---------|-------------|
| `p = count / total` bhool gaye | Hamesha `np.sum(y == cls) / len(y)` |
| Sirf ek class ka p liya | Loop lagao `np.unique(y)` pe |
| `p` square nahi kiya | `impurity -= p**2` — `**2` zaroor |
| `1 -` lagana bhool gaye | Formula: `impurity = 1`, phir ghata do |

---

## Quick Revision — 3 Sawaal

1. `y = [0,0,0,1]` ka Gini kya hoga? *(Ans: 0.375)*
2. Gini kab 0 hota hai? *(Ans: Jab group pure ho — ek hi class)*
3. `impurity -= p**2` mein `**2` kyun? *(Ans: Formula mein p squared hai)*

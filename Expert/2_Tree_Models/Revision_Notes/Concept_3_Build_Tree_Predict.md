# Concept 3: Build Tree & Predict

## Ek Line Mein
> Recursively best split karo jab tak group pure na ho ya depth limit na aaye. Predict karne ke liye tree traverse karo.

---

## Recursion Ka Core Idea

```
build_tree(poora data)
├── best_split dhundo
├── build_tree(LEFT data,  depth+1)   ← same function, chota data
└── build_tree(RIGHT data, depth+1)   ← same function, chota data
```

Har baar same kaam — bas data chhota hota jaata hai!

---

## Tree Kab Rukta Hai? (3 Stopping Conditions)

| Condition | Code | Matlab |
|-----------|------|--------|
| Depth limit | `depth >= self.max_depth` | Bahut gehri ho gayi |
| Pure group | `len(np.unique(y)) == 1` | Ek hi class bacha |
| Kam samples | `len(y) < self.min_samples_split` | Split karne layak nahi |

Koi bhi condition True → **Leaf node banao → majority class return karo**

```python
leaf_value = np.bincount(y).argmax()
# y=[0,0,1] → bincount=[2,1] → argmax=0 → majority=0
```

---

## Node Structure

```
Split Node:  Node(feature, threshold, left, right)
             "Feature X pe threshold T pe split karo"

Leaf Node:   Node(value=class)
             "Ruk jao — answer yeh hai"
```

---

## Code

```python
class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature   = feature
        self.threshold = threshold
        self.left      = left
        self.right     = right
        self.value     = value


class DecisionTree:
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth         = max_depth
        self.min_samples_split = min_samples_split

    def build_tree(self, X, y, depth=0):
        # Stopping conditions
        if depth >= self.max_depth or len(np.unique(y)) == 1 or len(y) < self.min_samples_split:
            leaf_value = np.bincount(y).argmax()
            return Node(value=leaf_value)

        # Best split
        feature, threshold = self.best_split(X, y)

        # Data baanto
        left_idx  = X[:, feature] <= threshold
        right_idx = X[:, feature] > threshold

        # Recursion
        left  = self.build_tree(X[left_idx],  y[left_idx],  depth+1)
        right = self.build_tree(X[right_idx], y[right_idx], depth+1)

        return Node(feature, threshold, left, right)

    def fit(self, X, y):
        self.tree = self.build_tree(X, y)

    def predict_sample(self, x, node):
        if node.value is not None:       # leaf node
            return node.value
        if x[node.feature] <= node.threshold:
            return self.predict_sample(x, node.left)
        return self.predict_sample(x, node.right)

    def predict(self, X):
        return np.array([self.predict_sample(x, self.tree) for x in X])
```

---

## Code ka Logic Line by Line

```python
if depth >= self.max_depth or len(np.unique(y)) == 1 or len(y) < self.min_samples_split:
# depth >= max_depth  → bahut gehri tree, ruk jao
# len(np.unique(y)) == 1  → sirf ek class bacha, pure node
# len(y) < min_samples_split  → bahut kam samples, split nahi kar sakte

leaf_value = np.bincount(y).argmax()
# y = [0,0,1,0]  →  bincount = [3,1]  →  argmax = 0  →  majority class = 0

return Node(value=leaf_value)
# value set hai, feature/threshold/left/right = None → yeh leaf node hai

feature, threshold = self.best_split(X, y)
# best_split saari features aur thresholds try karke
# jo weighted gini minimize kare woh return karta hai

left_idx  = X[:, feature] <= threshold
right_idx = X[:, feature] > threshold
# boolean mask — True/False array
# X[left_idx]  → sirf left wale rows
# X[right_idx] → sirf right wale rows

left  = self.build_tree(X[left_idx],  y[left_idx],  depth+1)
right = self.build_tree(X[right_idx], y[right_idx], depth+1)
# same function, chota data, ek level aur neeche
# depth+1 → tree ko pata chale kitna neeche gaya

return Node(feature, threshold, left, right)
# split node — value=None, lekin feature/threshold/children set hain

if node.value is not None:
# leaf node check — agar value set hai toh ruk jao
# split node mein value=None hota hai

if x[node.feature] <= node.threshold:
    return self.predict_sample(x, node.left)
return self.predict_sample(x, node.right)
# same tree traversal — left ya right jao condition ke basis pe

return np.array([self.predict_sample(x, self.tree) for x in X])
# har sample ke liye tree traverse karo
# self.tree = root node hai jahan se traversal shuru hoti hai
```

---

## Predict Ka Flow

```
Naya sample: x = [5, 70]

Root:  feature=1, threshold=60
       x[1]=70 > 60  → Right

Right: feature=0, threshold=5
       x[0]=5 <= 5   → Left

Left:  value=1 → LEAF → Return 1
```

---

## Common Mistakes

| Mistake | Sahi |
|---------|------|
| `len(np.unique(y) == 1)` | `len(np.unique(y)) == 1` — bracket bahar |
| `def build_tree(X, y)` | `def build_tree(self, X, y)` — self zaruri |
| `depth` pass nahi kiya | `depth+1` pass karo recursion mein |
| `node.leaf` | `node.left` — attribute ka naam |
| `return` loop ke andar | `return Node(...)` dono loops ke baad |

---

## Quick Revision — 3 Sawaal

1. `depth+1` kyun pass karte hain?
   *(Ans: Tree ko pata chale kitna neeche gaya — warna infinite loop)*

2. Leaf node mein kya store hota hai?
   *(Ans: Majority class — `np.bincount(y).argmax()`)*

3. `predict_sample` mein base case kya hai?
   *(Ans: `node.value is not None` — leaf node mil gaya)*

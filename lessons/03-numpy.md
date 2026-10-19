# NumPy — Arrays and Vectorised Computation

<p class="lesson-intro">Week 3 · Programming for Data Science (606315)</p>

Pure-Python lists are flexible but slow and memory-hungry. NumPy's `ndarray` stores numbers in one contiguous block of typed memory and runs loops in C. Pandas, Scikit-learn and Matplotlib are all built on it, so the mental model you build here carries through the rest of the course.

## 1 · Why NumPy

Same computation, two ways. The rule that follows: **never loop over array elements in Python when an array operation exists.**

```python run
import numpy as np, time

n = 1_000_000
py_list = list(range(n))
arr = np.arange(n)

t0 = time.perf_counter(); _ = [x * 2.5 + 1 for x in py_list]; t_py = time.perf_counter() - t0
t0 = time.perf_counter(); _ = arr * 2.5 + 1;                  t_np = time.perf_counter() - t0
print(f"list comprehension: {t_py * 1e3:7.1f} ms")
print(f"numpy             : {t_np * 1e3:7.1f} ms   ({t_py / t_np:.0f}x faster)")
```

## 2 · Creating arrays

```python run
import numpy as np
np.set_printoptions(precision=3, suppress=True)

a = np.array([1, 2, 3])                      # from a list
b = np.array([[1.0, 2.0], [3.0, 4.0]])       # 2-D from nested lists
print(a); print(b)

print(np.zeros((2, 3)))                      # shape is a tuple
print(np.ones(4, dtype=int))
print(np.full((2, 2), 7))
print(np.eye(3))                             # identity
print(np.arange(0, 1, 0.25))                 # like range(), float step allowed
print(np.linspace(0, 1, 5))                  # 5 evenly spaced points, inclusive
```

## 3 · `dtype`, `shape`, `ndim`

Check these three attributes on every array you receive. Unlike Python integers, NumPy integers have a fixed width — they can overflow.

```python run
import numpy as np

m = np.arange(12)
print(m.dtype, m.shape, m.ndim)

m2 = m.reshape(3, 4)          # a view of the same memory with a new shape
print(m2); print(m2.shape, m2.ndim)
print(m.reshape(2, -1).shape) # -1 means "work it out"
print(m2.T.shape)             # transpose
print(m2.ravel().shape)       # back to 1-D

i = np.array([1, 2, 3])
print(i / 2, i // 2, i.astype(np.float32).dtype)
small = np.array([250], dtype=np.uint8)
print(small + 10)             # wraps around!
```

## 4 · Indexing and slicing — views, not copies

Slicing a NumPy array returns a **view**: changing the slice changes the original. This is deliberate (no copying of big arrays) and the most common beginner bug.

```python run
import numpy as np
x = np.arange(10)
print(x[2], x[-1], x[2:5], x[::2], x[::-1])

s = x[2:5]
s[:] = 99
print("original after editing the slice:", x)     # changed!

c = x[5:8].copy()
c[:] = -1
print("original after editing the copy :", x)     # unchanged
```

```python run
import numpy as np
g = np.arange(1, 13).reshape(3, 4)
print(g)
print("row 1        :", g[1])
print("element (1,2):", g[1, 2])      # one bracket: row, column
print("column 2     :", g[:, 2])
print("sub-block    :"); print(g[0:2, 1:3])
print("last column  :", g[:, -1])
```

:::exercise id=ex1 title="Frame without loops"
Return a 5×5 integer array whose border is 1 and interior is 0. Use `np.ones` and one slice assignment — no loops.

```python
import numpy as np

def frame():
    f = np.ones((5, 5), dtype=int)
    ...
    return f

print(frame())
```

```python check
import numpy as np
f = frame()
assert f.shape == (5, 5) and f.dtype.kind == "i", "5x5 integer array expected"
assert f.sum() == 16 and f[2, 2] == 0 and f[0].sum() == 5 and f[:, 0].sum() == 5, "border must be 1, interior 0"
```
:::

## 5 · Boolean masks and fancy indexing

A comparison on an array gives a boolean array of the same shape; use it as an index to **filter**. This replaces `if` inside loops, and it is exactly how Pandas' `df[df.col > x]` works. Combine masks with `&`, `|`, `~` and put parentheses around each comparison.

```python run
import numpy as np
gpa = np.array([3.4, 2.1, 3.9, 2.8, 1.9, 3.2, 3.7])

mask = gpa >= 3.0
print(mask)
print(gpa[mask])
print(gpa[(gpa >= 2.0) & (gpa < 3.5)])
print(np.where(gpa >= 3.0, "honours", "regular"))     # vectorised if/else

gpa[gpa < 2.0] = 2.0                                  # assignment through a mask
print(gpa)
```

```python run
import numpy as np
gpa   = np.array([3.4, 2.1, 3.9, 2.8, 1.9, 3.2, 3.7])
names = np.array(["Ahmad", "Sara", "Omar", "Lina", "Khaled", "Noor", "Yousef"])

order = np.argsort(gpa)[::-1]          # indices that sort descending
print(order)
print(names[order][:3], gpa[order][:3])   # fancy indexing → always a copy
```

:::exercise id=ex2 title="Clip and count"
`clip_gpa(g)` returns a tuple `(array, n_changed)`: a **copy** of `g` where values below 0 become 0 and values above 4 become 4, plus how many values were changed. Do not use `np.clip`; use masks. The input must not be modified.

```python
import numpy as np

def clip_gpa(g):
    out = g.copy()
    ...
    return out, n_changed

print(clip_gpa(np.array([-1.0, 2.5, 4.7, 4.0])))
```

```python check
import numpy as np
src = np.array([-1.0, 2.5, 4.7, 4.0])
arr, n = clip_gpa(src)
assert list(arr) == [0.0, 2.5, 4.0, 4.0], f"got {arr}"
assert n == 2, f"n_changed should be 2, got {n}"
assert list(src) == [-1.0, 2.5, 4.7, 4.0], "input must not be modified"
```
:::

## 6 · Vectorised arithmetic and broadcasting

Arithmetic is element-wise. When shapes differ, NumPy **broadcasts** the smaller array across the larger one by one rule — compare shapes from the right; each pair of dimensions must be equal, or one of them must be 1:

```
(3, 4)  +  (4,)   → (3, 4)   ✓  a row vector is added to every row
(3, 4)  +  (3, 1) → (3, 4)   ✓  a column vector is added to every column
(3, 4)  +  (3,)   → error    ✗  3 ≠ 4
```

```python run
import numpy as np
scores = np.array([[80, 90, 70],
                   [60, 85, 95],
                   [75, 65, 80]])          # 3 students × 3 exams
weights = np.array([0.3, 0.3, 0.4])        # one weight per exam → shape (3,)

print(scores * weights)                    # broadcast across rows
print("weighted total per student:", (scores * weights).sum(axis=1))

bonus = np.array([[5], [0], [10]])         # one bonus per student → shape (3, 1)
print(scores + bonus)

# standardising columns is broadcasting in one line
z = (scores - scores.mean(axis=0)) / scores.std(axis=0)
print(z.round(3))
```

## 7 · Aggregations and `axis`

`axis=0` collapses rows (one value **per column**); `axis=1` collapses columns (one value **per row**). No `axis` collapses everything. Use the `nan*` variants when data has holes.

```python run
import numpy as np
scores = np.array([[80, 90, 70], [60, 85, 95], [75, 65, 80]])

print(scores.sum(), scores.mean().round(2), scores.max())
print("per exam    (axis=0):", scores.mean(axis=0).round(2))
print("per student (axis=1):", scores.mean(axis=1).round(2))
print("best exam per student:", scores.argmax(axis=1))
print("any > 90:", (scores > 90).any(), " all > 50:", (scores > 50).all())

with_nan = np.array([3.4, np.nan, 2.8, 3.9])
print(with_nan.mean(), np.nanmean(with_nan).round(3), np.isnan(with_nan).sum())
```

:::exercise id=ex3 title="Row normalisation with broadcasting"
`normalise_rows(M)` scales each **row** of a 2-D array so that it sums to 1. Rows that sum to 0 must stay all-zero — no `NaN`. Hint: `keepdims=True` and `np.divide(..., where=...)`.

```python
import numpy as np

def normalise_rows(M):
    s = M.sum(axis=1, keepdims=True)
    ...

M = np.array([[1., 1., 2.], [0., 0., 0.], [5., 0., 0.]])
print(normalise_rows(M))
```

```python check
import numpy as np
M = np.array([[1., 1., 2.], [0., 0., 0.], [5., 0., 0.]])
R = normalise_rows(M)
assert R.shape == (3, 3)
assert not np.isnan(R).any(), "zero rows must not produce NaN"
assert np.allclose(R, [[0.25, 0.25, 0.5], [0, 0, 0], [1, 0, 0]]), f"got\n{R}"
```
:::

## 8 · Random numbers — the modern API

Use `np.random.default_rng(seed)`, not the legacy `np.random.seed`. A seeded generator makes an experiment reproducible, which is essential for coursework and research.

```python run
import numpy as np
rng = np.random.default_rng(42)
print(rng.integers(1, 7, size=5))                 # dice
print(rng.random(3).round(3))                     # uniform [0, 1)
print(rng.normal(loc=2.9, scale=0.5, size=4).round(3))
print(rng.choice(["DS", "CS", "AI"], size=5, p=[0.5, 0.3, 0.2]))
print(np.random.default_rng(42).integers(1, 7, size=5))   # same seed → same draws

# simulation in two lines: P(mean of 30 dice rolls > 4)
rolls = rng.integers(1, 7, size=(50_000, 30))
print((rolls.mean(axis=1) > 4).mean())
```

:::exercise id=ex4 title="Sample means, reproducibly"
`sample_means(seed, n_samples, size)` draws `n_samples` samples of `size` values each from a standard normal distribution using `default_rng(seed)` and returns the array of sample means — shape `(n_samples,)`, no Python loop.

```python
import numpy as np

def sample_means(seed, n_samples, size):
    rng = np.random.default_rng(seed)
    ...

m = sample_means(7, 1000, 25)
print(m.shape, m.mean().round(3), m.std().round(3))
```

```python check
import numpy as np
m = sample_means(7, 1000, 25)
assert m.shape == (1000,), f"shape {m.shape}"
assert np.array_equal(m, sample_means(7, 1000, 25)), "same seed must give the same result"
assert abs(m.mean()) < 0.05 and abs(m.std() - 0.2) < 0.03, "means of 25 N(0,1) draws should have sd ≈ 0.2"
```
:::

## 9 · Linear algebra

`@` is matrix multiplication; `*` is element-wise. Prefer `np.linalg.solve` to computing an inverse.

```python run
import numpy as np
A = np.array([[2., 1.], [1., 3.]])
b = np.array([3., 5.])

print(A @ b)                              # matrix–vector product
print(A * A)                              # element-wise, not A²
x = np.linalg.solve(A, b)                 # solve Ax = b
print("x =", x, " check:", A @ x)
print("det", np.linalg.det(A).round(3), " norm", np.linalg.norm(b).round(3))

# least squares: fit y = m·x + c
rng = np.random.default_rng(0)
xs = np.arange(10)
ys = 2.5 * xs + 1 + rng.normal(0, 1, 10)
X = np.column_stack([xs, np.ones_like(xs)])
(m, c), *_ = np.linalg.lstsq(X, ys, rcond=None)
print(f"fitted slope {m:.2f}, intercept {c:.2f}")
```

:::exercise id=ex5 title="Pairwise distances by broadcasting"
`pairwise(P)` takes an `(n, 2)` array of points and returns the `(n, n)` matrix of Euclidean distances using broadcasting only — no loops. Hint: `P[:, None, :] - P[None, :, :]` has shape `(n, n, 2)`.

```python
import numpy as np

def pairwise(P):
    diff = ...
    return ...

P = np.array([[0, 0], [3, 4], [6, 8]])
print(pairwise(P))
```

```python check
import numpy as np
D = pairwise(np.array([[0, 0], [3, 4], [6, 8]]))
assert D.shape == (3, 3), f"shape {D.shape}"
assert np.allclose(D, [[0, 5, 10], [5, 0, 5], [10, 5, 0]]), f"got\n{D}"
```
:::

## 10 · Worked example: outliers in real data

Load one numeric column of `sales_2025.csv` with `np.genfromtxt`, compute revenue and z-scores, and find outliers — without a single Python loop.

```python run
import numpy as np
data = np.genfromtxt("data/sales_2025.csv", delimiter=",", names=True, dtype=None, encoding="utf-8")
print(data.dtype.names, data.shape)

revenue = data["units"] * data["unit_price"]
z = (revenue - revenue.mean()) / revenue.std()
print(f"{(np.abs(z) > 3).sum()} outlier rows out of {len(revenue)}")
print("largest sale:", data[revenue.argmax()])

for p in np.unique(data["product"]):
    print(f"{p:11s} {revenue[data['product'] == p].sum():12,.0f}")
```

## Summary

* Arrays are **typed, fixed-shape, contiguous** — check `dtype`, `shape`, `ndim`.
* Slices are **views**; `.copy()` when you need independence.
* **Masks** replace `if` inside loops; combine with `&`, `|`, `~`.
* **Broadcasting**: align shapes from the right; 1 stretches.
* `axis=0` → per column, `axis=1` → per row. `default_rng(seed)` for reproducibility.

Next: *Pandas I* — the same ideas, with labels.

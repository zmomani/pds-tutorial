# Sample — Textbook-based Sections

<p class="lesson-intro">Preview for Weeks 3–5 · Programming for Data Science (606315)</p>

This page is a **sample** of how the NumPy and Pandas weeks would look when built on the course textbook, Jake VanderPlas, *Python Data Science Handbook* (2nd ed., O'Reilly). It contains one NumPy section and one Pandas section.

> **📘 From the textbook.** A blue book next to a heading means the section follows the order of ideas in the matching textbook section. The explanations, examples and diagrams are written for this course; the "Read more" link at the end of each section points to the original text.
>
> **Helper notes.** Words in the code with a dotted underline have a short note. Hover over one (or tap it) to read what it does.

## A · NumPy: broadcasting 📘

### A.1 · The idea

Arithmetic between two arrays of the **same shape** works element by element. **Broadcasting** is the set of rules NumPy uses when the shapes are **different**: it stretches the smaller array so the shapes match, then works element by element as usual.

The simplest case is an array and a single number. The number is used for every element.

```python run
import numpy as np

scores = np.array([70, 80, 90])
print(scores + 5)
```

A table and a row also work. The row is used for every row of the table.

```python run
import numpy as np

scores = np.array([[70, 80, 90],
                   [60, 85, 95],
                   [75, 65, 80]])      # 3 students x 3 exams
bonus = np.array([5, 0, 10])           # one bonus per exam

print(scores + bonus)
```

In the third case **both** arrays are stretched. A column of 3 values and a row of 3 values give a 3 × 3 table.

```python run
import numpy as np

tens = np.array([0, 10, 20])[:, np.newaxis]   # a column, shape (3, 1)
ones = np.array([1, 2, 3])                    # a row, shape (3,)

print(tens.shape, ones.shape)
print(tens + ones)
```

![Three additions: an array plus a number, a table plus a row, and a column plus a row. Dashed cells are the copies that broadcasting creates.](figures/broadcasting.svg)

<p class="caption">The dashed cells are not stored anywhere. NumPy only behaves <em>as if</em> the smaller array had been copied, which is why broadcasting costs no extra memory.</p>

### A.2 · The three rules

NumPy compares the two shapes **from the right-hand side** and applies three rules.

1. If one array has fewer dimensions, its shape is padded with 1s **on the left**.
2. Where the two sizes differ and one of them is 1, that array is stretched to match the other.
3. Where the two sizes differ and neither is 1, NumPy raises an error.

Applied to the table-plus-row example above:

| Step | `scores` | `bonus` |
|---|---|---|
| Start | `(3, 3)` | `(3,)` |
| Rule 1: pad on the left | `(3, 3)` | `(1, 3)` |
| Rule 2: stretch the 1 | `(3, 3)` | `(3, 3)` |

You can ask NumPy to apply the rules to shapes alone, without building any arrays:

```python run
import numpy as np

print(np.broadcast_shapes((3, 3), (3,)))
print(np.broadcast_shapes((3, 1), (3,)))
```

:::challenge title="Predict the result shape"
For each pair of shapes, decide whether the arrays can be added. If they can, what is the shape of the result?

1. `(2, 3)` and `(3,)`
2. `(2, 3)` and `(2,)`
3. `(2, 1)` and `(1, 3)`
4. `(4,)` and `(4, 1)`

Write your four answers down first. Then run the code below to check them.

```python run
import numpy as np

pairs = [((2, 3), (3,)), ((2, 3), (2,)), ((2, 1), (1, 3)), ((4,), (4, 1))]
for a, b in pairs:
    try:
        print(a, "+", b, "->", np.broadcast_shapes(a, b))
    except ValueError:
        print(a, "+", b, "-> error")
```
---
1. `(2, 3)`. The row of 3 is copied down both rows.
2. **Error.** Padding gives `(1, 2)`; comparing from the right, 3 and 2 differ and neither is 1.
3. `(2, 3)`. Both arrays are stretched.
4. `(4, 4)`. Many students expect `(4,)` here. The first shape is padded to `(1, 4)`, and then both arrays are stretched. This one causes real bugs, because it runs without an error.
:::

### A.3 · When it fails, and how to fix it

A common task: subtract each student's own average from their scores. The averages have one value per **row**, but broadcasting lines shapes up from the right, so NumPy tries to match them with the **columns**.

```python run
import numpy as np

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])     # 3 students x 4 exams
row_mean = scores.mean(axis=1)             # shape (3,)

try:
    print(scores - row_mean)
except ValueError as err:
    print("ValueError:", err)
```

The fix is to make the averages a **column** of shape `(3, 1)`. There are two ways to do it, and they give the same result.

```python run
import numpy as np

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])

col_a = scores.mean(axis=1)[:, np.newaxis]       # add the dimension afterwards
col_b = scores.mean(axis=1, keepdims=True)       # or never lose it

print(col_a.shape, col_b.shape)
print(scores - col_b)
```

> **Look out: the silent version of this mistake.** With a **square** table the wrong code does not fail. A `(3, 3)` table minus a `(3,)` array of row averages is a legal broadcast, so NumPy subtracts each average from a *column* and gives you wrong numbers without any warning. Run the next example and compare the two results.

```python run
import numpy as np

square = np.array([[70, 80, 90],
                   [60, 85, 95],
                   [75, 65, 80]])

wrong = square - square.mean(axis=1)                   # runs, but is wrong
right = square - square.mean(axis=1, keepdims=True)

print("wrong: row sums =", wrong.sum(axis=1).round(2))
print("right: row sums =", right.sum(axis=1).round(2))
```

After subtracting its own average, every row must add up to 0. Only the second result passes that test. When you subtract or divide by a per-row value, use `keepdims=True` as a habit, and check the result with a property you know must hold.

### A.4 · Broadcasting in practice

Centring each **column** on its mean needs no reshaping, because per-column values already line up with the last dimension.

```python run
import numpy as np

scores = np.array([[70, 80, 90],
                   [60, 85, 95],
                   [75, 65, 80]])

centred = scores - scores.mean(axis=0)
print(centred.round(2))
print("column means now:", centred.mean(axis=0).round(10))
```

:::exercise id=a1 title="Each exam as a share of the student's total"
Complete `row_shares(x)` so that every value is divided by the total of **its own row**. Each row of the result must add up to 1. Do not use a loop.

```python
import numpy as np

def row_shares(x):
    totals = ...          # one total per row, in a shape that broadcasts
    return x / totals

demo = np.array([[10, 30, 60],
                 [25, 25, 50]])
print(row_shares(demo))
```

```python check
import numpy as np
x = np.array([[10., 30., 60.], [25., 25., 50.], [1., 1., 2.]])
r = row_shares(x)
assert isinstance(r, np.ndarray) and r.shape == (3, 3), "the result must be a 3x3 array for a 3x3 input"
assert np.allclose(r.sum(axis=1), 1), "every row must add up to 1 (did you divide by column totals?)"
assert np.allclose(r[0], [0.1, 0.3, 0.6]), "first row should be [0.1, 0.3, 0.6]"
assert row_shares(np.ones((2, 5))).shape == (2, 5), "it must also work for a table that is not square"
```
:::

**Read more:** [Computation on Arrays: Broadcasting](https://jakevdp.github.io/PythonDataScienceHandbook/02.05-computation-on-arrays-broadcasting.html) in the textbook's free online edition.

## B · Pandas: grouping 📘

### B.1 · One number for the whole table

An **aggregation** reduces many values to one summary value. On a whole column it gives a single number.

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "AI", "DS", "CS", "AI"],
    "gpa":   [3.0, 2.0, 3.5, 4.0, 3.0, 2.5],
})

print("mean GPA of everyone:", df["gpa"].mean())
```

That answers "what is the average GPA?" The more useful question is usually "what is the average GPA **in each major**?"

### B.2 · Split, apply, combine

Answering the per-major question takes three steps. **Split** the table into one piece per major. **Apply** the function to each piece. **Combine** the results into one new table.

![A table of majors and GPAs is split into three small tables, the mean of each is computed, and the three means are combined into a result table.](figures/split-apply-combine.svg)

<p class="caption">The same six rows as the code below. Pandas does all three steps in one line.</p>

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "AI", "DS", "CS", "AI"],
    "gpa":   [3.0, 2.0, 3.5, 4.0, 3.0, 2.5],
})

print(df.groupby("major")["gpa"].mean())
```

To see what `groupby` saves you, here are the same three steps written by hand.

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "AI", "DS", "CS", "AI"],
    "gpa":   [3.0, 2.0, 3.5, 4.0, 3.0, 2.5],
})

result = {}
for m in df["major"].unique():
    piece = df[df["major"] == m]          # split
    result[m] = piece["gpa"].mean()       # apply
print(result)                             # combine
```

### B.3 · Four things to do with a group

`groupby` on its own computes nothing; it only records how to split. What happens next depends on the method you call. The textbook covers four, and they differ in **how many rows come back**.

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "AI", "DS", "CS", "AI"],
    "gpa":   [3.0, 2.0, 3.5, 4.0, 3.0, 2.5],
})
groups = df.groupby("major")

# 1. aggregate: one row per group
print(groups["gpa"].agg(["min", "mean", "max"]))

# 2. filter: keep only the majors whose mean GPA is at least 3.0
print(groups.filter(lambda g: g["gpa"].mean() >= 3.0))

# 3. transform: the group's mean, repeated on every row of that group
df["major_mean"] = groups["gpa"].transform("mean")
print(df)

# 4. apply: any function of your own (here, the gap between best and worst)
print(groups["gpa"].apply(lambda s: s.max() - s.min()))
```

:::challenge title="How many rows come back?"
The table has **6 rows** and **3 majors**. Without running anything, say how many rows each result has.

1. `df.groupby("major")["gpa"].agg("mean")`
2. `df.groupby("major")["gpa"].transform("mean")`
3. `df.groupby("major").filter(lambda g: g["gpa"].mean() >= 3.0)`
---
1. **3 rows**, one per major. Aggregation always reduces each group to one row.
2. **6 rows**, the same as the original table. That is the point of `transform`: the result lines up with the table, so it can be stored as a new column.
3. **4 rows.** The means are DS 3.5, AI 3.0 and CS 2.5, so the two CS rows are dropped and the other four are kept unchanged. `filter` removes whole groups, never single rows.
:::

> **Look out.**
> - **Missing keys disappear.** Rows whose group key is missing (`NaN`) are left out of every group by default. Pass `dropna=False` to `groupby` to keep them as a group of their own.
> - **Choose the column before you aggregate.** `df.groupby("major").mean()` tries to average *every* other column and raises an error if one of them holds text. Write `df.groupby("major")["gpa"].mean()`, or pass `numeric_only=True`.
> - **The group labels become the index.** To get them back as an ordinary column, add `.reset_index()` to the result.

:::exercise id=b1 title="Students above their own major's average"
Complete `above_major_mean(df)` so that it returns only the rows whose `gpa` is **higher than the mean GPA of the same major**. Return the original columns, and do not use a loop.

Hint: you need a value per row to compare with, so think about which of the four methods returns as many rows as the table.

```python
import pandas as pd

def above_major_mean(df):
    major_mean = ...      # the mean of each row's own major, one value per row
    return df[df["gpa"] > major_mean]

demo = pd.DataFrame({
    "major": ["DS", "CS", "AI", "DS", "CS", "AI"],
    "gpa":   [3.0, 2.0, 3.5, 4.0, 3.0, 2.5],
})
print(above_major_mean(demo))
```

```python check
import pandas as pd
t = pd.DataFrame({"name": list("abcdefg"),
                  "major": ["DS", "CS", "AI", "DS", "CS", "AI", "DS"],
                  "gpa": [3.0, 2.0, 3.5, 4.0, 3.0, 2.5, 2.0]})
out = above_major_mean(t.copy())
assert isinstance(out, pd.DataFrame), "return a DataFrame"
assert sorted(out["name"]) == ["c", "d", "e"], f"expected students c, d and e, got {sorted(out['name'])}"
assert list(out.columns) == ["name", "major", "gpa"], "return the original columns only"
```
:::

**Read more:** [Aggregation and Grouping](https://jakevdp.github.io/PythonDataScienceHandbook/03.08-aggregation-and-grouping.html) in the textbook's free online edition.

## Summary

- Broadcasting compares shapes from the right: pad with 1s on the left, stretch the 1s, and fail if two sizes differ and neither is 1.
- For per-row values, use `keepdims=True` so the result has shape `(n, 1)`; a square table hides this mistake.
- `groupby` splits; the method you call next decides the result: `agg` gives one row per group, `transform` gives one row per original row, `filter` keeps or drops whole groups, and `apply` runs any function.

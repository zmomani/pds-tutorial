# NumPy — Arrays and Vectorised Computation

<p class="lesson-intro">Week 3 · Programming for Data Science (606315)</p>

NumPy gives Python a fast, compact container for numbers: the **array**. Pandas, Scikit-learn and Matplotlib are all built on it, so what you learn this week is used in every later week.

> **About this lesson.** It follows the order of Chapter 2 of the course textbook, Jake VanderPlas, *Python Data Science Handbook* (2nd ed., O'Reilly). The explanations, examples and diagrams are written for this course; each section ends with a "Read more" link to the matching section of the textbook's free online edition.
>
> **Helper notes.** Words in the code with a dotted underline have a short note. Hover over one (or tap it) to read what it does. Every example starts with its own `import` so that it runs on its own.

## 1 · Lists and arrays

### 1.1 · Why a list is not enough

A Python list can hold anything: numbers, text, other lists. That freedom has a price. Each item is a separate Python object that the list only points to, so a list of a million numbers is slow to compute with and uses a lot of memory.

A NumPy array makes the opposite choice. Every element has the **same type**, and the values sit side by side in one block of memory. That is less flexible and much faster.

```python run
import numpy as np

mixed = [1, "two", 3.0]            # a list accepts mixed types
print(mixed)

a = np.array([1, 2, 3])            # an array has one type for all elements
print(a, a.dtype)
```

If the values do not share a type, NumPy converts them to one type that can hold them all.

```python run
import numpy as np

print(np.array([1, 2, 3.5]))             # the integers become floats
print(np.array([1, 2, 3], dtype=float))  # or choose the type yourself
```

:::challenge title="What type do you get?"
Predict the `dtype` of each array before you run the code.

1. `np.array([1, 2, 3])`
2. `np.array([1, 2, 3.5])`
3. `np.array([1, 2, "3"])`
4. `np.array([True, False, 2])`

```python run
import numpy as np

for values in ([1, 2, 3], [1, 2, 3.5], [1, 2, "3"], [True, False, 2]):
    print(values, "->", np.array(values).dtype)
```
---
1. An integer type (shown as `int64` on most machines).
2. `float64`. One float is enough to turn every element into a float.
3. A text type (shown as `<U…`). The numbers were converted to text, so `a + 1` no longer works. This happens silently when a number arrives as a string, which is common when reading files.
4. An integer type. `True` and `False` become 1 and 0.
:::

### 1.2 · Creating arrays

Arrays are rarely typed in by hand. NumPy has functions that build them.

```python run
import numpy as np

print(np.zeros(5))                 # five zeros
print(np.ones((2, 3)))             # 2 rows, 3 columns of ones
print(np.full((2, 2), 7))          # filled with a value you choose
print(np.arange(0, 10, 2))         # start, stop (not included), step
print(np.linspace(0, 1, 5))        # 5 evenly spaced values, both ends included
print(np.eye(3))                   # identity matrix
```

> **Look out.** The shape of a 2-D array is given as one tuple, so the inner brackets are required: `np.ones((2, 3))`, not `np.ones(2, 3)`. Also note that `np.arange` leaves the stop value out, while `np.linspace` includes it.

:::exercise id=n1 title="The first n even numbers"
Complete `evens(n)` so that it returns an integer array with the first `n` even numbers, starting from 0. For example, `evens(4)` is `[0 2 4 6]`. Do not use a loop.

```python
import numpy as np

def evens(n):
    return ...

print(evens(4))
```

```python check
import numpy as np
r = evens(4)
assert isinstance(r, np.ndarray), "return a NumPy array, not a list"
assert r.tolist() == [0, 2, 4, 6], f"evens(4) should be [0 2 4 6], got {r}"
assert evens(1).tolist() == [0] and len(evens(50)) == 50 and evens(50)[-1] == 98, "check the stop value"
assert r.dtype.kind == "i", "the array should hold integers"
```
:::

**Read more:** [Understanding Data Types in Python](https://jakevdp.github.io/PythonDataScienceHandbook/02.01-understanding-data-types.html)

## 2 · The basics of arrays

### 2.1 · Attributes

Every array can describe itself.

```python run
import numpy as np

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])     # 3 students x 4 exams

print("ndim :", scores.ndim)     # number of dimensions
print("shape:", scores.shape)    # size along each dimension
print("size :", scores.size)     # total number of elements
print("dtype:", scores.dtype)    # type of every element
```

### 2.2 · Indexing one element

Counting starts at 0, and negative numbers count from the end, as with lists. In a 2-D array, give the row and the column separated by a comma.

```python run
import numpy as np

a = np.array([10, 20, 30, 40, 50])
print(a[0], a[-1])

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])
print(scores[1, 2])        # row 1, column 2
scores[0, 0] = 99          # elements can be changed
print(scores[0])
```

> **Look out.** An array keeps its type. Storing `3.9` in an integer array stores `3`, with no warning.

### 2.3 · Slicing

A slice `start:stop:step` selects a range. Any of the three parts can be left out.

```python run
import numpy as np

a = np.arange(10)
print(a[:4])        # first four
print(a[6:])        # from index 6 to the end
print(a[::2])       # every second element
print(a[::-1])      # reversed

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])
print(scores[:2, :3])    # first 2 rows, first 3 columns
print(scores[:, 0])      # the whole first column
print(scores[1, :])      # the whole second row
```

### 2.4 · A slice is a view, not a copy

This is the most important difference from lists. A slice of an array does **not** copy the data; it is a window onto the same memory. Changing the slice changes the original.

```python run
import numpy as np

a = np.arange(6)
part = a[:3]         # a view
part[0] = 100
print("a after changing the view:", a)

b = np.arange(6)
safe = b[:3].copy()  # an independent copy
safe[0] = 100
print("b after changing the copy:", b)
```

:::challenge title="View or copy?"
What does this code print? Decide first, then run it.

```python run
import numpy as np

grid = np.zeros((3, 3), dtype=int)
row = grid[1]
row[:] = 5
col = grid[:, 0].copy()
col[:] = 9
print(grid)
```
---
The middle row becomes 5s, and nothing becomes 9.

`grid[1]` is a view, so `row[:] = 5` writes into `grid`. `grid[:, 0].copy()` is an independent copy, so filling it with 9 leaves `grid` alone.

Note `row[:] = 5`, not `row = 5`. The second form would only make the name `row` point at the number 5 and would change no array.
:::

### 2.5 · Reshaping

`reshape` arranges the same values in a new shape. The total number of elements must not change.

```python run
import numpy as np

a = np.arange(12)
print(a.reshape(3, 4))
print(a.reshape(2, -1))            # -1 means "work this size out for me"

row = np.array([1, 2, 3])
print(row[np.newaxis, :].shape)    # (1, 3): one row
print(row[:, np.newaxis].shape)    # (3, 1): one column
```

### 2.6 · Joining and splitting

```python run
import numpy as np

x = np.array([1, 2, 3])
y = np.array([4, 5, 6])
print(np.concatenate([x, y]))      # end to end
print(np.vstack([x, y]))           # stacked as rows
print(np.hstack([x, y]))           # side by side

big = np.arange(10)
first, middle, last = np.split(big, [3, 7])    # cut before index 3 and before index 7
print(first, middle, last)
```

:::exercise id=n2 title="The inside of a table"
Complete `inside(table)` so that it returns the table **without** its first and last row and its first and last column. The result must be an independent copy: changing it must not change `table`.

```python
import numpy as np

def inside(table):
    return ...

demo = np.arange(20).reshape(4, 5)
print(demo)
print(inside(demo))
```

```python check
import numpy as np
t = np.arange(20).reshape(4, 5)
r = inside(t)
assert isinstance(r, np.ndarray) and r.shape == (2, 3), "a 4x5 table should give a 2x3 result"
assert r.tolist() == [[6, 7, 8], [11, 12, 13]], f"wrong values: {r.tolist()}"
r[0, 0] = -1
assert t[1, 1] == 6, "changing the result changed the original: return a copy, not a view"
```
:::

**Read more:** [The Basics of NumPy Arrays](https://jakevdp.github.io/PythonDataScienceHandbook/02.02-the-basics-of-numpy-arrays.html)

## 3 · Computing on arrays: universal functions

### 3.1 · Loops are slow

Python checks the type of every value each time it goes round a loop. On a large array that overhead dominates. NumPy's answer is the **universal function**, or **ufunc**: an operation that is applied to every element inside fast compiled code. Writing code this way is called **vectorising**.

```python run
import numpy as np, time

n = 300_000
values = np.arange(1, n + 1)

t0 = time.perf_counter()
out = np.empty(n)
for i in range(n):                 # one element at a time
    out[i] = 1.0 / values[i]
t_loop = time.perf_counter() - t0

t0 = time.perf_counter()
out2 = 1.0 / values                # the whole array at once
t_vec = time.perf_counter() - t0

print(f"loop      : {t_loop * 1000:8.1f} ms")
print(f"vectorised: {t_vec * 1000:8.1f} ms")
print("same result:", np.allclose(out, out2))
```

The exact times change from run to run, but the vectorised line is typically tens to hundreds of times faster. The rule for the rest of the course: **if you are writing a `for` loop over the elements of an array, look for an array operation instead.**

### 3.2 · Arithmetic and mathematical functions

The ordinary operators work element by element, and each one is a ufunc.

```python run
import numpy as np

x = np.arange(5)
print("x      =", x)
print("x + 5  =", x + 5)
print("x * 2  =", x * 2)
print("x / 2  =", x / 2)
print("x // 2 =", x // 2)      # floor division
print("x ** 2 =", x ** 2)
print("x % 2  =", x % 2)       # remainder

y = np.array([-2.5, 0.0, 2.5])
print(np.abs(y), np.sqrt(np.abs(y)), np.exp(y).round(2))
```

Two arrays of the same shape are combined element by element.

```python run
import numpy as np

midterm = np.array([70, 55, 90])
final = np.array([80, 65, 70])
print(0.4 * midterm + 0.6 * final)
```

### 3.3 · Three extras: reduce, accumulate, outer

Every two-input ufunc, such as `np.add`, comes with methods that are occasionally very handy.

```python run
import numpy as np

x = np.arange(1, 6)
print(np.add.reduce(x))            # 1+2+3+4+5, collapsed to one value
print(np.add.accumulate(x))        # running total
print(np.multiply.outer(x, x))     # every pair: a multiplication table
```

In practice you will usually write `x.sum()` and `x.cumsum()`, which do the same as the first two lines.

:::exercise id=n3 title="Rescale to the range 0 to 1"
Complete `rescale(x)` so that the smallest value of `x` becomes 0, the largest becomes 1, and the others are spaced in proportion. For example, `[10, 15, 20]` becomes `[0, 0.5, 1]`. Do not use a loop.

```python
import numpy as np

def rescale(x):
    return ...

print(rescale(np.array([10, 15, 20])))
```

```python check
import numpy as np
r = rescale(np.array([10, 15, 20]))
assert isinstance(r, np.ndarray), "return a NumPy array"
assert np.allclose(r, [0, 0.5, 1]), f"[10, 15, 20] should give [0, 0.5, 1], got {r}"
r2 = rescale(np.array([3.0, -1.0, 7.0, 1.0]))
assert np.isclose(r2.min(), 0) and np.isclose(r2.max(), 1), "the smallest must become 0 and the largest 1"
assert np.allclose(r2, [0.5, 0, 1, 0.25]), "values in between must keep their proportions"
```
:::

**Read more:** [Computation on NumPy Arrays: Universal Functions](https://jakevdp.github.io/PythonDataScienceHandbook/02.03-computation-on-arrays-ufuncs.html)

## 4 · Aggregations: min, max and everything in between

### 4.1 · Summarising a whole array

An **aggregation** reduces many values to one. NumPy's versions are much faster than Python's built-in `sum`, `min` and `max`, and they understand more than one dimension.

```python run
import numpy as np

x = np.array([70, 80, 90, 60, 85])
print("sum :", x.sum())
print("mean:", x.mean())
print("min :", x.min(), " max:", x.max())
print("std :", x.std().round(2))
print("position of the max:", x.argmax())
```

### 4.2 · Along one dimension: `axis`

For a table you usually want one result per column or one per row. The `axis` argument names the dimension that is **collapsed**.

![A table of scores. With axis 0 the rows are collapsed and there is one result per column. With axis 1 the columns are collapsed and there is one result per row.](figures/axis.svg)

<p class="caption"><code>axis=0</code> works down the rows and leaves one value per column. <code>axis=1</code> works across the columns and leaves one value per row.</p>

```python run
import numpy as np

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])     # 3 students x 4 exams

print("everything :", scores.sum())
print("per exam   :", scores.mean(axis=0).round(1))    # 4 values
print("per student:", scores.mean(axis=1).round(1))    # 3 values
```

:::challenge title="What shape comes back?"
`scores` has shape `(3, 4)`. What is the shape of each result?

1. `scores.max()`
2. `scores.max(axis=0)`
3. `scores.max(axis=1)`
---
1. A single number, with no shape to speak of.
2. `(4,)`. The 3 rows were collapsed, so one value per column remains.
3. `(3,)`. The 4 columns were collapsed, so one value per row remains.

A useful check: the dimension you name in `axis` is the one that **disappears** from the shape.
:::

### 4.3 · Missing values

`np.nan` marks a missing number. Any ordinary aggregation that meets a `nan` returns `nan`. The versions whose names start with `nan` skip the missing values.

```python run
import numpy as np

x = np.array([70, np.nan, 90, 60])
print(x.mean())            # nan
print(np.nanmean(x))       # the mean of the three known values
print(np.nanmax(x), np.nansum(x))
```

| Function | What it gives | Skips `nan` |
|---|---|---|
| `np.sum`, `np.prod` | total, product | `np.nansum`, `np.nanprod` |
| `np.mean`, `np.median` | average, middle value | `np.nanmean`, `np.nanmedian` |
| `np.std`, `np.var` | spread | `np.nanstd`, `np.nanvar` |
| `np.min`, `np.max` | smallest, largest | `np.nanmin`, `np.nanmax` |
| `np.argmin`, `np.argmax` | position of smallest, largest | `np.nanargmin`, `np.nanargmax` |
| `np.percentile` | value below which a given % falls | `np.nanpercentile` |
| `np.any`, `np.all` | is any, are all elements true | not applicable |

:::exercise id=n4 title="The hardest exam"
Each row of `scores` is a student and each column is an exam. Complete `hardest_exam(scores)` so that it returns the **column number** of the exam with the lowest average score.

```python
import numpy as np

def hardest_exam(scores):
    return ...

demo = np.array([[70, 80, 90, 60],
                 [60, 85, 95, 80],
                 [75, 65, 80, 100]])
print(hardest_exam(demo))
```

```python check
import numpy as np
d = np.array([[70, 80, 90, 60], [60, 85, 95, 80], [75, 65, 80, 100]])
assert hardest_exam(d) == 0, f"exam 0 has the lowest average here, got {hardest_exam(d)}"
d2 = np.array([[90, 10, 90], [90, 100, 20], [90, 100, 30], [90, 100, 40]])
assert hardest_exam(d2) == 2, "average the columns (axis=0), then find the position of the smallest"
```
:::

**Read more:** [Aggregations: Min, Max, and Everything In Between](https://jakevdp.github.io/PythonDataScienceHandbook/02.04-computation-on-arrays-aggregates.html)

## 5 · Broadcasting

### 5.1 · The idea

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

### 5.2 · The three rules

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

### 5.3 · When it fails, and how to fix it

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

### 5.4 · Broadcasting in practice

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

:::exercise id=n5 title="Each exam as a share of the student's total"
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

**Read more:** [Computation on Arrays: Broadcasting](https://jakevdp.github.io/PythonDataScienceHandbook/02.05-computation-on-arrays-broadcasting.html)

## 6 · Comparisons, masks and Boolean logic

### 6.1 · Comparing gives an array of True and False

The comparison operators are ufuncs too. The result has the same shape as the input and holds `True` or `False` for each element.

```python run
import numpy as np

x = np.array([55, 82, 47, 91, 68])
print(x > 60)
print(x == 47)
print(x != 47)
```

### 6.2 · Counting and testing

`True` counts as 1 and `False` as 0, so adding up a Boolean array **counts** the elements that pass the test.

```python run
import numpy as np

x = np.array([55, 82, 47, 91, 68])
print("how many above 60 :", np.sum(x > 60))
print("share above 60    :", np.mean(x > 60))
print("is any above 90?  :", np.any(x > 90))
print("are all above 50? :", np.all(x > 50))
```

### 6.3 · Combining conditions

Use `&` for "and", `|` for "or" and `~` for "not". Each condition **must** be wrapped in brackets.

```python run
import numpy as np

x = np.array([55, 82, 47, 91, 68])
print((x > 50) & (x < 85))     # both conditions
print((x < 50) | (x > 90))     # either condition
print(~(x > 60))               # the opposite
```

> **Look out.** The words `and` and `or` do not work on arrays. They ask "is this whole array true or false?", which has no single answer, so Python raises `ValueError: The truth value of an array … is ambiguous`. Leaving out the brackets is a second trap: `x > 50 & x < 85` is read as `x > (50 & x) < 85`, because `&` is applied before the comparisons.

### 6.4 · Masking: keeping the elements that pass

Put a Boolean array inside the square brackets and you get back only the elements where it is `True`. The Boolean array is called a **mask**.

![A row of five scores, a row of True and False values for the test "greater than 60", and the three scores that are kept.](figures/mask.svg)

<p class="caption">The mask has one True or False per element. Only the elements under a True survive.</p>

```python run
import numpy as np

x = np.array([55, 82, 47, 91, 68])
passed = x[x > 60]
print(passed)
print("average of those who passed:", passed.mean().round(2))

x[x < 50] = 50          # a mask can also choose which elements to change
print(x)
```

:::challenge title="Find the bug"
This line is meant to count the scores from 60 to 80. It raises an error. Why, and what is the corrected line?

```python
count = np.sum(x >= 60 and x <= 80)
```
---
`and` cannot combine two arrays. Use `&`, and put each comparison in brackets:

```python
count = np.sum((x >= 60) & (x <= 80))
```
:::

:::exercise id=n6 title="How many are in range?"
Complete `count_between(x, low, high)` so that it returns how many elements of `x` are **at least** `low` and **at most** `high`. Do not use a loop.

```python
import numpy as np

def count_between(x, low, high):
    return ...

print(count_between(np.array([55, 82, 47, 91, 68]), 50, 85))
```

```python check
import numpy as np
x = np.array([55, 82, 47, 91, 68])
assert count_between(x, 50, 85) == 3, f"three values are between 50 and 85, got {count_between(x, 50, 85)}"
assert count_between(x, 47, 47) == 1, "both ends are included"
assert count_between(x, 0, 10) == 0 and count_between(np.arange(100), 10, 19) == 10
```
:::

**Read more:** [Comparisons, Masks, and Boolean Logic](https://jakevdp.github.io/PythonDataScienceHandbook/02.06-boolean-arrays-and-masks.html)

## 7 · Fancy indexing

### 7.1 · Indexing with a list of positions

So far the square brackets have held a number, a slice or a mask. They can also hold a **list or array of positions**. This is called fancy indexing, and it returns the elements at those positions, in the order you ask for them.

```python run
import numpy as np

x = np.array([55, 82, 47, 91, 68])
print(x[[0, 3]])            # elements 0 and 3
print(x[[4, 4, 0]])         # any order, and repeats are allowed

order = np.array([3, 1, 4, 0, 2])
print(x[order])             # rearranged
```

For a table, one list picks whole rows. Two lists are read as pairs: the first row number with the first column number, and so on.

```python run
import numpy as np

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])

print(scores[[2, 0]])                # rows 2 and 0
print(scores[:, [0, 3]])             # columns 0 and 3
print(scores[[0, 1, 2], [3, 2, 0]])  # (0,3), (1,2), (2,0)
```

### 7.2 · Changing values

Fancy indexing can also be used on the left of `=`.

```python run
import numpy as np

x = np.zeros(6, dtype=int)
x[[1, 4]] = 99
print(x)
```

> **Look out.** Unlike a slice, fancy indexing returns a **copy**. Also, repeated positions do not accumulate: `x[[0, 0, 0]] += 1` adds 1 once, not three times. To add at repeated positions use `np.add.at(x, [0, 0, 0], 1)`.

**Read more:** [Fancy Indexing](https://jakevdp.github.io/PythonDataScienceHandbook/02.07-fancy-indexing.html)

## 8 · Sorting

### 8.1 · `sort` and `argsort`

`np.sort` returns a sorted copy. `np.argsort` returns the **positions** that would sort the array, which is more useful than it sounds: the same positions can reorder a second array.

```python run
import numpy as np

totals = np.array([310, 275, 340, 290])
names = np.array(["Ahmad", "Sara", "Omar", "Lina"])

print(np.sort(totals))
order = np.argsort(totals)
print(order)                 # positions, smallest total first
print(names[order])          # names in order of their totals
print(names[order][::-1])    # highest first
```

> **Look out.** `np.sort(x)` leaves `x` alone and returns a new array. `x.sort()` sorts `x` itself and returns `None`, so `x = x.sort()` destroys your data.

### 8.2 · Sorting rows or columns, and partial sorts

```python run
import numpy as np

scores = np.array([[70, 80, 90, 60],
                   [60, 85, 95, 80],
                   [75, 65, 80, 100]])

print(np.sort(scores, axis=1))     # each row sorted on its own
print(np.sort(scores, axis=0))     # each column sorted on its own

x = np.array([7, 2, 9, 1, 8, 3])
print(np.partition(x, 2)[:2])      # the two smallest, without sorting everything
```

Sorting each row or column on its own breaks the link between the values in a row. It is right for "each student's best scores" and wrong for "sort the students".

:::exercise id=n7 title="Rank the students"
`names` and `totals` are arrays of the same length. Complete `ranking(names, totals)` so that it returns the names ordered from the **highest** total to the lowest.

```python
import numpy as np

def ranking(names, totals):
    order = ...           # positions that sort the totals
    return ...

n = np.array(["Ahmad", "Sara", "Omar", "Lina"])
t = np.array([310, 275, 340, 290])
print(ranking(n, t))
```

```python check
import numpy as np
n = np.array(["Ahmad", "Sara", "Omar", "Lina"])
t = np.array([310, 275, 340, 290])
r = ranking(n, t)
assert r is not None and list(r) == ["Omar", "Ahmad", "Lina", "Sara"], f"expected Omar, Ahmad, Lina, Sara; got {r}"
assert list(ranking(np.array(["a", "b"]), np.array([1, 2]))) == ["b", "a"], "highest total first"
assert list(n) == ["Ahmad", "Sara", "Omar", "Lina"], "do not change the original names array"
```
:::

**Read more:** [Sorting Arrays](https://jakevdp.github.io/PythonDataScienceHandbook/02.08-sorting.html)

## 9 · Structured arrays

An array has one type, so names, ages and GPAs would need three separate arrays that you must keep in step yourself. A **structured array** gives each element several named fields.

```python run
import numpy as np

students = np.zeros(3, dtype=[("name", "U10"), ("year", "i4"), ("gpa", "f8")])
students["name"] = ["Ahmad", "Sara", "Omar"]
students["year"] = [2, 4, 1]
students["gpa"] = [3.4, 2.1, 3.9]

print(students)
print(students["name"])                         # one field
print(students[students["gpa"] > 3]["name"])    # a mask on one field, another field returned
```

This works, but it is awkward. Tables with named, differently typed columns are exactly what **Pandas** is for, and that is next week's topic. Treat this section as the bridge between the two libraries.

**Read more:** [Structured Data: NumPy's Structured Arrays](https://jakevdp.github.io/PythonDataScienceHandbook/02.09-structured-data-numpy.html)

## 10 · Also in the syllabus: random numbers and linear algebra

The textbook chapter does not give these two topics a section of their own, but the course syllabus lists both, so here are the essentials.

### 10.1 · Random numbers

Create a generator once and draw from it. Giving it a **seed** makes the "random" numbers the same on every run, which you need whenever results must be reproducible.

```python run
import numpy as np

rng = np.random.default_rng(42)            # 42 is the seed

print(rng.integers(1, 7, size=5))          # five dice rolls (7 is not included)
print(rng.random(3).round(3))              # floats from 0 up to 1
print(rng.normal(70, 10, size=4).round(1)) # bell curve: mean 70, spread 10
print(rng.choice(["DS", "CS", "AI"], size=4))

deck = np.arange(5)
rng.shuffle(deck)                          # shuffles in place
print(deck)
```

### 10.2 · Linear algebra

`*` multiplies element by element. **Matrix** multiplication is written `@`.

```python run
import numpy as np

A = np.array([[2, 1],
              [1, 3]])
B = np.array([[1, 0],
              [2, 1]])

print(A * B)          # element by element
print(A @ B)          # matrix product
print(A.T)            # transpose
print(np.linalg.det(A).round(2))
print(np.linalg.inv(A).round(2))
```

Solving a system of equations is one call. For `2x + y = 5` and `x + 3y = 10`:

```python run
import numpy as np

A = np.array([[2, 1],
              [1, 3]])
b = np.array([5, 10])

solution = np.linalg.solve(A, b)
print(solution)                 # x, y
print(A @ solution)             # check: gives back b
```

> **Look out.** Prefer `np.linalg.solve(A, b)` to `np.linalg.inv(A) @ b`. It is faster and more accurate.

## Summary

- An array holds values of **one type** in one block of memory. That is why it is fast.
- A **slice is a view**: changing it changes the original. Use `.copy()` when you need independence. Masks and fancy indexing return copies.
- Replace element-by-element loops with **vectorised** operations (ufuncs).
- `axis` names the dimension that is collapsed: `axis=0` gives one result per column, `axis=1` one per row.
- **Broadcasting** compares shapes from the right: pad with 1s on the left, stretch the 1s, fail otherwise. Use `keepdims=True` for per-row values.
- A **mask** selects by condition; combine conditions with `&`, `|`, `~` and brackets, never `and` / `or`.
- `argsort` gives positions, which can reorder other arrays.

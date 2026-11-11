# NumPy — Arrays and Vectorised Computation

<p class="lesson-intro">Week 3 · Programming for Data Science (606315)</p>

Pure-Python lists are flexible but slow and memory-hungry. NumPy's `ndarray` stores numbers in one contiguous block of typed memory and runs loops in C. Pandas, Scikit-learn and Matplotlib are all built on it, so the mental model you build here carries through the rest of the course.

> **🟢 Study these for the exams.** A green light next to a heading means that part follows the lecture slides: its examples are the slides' own, with extra explanation added, and the light covers everything under that heading. Anything without a green light is extra practice and background — useful, but not what the exams are built on. (Each example starts with `import numpy as np` so that it runs on its own.)

## 1 · Introduction: why NumPy

### 1.1 · What is NumPy? 🟢

**NumPy** (Numerical Python) is a free, open-source library created by Travis Oliphant in 2005. It provides a powerful N-dimensional array object, the `ndarray`, and a collection of routines for fast operations on arrays: math, logic, shape manipulation, sorting, input/output and more.

The core of NumPy is the `ndarray`: a **fixed-size, homogeneous** (all elements the same type) array stored in **contiguous memory**. This makes it far more efficient for numerical work than Python's built-in list. Its key capabilities are linear algebra, Fourier transforms, matrix computations, random number generation, **broadcasting** (automatic shape matching) and **universal functions** (ufuncs).

```python run
import numpy as np
print("NumPy version:", np.__version__)
```

Always import NumPy as `np`; this is the universal convention in data science. (The version you see depends on the installation; the slides show 1.26.4.)

**NumPy arrays vs Python lists**

| Feature | Python List | NumPy Array |
|---|---|---|
| Data Types | Mixed (heterogeneous) | Single type (homogeneous) |
| Speed | Slow — stores object pointers | Up to 50x faster — contiguous memory |
| Memory | Higher overhead per element | Compact, efficient storage |
| Operations | No built-in vectorization | Full vectorized element-wise ops |
| Broadcasting | Not supported | Automatic shape matching |
| Functions | Basic: append, sort, reverse | 1000+ math, stats, linalg, FFT |

**How does contiguous memory help?** A Python list stores one pointer per element, and the objects they point to are scattered in memory, so the CPU must jump around to find the values (cache misses, slow). A NumPy array stores all values side by side, so the CPU reads them in sequence (cache-friendly, fast). This is why NumPy can be 10–100x faster for numerical operations.

```python run
import numpy as np

# Example: element-wise multiply
py_list = list(range(1000000))
np_arr = np.arange(1000000)

# Python: [x*2 for x in py_list]  → ~120ms
# NumPy:  np_arr * 2              → ~2ms
print(np_arr * 2)
```

**Rule of thumb:** if you are doing math on sequences of numbers, use NumPy instead of Python lists. The timings in the comments are typical figures, not guarantees; the next subsection measures them on your own machine.

### 1.2 · More on why NumPy: measuring it yourself

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

The ratio changes from run to run and from machine to machine; it is largest for simple arithmetic on big arrays. A list also costs more memory, because each element is a separate Python object that the list refers to:

```python run
import sys
import numpy as np

n = 1_000_000
lst = list(range(n))
arr = np.arange(n)

list_bytes = sys.getsizeof(lst) + sum(sys.getsizeof(x) for x in lst)
print("list :", list_bytes // 1_000_000, "MB")   # roughly 32-36 MB
print("array:", arr.nbytes // 1_000_000, "MB")   # 4-8 MB, depending on the default integer size
```

## 2 · Creating arrays

### 2.1 · Array dimensions: 0-D to 3-D 🟢

Dimensions are levels of nesting, and each level adds an axis.

| Dimension | Name | Description |
|---|---|---|
| 0-D | Scalar | A single number; no axis, no length |
| 1-D | Vector | A row of numbers; 1 axis (axis 0); like a Python list |
| 2-D | Matrix | Rows and columns; 2 axes; like a spreadsheet |
| 3-D | Tensor | A stack of matrices; 3 axes; used in deep learning |

```python run
import numpy as np
a = np.array(42)                          # 0-D scalar
b = np.array([1, 2, 3, 4, 5])            # 1-D vector
c = np.array([[1, 2, 3], [4, 5, 6]])     # 2-D matrix
d = np.array([[[1,2],[3,4]],              # 3-D tensor
              [[5,6],[7,8]]])
print("0-D ndim:", a.ndim)  # 0
print("1-D ndim:", b.ndim)  # 1
print("2-D ndim:", c.ndim)  # 2
print("3-D ndim:", d.ndim)  # 3
print("Type:", type(b))     # <class 'numpy.ndarray'>
```

`np.array()` converts Python data into an `ndarray`; `.ndim` returns the number of dimensions, and `type()` confirms the object is a `numpy.ndarray`. The nesting depth of the brackets is the number of dimensions: `[1,2,3]` is one level (1-D), `[[1,2],[3,4]]` is two levels (2-D), `[[[1,2],[3,4]]]` is three (3-D). Use `.ndim` to check dimensions, `.shape` for the size of each axis, and `type()` to confirm it is a `numpy.ndarray`.

> **Careful:** `np.array([1, 'hello', 3.14])` upcasts everything to strings, because NumPy arrays must be homogeneous. The list is not changed; the array that NumPy builds from it stores one type for all values. Check `arr.dtype` after creating an array from mixed data.

```python run
import numpy as np
mixed = np.array([1, 'hello', 3.14])
print(mixed)          # ['1' 'hello' '3.14']
print(mixed.dtype)    # a string dtype such as <U32
```

### 2.2 · Built-in array creation functions 🟢

Quick ways to generate arrays without typing the values.

```python run
import numpy as np
zeros = np.zeros((2, 3))        # 2x3 array of 0.0s
ones = np.ones((3, 2))          # 3x2 array of 1.0s
arange = np.arange(0, 10, 2)   # [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5) # 5 values in [0, 1]
eye = np.eye(3)                 # 3x3 identity matrix
full = np.full((2, 3), 7)      # 2x3 array all 7s

print("zeros:", zeros)
print("ones:", ones)
print("arange:", arange)
print("linspace:", linspace)
print("eye:", eye)
print("full:", full)
```

| Function | What it does |
|---|---|
| `np.zeros(shape)` | Array filled with `0.0`; useful for initialising accumulators |
| `np.ones(shape)` | All `1.0`; often used to create masks or scale arrays |
| `np.arange(start, stop, step)` | Like Python's `range()` but returns an `ndarray`; the stop value is **exclusive** |
| `np.linspace(start, stop, n)` | Exactly `n` evenly spaced values; **both endpoints included** |
| `np.eye(n)` | Identity matrix (1s on the diagonal, 0s elsewhere); essential in linear algebra |
| `np.full(shape, value)` | Every element set to the given value |

The shape is a **tuple**: `(2, 3)` means 2 rows and 3 columns. `zeros`, `ones` and `eye` give floats unless you pass `dtype=`. You can also build an array from a tuple and choose its type explicitly:

```python run
import numpy as np
# From tuple with explicit dtype
arr = np.array((10, 20, 30, 40), dtype=float)
print(arr)        # [10. 20. 30. 40.]
print(arr.dtype)  # float64
```

> **Careful:** `np.arange()` with a float step (such as 0.1) can produce unexpected results because of floating-point precision; the number of elements may be one more or one fewer than you expect. Prefer `np.linspace()` for float sequences.

### 2.3 · Practice: creating arrays 🟢

These are the slide's three exercises. Write each one yourself; the slide's own solutions are under the exercise.

:::exercise id=s9 title="Creating arrays (slide 9)"
Create three arrays:

1. `random_arr`: a 4×4 array of random integers between 0 and 100 (`np.random.randint(low, high, size)`; `low` is inclusive, `high` is exclusive).
2. `lin_arr`: 10 evenly spaced numbers from 5 to 50 (`np.linspace`).
3. `arr_tuple`: an array built from the tuple `(10, 20, 30, 40)` with a **float** type.

```python
import numpy as np

# Exercise 1: 4x4 random integers between 0 and 100
random_arr = np.zeros((4, 4), dtype=int)     # replace with np.random.randint(...)
# Exercise 2: 10 evenly spaced numbers from 5 to 50
lin_arr = np.arange(5, 50, 5)                # replace with np.linspace(...)
# Exercise 3: array from tuple with float type
arr_tuple = np.array((10, 20, 30, 40))       # add dtype=...

print(random_arr); print(lin_arr); print(arr_tuple)
print("Shape:", random_arr.shape, "Dtype:", random_arr.dtype)
```

```python check
import numpy as np
assert random_arr.shape == (4, 4) and random_arr.dtype.kind == "i", "random_arr must be a 4x4 integer array"
assert random_arr.min() >= 0 and random_arr.max() < 100, "values must be in [0, 100)"
assert len(np.unique(random_arr)) > 1, "use np.random.randint so that the values are random"
assert lin_arr.shape == (10,) and np.allclose(lin_arr, np.linspace(5, 50, 10)), f"lin_arr should be 10 values from 5 to 50, got {lin_arr}"
assert arr_tuple.dtype == np.float64 and list(arr_tuple) == [10.0, 20.0, 30.0, 40.0], "arr_tuple must be float64"
```
:::

<details>
<summary>Slide solutions and what they mean</summary>

```python
# Exercise 1: 4x4 random integers between 0 and 100
random_arr = np.random.randint(0, 100, size=(4, 4))
print(random_arr)
print("Shape:", random_arr.shape)    # (4, 4)
print("Dtype:", random_arr.dtype)    # int64

# Exercise 2: 10 evenly spaced numbers from 5 to 50
lin_arr = np.linspace(5, 50, 10)
print(lin_arr)
# [ 5.  10.  15.  20.  25.  30.  35.  40.  45.  50.]

# Exercise 3: Array from tuple with float type
arr_tuple = np.array((10, 20, 30, 40), dtype=float)
print(arr_tuple)       # [10. 20. 30. 40.]
print(arr_tuple.dtype) # float64
```

Ex 1: `size=(4,4)` means 4 rows and 4 columns. Ex 2: the spacing is (50 − 5) / (10 − 1) = 5.0, because `linspace` counts the gaps between the 10 points (9 gaps). Ex 3: `dtype=float` forces the integer inputs to become floats, which is why the output has decimal points; the default float is `float64` (64 bits = 8 bytes). The dtype comment says `int64` for the first exercise on a typical 64-bit computer; in the browser it may show `int32`.

</details>

NumPy arrays are homogeneous: all elements share the same dtype, and mixing int and float makes everything float.

### 2.4 · More on creating arrays: printing and checking

The same functions again, with a nested list for a 2-D array and a print setting that keeps the output short.

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

`np.set_printoptions(precision=3, suppress=True)` changes only how arrays are *displayed* (at most 3 decimals, no scientific notation); the stored values are unchanged. It stays in force for the rest of the session. `dtype=int` asks for whole numbers (Python's `int` is translated to NumPy's default integer type).

## 3 · Array indexing

### 3.1 · 1-D indexing: accessing elements 🟢

Use integer indices starting from 0. Negative indices count from the end.

```python run
import numpy as np
arr = np.array([10, 20, 30, 40, 50])

print(arr[0])    # 10   → first element
print(arr[3])    # 40   → fourth element
print(arr[-1])   # 50   → last element
print(arr[-2])   # 40   → second from end
```

```
arr = [10, 20, 30, 40, 50]
         0    1    2    3    4    ← positive index
        -5   -4   -3   -2   -1   ← negative index
```

`arr[0]` is position 0 (the first element), `arr[3]` is position 3 (the fourth element), `arr[-1]` is the last position and `arr[-2]` the second from the end. Negative indexing is a Python convention: `-1` always means the last element.

**Fancy indexing** accesses several elements at once with a list of positions:

```python run
import numpy as np
arr = np.array([10, 20, 30, 40, 50])

# Fancy indexing: access multiple elements at once
indices = [0, 2, 4]
selected = arr[indices]
print(selected)   # [10, 30, 50]  → elements at positions 0, 2, 4
```

> **Careful:** an index outside the array raises `IndexError: index 5 is out of bounds for axis 0 with size 5`. An array of size *n* has valid indices 0 to *n* − 1.

### 3.2 · 2-D indexing: rows and columns 🟢

Access elements with `arr[row, column]`. Use `:` to select an entire row or column. The comma separates the axes: think of it as `arr[which_row, which_column]`.

```python run
import numpy as np
arr_2d = np.array([[10, 20, 30],
                    [40, 50, 60],
                    [70, 80, 90]])

print(arr_2d[0, 1])     # 20  → row 0, col 1
print(arr_2d[2, 2])     # 90  → row 2, col 2
print(arr_2d[1, :])     # [40, 50, 60]  → entire row 1
print(arr_2d[:, 2])     # [30, 60, 90]  → entire col 2
print(arr_2d[1, -1])    # 60  → row 1, last col
```

```
              col 0    col 1    col 2
  row 0:      10        20        30
  row 1:      40        50        60
  row 2:      70        80        90
```

The colon `:` alone means "all" along that axis, so `arr_2d[1, :]` is "all columns in row 1" and `arr_2d[:, 2]` is "all rows in column 2".

**Advanced:** two lists inside the brackets pick specific row–column *pairs*, not a block.

```python run
import numpy as np
arr_2d = np.array([[10, 20, 30],
                    [40, 50, 60],
                    [70, 80, 90]])

# Advanced: access specific row-col pairs
print(arr_2d[[0, 2], [1, 2]])  # [20, 90]
# This selects (row 0, col 1) and (row 2, col 2)
```

The lists are read in parallel: the first list gives the rows `[0, 2]`, the second the columns `[1, 2]`, so the result is the two elements at `(0, 1)` and `(2, 2)`, not the four elements of a 2×2 block.

:::exercise id=s12 title="2-D indexing (slide 12)"
Given `arr_2d`, set the three variables:

1. `first`: the element at row 2, column 0 (expected `70`)
2. `second`: the entire second column (expected `[20 50 80]`)
3. `last`: the last element, using negative indexing (expected `90`)

```python
import numpy as np
arr_2d = np.array([[10, 20, 30],
                   [40, 50, 60],
                   [70, 80, 90]])

first  = arr_2d[0, 0]      # 1. row 2, col 0
second = arr_2d[0, :]      # 2. the entire second column
last   = arr_2d[0, 0]      # 3. the last element, with negative indexing

print(first); print(second); print(last)
```

```python check
import numpy as np
assert first == 70, f"first should be 70, got {first}"
assert list(second) == [20, 50, 80], f"second should be [20 50 80], got {second}"
assert last == 90, f"last should be 90, got {last}"
```
:::

## 4 · Array slicing

### 4.1 · 1-D slicing: `[start:end:step]` 🟢

Extract ranges of elements. The end is **exclusive**. The defaults are start = 0, end = length, step = 1.

```python run
import numpy as np
arr = np.array([10, 20, 30, 40, 50, 60])

print(arr[1:4])    # [20, 30, 40]
print(arr[:3])     # [10, 20, 30]
print(arr[-3:])    # [40, 50, 60]
print(arr[::2])    # [10, 30, 50]
print(arr[::-1])   # [60, 50, 40, 30, 20, 10]
```

```
arr = [10, 20, 30, 40, 50, 60]
         0    1    2    3    4    5
```

- `arr[1:4]` goes from index 1 up to (not including) 4, so indices 1, 2, 3.
- `arr[:3]` goes from the start up to 3, so indices 0, 1, 2.
- `arr[-3:]` goes from the third-last element to the end.
- `arr[::2]` takes every second element: indices 0, 2, 4.
- `arr[::-1]` uses step −1 and reverses the array completely.

**Slicing rules:** `arr[start : end : step]`. `start` is inclusive (default 0), `end` is exclusive (default: length), `step` is the stride between elements (default 1). Negative start/end count from the end, a negative step reverses direction, and omitted values use their defaults.

> Slicing never raises `IndexError`: out-of-range indices are silently clamped to the array bounds. `arr[4:100]` simply returns what exists.

### 4.2 · 2-D slicing: `arr[row_slice, col_slice]` 🟢

Apply slicing independently to rows and columns, separated by a comma. Each side follows the same `start:end:step` rules, and a lone `:` means "everything along this axis".

```python run
import numpy as np
arr_2d = np.array([[1, 2, 3, 4],
                    [5, 6, 7, 8],
                    [9, 10, 11, 12]])

print(arr_2d[0, 1:3])      # [2, 3]
print(arr_2d[0:2, 0:3])    # [[1,2,3], [5,6,7]]
print(arr_2d[:, 1])         # [2, 6, 10]
print(arr_2d[1:, 2:])      # [[7,8], [11,12]]
```

- `arr_2d[0, 1:3]`: row 0, columns 1 to 2 → `[2, 3]`.
- `arr_2d[0:2, 0:3]`: rows 0–1, columns 0–2 → `[[1,2,3], [5,6,7]]`.
- `arr_2d[:, 1]`: all rows, column 1 only → `[2, 6, 10]`.
- `arr_2d[1:, 2:]`: rows from 1 onward, columns from 2 onward → `[[7,8], [11,12]]`.

:::exercise id=s15 title="2-D slicing (slide 15)"
From `arr_2d`, extract with slices:

1. `last_two`: the last two rows
2. `first_cols`: columns 0 and 1 of all rows
3. `every_other`: every other row (rows 0 and 2)

```python
import numpy as np
arr_2d = np.array([[1, 2, 3, 4],
                   [5, 6, 7, 8],
                   [9, 10, 11, 12]])

last_two    = arr_2d          # 1. replace with a slice
first_cols  = arr_2d          # 2. replace with a slice
every_other = arr_2d          # 3. replace with a slice

print(last_two); print(first_cols); print(every_other)
```

```python check
import numpy as np
assert np.array_equal(last_two, [[5, 6, 7, 8], [9, 10, 11, 12]]), f"last_two wrong:\n{last_two}"
assert np.array_equal(first_cols, [[1, 2], [5, 6], [9, 10]]), f"first_cols wrong:\n{first_cols}"
assert np.array_equal(every_other, [[1, 2, 3, 4], [9, 10, 11, 12]]), f"every_other wrong:\n{every_other}"
```
:::

<details>
<summary>Slide answers</summary>

```python
arr_2d[1:, :]    # or arr_2d[-2:]   → the last two rows
arr_2d[:, :2]    #                   → columns 0 and 1 of all rows
arr_2d[::2, :]   #                   → every other row
```

</details>

### 4.3 · Critical: slices create views, not copies 🟢

Modifying a slice changes the original array. This is a common source of bugs.

```python run
import numpy as np
arr = np.array([10, 20, 30, 40, 50, 60])
sub = arr[1:4]          # sub is a VIEW
print("Sub:", sub)       # [20, 30, 40]

sub[0] = 999             # modify the view
print("Sub:", sub)       # [999, 30, 40]
print("Original:", arr)  # [10, 999, 30, 40, 50, 60]
```

When you slice an array, NumPy does **not** copy the data. `sub` is a **view**: it points to the same memory as the original, so `sub[0] = 999` really modifies `arr[1]`, because `sub[0]` *is* `arr[1]`. This is done for performance: copying a large array on every slice would be slow and would waste memory.

The safe approach is `.copy()`, which creates a completely new array with its own memory:

```python run
import numpy as np
# SAFE approach: use .copy()
arr = np.array([10, 20, 30, 40, 50, 60])
sub = arr[1:4].copy()    # independent copy!
sub[0] = 999
print("Sub:", sub)        # [999, 30, 40]
print("Original:", arr)   # [10, 20, 30, 40, 50, 60]
```

This is the #1 NumPy bug for beginners: forgetting that slices share memory. Always ask: "Will I modify this slice?" If yes, use `.copy()`. Use `np.shares_memory(a, b)` to check whether two arrays share the same underlying data.

### 4.4 · More on slicing: views, not copies

The same ideas on a 1-D array and a 3×4 grid.

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

`s[:]` means "every element of `s`", so the assignment overwrites all three cells of the shared block. The copy `c` has its own memory, so writing −1 into it never reaches `x`.

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

Things to look out for: use the comma form `g[1, 2]`, not `g[1][2]` (the second builds an intermediate row first); a single index drops a dimension (`g[1]` has shape `(4,)`, while the slice `g[1:2]` keeps shape `(1, 4)`), which matters later when shapes must match for broadcasting.

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

## 5 · Data types

### 5.1 · NumPy data types (`dtype`) 🟢

Every array has a fixed `dtype`. Check it with `.dtype`; convert with `.astype()`.

| Type code | NumPy type | Description | Size |
|---|---|---|---|
| `'i'` / int32 | `np.int32` | Signed integer | 4 bytes |
| `'f'` / float32 | `np.float32` | Single-precision float | 4 bytes |
| `'d'` / float64 | `np.float64` | Double-precision float | 8 bytes |
| `'?'` / bool | `np.bool_` | True / False | 1 byte |
| `'S'` / bytes | `np.bytes_` | Byte string | Variable |
| `'D'` / complex128 | `np.complex128` | Complex number | 16 bytes |

> The slide's table lists `'f'` as float64 and `'b'` as bool. In NumPy `'f'` means float32 (as the code below shows), `'d'` is float64, `'b'` is a signed byte (`int8`), and bool is `'?'`. The table above uses the correct codes.

```python run
import numpy as np
arr = np.array([1, 2, 3])
print(arr.dtype)              # int64 (default on 64-bit)
arr_f = np.array([1,2,3], dtype='float32')
print(arr_f, arr_f.dtype)     # [1. 2. 3.] float32
# Convert with astype()
newarr = arr.astype('f')      # 'f' = float32
print(newarr, newarr.dtype)   # [1. 2. 3.] float32
arr_bool = np.array([1, 0, 3]).astype(bool)
print(arr_bool)               # [True False True]
```

- `.dtype` shows the current type.
- `.astype(type)` creates a **new** array with the converted type; the original is unchanged.
- `.itemsize` is the number of bytes per element, and `.nbytes` the total bytes used.
- Converting float → int **truncates** the decimals (it does not round).
- Converting int → bool: `0` → `False`, anything else → `True`.

```python run
import numpy as np
x = np.array([1.9, -1.9, 2.5])
print(x.astype(int))            # [ 1 -1  2]  truncated toward zero, not rounded
print(x.dtype, x.itemsize, x.nbytes)   # float64 8 24

try:
    np.array(['a', '2', '3'], dtype='i')
except ValueError as e:
    print("ValueError:", e)     # 'a' cannot be cast to integer
```

> **Careful:** `np.array(['a', '2', '3'], dtype='i')` raises `ValueError` because `'a'` cannot be cast to an integer. Choose the smallest dtype that fits your data: `float32` uses half the memory of `float64`. On a typical 64-bit computer the default integer is `int64`; in the browser it may display as `int32`.

### 5.2 · More on `dtype`, `shape`, `ndim`

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

`np.uint8` holds 0 to 255, so 250 + 10 wraps around to 4 without any error. A Python integer never overflows, but a fixed-width NumPy integer does, so pick a type large enough for your largest value, including sums and products.

## 6 · Copy vs view

### 6.1 · Copy vs view: complete comparison 🟢

Copies own their data; views share data with the original.

```python run
import numpy as np
original = np.array([10, 20, 30, 40, 50])

# COPY: independent data
copy_arr = original.copy()
copy_arr[0] = 999
print("Original:", original)   # [10, 20, 30, 40, 50]
print("Copy:", copy_arr)       # [999, 20, 30, 40, 50]
```

```python run
import numpy as np
original = np.array([10, 20, 30, 40, 50])

# VIEW: shared data
view_arr = original.view()
view_arr[1] = 777
print("Original:", original)   # [10, 777, 30, 40, 50]
print("View:", view_arr)       # [10, 777, 30, 40, 50]
```

```python run
import numpy as np
original = np.array([10, 20, 30, 40, 50])
copy_arr = original.copy()
view_arr = original.view()
view_arr[1] = 777

# Verify with shares_memory and .base
print(np.shares_memory(original, copy_arr))  # False
print(np.shares_memory(original, view_arr))  # True
print(copy_arr.base)    # None (owns its data)
print(view_arr.base)    # [10 777 30 40 50]
```

| Property | `.copy()` | `.view()` |
|---|---|---|
| Creates new data? | Yes | No (shares memory) |
| Affects original? | No | Yes |
| `np.shares_memory`? | False | True |
| `.base` returns | `None` | Original array |
| When to use | Need independence | Need speed/efficiency |

**When does NumPy create views automatically?** Slicing (`arr[1:4]`), reshaping when possible (`arr.reshape(2,3)`) and transposing (`arr.T`).

**When does it create copies?** An explicit `.copy()`, boolean indexing (`arr[arr > 5]`) and fancy indexing (`arr[[0, 2, 4]]`).

In data science, always `.copy()` DataFrames and arrays before modifying subsets, to avoid Pandas' `SettingWithCopyWarning`.

## 7 · Array shape and reshape

### 7.1 · Shape, reshape, flatten and transpose 🟢

`.shape` tells the structure, `.reshape()` changes it, and the total number of elements must stay the same.

```python run
import numpy as np
arr = np.array([[1, 2, 3], [4, 5, 6]])
print(arr.shape)   # (2, 3) → 2 rows, 3 cols
print(arr.ndim)    # 2 dimensions
# Reshape 1-D → 2-D
flat = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
matrix = flat.reshape(4, 3)      # 12 → 4x3
print(matrix)
# [[ 1  2  3] [ 4  5  6] [ 7  8  9] [10 11 12]]
# Auto-infer with -1
auto = flat.reshape(3, -1)       # -1 → NumPy calculates 4
print(auto.shape)   # (3, 4)
```

**Reshape rules.** The total number of elements must remain the same. Twelve elements can be `(12,)`, `(2,6)`, `(3,4)`, `(4,3)`, `(6,2)`, `(2,2,3)` and so on, but **not** `(3,5)`, because 15 ≠ 12. Using `-1` tells NumPy to calculate that dimension automatically: `reshape(3, -1)` gives 12 / 3 = 4, so shape `(3,4)`. `reshape` returns a **view** when possible, so modifying the reshaped array may affect the original.

```python run
import numpy as np
try:
    np.arange(12).reshape(3, 5)
except ValueError as e:
    print("ValueError:", e)    # cannot reshape array of size 12 into shape (3,5)
```

**Flatten** turns a multi-dimensional array into 1-D, in three ways:

```python run
import numpy as np
# Flatten: multi-D → 1D
arr_2d = np.array([[1,2,3],[4,5,6]])
print(arr_2d.flatten())   # [1 2 3 4 5 6]  → COPY
print(arr_2d.ravel())     # [1 2 3 4 5 6]  → VIEW
print(arr_2d.reshape(-1)) # [1 2 3 4 5 6]  → VIEW
```

- `.flatten()` always returns a **copy** (safe).
- `.ravel()` returns a **view** (fast, but linked to the original).
- `.reshape(-1)` behaves like `ravel`.
- `.T` or `.transpose()` swaps the axes: shape `(2,3)` becomes `(3,2)`.

`flatten()` is safe but slow for large arrays; `ravel()` is fast but modifications affect the original. You can see the difference directly:

```python run
import numpy as np
a = np.array([[1, 2, 3], [4, 5, 6]])
f = a.flatten(); f[0] = 100
r = a.ravel();   r[1] = 200
print(a)          # the flatten() edit is absent, the ravel() edit is present
print(a.T.shape)  # (3, 2)
```

## 8 · Iterating over arrays

### 8.1 · `for` loops, `nditer` and `ndenumerate` 🟢

```python run
import numpy as np
# Basic 1-D loop
arr = np.array([10, 20, 30, 40, 50])
for x in arr:
    print(x)     # prints 10, 20, 30, 40, 50

# 2-D: nested loops
arr_2d = np.array([[1,2,3], [4,5,6]])
for row in arr_2d:
    for val in row:
        print(val, end=" ")  # 1 2 3 4 5 6
```

```python run
import numpy as np
# nditer: flat iteration over ANY dimension
arr_3d = np.array([[[1,2],[3,4]], [[5,6],[7,8]]])
for x in np.nditer(arr_3d):
    print(x, end=" ")   # 1 2 3 4 5 6 7 8

# ndenumerate: get INDEX + VALUE
arr = np.array([[10,20], [30,40]])
for idx, val in np.ndenumerate(arr):
    print(f"{idx} → {val}")
# (0,0)→10  (0,1)→20  (1,0)→30  (1,1)→40
```

| Tool | Behaviour |
|---|---|
| `for x in arr:` | Simple and Pythonic; for a 2-D array it gives you **rows** |
| `np.nditer(arr)` | Iterates element by element regardless of the dimensions: one flat loop for any shape |
| `np.ndenumerate(arr)` | Like `enumerate()` but returns the multi-dimensional index; perfect for debugging |

> **Careful:** iteration is 10–100x **slower** than vectorized operations. Always prefer `arr * 2` over `[x*2 for x in arr]`.

**Vectorized alternative (preferred):**

```python run
import numpy as np
arr = np.array([10, 20, 30, 40, 50])

# Instead of looping:
squared = []
for x in np.nditer(arr):
    squared.append(x**2)
print(squared)

# Use vectorized:
squared = arr ** 2   # 100x faster!
print(squared)
```

## 9 · Joining arrays

### 9.1 · `concatenate`, `stack`, `hstack`, `vstack` 🟢

Four functions for joining arrays; each behaves differently.

```python run
import numpy as np
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])
# concatenate: join along existing axis
print(np.concatenate((arr1, arr2)))
# [1 2 3 4 5 6]
# stack: join along NEW axis
print(np.stack((arr1, arr2), axis=0))
# [[1 2 3]
#  [4 5 6]]   shape (2, 3)
```

```python run
import numpy as np
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])
# hstack & vstack shortcuts
print(np.hstack((arr1, arr2)))  # [1 2 3 4 5 6]
print(np.vstack((arr1, arr2)))
# [[1 2 3]
#  [4 5 6]]
# 2-D concatenation
A = np.array([[1,2],[3,4]])
B = np.array([[5,6],[7,8]])
print(np.concatenate((A,B), axis=0))  # 4x2
print(np.concatenate((A,B), axis=1))  # 2x4
```

- `concatenate((a, b), axis)` joins along an **existing** axis; the arrays must match on all other axes.
- `stack((a, b), axis)` creates a **new** dimension and stacks along it; 1-D arrays become rows of a 2-D array.
- `hstack` is horizontal (joins columns) and `vstack` is vertical (joins rows).
- `axis=0` is the row direction (vertically); `axis=1` is the column direction (horizontally).

| Function | Joins |
|---|---|
| `concatenate` | along an existing axis |
| `stack` | along a **new** axis |
| `hstack` | horizontally (column-wise) |
| `vstack` | vertically (row-wise) |

> **Careful:** all arrays must have compatible shapes. Joining `(2,3)` with `(2,4)` along `axis=0` fails, because the columns must match.

```python run
import numpy as np
try:
    np.concatenate((np.zeros((2, 3)), np.zeros((2, 4))), axis=0)
except ValueError as e:
    print("ValueError:", e)
```

## 10 · Splitting arrays

### 10.1 · `split`, `array_split`, `hsplit`, `vsplit` 🟢

The reverse of joining: break one array into many pieces.

```python run
import numpy as np
# Equal split (length must be divisible!)
arr = np.array([10, 20, 30, 40, 50, 60])
parts = np.split(arr, 3)
print(parts)
# [array([10,20]), array([30,40]), array([50,60])]
# Unequal split (handles remainders)
arr = np.arange(10)
parts = np.array_split(arr, 3)
print(parts)
# [array([0,1,2,3]), array([4,5,6]), array([7,8,9])]
```

```python run
import numpy as np
# 2-D splitting
arr_2d = np.array([[1,2,3,4],[5,6,7,8]])
v = np.vsplit(arr_2d, 2)   # split by rows
print(v)
# [array([[1,2,3,4]]), array([[5,6,7,8]])]
h = np.hsplit(arr_2d, 2)   # split by columns
print(h)
# [array([[1,2],[5,6]]), array([[3,4],[7,8]])]
```

`np.split(arr, n)` requires the array length to be divisible by `n`; otherwise it raises `ValueError`. `np.array_split(arr, n)` handles any size: the first chunks get one extra element, so 10 elements ÷ 3 gives chunks of `[4, 3, 3]`. `vsplit` splits vertically (by rows) and `hsplit` horizontally (by columns).

```python run
import numpy as np
try:
    np.split(np.arange(10), 3)      # 10 is not divisible by 3
except ValueError as e:
    print("ValueError:", e)
print([len(p) for p in np.array_split(np.arange(10), 3)])   # [4, 3, 3]
```

Use `np.array_split()` as the safe default: it never raises an error for uneven splits.

## 11 · Searching arrays

### 11.1 · `where`, `argmax`, `argmin`, `nonzero`, `searchsorted` 🟢

Locate elements that match a condition, or find the position of the maximum or minimum.

```python run
import numpy as np
arr = np.array([10, 25, 30, 45, 50, 65])

# where: find indices matching condition
idx = np.where(arr > 40)
print(idx)          # (array([3, 4, 5]),)
print(arr[idx])     # [45 50 65]
# Find even positions
arr2 = np.array([1,2,3,4,5,6,7,8])
print(np.where(arr2 % 2 == 0))  # (array([1,3,5,7]),)
```

```python run
import numpy as np
# argmax / argmin: position of max/min
arr = np.array([3, 15, 8, 22, 6])
print(np.argmax(arr))   # 3 (index of 22)
print(np.argmin(arr))   # 0 (index of 3)
# nonzero: indices of non-zero elements
arr = np.array([0, 7, 0, 9, 10, 0])
print(np.nonzero(arr))  # (array([1, 3, 4]),)

# searchsorted: where to insert to keep order
sorted_arr = np.array([1, 3, 5, 7, 9])
print(np.searchsorted(sorted_arr, 4))  # 2
```

**How `np.where(cond)` works:** (1) it evaluates the condition for each element (`arr > 40` gives `[F, F, F, T, T, T]`); (2) it returns the indices where the result is `True`, as a tuple `(array([3, 4, 5]),)`; (3) you use those indices to get the values, `arr[idx]` → `[45, 50, 65]`.

`np.argmax` and `np.argmin` return a **single index**: the position of the maximum or minimum value. `np.searchsorted` performs a binary search on a sorted array. For a 2-D array, `argmax` returns a position in the flattened array; use `np.unravel_index()` to convert it to `(row, col)`:

```python run
import numpy as np
M = np.array([[1, 9], [3, 4]])
flat = np.argmax(M)
print(flat)                                 # 1  (position in the flattened array)
row, col = np.unravel_index(flat, M.shape)
print(int(row), int(col))                   # 0 1
```

| Function | Returns |
|---|---|
| `np.where(cond)` | Tuple of index arrays where True |
| `np.argmax(arr)` | Single index of max value |
| `np.argmin(arr)` | Single index of min value |
| `np.nonzero(arr)` | Indices of all non-zero elements |
| `np.searchsorted()` | Insert position in a sorted array |

## 12 · Sorting arrays

### 12.1 · `np.sort()` and `np.argsort()` 🟢

`np.sort()` returns a **new** sorted array; `arr.sort()` sorts **in place**.

```python run
import numpy as np
arr = np.array([25, 5, 15, 30, 10])

# np.sort: returns NEW sorted array
print(np.sort(arr))          # [ 5 10 15 25 30]
print(arr)                   # [25  5 15 30 10] unchanged!

# Descending: sort then reverse
print(np.sort(arr)[::-1])    # [30 25 15 10  5]

# In-place sort
arr.sort()
print(arr)                   # [ 5 10 15 25 30] changed!
```

| | `np.sort(arr)` | `arr.sort()` |
|---|---|---|
| Result | A new sorted array | Sorts the array in place; returns `None` |
| Original | Unchanged | Modified |

`np.argsort()` returns the **indices that would sort** the array:

```python run
import numpy as np
# argsort: indices that WOULD sort the array
arr = np.array([40, 10, 30, 20])
idx = np.argsort(arr)
print(idx)           # [1 3 2 0]
print(arr[idx])      # [10 20 30 40]

# Practical: sort names by their scores
scores = np.array([75, 92, 60, 88])
names = np.array(['Alice','Bob','Charlie','David'])
order = np.argsort(scores)
print(names[order])  # Charlie Alice David Bob
```

For `[40, 10, 30, 20]` the smallest value, 10, is at index 1, then 20 at index 3, then 30 at index 2, and the largest, 40, at index 0, so the indices are `[1, 3, 2, 0]`. `argsort` lets you sort one array and reorder related arrays the same way, which is essential for data analysis.

**2-D sorting with `axis`:**

```python run
import numpy as np
arr_2d = np.array([[12, 5, 7], [1, 9, 3]])
print(np.sort(arr_2d, axis=1))   # sort each row:     [[ 5  7 12] [ 1  3  9]]
print(np.sort(arr_2d, axis=0))   # sort each column:  [[ 1  5  3] [12  9  7]]
```

## 13 · Filtering arrays

### 13.1 · Boolean masking: the core of filtering 🟢

Create a True/False mask, then use it to select the matching elements.

```python run
import numpy as np
arr = np.array([10, 15, 20, 25, 30, 35])
# Step 1: Create boolean mask
mask = arr > 20
print(mask)   # [False False False True True True]
# Step 2: Use mask to filter
filtered = arr[mask]
print(filtered)   # [25 30 35]
# One-liner:
print(arr[arr > 20])   # [25 30 35]
```

`arr > 20` compares each element (10>20 → F, 15>20 → F, 20>20 → F, 25>20 → T, 30>20 → T, 35>20 → T), producing `[F, F, F, T, T, T]`; `arr[mask]` keeps only the elements where the mask is True. The mask and the array must have the same shape. This is the most Pythonic way to filter arrays.

**Compound conditions** use `&` (AND), `|` (OR) and `~` (NOT), and **parentheses are mandatory**: `arr[(cond1) & (cond2)]`.

```python run
import numpy as np
# Compound conditions (MUST use parentheses + & | ~)
arr = np.arange(1, 21)
between = arr[(arr > 5) & (arr < 15)]
print(between)   # [ 6  7  8  9 10 11 12 13 14]
outside = arr[(arr < 5) | (arr > 17)]
print(outside)   # [ 1  2  3  4 18 19 20]
# Handle NaN values
arr = np.array([12, np.nan, 15, np.nan, 20])
clean = arr[~np.isnan(arr)]
print(clean)     # [12. 15. 20.]
```

> **Careful:** `arr[arr > 5 & arr < 15]` fails, because `&` binds tighter than `>`. You must write `arr[(arr > 5) & (arr < 15)]`. Filtering returns a **copy** (a new array); the original is never modified. Use `np.isnan()` for missing data.

```python run
import numpy as np
arr = np.arange(1, 21)
try:
    arr[arr > 5 & arr < 15]
except ValueError as e:
    print("ValueError:", e)
```

### 13.2 · More on masks and fancy indexing

A comparison on an array gives a boolean array of the same shape; use it as an index to **filter**. This replaces `if` inside loops, and it is exactly how Pandas' `df[df.col > x]` works.

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

`np.where` has two forms: with one argument it returns *indices* (section 11); with three, `np.where(cond, a, b)` picks `a` where the condition is true and `b` elsewhere, a vectorised `if/else`.

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

## 14 · Random numbers

### 14.1 · Random number generation functions 🟢

`numpy.random` provides tools for random floats, integers and distributions. The values change on every run, so the comments show examples.

```python run
import numpy as np
from numpy import random

# Random float in [0, 1)
print(random.rand())              # e.g. 0.7432

# Random integers in [low, high)
print(random.randint(100))        # single int 0-99
print(random.randint(10, 50, size=(2,3)))  # 2x3

# Random floats array
print(random.rand(3, 3))          # 3x3 uniform

# Normal distribution N(0, 1)
print(random.randn(2, 3))         # 2x3 standard normal
```

- `rand()` draws from a uniform distribution in [0, 1); every value is equally likely. `rand(rows, cols)` gives a 2-D array of uniform floats.
- `randint(low, high, size)` gives random integers; `low` is inclusive, `high` exclusive, and `size=(rows, cols)` makes a 2-D array.
- `randn(rows, cols)` draws from the standard normal N(0,1): values cluster around 0, and about 68% fall between −1 and 1.
- `choice(array, size)` makes random picks from an array.

```python run
import numpy as np
from numpy import random

# Random choice from an array
print(random.choice([3, 5, 7, 9]))           # one pick
print(random.choice([3, 5, 7, 9], size=5))   # 5 picks

# Choice without replacement (no repeats)
arr = np.arange(1, 11)
print(random.choice(arr, size=5, replace=False))
```

`replace=False` means each element can only be picked once, like drawing cards without putting them back.

### 14.2 · Reproducibility, shuffling and distributions 🟢

Seeds make results repeatable, `shuffle` rearranges, and `choice(p=...)` follows given probabilities.

```python run
import numpy as np
# SEED: same seed → same random numbers
np.random.seed(42)
print(np.random.randint(0, 10, 5))  # [6 3 7 4 6]
np.random.seed(42)                   # reset seed
print(np.random.randint(0, 10, 5))  # [6 3 7 4 6] same!
```

Random numbers are not truly random: they come from a deterministic algorithm, and the **seed** initialises it. The same seed gives the same sequence every time, which is essential for reproducible experiments, debugging and scientific publications. Always set `np.random.seed()` at the start of your experiments.

```python run
import numpy as np
# SHUFFLE: rearrange IN PLACE
arr = np.array([1, 2, 3, 4, 5])
np.random.shuffle(arr)
print(arr)   # e.g. [3, 1, 5, 2, 4] — original changed!
# PERMUTATION: returns NEW shuffled array
arr = np.array([1, 2, 3, 4, 5])
perm = np.random.permutation(arr)
print(perm)  # e.g. [4, 2, 5, 1, 3]
print(arr)   # [1, 2, 3, 4, 5] — original safe!
```

`shuffle` works in place (returns `None`) and `permutation` returns a new array: the same pattern as `arr.sort()` versus `np.sort()`.

```python run
import numpy as np
# Weighted random choice (probability distribution)
x = np.random.choice(
    [3, 5, 7, 9],
    p=[0.1, 0.3, 0.6, 0.0],   # probabilities must sum to 1
    size=10)
print(x)  # 7 appears ~60%, 5 ~30%, 3 ~10%, 9 never
```

> **Careful:** the probabilities in `choice()` must sum to exactly 1.0, otherwise you get a `ValueError`.

### 14.3 · More on random numbers: the modern API

The slides use the *legacy* functions (`np.random.seed`, `rand`, `randint`). NumPy now recommends creating a **generator object** with `np.random.default_rng(seed)` and calling methods on it. A seeded generator makes an experiment reproducible just as `seed` does, but the state belongs to the object instead of being hidden global state, so two parts of a program cannot disturb each other's random sequence. Both styles are common in existing code, so you should be able to read either.

| Legacy (slides) | Modern |
|---|---|
| `np.random.seed(42)` | `rng = np.random.default_rng(42)` |
| `np.random.randint(1, 7, 5)` | `rng.integers(1, 7, size=5)` |
| `np.random.rand(3)` | `rng.random(3)` |
| `np.random.randn(2, 3)` | `rng.normal(size=(2, 3))` |
| `np.random.choice(...)` | `rng.choice(...)` |
| `np.random.shuffle(a)` / `permutation(a)` | `rng.shuffle(a)` / `rng.permutation(a)` |

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

## 15 · NumPy ufuncs

### 15.1 · Arithmetic and mathematical ufuncs 🟢

A **universal function** (ufunc) operates on each element independently: like a `for` loop, but implemented in optimised C code. This is called **vectorization**: no Python loop is needed. `np.add(a, b)` does `a[0]+b[0]`, `a[1]+b[1]`, ... and returns `[11, 22, 33, 44]` for the arrays below.

```python run
import numpy as np
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])
print(np.add(a, b))       # [11 22 33 44]
print(np.subtract(b, a))  # [ 9 18 27 36]
print(np.multiply(a, b))  # [ 10  40  90 160]
print(np.divide(b, a))    # [10. 10. 10. 10.]
print(np.power(a, 2))     # [ 1  4  9 16]
print(np.mod(b, a))       # [0 0 0 0]
```

**Operator overloading:** `a + b` calls `np.add`, `a * b` calls `np.multiply`, and so on. The explicit ufunc names offer extra features such as `.reduce()`.

```python run
import numpy as np
# Unary ufuncs (one input)
arr = np.array([1, 4, 9, 16, 25])
print(np.sqrt(arr))   # [1. 2. 3. 4. 5.]
print(np.exp(arr))    # exponential: e^x
print(np.log(arr))    # natural log: ln(x)
# Rounding functions
print(np.trunc([-3.7, 3.7]))   # [-3.  3.]  truncate
print(np.around(3.1666, 2))     # 3.17  round to 2 dec
print(np.floor([-3.7, 3.7]))   # [-4.  3.]  round down
print(np.ceil([-3.7, 3.7]))    # [-3.  4.]  round up
```

| Category | Functions |
|---|---|
| Arithmetic | `add`, `subtract`, `multiply`, `divide`, `power`, `mod`, `abs` |
| Exponential | `sqrt`, `exp`, `log`, `log2`, `log10` |
| Rounding | `trunc`, `around`, `floor`, `ceil` |
| Trigonometric | `sin`, `cos`, `tan`, `arcsin`, `arccos`, `arctan` |
| Set operations | `unique`, `union1d`, `intersect1d`, `setdiff1d` |

### 15.2 · Trigonometry, reductions, set operations and custom ufuncs 🟢

Trigonometric functions work in **radians**; `reduce()` aggregates; `frompyfunc()` creates a custom ufunc.

```python run
import numpy as np
# Trig functions (input MUST be radians!)
angles_deg = np.array([0, 30, 45, 60, 90])
angles_rad = np.deg2rad(angles_deg)  # convert first!
with np.printoptions(precision=2, suppress=True):   # shorter display, only inside this block
    print(np.sin(angles_rad))
    # [0.   0.5  0.71 0.87 1.  ]
    print(np.cos(angles_rad))
    # [1.   0.87 0.71 0.5  0.  ]
```

> **Careful:** trig functions expect radians. `np.sin(90)` is **not** 1; convert first: `np.sin(np.deg2rad(90))` is `1.0`.

**Reduce** aggregates all elements with a ufunc, applying the function repeatedly: `np.add.reduce([1,2,3,4,5])` computes 1 + 2 = 3, then 3 + 3 = 6, then 6 + 4 = 10, then 10 + 5 = 15.

```python run
import numpy as np
# Reduce: aggregate all elements with a ufunc
arr = np.array([1, 2, 3, 4, 5])
print(np.add.reduce(arr))       # 15  (1+2+3+4+5)
print(np.multiply.reduce(arr))  # 120 (1*2*3*4*5)
# Set operations
a = np.array([1, 2, 3, 4, 5])
b = np.array([3, 4, 5, 6, 7])
print(np.unique([1,1,2,2,3]))      # [1 2 3]
print(np.intersect1d(a, b))        # [3 4 5]
print(np.union1d(a, b))            # [1 2 3 4 5 6 7]
print(np.setdiff1d(a, b))          # [1 2]
```

**Custom ufunc** with `frompyfunc(func, n_in, n_out)`: it wraps any Python function into a vectorized function that is applied to each element. `n_in=2` means it takes 2 array inputs and `n_out=1` means 1 output array.

```python run
import numpy as np
# Custom ufunc with frompyfunc()
def myadd(x, y):
    return x + y
my_ufunc = np.frompyfunc(myadd, 2, 1)  # 2 in, 1 out
print(my_ufunc([1,2,3], [4,5,6]))      # [5 7 9]
```

Always prefer built-in ufuncs over custom ones: the built-ins are implemented in C and are much faster. A `frompyfunc` result is an array of Python objects (`dtype=object`), because the Python function still runs once per element.

## 16 · Vectorised arithmetic and broadcasting

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

## 17 · Aggregations and `axis`

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

## 18 · Linear algebra

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

## 19 · Worked example: outliers in real data

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

## 20 · NumPy quick reference 🟢

| Task | Functions |
|---|---|
| **Create** | `array()`, `zeros()`, `ones()`, `arange()`, `linspace()`, `eye()`, `full()` |
| **Index** | `arr[i]`, `arr[row,col]`, `arr[[0,2]]`, `arr[-1]` |
| **Slice** | `arr[start:end:step]`, `arr[:,1]`, `arr[::2]` |
| **Shape** | `.shape`, `.ndim`, `reshape()`, `flatten()`, `ravel()`, `.T` |
| **Join** | `concatenate()`, `stack()`, `hstack()`, `vstack()` |
| **Split** | `split()`, `array_split()`, `hsplit()`, `vsplit()` |
| **Search** | `where()`, `argmax()`, `argmin()`, `nonzero()` |
| **Sort** | `np.sort()`, `.sort()`, `argsort()` |
| **Filter** | `arr[mask]`, `arr[arr>5]`, `arr[(c1)&(c2)]` |
| **Random** | `rand()`, `randint()`, `randn()`, `choice()`, `seed()` |
| **Ufuncs** | `add`, `multiply`, `sqrt`, `sin`, `reduce`, `frompyfunc` |
| **Types** | `.dtype`, `.astype()`, `.itemsize`, `.nbytes` |

## 21 · Common pitfalls and best practices 🟢

| Pitfall | The rule |
|---|---|
| Slices are views | Modifying a slice changes the original array. Use `.copy()` for independence. |
| Missing parentheses | `arr[arr>5 & arr<15]` fails. Use `arr[(arr>5) & (arr<15)]`. |
| Trig expects radians | `np.sin(90)` ≠ 1. Convert: `np.sin(np.deg2rad(90))`. |
| `split` on an uneven size | `np.split(10 elements, 3)` raises an error. Use `array_split()`. |
| `shuffle` vs `permutation` | `shuffle()` changes the original. `permutation()` returns a new array. |
| `sort()` vs `np.sort()` | `.sort()` modifies in place (returns `None`). `np.sort()` returns a new array. |
| Mixed types upcast | `np.array([1, 2.5, 'a'])` → all become strings. |
| `flatten` vs `ravel` | `flatten()` returns a copy. `ravel()` returns a view. |

Each rule in one run:

```python run
import numpy as np

a = np.array([1, 2, 3, 4])
s = a[1:3]; s[0] = 99
print("slice edit reached the original:", a)

print("np.sin(90) =", round(float(np.sin(90)), 3), " np.sin(deg2rad(90)) =", float(np.sin(np.deg2rad(90))))

b = np.array([3, 1, 2])
print("b.sort() returns:", b.sort(), "-> b is now", b)

x = np.array([1, 2, 3, 4, 5])
print("permutation:", np.random.permutation(x), " original untouched:", x)

print("mixed types:", np.array([1, 2.5, 'a']))
```

## Summary

* Arrays are **typed, fixed-shape, contiguous** — check `dtype`, `shape`, `ndim`.
* Index with `arr[row, col]`; slice with `start:end:step`. Slices are **views**; `.copy()` when you need independence.
* `reshape` keeps the number of elements (and `-1` fills in one dimension); `flatten` copies, `ravel` is a view.
* Join with `concatenate`/`stack`/`hstack`/`vstack`, split with `split`/`array_split`; sort with `np.sort` (new) or `.sort()` (in place); locate with `where`, `argmax`, `argmin`.
* **Masks** replace `if` inside loops; combine with `&`, `|`, `~`, always in parentheses.
* **Ufuncs** are vectorised C loops; trigonometry takes radians.
* **Broadcasting**: align shapes from the right; 1 stretches. `axis=0` → per column, `axis=1` → per row.
* Seed the generator (`np.random.seed` or `default_rng(seed)`) for reproducibility.

Next: *Pandas I* — the same ideas, with labels.

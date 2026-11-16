# Pandas I — Tables, Selection and Cleaning

<p class="lesson-intro">Week 4 · Programming for Data Science (606315)</p>

NumPy arrays are fast, but real data comes with **labels**: column names, student numbers, dates. Pandas adds labels to NumPy arrays and builds the tools of everyday data work on top of them. This week covers the objects themselves, how to select from them, and how to clean a messy table.

> **About this lesson.** It follows the first half of Chapter 3 of the course textbook, Jake VanderPlas, *Python Data Science Handbook* (2nd ed., O'Reilly). The explanations, examples and diagrams are written for this course; each section ends with a "Read more" link to the matching section of the textbook's free online edition.
>
> **Helper notes.** Words in the code with a dotted underline have a short note. Hover over one (or tap it) to read what it does. A table that is the **last line** of an example is shown as a formatted table in the Output panel.

## 1 · The Pandas objects

### 1.1 · Series: one labelled column

A `Series` is a 1-D array of values together with an **index** of labels, one label per value.

```python run
import pandas as pd

gpa = pd.Series([3.4, 2.1, 3.9, 3.2])
print(gpa)
print("values:", gpa.values)
print("index :", gpa.index)
```

When you give no index, Pandas numbers the rows 0, 1, 2, … The point of a Series is that the labels can be anything you choose.

```python run
import pandas as pd

gpa = pd.Series([3.4, 2.1, 3.9, 3.2], index=["Ahmad", "Sara", "Omar", "Lina"])
print(gpa)
print(gpa["Omar"])
```

A Series therefore behaves like a NumPy array and like a dictionary at the same time. A dictionary turns into a Series directly: the keys become the index.

```python run
import pandas as pd

credits = pd.Series({"Ahmad": 62, "Sara": 110, "Omar": 28})
print(credits)
print("Sara" in credits)      # membership tests the labels, like a dictionary
```

### 1.2 · DataFrame: a table

A `DataFrame` is a table. The simplest way to think of it is as several Series that **share one index**, each one forming a column.

![A small table with its three parts labelled: the index down the left, the column names along the top, and the values in the middle. One column is highlighted as a Series.](figures/dataframe.svg)

<p class="caption">Every DataFrame has an index (row labels), columns (column labels) and values. Any single column is a Series.</p>

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "DS", "AI"],
    "year":  [2, 4, 1, 3],
    "gpa":   [3.4, 2.1, 3.9, 3.2],
}, index=["Ahmad", "Sara", "Omar", "Lina"])

print(df)
print("index  :", df.index.tolist())
print("columns:", df.columns.tolist())
print("shape  :", df.shape)
```

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "DS", "AI"],
    "year":  [2, 4, 1, 3],
    "gpa":   [3.4, 2.1, 3.9, 3.2],
}, index=["Ahmad", "Sara", "Omar", "Lina"])

column = df["gpa"]            # one column is a Series
print(type(column).__name__)
print(column)
```

### 1.3 · Loading a real file

Tables usually come from files. `pd.read_csv` reads one into a DataFrame, and five short commands give you a first look at it.

```python run
import pandas as pd

students = pd.read_csv("data/students.csv")

print(students.shape)              # rows, columns
print(students.dtypes)             # the type of each column
print(students.isna().sum())       # missing values per column
students.head()                    # the first five rows
```

Look at the types. `gpa` should be a number, but it was read as text. Something in that column is not a number, and Section 4 finds it and fixes it.

:::challenge title="Series or DataFrame?"
`students` is the table loaded above. What type is each of these: a Series or a DataFrame?

1. `students["gpa"]`
2. `students[["gpa"]]`
3. `students[["name", "gpa"]]`
---
1. A **Series**. One pair of brackets with one column name gives that column.
2. A **DataFrame** with one column. The inner brackets make a *list* of column names, and a list of names always gives a table, even when the list has one name.
3. A **DataFrame** with two columns.

This matters because some methods exist only on one of the two types, and because a one-column DataFrame prints differently from a Series.
:::

**Read more:** [Introducing Pandas Objects](https://jakevdp.github.io/PythonDataScienceHandbook/03.01-introducing-pandas-objects.html)

## 2 · Indexing and selection

### 2.1 · `loc` uses labels, `iloc` uses positions

There are two ways to say which rows you want: by **label** or by **position**. Pandas keeps them apart with two indexers, so there is never any doubt about which one you mean.

```python run
import pandas as pd

gpa = pd.Series([3.4, 2.1, 3.9, 3.2], index=["Ahmad", "Sara", "Omar", "Lina"])

print(gpa.loc["Sara"])              # by label
print(gpa.iloc[1])                  # by position: the second value
print(gpa.loc["Sara":"Lina"])       # a label slice INCLUDES the end
print(gpa.iloc[1:3])                # a position slice excludes the end, as in Python
```

> **Look out.** The two kinds of slice treat the end differently. `gpa.loc["Sara":"Lina"]` includes Lina; `gpa.iloc[1:3]` stops before position 3.

The difference becomes a real trap when the labels are themselves integers.

:::challenge title="Label or position?"
What does each line print? Decide first, then run the code.

```python run
import pandas as pd

s = pd.Series(["a", "b", "c"], index=[1, 2, 3])
print(s.loc[1])
print(s.iloc[1])
print(len(s.loc[1:2]), len(s.iloc[1:2]))
```
---
- `s.loc[1]` is `"a"`: the row whose **label** is 1.
- `s.iloc[1]` is `"b"`: the row at **position** 1, which is the second row.
- The lengths are `2` and `1`. The label slice `1:2` includes label 2; the position slice `1:2` contains only position 1.

Plain `s[1]` would look up the label here, which is easy to misread. Writing `loc` or `iloc` every time removes the doubt.
:::

### 2.2 · Selecting from a DataFrame

`loc` and `iloc` take the rows first and the columns second, separated by a comma, like a 2-D NumPy array.

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "DS", "AI"],
    "year":  [2, 4, 1, 3],
    "gpa":   [3.4, 2.1, 3.9, 3.2],
}, index=["Ahmad", "Sara", "Omar", "Lina"])

print(df.loc["Omar", "gpa"])                   # one cell
print(df.loc[["Ahmad", "Lina"], ["major", "gpa"]])
print(df.iloc[:2, :2])                         # first 2 rows, first 2 columns
print(df.loc[:, "year"])                       # every row, one column
```

### 2.3 · Selecting rows with a mask

Masks work as in NumPy. A comparison on a column gives a Series of `True` and `False`, and putting it in the brackets keeps the `True` rows.

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "DS", "AI"],
    "year":  [2, 4, 1, 3],
    "gpa":   [3.4, 2.1, 3.9, 3.2],
}, index=["Ahmad", "Sara", "Omar", "Lina"])

print(df[df["gpa"] > 3.3])
print(df[(df["major"] == "DS") & (df["year"] >= 2)])
print(df.loc[df["gpa"] > 3.3, "major"])        # a mask for the rows, a label for the column
print(df[df["major"].isin(["CS", "AI"])])
```

The rules from last week still hold: `&`, `|` and `~`, with every condition in brackets.

### 2.4 · Adding and changing columns

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "DS", "AI"],
    "year":  [2, 4, 1, 3],
    "gpa":   [3.4, 2.1, 3.9, 3.2],
}, index=["Ahmad", "Sara", "Omar", "Lina"])

df["percent"] = df["gpa"] / 4 * 100            # a new column from an old one
df.loc[df["gpa"] < 2.5, "status"] = "probation"
df.loc[df["gpa"] >= 2.5, "status"] = "good"
df
```

> **Look out.** To change values, do the row choice and the column choice in **one** `loc`, as above. The two-step form `df[df["gpa"] < 2.5]["status"] = "probation"` first builds a temporary table and then changes that temporary table, so `df` itself is not changed.

:::exercise id=p1 title="Top students in one major"
Complete `top_in_major(df, major, minimum)` so that it returns the rows of `df` whose `major` equals `major` **and** whose `gpa` is at least `minimum`. Return only the columns `name` and `gpa`, in that order.

```python
import pandas as pd

def top_in_major(df, major, minimum):
    return ...

demo = pd.DataFrame({
    "name":  ["Ahmad", "Sara", "Omar", "Lina"],
    "major": ["DS", "CS", "DS", "AI"],
    "gpa":   [3.4, 2.1, 3.9, 3.2],
})
print(top_in_major(demo, "DS", 3.5))
```

```python check
import pandas as pd
d = pd.DataFrame({"name": ["Ahmad", "Sara", "Omar", "Lina", "Rami"],
                  "major": ["DS", "CS", "DS", "AI", "DS"],
                  "gpa": [3.4, 2.1, 3.9, 3.2, 3.5]})
r = top_in_major(d, "DS", 3.5)
assert isinstance(r, pd.DataFrame), "return a DataFrame"
assert list(r.columns) == ["name", "gpa"], f"columns should be name and gpa, got {list(r.columns)}"
assert sorted(r["name"]) == ["Omar", "Rami"], f"expected Omar and Rami (3.5 counts), got {sorted(r['name'])}"
assert len(top_in_major(d, "AI", 3.0)) == 1 and len(top_in_major(d, "CS", 3.0)) == 0
```
:::

**Read more:** [Data Indexing and Selection](https://jakevdp.github.io/PythonDataScienceHandbook/03.02-data-indexing-and-selection.html)

## 3 · Operating on data

### 3.1 · NumPy functions keep the labels

Everything from last week still works. The result of an operation keeps the index and the column names.

```python run
import numpy as np
import pandas as pd

marks = pd.DataFrame({"midterm": [70, 55, 90], "final": [80, 65, 70]},
                     index=["Ahmad", "Sara", "Omar"])

print(marks * 1.05)                 # every value
print(np.sqrt(marks).round(2))      # a NumPy function, labels kept
print(marks["midterm"] * 0.4 + marks["final"] * 0.6)
print(marks.mean())                 # per column
print(marks.mean(axis=1))           # per row
```

### 3.2 · Index alignment

When two Series are combined, Pandas matches the values by **label**, not by position. A label that appears on only one side has no partner, and the result for it is `NaN`, which means "missing".

![Two columns of quiz marks with partly different student names are added. Names found in both get a sum. Names found in only one get NaN.](figures/alignment.svg)

<p class="caption">Sara and Omar appear in both, so their marks are added. Ahmad and Lina each appear in one only, so their results are missing.</p>

```python run
import pandas as pd

quiz1 = pd.Series({"Ahmad": 8, "Sara": 6, "Omar": 9})
quiz2 = pd.Series({"Sara": 7, "Omar": 10, "Lina": 5})

print(quiz1 + quiz2)
```

This protects you from adding values that belong to different students merely because they sit on the same row. When a missing partner should count as zero, use the method form and say so.

```python run
import pandas as pd

quiz1 = pd.Series({"Ahmad": 8, "Sara": 6, "Omar": 9})
quiz2 = pd.Series({"Sara": 7, "Omar": 10, "Lina": 5})

print(quiz1.add(quiz2, fill_value=0))
```

| Operator | Method with the same meaning |
|---|---|
| `+` | `add()` |
| `-` | `sub()` |
| `*` | `mul()` |
| `/` | `div()` |

> **Look out.** The order of the rows does not matter to Pandas, only the labels. Two Series with the same values in the same order but **different labels** give a result that is entirely `NaN`. If you see that, compare the two indexes first.

:::exercise id=p2 title="Total points, with absences as zero"
`a` and `b` are Series of points indexed by student name. Some students are missing from one of them. Complete `total_points(a, b)` so that it returns the total for **every** student, counting a missing mark as 0.

```python
import pandas as pd

def total_points(a, b):
    return ...

q1 = pd.Series({"Ahmad": 8, "Sara": 6, "Omar": 9})
q2 = pd.Series({"Sara": 7, "Omar": 10, "Lina": 5})
print(total_points(q1, q2))
```

```python check
import pandas as pd
q1 = pd.Series({"Ahmad": 8, "Sara": 6, "Omar": 9})
q2 = pd.Series({"Sara": 7, "Omar": 10, "Lina": 5})
r = total_points(q1, q2)
assert isinstance(r, pd.Series), "return a Series"
assert not r.isna().any(), "no total should be missing: a missing mark counts as 0"
assert r.to_dict() == {"Ahmad": 8, "Lina": 5, "Omar": 19, "Sara": 13}, f"wrong totals: {r.to_dict()}"
```
:::

**Read more:** [Operating on Data in Pandas](https://jakevdp.github.io/PythonDataScienceHandbook/03.03-operations-in-pandas.html)

## 4 · Handling missing data

### 4.1 · How missing values behave

Real tables have holes. Pandas marks a missing number as `NaN`. Arithmetic with `NaN` gives `NaN`, but Pandas' own summaries **skip** missing values by default.

```python run
import numpy as np
import pandas as pd

s = pd.Series([3.4, np.nan, 3.9, None])     # None also becomes NaN
print(s)
print(s + 1)             # missing stays missing
print(s.sum(), s.mean()) # summaries skip the missing values
print(s.count(), "known values out of", len(s))
```

> **Look out.** `NaN` is not equal to anything, including itself, so `s == np.nan` is `False` everywhere and finds nothing. Use `isna()`.

### 4.2 · Finding them

```python run
import numpy as np
import pandas as pd

s = pd.Series([3.4, np.nan, 3.9, np.nan], index=["Ahmad", "Sara", "Omar", "Lina"])
print(s.isna())
print(s[s.notna()])
print("missing:", s.isna().sum())
```

### 4.3 · Dropping them

```python run
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "name": ["Ahmad", "Sara", "Omar", "Lina"],
    "gpa":  [3.4, np.nan, 3.9, 3.2],
    "city": ["Amman", "Irbid", None, "Zarqa"],
})

print(df.dropna())                     # drop every row that has any hole
print(df.dropna(subset=["gpa"]))       # only rows whose gpa is missing
print(df.dropna(axis=1))               # drop COLUMNS that have a hole
```

### 4.4 · Filling them

```python run
import numpy as np
import pandas as pd

s = pd.Series([3.4, np.nan, 3.9, np.nan, 2.8])

print(s.fillna(0).tolist())                    # a fixed value
print(s.fillna(s.mean()).round(2).tolist())    # the mean of the known values
print(s.ffill().tolist())                      # carry the previous value forward
print(s.bfill().tolist())                      # use the next value
```

Which is right depends on what the hole means. Filling a GPA with 0 would badly distort the average. Carrying the last value forward suits a reading that changes slowly over time and makes no sense for a list of unrelated students. Dropping rows is the honest choice when few are missing and nothing suggests a pattern. Whatever you choose, **say what you did and why** in your project report.

### 4.5 · A real case: the GPA column

In Section 1.3 the `gpa` column was read as text. Here is why, and the fix.

```python run
import pandas as pd

students = pd.read_csv("data/students.csv")

as_number = pd.to_numeric(students["gpa"], errors="coerce")   # anything unreadable becomes NaN
bad = students.loc[as_number.isna(), "gpa"]
print(bad.value_counts(dropna=False))                         # what was in those cells

students["gpa"] = as_number
print(students["gpa"].dtype, "| missing:", students["gpa"].isna().sum())
print("mean GPA:", students["gpa"].mean().round(3))
```

A few cells held the word `unknown` and a few were empty. One piece of text is enough to turn a whole column into text. `errors="coerce"` converts what it can and marks the rest as missing.

:::challenge title="Which number is it?"
A column of five marks is `[80, NaN, 60, NaN, 70]`. Without running anything, what are `s.mean()`, `s.fillna(0).mean()` and `len(s.dropna())`?
---
- `s.mean()` is **70**. Missing values are skipped: (80 + 60 + 70) / 3.
- `s.fillna(0).mean()` is **42**. Now the two zeros count: 210 / 5.
- `len(s.dropna())` is **3**.

The gap between 70 and 42 is why "fill with 0" must be a deliberate decision. It is right when missing truly means zero (an exam that was not sat) and wrong when it means "not recorded".
:::

:::exercise id=p3 title="Clean the GPA column"
Complete `clean_gpa(df)` so that it returns a copy of `df` in which the `gpa` column is numeric, and every value that was missing or unreadable is replaced by the **median** of the valid GPAs.

```python
import pandas as pd

def clean_gpa(df):
    out = df.copy()
    ...
    return out

demo = pd.DataFrame({"name": ["a", "b", "c", "d"], "gpa": ["3.0", "unknown", "2.0", None]})
print(clean_gpa(demo))
```

```python check
import pandas as pd
d = pd.DataFrame({"name": list("abcde"), "gpa": ["3.0", "unknown", "2.0", None, "4.0"]})
r = clean_gpa(d)
assert isinstance(r, pd.DataFrame) and len(r) == 5, "return a DataFrame with the same rows"
assert pd.api.types.is_numeric_dtype(r["gpa"]), "the gpa column must be numeric"
assert not r["gpa"].isna().any(), "no GPA may be missing in the result"
assert r["gpa"].tolist() == [3.0, 3.0, 2.0, 3.0, 4.0], f"missing values should become the median, 3.0: {r['gpa'].tolist()}"
assert d["gpa"].tolist()[1] == "unknown", "do not change the original table"
```
:::

**Read more:** [Handling Missing Data](https://jakevdp.github.io/PythonDataScienceHandbook/03.04-missing-values.html)

## 5 · Working with text columns

The textbook treats text later in the chapter. It is placed here because cleaning text is part of this week's work.

### 5.1 · The `.str` accessor

A text column has a `.str` attribute that applies Python's string methods to **every value at once**, and skips missing values instead of failing on them.

```python run
import pandas as pd

names = pd.Series(["  ahmad ODEH", "Sara nasser ", None, "OMAR zaid"])

print(names.str.strip().str.title())
print(names.str.len())
print(names.str.lower().str.contains("sa"))
print(names.str.strip().str.split().str[0])     # the first word of each
```

| Purpose | Methods |
|---|---|
| Change case | `str.lower()`, `str.upper()`, `str.title()` |
| Remove spaces at the ends | `str.strip()` |
| Test the content | `str.contains()`, `str.startswith()`, `str.endswith()` |
| Replace part of the text | `str.replace()` |
| Cut into pieces | `str.split()`, then `str[0]`, `str[1]`, … |
| Measure | `str.len()` |

### 5.2 · A real case: inconsistent categories

Counting the distinct values of a text column is the quickest way to find spelling problems.

```python run
import pandas as pd

students = pd.read_csv("data/students.csv")

print(students["city"].value_counts())
print(students["major"].unique())
```

`AMMAN` and `Amman` are counted as different cities, and one major has stray spaces around it. To Pandas these are different values, so every later count and group would be wrong.

```python run
import pandas as pd

students = pd.read_csv("data/students.csv")

students["city"] = students["city"].str.title()
students["major"] = students["major"].str.strip()

print(students["city"].value_counts())
print(students["major"].nunique(), "majors")

students["domain"] = students["email"].str.split("@").str[1]
print(students["domain"].value_counts())
```

:::exercise id=p4 title="Tidy two text columns"
Complete `tidy(df)` so that it returns a copy of `df` in which `major` has no spaces at either end and `city` has a capital first letter with the rest in lower case (`AMMAN` and `amman` both become `Amman`).

```python
import pandas as pd

def tidy(df):
    out = df.copy()
    ...
    return out

demo = pd.DataFrame({"major": [" AI ", "AI"], "city": ["AMMAN", "amman"]})
print(tidy(demo))
```

```python check
import pandas as pd
d = pd.DataFrame({"major": [" AI ", "AI", "Data Science  "], "city": ["AMMAN", "amman", "Irbid"]})
r = tidy(d)
assert isinstance(r, pd.DataFrame), "return a DataFrame"
assert r["major"].tolist() == ["AI", "AI", "Data Science"], f"majors not stripped: {r['major'].tolist()}"
assert r["city"].tolist() == ["Amman", "Amman", "Irbid"], f"cities not tidied: {r['city'].tolist()}"
assert d["city"].tolist()[0] == "AMMAN", "do not change the original table"
```
:::

**Read more:** [Vectorized String Operations](https://jakevdp.github.io/PythonDataScienceHandbook/03.10-working-with-strings.html)

## 6 · Hierarchical indexing

### 6.1 · Two labels per row

Sometimes one label is not enough to identify a row. A grade belongs to a **student** in a **course**. Pandas can use both as the index, one level inside the other. This is called a hierarchical index, or `MultiIndex`.

```python run
import pandas as pd

grades = pd.DataFrame({
    "student": ["Ahmad", "Ahmad", "Sara", "Sara", "Omar", "Omar"],
    "course":  ["ML", "OOP", "ML", "OOP", "ML", "OOP"],
    "grade":   [89, 51, 74, 80, 92, 67],
})

by_both = grades.set_index(["student", "course"])["grade"]
print(by_both)
```

### 6.2 · Selecting with two levels

```python run
import pandas as pd

grades = pd.DataFrame({
    "student": ["Ahmad", "Ahmad", "Sara", "Sara", "Omar", "Omar"],
    "course":  ["ML", "OOP", "ML", "OOP", "ML", "OOP"],
    "grade":   [89, 51, 74, 80, 92, 67],
})
by_both = grades.set_index(["student", "course"])["grade"]

print(by_both.loc["Sara"])               # everything for one student
print(by_both.loc[("Sara", "OOP")])      # one student in one course
print(by_both.loc[:, "ML"])              # one course, every student
```

### 6.3 · Long and wide: `unstack` and `stack`

The same data can be laid out **long** (one row per student and course) or **wide** (one row per student, one column per course). `unstack` moves the inner level of the index into the columns, and `stack` moves it back.

```python run
import pandas as pd

grades = pd.DataFrame({
    "student": ["Ahmad", "Ahmad", "Sara", "Sara", "Omar", "Omar"],
    "course":  ["ML", "OOP", "ML", "OOP", "ML", "OOP"],
    "grade":   [89, 51, 74, 80, 92, 67],
})
by_both = grades.set_index(["student", "course"])["grade"]

wide = by_both.unstack()
print(wide)
print(wide.stack().head(3))
print(by_both.reset_index().head(3))     # back to ordinary columns
```

You will meet a `MultiIndex` most often as the **result** of grouping by two columns, which is next week's topic. `reset_index()` always turns it back into ordinary columns.

> **Good to know.** Older tutorials mention a three-dimensional Pandas object called `Panel`. It was removed from Pandas in 2019. A DataFrame with a hierarchical index does the same job and is what you should use.

**Read more:** [Hierarchical Indexing](https://jakevdp.github.io/PythonDataScienceHandbook/03.05-hierarchical-indexing.html)

## Summary

- A **Series** is values plus an index of labels. A **DataFrame** is several Series sharing one index.
- Use `loc` for labels and `iloc` for positions. A label slice includes its end; a position slice does not.
- Select rows with a mask; change values with a single `df.loc[rows, column] = value`.
- Operations match values by **label**. Labels found on one side only give `NaN`.
- Find missing values with `isna()`; choose between `dropna()` and `fillna()` deliberately, and report the choice.
- `pd.to_numeric(..., errors="coerce")` rescues a numeric column that was read as text.
- `.str` cleans a whole text column at once. Check categories with `value_counts()`.
- Two index levels describe data with two keys; `unstack` and `stack` switch between long and wide.

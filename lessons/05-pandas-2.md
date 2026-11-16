# Pandas II — Combining, Grouping, Pivoting and Time Series

<p class="lesson-intro">Week 5 · Programming for Data Science (606315)</p>

Last week ended with one clean table. Analysis starts when you **combine** tables, **group** rows to compare categories, **reshape** the result into something readable, and work with **dates**. This lesson covers all four and ends with the structure your Project Stage 1 notebook should follow.

> **About this lesson.** It follows the second half of Chapter 3 of the course textbook, Jake VanderPlas, *Python Data Science Handbook* (2nd ed., O'Reilly). The explanations, examples and diagrams are written for this course; each section ends with a "Read more" link to the matching section of the textbook's free online edition.
>
> **Helper notes.** Words in the code with a dotted underline have a short note. Hover over one (or tap it) to read what it does. A table that is the **last line** of an example is shown as a formatted table in the Output panel.

## 1 · Combining tables: `concat`

### 1.1 · Stacking rows

`pd.concat` glues tables together. By default it places them one **under** the other, which is what you need when the same kind of data arrives in several files.

```python run
import pandas as pd

section1 = pd.DataFrame({"name": ["Ahmad", "Sara"], "grade": [80, 65]})
section2 = pd.DataFrame({"name": ["Omar", "Lina"], "grade": [92, 71]})

both = pd.concat([section1, section2])
print(both)
```

Look at the index: 0, 1, 0, 1. Each table kept its own row labels, so the labels are now repeated. Ask for a fresh index instead.

```python run
import pandas as pd

section1 = pd.DataFrame({"name": ["Ahmad", "Sara"], "grade": [80, 65]})
section2 = pd.DataFrame({"name": ["Omar", "Lina"], "grade": [92, 71]})

both = pd.concat([section1, section2], ignore_index=True)
print(both)
```

### 1.2 · Columns that do not match

`concat` matches columns by **name**. A column that exists in only one table is filled with `NaN` for the rows of the other.

```python run
import pandas as pd

a = pd.DataFrame({"name": ["Ahmad"], "grade": [80]})
b = pd.DataFrame({"name": ["Omar"], "grade": [92], "bonus": [5]})

print(pd.concat([a, b], ignore_index=True))                  # keep every column
print(pd.concat([a, b], ignore_index=True, join="inner"))    # keep only shared columns
```

> **Look out.** Older tutorials use `df.append(other)`. That method was removed from Pandas; use `pd.concat([df, other])`. Also avoid calling `concat` inside a loop to add one row at a time: collect the pieces in a list and call `concat` once at the end.

**Read more:** [Combining Datasets: Concat and Append](https://jakevdp.github.io/PythonDataScienceHandbook/03.06-concat-and-append.html)

## 2 · Combining tables: `merge`

### 2.1 · Joining on a key

`concat` stacks. `merge` **joins**: it puts together rows from two tables that share the same value in a **key** column, as a database join does.

```python run
import pandas as pd

students = pd.DataFrame({"name": ["Ahmad", "Sara", "Omar"], "major": ["DS", "CS", "DS"]})
advisors = pd.DataFrame({"major": ["DS", "CS"], "advisor": ["Dr. Rana", "Dr. Sami"]})

print(pd.merge(students, advisors, on="major"))
```

Each major appears once in `advisors` and several times in `students`, so the advisor's name is repeated for every student of that major. This is a **many-to-one** join, the most common kind. When both tables have exactly one row per key the join is **one-to-one**. When the key repeats in both tables the join is **many-to-many**, and every matching pair of rows is produced.

Always name the key with `on=`. When the key column has different names in the two tables, use `left_on=` and `right_on=`.

### 2.2 · What happens to rows without a partner: `how`

A key that appears in only one table has no partner. The `how` argument decides whether such rows are kept.

![Two small tables joined on the name column in three ways. The inner join keeps only names found in both. The left join keeps every row of the left table. The outer join keeps every row of both. Missing cells are shown as NaN.](figures/merge.svg)

<p class="caption">The same two tables joined three ways. Rows without a partner are dropped by an inner join and kept, with NaN in the gaps, by a left or outer join.</p>

```python run
import pandas as pd

majors = pd.DataFrame({"name": ["Ahmad", "Sara", "Omar"], "major": ["DS", "CS", "DS"]})
grades = pd.DataFrame({"name": ["Sara", "Omar", "Lina"], "grade": [65, 92, 71]})

print(pd.merge(majors, grades, on="name", how="inner"))   # the default
print(pd.merge(majors, grades, on="name", how="left"))
print(pd.merge(majors, grades, on="name", how="outer"))
```

| `how` | Rows kept |
|---|---|
| `"inner"` (default) | only keys found in **both** tables |
| `"left"` | every row of the left table |
| `"right"` | every row of the right table |
| `"outer"` | every row of both tables |

:::challenge title="How many rows?"
The left table has the keys `A, B, C`. The right table has the keys `B, C, C, D`. How many rows does each join give?

1. `how="inner"`
2. `how="left"`
3. `how="outer"`

```python run
import pandas as pd

left = pd.DataFrame({"key": ["A", "B", "C"], "x": [1, 2, 3]})
right = pd.DataFrame({"key": ["B", "C", "C", "D"], "y": [10, 20, 30, 40]})

for how in ("inner", "left", "outer"):
    print(how, "->", len(pd.merge(left, right, on="key", how=how)), "rows")
```
---
1. **3 rows.** B matches once and C matches twice. A and D have no partner and are dropped.
2. **4 rows.** The 3 matches, plus A with `NaN` for `y`.
3. **5 rows.** The 3 matches, plus A, plus D.

The surprise is C. The left table has one C row, but the result has two, because the key is repeated on the right. **A merge can increase the number of rows.** Count the rows before and after every merge.
:::

### 2.3 · A real case: grades and course titles

`enrollments.csv` holds grades with a course code. `courses.json` holds the title of each course. Joining them should be simple.

```python run
import pandas as pd

enrollments = pd.read_csv("data/enrollments.csv")
courses = pd.read_json("data/courses.json", dtype={"code": str})

print(enrollments["course_code"].dtype, "|", courses["code"].dtype)

try:
    pd.merge(enrollments, courses, left_on="course_code", right_on="code")
except ValueError as err:
    print("ValueError:", str(err)[:70], "…")
```

The codes look the same to a person, but one column holds integers and the other holds text, so no value on one side can ever equal a value on the other. Pandas refuses to merge. Convert one side so that the types agree.

```python run
import pandas as pd

enrollments = pd.read_csv("data/enrollments.csv")
courses = pd.read_json("data/courses.json", dtype={"code": str})

enrollments["course_code"] = enrollments["course_code"].astype(str)

full = pd.merge(enrollments, courses, left_on="course_code", right_on="code", how="left")
print(len(enrollments), "rows before,", len(full), "rows after")
print("grades without a course title:", full["title"].isna().sum())
full[["student_id", "title", "semester", "grade"]].head()
```

> **Look out: three checks for every merge.**
> - **Types.** The key columns must have the same type. Text against numbers either fails, as above, or silently matches nothing.
> - **Row count.** Compare `len()` before and after. More rows than you expected means the key is repeated where you assumed it was unique.
> - **Unmatched rows.** With `how="left"`, count the `NaN`s in a column that came from the right table. Adding `indicator=True` gives a `_merge` column that says where each row came from.

:::exercise id=q1 title="Average grade per course title"
Complete `average_by_title(enrollments, courses)`. `enrollments` has the columns `course_code` and `grade`; `courses` has `code` and `title`. Both code columns are already text. Return a **Series** of the mean grade for each course title, indexed by title.

```python
import pandas as pd

def average_by_title(enrollments, courses):
    joined = ...
    return ...

e = pd.DataFrame({"course_code": ["1", "1", "2"], "grade": [80, 60, 90]})
c = pd.DataFrame({"code": ["1", "2"], "title": ["ML", "OOP"]})
print(average_by_title(e, c))
```

```python check
import pandas as pd
e = pd.DataFrame({"course_code": ["1", "1", "2", "2", "2"], "grade": [80, 60, 90, 70, 50]})
c = pd.DataFrame({"code": ["1", "2", "3"], "title": ["ML", "OOP", "Big Data"]})
r = average_by_title(e, c)
assert isinstance(r, pd.Series), "return a Series (select the grade column before taking the mean)"
assert round(float(r["ML"]), 2) == 70.0 and round(float(r["OOP"]), 2) == 70.0, f"wrong means: {r.to_dict()}"
assert "Big Data" not in r.index or pd.isna(r["Big Data"]), "a course with no grades has no mean"
```
:::

**Read more:** [Combining Datasets: Merge and Join](https://jakevdp.github.io/PythonDataScienceHandbook/03.07-merge-and-join.html)

## 3 · Aggregation and grouping

### 3.1 · One number for the whole table

An **aggregation** reduces many values to one summary value. On a whole column it gives a single number.

```python run
import pandas as pd

df = pd.DataFrame({
    "major": ["DS", "CS", "AI", "DS", "CS", "AI"],
    "gpa":   [3.0, 2.0, 3.5, 4.0, 3.0, 2.5],
})

print("mean GPA of everyone:", df["gpa"].mean())
print(df["gpa"].describe().round(2))
```

That answers "what is the average GPA?" The more useful question is usually "what is the average GPA **in each major**?"

### 3.2 · Split, apply, combine

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

### 3.3 · Four things to do with a group

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

### 3.4 · A summary table from real data

Named aggregations build a whole summary in one statement: each line reads `new_column=(source_column, function)`.

```python run
import pandas as pd

students = pd.read_csv("data/students.csv")
students["major"] = students["major"].str.strip()
students["gpa"] = pd.to_numeric(students["gpa"], errors="coerce")
students = students.drop_duplicates()

summary = students.groupby("major").agg(
    students=("student_id", "size"),
    mean_gpa=("gpa", "mean"),
    best_gpa=("gpa", "max"),
    cities=("city", "nunique"),
).round(2).sort_values("mean_gpa", ascending=False)
summary
```

Grouping by two columns gives a result with two index levels, as described at the end of last week's lesson. `unstack` turns it into a readable grid.

```python run
import pandas as pd

students = pd.read_csv("data/students.csv")
students["major"] = students["major"].str.strip()
students["gpa"] = pd.to_numeric(students["gpa"], errors="coerce")

by_two = students.groupby(["major", "year"])["gpa"].mean().round(2)
print(by_two.head(6))
by_two.unstack()
```

> **Look out.**
> - **Clean before you group.** `"AI"` and `" AI "` are two different groups. That is why the example strips the major first.
> - **Missing keys disappear.** Rows whose group key is missing (`NaN`) are left out of every group by default. Pass `dropna=False` to `groupby` to keep them as a group of their own.
> - **Choose the column before you aggregate.** `df.groupby("major").mean()` tries to average *every* other column and raises an error if one of them holds text. Write `df.groupby("major")["gpa"].mean()`, or pass `numeric_only=True`.
> - **The group labels become the index.** To get them back as an ordinary column, add `.reset_index()` to the result.

:::exercise id=q2 title="Students above their own major's average"
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

**Read more:** [Aggregation and Grouping](https://jakevdp.github.io/PythonDataScienceHandbook/03.08-aggregation-and-grouping.html)

## 4 · Pivot tables

### 4.1 · A grid from two keys

A **pivot table** is a grouping by two columns, shown as a grid: one key runs down the rows, the other across the columns, and each cell holds a summary of the rows that have both.

![A long table with one row per city and product is turned into a wide grid with one row per city and one column per product.](figures/pivot.svg)

<p class="caption">Long on the left, wide on the right. Each cell of the grid is the total of the rows with that city and that product.</p>

```python run
import pandas as pd

sales = pd.DataFrame({
    "city":    ["Amman", "Amman", "Irbid", "Irbid", "Amman", "Irbid"],
    "product": ["Laptop", "Phone", "Laptop", "Phone", "Laptop", "Phone"],
    "units":   [3, 5, 2, 4, 1, 6],
})

print(sales.pivot_table(values="units", index="city", columns="product", aggfunc="sum"))
```

It is the same result as `groupby` with two keys followed by `unstack`, written in a form that says directly what goes where.

```python run
import pandas as pd

sales = pd.DataFrame({
    "city":    ["Amman", "Amman", "Irbid", "Irbid", "Amman", "Irbid"],
    "product": ["Laptop", "Phone", "Laptop", "Phone", "Laptop", "Phone"],
    "units":   [3, 5, 2, 4, 1, 6],
})

print(sales.groupby(["city", "product"])["units"].sum().unstack())
```

### 4.2 · On real data, with totals

```python run
import pandas as pd

sales = pd.read_csv("data/sales_2025.csv")
sales["revenue"] = sales["units"] * sales["unit_price"]

table = sales.pivot_table(values="revenue", index="city", columns="product",
                          aggfunc="sum", margins=True, margins_name="Total")
table.round(0)
```

> **Look out.** The default `aggfunc` is the **mean**, not the sum. For money and counts you almost always want `aggfunc="sum"`, so write it every time. A combination that never occurs in the data gives `NaN` in its cell; `fill_value=0` shows 0 instead.

:::exercise id=q3 title="Units sold: city by product"
Complete `units_grid(sales)` so that it returns a table with one row per `city`, one column per `product`, and the **total** `units` in each cell.

```python
import pandas as pd

def units_grid(sales):
    return ...

demo = pd.DataFrame({
    "city":    ["Amman", "Amman", "Irbid", "Amman"],
    "product": ["Laptop", "Phone", "Laptop", "Laptop"],
    "units":   [3, 5, 2, 1],
})
print(units_grid(demo))
```

```python check
import pandas as pd
d = pd.DataFrame({"city": ["Amman", "Amman", "Irbid", "Amman", "Irbid"],
                  "product": ["Laptop", "Phone", "Laptop", "Laptop", "Phone"],
                  "units": [3, 5, 2, 1, 7]})
r = units_grid(d)
assert isinstance(r, pd.DataFrame), "return a DataFrame"
assert sorted(r.index) == ["Amman", "Irbid"] and sorted(r.columns) == ["Laptop", "Phone"], "rows are cities, columns are products"
assert r.loc["Amman", "Laptop"] == 4, f"Amman sold 3 + 1 laptops; got {r.loc['Amman', 'Laptop']} (is your aggfunc the sum?)"
assert r.loc["Irbid", "Phone"] == 7 and r.loc["Amman", "Phone"] == 5
```
:::

**Read more:** [Pivot Tables](https://jakevdp.github.io/PythonDataScienceHandbook/03.09-pivot-tables.html)

## 5 · Working with time series

### 5.1 · Text is not a date

A date read from a file is text until you convert it. Only after conversion can Pandas compare dates, pick out the month, or measure the time between two of them.

```python run
import pandas as pd

sales = pd.read_csv("data/sales_2025.csv")
print(sales["date"].dtype)

sales["date"] = pd.to_datetime(sales["date"])
print(sales["date"].dtype)
print(sales["date"].min(), "to", sales["date"].max())
```

A date column has a `.dt` attribute, in the same way that a text column has `.str`.

```python run
import pandas as pd

sales = pd.read_csv("data/sales_2025.csv")
sales["date"] = pd.to_datetime(sales["date"])

sales["month"] = sales["date"].dt.month
sales["weekday"] = sales["date"].dt.day_name()
print(sales[["date", "month", "weekday"]].head(3))
print(sales.groupby("weekday")["units"].sum().sort_values(ascending=False).head(3))
```

### 5.2 · Dates as the index

When the dates become the index, you can select a period by writing it as text.

```python run
import pandas as pd

sales = pd.read_csv("data/sales_2025.csv")
sales["date"] = pd.to_datetime(sales["date"])
sales["revenue"] = sales["units"] * sales["unit_price"]

daily = sales.groupby("date")["revenue"].sum()     # one value per day, indexed by date

print(daily.loc["2025-03-01"].round(2))            # one day
print(len(daily.loc["2025-03"]), "days in March")  # a whole month
print(daily.loc["2025-03-10":"2025-03-12"].round(2))
```

### 5.3 · Resampling, rolling and shifting

Three operations cover most time-series questions.

- **`resample`** is a `groupby` for time: it groups the rows into regular periods such as weeks or months.
- **`rolling`** computes over a moving window, which smooths out day-to-day noise.
- **`shift`** moves the values in time, which lets you compare each day with an earlier one.

```python run
import pandas as pd

sales = pd.read_csv("data/sales_2025.csv")
sales["date"] = pd.to_datetime(sales["date"])
sales["revenue"] = sales["units"] * sales["unit_price"]
daily = sales.groupby("date")["revenue"].sum()

monthly = daily.resample("ME").sum()               # "ME" = month end
print(monthly.round(0).head(4))

smooth = daily.rolling(7).mean()                   # 7-day moving average
print(smooth.round(0).head(8))

change = daily - daily.shift(1)                    # today minus yesterday
print(change.round(0).head(3))
```

> **Look out.**
> - The first six values of a 7-day rolling mean are `NaN`, because a full window does not exist yet. That is correct, not an error.
> - `resample` works only when the index (or the column named with `on=`) holds real dates. If you get `TypeError: Only valid with DatetimeIndex`, the dates are still text.
> - Dates such as `03/04/2025` are ambiguous. Pandas reads them month-first unless you pass `dayfirst=True`, so state the format when the file does not use year-month-day.

:::challenge title="resample or rolling?"
`daily` holds one revenue value for each of the 365 days of 2025. How many values does each result have?

1. `daily.resample("ME").sum()`
2. `daily.rolling(30).mean()`
---
1. **12**, one per month. `resample` reduces: each period becomes one row.
2. **365**, the same as `daily`, of which the first 29 are `NaN`. `rolling` does not reduce: every day gets a value computed from the window that ends on it.

This is the same distinction as `agg` and `transform` in Section 3.
:::

:::exercise id=q4 title="The best month"
`sales` has the columns `date` (as text), `units` and `unit_price`. Complete `best_month(sales)` so that it returns the **number of the month** (1 to 12) with the highest total revenue, where revenue is `units * unit_price`.

```python
import pandas as pd

def best_month(sales):
    df = sales.copy()
    ...
    return ...

demo = pd.DataFrame({"date": ["2025-01-05", "2025-02-10", "2025-02-11"],
                     "units": [1, 2, 3], "unit_price": [100.0, 100.0, 100.0]})
print(best_month(demo))
```

```python check
import pandas as pd
d = pd.DataFrame({"date": ["2025-01-05", "2025-02-10", "2025-02-11", "2025-11-30", "2025-11-01"],
                  "units": [1, 2, 3, 10, 1], "unit_price": [100.0, 100.0, 100.0, 60.0, 10.0]})
r = best_month(d)
assert r is not None and int(r) == 11, f"November has the highest revenue (610); got {r}"
d2 = pd.DataFrame({"date": ["2025-03-01", "2025-07-01"], "units": [5, 1], "unit_price": [1.0, 100.0]})
assert int(best_month(d2)) == 7, "use revenue (units * unit_price), not units alone"
```
:::

**Read more:** [Working with Time Series](https://jakevdp.github.io/PythonDataScienceHandbook/03.11-working-with-time-series.html)

## 6 · A shorter way to filter: `query`

A long mask is hard to read. `query` takes the condition as text, with column names written directly and the ordinary words `and` and `or`.

```python run
import pandas as pd

students = pd.read_csv("data/students.csv")
students["major"] = students["major"].str.strip()
students["gpa"] = pd.to_numeric(students["gpa"], errors="coerce")

a = students[(students["gpa"] > 3.7) & (students["major"] == "AI")]
b = students.query("gpa > 3.7 and major == 'AI'")

print(len(a), len(b))
b[["name", "major", "gpa"]].head()
```

Both lines select the same rows. Use `@` to refer to a Python variable inside the text: `students.query("gpa > @limit")`.

**Read more:** [High-Performance Pandas: eval() and query()](https://jakevdp.github.io/PythonDataScienceHandbook/03.12-performance-eval-and-query.html)

## 7 · Putting it together: the Project Stage 1 structure

This section is not from the textbook. It shows how the tools of Weeks 4 and 5 fit into the exploratory analysis you will hand in for Project Stage 1. Your notebook should follow these six steps, each with a sentence of commentary and the code that supports it.

1. **Load**: shape, columns, types.
2. **Audit**: missing values, duplicates, inconsistent categories, suspicious ranges.
3. **Clean**: fix what you found, and say what you did and why.
4. **One variable at a time**: the distribution of each key variable.
5. **Relationships**: `groupby`, `pivot_table`, correlations.
6. **Findings**: three to five statements, each backed by a number from above.

```python run
import pandas as pd

raw = pd.read_csv("data/students.csv")

# 1 Load, 2 Audit
print(raw.shape)
print(pd.DataFrame({"type": raw.dtypes.astype(str), "missing": raw.isna().sum(), "distinct": raw.nunique()}))
print("duplicate rows:", raw.duplicated().sum())

# 3 Clean
df = raw.copy()
df["major"] = df["major"].str.strip()
df["city"] = df["city"].str.title()
df["gpa"] = pd.to_numeric(df["gpa"], errors="coerce")
df = df.drop_duplicates().reset_index(drop=True)
print(len(raw), "rows ->", len(df), "rows;", df["gpa"].isna().sum(), "GPAs missing")

# 4 One variable at a time, 5 Relationships
print(df[["gpa", "credits", "year"]].describe().round(2))
print(df.groupby("major")["gpa"].agg(["count", "mean", "std"]).round(2))
print(df[["gpa", "credits", "year"]].corr().round(2))
```

A finding is a sentence with a number in it, for example: "The file has 205 rows, of which 5 are exact duplicates, leaving 200 students." Write yours from the output above, and state every cleaning decision you made.

## Summary

- `pd.concat` stacks tables; use `ignore_index=True` for a fresh index.
- `pd.merge` joins on a key. `how` decides what happens to rows without a partner. Check key types, the row count, and unmatched rows every time.
- `groupby` splits; then `agg` gives one row per group, `transform` one row per original row, `filter` keeps or drops whole groups, and `apply` runs any function.
- `pivot_table` is a two-key grouping shown as a grid. Write `aggfunc` explicitly.
- Convert dates with `pd.to_datetime`; use `.dt` for parts of a date, `resample` to reduce to periods, `rolling` for moving windows and `shift` for comparisons over time.
- `query` writes a filter as readable text.

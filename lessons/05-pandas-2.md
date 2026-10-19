# Pandas II — GroupBy, Merge, Pivot, Time Series

<p class="lesson-intro">Week 5 · Programming for Data Science (606315)</p>

With a clean table in hand, analysis is mostly four operations: **group** it, **join** it to other tables, **reshape** it, and — for dated data — **resample** it. This lesson covers all four and ends with the EDA structure your Project Stage 1 notebook should follow.

Every example starts by loading and cleaning `students.csv` the same way, so each box runs on its own.

## 1 · GroupBy — split, apply, combine

`groupby` splits the frame by a key, applies a function to each piece, and combines the results. It is Pandas' `GROUP BY`, and the heart of every summary table.

```python run
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(), city=lambda d: d["city"].str.title(),
                   gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))

print(clean.groupby("major")["gpa"].mean().round(2))

summary = (clean.groupby("major")
                .agg(n=("student_id", "size"),
                     mean_gpa=("gpa", "mean"),
                     max_gpa=("gpa", "max"),
                     missing_gpa=("gpa", lambda s: s.isna().sum()),
                     cities=("city", "nunique"))
                .round(2)
                .sort_values("mean_gpa", ascending=False))
summary
```

Two keys give a `MultiIndex`; `unstack` moves the inner key into columns. `transform` broadcasts a group statistic back to every row; `filter` keeps whole groups that satisfy a condition.

```python run
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(), gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))

print(clean.groupby(["major", "year"])["gpa"].mean().unstack().round(2))

g = clean.groupby("major")["gpa"]
clean["gpa_z_in_major"] = (clean["gpa"] - g.transform("mean")) / g.transform("std")
print(clean[["name", "major", "gpa", "gpa_z_in_major"]].head().round(2))

big = clean.groupby("major").filter(lambda d: len(d) >= 40)
print(big["major"].value_counts())
```

:::exercise id=ex1 title="City report"
`city_report(df)` returns a DataFrame indexed by `city` with columns `students` (count), `mean_gpa` (2 dp) and `top_major` (the most common major in that city — hint: `s.mode()[0]`), sorted by `students` descending.

```python
import pandas as pd

def city_report(df):
    return (df.groupby("city")
              .agg(students=(...),
                   mean_gpa=(...),
                   top_major=(...))
              .round({"mean_gpa": 2})
              .sort_values("students", ascending=False))

clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(), city=lambda d: d["city"].str.title(),
                   gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))
city_report(clean)
```

```python check
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(), city=lambda d: d["city"].str.title(),
                   gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))
r = city_report(clean)
assert list(r.columns) == ["students", "mean_gpa", "top_major"], f"columns {list(r.columns)}"
assert r["students"].is_monotonic_decreasing, "sort by students descending"
assert r["students"].sum() == len(clean)
assert r.loc["Amman", "top_major"] == clean[clean["city"] == "Amman"]["major"].mode()[0]
assert abs(r.loc["Amman", "mean_gpa"] - round(clean[clean["city"] == "Amman"]["gpa"].mean(), 2)) < 1e-9
```
:::

## 2 · Merge, join, concat

`enrollments.csv` has one row per (student, course). Joining student names onto it is a **left merge** on `student_id`; course titles come from `courses.json`. Always know which `how=` you want, and use `indicator=True` when you are unsure both sides match.

```python run
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(), gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))
enr = pd.read_csv("data/enrollments.csv")
courses = pd.read_json("data/courses.json")
print(enr.shape, courses.shape)

full = (enr.merge(clean[["student_id", "name", "major"]], on="student_id", how="left")
           .merge(courses, left_on="course_code", right_on="code", how="left")
           .drop(columns="code"))
print(full.shape)

chk = enr.merge(clean[["student_id"]], on="student_id", how="outer", indicator=True)
print(chk["_merge"].value_counts())

part1, part2 = clean.iloc[:100], clean.iloc[100:]
print(pd.concat([part1, part2]).shape == clean.shape)      # concat stacks vertically
full.head()
```

:::exercise id=ex2 title="Grades with names"
`grades_with_names(students, enr)` returns one row per enrollment with columns `student_id, name, major, course_code, grade`, keeping **only** enrollments whose student exists in `students` (an inner join), and dropping rows with a missing grade.

```python
import pandas as pd

def grades_with_names(students, enr):
    return (enr.merge(..., on="student_id", how=...)
               .dropna(subset=[...])
               [["student_id", "name", "major", "course_code", "grade"]]
               .reset_index(drop=True))

clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip())
           .drop_duplicates().reset_index(drop=True))
enr = pd.read_csv("data/enrollments.csv")
g = grades_with_names(clean, enr)
print(g.shape)
g.head()
```

```python check
import pandas as pd
clean = (pd.read_csv("data/students.csv").assign(major=lambda d: d["major"].str.strip())
           .drop_duplicates().reset_index(drop=True))
enr = pd.read_csv("data/enrollments.csv")
g = grades_with_names(clean, enr)
assert list(g.columns) == ["student_id", "name", "major", "course_code", "grade"], f"columns {list(g.columns)}"
assert g["grade"].notna().all(), "drop missing grades"
assert g["name"].notna().all(), "every row needs a name (inner join)"
assert len(g) == enr["grade"].notna().sum(), f"{len(g)} rows"
```
:::

## 3 · Pivot tables and reshaping

A pivot table is a groupby with two keys laid out as rows × columns; `melt` is its inverse (wide → long); `crosstab` counts.

```python run
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(), gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))
enr = pd.read_csv("data/enrollments.csv")
courses = pd.read_json("data/courses.json")
full = (enr.merge(clean[["student_id", "major"]], on="student_id")
           .merge(courses, left_on="course_code", right_on="code"))

pt = full.pivot_table(index="major", columns="title", values="grade", aggfunc="mean").round(1)
print(pt)
print()
print(pt.reset_index().melt(id_vars="major", var_name="course", value_name="mean_grade").head())
print()
clean["standing"] = pd.cut(clean["gpa"], bins=[0, 2, 3.5, 4], labels=["probation", "good", "honours"])
pd.crosstab(clean["major"], clean["standing"], margins=True)
```

:::exercise id=ex3 title="Grade pivot with an overall column"
Using the result of Exercise 2, return a pivot of **mean grade** with majors as rows and course codes as columns, plus a final column `overall` holding each major's mean over all its enrollments (not the mean of the row means). Round to 1 dp.

```python
import pandas as pd

def grade_pivot(g):
    p = g.pivot_table(index=..., columns=..., values=..., aggfunc="mean")
    p["overall"] = ...
    return p.round(1)

clean = (pd.read_csv("data/students.csv").assign(major=lambda d: d["major"].str.strip())
           .drop_duplicates().reset_index(drop=True))
enr = pd.read_csv("data/enrollments.csv")
g = (enr.merge(clean[["student_id", "name", "major"]], on="student_id").dropna(subset=["grade"]))
grade_pivot(g)
```

```python check
import pandas as pd
clean = (pd.read_csv("data/students.csv").assign(major=lambda d: d["major"].str.strip())
           .drop_duplicates().reset_index(drop=True))
enr = pd.read_csv("data/enrollments.csv")
g = enr.merge(clean[["student_id", "name", "major"]], on="student_id").dropna(subset=["grade"])
p = grade_pivot(g)
assert p.index.name == "major" and "overall" in p.columns, "index must be major, with an overall column"
assert set(p.columns) - {"overall"} == set(g["course_code"].unique()), "one column per course code"
ds = round(g[g["major"] == "Data Science"]["grade"].mean(), 1)
assert abs(p.loc["Data Science", "overall"] - ds) < 1e-9, "overall must be the mean over all enrollments"
```
:::

## 4 · Time series

Parse dates on load (`parse_dates=`), and the resample/rolling toolkit opens up. `"ME"` is month-end; the `.dt` accessor extracts calendar features.

```python run
import pandas as pd
sales = pd.read_csv("data/sales_2025.csv", parse_dates=["date"])
sales["revenue"] = sales["units"] * sales["unit_price"]
print(sales.dtypes["date"])

daily = sales.groupby("date")["revenue"].sum()
print(daily.resample("ME").sum().round(0))

sales["weekday"] = sales["date"].dt.day_name()
print(sales.groupby("weekday")["revenue"].mean().round(0).sort_values(ascending=False))

rolling = daily.rolling(window=7).mean()
pd.DataFrame({"daily": daily, "7d_avg": rolling}).iloc[5:12].round(0)
```

:::exercise id=ex4 title="Monthly revenue by product"
`monthly_product_revenue(sales)` returns a DataFrame indexed by month-end with one column per product, holding total revenue (units × unit_price) rounded to 0 dp. Hint: `pivot_table` on the date, then `.resample("ME").sum()`.

```python
import pandas as pd

def monthly_product_revenue(sales):
    s = sales.assign(revenue=sales["units"] * sales["unit_price"])
    ...

sales = pd.read_csv("data/sales_2025.csv", parse_dates=["date"])
monthly_product_revenue(sales)
```

```python check
import pandas as pd
sales = pd.read_csv("data/sales_2025.csv", parse_dates=["date"])
m = monthly_product_revenue(sales)
assert m.shape == (12, 5), f"shape {m.shape} — expected 12 months x 5 products"
assert set(m.columns) == set(sales["product"].unique())
assert m.index[0].month == 1 and m.index[-1].month == 12
assert abs(m.values.sum() - (sales["units"] * sales["unit_price"]).sum()) < 5, "totals must match"
```
:::

## 5 · Quick plots

`df.plot()` wraps Matplotlib; the figure appears in the output panel. Good enough for EDA.

```python run
import pandas as pd
import matplotlib.pyplot as plt
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(), gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))
sales = pd.read_csv("data/sales_2025.csv", parse_dates=["date"])
daily = sales.assign(rev=sales["units"] * sales["unit_price"]).groupby("date")["rev"].sum()

fig, axes = plt.subplots(1, 3, figsize=(13, 3.4))
clean["gpa"].plot.hist(bins=20, ax=axes[0], title="GPA distribution")
clean.groupby("major")["gpa"].mean().plot.bar(ax=axes[1], title="Mean GPA by major", rot=30)
daily.rolling(7).mean().plot(ax=axes[2], title="Revenue, 7-day average")
plt.tight_layout()
```

:::exercise id=ex5 title="Best week"
`best_week(sales)` returns the `pd.Timestamp` of the **end** of the 7-day window with the highest total revenue: daily totals → rolling sum of 7 → `idxmax()`.

```python
import pandas as pd

def best_week(sales):
    daily = ...
    return ...

sales = pd.read_csv("data/sales_2025.csv", parse_dates=["date"])
print(best_week(sales))
```

```python check
import pandas as pd
sales = pd.read_csv("data/sales_2025.csv", parse_dates=["date"])
b = best_week(sales)
assert isinstance(b, pd.Timestamp), "return a Timestamp"
daily = sales.assign(rev=sales["units"] * sales["unit_price"]).groupby("date")["rev"].sum()
assert b == daily.rolling(7).sum().idxmax(), f"got {b.date()}"
```
:::

## 6 · A complete EDA — the Stage 1 structure

Your project notebook should follow these six headings, each with a sentence of commentary and the code that supports it:

1. **Load** — shape, columns, dtypes.
2. **Audit** — missing values, duplicates, inconsistent categories, suspicious ranges.
3. **Clean** — fix what you found; say what you did and why.
4. **Univariate** — distribution of each key variable.
5. **Bivariate / group** — `groupby`, `pivot_table`, `crosstab`, correlations.
6. **Findings** — 3–5 bullets, each backed by a number from above.

```python run
import pandas as pd
raw = pd.read_csv("data/students.csv")

# 1 Load   2 Audit
print(raw.shape)
audit = pd.DataFrame({"dtype": raw.dtypes, "missing": raw.isna().sum(), "unique": raw.nunique()})
print(audit); print("duplicates:", raw.duplicated().sum())

# 3 Clean
df = (raw.assign(major=lambda d: d["major"].str.strip(), city=lambda d: d["city"].str.title(),
                 gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
         .drop_duplicates().reset_index(drop=True))
print(f"{len(raw)} → {len(df)} rows; {df['gpa'].isna().sum()} GPAs missing (kept as NaN)")

# 4 Univariate   5 Bivariate
print(df[["gpa", "credits", "year"]].describe().round(2))
print(df.groupby("major")["gpa"].agg(["count", "mean", "std"]).round(2))
print(df[["gpa", "credits", "year"]].corr().round(2))
```

**6 · Findings (example).** 205 raw rows contain 5 exact duplicates → 200 students. About 5 % of GPAs were unparseable and are kept as missing rather than imputed, because they are few and look random. Mean GPA is similar across majors (≈ 2.85–2.97), smaller than one standard deviation (≈ 0.5), so no major stands out. `credits` and `year` are positively correlated as expected; GPA is uncorrelated with both.

## Summary

* `groupby().agg()` for summary tables; `transform` to broadcast back; `filter` to keep groups.
* `merge` with an explicit `how=`; `indicator=True` to validate; `concat` to stack.
* `pivot_table` / `melt` / `crosstab` to reshape.
* `parse_dates` → `.dt`, `.resample("ME")`, `.rolling(7)`.
* Six EDA headings → Project Stage 1.

Next: *JSON* — the format every API speaks.

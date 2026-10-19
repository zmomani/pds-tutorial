# Pandas I — Load, Select, Clean

<p class="lesson-intro">Week 4 · Programming for Data Science (606315)</p>

Pandas puts **labels** on NumPy arrays. A `DataFrame` is a table whose columns are typed arrays sharing a row index; masks, broadcasting and `axis` all still apply. This lesson takes a dirty CSV from first look to a clean table — the first half of every data project.

> A DataFrame that is the **last expression** of your code is shown as a table in the output panel, just as in a notebook. `print(df)` gives plain text instead.

## 1 · Series and DataFrame

```python run
import pandas as pd

s = pd.Series([3.4, 2.1, 3.9], index=["Ahmad", "Sara", "Omar"], name="gpa")
print(s)
print("label access:", s["Sara"], "  position access:", s.iloc[1])

df = pd.DataFrame({
    "name":  ["Ahmad", "Sara", "Omar", "Lina"],
    "major": ["DS", "CS", "DS", "AI"],
    "gpa":   [3.4, 2.1, 3.9, 3.2],
    "year":  [2, 4, 1, 3],
})
print(df.shape, df.columns.tolist())
print(df.dtypes)
df
```

## 2 · Loading and the five-command inspection

Run these on **every** new dataset before doing anything else: `head`, `info`, `describe`, `isna().sum()`, `nunique`.

```python run
import pandas as pd
students = pd.read_csv("data/students.csv")
students.head()
```

```python run
import pandas as pd
students = pd.read_csv("data/students.csv")
students.info()
```

`gpa` loaded as **object**, not float — a sign of dirty values. `describe()` summarises numeric columns; `describe(include="object")` the text ones.

```python run
import pandas as pd
students = pd.read_csv("data/students.csv")
print(students.describe().round(2))
print()
print(students.describe(include="object").T)
print()
print(students.isna().sum())
print()
print(students.nunique())
```

:::exercise id=ex1 title="Inspection report"
Write `report(df)` that returns a dict with `rows`, `cols`, `missing` (a dict `column → count`, **only** columns with at least one missing value) and `object_cols` (a list of column names with dtype `object`).

```python
import pandas as pd

def report(df):
    return {
        "rows": ...,
        "cols": ...,
        "missing": ...,
        "object_cols": ...,
    }

print(report(pd.read_csv("data/students.csv")))
```

```python check
import pandas as pd
df = pd.read_csv("data/students.csv")
r = report(df)
assert r["rows"] == 205 and r["cols"] == 8, f"{r['rows']}x{r['cols']}"
assert r["missing"] == {"gpa": int(df["gpa"].isna().sum())}, f"missing: {r['missing']}"
assert set(r["object_cols"]) == {"name", "major", "city", "gpa", "email"}, f"object_cols: {r['object_cols']}"
```
:::

## 3 · Selecting data

| Want | Use |
|---|---|
| one column | `df["col"]` |
| several columns | `df[["a", "b"]]` |
| rows by **label** (and columns) | `df.loc[rows, cols]` |
| rows by **position** | `df.iloc[rows, cols]` |
| rows by condition | `df[mask]` or `df.loc[mask, cols]` |
| SQL-style string filter | `df.query("gpa > 3 and year == 4")` |

```python run
import pandas as pd
students = pd.read_csv("data/students.csv")

print(students.loc[0, "name"], "|", students.iloc[0, 1])    # same cell, label vs position
print(students.iloc[2:5, :3])

seniors_amman = students[(students["year"] == 4) & (students["city"] == "Amman")]
print(len(seniors_amman), "rows")
print(students.query("year == 4 and city == 'Amman'").equals(seniors_amman))
seniors_amman[["name", "major", "gpa"]].head()
```

:::exercise id=ex2 title="Filter and project"
Return a DataFrame with columns `name, major` for students in **year 1 or 2** whose `city` is `Irbid` or `Zarqa`, sorted by name. Hint: `.isin()`.

```python
import pandas as pd

def juniors_north(df):
    mask = ...
    return df.loc[mask, ["name", "major"]].sort_values("name")

students = pd.read_csv("data/students.csv")
juniors_north(students)
```

```python check
import pandas as pd
df = pd.read_csv("data/students.csv")
r = juniors_north(df)
assert list(r.columns) == ["name", "major"], f"columns {list(r.columns)}"
assert set(df.loc[r.index, "year"]) <= {1, 2}, "years must be 1 or 2"
assert set(df.loc[r.index, "city"]) <= {"Irbid", "Zarqa"}, "cities must be Irbid or Zarqa"
expected = df[df["year"].isin([1, 2]) & df["city"].isin(["Irbid", "Zarqa"])]
assert len(r) == len(expected), f"{len(r)} rows, expected {len(expected)}"
assert r["name"].is_monotonic_increasing, "sort by name"
```
:::

## 4 · Cleaning

`students.csv` was deliberately dirtied: `unknown` and blank GPAs, stray whitespace in `major`, upper-case cities, and five duplicate rows. This is the normal state of real data.

```python run
import pandas as pd
students = pd.read_csv("data/students.csv")
print(students["major"].unique())
print(students["city"].unique())
print("duplicates:", students.duplicated().sum())
print("non-numeric gpa tokens:", students.loc[pd.to_numeric(students["gpa"], errors="coerce").isna(), "gpa"].unique())
```

The `.str` accessor applies string methods to a whole column; `pd.to_numeric(errors="coerce")` turns anything unparseable into `NaN`.

```python run
import pandas as pd
students = pd.read_csv("data/students.csv")

clean = students.copy()
clean["major"] = clean["major"].str.strip()
clean["city"]  = clean["city"].str.title()
clean["gpa"]   = pd.to_numeric(clean["gpa"], errors="coerce")
clean = clean.drop_duplicates().reset_index(drop=True)

print(clean["major"].unique(), clean["city"].unique())
print(clean.dtypes["gpa"], "| rows:", len(students), "→", len(clean))
```

The same cleaning as one chained expression — the style you will see in production code. `assign` with a `lambda` lets each step refer to the frame as it is *at that point* in the chain.

```python run
import pandas as pd
students = pd.read_csv("data/students.csv")

clean = (students
         .assign(major=lambda d: d["major"].str.strip(),
                 city=lambda d: d["city"].str.title(),
                 gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
         .drop_duplicates()
         .reset_index(drop=True))
clean.head()
```

:::exercise id=ex3 title="Audit before you clean"
`audit(raw)` takes the **raw** frame and returns a dict: `duplicates` (count of duplicate rows), `bad_gpa` (count of non-numeric, non-blank GPA tokens), `blank_gpa` (count of missing GPAs), `untrimmed_major` (rows whose major has leading/trailing spaces), `upper_city` (rows whose city is entirely upper-case). Return plain `int`s.

```python
import pandas as pd

def audit(raw):
    gpa_num = pd.to_numeric(raw["gpa"], errors="coerce")
    blank = raw["gpa"].isna()
    return {
        "duplicates": int(raw.duplicated().sum()),
        "bad_gpa": ...,
        "blank_gpa": ...,
        "untrimmed_major": ...,
        "upper_city": ...,
    }

print(audit(pd.read_csv("data/students.csv")))
```

```python check
import pandas as pd
a = audit(pd.read_csv("data/students.csv"))
assert set(a) == {"duplicates", "bad_gpa", "blank_gpa", "untrimmed_major", "upper_city"}
assert a["duplicates"] == 5, a
assert a["bad_gpa"] == 3, f"bad_gpa {a['bad_gpa']} (expected 3: the 'unknown' tokens)"
assert a["blank_gpa"] == 8, f"blank_gpa {a['blank_gpa']}"
assert a["untrimmed_major"] == 6, f"untrimmed_major {a['untrimmed_major']}"
assert a["upper_city"] == 3, f"upper_city {a['upper_city']}"
assert all(isinstance(v, int) for v in a.values()), "return plain ints"
```
:::

## 5 · Missing values

`NaN` propagates through arithmetic and is **skipped** by aggregations. Decide column by column whether to drop, fill, or flag — and write down why.

```python run
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(),
                   gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))

print(clean["gpa"].isna().sum(), "missing GPAs;  mean skips them:", clean["gpa"].mean().round(3))

dropped  = clean.dropna(subset=["gpa"])                                        # 1. drop rows
filled   = clean.fillna({"gpa": clean["gpa"].median()})                        # 2. fill with a statistic
by_major = clean["gpa"].fillna(clean.groupby("major")["gpa"].transform("median"))  # 3. group-wise fill
flagged  = clean.assign(gpa_missing=clean["gpa"].isna())                       # 4. keep the information

print(len(dropped), filled["gpa"].isna().sum(), by_major.isna().sum(), flagged["gpa_missing"].sum())
```

:::exercise id=ex4 title="Group-wise imputation"
`fill_gpa_by_major(df)` returns a **copy** in which missing GPAs are replaced by the **median GPA of the same major**. No other column may change, and the input must not be modified.

```python
import pandas as pd

def fill_gpa_by_major(df):
    out = df.copy()
    ...
    return out

clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(),
                   gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))
print(fill_gpa_by_major(clean)["gpa"].isna().sum())
```

```python check
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(),
                   gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))
f = fill_gpa_by_major(clean)
assert clean["gpa"].isna().sum() > 0, "input was modified"
assert f["gpa"].isna().sum() == 0, "all GPAs should be filled"
m = clean["gpa"].isna()
for major in clean.loc[m, "major"].unique():
    med = clean.loc[clean["major"] == major, "gpa"].median()
    assert (f.loc[m & (clean["major"] == major), "gpa"] == med).all(), f"wrong fill value for {major}"
assert f.drop(columns="gpa").equals(clean.drop(columns="gpa")), "other columns must be unchanged"
```
:::

## 6 · New columns and accessors

Prefer vectorised arithmetic. Use `map` for value lookups, `pd.cut` for binning, `.str` for text, and `apply(axis=1)` only for row logic you cannot vectorise.

```python run
import pandas as pd
clean = (pd.read_csv("data/students.csv")
           .assign(major=lambda d: d["major"].str.strip(),
                   gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
           .drop_duplicates().reset_index(drop=True))

clean["gpa_pct"]    = clean["gpa"] / 4 * 100
clean["standing"]   = pd.cut(clean["gpa"], bins=[0, 2, 3.5, 4], labels=["probation", "good", "honours"])
clean["major_code"] = clean["major"].map({"Data Science": "DS", "Computer Science": "CS",
                                          "Cybersecurity": "CY", "AI": "AI", "Software Eng": "SE"})
clean["first_name"] = clean["name"].str.split().str[0]
clean["domain"]     = clean["email"].str.extract(r"@(.+)$")
clean["load"]       = clean.apply(lambda r: "heavy" if r["credits"] / max(r["year"], 1) > 30 else "normal", axis=1)

print(clean["standing"].value_counts(dropna=False))
clean[["name", "major_code", "gpa", "standing", "first_name", "domain", "load"]].head()
```

:::exercise id=ex5 title="Derived columns"
Add two columns and return the frame: `progress` = `credits / 132 × 100` rounded to one decimal, and `band` = `pd.cut` of GPA into `C` for `[0, 2)`, `B` for `[2, 3)`, `A` for `[3, 4]` — use `right=False` and make sure a GPA of exactly 4.0 lands in `A`.

```python
import pandas as pd

def derive(df):
    return df.assign(
        progress=...,
        band=pd.cut(df["gpa"], bins=[...], labels=["C", "B", "A"], right=False),
    )

clean = pd.read_csv("data/students.csv").assign(gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
print(derive(clean)["band"].value_counts())
```

```python check
import pandas as pd
clean = pd.read_csv("data/students.csv").assign(gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
d = derive(clean)
assert "progress" in d and "band" in d
assert abs(d.loc[0, "progress"] - round(clean.loc[0, "credits"] / 132 * 100, 1)) < 1e-9, "progress formula"
assert d.loc[d["gpa"] == 4.0, "band"].astype(str).eq("A").all(), "GPA 4.0 must be band A"
assert d.loc[d["gpa"] < 2.0, "band"].astype(str).eq("C").all(), "GPA < 2 must be band C"
assert d.loc[(d["gpa"] >= 2.0) & (d["gpa"] < 3.0), "band"].astype(str).eq("B").all(), "[2,3) must be band B"
```
:::

## Summary

* Five commands on every dataset: `head`, `info`, `describe`, `isna().sum()`, `nunique`.
* `[]` for columns, `.loc` for labels, `.iloc` for positions, masks for conditions.
* Clean with `.str`, `pd.to_numeric(errors="coerce")`, `drop_duplicates()` — ideally as one `assign` chain.
* Missing values: drop, fill, group-fill, or flag — and justify the choice.

Next: *Pandas II* — groupby, merge, pivot and time series.

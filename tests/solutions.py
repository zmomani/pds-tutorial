"""Reference solutions for every exercise, keyed by "<lesson-id>/<exercise-id>".

Used by tests/run_lessons.py to verify that each hidden check passes with a
correct answer (and fails with the untouched starter). Students never see this file
through the site; it lives only in the repository.
"""

SOLUTIONS = {
# ---------------------------------------------------------------- 01
"01-python-1/ex1": """
def honours_pct(pairs):
    return {name: round(g / 4 * 100, 1) for name, g in pairs if g >= 3.0}
""",
"01-python-1/ex2": """
def running_mean(values):
    total, n = 0.0, 0
    for v in values:
        total += v; n += 1
        yield total / n
""",
"01-python-1/ex3": """
def warning_users(path):
    with open(path) as f:
        for line in f:
            if " WARNING " in line:
                yield int(line.split("user=")[1].split()[0])
""",
"01-python-1/ex4": """
def rank(rows):
    return sorted(rows, key=lambda r: (r[1], -r[2], r[0]))
""",
"01-python-1/ex5": """
import csv
def top_per_major(path):
    best = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                g = float(r["gpa"])
            except ValueError:
                continue
            m = r["major"].strip()
            if m not in best or g > best[m][0]:
                best[m] = (g, r["name"])
    return {m: name for m, (gpa, name) in best.items()}
""",
# ---------------------------------------------------------------- 02
"02-python-2/ex1": """
from functools import wraps
def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper
""",
"02-python-2/ex2": """
def to_float(s, default=None):
    if s is None:
        return default
    try:
        return float(str(s).replace(",", "."))
    except ValueError:
        return default
""",
"02-python-2/ex3": """
from dataclasses import dataclass
@dataclass
class Course:
    code: str
    title: str
    credits: int
    def __post_init__(self):
        if not (len(self.code) == 6 and self.code.isdigit()):
            raise ValueError("bad code")
        if not 1 <= self.credits <= 6:
            raise ValueError("bad credits")
""",
"02-python-2/ex4": """
from contextlib import contextmanager
_MISSING = object()
@contextmanager
def override(d, key, value):
    old = d.get(key, _MISSING)
    d[key] = value
    try:
        yield
    finally:
        if old is _MISSING:
            d.pop(key, None)
        else:
            d[key] = old
""",
# ---------------------------------------------------------------- 03
"03-numpy/ex1": """
import numpy as np
def frame():
    f = np.ones((5, 5), dtype=int)
    f[1:-1, 1:-1] = 0
    return f
""",
"03-numpy/ex2": """
import numpy as np
def clip_gpa(g):
    out = g.copy()
    changed = (out < 0) | (out > 4)
    out[out < 0] = 0
    out[out > 4] = 4
    return out, int(changed.sum())
""",
"03-numpy/ex3": """
import numpy as np
def normalise_rows(M):
    s = M.sum(axis=1, keepdims=True)
    return np.divide(M, s, out=np.zeros_like(M, dtype=float), where=s != 0)
""",
"03-numpy/ex4": """
import numpy as np
def sample_means(seed, n_samples, size):
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, size=(n_samples, size)).mean(axis=1)
""",
"03-numpy/ex5": """
import numpy as np
def pairwise(P):
    diff = P[:, None, :] - P[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=2))
""",
# ---------------------------------------------------------------- 04
"04-pandas-1/ex1": """
import pandas as pd
def report(df):
    miss = df.isna().sum()
    return {"rows": len(df), "cols": df.shape[1],
            "missing": {c: int(v) for c, v in miss.items() if v > 0},
            "object_cols": df.select_dtypes("object").columns.tolist()}
""",
"04-pandas-1/ex2": """
import pandas as pd
def juniors_north(df):
    mask = df["year"].isin([1, 2]) & df["city"].isin(["Irbid", "Zarqa"])
    return df.loc[mask, ["name", "major"]].sort_values("name")
""",
"04-pandas-1/ex3": """
import pandas as pd
def audit(raw):
    gpa_num = pd.to_numeric(raw["gpa"], errors="coerce")
    blank = raw["gpa"].isna()
    return {"duplicates": int(raw.duplicated().sum()),
            "bad_gpa": int((gpa_num.isna() & ~blank).sum()),
            "blank_gpa": int(blank.sum()),
            "untrimmed_major": int((raw["major"] != raw["major"].str.strip()).sum()),
            "upper_city": int(raw["city"].str.isupper().sum())}
""",
"04-pandas-1/ex4": """
import pandas as pd
def fill_gpa_by_major(df):
    out = df.copy()
    out["gpa"] = out["gpa"].fillna(out.groupby("major")["gpa"].transform("median"))
    return out
""",
"04-pandas-1/ex5": """
import pandas as pd
def derive(df):
    return df.assign(progress=(df["credits"] / 132 * 100).round(1),
                     band=pd.cut(df["gpa"], bins=[0, 2, 3, 4.0001], labels=["C", "B", "A"], right=False))
""",
# ---------------------------------------------------------------- 05
"05-pandas-2/ex1": """
import pandas as pd
def city_report(df):
    return (df.groupby("city")
              .agg(students=("student_id", "size"), mean_gpa=("gpa", "mean"),
                   top_major=("major", lambda s: s.mode()[0]))
              .round({"mean_gpa": 2}).sort_values("students", ascending=False))
""",
"05-pandas-2/ex2": """
import pandas as pd
def grades_with_names(students, enr):
    return (enr.merge(students[["student_id", "name", "major"]], on="student_id", how="inner")
               .dropna(subset=["grade"])
               [["student_id", "name", "major", "course_code", "grade"]].reset_index(drop=True))
""",
"05-pandas-2/ex3": """
import pandas as pd
def grade_pivot(g):
    p = g.pivot_table(index="major", columns="course_code", values="grade", aggfunc="mean")
    p["overall"] = g.groupby("major")["grade"].mean()
    return p.round(1)
""",
"05-pandas-2/ex4": """
import pandas as pd
def monthly_product_revenue(sales):
    s = sales.assign(revenue=sales["units"] * sales["unit_price"])
    return (s.pivot_table(index="date", columns="product", values="revenue", aggfunc="sum")
             .resample("ME").sum().round(0))
""",
"05-pandas-2/ex5": """
import pandas as pd
def best_week(sales):
    daily = sales.assign(rev=sales["units"] * sales["unit_price"]).groupby("date")["rev"].sum()
    return daily.rolling(7).sum().idxmax()
""",
# ---------------------------------------------------------------- 07
"07-json/ex1": """
import json
from datetime import date
def to_json(records):
    def encode(obj):
        if isinstance(obj, date): return obj.isoformat()
        if isinstance(obj, set): return sorted(obj)
        raise TypeError(type(obj))
    return json.dumps(records, default=encode)
""",
"07-json/ex2": """
def dig(obj, path, default=None):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur: return default
            cur = cur[part]
        elif isinstance(cur, list):
            if not part.isdigit() or int(part) >= len(cur): return default
            cur = cur[int(part)]
        else:
            return default
    return cur
""",
"07-json/ex3": """
import pandas as pd
def courses_table(payload):
    t = pd.json_normalize(payload["results"], record_path="courses", meta=["id", "name"])
    return t[["id", "name", "code", "grade"]].sort_values(["id", "code"]).reset_index(drop=True)
""",
"07-json/ex4": """
import json
def fetch_all(api):
    page, items = 1, []
    while page is not None:
        body = json.loads(api(page))
        items.extend(body["data"])
        page = body["next"]
    return items
""",
# ---------------------------------------------------------------- 13
"13-sklearn/ex1": """
from sklearn.preprocessing import StandardScaler
def scale_split(X_train, X_test):
    scaler = StandardScaler().fit(X_train)
    return scaler.transform(X_train), scaler.transform(X_test)
""",
"13-sklearn/ex2": """
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
def make_pipeline():
    pre = ColumnTransformer([("num", StandardScaler(), ["units", "unit_price"]),
                             ("cat", OneHotEncoder(handle_unknown="ignore"), ["product", "city"])])
    return Pipeline([("pre", pre), ("model", LinearRegression())])
""",
"13-sklearn/ex3": """
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
def evaluate(model, X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
    p = model.fit(X_train, y_train).predict(X_test)
    return {"mae": round(mean_absolute_error(y_test, p), 2),
            "rmse": round(root_mean_squared_error(y_test, p), 2),
            "r2": round(r2_score(y_test, p), 2)}
""",
}

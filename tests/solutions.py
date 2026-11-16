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
"01-python-1/s21": """
class Countdown:
    def __init__(self, k):
        self.current = k
    def __iter__(self):
        return self
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value
""",
"01-python-1/s24a": """
import types
cubes = (x**3 for x in range(1, 11))
cube_list = list(cubes)
print(cube_list)
""",
"01-python-1/s24b": """
def emails(names):
    for name in names:
        yield f"{name.lower()}@uop.edu.jo"
""",
# ---------------------------------------------------------------- 02
"02-python-2/ex0": """
def only_even(func):
    def wrapper(n):
        if n % 2 != 0:
            print("odd number, skipped")
            return None
        return func(n)
    return wrapper
""",
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
# ---------------------------------------------------------------- 04
# ---------------------------------------------------------------- 05
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

"03-numpy/n1": """
import numpy as np

def evens(n):
    return np.arange(0, 2 * n, 2)
""",

"03-numpy/n2": """
import numpy as np

def inside(table):
    return table[1:-1, 1:-1].copy()
""",

"03-numpy/n3": """
import numpy as np

def rescale(x):
    return (x - x.min()) / (x.max() - x.min())
""",

"03-numpy/n4": """
import numpy as np

def hardest_exam(scores):
    return scores.mean(axis=0).argmin()
""",

"03-numpy/n5": """
import numpy as np

def row_shares(x):
    totals = x.sum(axis=1, keepdims=True)
    return x / totals
""",

"03-numpy/n6": """
import numpy as np

def count_between(x, low, high):
    return np.sum((x >= low) & (x <= high))
""",

"03-numpy/n7": """
import numpy as np

def ranking(names, totals):
    order = np.argsort(totals)
    return names[order][::-1]
""",

"04-pandas-1/p1": """
import pandas as pd

def top_in_major(df, major, minimum):
    return df.loc[(df["major"] == major) & (df["gpa"] >= minimum), ["name", "gpa"]]
""",

"04-pandas-1/p2": """
import pandas as pd

def total_points(a, b):
    return a.add(b, fill_value=0)
""",

"04-pandas-1/p3": """
import pandas as pd

def clean_gpa(df):
    out = df.copy()
    out["gpa"] = pd.to_numeric(out["gpa"], errors="coerce")
    out["gpa"] = out["gpa"].fillna(out["gpa"].median())
    return out
""",

"04-pandas-1/p4": """
import pandas as pd

def tidy(df):
    out = df.copy()
    out["major"] = out["major"].str.strip()
    out["city"] = out["city"].str.title()
    return out
""",

"05-pandas-2/q1": """
import pandas as pd

def average_by_title(enrollments, courses):
    joined = pd.merge(enrollments, courses, left_on="course_code", right_on="code")
    return joined.groupby("title")["grade"].mean()
""",

"05-pandas-2/q2": """
import pandas as pd

def above_major_mean(df):
    major_mean = df.groupby("major")["gpa"].transform("mean")
    return df[df["gpa"] > major_mean]
""",

"05-pandas-2/q3": """
import pandas as pd

def units_grid(sales):
    return sales.pivot_table(values="units", index="city", columns="product", aggfunc="sum")
""",

"05-pandas-2/q4": """
import pandas as pd

def best_month(sales):
    df = sales.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["revenue"] = df["units"] * df["unit_price"]
    return df.groupby(df["date"].dt.month)["revenue"].sum().idxmax()
""",
}

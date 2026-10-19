# JSON — Parsing, Nested Data, APIs

<p class="lesson-intro">Week 7 · Programming for Data Science (606315)</p>

JSON (JavaScript Object Notation) is the format every web API speaks and most configuration files use. It maps almost one-to-one onto Python: objects become `dict`, arrays become `list`, and the scalars are `str`, numbers, `True`/`False`/`None`. The work is rarely the parsing — it is flattening **nested** structures into tables and back.

## 1 · Serialise and parse

`json.dumps` / `json.loads` work on strings; `json.dump` / `json.load` on files. `indent` makes output readable; `sort_keys` makes it reproducible.

```python run
import json

record = {"student_id": 20230001, "name": "Sara Khalil", "gpa": 3.8,
          "courses": ["606315", "606272"], "active": True, "advisor": None}

text = json.dumps(record, indent=2)
print(text)

back = json.loads(text)
print(type(back), back == record)
print(json.dumps(record, sort_keys=True))        # compact, deterministic key order
```

Types that have no JSON equivalent — dates, sets, NumPy numbers, dataclasses — need a `default=` hook.

```python run
import json
from datetime import date
from dataclasses import dataclass, asdict

@dataclass
class Enrolment:
    student_id: int
    course: str
    on: date

def encode(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    raise TypeError(f"not serialisable: {type(obj).__name__}")

e = Enrolment(20230001, "606315", date(2025, 9, 1))
print(json.dumps(e, default=encode))
```

:::exercise id=ex1 title="Round-trip with a custom encoder"
Write `to_json(records)` that serialises a list of dicts whose values may include `date` objects and `set`s. Dates become ISO strings, sets become **sorted lists**. The output must be parseable by `json.loads`.

```python
import json
from datetime import date

def to_json(records):
    def encode(obj):
        ...
    return json.dumps(records, default=encode)

print(to_json([{"id": 1, "on": date(2025, 9, 1), "tags": {"b", "a"}}]))
```

```python check
import json
from datetime import date
out = to_json([{"id": 1, "on": date(2025, 9, 1), "tags": {"b", "a"}}, {"id": 2, "on": date(2025, 1, 31), "tags": set()}])
parsed = json.loads(out)
assert parsed[0]["on"] == "2025-09-01" and parsed[1]["on"] == "2025-01-31", "dates must be ISO strings"
assert parsed[0]["tags"] == ["a", "b"] and parsed[1]["tags"] == [], "sets become sorted lists"
```
:::

## 2 · Files

```python run
import json
with open("data/courses.json") as f:
    courses = json.load(f)

print(type(courses), len(courses))
print(courses[0])
print([c["code"] for c in courses])

by_code = {c["code"]: c for c in courses}          # index it for O(1) lookup
print(by_code["606315"]["title"])
```

## 3 · Walking nested structures

API responses are rarely flat. Practise reading the shape first — `keys()`, `type()`, `len()` — then write the access path. A missing key is a `KeyError`; use `.get()` with a default when a field is optional.

```python run
import json
payload = json.loads("""
{
  "meta": {"page": 1, "total": 2},
  "results": [
    {"id": 1, "name": "Ahmad", "scores": {"mid": 70, "final": 82},
     "courses": [{"code": "606315", "grade": 88}, {"code": "606272", "grade": 75}]},
    {"id": 2, "name": "Sara",  "scores": {"mid": 91},
     "courses": []}
  ]
}
""")

print(payload.keys(), payload["meta"]["total"])
for r in payload["results"]:
    final = r["scores"].get("final", "n/a")          # optional field
    codes = [c["code"] for c in r["courses"]]
    print(r["id"], r["name"], "final:", final, "courses:", codes)
```

A recursive walker is a reusable tool for *unknown* shapes — it prints every leaf with its path.

```python run
def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj

sample = {"meta": {"page": 1}, "results": [{"id": 1, "scores": {"mid": 70}}]}
for path, value in walk(sample):
    print(f"{path:25s} {value!r}")
```

:::exercise id=ex2 title="Safe nested access"
Write `dig(obj, path, default=None)` that follows a dotted path such as `"meta.page"` or `"results.0.scores.mid"` through dicts **and lists** (numeric segments index lists) and returns `default` if any step is missing or of the wrong type.

```python
def dig(obj, path, default=None):
    cur = obj
    for part in path.split("."):
        ...
    return cur

d = {"meta": {"page": 1}, "results": [{"id": 1, "scores": {"mid": 70}}]}
print(dig(d, "meta.page"), dig(d, "results.0.scores.mid"), dig(d, "results.5.id", "none"))
```

```python check
d = {"meta": {"page": 1}, "results": [{"id": 1, "scores": {"mid": 70}}]}
assert dig(d, "meta.page") == 1
assert dig(d, "results.0.scores.mid") == 70
assert dig(d, "results.0.scores.final") is None, "missing key → default"
assert dig(d, "results.5.id", "none") == "none", "index out of range → default"
assert dig(d, "meta.page.x", 0) == 0, "indexing into an int → default"
assert dig(d, "results.x", -1) == -1, "non-numeric index into a list → default"
```
:::

## 4 · JSON ↔ DataFrame

`pd.json_normalize` flattens nested dicts into columns (`scores.mid`) and can explode a list of records with `record_path`. Going the other way, `to_dict("records")` and `to_json(orient="records")` produce the shape APIs expect.

```python run
import json
import pandas as pd

payload = {"results": [
    {"id": 1, "name": "Ahmad", "scores": {"mid": 70, "final": 82},
     "courses": [{"code": "606315", "grade": 88}, {"code": "606272", "grade": 75}]},
    {"id": 2, "name": "Sara", "scores": {"mid": 91}, "courses": [{"code": "606315", "grade": 95}]},
]}

flat = pd.json_normalize(payload["results"])
print(flat.drop(columns="courses"))
print()

long = pd.json_normalize(payload["results"], record_path="courses", meta=["id", "name"])
print(long)
print()

print(long.to_json(orient="records"))
print(flat.drop(columns="courses").to_dict("records")[0])
```

```python run
import pandas as pd
df = pd.read_csv("data/students.csv").head(3)
print(df[["student_id", "name", "major"]].to_json(orient="records", indent=1))
```

:::exercise id=ex3 title="Nested records to a long table"
`courses_table(payload)` takes the payload shape above and returns a DataFrame with columns `id, name, code, grade` — one row per course taken — sorted by `id` then `code`.

```python
import pandas as pd

def courses_table(payload):
    t = pd.json_normalize(payload["results"], record_path=..., meta=[...])
    return t[["id", "name", "code", "grade"]].sort_values(["id", "code"]).reset_index(drop=True)

payload = {"results": [
    {"id": 1, "name": "Ahmad", "scores": {"mid": 70}, "courses": [{"code": "606315", "grade": 88}, {"code": "606272", "grade": 75}]},
    {"id": 2, "name": "Sara", "scores": {"mid": 91}, "courses": [{"code": "606315", "grade": 95}]},
]}
courses_table(payload)
```

```python check
import pandas as pd
payload = {"results": [
    {"id": 1, "name": "Ahmad", "scores": {"mid": 70}, "courses": [{"code": "606315", "grade": 88}, {"code": "606272", "grade": 75}]},
    {"id": 2, "name": "Sara", "scores": {"mid": 91}, "courses": [{"code": "606315", "grade": 95}]},
]}
t = courses_table(payload)
assert list(t.columns) == ["id", "name", "code", "grade"], f"columns {list(t.columns)}"
assert len(t) == 3
assert t.iloc[0].tolist() == [1, "Ahmad", "606272", 75], f"first row {t.iloc[0].tolist()}"
assert t.iloc[2].tolist() == [2, "Sara", "606315", 95]
```
:::

## 5 · Talking to an API

In the full course environment you fetch JSON with `requests`:

```python
import requests
r = requests.get("https://api.example.com/students", params={"page": 1}, timeout=10)
r.raise_for_status()           # raise on 4xx / 5xx
data = r.json()                # parsed body
```

The browser cannot make arbitrary cross-site requests, so here we simulate a paginated API with a function and practise the loop that collects every page — the part that actually needs thought.

```python run
import json

def fake_api(page, per_page=4):
    """Pretend endpoint: 10 records across pages of 4, with a `next` pointer."""
    records = [{"id": i, "value": i * i} for i in range(1, 11)]
    chunk = records[(page - 1) * per_page: page * per_page]
    has_more = page * per_page < len(records)
    return json.dumps({"data": chunk, "next": page + 1 if has_more else None})

page, items = 1, []
while page is not None:
    body = json.loads(fake_api(page))
    items.extend(body["data"])
    page = body["next"]
print(len(items), "records;", items[-1])
```

:::exercise id=ex4 title="Collect all pages"
Write `fetch_all(api)` that calls `api(page)` starting at 1, follows the `next` pointer until it is `None`, and returns the concatenated list of `data` records. `api` returns a JSON **string**.

```python
import json

def fetch_all(api):
    page, items = 1, []
    while page is not None:
        body = json.loads(api(page))
        ...                 # add body["data"] to items
        page = None         # replace: follow body["next"]
    return items

def fake_api(page, per_page=4):
    records = [{"id": i, "value": i * i} for i in range(1, 11)]
    chunk = records[(page - 1) * per_page: page * per_page]
    return json.dumps({"data": chunk, "next": page + 1 if page * per_page < len(records) else None})

print(len(fetch_all(fake_api)))
```

```python check
import json
def _api(n):
    def api(page):
        recs = [{"id": i} for i in range(1, n + 1)]
        chunk = recs[(page - 1) * 3: page * 3]
        return json.dumps({"data": chunk, "next": page + 1 if page * 3 < n else None})
    return api
assert [r["id"] for r in fetch_all(_api(10))] == list(range(1, 11))
assert fetch_all(_api(0)) == [], "an empty first page must return []"
assert [r["id"] for r in fetch_all(_api(3))] == [1, 2, 3], "exactly one full page"
```
:::

## Summary

* `dumps/loads` for strings, `dump/load` for files; `default=` for dates, sets, dataclasses.
* Read the shape before writing the access path; `.get()` for optional keys.
* `pd.json_normalize(..., record_path=, meta=)` flattens; `to_dict("records")` goes back.
* Pagination: loop on the `next` pointer, accumulate `data`.

Next, in the course: web scraping (Codespaces), then Django. On this site: *Scikit-learn*.

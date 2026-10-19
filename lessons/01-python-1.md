# Advanced Python I — Comprehensions, Generators, Lambdas

<p class="lesson-intro">Week 1 · Programming for Data Science (606315)</p>

You already know Python. This lesson is about writing it the way data scientists do: compact where the intent is simple, lazy where the data is large. Every grey box with a **▶ Try it** button loads into the editor on the right — run it, then change it.

> **How this page works.** Press **▶ Try it** on any example to load and run it. Edit freely; **Reset** restores the original. Exercises have a **Check** button that runs hidden tests on your code.

## 1 · Comprehensions

A comprehension builds a collection from an iterable in a single expression. The loop and the comprehension below produce the same list; the comprehension says *what* you want rather than *how* to accumulate it.

```python run
gpas = [3.4, 2.1, 3.9, 2.8, 1.9, 3.2]

# the loop way
scaled = []
for g in gpas:
    scaled.append(round(g / 4 * 100, 1))

# the comprehension way
scaled2 = [round(g / 4 * 100, 1) for g in gpas]

print(scaled)
print(scaled == scaled2)
```

### Filtering and conditional values

An `if` **after** the `for` filters elements out. An `if/else` **before** the `for` chooses a value for every element. They look similar and do different things.

```python run
gpas = [3.4, 2.1, 3.9, 2.8, 1.9, 3.2]

honours = [g for g in gpas if g >= 3.0]                         # filter: fewer items
status  = ["pass" if g >= 2.0 else "probation" for g in gpas]   # map: same number of items

print(honours)
print(status)
```

### Dictionary and set comprehensions

Braces give you a `dict` or a `set`. Building a lookup table, or inverting one, is where these shine.

```python run
names = ["Ahmad", "Sara", "Omar", "Lina"]
gpas  = [3.4, 2.1, 3.9, 2.8]

gpa_by_name = {n: g for n, g in zip(names, gpas)}
print(gpa_by_name)

code_to_name = {"DS": "Data Science", "CS": "Computer Science"}
name_to_code = {v: k for k, v in code_to_name.items()}      # invert a mapping
print(name_to_code)

majors = ["DS", "CS", "DS", "AI", "CS"]
print({m for m in majors})                                   # unique values
```

### Nested comprehensions

Flattening a list of lists is the one nested comprehension worth memorising. Read the `for` clauses left to right, exactly as you would write nested loops.

```python run
grades_per_course = [[88, 92], [75], [60, 70, 65]]
flat = [g for course in grades_per_course for g in course]
print(flat)

identity = [[1 if r == c else 0 for c in range(3)] for r in range(3)]
for row in identity:
    print(row)
```

> **Rule of thumb.** If a comprehension does not fit on one line, or needs a comment, write a loop.

:::exercise id=ex1 title="Honours percentage table"
Complete `honours_pct` so that it returns a dict mapping each name whose GPA is **at least 3.0** to its GPA scaled to a percentage (GPA ÷ 4 × 100, rounded to one decimal). Use a single dictionary comprehension.

```python
def honours_pct(pairs):
    """pairs: list of (name, gpa) tuples"""
    return {}   # replace this

print(honours_pct([("a", 3.0), ("b", 2.9), ("c", 4.0)]))
```

```python check
assert honours_pct([("a", 3.0), ("b", 2.9), ("c", 4.0)]) == {"a": 75.0, "c": 100.0}, "wrong result for the sample input"
assert honours_pct([]) == {}, "an empty input should give an empty dict"
assert honours_pct([("x", 2.99)]) == {}, "2.99 is below the threshold"
```
:::

## 2 · Generators: processing more than fits in memory

A list holds every element at once. A **generator** produces one element at a time, on demand, so a 10 GB file can be processed with a few kilobytes of RAM. Any function containing `yield` is a generator function.

```python run
def countdown(n):
    print("starting")
    while n > 0:
        yield n
        n -= 1
    print("done")

gen = countdown(3)
print(type(gen))        # nothing has run yet — 'starting' is not printed
print(next(gen))
print(next(gen))
print(list(gen))        # drains the rest
```

Generators are **lazy**: the body runs only when something asks for the next value. Compare the memory footprint of a list of a million squares with a generator expression (round brackets instead of square):

```python run
import sys
squares_list = [i * i for i in range(1_000_000)]
squares_gen  = (i * i for i in range(1_000_000))

print(f"list : {sys.getsizeof(squares_list) / 1e6:.1f} MB")
print(f"gen  : {sys.getsizeof(squares_gen)} bytes")
print(sum(squares_gen))   # consumes it — a generator can be iterated only once
print(sum(squares_gen))   # already exhausted
```

### A streaming pipeline over a log file

`data/server.log` has 500 lines like `2025-09-01T00:07:00 WARNING user=12 latency_ms=410`. Each function below is a generator; chained together they stream the file line by line — the same code would work on 500 million lines.

```python run
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n")

def only(level, lines):
    for line in lines:
        if f" {level} " in line:
            yield line

def latencies(lines):
    for line in lines:
        yield int(line.split("latency_ms=")[1])

errs = list(latencies(only("ERROR", read_lines("data/server.log"))))
print(len(errs), "error lines; mean latency", round(sum(errs) / len(errs)), "ms")
```

### `itertools` — lazy building blocks

```python run
from itertools import islice, chain, groupby

def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n")

print(*islice(read_lines("data/server.log"), 3), sep="\n")   # first 3, without reading the file

print(list(chain([1, 2], (3, 4), "ab")))                     # concatenate lazily

levels = sorted(line.split()[1] for line in read_lines("data/server.log"))
for level, group in groupby(levels):                           # groups consecutive equal keys
    print(f"{level:8s} {sum(1 for _ in group)}")
```

:::exercise id=ex2 title="Running mean generator"
Write a generator `running_mean(values)` that yields the mean of all values seen so far, after each value. It must work on an **infinite** input, so you may not call `list()` or `sum()` on the whole input.

```python
def running_mean(values):
    total = 0.0
    n = 0
    for v in values:
        # update total and n, then yield the mean so far
        yield 0.0      # replace this

print(list(running_mean([2, 4, 6])))     # expected [2.0, 3.0, 4.0]
```

```python check
import types
from itertools import count, islice
assert isinstance(running_mean([1]), types.GeneratorType), "running_mean must be a generator (use yield)"
assert list(running_mean([2, 4, 6])) == [2.0, 3.0, 4.0]
assert list(islice(running_mean(count(1)), 4)) == [1.0, 1.5, 2.0, 2.5], "must work on an infinite input"
```
:::

:::exercise id=ex3 title="Warnings from the log"
Write a generator `warning_users(path)` that yields the **user id (as an `int`)** of every `WARNING` line in the file, reading lazily (no `readlines()`, no list of the whole file).

```python
def warning_users(path):
    with open(path) as f:
        for line in f:
            ...

ids = list(warning_users("data/server.log"))
print(len(ids), ids[:10])
```

```python check
import types
g = warning_users("data/server.log")
assert isinstance(g, types.GeneratorType), "must be a generator"
ids = list(g)
assert all(isinstance(i, int) for i in ids), "yield ints"
assert 50 < len(ids) < 200, f"unexpected count {len(ids)} — check the level filter"
assert all(1 <= i <= 40 for i in ids), "user ids are between 1 and 40"
```
:::

## 3 · `lambda`, `sorted`, `map`, `filter`

A `lambda` is an anonymous one-expression function. Its natural home is the `key=` argument of `sorted`, `min` and `max` — and later, Pandas' `.apply()`.

```python run
records = [("Ahmad", 3.4, 2), ("Sara", 3.9, 4), ("Omar", 2.1, 1), ("Lina", 3.9, 3)]

by_gpa = sorted(records, key=lambda r: r[1], reverse=True)
by_gpa_then_year = sorted(records, key=lambda r: (-r[1], r[2]))   # tuple keys break ties
best = max(records, key=lambda r: r[1])

print(by_gpa)
print(by_gpa_then_year)
print("top:", best[0])
```

`map` and `filter` return lazy iterators. In new code a comprehension is usually clearer, but you will meet them constantly in other people's code.

```python run
records = [("Ahmad", 3.4, 2), ("Sara", 3.9, 4), ("Omar", 2.1, 1), ("Lina", 3.9, 3)]

names   = list(map(lambda r: r[0].upper(), records))
seniors = list(filter(lambda r: r[2] >= 3, records))
print(names)
print(seniors)

# the equivalent comprehensions
print([r[0].upper() for r in records] == names)
print([r for r in records if r[2] >= 3] == seniors)

# map with a built-in and several iterables
print(list(map(pow, [2, 3, 4], [2, 2, 2])))
```

:::exercise id=ex4 title="Multi-key ranking"
Sort a list of `(name, major, gpa)` tuples by **major ascending**, then **GPA descending**, then **name ascending**. Return the new list; do not modify the input.

```python
def rank(rows):
    return sorted(rows, key=lambda r: ...)

rows = [("Omar", "CS", 3.1), ("Sara", "DS", 3.9), ("Ahmad", "CS", 3.1), ("Lina", "CS", 3.8)]
print(rank(rows))
```

```python check
rows = [("Omar", "CS", 3.1), ("Sara", "DS", 3.9), ("Ahmad", "CS", 3.1), ("Lina", "CS", 3.8)]
expected = [("Lina", "CS", 3.8), ("Ahmad", "CS", 3.1), ("Omar", "CS", 3.1), ("Sara", "DS", 3.9)]
assert rank(rows) == expected, f"got {rank(rows)}"
assert rows[0] == ("Omar", "CS", 3.1), "do not modify the input list"
```
:::

## 4 · Putting it together

Everything above in one small pipeline: stream `students.csv` with the `csv` module, skip rows whose GPA is not a number, and print the mean GPA per major with the highest first.

```python run
import csv

def rows(path):
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                yield r["major"].strip(), float(r["gpa"])
            except ValueError:
                pass                       # 'unknown' or blank GPA — skip

by_major = {}
for major, gpa in rows("data/students.csv"):
    by_major.setdefault(major, []).append(gpa)

for major, g in sorted(by_major.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
    print(f"{major:18s} n={len(g):3d}  mean={sum(g)/len(g):.2f}")
```

:::exercise id=ex5 title="Top student per major"
Using the same streaming approach, write `top_per_major(path)` that returns a dict `{major: name}` of the student with the **highest GPA** in each major (majors stripped of whitespace, unparseable GPAs skipped). On ties keep the first one seen.

```python
import csv

def top_per_major(path):
    best = {}            # major -> (gpa, name)
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ...
    return {m: name for m, (gpa, name) in best.items()}

print(top_per_major("data/students.csv"))
```

```python check
res = top_per_major("data/students.csv")
assert set(res) == {"Data Science", "Computer Science", "Cybersecurity", "AI", "Software Eng"}, f"majors: {set(res)}"
import csv
best = {}
with open("data/students.csv", newline="") as f:
    for r in csv.DictReader(f):
        try: g = float(r["gpa"])
        except ValueError: continue
        m = r["major"].strip()
        if m not in best or g > best[m][0]: best[m] = (g, r["name"])
assert all(res[m] == best[m][1] for m in best), "a major has the wrong top student"
```
:::

## Summary

* **Comprehensions** replace short accumulate-loops; keep them to one line.
* **Generators** make pipelines lazy — chain them to stream big files.
* **`lambda`** belongs in `key=`; prefer comprehensions over `map`/`filter` in new code.

Next: *Advanced Python II* — decorators, exceptions, type hints and context managers.

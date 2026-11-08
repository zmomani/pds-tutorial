# Advanced Python II — Decorators, Errors, Types, Context Managers

<p class="lesson-intro">Week 2 · Programming for Data Science (606315)</p>

Last lesson was about expressing transformations compactly. This one is about making code **robust** — it survives dirty data — and **self-describing** — a colleague (or you in six months) can read a function's signature and know what it does.

> **🟢 Study these for the exams.** A green light next to a heading means that part follows the lecture slides: its examples are the slides' own, with extra explanation added, and the light covers everything under that heading. Anything without a green light is extra practice and background — useful, but not what the exams are built on.

## 1 · Decorators

A decorator is a function that takes a function and returns a new function. Writing `@timer` above a `def` is just shorthand for `f = timer(f)`. Decorators add behaviour *around* a function without touching its body: timing, caching, logging, retries.

### 1.1 · Decorators: building blocks 🟢

A decorator combines two patterns: **nested functions** and **functions as arguments**.

**Pattern 1: nested functions.** `outer` below does not multiply anything. It *builds* a new function, `inner`, that remembers `x`, and hands it back.

```python run
def outer(x):
    def inner(y):
        return x * y
    return inner

multiply_five = outer(5)
print(multiply_five(6))  # 30
```

**Pattern 2: functions as arguments.** A function is a value like any other, so you can hand it to another function. (You already did this in lesson 1 with `key=lambda …`.)

```python run
def multiply(x, y):
    return x * y

def calculate(func, x, y):
    return func(x, y)

print(calculate(multiply,5,6)) # 30
```

A decorator combines both: it takes a function as input, wraps it in an inner function, and returns the wrapper.

### 1.2 · More on decorators: the repetition problem

The reason for decorators is repetition. Suppose you want a message printed whenever certain functions run, and you have three of them:

```python run
def add(a, b):
    print("calling add")        # same extra line...
    return a + b

def subtract(a, b):
    print("calling subtract")   # ...copied here
    return a - b

def multiply(a, b):
    print("calling multiply")   # ...and here
    return a * b

print(add(2, 3))
print(subtract(7, 4))
print(multiply(5, 6))
```

The extra behaviour is mixed into every function, and it is copied each time. If you later want to change it, you must edit all three. With 50 functions it gets worse, and the logging code hides what each function actually does.

A decorator lets you write the extra behaviour once and attach it. Don't worry about how `log_call` works yet — the next section builds it step by step. Just compare the result with the version above:

```python run
def log_call(func):
    def wrapper(a, b):
        print(f"calling {func.__name__}")
        return func(a, b)
    return wrapper

@log_call
def add(a, b):
    return a + b

@log_call
def subtract(a, b):
    return a - b

@log_call
def multiply(a, b):
    return a * b

print(add(2, 3))
print(subtract(7, 4))
print(multiply(5, 6))
```

The output is identical, but now each function contains only its own job. The logging lives in one place, and one line above a function adds it. Changing the message means editing `log_call` once.

(`func.__name__` is the function's own name as text, so one `log_call` prints the right name for each function it wraps. The `f` before the quote makes it an *f-string*: whatever is inside `{ }` is evaluated and inserted into the text.)

### 1.3 · Your first decorator: manual and `@` syntax 🟢

The decorator below takes a function, defines an inner function that does something extra and then calls the original, and returns the inner function. The original is not replaced by the extra behaviour; it is **wrapped**: it sits inside and is still called.

**Manual** (wrap by hand):

```python run
def func1(func):
    def inner():
        print("Before"); func()
    return inner
def func2(): print("Hello")
decorated = func1(func2)
decorated()
```

**Using `@` syntax** (preferred):

```python run
def func1(func):
    def inner():
        print("Before"); func()
    return inner

@func1
def func2(): print("Hello")
func2()  # same result!
```

`@func1` above a `def` is exactly `func2 = func1(func2)`. After that line the name `func2` points to `inner`, and the original `func2` lives on inside it. Both versions print `Before` and then `Hello`.

### 1.4 · Decorators with parameters: a guard 🟢

Because the wrapper decides whether to call the original, it can refuse to. Here `inner` takes the same arguments as the function it replaces (`a, b`), checks them, and only then passes them on.

```python run
def safe_division(func):
    def inner(a, b):
        if b == 0:
            print(f"Divide by Zero {a}/{b}: Exiting")
            return
        else:
            print(f"Computing {a}/{b} = ", end="")
            func(a, b)
    return inner

@safe_division
def divide(a, b):
    print(f"{a/b}")

divide(5, 6)   # → Computing 5/6 = 0.8333333333333334
divide(5, 0)   # → Divide by Zero 5/0: Exiting
```

**Execution flow** for `divide(5, 6)`: `divide(5,6)` is called, which is really `inner(5,6)`; `inner` runs its check; because `b ≠ 0` the check passes and `inner` calls `func(5,6)`, the original function. For `divide(5, 0)` the flow stops at the check, so the original `divide` never runs and nothing can crash.

### 1.5 · Chaining decorators 🟢

You can stack several decorators on one function, **one per line**. They are applied from the bottom up (innermost first), but when you *call* the function the top one runs first and the original runs last, like layers of wrapping paper.

```python run
def divisor_not_zero(func):
    def wrapper(a, b):
        if b == 0: print("Divide by Zero Error"); return
        return func(a, b)
    return wrapper

def divisor_not_negative(func):
    def wrapper(a, b):
        if b < 0: print("Divisor must be positive"); return
        return func(a, b)
    return wrapper

@divisor_not_negative   # outer check: runs first when called
@divisor_not_zero       # inner check: applied first, runs second when called
def division(a, b):
    print(f"{a}/{b} = {a/b}")

division(5, -6)
division(5, 0)
division(5, 2)
```

`@divisor_not_negative` over `@divisor_not_zero` means `division = divisor_not_negative(divisor_not_zero(division))`. The negative check is the outer layer, so it runs first; the zero check is next; the original `division` runs last.

| Call | Output |
|---|---|
| `division(5, -6)` | Divisor must be positive |
| `division(5, 0)` | Divide by Zero Error |
| `division(5, 2)` | 5/2 = 2.5 |

> The slide's comment says the lower decorator is the one that "runs first". That is true of *applying* the decorators (bottom up), but when the function is *called*, the top decorator's check happens first, as the outputs above show.

### 1.6 · Practice: message sending system 🟢

Validate the credentials and the message before sending, a real-world pattern. Decorators like these are used extensively in Django and Flask for authentication, logging and permissions.

```python run
def check_authentication(func):
    def wrapper(u, r, m):
        if u['name']!='admin' or u['password']!='123':
            print("Invalid credentials"); return
        return func(u, r, m)
    return wrapper

def check_message(func):
    def wrapper(u, r, m):
        if r.strip()=="" or m.strip()=="":
            print("Receiver or Message empty"); return
        return func(u, r, m)
    return wrapper

@check_authentication
@check_message
def send_email(user, receiver, message):
    print(f"Sending to {receiver} by {user['name']}")

user_a = {'name':'bad','password':'wrong'}
user_b = {'name':'admin','password':'123'}
send_email(user_a,"","Hi")       # Invalid credentials
send_email(user_b,"","Hi")       # Receiver or Message empty
send_email(user_b,"Raghad","Hi") # Sending to Raghad by admin
```

(The slide writes both decorators on one line; Python needs them on separate lines.) Authentication is on top, so it is checked first: `user_a` is rejected before the message is even looked at.

### 1.7 · More on decorators: guards that return values and the wrapping order

The guard on the slide only *prints* the result. In real code the wrapper should usually `return` what the original returns, so the caller can use it:

```python run
def safe_division(func):
    def inner(a, b):
        if b == 0:
            print(f"Divide by Zero {a}/{b}: Exiting")
            return None
        return func(a, b)
    return inner

@safe_division
def divide(a, b):
    return a / b

print(divide(5, 6))    # 0.8333333333333334
print(divide(5, 0))    # prints the warning, then None
```

To see the layers of stacking directly, give each wrapper a "before" and "after" print:

```python run
def deco_a(func):
    def wrapper():
        print("A before")
        func()
        print("A after")
    return wrapper

def deco_b(func):
    def wrapper():
        print("B before")
        func()
        print("B after")
    return wrapper

@deco_a
@deco_b
def work():
    print("work")

work()
```

`@deco_a` over `@deco_b` means `work = deco_a(deco_b(work))`: A's wrapper is the outermost layer, so it starts first and finishes last.

:::exercise id=ex0 title="A guard decorator"
Write the decorator `only_even` so that a decorated function runs **only when its argument is even**. For an odd argument the wrapper must print a short message and return `None` **without calling the original function**; otherwise it must return the original function's result.

```python
def only_even(func):
    def wrapper(n):
        ...          # replace this
    return wrapper

@only_even
def half(n):
    return n // 2

print(half(10), half(7))    # expected: 5 None
```

```python check
@only_even
def _half(n):
    return n // 2
assert _half(10) == 5, "return the original function's result for an even number"
assert _half(7) is None, "an odd number should give None"

calls = []
@only_even
def _record(n):
    calls.append(n)
    return n
_record(3)
assert calls == [], "the original function must not run for an odd number"
_record(4)
assert calls == [4], "the original function must run for an even number"

def _positive(func):
    def wrapper(n):
        return func(n) if n > 0 else None
    return wrapper

@_positive
@only_even
def _stacked(n):
    return n // 2
assert (_stacked(8), _stacked(-4), _stacked(3)) == (4, None, None), "only_even must work when stacked with another decorator"
```
:::

### 1.8 · A practical decorator — `timer` and `@wraps`

The wrappers above take exactly `(a, b)` because they wrap two-argument functions. A reusable decorator should accept *any* arguments, which is what `*args, **kwargs` means below.

```python run
import time
from functools import wraps

def timer(func):
    @wraps(func)                       # keep the original name and docstring
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {(time.perf_counter() - t0) * 1000:.1f} ms")
        return result
    return wrapper

@timer
def slow_sum(n):
    """Sum the first n integers the slow way."""
    return sum(i for i in range(n))

print(slow_sum(500_000))
print(slow_sum.__name__, "-", slow_sum.__doc__)
```

Try deleting the `@wraps(func)` line and re-running: the name becomes `wrapper` and the docstring disappears.

### 1.9 · `lru_cache` — memoisation in one line

Expensive pure functions (feature computation, API lookups) can be cached by the standard library.

```python run
import time
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

t0 = time.perf_counter(); fib(60); print(f"first call : {(time.perf_counter() - t0) * 1e3:.3f} ms")
t0 = time.perf_counter(); fib(60); print(f"cached call: {(time.perf_counter() - t0) * 1e6:.1f} µs")
print(fib.cache_info())
```

### 1.10 · Decorators with arguments

One more level: a *factory* that returns a decorator. This is the pattern behind `@retry(times=3)` or `@app.route("/")` in web frameworks.

```python run
import random
from functools import wraps

def retry(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*a, **kw):
            for attempt in range(1, times + 1):
                try:
                    return func(*a, **kw)
                except ValueError as e:
                    print(f"attempt {attempt} failed: {e}")
            raise RuntimeError(f"{func.__name__} failed after {times} attempts")
        return wrapper
    return decorator

random.seed(1)

@retry(times=3)
def flaky_download():
    if random.random() < 0.6:
        raise ValueError("network hiccup")
    return "data!"

print(flaky_download())
```

:::exercise id=ex1 title="A call-counting decorator"
Write a decorator `count_calls` that gives the wrapped function a `.calls` attribute, incremented on every call, while preserving the function's name, docstring and return value.

```python
from functools import wraps

def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ...
    wrapper.calls = 0
    return wrapper

@count_calls
def square(x):
    """Square a number."""
    return x * x

print(square(2), square(3), square.calls)
```

```python check
@count_calls
def _f(x):
    """doc"""
    return x + 1
assert [_f(1), _f(2), _f(3)] == [2, 3, 4], "return value must be preserved"
assert _f.calls == 3, f"calls should be 3, got {_f.calls}"
assert _f.__name__ == "_f" and _f.__doc__ == "doc", "use functools.wraps"
```
:::

## 2 · Error handling

Real datasets contain `"unknown"`, blank strings, and numbers written with commas. For each bad value your code has three options — crash, skip, or substitute — and `try/except` lets you make that choice explicit.

```python run
raw = ["3.4", "unknown", "", "2.75", "3,1", "4.0"]

def parse_gpa(s):
    try:
        return float(s)
    except ValueError:
        return None          # an explicit "missing" marker

cleaned = [parse_gpa(s) for s in raw]
print(cleaned)
print("valid:", [g for g in cleaned if g is not None])
```

### 2.1 · The full form: `try / except / else / finally`

`except` runs on error, `else` only when there was none, `finally` always. Catch the **narrowest** exception that makes sense — a bare `except:` also swallows typos and `KeyboardInterrupt`.

```python run
def load_number(path):
    try:
        f = open(path)
    except FileNotFoundError:
        print(f"{path}: not found, using default")
        return 0
    else:
        with f:
            return float(f.read())
    finally:
        print("load_number finished")

print(load_number("does_not_exist.txt"))
```

### 2.2 · Raising your own exceptions

A small exception hierarchy lets callers catch exactly what they care about.

```python run
class DataError(Exception):
    """Base class for problems with input data."""

class SchemaError(DataError):
    pass

def check_row(row, required=("student_id", "gpa")):
    missing = [k for k in required if k not in row]
    if missing:
        raise SchemaError(f"missing columns: {missing}")
    return row

try:
    check_row({"student_id": 1})
except DataError as e:            # catches SchemaError too
    print(type(e).__name__, "->", e)
```

:::exercise id=ex2 title="Safe float parsing"
Complete `to_float(s, default=None)` so it returns `float(s)` — also accepting a **comma decimal separator** such as `"3,1"` — and returns `default` for anything unparseable, including `None`.

```python
def to_float(s, default=None):
    ...

print(to_float("3.5"), to_float("3,1"), to_float("unknown"), to_float("", default=0.0))
```

```python check
assert to_float("3.5") == 3.5
assert to_float("3,1") == 3.1, "accept a comma as decimal separator"
assert to_float("unknown") is None
assert to_float("", default=0.0) == 0.0
assert to_float(None, -1) == -1, "None input must return the default"
assert to_float(" 2.0 ") == 2.0, "surrounding whitespace is fine for float()"
```
:::

## 3 · Type hints and dataclasses

Hints do not change how Python runs. They document intent, let your editor autocomplete correctly, and let a type checker warn you before you execute. `list[float]`, `dict[str, int]` and `X | None` are all valid in Python 3.10+.

```python run
from typing import Iterable

def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values)

def summarise(name: str, gpas: list[float], threshold: float | None = None) -> dict[str, float | int]:
    out = {"n": len(gpas), "mean": round(mean(gpas), 3)}
    if threshold is not None:
        out["above"] = sum(g > threshold for g in gpas)
    return out

print(summarise("DS", [3.1, 2.8, 3.7], threshold=3.0))
```

A `@dataclass` generates `__init__`, `__repr__` and `__eq__` from the annotations — the right tool for small typed records before you reach for Pandas.

```python run
from dataclasses import dataclass, field

@dataclass
class Student:
    student_id: int
    name: str
    gpa: float
    courses: list[str] = field(default_factory=list)

    def standing(self) -> str:
        if self.gpa >= 3.5: return "honours"
        if self.gpa >= 2.0: return "good"
        return "probation"

s = Student(20230001, "Sara Khalil", 3.8, ["606315"])
print(s)
print(s.standing(), s == Student(20230001, "Sara Khalil", 3.8, ["606315"]))
```

:::exercise id=ex3 title="A validated record"
Create a `@dataclass` `Course` with fields `code: str`, `title: str`, `credits: int`. Its `__post_init__` must raise `ValueError` if `credits` is not between 1 and 6 inclusive, or if `code` is not exactly six digits.

```python
from dataclasses import dataclass

@dataclass
class Course:
    code: str
    title: str
    credits: int

    def __post_init__(self):
        ...

print(Course("606315", "Programming for DS", 3))
```

```python check
c = Course("606315", "Programming for DS", 3)
assert (c.code, c.title, c.credits) == ("606315", "Programming for DS", 3)
for bad in [("60631", "x", 3), ("6063150", "x", 3), ("60631A", "x", 3), ("606315", "x", 0), ("606315", "x", 7)]:
    try:
        Course(*bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"should have raised ValueError for {bad}")
```
:::

## 4 · Context managers

`with` guarantees clean-up — the file is closed, the lock released, the timer stopped — even if an exception is raised inside the block. You can write your own with `contextlib.contextmanager`: everything before `yield` is set-up, everything after is tear-down.

```python run
import time
from contextlib import contextmanager

@contextmanager
def timed(label):
    t0 = time.perf_counter()
    try:
        yield                          # the with-block runs here
    finally:
        print(f"[{label}] {(time.perf_counter() - t0) * 1000:.1f} ms")

with timed("build list"):
    _ = [i * i for i in range(300_000)]

with timed("sum generator"):
    _ = sum(i * i for i in range(300_000))
```

```python run
# clean-up runs even when the block raises
from contextlib import contextmanager

@contextmanager
def resource(name):
    print("open ", name)
    try:
        yield name
    finally:
        print("close", name)

try:
    with resource("db-connection") as r:
        raise RuntimeError("something went wrong while using " + r)
except RuntimeError as e:
    print("caught:", e)
```

:::exercise id=ex4 title="A temporary setting"
Write a context manager `override(d, key, value)` that sets `d[key] = value` on entry and **restores the previous value** (or removes the key if it did not exist) on exit — even if the block raises.

```python
from contextlib import contextmanager

@contextmanager
def override(d, key, value):
    ...

config = {"debug": False}
with override(config, "debug", True):
    print("inside :", config)
print("outside:", config)
```

```python check
cfg = {"debug": False}
with override(cfg, "debug", True):
    assert cfg["debug"] is True
assert cfg == {"debug": False}, "previous value must be restored"
with override(cfg, "level", 3):
    assert cfg["level"] == 3
assert "level" not in cfg, "a key that did not exist must be removed again"
try:
    with override(cfg, "debug", True):
        raise RuntimeError("boom")
except RuntimeError:
    pass
assert cfg == {"debug": False}, "must restore even when the block raises"
```
:::

## 5 · A tiny ETL, properly

The same job as last lesson's final example, now with a dataclass, safe parsing, and a timer.

```python run
import csv, time
from dataclasses import dataclass
from contextlib import contextmanager

@contextmanager
def timed(label):
    t0 = time.perf_counter()
    try: yield
    finally: print(f"[{label}] {(time.perf_counter() - t0) * 1000:.1f} ms")

@dataclass
class Row:
    student_id: int
    major: str
    gpa: float | None

def rows(path):
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                gpa = float(r["gpa"])
            except ValueError:
                gpa = None
            yield Row(int(r["student_id"]), r["major"].strip(), gpa)

with timed("ETL"):
    data = list(rows("data/students.csv"))

valid = [r for r in data if r.gpa is not None]
print(f"{len(data)} rows, {len(data) - len(valid)} unparseable GPAs")
print(max(valid, key=lambda r: r.gpa))
```

## Summary

* **Decorators** wrap behaviour around functions — `@timer`, `@lru_cache`, `@retry(n)`. Use `@wraps`. When stacked, the top decorator runs first.
* **Exceptions**: catch narrowly; decide explicitly what a bad value becomes; define your own hierarchy.
* **Type hints + dataclasses** make records self-describing and editor-checkable.
* **Context managers** guarantee clean-up; write yours with `@contextmanager`.

Next: *NumPy* — where loops disappear.

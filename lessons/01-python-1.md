# Advanced Python I — Modules, Comprehensions, Generators, Lambdas

<p class="lesson-intro">Week 1 · Programming for Data Science (606315)</p>

You already know Python. This lesson is about writing it the way data scientists do: compact where the intent is simple, lazy where the data is large. Every grey box with a **▶ Try it** button loads into the editor on the right — run it, then change it.

> **How this page works.** Press **▶ Try it** on any example to load and run it. Edit freely; **Reset** restores the original. Exercises have a **Check** button that runs hidden tests on your code.

> **🟢 Study these for the exams.** A green light next to a heading means that part follows the lecture slides: its examples are the slides' own, with extra explanation added, and the light covers everything under that heading. Anything without a green light is extra practice and background — useful, but not what the exams are built on.

## 1 · Modules 🟢

A **module** is a `.py` file containing functions, classes and variables that you can reuse. Every `import numpy` you will write from Week 3 onwards is the same idea: someone else's `.py` file, loaded by name.

There are three steps: **import** it (`import module_name`), **access** what is inside it (`module_name.function()`), and **explore** it with `dir()` and `help()`. The slide's example uses two files that sit in the same folder. Save the first as `studentslib.py`, then run the second:

```python
# studentslib.py
def my_best_student(*student):
    print("Best: " + student[2])
```

```python
# main.py
import studentslib
studentslib.my_best_student(
    "Dima","Mohd","Ali")
```

Running `main.py` prints `Best: Ali`. The `*student` in the definition collects all the arguments into one tuple, here `("Dima", "Mohd", "Ali")`, so `student[2]` is the third name. These two files cannot run in the browser, so use VS Code or a Codespace for them; the examples below use modules that ship with Python.

Python looks for `studentslib` in the folder of the script first and then in the installed libraries, which is why the file has to sit next to `main.py`. A name from a module is always written with its module as a prefix, `studentslib.my_best_student`, so two modules can each have a function with the same name without clashing.

Python comes with many ready-made modules:

| Module | Purpose |
|---|---|
| `math` | Math functions (ceil, sqrt, pi) |
| `sys` | System params & CLI arguments |
| `os` | Operating system interface |
| `random` | Random number generation |

```python run
import math
from math import sqrt
import random as rd

print(math.sqrt(16), sqrt(16))   # two ways to reach the same function
print(math.ceil(2.1), math.pi)
print(rd.randint(1, 999))        # a random whole number from 1 to 999
```

`import random as rd` gives the module a shorter name, and `from math import sqrt` brings a single function in so you can call it without the prefix.

**Explore.** Use `dir(module)` to list what a module contains and `help(module.func)` to read the documentation of one function:

```python run
import math

print(dir(math)[-8:])    # dir() lists every name inside the module; this shows the last eight
help(math.ceil)          # the documentation for one function
```

## 2 · Comprehensions

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

### 2.1 · List comprehensions: syntax and flow 🟢

The general form is

```
[ expression  for  item  in  iterable  if  condition ]
```

Python carries it out in four steps: **1 Iterate** (loop through the iterable), **2 Filter** (check the condition, which is optional), **3 Transform** (apply the expression) and **4 Collect** (build the new list). Notice that the expression is *written* first even though it is *evaluated* third.

```python run
# Even numbers 0-19
evens = [v for v in range(20)
         if v % 2 == 0]
# → [0,2,4,6,8,10,12,14,16,18]
print(evens)

# Celsius to Fahrenheit
celsius = [0, 10, 20.1, 34.5]
fahr = [(9/5)*t + 32
         for t in celsius]
print(fahr)

# Nested: square the squares
print([x**2 for x in [x**2 for x in range(11)]])

# Filter uppercase names
names = ["ahmad","Moh","Zain"]
print([n for n in names if n[0].isupper()])
```

The first example uses the filter step (`if v % 2 == 0`), the second only transforms (there is no `if`), and the fourth only filters (the expression is just `n`). In the nested example the inner comprehension builds the squares of 0 to 10 and the outer one squares each of them again. It reuses the name `x` for both loops, which works because each comprehension has its own scope, but `[y**2 for y in [x**2 for x in range(11)]]` is easier to read.

> **Don't confuse `()` with `[]`.** Parentheses create a *generator expression*, not a list. You will meet those in the generators section below.

### 2.2 · Dictionary comprehensions 🟢

The dictionary form puts a `key : value` pair in front of the `for`:

```
{ key : value  for  item  in  iterable  if  condition }
```

```python run
# Student → Random ID
import random as rd
names = ["ahmad","moh","zain"]
ids = {name: rd.randint(1,999)
       for name in names}
print(ids)
```

```python run
# Student → Email
students = ["Ahmad","Lina","Murad"]
emails = {
  s: f'{s.lower()}@uop.edu.jo'
  for s in students}
print(emails)
```

In both examples the loop variable (`name`, `s`) becomes the key, and the expression after the colon builds the value. The three comprehension forms differ only in their brackets:

| Feature | List | Dict | Generator |
|---|---|---|---|
| Brackets | `[ ]` | `{ k:v }` | `( )` |
| Returns | list | dict | generator obj |
| Memory | All at once | All at once | Lazy (one at a time) |

Generator expressions use `()`: the values are produced on demand, and you can iterate over them only once.

### 2.3 · Filtering and conditional values

An `if` **after** the `for` filters elements out. An `if/else` **before** the `for` chooses a value for every element. They look similar and do different things.

```python run
gpas = [3.4, 2.1, 3.9, 2.8, 1.9, 3.2]

honours = [g for g in gpas if g >= 3.0]                         # filter: fewer items
status  = ["pass" if g >= 2.0 else "probation" for g in gpas]   # map: same number of items

print(honours)
print(status)
```

### 2.4 · More on dictionary comprehensions, and set comprehensions

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

### 2.5 · Nested comprehensions

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

## 3 · Iterators 🟢

An **iterator** is an object that you can traverse one value at a time. Anything you can put in a `for` loop is *iterable*: lists, tuples, dicts, sets and strings. `iter()` turns an iterable into an iterator, and `next()` pulls the next value out of it.

### 3.1 · The iterator protocol

An iterator needs two methods: `__iter__()` returns the iterator itself, and `__next__()` returns the next value and **raises `StopIteration`** when there are no more.

```python run
students = ("Dima","Mohammad",
             "Ali","Rawan")
it = iter(students)
print(next(it))  # Dima
print(next(it))  # Mohammad
print(next(it))  # Ali
# next(it) → StopIteration!
```

Strictly, the tuple has four names, so the fourth `next(it)` still returns `"Rawan"` and it is the fifth call that raises `StopIteration`. A `for` loop is built on exactly this: it calls `iter()` once, then `next()` again and again, and stops quietly when `StopIteration` is raised. Passing a default to `next()` is a way to see the end without an error:

```python run
it = iter(("Dima", "Mohammad", "Ali", "Rawan"))
for name in it:                  # the for loop calls next() for you
    print(name)
print(next(it, "exhausted"))     # nothing left, so the default is returned
```

### 3.2 · A custom iterator: squares

```python run
class Squares:
    def __init__(self, n):
        self.n = n; self.current = 0
    def __iter__(self): return self
    def __next__(self):
        if self.current > self.n:
            raise StopIteration
        val = self.current ** 2
        self.current += 1
        return val

print(list(Squares(5)))  # [0,1,4,9,16,25]
```

`__init__` stores the state: the limit `n` and a counter `current`. `__iter__` returns `self`, because the object is its own iterator. Each call to `__next__` returns the next square and moves the counter on, and once the counter passes `n` it raises `StopIteration`. `list()` simply keeps calling `next()` until that happens. Generators, in the next section, give you the same behaviour with far less code: no class, no `__next__` and no `StopIteration`.

:::exercise id=s21 title="Countdown iterator (slide 21)"
Write the class `Countdown` so that iterating over `Countdown(k)` gives `k, k-1, ..., 1`. Keep the current value as state, and `raise StopIteration` when there is nothing left.

```python
class Countdown:
    def __init__(self, k):
        self.current = k

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration      # replace this

print(list(Countdown(5)))        # expected [5, 4, 3, 2, 1]
```

```python check
assert list(Countdown(5)) == [5, 4, 3, 2, 1], f"got {list(Countdown(5))}"
assert list(Countdown(1)) == [1]
assert list(Countdown(0)) == [], "Countdown(0) has nothing to give"
it = Countdown(2)
assert iter(it) is it, "__iter__ should return self"
assert (next(it), next(it)) == (2, 1)
try:
    next(it)
except StopIteration:
    pass
else:
    raise AssertionError("next() must raise StopIteration when the countdown is over")
```
:::

## 4 · Generators: processing more than fits in memory

A list holds every element at once. A **generator** produces one element at a time, on demand, so a 10 GB file can be processed with a few kilobytes of RAM. Any function containing `yield` is a generator function.

### 4.1 · Generator functions: `yield` vs `return` 🟢

`yield` produces values one at a time, pausing and resuming execution. Unlike `return`, the function's state is preserved between calls.

```python run
# Simple generator
def simple_gen(x):
    yield x
    yield x * 2
    yield x * 3

for v in simple_gen(5):
    print(v)  # 5, 10, 15

g = simple_gen(5)
print(next(g))  # 5
print(next(g))  # 10
```

Calling `simple_gen(5)` runs nothing yet; it returns a generator. The first `next(g)` runs the body up to the first `yield` and pauses there with `5`, and the second resumes and pauses at the next `yield` with `10`. A `for` loop makes the `next()` calls for you and stops when the function ends.

```python run
# Fibonacci generator
def genfibon(n):
    a, b = 1, 1
    for i in range(n):
        yield a
        a, b = b, a + b

for num in genfibon(10):
    print(num)
# 1,1,2,3,5,8,13,21,34,55
```

`a, b = b, a + b` updates both names at once, so only two numbers are ever held in memory, however large `n` is. A function that used `return` would have to build and hand back the whole sequence in one go.

| Feature | Regular Function | Generator |
|---|---|---|
| Keyword | `return` | `yield` |
| Memory | All results at once | One at a time (lazy) |
| State | Lost after return | Preserved between yields |

### 4.2 · Generator expressions and practice 🟢

```python run
# Generator expression (like list comp but with ())
g = (x**2 for x in range(1, 6))
print(next(g))  # 1
print(next(g))  # 4
print(list(g))  # [9, 16, 25]  remaining
print(list(g))  # []  exhausted!
```

`list(g)` takes whatever is left, which is why it shows only `[9, 16, 25]`, and once a generator has been used up it stays empty.

```python run
# Practical: email + password generator
import random
def email_and_password(names):
    symbols = ['@','#','_']
    for name in names:
        email = f"{name.lower()}@uop.edu.jo"
        pwd = f"{name[0]}{random.choice(symbols)}"\
              f"{random.randint(100,999)}"
        yield email, pwd

for e, p in email_and_password(
    ['Ahmad','Zaid']):
    print(e, p)
```

`yield email, pwd` yields a tuple, and `for e, p in ...` unpacks it into two names. The backslash at the end of the `pwd` line continues the statement on the next line, where a second f-string is glued on to the first.

```python run
# Unpacking operator * with generators
import random as rd
stname = ["ahmad","moh","zain"]
y = (f'{rd.randint(1,999)}' for n in stname)
print([*y])   # e.g. ['547','23','891']
print([*y])   # []  ← already exhausted!
```

`[*y]` unpacks every value of the generator into a list, much like `list(y)`. The second one is empty because the first already used the generator up.

:::exercise id=s24a title="Cubes (slide 24, exercise 1)"
Create a **generator expression** `cubes` for the cubes of 1 to 10, then convert it to a list called `cube_list`.

```python
cubes = (x for x in range(1, 11))     # change the expression so it gives cubes
cube_list = list(cubes)
print(cube_list)                      # expected [1, 8, 27, 64, 125, 216, 343, 512, 729, 1000]
```

```python check
import types
assert isinstance(cubes, types.GeneratorType), "cubes must be a generator expression (round brackets)"
assert cube_list == [i ** 3 for i in range(1, 11)], f"got {cube_list}"
```
:::

:::exercise id=s24b title="Emails (slide 24, exercise 2)"
Given student names, produce their emails (`name.lower()` + `@uop.edu.jo`) with a **generator function** that uses `yield`.

```python
def emails(names):
    for name in names:
        yield name            # replace this: yield the email address instead

print(list(emails(["Ahmad", "Lina"])))   # expected ['ahmad@uop.edu.jo', 'lina@uop.edu.jo']
```

```python check
import types
g = emails(["Ahmad", "Lina", "Murad"])
assert isinstance(g, types.GeneratorType), "emails must be a generator function (use yield)"
assert list(g) == ["ahmad@uop.edu.jo", "lina@uop.edu.jo", "murad@uop.edu.jo"]
assert list(emails([])) == [], "no names, no emails"
```
:::

**Think about it (slide 24, question 3).** Why does printing `[*g]` twice give different results?

<details>
<summary>Show the answer</summary>

A generator is used up as you read it. The first `[*g]` pulls every value out, so the second `[*g]` finds nothing left and gives `[]`. To get the values again you have to build a new generator.

</details>

### 4.3 · More on generators: laziness and memory

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

### 4.4 · A streaming pipeline over a log file

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

### 4.5 · `itertools` — lazy building blocks

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

## 5 · `lambda`, `sorted`, `map`, `filter`

A `lambda` is an anonymous one-expression function. Its natural home is the `key=` argument of `sorted`, `min` and `max` — and later, Pandas' `.apply()`.

### 5.1 · Lambda: syntax and basics 🟢

```
lambda  arguments  :  expression
```

A lambda is **anonymous** (no name required), holds a **single expression** (no statements), takes **any number of arguments**, and **returns the result automatically**.

```python run
# Add 20 to input
x = lambda a: a + 20
print(x(6))  # → 26

# Sum two arguments
x = lambda a, b: a + b
print(x(10, 22))  # → 32
```

A regular function and its lambda equivalent give the same result:

```python run
# Regular function
def square(num):
    return num ** 2
print(square(5))  # → 25

# Lambda equivalent
square = lambda num: num ** 2
print(square(5))  # → 25
# Same result, one line!
```

"Single expression only" means no loops, no assignments and no `return` inside a lambda. A conditional expression such as `a if cond else b` is still an expression, so `lambda n: "even" if n % 2 == 0 else "odd"` is allowed. Giving a lambda a name, as above, is only there to show that it matches the `def`; in real code a lambda is normally passed straight into another call, as the next sections show.

### 5.2 · Lambda: closures and lambda as an argument 🟢

A lambda can be the **return value** of a function. The lambda below remembers `domain` even after `email_gen` has finished, which is called a **closure**: an inner function that keeps the variables of the function around it. Decorators in the next lesson rely on exactly the same mechanism.

```python run
def email_gen(domain):
    return lambda n: \
      f'{n.lower()}@{domain}'

uop = email_gen('uop.edu.jo')
gmail = email_gen('gmail.com')
print(uop('Ahmad'))  # ahmad@uop.edu.jo
print(gmail('Ahmad')) # ahmad@gmail.com
```

Each call to `email_gen` builds a separate lambda with its own `domain`. A lambda can also be passed **as an argument** to a function:

```python run
def student_info(name, gen):
    return {name: gen(name)}

email = lambda n: \
  f'{n.lower()}@uop.edu.jo'
passw = lambda n: f'{n[0]}{__import__("random").randint(1,999)}'

print(student_info('Ahmad',email))
print(student_info('Ahmad',passw))   # also try the password generator
```

`student_info` does not know what `gen` does; it only calls it with the name. That is why you can hand it the `email` lambda or the `passw` lambda and get a different result each time. `__import__("random")` imports the module inside the expression, because a lambda cannot contain an `import` statement.

A real-world example, a tax calculator:

```python run
def tax_generator(rate):
    return lambda n: n * rate

vat = tax_generator(0.16)
print(vat(50))       # → 8.0

def salary_calc(salary, tax_gen):
    return salary - tax_gen(salary)

income_tax = lambda n: n * 0.05
print(salary_calc(700, income_tax))  # → 665.0
```

`tax_generator(0.16)` is a closure, a function with the 16% rate built in, and `salary_calc` receives the tax rule as an argument, so the same function works for any tax. Lambdas shine when they are passed to `map()`, `filter()` and `sorted()`, which come next.

### 5.3 · `map()`: transform every element 🟢

```
map( function,  iterable )  →  iterator of results
```

`map` applies the function to every element and gives back the results. The output has the same number of elements as the input.

```python run
# Generate emails
students = ["Ahmad","Lina","Murad"]
emails = map(
  lambda s: f'{s.lower()}@uop.edu.jo',
  students)
print([*emails])

# Sum student marks
marks = [[10,15],[13,12],[7,11]]
totals = map(
  lambda s: sum(s),
  marks)
print([*totals])  # [25, 25, 18]
```

`map()` returns an iterator, so use `[*result]` or `list(result)` to materialize it. In the second example the lambda only calls `sum`, so `map(sum, marks)` would do the same job.

### 5.4 · `filter()`: select by condition 🟢

```
filter( function,  iterable )  →  items where function returns True
```

```python run
# Filter names starting with A/B/C
students = {"Ahmad":[10,15],
  "Lina":[13,12],"Bassam":[7,11]}
first = filter(
  lambda s: s[0] in 'ABC',
  students)
print([*first])  # ['Ahmad', 'Bassam']

# Filter failed students (sum<20)
failed = dict(filter(
  lambda p: sum(p[1]) < 20,
  students.items()
))
print(failed)
# {'Bassam': [7, 11]}
```

Looping over a dict gives its **keys**, so in the first example the lambda receives the names. `students.items()` gives `(name, marks)` pairs instead, which is why the second lambda uses `p[1]` for the marks (the second item of each pair). Wrapping the result in `dict(...)` turns the surviving pairs back into a dictionary.

| | `map()` | `filter()` |
|---|---|---|
| Purpose | Transform each element | Select by condition |
| Output size | Same as input | ≤ input (True items only) |
| Lambda returns | Transformed value | True / False |

### 5.5 · `sorted()`: custom sorting 🟢

```
sorted( iterable,  key=function,  reverse=False )  →  sorted list
```

```python run
# Sort by last character
students = {"Ahmad":[10,15],
  "Lina":[13,12],"Bassam":[7,11]}
result = sorted(students,
  key=lambda s: s[-1])
print(result) # ['Lina', 'Ahmad', 'Bassam']

# Sort by total marks
result = dict(sorted(
  students.items(),
  key=lambda p: sum(p[1])
))
print(result)
# {'Bassam': [7, 11], 'Ahmad': [10, 15], 'Lina': [13, 12]}
```

The `key` function is called once on every element, and Python sorts by the values it returns. The names end in `a` (Lina), `d` (Ahmad) and `m` (Bassam), which gives the first order. In the second example the totals are 25, 25 and 18, so Bassam comes first, and Ahmad stays ahead of Lina because Python's sort keeps equal items in their original order.

| Function | What it does | Typical Use |
|---|---|---|
| `map(f, iter)` | Transform each element | Convert, compute, format |
| `filter(f, iter)` | Keep items where f→True | Select, validate, remove |
| `sorted(iter, key=f)` | Sort by custom key | Rank, order, prioritize |

### 5.6 · More on `lambda`, `sorted`, `map` and `filter`

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

## 6 · Putting it together

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

## 7 · Virtual environments and `.env` 🟢

A **virtual environment** is a private copy of Python with its own installed packages. It isolates the dependencies of one project from another, avoids version conflicts between projects, makes an environment reproducible, and keeps the system Python clean.

These commands run in a terminal (in VS Code, open **Terminal → New Terminal**), not in the browser:

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install packages
pip install numpy pandas
```

`python -m venv venv` creates a folder called `venv` (the second `venv` is the folder name, and you can choose another). Once the environment is activated, your terminal prompt shows `(venv)` and `pip install` puts packages inside it instead of the system Python. Do the activation again each time you open a new terminal for the project, and run `pip freeze > requirements.txt` to record the packages so someone else can recreate the environment.

**Environment variables with `.env`.** A `.env` file stores configuration and secrets as `NAME=value` lines, outside your source code:

```ini
# .env file
SECRET_KEY=123
DATABASE=user:123@localhost/shop
API_KEY=232faasd112f
ADMIN=True
```

```python
# app.py
from dotenv import load_dotenv
import os

load_dotenv()
SECRET = os.getenv('SECRET_KEY')
DB = os.getenv('DATABASE')
print(f'SECRET: {SECRET}')
```

Keeping secrets out of the source code means they cannot leak when you share or publish the code, and it makes configuration easy to change across environments. You need `pip install python-dotenv` first. Two cautions: add `.env` to your `.gitignore` so it is never committed, and remember that every value read from it is **text**. `os.getenv('ADMIN')` returns the string `'True'`, and the string `'False'` is also truthy, so compare explicitly: `os.getenv('ADMIN') == 'True'`.

## 8 · Command-line arguments 🟢

`sys.argv` is a list of **strings** passed to the script when you run it. `sys.argv[0]` is always the script name, and the arguments follow.

```
$ python  main.py  Ahmad  25
          sys.argv[0]  sys.argv[1]  sys.argv[2]
```

```python
# main.py
import sys, random

name = sys.argv[1]
print('Email:',
  f'{name.lower()}@uop.edu.jo')
print('Password:',
  f'{name.upper()[0]}'
  f'{random.randint(100,999)}')
```

```
$ python main.py Ahmad
Email: ahmad@uop.edu.jo
Password: A480
```

The password changes on every run because of `random`. For `python main.py Ahmad 25`:

| Expression | Value |
|---|---|
| `sys.argv[0]` | `'main.py'` (script name) |
| `sys.argv[1]` | `'Ahmad'` (1st argument) |
| `len(sys.argv)` | `3` (total count) |

> **Always check `len(sys.argv)` before accessing indices to avoid `IndexError`.**

The browser has no terminal, so this version sets `sys.argv` by hand to imitate `python main.py Ahmad`; the rest is the slide's code:

```python run
import sys, random

sys.argv = ["main.py", "Ahmad"]    # imitates:  python main.py Ahmad   (browser only)

name = sys.argv[1]
print('Email:',
  f'{name.lower()}@uop.edu.jo')
print('Password:',
  f'{name.upper()[0]}'
  f'{random.randint(100,999)}')
```

Every argument arrives as a string, so convert it when you need a number: `int(sys.argv[2])`. And this is the length check from the box above in action:

```python run
import sys
sys.argv = ["main.py"]             # imitates:  python main.py   (no argument given)

if len(sys.argv) < 2:
    print("usage: python main.py <name>")
else:
    print("Hello", sys.argv[1])
```

## Summary

* **Modules** are reusable `.py` files: `import` them, call their functions with the module prefix, and explore them with `dir()` and `help()`.
* **Comprehensions** replace short accumulate-loops; keep them to one line.
* **Iterators** follow the `__iter__` / `__next__` protocol and signal the end with `StopIteration`.
* **Generators** make pipelines lazy — chain them to stream big files.
* **`lambda`** belongs in `key=`; prefer comprehensions over `map`/`filter` in new code.
* **`venv` and `.env`** isolate dependencies and keep secrets out of the code; **`sys.argv`** passes arguments to a script.

Next: *Advanced Python II* — decorators, exceptions, type hints and context managers.

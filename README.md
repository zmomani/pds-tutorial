# Programming for Data Science — Interactive Tutorial

**University of Petra · Faculty of Information Technology · 606315**

A browser-based tutorial: the lesson on the left, a live Python editor on the right. Python runs *inside the
browser* (via [Pyodide](https://pyodide.org)), so students need nothing but a link — no installation, no account.

**Live site:** https://zmomani.github.io/pds-tutorial/

## Lessons

| # | Week | Lesson | Exercises |
|---|---|---|---|
| 01 | 1 | Advanced Python I — comprehensions, generators, lambdas | 5 |
| 02 | 2 | Advanced Python II — decorators, errors, type hints, context managers | 4 |
| 03 | 3 | NumPy — arrays, masks, broadcasting, random, linear algebra | 5 |
| 04 | 4 | Pandas I — load, select, clean, missing values | 5 |
| 05 | 5 | Pandas II — groupby, merge, pivot, time series, EDA | 5 |
| 07 | 7 | JSON — parsing, nested data, APIs | 4 |
| 13 | 13 | Scikit-learn — preprocessing, pipelines, evaluation | 3 |

Weeks 6 (multiprocessing), 8–9 (web scraping) and 10–12 (Django) need a real terminal and network access, so
they live in the [Codespaces repository](https://github.com/zmomani/pds-606315) instead.

## How a lesson works

* Every example has a **▶ Try it** button that loads it into the editor and runs it. Students are meant to edit and re-run (`Ctrl+Enter`).
* **Exercises** open a starter in the editor; **✓ Check** runs hidden tests and shows ✓ or the failing assertion.
  Passed exercises are remembered in the browser (`localStorage`) and shown on the home page.
* A DataFrame that is the last expression of a run is shown as a table; Matplotlib figures appear as images.
* Datasets in `data/` are mounted into the in-browser file system, so `pd.read_csv("data/students.csv")` works as it would locally.

## Writing a lesson

Lessons are plain Markdown in `lessons/`, registered in `lessons/manifest.json`.

````markdown
```python run
print("a runnable example — gets a Try-it button")
```

:::exercise id=ex1 title="Short title"
Description of the task (Markdown).

```python
def solve(x):
    ...          # starter code shown to the student
```

```python check
assert solve(2) == 4, "message shown when this fails"
```
:::
````

Manifest fields: `packages` (Pyodide packages to load, e.g. `numpy`, `pandas`, `matplotlib`, `scikit-learn`),
`data` (files from `data/` to mount), `exercises` (ids, for the progress counter).

## Testing

`tests/run_lessons.py` executes every example in CPython and verifies each exercise twice: the untouched
starter must **fail** its check (otherwise the check is vacuous) and the reference solution in
`tests/solutions.py` must **pass**. The GitHub Actions workflow runs this before every deployment.

```bash
pip install numpy pandas matplotlib scikit-learn
python tests/run_lessons.py
```

To preview locally: `python -m http.server 8000` in the repository root, then open http://localhost:8000.

## Stack

Static HTML/CSS/JS, no build step. CodeMirror 5, marked and highlight.js are vendored in `vendor/`
(licences listed there); Pyodide 0.26 is loaded from the jsDelivr CDN at runtime (~10 MB on first visit, cached afterwards).
Deployed to GitHub Pages by `.github/workflows/deploy.yml`.

## Limits

* Code runs on the page's main thread; an infinite loop freezes the tab (reload to recover).
* `input()` is disabled; cross-site HTTP requests are blocked by the browser, so APIs are simulated in the JSON lesson.
* The first run of a NumPy/Pandas/Scikit-learn lesson downloads those packages (10–20 MB) once.

---

*Course materials © University of Petra. Instructor: Dr. Zaid G. Momani.*

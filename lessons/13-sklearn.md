# Scikit-learn — Preprocessing, Models, Evaluation

<p class="lesson-intro">Week 13 · Programming for Data Science (606315)</p>

Scikit-learn gives every model the same three methods — `fit`, `predict`, `score` — and every preprocessing step the same two — `fit`, `transform`. Once you know that **estimator API**, switching from a linear model to a random forest is a one-line change. This lesson builds the pipeline your Project Stage 3 model endpoint will wrap.

> The first run of a box below takes a few seconds longer while Scikit-learn loads.

## 1 · The estimator API in sixty seconds

Features `X` are a 2-D array (rows × columns); the target `y` is 1-D. Fit on training data, evaluate on data the model has never seen.

```python run
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(0)
X = rng.uniform(0, 10, size=(200, 1))               # one feature
y = 3 * X[:, 0] + 2 + rng.normal(0, 1.5, 200)       # a noisy line

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

model = LinearRegression().fit(X_train, y_train)
print("slope", model.coef_.round(2), "intercept", round(model.intercept_, 2))
print("R² on test:", round(model.score(X_test, y_test), 3))
print("predict:", model.predict([[5.0]]).round(2))
```

## 2 · Preparing data: scaling and encoding

Distance- and gradient-based models (k-NN, SVM, logistic regression, neural nets) need features on comparable scales. Tree models do not. Text categories must be encoded as numbers — **one-hot** for nominal categories. Always `fit` the transformer on the training set only, then `transform` both sets.

```python run
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder

X = np.array([[1200.0, 3], [850.0, 1], [2300.0, 4], [400.0, 2]])   # [credits-ish, year]
print(StandardScaler().fit_transform(X).round(2))     # mean 0, sd 1 per column
print(MinMaxScaler().fit_transform(X).round(2))       # 0–1 per column

majors = np.array([["DS"], ["CS"], ["DS"], ["AI"]])
enc = OneHotEncoder(sparse_output=False).fit(majors)
print(enc.categories_)
print(enc.transform(majors))
```

:::exercise id=ex1 title="Fit on train, transform both"
`scale_split(X_train, X_test)` returns `(Xtr_s, Xte_s)` standardised with a `StandardScaler` that is fitted on **training data only**. Check: the training columns must have mean ≈ 0, and the same transformation (not a refit) must be applied to the test set.

```python
from sklearn.preprocessing import StandardScaler
import numpy as np

def scale_split(X_train, X_test):
    scaler = StandardScaler()
    ...
    return Xtr_s, Xte_s

Xtr = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
Xte = np.array([[2.0, 20.0], [4.0, 40.0]])
print(scale_split(Xtr, Xte))
```

```python check
import numpy as np
Xtr = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
Xte = np.array([[2.0, 20.0], [4.0, 40.0]])
a, b = scale_split(Xtr, Xte)
assert np.allclose(a.mean(axis=0), 0) and np.allclose(a.std(axis=0), 1), "train must be standardised"
assert np.allclose(b[0], [0, 0]), "test row equal to the train mean must map to 0 — scaler must NOT be refit on test"
assert np.allclose(b[1], [2.449, 2.449], atol=1e-3), f"got {b[1]}"
```
:::

## 3 · A classification problem from the course data

We predict whether a student is on **honours** (GPA ≥ 3.5) from `year`, `credits`, `major` and `city`. The signal is weak by construction — the data is synthetic — which makes it a good lesson in honest evaluation: accuracy alone can look fine on an imbalanced target.

```python run
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

df = (pd.read_csv("data/students.csv")
        .assign(major=lambda d: d["major"].str.strip(), city=lambda d: d["city"].str.title(),
                gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
        .drop_duplicates().dropna(subset=["gpa"]).reset_index(drop=True))
df["honours"] = (df["gpa"] >= 3.5).astype(int)
print(df["honours"].value_counts(normalize=True).round(2))

X = pd.get_dummies(df[["year", "credits", "major", "city"]], drop_first=True).astype(float)
y = df["honours"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)

for name, model in [("majority class", DummyClassifier(strategy="most_frequent")),
                    ("logistic regression", LogisticRegression(max_iter=1000))]:
    pred = model.fit(X_train, y_train).predict(X_test)
    print(f"{name:20s} acc={accuracy_score(y_test, pred):.2f}  "
          f"prec={precision_score(y_test, pred, zero_division=0):.2f}  "
          f"rec={recall_score(y_test, pred):.2f}  f1={f1_score(y_test, pred):.2f}")
print(confusion_matrix(y_test, pred))
```

Both models reach similar accuracy because ~85 % of students are not on honours — the **baseline** is what any model has to beat. Report precision, recall and F1, and always compare against a `DummyClassifier`.

## 4 · Pipelines — preprocessing and model as one object

A `Pipeline` chains transformers and a final estimator, so `fit` fits everything in order and `predict` transforms then predicts. `ColumnTransformer` applies different preprocessing to different columns. This is the object you will pickle and load inside your Django view.

```python run
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score

df = (pd.read_csv("data/students.csv")
        .assign(major=lambda d: d["major"].str.strip(), city=lambda d: d["city"].str.title(),
                gpa=lambda d: pd.to_numeric(d["gpa"], errors="coerce"))
        .drop_duplicates().dropna(subset=["gpa"]).reset_index(drop=True))
X = df[["year", "credits", "major", "city"]]
y = (df["gpa"] >= 3.5).astype(int)

pre = ColumnTransformer([
    ("num", StandardScaler(), ["year", "credits"]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["major", "city"]),
])
pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])

scores = cross_val_score(pipe, X, y, cv=5, scoring="f1")
print("5-fold F1:", scores.round(2), "mean", scores.mean().round(2))

pipe.fit(X, y)
new_student = pd.DataFrame([{"year": 3, "credits": 90, "major": "Data Science", "city": "Amman"}])
print("P(honours) for a new student:", pipe.predict_proba(new_student)[0, 1].round(3))
```

:::exercise id=ex2 title="Build the pipeline"
`make_pipeline()` returns an **unfitted** `Pipeline` with a `ColumnTransformer` that standardises `["units", "unit_price"]` and one-hot encodes `["product", "city"]` (`handle_unknown="ignore"`), followed by a `LinearRegression`. It will be used to predict daily revenue-per-row from `sales_2025.csv`.

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression

def make_pipeline():
    pre = ColumnTransformer([
        ("num", ..., [...]),
        ("cat", ..., [...]),
    ])
    return Pipeline([("pre", pre), ("model", ...)])

print(make_pipeline())
```

```python check
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
p = make_pipeline()
assert isinstance(p, Pipeline) and isinstance(p.steps[0][1], ColumnTransformer), "Pipeline(ColumnTransformer, model)"
assert isinstance(p.steps[-1][1], LinearRegression)
sales = pd.read_csv("data/sales_2025.csv")
sales["revenue"] = sales["units"] * sales["unit_price"]
p.fit(sales[["units", "unit_price", "product", "city"]], sales["revenue"])
r2 = p.score(sales[["units", "unit_price", "product", "city"]], sales["revenue"])
assert r2 > 0.85, f"R² {r2:.2f} — check the column lists"
new = pd.DataFrame([{"units": 5, "unit_price": 800.0, "product": "Laptop", "city": "Nowhere"}])
p.predict(new)   # unknown city must not raise → handle_unknown='ignore'
```
:::

## 5 · Regression metrics and a model comparison

For regression report **MAE** (in the units of the target), **RMSE** (penalises large errors) and **R²**. Compare at least two model families; trees need no scaling and capture interactions.

```python run
import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

sales = pd.read_csv("data/sales_2025.csv", parse_dates=["date"])
sales["revenue"] = sales["units"] * sales["unit_price"]
sales["month"] = sales["date"].dt.month
sales["weekday"] = sales["date"].dt.weekday
X = sales[["units", "product", "city", "month", "weekday"]]     # unit_price withheld: make it harder
y = sales["revenue"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), ["product", "city"])], remainder="passthrough")
for name, est in [("linear", LinearRegression()), ("random forest", RandomForestRegressor(n_estimators=100, random_state=0))]:
    pipe = Pipeline([("pre", pre), ("m", est)]).fit(X_train, y_train)
    pred = pipe.predict(X_test)
    print(f"{name:14s} MAE={mean_absolute_error(y_test, pred):8.0f}  RMSE={root_mean_squared_error(y_test, pred):8.0f}  R²={r2_score(y_test, pred):.3f}")
```

:::exercise id=ex3 title="Evaluate honestly"
`evaluate(model, X, y)` splits with `test_size=0.25, random_state=0`, fits on the training part, and returns a dict `{"mae": …, "rmse": …, "r2": …}` computed on the **test** part, rounded to 2 dp.

```python
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

def evaluate(model, X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
    ...
    return {"mae": ..., "rmse": ..., "r2": ...}

import numpy as np
from sklearn.linear_model import LinearRegression
rng = np.random.default_rng(0)
X = rng.uniform(0, 10, size=(200, 1)); y = 3 * X[:, 0] + 2 + rng.normal(0, 1.5, 200)
print(evaluate(LinearRegression(), X, y))
```

```python check
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
rng = np.random.default_rng(0)
X = rng.uniform(0, 10, size=(200, 1)); y = 3 * X[:, 0] + 2 + rng.normal(0, 1.5, 200)
r = evaluate(LinearRegression(), X, y)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0)
p = LinearRegression().fit(Xtr, ytr).predict(Xte)
assert set(r) == {"mae", "rmse", "r2"}
assert abs(r["mae"] - round(mean_absolute_error(yte, p), 2)) < 1e-9, "mae on the test split"
assert abs(r["rmse"] - round(root_mean_squared_error(yte, p), 2)) < 1e-9
assert abs(r["r2"] - round(r2_score(yte, p), 2)) < 1e-9
```
:::

## 6 · Saving the model for the web app

In Stage 3 the Django view loads a pickled pipeline and calls `predict_proba` on a one-row DataFrame built from the form. Use `joblib` and save the whole pipeline, never just the model, so preprocessing travels with it.

```python
import joblib
joblib.dump(pipe, "model.joblib")                 # training script
pipe = joblib.load("model.joblib")                # Django view, at start-up
pipe.predict_proba(pd.DataFrame([form_data]))
```

## Summary

* Everything is `fit` / `predict` (/ `transform`); fit transformers on **training data only**.
* Scale for linear/distance models; one-hot encode nominal categories; trees need neither.
* Beat the **baseline**; report precision/recall/F1 or MAE/RMSE/R², and use cross-validation.
* Wrap preprocessing + model in a `Pipeline`; that single object is what you deploy.

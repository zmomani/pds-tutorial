/* Programming for Data Science – interactive tutorial
 * Lesson text (Markdown) on the left, a Python editor on the right.
 * Python runs in the browser through Pyodide; no server is involved.
 */
(() => {
  "use strict";

  // ---------------------------------------------------------------- state
  const S = {
    manifest: [],
    lesson: null,          // current lesson object from manifest
    exercises: {},         // id -> {id,title,starter,check,el}
    current: null,         // {kind:'example'|'exercise', id, code}
    pyodide: null,
    pyReady: null,         // promise
    loadedPkgs: new Set(),
    mountedData: new Set(),
    running: false,
  };

  const $ = (sel) => document.querySelector(sel);
  const el = {
    home: $("#home"), lesson: $("#lesson"), content: $("#lesson-content"),
    list: $("#lesson-list"), select: $("#lesson-select"),
    prev: $("#btn-prev"), next: $("#btn-next"),
    run: $("#btn-run"), check: $("#btn-check"), reset: $("#btn-reset"), clear: $("#btn-clear"),
    out: $("#output"), runTime: $("#run-time"), wbTitle: $("#wb-title"),
    status: $("#py-status"), statusText: $("#py-status-text"), splitter: $("#splitter"),
  };

  // ---------------------------------------------------------------- editor
  const editor = CodeMirror.fromTextArea($("#editor"), {
    mode: "python", theme: "material-darker", lineNumbers: true, indentUnit: 4,
    matchBrackets: true, autoCloseBrackets: true, viewportMargin: Infinity,
    extraKeys: {
      "Ctrl-Enter": () => runEditor(), "Cmd-Enter": () => runEditor(),
      "Shift-Ctrl-Enter": () => checkExercise(), "Shift-Cmd-Enter": () => checkExercise(),
      Tab: (cm) => cm.somethingSelected() ? cm.indentSelection("add") : cm.replaceSelection("    ", "end"),
    },
  });

  // ---------------------------------------------------------------- python runtime
  const PRELUDE = `
import sys, io, base64, json
import builtins
def _pds_repr(obj):
    try:
        import pandas as _pd
        if isinstance(obj, (_pd.DataFrame,)):
            return {"kind": "html", "value": obj.to_html(max_rows=60, max_cols=25, border=0)}
        if isinstance(obj, _pd.Series):
            return {"kind": "html", "value": obj.to_frame().to_html(max_rows=60, border=0)}
    except Exception:
        pass
    return {"kind": "text", "value": repr(obj)}

def _pds_figs():
    if "matplotlib.pyplot" not in sys.modules:
        return []
    import matplotlib.pyplot as plt
    out = []
    for n in plt.get_fignums():
        fig = plt.figure(n)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
        out.append(base64.b64encode(buf.getvalue()).decode())
    plt.close("all")
    return out

def _pds_setup_mpl():
    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    plt.rcParams["figure.figsize"] = (6.4, 3.6)
    plt.rcParams["figure.dpi"] = 100

def input(prompt=""):
    raise RuntimeError("input() is not available in the browser tutorial. Assign the value to a variable instead.")
builtins.input = input
`;

  function setStatus(text, cls) {
    el.statusText.textContent = text;
    el.status.className = "status" + (cls ? " " + cls : "");
  }

  async function ensurePython() {
    if (S.pyReady) return S.pyReady;
    S.pyReady = (async () => {
      setStatus("Loading Python (≈10 MB, once)…");
      const py = await loadPyodide({ indexURL: window.PDS_PYODIDE_URL });
      await py.runPythonAsync(PRELUDE);
      S.pyodide = py;
      setStatus("Python ready", "ready");
      return py;
    })().catch((e) => {
      setStatus("Python failed to load — check your connection and reload", "error");
      throw e;
    });
    return S.pyReady;
  }

  async function prepareLesson(lesson) {
    const py = await ensurePython();
    const pkgs = (lesson.packages || []).filter((p) => !S.loadedPkgs.has(p));
    if (pkgs.length) {
      setStatus("Loading " + pkgs.join(", ") + "…");
      await py.loadPackage(pkgs);
      pkgs.forEach((p) => S.loadedPkgs.add(p));
      if (pkgs.includes("matplotlib")) await py.runPythonAsync("_pds_setup_mpl()");
    }
    const files = (lesson.data || []).filter((f) => !S.mountedData.has(f));
    if (files.length) {
      setStatus("Loading datasets…");
      try { py.FS.mkdir("data"); } catch (_) { /* exists */ }
      await Promise.all(files.map(async (f) => {
        const r = await fetch("data/" + f);
        if (!r.ok) throw new Error("Could not fetch data/" + f);
        py.FS.writeFile("data/" + f, await r.text());
        S.mountedData.add(f);
      }));
    }
    setStatus("Python ready", "ready");
    return py;
  }

  // ---------------------------------------------------------------- output helpers
  function out(kind, text) {
    const span = document.createElement("span");
    span.className = kind;
    span.textContent = text;
    el.out.appendChild(span);
    el.out.scrollTop = el.out.scrollHeight;
  }
  function outHTML(html) {
    const div = document.createElement("div");
    div.innerHTML = html;
    el.out.appendChild(div);
    el.out.scrollTop = el.out.scrollHeight;
  }
  function clearOut() { el.out.innerHTML = ""; el.runTime.textContent = ""; }

  function cleanTraceback(msg) {
    // Drop Pyodide's internal frames, keep the user's.
    const lines = String(msg).split("\n");
    const keep = [];
    let skip = false;
    for (const ln of lines) {
      const isFrame = /^\s+File "/.test(ln);
      if (isFrame) skip = /File "\/lib\/python|pyodide/.test(ln);   // internal frame → hide it and its source lines
      if (skip) continue;
      keep.push(ln.replace('File "<exec>"', 'File "<your code>"'));
    }
    return keep.join("\n").trim();
  }

  async function execute(code, { globals, echoResult = true } = {}) {
    const py = S.pyodide;
    py.setStdout({ batched: (s) => out("stdout", s + "\n") });
    py.setStderr({ batched: (s) => out("stderr", s + "\n") });
    let result;
    try {
      result = await py.runPythonAsync(code, { globals });
    } finally {
      // figures produced during the run
      const figs = py.runPython("_pds_figs()").toJs();
      for (const b64 of figs) outHTML(`<img alt="figure" src="data:image/png;base64,${b64}">`);
    }
    if (echoResult && result !== undefined && result !== null) {
      const r = py.globals.get("_pds_repr")(result);
      const info = r.toJs({ dict_converter: Object.fromEntries });
      r.destroy();
      if (info.kind === "html") outHTML(info.value); else out("result", info.value + "\n");
      if (result && typeof result.destroy === "function") result.destroy();
    }
  }

  async function runEditor() {
    if (S.running || !S.lesson) return;
    S.running = true; el.run.disabled = true; el.check.disabled = true;
    clearOut();
    const t0 = performance.now();
    try {
      const py = await prepareLesson(S.lesson);
      const ns = py.globals.get("dict")();
      try {
        await execute(editor.getValue(), { globals: ns });
      } catch (e) {
        out("stderr", cleanTraceback(e.message) + "\n");
      } finally { ns.destroy(); }
      el.runTime.textContent = ((performance.now() - t0) / 1000).toFixed(2) + " s";
    } catch (e) {
      out("stderr", "Runtime error: " + e.message + "\n");
    } finally { S.running = false; el.run.disabled = false; el.check.disabled = false; }
  }

  async function checkExercise() {
    if (S.running || !S.current || S.current.kind !== "exercise") return;
    const ex = S.exercises[S.current.id];
    S.running = true; el.run.disabled = true; el.check.disabled = true;
    clearOut();
    try {
      const py = await prepareLesson(S.lesson);
      const ns = py.globals.get("dict")();
      let passed = false, msg = "";
      try {
        await execute(editor.getValue(), { globals: ns, echoResult: false });
        await execute(ex.check, { globals: ns, echoResult: false });
        passed = true;
      } catch (e) {
        msg = cleanTraceback(e.message);
      } finally { ns.destroy(); }
      if (passed) {
        out("ok", "✓ Correct — exercise " + ex.id + " passed.\n");
        markDone(S.lesson.id, ex.id);
      } else {
        out("fail", "✗ Not yet.\n");
        out("stderr", msg + "\n");
      }
    } catch (e) {
      out("stderr", "Runtime error: " + e.message + "\n");
    } finally { S.running = false; el.run.disabled = false; el.check.disabled = false; }
  }

  // ---------------------------------------------------------------- progress
  const doneKey = (l, x) => `pds:done:${l}:${x}`;
  const isDone = (l, x) => { try { return localStorage.getItem(doneKey(l, x)) === "1"; } catch { return false; } };
  function markDone(l, x) {
    try { localStorage.setItem(doneKey(l, x), "1"); } catch { /* private mode */ }
    const ex = S.exercises[x];
    if (ex && ex.el) { ex.el.classList.add("done"); ex.el.querySelector(".tick").textContent = "✓ done"; }
  }
  function lessonProgress(lesson) {
    const ids = lesson.exercises || [];
    const n = ids.filter((x) => isDone(lesson.id, x)).length;
    return { n, total: ids.length };
  }

  // ---------------------------------------------------------------- markdown → lesson DOM
  const escapeAttr = (s) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");

  function parseLesson(md) {
    // 1. pull out :::exercise blocks
    const exercises = [];
    md = md.replace(/^:::exercise\s+([^\n]*)\n([\s\S]*?)^:::\s*$/gm, (_, header, body) => {
      const id = (header.match(/id=([\w-]+)/) || [])[1] || `ex${exercises.length + 1}`;
      const title = (header.match(/title="([^"]*)"/) || [])[1] || "Exercise";
      const fence = /```python\s*(check)?\s*\n([\s\S]*?)```/g;
      let starter = "", check = "", m;
      let desc = body;
      while ((m = fence.exec(body))) {
        if (m[1]) check = m[2]; else starter = m[2];
      }
      desc = desc.replace(fence, "").trim();
      exercises.push({ id, title, starter: starter.trimEnd(), check: check.trimEnd(), descMd: desc });
      return `\n<div data-exercise="${id}"></div>\n`;
    });

    // 2. render markdown with runnable code blocks
    const renderer = new marked.Renderer();
    const baseCode = renderer.code.bind(renderer);
    renderer.code = function (codeObj, infoString) {
      const text = typeof codeObj === "object" ? codeObj.text : codeObj;
      const info = typeof codeObj === "object" ? (codeObj.lang || "") : (infoString || "");
      const lang = info.split(/\s+/)[0] || "";
      const runnable = /\brun\b/.test(info);
      const hl = lang && hljs.getLanguage(lang) ? hljs.highlight(text, { language: lang }).value : escapeAttr(text);
      const pre = `<pre><code class="hljs language-${lang}">${hl}</code></pre>`;
      return runnable ? `<div class="runnable"><button class="try" data-code="${escapeAttr(text)}">▶ Try it</button>${pre}</div>` : pre;
    };
    const html = marked.parse(md, { renderer, gfm: true, breaks: false });
    return { html, exercises };
  }

  function buildExerciseCard(ex, lessonId) {
    const wrap = document.createElement("div");
    wrap.className = "exercise" + (isDone(lessonId, ex.id) ? " done" : "");
    wrap.id = "ex-" + ex.id;
    wrap.innerHTML = `
      <div class="exercise-head">
        <span class="exercise-badge">${ex.id}</span>
        <span class="exercise-title">${ex.title}</span>
        <span class="tick">${isDone(lessonId, ex.id) ? "✓ done" : ""}</span>
      </div>
      <div class="exercise-body">
        ${marked.parse(ex.descMd)}
        <button class="btn primary open">Open in editor</button>
        <details><summary>Show starter code</summary><pre><code class="hljs language-python">${hljs.highlight(ex.starter, { language: "python" }).value}</code></pre></details>
      </div>`;
    wrap.querySelector(".open").addEventListener("click", () => loadIntoEditor({ kind: "exercise", id: ex.id, code: ex.starter }));
    ex.el = wrap;
    return wrap;
  }

  function loadIntoEditor(item) {
    S.current = item;
    editor.setValue(item.code);
    editor.focus();
    clearOut();
    if (item.kind === "exercise") {
      const ex = S.exercises[item.id];
      el.wbTitle.textContent = `Exercise ${ex.id} · ${ex.title}`;
      el.check.classList.remove("hidden");
    } else {
      el.wbTitle.textContent = "Example";
      el.check.classList.add("hidden");
    }
  }

  // ---------------------------------------------------------------- routing / views
  async function showHome() {
    el.lesson.classList.add("hidden");
    el.home.classList.remove("hidden");
    el.list.innerHTML = "";
    S.manifest.forEach((l, i) => {
      const { n, total } = lessonProgress(l);
      const li = document.createElement("li");
      li.innerHTML = `<a class="lesson-card" href="#/lesson/${l.id}">
        <span class="lesson-num">${String(i + 1).padStart(2, "0")}</span>
        <span><h3>${l.title}</h3><p>${l.blurb}</p></span>
        <span class="lesson-meta">${l.week}<br><span class="progress-pill ${n === total && total ? "done" : ""}">${n}/${total} exercises</span></span>
      </a>`;
      el.list.appendChild(li);
    });
    document.title = "Programming for Data Science · Interactive Tutorial";
    el.select.value = "";
  }

  async function showLesson(id, anchor) {
    const lesson = S.manifest.find((l) => l.id === id);
    if (!lesson) { location.hash = "#/"; return; }
    S.lesson = lesson; S.exercises = {}; S.current = null;
    el.home.classList.add("hidden");
    el.lesson.classList.remove("hidden");
    el.select.value = id;
    document.title = lesson.title + " · PDS Tutorial";

    el.content.innerHTML = `<p class="muted">Loading lesson…</p>`;
    const md = await (await fetch("lessons/" + lesson.file)).text();
    const { html, exercises } = parseLesson(md);
    el.content.innerHTML = html;
    exercises.forEach((ex) => {
      S.exercises[ex.id] = ex;
      const ph = el.content.querySelector(`[data-exercise="${ex.id}"]`);
      if (ph) ph.replaceWith(buildExerciseCard(ex, lesson.id));
    });

    // prev / next footer
    const i = S.manifest.indexOf(lesson);
    const nav = document.createElement("div");
    nav.className = "lesson-nav";
    nav.innerHTML = `${i > 0 ? `<a href="#/lesson/${S.manifest[i - 1].id}">‹ ${S.manifest[i - 1].title}</a>` : "<span></span>"}
                     ${i < S.manifest.length - 1 ? `<a href="#/lesson/${S.manifest[i + 1].id}">${S.manifest[i + 1].title} ›</a>` : "<a href='#/'>Back to lessons</a>"}`;
    el.content.appendChild(nav);

    // wire "Try it" buttons
    el.content.querySelectorAll(".runnable .try").forEach((b) => {
      b.addEventListener("click", () => { loadIntoEditor({ kind: "example", code: b.dataset.code }); runEditor(); });
    });

    // put the first example in the editor
    const first = el.content.querySelector(".runnable .try");
    if (first) loadIntoEditor({ kind: "example", code: first.dataset.code });
    else editor.setValue("# Write Python here and press Ctrl+Enter\n");

    el.content.scrollTop = 0;
    if (anchor) { const t = el.content.querySelector("#ex-" + anchor); if (t) t.scrollIntoView({ behavior: "smooth", block: "start" }); }

    el.prev.disabled = i === 0; el.next.disabled = i === S.manifest.length - 1;
    prepareLesson(lesson).catch(() => {});   // warm up in the background
  }

  function route() {
    const h = location.hash || "#/";
    const m = h.match(/^#\/lesson\/([\w-]+)(?:\/([\w-]+))?/);
    if (m) showLesson(m[1], m[2]); else showHome();
  }

  // ---------------------------------------------------------------- wiring
  el.run.addEventListener("click", runEditor);
  el.check.addEventListener("click", checkExercise);
  el.clear.addEventListener("click", clearOut);
  el.reset.addEventListener("click", () => { if (S.current) { editor.setValue(S.current.code); clearOut(); } });
  el.select.addEventListener("change", () => { if (el.select.value) location.hash = "#/lesson/" + el.select.value; });
  el.prev.addEventListener("click", () => { const i = S.manifest.indexOf(S.lesson); if (i > 0) location.hash = "#/lesson/" + S.manifest[i - 1].id; });
  el.next.addEventListener("click", () => { const i = S.manifest.indexOf(S.lesson); if (i < S.manifest.length - 1) location.hash = "#/lesson/" + S.manifest[i + 1].id; });
  window.addEventListener("hashchange", route);

  // draggable splitter
  (() => {
    let dragging = false;
    el.splitter.addEventListener("mousedown", (e) => { dragging = true; e.preventDefault(); document.body.style.cursor = "col-resize"; });
    window.addEventListener("mouseup", () => { dragging = false; document.body.style.cursor = ""; });
    window.addEventListener("mousemove", (e) => {
      if (!dragging) return;
      const pct = Math.min(75, Math.max(25, (e.clientX / window.innerWidth) * 100));
      el.lesson.style.setProperty("--left", pct + "%");
      editor.refresh();
    });
  })();

  // ---------------------------------------------------------------- boot
  (async () => {
    S.manifest = await (await fetch("lessons/manifest.json")).json();
    el.select.innerHTML = `<option value="">Lessons…</option>` + S.manifest.map((l) => `<option value="${l.id}">${l.week} · ${l.title}</option>`).join("");
    route();
    ensurePython().catch(() => {});
  })();
})();

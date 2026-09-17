#!/usr/bin/env node
/** Tests: hint gone, Wails graph (ply 0 / lead / fight), silent occupied, dblclick-to-main. */
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const route26 = join(root, "assets/routes-aura26.js");
const route27 = join(root, "assets/routes-aura27.js");
const src = readFileSync(existsSync(route27) ? route27 : route26, "utf8");
const html = existsSync(join(root, "index.html"))
  ? readFileSync(join(root, "index.html"), "utf8")
  : "";

let failed = 0;
function check(name, cond) {
  if (cond) console.log("PASS", name);
  else {
    console.error("FAIL", name);
    failed++;
  }
}

check("hint gone from js", !src.includes("點擊表格切換精簡") && !src.includes("vs-hint"));
check("評級需滿 gone", !src.includes("評級需滿 20 手"));
check("goMain ASI safe", !src.includes("goMain()else") && src.includes("if(n<0){goMain()}"));
check("module parses", (() => {
  try {
    const stripped = src
      .replace(/^import[^;]+;/, "")
      .replace(/export\{[^}]+\};?\s*$/, "");
    new Function(stripped);
    return true;
  } catch (e) {
    console.error("PARSE", e.message);
    return false;
  }
})());
check("pointerup occupied lastOcc", src.includes("l.current[a.y][a.x]") && src.includes("L.x===a.x&&L.y===a.y)goMain()"));
check("S preserves lastOcc", src.includes("let L=v.current.lastOcc"));
check("occupied no toast", src.includes("e.reason!==`已有子`"));
check("occupied skip place", src.includes("e.board[i][r]||t(r,i)") || src.includes("e.board[a.y][a.x]"));
check("illegal reasons kept", src.includes("reason:`越界`") && src.includes("reason:`已有子`"));
check("wails graph helpers", src.includes("function fightIndex(") && src.includes("function wrSeries(") && src.includes("function drawWrGraph("));
check("canvas graph wired", src.includes("wr-graph-wrap") && src.includes("className:`wr-graph`"));
check("old svg chart gone", !src.includes("chart-box") && !src.includes("a.length<2"));
check("engine-stats gone", !src.includes("className:`engine-stats`"));
check("ply0 uses root node", src.includes("t<=0?e:a[t-1]"));
check("entropy stamped", src.includes("entropy:fightIndex(n)"));
check("blue fight fill", src.includes("rgba(0,0,255,.5)"));
check("lead curve drawn", src.includes("n[e]>-900&&n[e+1]>-900"));
if (existsSync(route27)) {
  const r27 = readFileSync(route27, "utf8");
  check("routes27 imports index27", r27.includes('from"./index-aura27.js"') && !r27.includes('from"./index-aura26.js"'));
}
if (html) {
  check("html cache-bust aura27", html.includes("routes-aura27.js") && html.includes("index-aura27.js"));
  check("html no stale aura26 routes", !html.includes("routes-aura26.js"));
}

function extract(fnName) {
  const start = src.indexOf(`function ${fnName}(`);
  if (start < 0) throw new Error("missing " + fnName);
  let i = src.indexOf("{", start);
  let depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  throw new Error("unclosed " + fnName);
}

const goMainSrc = extract("goMain");

function node(parent = null) {
  const n = { parent, children: [] };
  if (parent) parent.children.push(n);
  return n;
}

function runGoMain(cursor, rootNode) {
  const toasts = [];
  const jumps = [];
  const q = {
    getState() {
      return {
        root: rootNode,
        cursor,
        setToast: (t) => toasts.push(t),
        jumpTo: (n) => jumps.push(n),
      };
    },
  };
  const fn = new Function("q", goMainSrc + "\ngoMain();");
  fn(q);
  return { toasts, jumps };
}

const rootN = node();
const m1 = node(rootN);
const m2 = node(m1);
const m3 = node(m2);
const v1 = node(m1);
const v2 = node(v1);

{
  const r = runGoMain(m3, rootN);
  check("main-line toast", r.toasts.join() === "已在主線" && r.jumps.length === 0);
}
{
  const r = runGoMain(v2, rootN);
  check("variation jumps to fork", r.toasts.join() === "已回主線" && r.jumps[0] === m1);
}
{
  const r = runGoMain(v1, rootN);
  check("side child jumps to parent on main", r.jumps[0] === m1);
}

function simClick(board, x, y, lastOcc, now) {
  const occupied = !!board[y][x];
  const toasts = [];
  const placed = [];
  let go = false;
  if (occupied) {
    const L = lastOcc;
    const next = { t: now, x, y };
    if (L && now - L.t < 480 && L.x === x && L.y === y) go = true;
    return { go, lastOcc: next, toasts, placed };
  }
  placed.push([x, y]);
  return { go, lastOcc, toasts, placed };
}

{
  const board = Array.from({ length: 19 }, () => Array(19).fill(0));
  board[3][3] = 1;
  const a = simClick(board, 3, 3, null, 1000);
  check("single occupied click silent", a.go === false && a.placed.length === 0 && a.toasts.length === 0);
  const b = simClick(board, 3, 3, a.lastOcc, 1200);
  check("double occupied click goMain", b.go === true && b.placed.length === 0);
  const c = simClick(board, 3, 3, a.lastOcc, 2000);
  check("slow second click is not dbl", c.go === false);
  const d = simClick(board, 4, 4, null, 3000);
  check("empty click places", d.placed[0][0] === 4 && d.placed[0][1] === 4);
}

const ctx = {
  Nt(c) {
    return c._path || [];
  },
  Se(w, tm) {
    return tm === "W" ? 1 - w : w;
  },
  Ce(s, tm) {
    return tm === "W" ? -s : s;
  },
  LeadMap: {},
  Math,
  Number,
};
vm.runInNewContext(
  extract("fightIndex") + "\n" + extract("wrSeries") + "\nthis.fightIndex=fightIndex;this.wrSeries=wrSeries;",
  ctx,
);

{
  const fi = ctx.fightIndex;
  check("fight null", fi(null) === -1);
  check("fight entropy already 0-100", fi({ entropy: 55 }) === 55);
  check("fight entropy small *25", fi({ entropy: 2 }) === 50);
  check("fight scoreStdev *5", fi({ scoreStdev: 8 }) === 40);
  const p = fi({ candidates: [{ prior: 0.5 }, { prior: 0.5 }] });
  check("fight priors in 0-100", p >= 0 && p <= 100);
}

{
  const live = {
    winrate: 0.47,
    toMove: "B",
    scoreLead: -3.2,
    _view: 0,
    candidates: [{ prior: 0.4 }, { prior: 0.3 }, { prior: 0.2 }, { prior: 0.1 }],
  };
  const r = ctx.wrSeries({ blackWRAfter: 0.5 }, { _path: [] }, [], live, 0);
  check("ply0 total is 0", r.total === 0);
  check("ply0 wr from live", Math.abs(r.wr[0] - 0.47) < 1e-9);
  check("ply0 lead from live", Math.abs(r.ld[0] + 3.2) < 1e-9);
  check("ply0 fight from live", r.en[0] >= 0);
}

{
  const path = [
    { blackWRAfter: 0.55, scoreLead: 2, entropy: 30 },
    { blackWRAfter: 0.48, scoreLead: -1, entropy: 70 },
    { blackWRAfter: 0.51, scoreLead: 0.5, entropy: 20 },
  ];
  const hist = [
    { blackWinrate: 0.5, scoreLead: 0.2, entropy: 12 },
    { blackWinrate: 0.55, scoreLead: 2, entropy: 30 },
    { blackWinrate: 0.48, scoreLead: -1, entropy: 70 },
    { blackWinrate: 0.51, scoreLead: 0.5, entropy: 20 },
  ];
  const r = ctx.wrSeries({}, { _path: path }, hist, null, 3);
  check("series total 3", r.total === 3);
  check("series wr0 hist", r.wr[0] === 0.5);
  check("series wr3 hist", r.wr[3] === 0.51);
  check("lead curve consecutive", r.ld.every((v) => v > -900));
  check("fight dots all plies", r.en.every((v) => v >= 0));
}

{
  const r = ctx.wrSeries(
    { blackWRAfter: 0.61, scoreLead: 4.4, entropy: 18 },
    { _path: [] },
    [],
    null,
    0,
  );
  check("ply0 from root stamp without live", r.wr[0] === 0.61 && r.ld[0] === 4.4 && r.en[0] === 18);
}

if (failed) {
  console.error(failed, "failed");
  process.exit(1);
}
console.log("all tests passed");

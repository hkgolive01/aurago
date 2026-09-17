#!/usr/bin/env node
/** Unit tests for goMain + occupied-click silence. */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = readFileSync(join(root, "assets/routes-aura26.js"), "utf8");

let failed = 0;
function check(name, cond) {
  if (cond) console.log("PASS", name);
  else {
    console.error("FAIL", name);
    failed++;
  }
}

check("hint gone", !src.includes("點擊表格切換精簡") && !src.includes("vs-hint"));
check("goMain present", src.includes("function goMain()"));
check("KeyV uses goMain", src.includes("n=goMain"));
check("swipe uses goMain", src.includes("if(n<0)goMain()"));
check("double-click wired", src.includes("onDoubleClick:D") && src.includes("function D(ev)"));
check("dblclick only on stone", src.includes("if(!a||!e.board[a.y][a.x])return;goMain()"));
check("occupied no toast", src.includes("e.reason!==`已有子`"));
check("occupied skip place", src.includes("e.board[i][r]||t(r,i)"));
check("ko still toasts", src.includes("reason:`劫爭未消解`"));

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
  check("variation jumps to fork", r.jumps[0] === m1 && r.toasts.join() === "已回主線");
}
{
  const r = runGoMain(v1, rootN);
  check("variation child jumps to fork", r.jumps[0] === m1 && r.toasts.join() === "已回主線");
}
{
  const r = runGoMain(rootN, rootN);
  check("root is main", r.toasts.join() === "已在主線" && r.jumps.length === 0);
}

function addMoveToast(reason) {
  const toasts = [];
  const t = () => ({ setToast: (x) => toasts.push(x) });
  const e = { ok: false, reason };
  const body = "if(!e.ok)return e.reason!==`已有子`&&t().setToast(e.reason),null";
  const fn = new Function("e", "t", body);
  const ret = fn(e, t);
  return { toasts, ret };
}
{
  const r = addMoveToast("已有子");
  check("已有子 silent", r.toasts.length === 0 && r.ret === null);
}
{
  const r = addMoveToast("劫爭未消解");
  check("ko still toasts", r.toasts.join() === "劫爭未消解" && r.ret === null);
}
{
  const r = addMoveToast("越界");
  check("越界 still toasts", r.toasts.join() === "越界");
}

function clickOccupied(board, x, y, nexts) {
  const placed = [];
  const jumped = [];
  const e = { board, nexts };
  const n = (node) => jumped.push(node);
  const t = (x, y) => placed.push([x, y]);
  const b = new Function(
    "e",
    "n",
    "t",
    "r",
    "i",
    "let a=e.nexts.find(e=>!e.pass&&e.x===r&&e.y===i);a?n(a):e.board[i][r]||t(r,i)",
  );
  b(e, n, t, x, y);
  return { placed, jumped };
}
{
  const board = Array.from({ length: 19 }, () => Array(19).fill(0));
  board[3][3] = 1;
  const r = clickOccupied(board, 3, 3, []);
  check("click stone does not place", r.placed.length === 0 && r.jumped.length === 0);
}
{
  const board = Array.from({ length: 19 }, () => Array(19).fill(0));
  const r = clickOccupied(board, 3, 3, []);
  check("click empty places", r.placed.length === 1 && r.placed[0][0] === 3 && r.placed[0][1] === 3);
}
{
  const board = Array.from({ length: 19 }, () => Array(19).fill(0));
  const nxt = { pass: false, x: 4, y: 4 };
  const r = clickOccupied(board, 4, 4, [nxt]);
  check("click next-move jumps", r.jumped[0] === nxt && r.placed.length === 0);
}

if (failed) {
  console.error(failed, "failed");
  process.exit(1);
}
console.log("all board-click tests passed");

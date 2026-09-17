#!/usr/bin/env python3
"""Patch AuraGo routes + CSS: Wails wr graph (ply0/lead/fight), silent occupied, dblclick-to-main, cache-bust."""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "assets" / "routes-aura26.js"
CSS = ROOT / "assets" / "styles-aura26.css"
HTML = ROOT / "index.html"
IDX = ROOT / "assets" / "index-aura26.js"
VER = "aura28"


def _js(name: str) -> str:
    return (Path(__file__).resolve().parent / name).read_text(encoding="utf-8").strip() + "\n"


GRAPH_FNS = _js("wr-graph-fns.js")
NEW_PT = _js("wr-graph-pt.js")
NEW_LIVE = _js("wr-graph-live.js")

CSS_BLOCK = """
/* wr-graph-wails */
.wr-live{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;margin:0 0 8px;font-variant-numeric:tabular-nums}
.wr-live .k{letter-spacing:.12em;color:var(--gold);font-size:10px;margin-right:5px}
.wr-live .v{font-family:var(--font-serif);font-size:15px;font-weight:600}
.wr-graph-wrap{border:1px solid var(--line);background:#fff;border-radius:12px;height:152px;margin:0 0 10px;overflow:hidden}
.wr-graph{width:100%;height:152px;display:block;cursor:pointer;touch-action:none;background:#fff}
html.desk .wr-graph-wrap,html.desk .wr-graph{height:168px}
.wr-key{letter-spacing:.12em;color:var(--muted);text-align:center;margin:-4px 0 10px;font-size:10px}
.chart-box{display:none!important;height:0!important;margin:0!important}
.hint.vs-hint,.vs-hint{display:none!important;height:0!important;margin:0!important;overflow:hidden!important;font-size:0!important}
.engine-stats{display:none!important}
"""

REPLACEMENTS = [
    (
        "if(n<0)goMain()else if(!e.engine.ready)",
        "if(n<0){goMain()}else if(!e.engine.ready)",
    ),
    (
        "function S(e){v.current={x:e.clientX,y:e.clientY,swiping:!1,pid:e.pointerId};try{e.currentTarget.setPointerCapture(e.pointerId)}catch{}}",
        "function S(e){let L=v.current.lastOcc;v.current={x:e.clientX,y:e.clientY,swiping:!1,pid:e.pointerId,lastOcc:L};try{e.currentTarget.setPointerCapture(e.pointerId)}catch{}}",
    ),
    (
        "if(t.swiping)return;let a=y(e);a&&b(a.x,a.y)}function D(ev){ev.preventDefault();let a=y(ev);if(!a||!e.board[a.y][a.x])return;goMain()}",
        "if(t.swiping)return;let a=y(e);if(!a)return;if(l.current[a.y][a.x]){let now=Date.now(),L=v.current.lastOcc;v.current.lastOcc={t:now,x:a.x,y:a.y};if(L&&now-L.t<480&&L.x===a.x&&L.y===a.y)goMain();return}b(a.x,a.y)}function D(ev){ev.preventDefault();let a=y(ev);if(!a||!e.board[a.y][a.x])return;goMain()}",
    ),
    (
        "if(t.swiping)return;let a=y(e);a&&b(a.x,a.y)}",
        "if(t.swiping)return;let a=y(e);if(!a)return;if(l.current[a.y][a.x]){let now=Date.now(),L=v.current.lastOcc;v.current.lastOcc={t:now,x:a.x,y:a.y};if(L&&now-L.t<480&&L.x===a.x&&L.y===a.y)goMain();return}b(a.x,a.y)}",
    ),
    (
        "a?n(a):t(r,i)}function x()",
        "a?n(a):e.board[i][r]||t(r,i)}function x()",
    ),
    (
        "if(!e.ok)return t().setToast(e.reason),null}",
        "if(!e.ok)return e.reason!==`已有子`&&t().setToast(e.reason),null}",
    ),
    (
        "(0,Y.jsx)(`p`,{className:`hint vs-hint`,children:m.black.moves+m.white.moves?`點擊表格切換精簡／加權　評級需滿 20 手有效手`:`匯入棋譜請到選單按「全譜掃描」，才有評級與每手勝率／目差`}),",
        "",
    ),
    (
        "(0,Y.jsx)(`p`,{className:`hint vs-hint`,children:`點擊表格切換精簡／加權　評級需滿 20 手有效手`}),",
        "",
    ),
    (
        "d[a]=u||!l?{ply:a,blackWinrate:o,scoreLead:s,visits:n.visits}:{...l,blackWinrate:o,scoreLead:s,visits:n.visits}",
        "d[a]=u||!l?{ply:a,blackWinrate:o,scoreLead:s,visits:n.visits,entropy:fightIndex(n)}:{...l,blackWinrate:o,scoreLead:s,visits:n.visits,entropy:fightIndex(n)}",
    ),
    (
        "c&&(c.blackWRAfter=o,c.scoreLead=s,c.evalVisits=n.visits,c.scoreMean=s),rememberLead(a,s)",
        "c&&(c.blackWRAfter=o,c.scoreLead=s,c.evalVisits=n.visits,c.scoreMean=s,c.entropy=fightIndex(n)),rememberLead(a,s)",
    ),
]


def replace_once(s, old, new, label):
    n = s.count(old)
    if n == 0:
        if new in s:
            print("skip (already):", label)
            return s, 0
        print("skip (missing):", label)
        return s, 0
    if n != 1:
        if new in s:
            print("skip (already, non-unique old):", label)
            return s, 0
        print("not unique", n, label, file=sys.stderr)
        raise SystemExit(1)
    print("apply:", label)
    return s.replace(old, new, 1), 1


def insert_or_replace_graph_helpers(s: str) -> str:
    pt = s.find("function Pt()")
    if pt < 0:
        raise SystemExit("Pt() not found")
    start = s.find("function fightIndex(")
    if start >= 0 and start < pt:
        s = s[:start] + GRAPH_FNS + s[pt:]
        print("replace graph helpers")
    else:
        s = s[:pt] + GRAPH_FNS + s[pt:]
        print("insert graph helpers")
    return s


def replace_pt(s: str) -> str:
    start = s.find("function Pt()")
    end = s.find("var Ft=", start)
    if start < 0 or end < 0:
        raise SystemExit("cannot locate Pt() body")
    s = s[:start] + NEW_PT + s[end:]
    print("replace Pt() with canvas graph")
    return s


def replace_engine_stats(s: str) -> str:
    i = s.find("(0,Y.jsxs)(`div`,{className:`engine-stats`")
    if i >= 0:
        term = "),(0,Y.jsx)(Pt,{}),(0,Y.jsx)(It,{})]})}function Rt"
        j = s.find(term, i)
        if j < 0:
            raise SystemExit("engine-stats terminator not found")
        s = s[:i] + NEW_LIVE + "]})}function Rt" + s[j + len(term) :]
        print("replace engine-stats with wr-live + graph")
        return s
    if "wr-live" in s:
        old = "),(0,Y.jsx)(Pt,{}),(0,Y.jsx)(It,{})"
        new = "),(0,Y.jsx)(Pt,{}),(0,Y.jsx)(`p`,{className:`wr-key`,children:`粗線勝率　細線目差　藍點對抗`}),(0,Y.jsx)(It,{})"
        if "wr-key" not in s and old in s:
            s = s.replace(old, new, 1)
            print("insert wr-key")
        else:
            print("engine-stats already replaced")
        return s
    raise SystemExit("engine-stats block not found")


def patch_js(s: str) -> str:
    applied = 0
    for old, new in REPLACEMENTS:
        s, n = replace_once(s, old, new, old[:56])
        applied += n
    s = insert_or_replace_graph_helpers(s)
    s = replace_pt(s)
    s = replace_engine_stats(s)
    print("js replacements applied this run:", applied)
    return s


def patch_css(s: str) -> str:
    if "wr-graph-wails" in s:
        # refresh block
        idx = s.find("/* wr-graph-wails */")
        if idx >= 0:
            return s[:idx].rstrip() + "\n" + CSS_BLOCK
        return s
    return s.rstrip() + "\n" + CSS_BLOCK


def cache_bust(js: str, css: str):
    dest = ROOT / "assets" / f"routes-{VER}.js"
    js_ver = js.replace('from"./index-aura26.js"', f'from"./index-{VER}.js"')
    for old in range(20, 28):
        js_ver = js_ver.replace(f'from"./index-aura{old}.js"', f'from"./index-{VER}.js"')
    dest.write_text(js_ver, encoding="utf-8")
    print("wrote", dest, "bytes", len(js_ver.encode()))

    if IDX.exists():
        ix = IDX.read_text(encoding="utf-8")
        ix2 = ix
        for old in range(20, 28):
            ix2 = ix2.replace(f"routes-aura{old}.js", f"routes-{VER}.js")
        out = ROOT / "assets" / f"index-{VER}.js"
        out.write_text(ix2, encoding="utf-8")
        print("wrote", out)

    css_out = ROOT / "assets" / f"styles-{VER}.css"
    css_out.write_text(css, encoding="utf-8")
    print("wrote", css_out)

    if HTML.exists():
        h = HTML.read_text(encoding="utf-8")
        h2 = h
        for old in range(20, 28):
            h2 = (
                h2.replace(f"index-aura{old}.js", f"index-{VER}.js")
                .replace(f"routes-aura{old}.js", f"routes-{VER}.js")
                .replace(f"styles-aura{old}.css", f"styles-{VER}.css")
            )
        if f"index-{VER}.js" not in h2 or f"styles-{VER}.css" not in h2:
            raise SystemExit("failed to retarget index.html")
        HTML.write_text(h2, encoding="utf-8")
        print("patched index.html ->", VER)


def verify(s: str):
    need = [
        "function fightIndex(",
        "function wrSeries(",
        "function drawWrGraph(",
        "wr-graph-wrap",
        "lastOcc",
        "e.reason!==`已有子`",
        "entropy:fightIndex(n)",
        "function goMain()",
        "t<=0?e:a[t-1]",
        "if(n<0){goMain()}",
        "l.current[a.y][a.x]",
        "rgba(0,0,255,.5)",
        "yLd",
        "ldPts",
        "wr-key",
    ]
    forbid = [
        "點擊表格切換精簡",
        "className:`hint vs-hint`",
        "className:`engine-stats`",
        "a.length<2",
        "goMain()else",
    ]
    for x in need:
        if x not in s:
            raise SystemExit("verify fail need " + x)
    for x in forbid:
        if x in s:
            raise SystemExit("verify fail still has " + x)


def main():
    if not JS.exists():
        raise SystemExit(f"missing {JS}")
    js = JS.read_text(encoding="utf-8")
    new_js = patch_js(js)
    verify(new_js)
    if new_js != js:
        JS.write_text(new_js, encoding="utf-8")
        print(f"patched {JS} {len(js)} -> {len(new_js)}")
    else:
        print(f"no net js text change {JS} (already patched)")

    css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
    new_css = patch_css(css)
    if CSS.exists() and new_css != css:
        CSS.write_text(new_css, encoding="utf-8")
        print(f"patched {CSS}")

    cache_bust(new_js, new_css)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Patch AuraGo: drop wr-key legend, Wails fight-index wr/lead damp, cache-bust."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "assets" / "routes-aura26.js"
CSS = ROOT / "assets" / "styles-aura26.css"
HTML = ROOT / "index.html"
IDX = ROOT / "assets" / "index-aura26.js"
VER = "aura31"


def _js(name: str) -> str:
    return (Path(__file__).resolve().parent / name).read_text(encoding="utf-8").strip() + "\n"


GRAPH_FNS = _js("wr-graph-fns.js")
NEW_PT = _js("wr-graph-pt.js")
NEW_LIVE = _js("wr-graph-live.js")

CSS_BLOCK = """
/* wr-graph-wails */
.wr-live{display:none!important;height:0!important;margin:0!important;overflow:hidden!important}
.wr-graph-wrap{border:1px solid var(--line);background:#fff;border-radius:12px;height:152px;margin:0 0 10px;overflow:hidden}
.wr-graph{width:100%;height:152px;display:block;cursor:pointer;touch-action:none;background:#fff}
html.desk .wr-graph-wrap,html.desk .wr-graph{height:168px}
.chart-box{display:none!important;height:0!important;margin:0!important}
.hint.vs-hint,.vs-hint{display:none!important;height:0!important;margin:0!important;overflow:hidden!important;font-size:0!important}
.engine-stats{display:none!important}
.wr-key{display:none!important;height:0!important;margin:0!important;overflow:hidden!important;font-size:0!important}
"""

YT_OLD = (
    "function yt(e,t){let n=[];for(let r=0;r<19;r++)for(let i=0;i<19;i++){"
    "let a=e[r*19+i],o=t[r][i],s=Math.abs(a),c=Math.min(1,s*.78+.22),l=s>.95,"
    "u=a>=0?o===1||a>=.5?`rgba(0, 255, 0, ${c})`:null:o===2||a<=-.5?`rgba(255, 0, 0, ${c})`:null;"
    "u&&n.push({x:i,y:r,star:l,text:String(Math.round(s*10)),color:u})}return n}"
)
YT_NEW = (
    "function yt(e,t){let n=[];for(let r=0;r<19;r++)for(let i=0;i<19;i++){"
    "let a=e[r*19+i],o=t[r][i],s=Math.abs(a),c=Math.min(1,s*.78+.22),l=s>.95,u;"
    "a>=0?u=o===1?`rgba(0, 255, 0, ${c})`:a>=.5?`rgba(15, 10, 5, ${c})`:null:"
    "u=o===2?`rgba(255, 0, 0, ${c})`:a<=-.5?`rgba(255, 255, 255, ${c})`:null;"
    "u&&n.push({x:i,y:r,star:l,text:String(Math.round(s*10)),color:u})}return n}"
)

WT_OLD = (
    "function wt(e,t,n,r){e.beginPath();for(let i=0;i<5;i++){"
    "let a=-Math.PI/2+i*2*Math.PI/5,o=a+Math.PI/5,s=t+Math.cos(a)*r,c=n+Math.sin(a)*r,"
    "l=t+Math.cos(o)*r*.38,u=n+Math.sin(o)*r*.38;i===0?e.moveTo(s,c):e.lineTo(s,c),e.lineTo(l,u)}"
    "e.closePath(),e.fill()}"
)
WT_NEW = (
    "function wt(e,t,n,r){e.beginPath();for(let i=0;i<3;i++){"
    "let a=Math.PI/3*i;e.moveTo(t-r*Math.cos(a),n-r*Math.sin(a)),e.lineTo(t+r*Math.cos(a),n+r*Math.sin(a))}"
    "e.stroke()}"
)

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
    (YT_OLD, YT_NEW),
    (WT_OLD, WT_NEW),
    (
        "e.star?(a.fillStyle=e.color,wt(a,t,n,s*.2))",
        "e.star?(a.strokeStyle=e.color,a.lineWidth=Math.max(1.5,s*.09),wt(a,t,n,s*.168))",
    ),
    (
        "let t=c(e.x),n=c(e.y),r=e.count>=10?s*.86:s*(.56+e.count*.026);a.font=`bold ${Math.max(9,Math.floor(r))}px \"Noto Sans TC\", \"PingFang TC\", sans-serif`;let i=a.measureText(String(e.count)).width,h=r,p=s*.24",
        "let t=c(e.x),n=c(e.y),sc=e.count>=10?1:.5+(e.count-1)*.05,r=s*.94*sc;a.font=`bold ${Math.max(9,Math.floor(r))}px \"Noto Sans TC\", \"PingFang TC\", sans-serif`;let i=a.measureText(String(e.count)).width,h=r,p=s*.24*sc",
    ),
    (
        "let e=At(),t=q(e=>e.showSubBoard),n=q(e=>e.setShowSubBoard),r=q(e=>e.showOwnership),i=q(e=>e.analysis),a=(0,u.useRef)(null)",
        "let e=At(),t=q(e=>e.showSubBoard),n=q(e=>e.setShowSubBoard),r=q(e=>e.showOwnership),i=q(e=>e.analysis),sg=q(e=>e.showSuggestions),a=(0,u.useRef)(null)",
    ),
    (
        "g.current=r,Et(e,o.current,n,c.current,l)}",
        "g.current=r;let hasC=sg!==!1&&t&&t.candidates&&t.candidates.length;Et(e,o.current,n,c.current,hasC?!1:l);if(hasC){let k=ht(e);k&&gt(k.ctx,t.candidates,t.toMove||`B`,o.current,k.css,c.current)}}",
    ),
    (
        "(0,u.useLayoutEffect)(()=>{f()},[e.board,r,t,e.coordsOn,i])",
        "(0,u.useLayoutEffect)(()=>{f()},[e.board,r,t,e.coordsOn,i,sg])",
    ),
    (
        "(0,Y.jsx)(Pt,{}),(0,Y.jsx)(`p`,{className:`wr-key`,children:`粗線勝率　細線目差　藍點對抗`}),(0,Y.jsx)(It,{})",
        "(0,Y.jsx)(Pt,{}),(0,Y.jsx)(It,{})",
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
        print("replace engine-stats with graph")
        return s
    live = "(0,Y.jsxs)(`div`,{className:`wr-live`"
    i = s.find(live)
    if i >= 0:
        j = s.find("),(0,Y.jsx)(Pt,{})", i)
        if j < 0:
            raise SystemExit("wr-live terminator not found")
        s = s[:i] + s[j + 1 :]
        print("strip wr-live stats row")
        return s
    if "className:`wr-live`" not in s:
        print("wr-live already gone")
        return s
    raise SystemExit("engine-stats / wr-live block not found")


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
    idx = s.find("/* wr-graph-wails */")
    if idx >= 0:
        return s[:idx].rstrip() + "\n" + CSS_BLOCK
    return s.rstrip() + "\n" + CSS_BLOCK


def cache_bust(js: str, css: str):
    dest = ROOT / "assets" / f"routes-{VER}.js"
    js_ver = js
    for old in range(20, 32):
        js_ver = js_ver.replace(f'from"./index-aura{old}.js"', f'from"./index-{VER}.js"')
    dest.write_text(js_ver, encoding="utf-8")
    print("wrote", dest, "bytes", len(js_ver.encode()))

    if IDX.exists():
        ix = IDX.read_text(encoding="utf-8")
        ix2 = ix
        for old in range(20, 32):
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
        for old in range(20, 32):
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
        "Math.abs(e.scoreLead)/12",
        "(-w*Math.log(w)",
        "rgba(15, 10, 5",
        "Math.PI/3*i",
        "s*.168",
        "s*.94*sc",
        "gt(k.ctx,t.candidates",
    ]
    forbid = [
        "點擊表格切換精簡",
        "className:`hint vs-hint`",
        "className:`engine-stats`",
        "className:`wr-live`",
        "a.length<2",
        "goMain()else",
        "白勝率",
        "className:`wr-key`",
        "粗線勝率",
        "4*w*(1-w)",
        "for(let i=0;i<5;i++){let a=-Math.PI/2",
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

#!/usr/bin/env python3
"""Apply AuraGo analysis/UI patches to assets/routes-aura26.js."""
from pathlib import Path
import sys

p = Path("assets/routes-aura26.js")
s = p.read_text(encoding="utf-8")

REPLACEMENTS = [
# --- original refresh/left-panel patches ---
(
"if(typeof e.token==`number`&&e.token>=0&&Ee>=0)AnaView[e.token]=Ee;e._view=typeof AnaView[e.token]==`number`?AnaView[e.token]:Ee}we=e,A(e)",
"if(typeof e.token==`number`&&e.token>=0&&Ee>=0)AnaView[e.token]=Ee;let _v=typeof AnaView[e.token]==`number`?AnaView[e.token]:Ee;if(!(_v>=0)){try{_v=q.getState().view}catch{}_v=_v>=0?_v:0}e._view=_v}we=e,A(e)",
),
(
"function ke(e,t){e&&F&&(Ee=t,De=Date.now(),F(e,t))}",
"function ke(e,t){typeof t==`number`&&(Ee=t,De=Date.now()),e&&F&&F(e,t)}",
),
(
"if(typeof tok==`number`&&tok>=0&&(tok===r||tok<Te||i>=0&&tok!==i))return;",
"if(typeof tok==`number`&&tok>=0&&(tok===r||tok<Te))return;",
),
(
"e&&typeof e._view==`number`&&e._view!==st.view&&(e=null)",
"e&&typeof e._view==`number`&&e._view>=0&&e._view!==st.view&&(e=null)",
),
(
"function Lt({onConnect:e}){let t=q(e=>e.engine),n=q(e=>e.analysis),r=q(e=>e.currentColor()),i=t.ready,a=n?.toMove||r",
"function Lt({onConnect:e}){let[,tick]=(0,u.useState)(0);(0,u.useEffect)(()=>P(()=>tick(e=>e+1)),[]);let t=q(e=>e.engine),n=q(e=>e.analysis),r=q(e=>e.currentColor()),i=t.ready,vw=q.getState().view,live=i?j():null;live&&typeof live._view==`number`&&live._view>=0&&live._view!==vw&&(live=null);n&&typeof n._view==`number`&&n._view>=0&&n._view!==vw&&(n=null);n=n||live;let a=n?.toMove||r",
),
(
",u=q(e=>e.showSubBoard)?_t(n?.ownership,n?.toMove||`B`):null,d=u?vt(u):null",
",own=q(e=>e.showSubBoard)?_t(n?.ownership,n?.toMove||`B`):null,d=own?vt(own):null",
),
(
"if(!e){v(`終局變化無法分析，請回上一手`);return}try{let t=await ln(e);",
"if(!e){v(`終局變化無法分析，請回上一手`);return}try{Ee=q.getState().view;let t=await ln(e);",
),
(
"i=()=>{if(z.current!==n)return;ln(e).then(e=>{",
"i=()=>{if(z.current!==n)return;Ee=r,ln(e).then(e=>{",
),
(
"((p=>{let n=q.getState().enginePosition();n&&ln({...n,maxMoves:q.getState().maxVars,interval:2,ownership:!0}).catch(()=>void 0)})()))",
"((p=>{let st=q.getState(),n=st.enginePosition();n&&(Ee=st.view,ln({...n,maxMoves:st.maxVars,interval:2,ownership:!0}).catch(()=>void 0))})()))",
),
(
"n&&(await ln({...n,maxMoves:4,interval:5,ownership:!1,maxVisits:80})",
"n&&(Ee=q.getState().view,await ln({...n,maxMoves:4,interval:5,ownership:!1,maxVisits:80})",
),
(
"t&&e.engine.ready&&ln({...t,maxMoves:e.maxVars,interval:2,ownership:!0}).catch(()=>void 0)",
"t&&e.engine.ready&&(Ee=e.view,ln({...t,maxMoves:e.maxVars,interval:2,ownership:!0})).catch(()=>void 0)",
),
# --- kE: set module Ee from inside pn() where Ee is a local useState ---
(
"function ke(e,t){typeof t==`number`&&(Ee=t,De=Date.now()),e&&F&&F(e,t)}function Ae",
"function ke(e,t){typeof t==`number`&&(Ee=t,De=Date.now()),e&&F&&F(e,t)}function kE(t){typeof t==`number`&&(Ee=t,De=Date.now())}function Ae",
),
(
"try{Ee=q.getState().view;let t=await ln(e);",
"try{kE(q.getState().view);let t=await ln(e);",
),
(
"if(z.current!==n)return;Ee=r,ln(e).then(e=>{",
"if(z.current!==n)return;kE(r),ln(e).then(e=>{",
),
(
"n&&(Ee=st.view,ln({...n,maxMoves:st.maxVars",
"n&&(kE(st.view),ln({...n,maxMoves:st.maxVars",
),
(
"n&&(Ee=q.getState().view,await ln({...n,maxMoves:4",
"n&&(kE(q.getState().view),await ln({...n,maxMoves:4",
),
(
"t&&e.engine.ready&&(Ee=e.view,ln({...t,maxMoves:e.maxVars",
"t&&e.engine.ready&&(kE(e.view),ln({...t,maxMoves:e.maxVars",
),
# --- remove territory totals ---
(
",own=q(e=>e.showSubBoard)?_t(n?.ownership,n?.toMove||`B`):null,d=own?vt(own):null;return(0,Y.jsxs)(`aside`",
";return(0,Y.jsxs)(`aside`",
),
(
",d?(0,Y.jsxs)(`p`,{className:`hint terr-line`,children:[`數子　黑 `,d.black.toFixed(1),`　白 `,d.white.toFixed(1)]}):null,(0,Y.jsx)(Pt,{})",
",(0,Y.jsx)(Pt,{})",
),
# --- move list: subscribe to live analysis so WR/lead fill on current ply ---
(
"function It(){let e=q(e=>e.root),t=q(e=>e.cursor),n=q(e=>e.analysis),r=q(e=>e.view),i=q(e=>e.history)",
"function It(){let[,tick]=(0,u.useState)(0);(0,u.useEffect)(()=>P(()=>tick(e=>e+1)),[]);let e=q(e=>e.root),t=q(e=>e.cursor),n=q(e=>e.analysis),r=q(e=>e.view);{let L=j();L&&typeof L._view==`number`&&L._view>=0&&L._view!==r&&(L=null);n=L||n}let i=q(e=>e.history)",
),
]

applied = 0
for old, new in REPLACEMENTS:
    n = s.count(old)
    if n == 0:
        if new in s:
            print("skip (already):", old[:56])
            continue
        print("MISSING:", old[:90], file=sys.stderr)
        sys.exit(1)
    if n != 1:
        print("not unique", n, old[:80], file=sys.stderr)
        sys.exit(1)
    s = s.replace(old, new, 1)
    applied += 1

need = [
    "typeof t==`number`&&(Ee=t,De=Date.now())",
    "e._view>=0&&e._view!==st.view",
    "n=n||live",
    "tok===r||tok<Te))return",
    "function kE(t)",
    "kE(q.getState().view)",
    "kE(st.view)",
    "n=L||n",
]
forbid = [
    "terr-line",
    "數子",
]
for x in need:
    if x not in s:
        print("verify fail need", x, file=sys.stderr)
        sys.exit(1)
for x in forbid:
    if x in s:
        print("verify fail still has", x, file=sys.stderr)
        sys.exit(1)

i = s.find("function Lt({onConnect:e})")
j = s.find("function Rt({open:e", i)
lt = s[i:j]
if ",u=" in lt or "let u=" in lt:
    print("TDZ risk: Lt still binds u", file=sys.stderr)
    sys.exit(1)

if applied == 0:
    print("already patched")
    sys.exit(0)

p.write_text(s, encoding="utf-8")
print("patched", applied, "replacements, bytes", len(s.encode("utf-8")))

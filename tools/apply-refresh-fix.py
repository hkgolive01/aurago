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
# --- remove 數子 totals (user did not ask for them) ---
(
",own=q(e=>e.showSubBoard)?_t(n?.ownership,n?.toMove||`B`):null,d=own?vt(own):null;return(0,Y.jsxs)(`aside`",
";return(0,Y.jsxs)(`aside`",
),
(
",d?(0,Y.jsxs)(`p`,{className:`hint terr-line`,children:[`數子　黑 `,d.black.toFixed(1),`　白 `,d.white.toFixed(1)]}):null,(0,Y.jsx)(Pt,{})",
",(0,Y.jsx)(Pt,{})",
),
# --- move list: subscribe to live analysis so 勝率/目差 fill on current ply ---
(
"function It(){let e=q(e=>e.root),t=q(e=>e.cursor),n=q(e=>e.analysis),r=q(e=>e.view),i=q(e=>e.history)",
"function It(){let[,tick]=(0,u.useState)(0);(0,u.useEffect)(()=>P(()=>tick(e=>e+1)),[]);let e=q(e=>e.root),t=q(e=>e.cursor),n=q(e=>e.analysis),r=q(e=>e.view);{let L=j();L&&typeof L._view==`number`&&L._view>=0&&L._view!==r&&(L=null);n=L||n}let i=q(e=>e.history)",
),
# --- setAnalysis: bind node via _view; stamp NEXT child only (never overwrite current policy) ---
(
"let a=t().view;o=Se(n.winrate,n.toMove),s=Ce(n.scoreLead,n.toMove),c=t().cursor,main=c&&function(n){for(;n&&n.parent;){if(n.parent.children[0]!==n)return!1;n=n.parent}return!0}(c);c&&(c.blackWRAfter=o,c.scoreLead=s,c.evalVisits=n.visits,c.scoreMean=s),rememberLead(a,s),main&&n.candidates&&n.candidates.length&&(c.children[0]?it(c.children[0],n):c.parent&&it(c,n))",
"let a=typeof n._view==`number`&&n._view>=0?n._view:t().view,o=Se(n.winrate,n.toMove),s=Ce(n.scoreLead,n.toMove),c=t().cursor,path=w(c);c=a<=0?t().root:a<=path.length?path[a-1]:Xe(t().root)[a-1];c&&(c.blackWRAfter=o,c.scoreLead=s,c.evalVisits=n.visits,c.scoreMean=s),rememberLead(a,s),n.candidates&&n.candidates.length&&c&&c.children[0]&&it(c.children[0],n)",
),
# --- jumpTo: stamp child with current analysis before clearing (step-forward / 全譜掃描) ---
(
"jumpTo(n){let r=t().anaToken;M(r),e({cursor:n,freshMove:!1,analysis:null,anaToken:-1,staleToken:r>=0?r:t().staleToken,...W(t().info,n)}),ut(t),at(t)}",
"jumpTo(n){let r=t().anaToken,cur=t().cursor,an=t().analysis;an&&n&&cur&&n.parent===cur&&an.candidates&&an.candidates.length&&it(n,an);M(r),e({cursor:n,freshMove:!1,analysis:null,anaToken:-1,staleToken:r>=0?r:t().staleToken,...W(t().info,n)}),ut(t),at(t)}",
),
# --- He: live wr=0 ok; scoreLeadBefore; LeadMap; absolute WR/lead when delta missing ---
(
"s&&n&&n.wr>0?d=n.wr:l?.wr==null?typeof i.blackWRAfter==`number`&&i.blackWRAfter>0?d=i.blackWRAfter",
"s&&n&&typeof n.wr==`number`?d=n.wr:l?.wr==null?typeof i.blackWRAfter==`number`&&i.blackWRAfter>=0?d=i.blackWRAfter",
),
(
"c?.lead==null?a&&typeof a.scoreLead==`number`&&(m=a.scoreLead):m=c.lead,s&&n?p=n.lead:l?.lead==null?typeof i.scoreLead==`number`&&(p=i.scoreLead):p=l.lead",
"c?.lead==null?typeof i.scoreLeadBefore==`number`?m=i.scoreLeadBefore:typeof i.scoreMean==`number`?m=i.scoreMean:a&&typeof a.scoreLead==`number`&&(m=a.scoreLead):m=c.lead,s&&n&&typeof n.lead==`number`?p=n.lead:l?.lead==null?typeof i.scoreLead==`number`&&(p=i.scoreLead):p=l.lead,m==null&&typeof LeadMap[t]==`number`&&(m=LeadMap[t]),p==null&&typeof LeadMap[t+1]==`number`&&(p=LeadMap[t+1])",
),
(
"if(f==null&&h==null)return null;",
"if(f==null&&h==null){if(d==null&&p==null)return null;let A=[],bw=d==null?null:d*100;bw!=null&&A.push((bw>=50?`黑`:`白`)+(bw>=50?bw:100-bw).toFixed(1)+`%`),p!=null&&A.push((p>=0?`黑`:`白`)+`+`+Math.abs(p).toFixed(1));return{dwr:null,dlead:null,cls:``,wrTxt:A.join(` · `)}}",
),
# --- empty rating hint: imported SGF needs 全譜掃描 ---
(
"children:`點擊表格切換精簡／加權　評級需滿 20 手有效手`",
"children:m.black.moves+m.white.moves?`點擊表格切換精簡／加權　評級需滿 20 手有效手`:`匯入棋譜請到選單按「全譜掃描」，才有評級與每手勝率／目差`",
),
# --- 全譜掃描: restore the ply the user was looking at ---
(
"async function Ie(){if(!t.ready)return;[...xn(p)];let e=bn(p);I.current=!1,he({running:!0,index:0,total:e.length}),v(`開始全譜掃描`);try{for(let t=0;t<=e.length&&!I.current;t++){",
"async function Ie(){if(!t.ready)return;[...xn(p)];let e=bn(p),saved=q.getState().cursor;I.current=!1,he({running:!0,index:0,total:e.length}),v(`開始全譜掃描`);try{for(let t=0;t<=e.length&&!I.current;t++){",
),
(
"v(`全譜掃描完成`)}catch(e){v(e instanceof Error?e.message:`掃描中斷`)}",
"saved&&q.getState().jumpTo(saved),v(`全譜掃描完成`)}catch(e){v(e instanceof Error?e.message:`掃描中斷`)}",
),
# --- remove rating-table hint ---
(
"(0,Y.jsx)(`p`,{className:`hint vs-hint`,children:m.black.moves+m.white.moves?`點擊表格切換精簡／加權　評級需滿 20 手有效手`:`匯入棋譜請到選單按「全譜掃描」，才有評級與每手勝率／目差`}),",
"",
),
# --- goMain ---
(
"function kE(t){typeof t==`number`&&(Ee=t,De=Date.now())}function Ae",
"function kE(t){typeof t==`number`&&(Ee=t,De=Date.now())}function goMain(){let e=q.getState(),t=e.root,r=new Set,i=t;for(;i;)r.add(i),i=i.children&&i.children[0];let a=e.cursor;if(r.has(a)){e.setToast(`已在主線`);return}for(;a&&a.parent&&!r.has(a);)a=a.parent;a&&e.jumpTo(a),e.setToast(`已回主線`)}function Ae",
),
(
"if(n<0){let t=e.root,r=new Set,i=t;for(;i;)r.add(i),i=i.children&&i.children[0];let a=e.cursor;if(r.has(a)){e.setToast(`已在主線`);return}for(;a&&a.parent&&!r.has(a);)a=a.parent;a&&e.jumpTo(a),e.setToast(`已回主線`)}",
"if(n<0)goMain()",
),
(
"let t=q.getState(),n=()=>{let e=t.root,n=new Set,r=e;for(;r;)n.add(r),r=r.children&&r.children[0];let i=t.cursor;if(n.has(i)){t.setToast(`已在主線`);return}for(;i&&i.parent&&!n.has(i);)i=i.parent;i&&t.jumpTo(i),t.setToast(`已回主線`)};",
"let t=q.getState(),n=goMain;",
),
# --- click occupied ---
(
"if(!e.ok)return t().setToast(e.reason),null",
"if(!e.ok)return e.reason!==`已有子`&&t().setToast(e.reason),null",
),
(
"function b(r,i){let a=e.nexts.find(e=>!e.pass&&e.x===r&&e.y===i);a?n(a):t(r,i)}",
"function b(r,i){let a=e.nexts.find(e=>!e.pass&&e.x===r&&e.y===i);a?n(a):e.board[i][r]||t(r,i)}",
),
(
"if(t.swiping)return;let a=y(e);a&&b(a.x,a.y)}return(0,Y.jsx)(`div`,{className:`board-stage main`",
"if(t.swiping)return;let a=y(e);a&&b(a.x,a.y)}function D(ev){ev.preventDefault();let a=y(ev);if(!a||!e.board[a.y][a.x])return;goMain()}return(0,Y.jsx)(`div`,{className:`board-stage main`",
),
(
"\"aria-label\":`主棋盤`,onPointerDown:S,onPointerMove:C,onPointerUp:w,onPointerCancel:()=>{v.current.pid=-1,_(null)},onPointerLeave:()=>_(null),children:",
"\"aria-label\":`主棋盤`,onPointerDown:S,onPointerMove:C,onPointerUp:w,onPointerCancel:()=>{v.current.pid=-1,_(null)},onPointerLeave:()=>_(null),onDoubleClick:D,children:",
),
]

applied = 0
for old, new in REPLACEMENTS:
    n = s.count(old)
    if n == 0:
        if new in s:
            print("skip (already):", old[:56])
            continue
        print("skip (obsolete):", old[:56])
        continue
    if new and new in s and old in new:
        print("skip (already):", old[:56])
        continue
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
    "c&&c.children[0]&&it(c.children[0],n)",
    "n.parent===cur&&an.candidates",
    "scoreLeadBefore==`number`?m=i.scoreLeadBefore",
    "LeadMap[t+1]",
    "saved&&q.getState().jumpTo(saved)",
    "typeof n.wr==`number`?d=n.wr",
    "function goMain()",
    "n=goMain",
    "if(n<0)goMain()",
    "onDoubleClick:D",
    "function D(ev)",
    "e.reason!==`已有子`",
    "e.board[i][r]||t(r,i)",
]
forbid = [
    "terr-line",
    "數子",
    "c.parent&&it(c,n)",
    "main&&n.candidates",
    "vs-hint",
    "點擊表格切換精簡",
    "評級需滿 20 手",
    "匯入棋譜請到選單按",
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

if s.count("saved&&q.getState().jumpTo(saved)") != 1:
    print("verify fail saved jumpTo count", s.count("saved&&q.getState().jumpTo(saved)"), file=sys.stderr)
    sys.exit(1)
if s.count("onDoubleClick:D") != 1:
    print("verify fail onDoubleClick count", s.count("onDoubleClick:D"), file=sys.stderr)
    sys.exit(1)
if s.count("function goMain()") != 1:
    print("verify fail goMain count", file=sys.stderr)
    sys.exit(1)

if applied == 0:
    print("already patched")
    sys.exit(0)

p.write_text(s, encoding="utf-8")
print("patched", applied, "replacements, bytes", len(s.encode("utf-8")))

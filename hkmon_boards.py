# -*- coding: utf-8 -*-
"""HK-MON — 象棋真實棋盤 (CCv2).

Wooden board, pieces sitting on intersections, palace diagonals,
楚河/漢界 river, legal-move dots. Trigger: sq = clicked square index (0..89).
"""
import streamlit as st

CSS = """
#xqroot{ font-family:'Noto Sans TC','Noto Sans JP',sans-serif; }
.xqboard{ position:relative; width:100%; max-width:540px; margin:0 auto;
  aspect-ratio:9/10; background:
  radial-gradient(ellipse at 50% 30%, #f3d9a4 0%, #e9c98c 55%, #d9b273 100%);
  border:10px solid #5b3a1e; border-radius:12px;
  box-shadow:0 10px 26px rgba(0,0,0,.5), inset 0 0 30px rgba(120,72,20,.25);
  overflow:hidden; touch-action:manipulation;}
.xqboard svg{ position:absolute; inset:0; width:100%; height:100%; }
.pc{ position:absolute; width:9.4%; aspect-ratio:1/1; transform:translate(-50%,-50%);
  border-radius:50%; display:flex; align-items:center; justify-content:center;
  background:radial-gradient(circle at 38% 30%, #fdf0d2 0%, #f0d49e 55%, #d8ab66 100%);
  border:2px solid #8a5a24; box-shadow:0 3px 6px rgba(0,0,0,.45), inset 0 2px 2px rgba(255,255,255,.7);
  font-weight:900; cursor:pointer; user-select:none; z-index:3;
  font-size:min(4.2vw, 26px); line-height:1;}
.pc.red{ color:#b03024; text-shadow:0 1px 0 rgba(255,255,255,.6);}
.pc.blk{ color:#262626; }
.pc.selpc{ box-shadow:0 0 0 4px #ffd23f, 0 6px 10px rgba(0,0,0,.5); z-index:4;}
.dot{ position:absolute; width:3.4%; aspect-ratio:1/1; transform:translate(-50%,-50%);
  border-radius:50%; background:radial-gradient(circle at 35% 30%, #8ef0a8, #1e8449);
  box-shadow:0 0 8px rgba(30,132,73,.8); cursor:pointer; z-index:5;}
.ring{ position:absolute; width:8.6%; aspect-ratio:1/1; transform:translate(-50%,-50%);
  border-radius:50%; border:4px solid #e8483b; cursor:pointer; z-index:5;
  box-shadow:0 0 10px rgba(232,72,59,.7);}
.lastmv{ position:absolute; width:2.6%; aspect-ratio:1/1; transform:translate(-50%,-50%);
  border-radius:50%; background:rgba(255,210,63,.85); z-index:1;}
.xqtag{ text-align:center; font-weight:900; margin:8px 0 4px; }
"""

JS = """
export default function (component) {
  const d = component.data || {};
  const root = component.parentElement.querySelector('#xqroot');
  if (!root) return;
  const P = 5, S = 10;
  const X = c => (P + c * S) * 100 / 90;
  const Y = r => P + r * S;

  let lines = '';
  for (let c = 0; c < 9; c++) {
    if (c === 0 || c === 8) {
      lines += `<line x1="${X(c)}" y1="${Y(0)}" x2="${X(c)}" y2="${Y(9)}"/>`;
    } else {
      lines += `<line x1="${X(c)}" y1="${Y(0)}" x2="${X(c)}" y2="${Y(4)}"/>`;
      lines += `<line x1="${X(c)}" y1="${Y(5)}" x2="${X(c)}" y2="${Y(9)}"/>`;
    }
  }
  for (let r = 0; r < 10; r++) {
    lines += `<line x1="${X(0)}" y1="${Y(r)}" x2="${X(8)}" y2="${Y(r)}"/>`;
  }
  for (const [x1, y1, x2, y2] of [[X(3),Y(0),X(5),Y(2)],[X(5),Y(0),X(3),Y(2)],
                                   [X(3),Y(7),X(5),Y(9)],[X(5),Y(7),X(3),Y(9)]]) {
    lines += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
  }
  const outer = `<rect x="${X(0)-1.6}" y="${Y(0)-1.6}" width="${S*8+3.2}" height="${S*9+3.2}"
    fill="none" stroke-width="0.8"/>`;

  let h = `<div class="xqboard">
    <svg viewBox="0 0 90 100" stroke="#7a4a1c" stroke-width="0.45">
      ${lines}${outer}
      <text x="25" y="51.8" font-size="4.6" fill="#8a5a24" text-anchor="middle"
        font-weight="700" stroke="none" font-family="serif" letter-spacing="1">楚 河</text>
      <text x="65" y="51.8" font-size="4.6" fill="#8a5a24" text-anchor="middle"
        font-weight="700" stroke="none" font-family="serif" letter-spacing="1">漢 界</text>
    </svg>`;
  if (d.last && d.last.length === 2) {
    for (const sq of d.last) {
      const r = Math.floor(sq / 9), c = sq % 9;
      h += `<div class="lastmv" style="left:${X(c)}%;top:${Y(r)}%;"></div>`;
    }
  }
  for (let sq = 0; sq < 90; sq++) {
    const p = d.board[sq];
    if (!p) continue;
    const r = Math.floor(sq / 9), c = sq % 9;
    const cls = (p.red ? 'red' : 'blk') + (d.sel === sq ? ' selpc' : '');
    h += `<div class="pc ${cls}" data-sq="${sq}"
      style="left:${X(c)}%;top:${Y(r)}%;">${p.t}</div>`;
  }
  for (const sq of (d.targets || [])) {
    const r = Math.floor(sq / 9), c = sq % 9;
    const isCap = !!d.board[sq];
    h += isCap
      ? `<div class="ring" data-sq="${sq}" style="left:${X(c)}%;top:${Y(r)}%;"></div>`
      : `<div class="dot" data-sq="${sq}" style="left:${X(c)}%;top:${Y(r)}%;"></div>`;
  }
  h += '</div>';
  root.innerHTML = h;
  root.querySelectorAll('[data-sq]').forEach(el => {
    el.addEventListener('click', () => component.setTriggerValue('sq', Number(el.dataset.sq)));
  });
  return {};
}
"""

XQ_BOARD = st.components.v2.component(
    "hkmon_xq_board",
    html="<div id='xqroot'></div>",
    css=CSS,
    js=JS,
)


def build_view(board, sel, targets, last):
    import hkmon_xiangqi as XQ
    disp = []
    for p in board:
        disp.append({"t": XQ.CHAR[p], "red": p[0] == "r"} if p else None)
    return {"board": disp, "sel": sel, "targets": targets or [],
            "last": last if last else []}

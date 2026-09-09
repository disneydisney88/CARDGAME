# -*- coding: utf-8 -*-
"""HK-MON 榕樹頭 — 麻將檯 UI (Custom Component v2).

A green-felt mahjong table with 3D tiles, four seats, discards in the
middle and round action buttons — like the classic HK mahjong apps.
The component renders everything from `data` and reports clicks back via
triggers: tile_click (hand tile index) / action (pong|kong|chi:<lo>|win|skip|confirm|zimo).
"""
import streamlit as st

NUMCN = "一二三四五六七八九"
SUITCN = "萬筒索"


def tile_inners():
    out = []
    for t in range(34):
        if t < 27:
            n, s = NUMCN[t % 9], SUITCN[t // 9]
            cls = " class='red'" if t % 9 == 4 else ""
            out.append(f"<b{cls}>{n}</b><i>{s}</i>")
        elif t == 27:
            out.append("<b>東</b>")
        elif t == 28:
            out.append("<b>南</b>")
        elif t == 29:
            out.append("<b>西</b>")
        elif t == 30:
            out.append("<b>北</b>")
        elif t == 31:
            out.append("<b class='red'>中</b>")
        elif t == 32:
            out.append("<b class='green'>發</b>")
        else:
            out.append("<span class='paik'></span>")
    return out


CSS = """
#mjroot{ font-family:'Noto Sans TC','Noto Sans JP',sans-serif; }
.tbl{ background:radial-gradient(ellipse at center,#3a8f5c 0%,#2a7349 62%,#1d5636 100%);
  border:12px solid #4a2f18; border-radius:20px; padding:12px 14px;
  box-shadow:inset 0 0 46px rgba(0,0,0,.4), 0 8px 22px rgba(0,0,0,.5); }
.topline{ display:flex; flex-wrap:wrap; justify-content:space-between; gap:6px;
  color:#d7efe0; font-size:13px; font-weight:700; margin-bottom:8px; }
.topline .pill{ background:rgba(0,0,0,.28); border-radius:999px; padding:2px 10px; }
.seat{ display:flex; align-items:center; gap:10px; margin:6px 0; flex-wrap:wrap; }
.pname{ background:#10331f; color:#ffe9a8; border:1px solid rgba(255,233,168,.35);
  border-radius:8px; padding:3px 10px; font-size:13px; font-weight:800; white-space:nowrap;}
.pname.me{ background:#5b3a00; color:#ffe27a; border-color:rgba(255,210,63,.5);}
.backs{ display:flex; gap:2px; flex-wrap:wrap; }
.back{ width:17px; height:28px; border-radius:3px; margin:1px;
  background:linear-gradient(#37a06a,#1c5e3a); border:1px solid #0f3d24;
  box-shadow:inset 0 2px 0 rgba(255,255,255,.25);}
.melds{ display:flex; flex-wrap:wrap; gap:2px; }
.center{ background:rgba(0,0,0,.16); border-radius:12px; padding:8px 10px; margin:8px 0; }
.riverrow{ display:flex; align-items:center; gap:6px; margin:3px 0; }
.rname{ color:#cfe8d8; font-size:12px; font-weight:800; width:74px; flex:none; text-align:right;}
.river{ display:flex; flex-wrap:wrap; }
.tile{ display:inline-flex; flex-direction:column; align-items:center; justify-content:center;
  background:linear-gradient(160deg,#ffffff 0%,#f2f1ea 70%,#d4d3c9 100%);
  border:1px solid #a09f94; border-radius:5px; margin:1px;
  box-shadow:0 3px 4px rgba(0,0,0,.4), inset 0 1px 0 #fff;
  text-align:center; user-select:none; line-height:1.02;}
.tile b{ font-weight:900; color:#1b3f8f; }
.tile i{ font-style:normal; font-weight:800; color:#1b3f8f; font-size:.68em; }
.tile b.red{ color:#c0392b; } .tile b.green{ color:#1e8449; }
.paik{ display:block; width:58%; height:46%; border:3px solid #1b3f8f; border-radius:2px; }
.t-hand{ width:50px; height:70px; font-size:23px; cursor:pointer; }
.t-hand:hover{ transform:translateY(-4px); }
.t-hand.sel{ transform:translateY(-12px); box-shadow:0 12px 16px rgba(0,0,0,.55), 0 0 0 3px #ffd23f; }
.t-hand.drawn{ box-shadow:0 3px 4px rgba(0,0,0,.4), 0 0 0 3px #ffd23f; }
.gap{ width:16px; }
.t-meld{ width:30px; height:42px; font-size:16px; }
.t-river{ width:29px; height:40px; font-size:15px; }
.t-back{ width:17px; height:28px; border-radius:3px;
  background:linear-gradient(#37a06a,#1c5e3a); border:1px solid #0f3d24;
  box-shadow:inset 0 2px 0 rgba(255,255,255,.25); }
.acts{ display:flex; align-items:center; gap:10px; margin:10px 0 2px; flex-wrap:wrap; }
.act{ display:inline-flex; flex-direction:column; align-items:center; justify-content:center;
  min-width:72px; height:72px; padding:4px 10px; border-radius:50%;
  font-size:28px; font-weight:900; color:#fff; cursor:pointer; user-select:none;
  box-shadow:0 6px 12px rgba(0,0,0,.45), inset 0 -4px 0 rgba(0,0,0,.25); }
.act small{ font-size:11px; font-weight:700; opacity:.92; }
.act:hover{ filter:brightness(1.12); }
.act.up{ background:radial-gradient(circle at 35% 30%,#6fe08a,#1e8449); }
.act.hu{ background:radial-gradient(circle at 35% 30%,#ff8a7a,#c0392b); }
.act.zimo{ background:radial-gradient(circle at 35% 30%,#ffb35c,#d35400); }
.act.pong{ background:radial-gradient(circle at 35% 30%,#ffd76e,#b8860b); color:#4a3000; }
.act.kong{ background:radial-gradient(circle at 35% 30%,#7ab8ff,#1b4f8f); }
.act.skip{ background:radial-gradient(circle at 35% 30%,#aab4c4,#57606f); }
.act.confirm{ background:radial-gradient(circle at 35% 30%,#ff9f6e,#c0562b); }
.banner{ text-align:center; color:#ffe27a; font-size:20px; font-weight:900;
  background:rgba(0,0,0,.35); border-radius:10px; padding:10px; margin:6px 0; }
.hint{ color:#cfe8d8; font-size:12px; margin-top:6px; }
"""

JS = """
export default function (component) {
  const d = component.data || {};
  const root = component.parentElement.querySelector('#mjroot');
  if (!root) return;
  const inn = d.tile_inners || [];
  const T = (tid, cls, attrs) =>
    '<div class="tile ' + cls + '"' + (attrs || '') + '>' + (inn[tid] || '') + '</div>';

  let h = '<div class="tbl">';
  h += '<div class="topline">';
  h += '<span class="pill">🀄 牌牆剩 ' + d.wall + '</span>';
  h += '<span class="pill">' + d.names.map((n, i) => n + ' ' + d.scores[i]).join('　·　') + '</span>';
  h += '</div>';

  if (d.over) {
    if (d.over.winner < 0) {
      h += '<div class="banner">' + d.over.labels.join('、') + '</div>';
    } else {
      h += '<div class="banner">🎉 ' + d.names[d.over.winner] + '　' +
           d.over.fan + ' 番　（' + d.over.labels.join('、') + '）</div>';
    }
  }

  // side/top opponents: p3 (top), p1 (left-down), p2 (right-down) simplified:
  // top row = p3, middle row = p1 melds/backs + center + p2
  const seat = (vi, pi) => {
    const pl = d.players[vi];
    let s = '<div class="seat"><span class="pname">' + d.names[pi] + ' ' + pl.score + '</span>';
    s += '<span class="backs">';
    for (let i = 0; i < pl.count; i++) s += '<span class="back"></span>';
    s += '</span><span class="melds">';
    for (const m of pl.melds) {
      if (m[0] === 'chi') {
        for (let x = m[1]; x < m[1] + 3; x++) s += T(x, 't-meld');
      } else {
        s += T(m[1], 't-meld') + T(m[1], 't-meld');
      }
    }
    s += '</span><span class="melds">';
    for (const r of pl.river) s += T(r, 't-river');
    s += '</span></div>';
    return s;
  };
  h += seat(0, 3);
  h += seat(1, 1);
  h += seat(2, 2);
  h += '<div class="center"><div class="riverrow"><span class="rname">🀄 檯面</span><span class="river">';
  h += '</span></div>';

  // my melds + river
  h += '<div class="seat"><span class="pname me">' + d.names[0] + ' ' + d.scores[0] + '</span><span class="melds">';
  for (const m of d.my_melds) {
    if (m[0] === 'chi') {
      for (let x = m[1]; x < m[1] + 3; x++) h += T(x, 't-meld');
    } else {
      h += T(m[1], 't-meld') + T(m[1], 't-meld');
    }
  }
  h += '</span><span class="melds">';
  for (const r of d.my_river) h += T(r, 't-river');
  h += '</span></div>';

  // hand
  h += '<div style="text-align:center;margin-top:4px;">';
  d.hand.forEach((tid, i) => {
    if (d.drawn_pos >= 0 && i === d.drawn_pos) h += '<span class="gap"></span>';
    const sel = i === d.sel ? ' sel' : '';
    const drw = i === d.drawn_pos ? ' drawn' : '';
    h += T(tid, 't-hand' + sel + drw, ' data-idx="' + i + '" style="cursor:pointer;"');
  });
  h += '</div>';

  // actions
  h += '<div class="acts">';
  if (d.over) {
    // nothing
  } else if (d.claim) {
    const c = d.claim;
    if (c.win) h += '<div class="act hu" data-act="win">胡</div>';
    if (c.kong) h += '<div class="act kong" data-act="kong">槓</div>';
    if (c.pong) h += '<div class="act pong" data-act="pong">碰</div>';
    if (c.chi && c.chi.length === 1) {
      h += '<div class="act up" data-act="chi:' + c.chi[0] + '">上</div>';
    }
    if (c.chi && c.chi.length > 1) {
      for (const lo of c.chi) {
        h += '<div class="act up" data-act="chi:' + lo + '" style="font-size:16px;">上' +
             d.tile_inners[lo] + '</div>';
      }
    }
    h += '<div class="act skip" data-act="skip">✕</div>';
  } else if (d.await_discard) {
    if (d.zimo) h += '<div class="act zimo" data-act="zimo">自摸</div>';
    if (d.sel >= 0) h += '<div class="act confirm" data-act="confirm">打出</div>';
  }
  h += '</div>';
  if (d.hint) h += '<div class="hint">' + d.hint + '</div>';
  h += '</div>';

  root.innerHTML = h;

  root.querySelectorAll('[data-idx]').forEach(el => {
    el.addEventListener('click', () => component.setTriggerValue('tile_click', Number(el.dataset.idx)));
  });
  root.querySelectorAll('[data-act]').forEach(el => {
    el.addEventListener('click', () => component.setTriggerValue('action', el.dataset.act));
  });
  return {};
}
"""

_MJ_TABLE = st.components.v2.component(
    "hkmon_mj_table",
    html="<div id='mjroot'></div>",
    css=CSS,
    js=JS,
)

MJ_TABLE = _MJ_TABLE


def build_view(g, sel):
    """Convert engine game state into component data."""
    hand = MJ_sorted(g)
    drawn = (g.get("await") or {}).get("drawn") if g.get("await") else None
    drawn_pos = -1
    if drawn is not None and hand:
        for i in range(len(hand) - 1, -1, -1):
            if hand[i] == drawn:
                drawn_pos = i
                break

    def meld_view(m):
        return [m[0], m[1]]

    players = []
    for p in (3, 1, 2):
        players.append({
            "score": g["scores"][p],
            "count": sum(g["hands"][p]),
            "melds": [meld_view(m) for m in g["melds"][p]],
            "river": g["rivers"][p][-12:],
        })

    aw = g.get("await")
    claim = None
    zimo = False
    hint = ""
    if aw and aw["type"] == "claim":
        o = aw["opts"]
        claim = {"win": "win" in o, "pong": "pong" in o, "kong": "kong" in o,
                 "chi": o.get("chi") or []}
    elif aw and aw["type"] == "discard":
        import hkmon_mahjong as MJm
        zimo = MJm.can_win(g["hands"][0], len(g["melds"][0])) or \
            MJm.is_thirteen_orphans(g["hands"][0], len(g["melds"][0]))
        if zimo:
            hint = "可以自摸！"
        elif sel is not None:
            hint = "再撳同一隻牌（或撳「打出」）即可打出"

    o = g.get("over")
    over = None
    if o:
        over = {"winner": -1 if o["winner"] is None else o["winner"],
                "fan": o.get("fan", 0), "labels": o.get("labels", [])}

    return {
        "hand": hand,
        "sel": sel if sel is not None else -1,
        "drawn_pos": drawn_pos,
        "zimo": bool(zimo),
        "await_discard": bool(aw and aw["type"] == "discard"),
        "claim": claim,
        "wall": len(g["wall"]),
        "names": list(g["names"]),
        "scores": list(g["scores"]),
        "players": players,
        "my_melds": [meld_view(m) for m in g["melds"][0]],
        "my_river": g["rivers"][0][-12:],
        "over": over,
        "hint": hint,
        "tile_inners": tile_inners(),
    }


def MJ_sorted(g):
    import hkmon_mahjong as MJm
    return MJm.sorted_hand(g["hands"][0])

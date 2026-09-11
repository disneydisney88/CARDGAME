# -*- coding: utf-8 -*-
"""HK-MON — modern card-battle arena (CCv2).

A Hearthstone/PTCG-Live style board: opponent area on top, glowing centre
divider with the battle log ticker, your area below, and a game-style
action bar. Triggers:
  act   : "move1" | "move2" | "surrender" | "confirm"
  bench : bench index (switch / send-in after faint)
  item  : item id
  panel : "swap" | "items" | "none"
"""
import streamlit as st

CSS = """
#arroot{ font-family:'Noto Sans TC','Noto Sans JP',sans-serif; }
.arena{ position:relative; border-radius:18px; overflow:hidden;
  background:linear-gradient(180deg,#1a2036 0%,#232c4a 46%,#3a2a24 52%,#241d33 100%);
  border:2px solid #3d466b; box-shadow:0 10px 26px rgba(0,0,0,.5); padding:10px 12px;}
.half{ display:flex; align-items:center; gap:12px; }
.half.foe{ justify-content:flex-end; }
.half.me{ justify-content:flex-start; }
.divider{ display:flex; align-items:center; justify-content:space-between;
  background:linear-gradient(90deg,rgba(255,210,63,.06),rgba(255,77,77,.14),rgba(255,210,63,.06));
  border-top:1.5px solid #4a5478; border-bottom:1.5px solid #4a5478;
  border-radius:8px; padding:4px 12px; margin:8px 0; min-height:34px;}
.logtick{ color:#aeb8d8; font-size:.74rem; text-align:left; flex:1;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.turnbadge{ color:#ffd23f; font-weight:900; font-size:.9rem; white-space:nowrap;
  text-shadow:0 0 8px rgba(255,136,0,.6);}
.seatname{ font-weight:900; font-size:.85rem; margin-bottom:3px;}
.benchrow{ display:flex; gap:5px; flex-wrap:wrap; margin-top:4px; }
.bench{ display:flex; align-items:center; gap:3px; background:#161b2c;
  border:1.5px solid #3a4055; border-radius:999px; padding:2px 9px 2px 4px;
  font-size:.72rem; color:#e8ecf8; font-weight:700;}
.bench.click{ cursor:pointer; }
.bench.click:hover{ border-color:#ffd23f; }
.bench.dead{ opacity:.35; text-decoration:line-through;}
.bench.hpbar{ width:44px; height:5px; background:#262b3a; border-radius:4px; overflow:hidden;}
.bench.hpfill{ height:100%; background:#3ecf6e;}
.card{ position:relative; width:216px; border-radius:14px; padding:7px;
  background:linear-gradient(160deg,var(--c1,#888),var(--c2,#ccc));
  box-shadow:0 10px 22px rgba(0,0,0,.5); border:2px solid rgba(255,255,255,.6);
  color:#1c1710;}
.card .art{ position:relative; height:86px; border-radius:9px;
  background:radial-gradient(circle at 50% 40%, var(--c2), var(--c1) 80%);
  display:flex; align-items:center; justify-content:center;
  border:2px solid rgba(255,255,255,.55); overflow:hidden;}
.card .art span{ font-size:3.2rem; filter:drop-shadow(0 4px 6px rgba(0,0,0,.4));}
.card .nm{ display:flex; justify-content:space-between; align-items:baseline;
  font-weight:900; font-size:.86rem; margin-bottom:4px; gap:4px;}
.card .nm .hp{ color:#d43a2f; }
.hpw{ height:12px; border-radius:7px; background:#262b3a; overflow:hidden;
  border:1.5px solid rgba(0,0,0,.45); margin-top:5px;}
.hpf{ height:100%; border-radius:7px; background:#3ecf6e; transition:width .5s;}
.hplbl{ display:flex; justify-content:space-between; color:#dfe4f2; font-size:.68rem;
  font-weight:800; margin-top:2px;}
.chips{ min-height:20px; margin-top:3px;}
.chip{ display:inline-block; padding:1px 7px; border-radius:999px; font-size:.62rem;
  font-weight:800; margin-right:3px; border:1.5px solid rgba(255,255,255,.3);}
.c-burn{ background:#5a1d0e; color:#ffb38a;} .c-para{ background:#4a4410; color:#ffef9e;}
.c-buff{ background:#123f2a; color:#9ff0c0;} .c-shield{ background:#153450; color:#a8d8ff;}
.card.shake{ animation:arshake .5s; }
@keyframes arshake{ 0%,100%{transform:translateX(0)} 20%{transform:translateX(-9px)}
  40%{transform:translateX(9px)} 60%{transform:translateX(-6px)} 80%{transform:translateX(6px)}}
.vs{ text-align:center; font-weight:900; color:#ffd23f; font-size:1.6rem;
  text-shadow:0 0 14px #ff8800; padding:0 8px;}
.abar{ display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; justify-content:center;}
.abtn{ position:relative; border-radius:12px; padding:9px 16px; cursor:pointer;
  font-weight:900; font-size:.92rem; color:#fff; user-select:none; text-align:center;
  background:linear-gradient(180deg,#e05548,#a02c22);
  box-shadow:0 4px 0 rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.35);
  border:1.5px solid rgba(255,255,255,.25);}
.abtn:hover{ filter:brightness(1.12); }
.abtn small{ display:block; font-size:.68rem; font-weight:700; opacity:.92;}
.abtn.gold{ background:linear-gradient(180deg,#e8a93d,#a8700f); }
.abtn.blue{ background:linear-gradient(180deg,#4a7fd6,#274b8f); }
.abtn.grey{ background:linear-gradient(180deg,#6b7488,#3d4454); }
.abtn.off{ opacity:.45; pointer-events:none; filter:grayscale(.6);}
.sup{ position:absolute; top:-8px; right:-6px; background:#1e8449; color:#fff;
  font-size:.6rem; border-radius:999px; padding:1px 6px; border:1.5px solid #fff;}
.panel{ background:#161b2c; border:1.5px solid #3a4055; border-radius:12px;
  padding:8px; margin-top:8px;}
.ptitle{ color:#ffe9a8; font-weight:800; font-size:.8rem; margin-bottom:5px;}
.popts{ display:flex; gap:6px; flex-wrap:wrap;}
.popt{ display:flex; align-items:center; gap:4px; background:#1f2537;
  border:1.5px solid #3a4055; border-radius:10px; padding:4px 9px; cursor:pointer;
  color:#e8ecf8; font-size:.75rem; font-weight:700;}
.popt:hover{ border-color:#ffd23f; }
.popt .mhp{ width:34px; height:5px; background:#262b3a; border-radius:4px; overflow:hidden;}
.popt .mhpf{ height:100%; background:#3ecf6e;}
.deads{ color:#7d87a8; font-size:.72rem; }
.banner{ text-align:center; font-weight:900; font-size:1.15rem; padding:10px;
  border-radius:12px; margin:4px 0;}
.banner.w{ background:rgba(255,210,63,.14); color:#ffd23f; border:1.5px solid #ffd23f;}
.banner.l{ background:rgba(138,147,181,.12); color:#8a93b5; border:1.5px solid #8a93b5;}
.stagedots{ display:inline-block; }
.stagedots i{ display:inline-block; width:11px; height:11px; border-radius:50%;
  border:2px solid #ffd23f; margin-right:3px;}
.stagedots i.done{ background:#3ecf6e; border-color:#3ecf6e;}
.stagedots i.now{ background:#ffd23f; box-shadow:0 0 8px #ffd23f;}
"""

JS = """
export default function (component) {
  const d = component.data || {};
  const root = component.parentElement.querySelector('#arroot');
  if (!root) return;

  const hpColor = p => p > 50 ? '#3ecf6e' : (p > 25 ? '#f5b83d' : '#e8483b');
  const card = (f, right, shake) => {
    if (!f) return '';
    const pct = Math.max(0, Math.round(100 * f.hp / Math.max(1, f.mhp)));
    let chips = '';
    if (f.status === 'burn') chips += '<span class="chip c-burn">🔥</span>';
    if (f.status === 'para') chips += '<span class="chip c-para">⚡</span>';
    if (f.buff) chips += '<span class="chip c-buff">⬆+' + f.buff + '</span>';
    if (f.shield) chips += '<span class="chip c-shield">🛡</span>';
    return '<div class="card' + (shake ? ' shake' : '') + '" style="--c1:' + f.c1 + ';--c2:' + f.c2 + '">' +
      '<div class="nm"><span>' + f.name + '</span><span class="hp">HP ' + f.hp + '</span></div>' +
      '<div class="art"><span>' + f.emoji + '</span></div>' +
      '<div class="hpw"><div class="hpf" style="width:' + pct + '%;background:' + hpColor(pct) + '"></div></div>' +
      '<div class="hplbl"><span>' + f.label + '</span><span>' + f.hp + '/' + f.mhp + '</span></div>' +
      '<div class="chips">' + chips + '</div></div>';
  };
  const benchRow = (f, clickable) => {
    if (!f) return '';
    let s = '<div class="benchrow">';
    for (const b of (f.bench || [])) {
      const pct = Math.max(0, Math.round(100 * b.hp / Math.max(1, b.mhp)));
      s += b.hp > 0
        ? '<div class="bench' + (clickable ? ' click' : '') + '"' +
          (clickable ? ' data-bench="' + b.i + '"' : '') + '>' + b.emoji + ' ' + b.name +
          '<span class="hpbar"><span class="hpfill" style="width:' + pct + '%"></span></span></div>'
        : '<div class="bench dead">' + b.emoji + ' ' + b.name + '</div>';
    }
    return s + '</div>';
  };
  const dots = d.stage_dots || null;
  let mid = '<div class="divider"><span class="logtick">' + (d.log || '') + '</span>';
  mid += '<span class="vs">VS</span>';
  mid += '<span class="turnbadge">' + (d.turn_label || '') +
         (dots ? '<span class="stagedots">' + dots.map(s => '<i class="' + s + '"></i>').join('') + '</span>' : '') +
         '</span></div>';

  let h = '<div class="arena">';
  h += '<div class="seatname" style="color:#ff9f9f;text-align:right;">🔴 ' + d.foe.label +
       (d.foe.deck_name ? ' · ' + d.foe.deck_name : '') + '</div>';
  h += '<div class="half foe"><div>' + benchRow(d.foe, false) + '</div></div>';
  h += '<div class="half foe">' + card(d.foe, true, d.hit === 'e' || d.hit === 'ep') + '</div>';
  h += mid;
  h += '<div class="half me">' + card(d.me, false, d.hit === 'p' || d.hit === 'pe') + '</div>';
  h += '<div class="half me"><div>' + benchRow(d.me, d.can_bench) + '</div></div>';

  if (d.over) {
    h += '<div class="banner ' + (d.over.win ? 'w' : 'l') + '">' + d.over.title + '</div>';
  } else if (d.pending) {
    h += '<div class="panel"><div class="ptitle">' + d.replace_title + '</div><div class="popts">';
    for (const b of (d.me.bench || [])) {
      if (b.hp > 0) {
        h += '<div class="popt" data-bench="' + b.i + '">' + b.emoji + ' ' + b.name + '</div>';
      }
    }
    h += '</div></div>';
  } else if (d.can_act) {
    h += '<div class="abar">';
    for (const m of (d.moves || [])) {
      const off = m.off ? ' off' : '';
      const cls = m.key === 'move1' ? '' : ' gold';
      h += '<div class="abtn' + cls + off + '" data-act="' + m.key + '">' + m.name +
           '<small>⚔ ' + m.power + (m.tag || '') + (m.cd ? ' · ⏳' + d.cd_txt : '') + '</small>' +
           (m.sup ? '<span class="sup">×1.5</span>' : '') + '</div>';
    }
    h += '<div class="abtn blue" data-panel="items">' + d.items_txt + '</div>';
    h += '<div class="abtn grey" data-panel="swap">' + d.swap_txt + '</div>';
    h += '<div class="abtn grey" data-act="surrender" style="font-size:.7rem;">🏳</div>';
    h += '</div>';
    if (d.panel === 'swap') {
      h += '<div class="panel"><div class="ptitle">' + d.swap_txt + '</div><div class="popts">';
      let any = false;
      for (const b of (d.me.bench || [])) {
        if (b.hp > 0 && !b.active) {
          any = true;
          h += '<div class="popt" data-bench="' + b.i + '">' + b.emoji + ' ' + b.name + '</div>';
        }
      }
      h += (any ? '' : '<span class="deads">' + d.none_txt + '</span>') + '</div></div>';
    }
    if (d.panel === 'items') {
      h += '<div class="panel"><div class="ptitle">' + d.items_txt + '</div><div class="popts">';
      if (!(d.items || []).length) h += '<span class="deads">' + d.none_txt + '</span>';
      for (const it of (d.items || [])) {
        h += '<div class="popt" data-item="' + it.id + '">' + it.emoji + ' ' + it.name + '</div>';
      }
      h += '</div></div>';
    }
  } else {
    h += '<div class="abar"><div class="abtn grey off">' + d.wait_txt + '</div></div>';
  }
  if (d.hint) h += '<div class="hint" style="color:#aeb8d8;font-size:.72rem;text-align:center;margin-top:6px;">' + d.hint + '</div>';
  h += '</div>';
  root.innerHTML = h;

  root.querySelectorAll('[data-act]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('act', el.dataset.act)));
  root.querySelectorAll('[data-bench]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('bench', Number(el.dataset.bench))));
  root.querySelectorAll('[data-item]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('item', el.dataset.item)));
  root.querySelectorAll('[data-panel]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('panel', el.dataset.panel)));
  return {};
}
"""

ARENA = st.components.v2.component(
    "hkmon_arena",
    html="<div id='arroot'></div>",
    css=CSS,
    js=JS,
)


def build_arena(b, my_side, panel):
    """Convert engine battle state into arena component data.

    my_side: which seat is 'me' (bottom). AI mode always 'p'; hotseat = the
    acting side; online host 'p' / guest 'e'."""
    import hkmon_data as D
    import hkmon_i18n as I18N

    lang = b["lang"]
    foe_side = "e" if my_side == "p" else "p"
    pvpish = b["mode"] in ("hotseat", "online")

    def act_idx(side):
        return b["pa" if side == "p" else "ea"]

    def side_view(side, label, deck_name=None):
        idx = act_idx(side)
        f = b[side][idx]
        card = D.MON[f["id"]]
        typ = D.TYPES[card["type"]]
        bench = []
        for i, x in enumerate(b[side]):
            cc = D.MON[x["id"]]
            bench.append({"i": i, "emoji": cc["emoji"], "name": cc["name"][lang],
                          "hp": x["hp"], "mhp": x["mhp"], "active": i == idx})
        return {"label": label, "name": card["name"][lang], "emoji": card["emoji"],
                "hp": f["hp"], "mhp": f["mhp"], "c1": typ["c1"], "c2": typ["c2"],
                "status": f["status"], "buff": f["buff"], "shield": f["shield"],
                "bench": bench, "deck_name": deck_name}

    cur = b["pending"] or (b["to_act"] if pvpish else my_side)
    me = side_view(my_side, b["labels"][my_side])
    foe = side_view(foe_side, b["labels"][foe_side],
                    D.DECK[b["enemy_deck_id"]]["name"][lang] if not pvpish else None)

    f_active = b[my_side][act_idx(my_side)]
    f_card = D.MON[f_active["id"]]
    foe_active = b[foe_side][act_idx(foe_side)]
    foe_card = D.MON[foe_active["id"]]
    mult = D.eff_mult(f_card["type"], foe_card["type"])
    m1 = D.MOVE1[f_card["type"]][act_idx(my_side) % 4]
    m2 = f_card["move2"]
    items_ids = b["pitems" if my_side == "p" else "eitems"]

    pending = b["pending"] == my_side
    can_act = (not b["over"]) and (not b["pending"]) and \
        (not pvpish or b["to_act"] == my_side)

    turn_label = I18N.t(lang, "turn_of", n=b["labels"][cur]) if pvpish \
        else f"{I18N.t(lang, 'turn')} {b['turn']}"
    stage_dots = None
    if b["mode"] == "gauntlet":
        stage_dots = ["done" if s < b["stage"] else ("now" if s == b["stage"] else "")
                      for s in (1, 2, 3)]

    over = None
    if b["over"]:
        if pvpish:
            wl = b["labels"].get(b.get("winner"), "?")
            over = {"win": b.get("winner") == my_side,
                    "title": "🏆 " + I18N.t(lang, "m_win_pvp", n=wl)}
        else:
            over = {"win": b["win"],
                    "title": "🏆 " + I18N.t(lang, "result_title_win" if b["win"] else "result_title_lose")}

    log = b["log"][-1] if b["log"] else ""
    return {
        "me": me, "foe": foe,
        "moves": [
            {"key": "move1", "name": m1["name"][lang], "power": m1["power"],
             "tag": " ×1.5" if mult > 1 else (" ×0.75" if mult < 1 else ""),
             "sup": mult > 1, "off": False, "cd": 0},
            {"key": "move2", "name": m2["name"][lang], "power": m2["power"],
             "tag": "", "sup": False, "off": f_active["cd2"] > 0, "cd": f_active["cd2"]},
        ],
        "items": [{"id": iid, "emoji": D.ITEM[iid]["emoji"],
                   "name": D.ITEM[iid]["name"][lang]} for iid in items_ids],
        "pending": pending,
        "can_act": can_act,
        "can_bench": pending or can_act,
        "turn_label": turn_label,
        "stage_dots": stage_dots,
        "log": log,
        "hit": b.get("hit") or "",
        "over": over,
        "panel": panel or "",
        "hint": "" if can_act or b["over"] or pending else I18N.t(lang, "not_your_turn"),
        "items_txt": "🎒 " + I18N.t(lang, "items_panel")[2:] if False else "🎒 " + I18N.t(lang, "use"),
        "swap_txt": I18N.t(lang, "switch_panel"),
        "none_txt": I18N.t(lang, "empty_bench"),
        "wait_txt": I18N.t(lang, "not_your_turn"),
        "replace_title": I18N.t(lang, "replace_title"),
        "cd_txt": I18N.t(lang, "cooldown", n=""),
        "tile_inners": [],
    }

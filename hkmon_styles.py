# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — CSS + card HTML renderer (Pokémon-TCG-style layout)."""

import hkmon_data as D
import hkmon_i18n as I18N

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Sans+JP:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap');

.stApp, .stApp * { font-family:'Noto Sans TC','Noto Sans JP','Noto Sans KR',-apple-system,'Segoe UI',sans-serif; }

/* ---------------- Hong Kong neon hero ---------------- */
.neon-band{ background:linear-gradient(180deg,#171d33 0%,#0e1116 100%); border:1.5px solid #2c3350;
  border-radius:18px; padding:30px 18px 24px; margin-bottom:6px; }
.neon-title{ font-weight:900; font-size:3rem; line-height:1.08; text-align:center; color:#fff;
  text-shadow:0 0 6px #ff4d4d,0 0 18px #ff2d2d,0 0 46px #ff0000,0 0 80px #ff8800; letter-spacing:.05em; }
.neon-sub{ text-align:center; color:#ffe9a8; font-size:1.06rem; margin-top:10px;
  text-shadow:0 0 10px rgba(255,210,63,.85); }
.neon-tag{ text-align:center; color:#b9c3e0; font-size:.92rem; margin-top:8px; }
.hk-badge{ display:inline-block; background:#1c2237; border:1.5px solid #3d466b; color:#ffe9a8;
  border-radius:999px; padding:4px 14px; font-size:.8rem; font-weight:700; }
.badge-row{ text-align:center; margin-top:14px; }

/* ---------------- street-sign section header ---------------- */
.street-sign{ display:inline-block; background:#0a5c36; color:#fff; padding:.3em 1.1em;
  border-radius:8px; border:3px solid #fff; box-shadow:0 4px 0 rgba(0,0,0,.45);
  font-weight:900; letter-spacing:.14em; font-size:1.05rem; }

/* ---------------- TCG card ---------------- */
.hkcard{ position:relative; width:292px; margin:0 auto; border-radius:16px; padding:9px;
  background:linear-gradient(160deg,var(--c1),var(--c2)); color:#1c1710;
  box-shadow:0 12px 26px rgba(0,0,0,.5); border:2px solid rgba(255,255,255,.7); }
.hkcard .hkinner{ background:#fdfaf1; border-radius:10px; padding:8px 8px 7px; }
.hkcard-top{ display:flex; align-items:baseline; gap:6px; margin-bottom:5px; }
.hkcard-name{ font-weight:900; font-size:1.0rem; flex:1; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis; }
.hkcard-hp{ font-weight:900; color:#d43a2f; font-size:.92rem; white-space:nowrap; }
.hkcard-art{ position:relative; height:148px; border-radius:8px;
  background:radial-gradient(circle at 50% 40%, var(--c2), var(--c1) 78%);
  display:flex; align-items:center; justify-content:center; overflow:hidden;
  border:2px solid #d9a13c; }
.hkcard-emoji{ font-size:4.6rem; filter:drop-shadow(0 6px 8px rgba(0,0,0,.35));
  z-index:2; }
.hkcard-rare{ position:absolute; top:4px; right:7px; font-size:1rem; z-index:3;
  text-shadow:0 0 6px #fff, 0 0 12px #ffd23f; }
.hkcard.rare2 .hkcard-art::after{ content:''; position:absolute; inset:0; z-index:1;
  background:linear-gradient(115deg,transparent 32%,rgba(255,255,255,.8) 46%,rgba(255,255,255,0) 60%);
  transform:translateX(-130%); animation:holoshine 2.8s infinite; }
@keyframes holoshine{ 0%{transform:translateX(-130%);} 55%,100%{transform:translateX(130%);} }
.hkmove{ display:flex; justify-content:space-between; align-items:baseline; gap:8px;
  padding:3px 7px; margin:4px 0 0; background:#fff; border:1.5px solid #e0d3ab;
  border-radius:6px; font-size:.78rem; font-weight:700; }
.hkmove .mno{ color:#8a7a52; font-weight:500; margin-right:4px; }
.hkmove-dmg{ color:#d43a2f; font-weight:900; white-space:nowrap; }
.hkcard-foot{ display:flex; justify-content:space-between; gap:6px; font-size:.66rem;
  color:#6b5f45; margin-top:5px; padding:0 2px; font-weight:600; }
.hkcard-flavor{ font-size:.68rem; color:#7a6f57; margin-top:4px; line-height:1.35;
  border-top:1px dashed #d8cba6; padding-top:4px; min-height:2.5em; }
.hkcard.shake{ animation:shake .5s; }
@keyframes shake{ 0%,100%{transform:translateX(0)} 20%{transform:translateX(-9px)}
  40%{transform:translateX(9px)} 60%{transform:translateX(-6px)} 80%{transform:translateX(6px)} }
.hkcard.small{ width:216px; padding:7px; }
.hkcard.small .hkcard-art{ height:100px; }
.hkcard.small .hkcard-emoji{ font-size:3rem; }
.hkcard.small .hkcard-name{ font-size:.82rem; }
.hkcard.small .hkmove{ font-size:.66rem; }
.hkcard.small .hkcard-flavor{ font-size:.6rem; }
.hkcard.item .hkcard-art{ border-color:#b08020; }

/* ---------------- HP bar / chips ---------------- */
.hpwrap{ width:292px; margin:8px auto 0; }
.hpwrap.small{ width:216px; }
.hpbar{ height:13px; border-radius:8px; background:#262b3a; border:1.5px solid #00000066;
  overflow:hidden; }
.hpfill{ height:100%; border-radius:8px; transition:width .5s ease, background .5s ease;
  background:#3ecf6e; }
.hplabel{ font-size:.72rem; color:#dfe4f2; display:flex; justify-content:space-between;
  margin-top:3px; font-weight:800; }
.stchip{ display:inline-block; padding:2px 9px; border-radius:999px; font-size:.68rem;
  font-weight:800; margin:3px 4px 0 0; border:1.5px solid rgba(255,255,255,.3); }
.chip-burn{ background:#5a1d0e; color:#ffb38a; }
.chip-para{ background:#4a4410; color:#ffef9e; }
.chip-buff{ background:#123f2a; color:#9ff0c0; }
.chip-shield{ background:#153450; color:#a8d8ff; }
.benchchip{ display:inline-flex; align-items:center; gap:5px; background:#1c2030;
  border:1.5px solid #3a4055; padding:3px 9px; border-radius:999px; font-size:.72rem;
  color:#e8ecf8; margin:3px 4px 0 0; font-weight:600; }
.benchchip.dead{ opacity:.38; text-decoration:line-through; }
.vs-badge{ font-size:2rem; text-align:center; font-weight:900; color:#ffd23f;
  text-shadow:0 0 14px #ff8800; }
.stage-dot{ display:inline-block; width:14px; height:14px; border-radius:50%;
  border:2px solid #ffd23f; margin:0 4px; }
.stage-dot.done{ background:#3ecf6e; border-color:#3ecf6e; }
.stage-dot.now{ background:#ffd23f; box-shadow:0 0 10px #ffd23f; }

/* ---------------- type chart ---------------- */
.tchart{ border-collapse:collapse; margin:10px auto; }
.tchart th, .tchart td{ border:1.5px solid #3a4055; padding:5px 9px; text-align:center;
  font-size:.82rem; }
.tchart th{ background:#1c2237; color:#ffe9a8; }
.tchart td.rowhead{ background:#1c2237; font-weight:800; }
.tchart .x15{ background:#1d3a24; color:#7ef0a2; font-weight:900; }
.tchart .x075{ background:#3a1d1d; color:#ff9f9f; font-weight:900; }
.tchart .x10{ color:#8a93b5; }

/* ---------------- misc ---------------- */
.feature-row{ text-align:center; margin-top:16px; }
.feature-chip{ display:inline-block; background:#171c2e; border:1.5px solid #333c5e;
  color:#dfe4f5; border-radius:12px; padding:8px 14px; margin:4px; font-size:.85rem; font-weight:600; }
.credit{ text-align:center; color:#7d87a8; font-size:.75rem; margin-top:18px; line-height:1.6; }
"""


def inject_css():
    import streamlit as st
    st.markdown(f"<style>{BASE_CSS}</style>", unsafe_allow_html=True)


RARITY_MARK = {0: "●", 1: "★", 2: "✦"}


def card_html(card, lang, small=False, shake=False, hp=None, mhp=None):
    """Render a card (monster or item) as Pokémon-TCG-style HTML."""
    typ = D.TYPES[card.get("type", "trainer")]
    kind = card.get("kind") or ("item" if "effect" in card else "mon")
    style = f"--c1:{typ['c1']};--c2:{typ['c2']}"
    classes = ["hkcard"]
    if card.get("rarity", 1) == 2 and kind == "mon":
        classes.append("rare2")
    if kind == "item":
        classes.append("item")
    if small:
        classes.append("small")
    if shake:
        classes.append("shake")
    cls = " ".join(classes)

    tname = typ["name"][lang]
    setno = D.SET_NO[card["id"]]
    total = D.TOTAL_CARDS
    rare = RARITY_MARK[card.get("rarity", 1)]

    if kind == "mon":
        m1 = D.MOVE1[card["type"]][0]
        m2 = card["move2"]
        wk = D.weaknesses(card["type"])
        wk_str = " ".join(D.TYPES[t]["emoji"] for t in wk) if wk else "—"
        moves = (
            f'<div class="hkmove"><span><span class="mno">1.</span>{m1["name"][lang]}</span>'
            f'<span class="hkmove-dmg">{m1["power"]}</span></div>'
            f'<div class="hkmove"><span><span class="mno">2.</span>{m2["name"][lang]}</span>'
            f'<span class="hkmove-dmg">{m2["power"]}</span></div>'
        )
        hp_txt = f"HP {card['hp']}"
        body = (
            f'<div class="hkcard-top"><span class="hkcard-name">{card["name"][lang]}</span>'
            f'<span class="hkcard-hp">{hp_txt}</span>'
            f'<span title="{tname}">{typ["emoji"]}</span></div>'
            f'<div class="hkcard-art"><span class="hkcard-emoji">{card["emoji"]}</span>'
            f'<span class="hkcard-rare">{rare}</span></div>'
            f'<div class="hkinner" style="margin-top:6px;">{moves}'
            f'<div class="hkcard-foot"><span>{I18N.t(lang,"weakness")}:{wk_str}</span>'
            f'<span>Nº {setno:03d}/{total}</span></div>'
            f'<div class="hkcard-flavor">「{card["flavor"][lang]}」</div></div>'
        )
    else:  # item
        body = (
            f'<div class="hkcard-top"><span class="hkcard-name">{card["name"][lang]}</span>'
            f'<span class="hkcard-hp">ITEM</span>'
            f'<span title="{tname}">{typ["emoji"]}</span></div>'
            f'<div class="hkcard-art"><span class="hkcard-emoji">{card["emoji"]}</span>'
            f'<span class="hkcard-rare">{rare}</span></div>'
            f'<div class="hkinner" style="margin-top:6px;">'
            f'<div class="hkmove"><span>{card["desc"][lang]}</span></div>'
            f'<div class="hkcard-foot"><span>{D.TYPES["trainer"]["name"][lang]}</span>'
            f'<span>Nº {setno:03d}/{total}</span></div></div>'
        )
    return f'<div class="{cls}" style="{style}"><div class="hkinner">{body}</div></div>'


def hp_bar(f, lang, label_left="", small=False):
    pct = max(0, min(100, round(100 * f["hp"] / f["mhp"])))
    color = "#3ecf6e" if pct > 50 else ("#f5b83d" if pct > 25 else "#e8483b")
    chips = ""
    if f["status"] == "burn":
        chips += f'<span class="stchip chip-burn">🔥{I18N.t(lang, "status_burn")}</span>'
    elif f["status"] == "para":
        chips += f'<span class="stchip chip-para">⚡{I18N.t(lang, "status_para")}</span>'
    if f["buff"]:
        chips += f'<span class="stchip chip-buff">⬆ +{f["buff"]}</span>'
    if f["shield"]:
        chips += f'<span class="stchip chip-shield">🛡</span>'
    cls = "hpwrap small" if small else "hpwrap"
    return (
        f'<div class="{cls}"><div class="hpbar"><div class="hpfill" style="width:{pct}%;background:{color}"></div></div>'
        f'<div class="hplabel"><span>{label_left}</span><span>{f["hp"]} / {f["mhp"]} ({pct}%)</span></div>'
        f'<div>{chips}</div></div>'
    )


def type_chart_html(lang):
    heads = "".join(
        f'<th title="{D.TYPES[t]["name"][lang]}">{D.TYPES[t]["emoji"]}</th>'
        for t in D.TYPE_ORDER
    )
    rows = ""
    for at in D.TYPE_ORDER:
        cells = ""
        for df in D.TYPE_ORDER:
            m = D.eff_mult(at, df)
            if m > 1:
                cells += '<td class="x15">×1.5</td>'
            elif m < 1:
                cells += '<td class="x075">×0.75</td>'
            else:
                cells += '<td class="x10">—</td>'
        an = D.TYPES[at]["name"][lang]
        rows += (f'<tr><td class="rowhead">{D.TYPES[at]["emoji"]} {an}</td>{cells}</tr>')
    return (f'<table class="tchart"><tr><th></th>{heads}</tr>{rows}</table>')


def bench_chips_html(side_list, active_idx, lang):
    out = []
    for i, f in enumerate(side_list):
        card = D.MON[f["id"]]
        if f["hp"] <= 0:
            out.append(f'<span class="benchchip dead">{card["emoji"]} {card["name"][lang]}</span>')
        elif i == active_idx:
            out.append(f'<span class="benchchip" style="border-color:#ffd23f">▶ {card["emoji"]} {card["name"][lang]} {f["hp"]}</span>')
        else:
            out.append(f'<span class="benchchip">{card["emoji"]} {card["name"][lang]} {f["hp"]}</span>')
    return "".join(out)

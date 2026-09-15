# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — CSS + card HTML renderer (Pokémon-TCG-style layout)."""

import hkmon_data as D
import hkmon_i18n as I18N

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Sans+JP:wght@400;700&family=Noto+Sans+KR:wght@400;700&family=Outfit:wght@500;700;800;900&display=swap');

:root{
  --bg:#0a0d16; --surface:rgba(255,255,255,.045); --surface2:rgba(255,255,255,.07);
  --border:rgba(255,255,255,.09); --border2:rgba(255,255,255,.16);
  --accent1:#7c5cff; --accent2:#22d3ee; --pink:#ff4d6d; --gold:#ffd23f;
  --text:#eef1f8; --muted:#9aa3bd; --radius:16px;
}

.stApp{
  background:
    radial-gradient(1100px 760px at 88% -12%, rgba(124,92,255,.16), transparent 58%),
    radial-gradient(900px 640px at -8% 28%, rgba(34,211,238,.10), transparent 55%),
    radial-gradient(820px 620px at 50% 118%, rgba(255,77,109,.09), transparent 60%),
    var(--bg) !important;
  color:var(--text);
}
.stApp, .stApp *{ font-family:'Noto Sans TC','Noto Sans JP','Noto Sans KR','Outfit',
  -apple-system,'Segoe UI',sans-serif; }
h1,h2,h3{ letter-spacing:.01em; }
#MainMenu, footer{ visibility:hidden; }
[data-testid="stHeader"]{ background:transparent !important; }
.block-container{ padding-top:1.2rem !important; max-width:1200px; }

[data-testid="stSidebar"]{
  background:linear-gradient(180deg, rgba(20,25,42,.92), rgba(10,13,22,.96)) !important;
  border-right:1px solid var(--border);
  backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);}
[data-testid="stSidebar"] hr{ border-color:var(--border) !important; }
[data-testid="stSidebar"] .stButton>button{
  background:transparent !important; border:1px solid transparent !important;
  box-shadow:none !important; justify-content:flex-start; width:100%;}
[data-testid="stSidebar"] .stButton>button:hover{
  background:var(--surface2) !important; border-color:var(--border2) !important;
  transform:none; box-shadow:none !important;}

.stButton>button{
  border-radius:13px !important; border:1px solid var(--border2) !important;
  background:linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03)) !important;
  color:var(--text) !important; font-weight:800; padding:.5rem 1.05rem;
  transition:transform .16s ease, box-shadow .16s ease, border-color .16s ease, filter .16s ease;
  box-shadow:0 4px 14px rgba(0,0,0,.35);}
.stButton>button:hover{
  transform:translateY(-2px); border-color:rgba(124,92,255,.55) !important;
  box-shadow:0 10px 24px rgba(124,92,255,.28) !important; filter:brightness(1.08);}
.stButton>button:active{ transform:translateY(0) scale(.98); }
.stButton>button[kind="primary"], [data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,#ff4d6d 0%,#c9184a 100%) !important;
  border:1px solid rgba(255,255,255,.25) !important;
  box-shadow:0 8px 22px rgba(255,77,109,.35) !important;}
p, li{ color:var(--text); }
hr{ border-color:var(--border) !important; }
code{ background:rgba(124,92,255,.14) !important; color:#c9b8ff !important;
  border-radius:6px !important; padding:1px 6px !important; }

[data-testid="stTextInput"] input{
  background:rgba(255,255,255,.05) !important; border:1px solid var(--border) !important;
  border-radius:12px !important; color:var(--text) !important;}
[data-testid="stTextInput"] input:focus{
  border-color:var(--accent1) !important; box-shadow:0 0 0 3px rgba(124,92,255,.22) !important;}
[data-baseweb="select"] > div{
  background:rgba(255,255,255,.05) !important; border-color:var(--border) !important;
  border-radius:12px !important;}

[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button{
  border-radius:999px !important; background:rgba(255,255,255,.05) !important;
  border:1px solid var(--border) !important; color:var(--text) !important;
  font-weight:700; transition:all .15s ease;}
[data-testid="stPills"] button:hover, [data-testid="stSegmentedControl"] button:hover{
  border-color:rgba(34,211,238,.5) !important; transform:translateY(-1px);}
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[data-selected="true"],
[data-testid="stPills"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"]{
  background:linear-gradient(135deg,var(--accent1),var(--accent2)) !important;
  color:#0a0d16 !important; border-color:transparent !important;
  box-shadow:0 4px 16px rgba(124,92,255,.4);}

[data-testid="stExpander"]{
  border:1px solid var(--border) !important; border-radius:var(--radius) !important;
  background:var(--surface) !important;}
[data-testid="stExpander"] summary{ font-weight:800; }
[data-testid="stAlert"]{ border-radius:14px !important; border:1px solid var(--border);}
[data-testid="stVerticalBlockBorderWrapper"]{ border-radius:var(--radius) !important;}

.neon-band{
  background:
    radial-gradient(560px 260px at 82% -8%, rgba(34,211,238,.13), transparent 60%),
    radial-gradient(520px 260px at 12% 0%, rgba(124,92,255,.16), transparent 58%),
    linear-gradient(180deg,#141a2c 0%, #0b0e16 100%);
  border:1px solid #2a3150; border-radius:26px; padding:34px 20px 26px; margin-bottom:8px;}
.neon-title{
  font-weight:900; font-size:clamp(2rem, 5.6vw, 3.4rem); line-height:1.1; text-align:center;
  background:linear-gradient(100deg,#ffffff 8%, #ffd23f 34%, #ff4d6d 58%, #7c5cff 88%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter:drop-shadow(0 8px 30px rgba(255,77,109,.22)); letter-spacing:.02em;}
.neon-sub{ text-align:center; color:#dfe6ff; font-size:1.1rem; font-weight:700; margin-top:12px;}
.neon-tag{ text-align:center; color:var(--muted); font-size:.94rem; margin-top:8px; }
.badge-row{ text-align:center; margin-top:16px; }

.hk-badge{ display:inline-flex; align-items:center; gap:6px;
  background:var(--surface2); border:1px solid var(--border2); color:#e9edfb;
  border-radius:999px; padding:6px 16px; font-size:.84rem; font-weight:700;}
.feature-row{ text-align:center; margin-top:16px; }
.feature-chip{ display:inline-flex; align-items:center; gap:6px;
  background:var(--surface); border:1px solid var(--border); color:#dfe4f5;
  border-radius:14px; padding:10px 16px; margin:4px; font-size:.88rem; font-weight:600;
  transition:transform .15s ease, border-color .15s ease;}
.feature-chip:hover{ transform:translateY(-2px); border-color:rgba(34,211,238,.45);}

.street-sign{ display:inline-flex; align-items:center; gap:9px;
  background:linear-gradient(90deg, rgba(124,92,255,.16), rgba(34,211,238,.08));
  border:1px solid rgba(124,92,255,.45); color:var(--text);
  padding:.42em 1.15em; border-radius:999px;
  font-weight:900; letter-spacing:.1em; font-size:1.02rem;
  box-shadow:0 4px 20px rgba(124,92,255,.18);}
.street-sign::before{ content:''; width:9px; height:9px; border-radius:50%;
  background:var(--accent2); box-shadow:0 0 12px var(--accent2);}

.hkcard{ position:relative; width:292px; margin:0 auto; border-radius:18px; padding:9px;
  background:linear-gradient(155deg,var(--c1) 0%,var(--c2) 100%); color:#1c1710;
  box-shadow:0 16px 34px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.5);
  border:1.5px solid rgba(255,255,255,.8);}
.hkcard .hkinner{ background:linear-gradient(180deg,#fffefa 0%,#faf4e4 100%);
  border-radius:12px; padding:9px 9px 8px;}
.hkcard-top{ display:flex; align-items:baseline; gap:6px; margin-bottom:6px;}
.hkcard-name{ font-weight:900; font-size:1rem; flex:1; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis;}
.hkcard-hp{ font-weight:900; color:#d43a2f; font-size:.9rem; white-space:nowrap;}
.hkcard-art{ position:relative; height:150px; border-radius:11px;
  background:radial-gradient(circle at 50% 38%, var(--c2), var(--c1) 80%);
  display:flex; align-items:center; justify-content:center; overflow:hidden;
  border:2px solid rgba(255,255,255,.75); box-shadow:inset 0 0 24px rgba(0,0,0,.18);}
.hkcard-emoji{ font-size:4.6rem; filter:drop-shadow(0 7px 9px rgba(0,0,0,.38)); z-index:2;}
.hkcard-rare{ position:absolute; top:5px; right:8px; font-size:1rem; z-index:3;
  text-shadow:0 0 6px #fff, 0 0 14px #ffd23f;}
.hkcard.rare2 .hkcard-art::after{ content:''; position:absolute; inset:0; z-index:1;
  background:linear-gradient(115deg,transparent 32%,rgba(255,255,255,.8) 46%,rgba(255,255,255,0) 60%);
  transform:translateX(-130%); animation:holoshine 3s infinite;}
@keyframes holoshine{ 0%{transform:translateX(-130%);} 55%,100%{transform:translateX(130%);} }
.hkmove{ display:flex; justify-content:space-between; align-items:baseline; gap:8px;
  padding:4px 8px; margin:4px 0 0; background:rgba(255,255,255,.85);
  border:1px solid #e6dcc0; border-radius:8px; font-size:.78rem; font-weight:700;}
.hkmove .mno{ color:#8a7a52; font-weight:600; margin-right:4px; }
.hkmove-dmg{ color:#d43a2f; font-weight:900; white-space:nowrap;}
.hkcard-foot{ display:flex; justify-content:space-between; gap:6px; font-size:.66rem;
  color:#6b5f45; margin-top:5px; padding:0 2px; font-weight:700;}
.hkcard-flavor{ font-size:.68rem; color:#7a6f57; margin-top:4px; line-height:1.35;
  border-top:1px dashed #ddd0ac; padding-top:4px; min-height:2.5em;}
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

.hpwrap{ width:292px; margin:8px auto 0; }
.hpwrap.small{ width:216px; }
.hpbar{ height:13px; border-radius:8px; background:#262b3a; border:1.5px solid rgba(0,0,0,.45);
  overflow:hidden; }
.hpfill{ height:100%; border-radius:8px; transition:width .5s ease, background .5s ease;
  background:linear-gradient(90deg,#2fbf68,#3ecf6e); }
.hplbl{ font-size:.72rem; color:#dfe4f2; display:flex; justify-content:space-between;
  margin-top:3px; font-weight:800; }
.stchip{ display:inline-block; padding:2px 9px; border-radius:999px; font-size:.68rem;
  font-weight:800; margin:3px 4px 0 0; border:1.5px solid rgba(255,255,255,.3);}
.chip-burn{ background:#5a1d0e; color:#ffb38a; }
.chip-para{ background:#4a4410; color:#ffef9e; }
.chip-buff{ background:#123f2a; color:#9ff0c0; }
.chip-shield{ background:#153450; color:#a8d8ff; }
.benchchip{ display:inline-flex; align-items:center; gap:5px; background:var(--surface2);
  border:1.5px solid #3a4055; padding:3px 9px; border-radius:999px; font-size:.72rem;
  color:#e8ecf8; margin:3px 4px 0 0; font-weight:600;}
.benchchip.dead{ opacity:.38; text-decoration:line-through; }
.vs-badge{ font-size:2rem; text-align:center; font-weight:900; color:#ffd23f;
  text-shadow:0 0 14px #ff8800; }
.stage-dot{ display:inline-block; width:13px; height:13px; border-radius:50%;
  border:2px solid #ffd23f; margin:0 4px; }
.stage-dot.done{ background:#3ecf6e; border-color:#3ecf6e; }
.stage-dot.now{ background:#ffd23f; box-shadow:0 0 10px #ffd23f; }

.tchart{ border-collapse:separate; border-spacing:0; margin:10px auto; border-radius:12px;
  overflow:hidden; border:1px solid #3a4055;}
.tchart th, .tchart td{ border-bottom:1px solid #3a4055; border-right:1px solid #3a4055;
  padding:6px 10px; text-align:center; font-size:.82rem; background:rgba(255,255,255,.02);}
.tchart th{ background:#1c2237; color:#ffe9a8; font-weight:800;}
.tchart td.rowhead{ background:#1c2237; font-weight:800;}
.tchart .x15{ background:rgba(30,132,73,.25); color:#7ef0a2; font-weight:900;}
.tchart .x075{ background:rgba(192,57,43,.22); color:#ff9f9f; font-weight:900;}
.tchart .x10{ color:#8a93b5; }

.credit{ text-align:center; color:var(--muted); font-size:.75rem; margin-top:18px; line-height:1.7;}
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

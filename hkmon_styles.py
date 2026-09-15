# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — CSS + card HTML renderer (Pokémon-TCG-style layout)."""

import hkmon_data as D
import hkmon_i18n as I18N

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Sans+JP:wght@400;700&family=Noto+Sans+KR:wght@400;700&family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&display=swap');

:root{
  --bg:#05070d; --neon-c:#00f0ff; --neon-m:#ff2bd6; --neon-p:#8b5cff; --neon-g:#39ff14;
  --surface:rgba(10,16,30,.55); --border:rgba(0,240,255,.22); --border2:rgba(255,43,214,.35);
  --text:#d9fbff; --muted:#6f8fa3; --radius:4px;
  --hud:'Share Tech Mono',monospace; --disp:'Orbitron','Noto Sans TC',sans-serif;
}

.stApp{
  background:
    radial-gradient(1000px 700px at 85% -10%, rgba(139,92,255,.13), transparent 60%),
    radial-gradient(900px 600px at 0% 110%, rgba(0,240,255,.08), transparent 55%),
    linear-gradient(180deg,#070a12 0%, #05070d 100%) !important;
  color:var(--text);
}
.stApp::before{
  content:''; position:fixed; inset:0; pointer-events:none; z-index:1;
  background:repeating-linear-gradient(0deg, rgba(0,240,255,.028) 0 1px, transparent 1px 3px);
  mix-blend-mode:screen;}
.stApp::after{
  content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
  background:
    linear-gradient(rgba(0,240,255,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,240,255,.05) 1px, transparent 1px);
  background-size:44px 44px;
  -webkit-mask-image:linear-gradient(180deg, rgba(0,0,0,.5), transparent 40%);
  mask-image:linear-gradient(180deg, rgba(0,0,0,.5), transparent 40%);}
.stApp, .stApp *{ font-family:'Noto Sans TC','Noto Sans JP','Noto Sans KR',
  -apple-system,'Segoe UI',sans-serif; }
h1,h2,h3{ letter-spacing:.04em; }
.block-container{ padding-top:1.2rem !important; max-width:1200px; position:relative; z-index:2;}
[data-testid="stHeader"]{ background:rgba(5,7,13,.75) !important;
  backdrop-filter:blur(10px); border-bottom:1px solid rgba(0,240,255,.15);}

[data-testid="stSidebar"]{
  background:linear-gradient(180deg, rgba(7,11,22,.97), rgba(5,7,13,.99)) !important;
  border-right:1px solid var(--border) !important;
  box-shadow:4px 0 24px rgba(0,240,255,.06);}
[data-testid="stSidebar"] hr{ border-color:rgba(0,240,255,.14) !important; }
[data-testid="stSidebar"] .stButton>button{
  background:transparent !important; border:1px solid transparent !important;
  box-shadow:none !important; color:var(--muted) !important; width:100%;
  font-family:var(--hud); letter-spacing:.06em;}
[data-testid="stSidebar"] .stButton>button:hover{
  color:var(--neon-c) !important; border-color:var(--border) !important;
  background:rgba(0,240,255,.05) !important; transform:none; box-shadow:none !important;
  text-shadow:0 0 8px rgba(0,240,255,.7);}

.stButton>button{
  border-radius:2px !important; border:1px solid var(--border) !important;
  background:linear-gradient(180deg, rgba(0,240,255,.07), rgba(0,0,0,.3)) !important;
  color:var(--text) !important; font-weight:800; padding:.5rem 1.05rem;
  transition:all .16s ease;
  clip-path:polygon(10px 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,0 100%,0 10px);}
.stButton>button:hover{
  border-color:var(--neon-c) !important; color:#fff !important;
  box-shadow:0 0 18px rgba(0,240,255,.35), inset 0 0 14px rgba(0,240,255,.08) !important;
  text-shadow:0 0 8px rgba(0,240,255,.8);}
.stButton>button[kind="primary"], [data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg, rgba(255,43,214,.25), rgba(255,43,214,.08)) !important;
  border:1px solid var(--neon-m) !important; color:#ffd9f6 !important;
  box-shadow:0 0 18px rgba(255,43,214,.3), inset 0 0 12px rgba(255,43,214,.1) !important;}
.stButton>button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover{
  box-shadow:0 0 26px rgba(255,43,214,.55), inset 0 0 16px rgba(255,43,214,.18) !important;}
p, li{ color:var(--text); }
hr{ border-color:rgba(0,240,255,.14) !important; }
code{ background:rgba(0,240,255,.1) !important; color:var(--neon-c) !important;
  border-radius:2px !important; padding:1px 6px !important; font-family:var(--hud);}

[data-testid="stTextInput"] input{
  background:rgba(0,20,30,.5) !important; border:1px solid var(--border) !important;
  border-radius:2px !important; color:var(--neon-c) !important; font-family:var(--hud);
  letter-spacing:.05em;}
[data-testid="stTextInput"] input:focus{
  border-color:var(--neon-c) !important; box-shadow:0 0 0 3px rgba(0,240,255,.18),
  inset 0 0 12px rgba(0,240,255,.06) !important;}
[data-baseweb="select"] > div{
  background:rgba(0,20,30,.5) !important; border-color:var(--border) !important;
  border-radius:2px !important; color:var(--text) !important;}

[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button{
  border-radius:2px !important; background:rgba(0,20,30,.4) !important;
  border:1px solid var(--border) !important; color:var(--muted) !important;
  font-weight:800; transition:all .15s ease; letter-spacing:.04em;}
[data-testid="stPills"] button:hover, [data-testid="stSegmentedControl"] button:hover{
  border-color:var(--neon-c) !important; color:var(--neon-c) !important;
  box-shadow:0 0 12px rgba(0,240,255,.25);}
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[data-selected="true"],
[data-testid="stPills"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"]{
  background:linear-gradient(135deg, rgba(0,240,255,.22), rgba(139,92,255,.22)) !important;
  color:#fff !important; border-color:var(--neon-c) !important;
  box-shadow:0 0 16px rgba(0,240,255,.35), inset 0 0 10px rgba(0,240,255,.12) !important;
  text-shadow:0 0 6px rgba(0,240,255,.9);}

[data-testid="stExpander"]{
  border:1px solid var(--border) !important; border-radius:2px !important;
  background:rgba(6,10,20,.6) !important;}
[data-testid="stExpander"] summary{ font-weight:800; color:var(--neon-c); }
[data-testid="stAlert"]{ border-radius:2px !important; border:1px solid var(--border);
  background:rgba(0,20,30,.55) !important;}
[data-testid="stVerticalBlockBorderWrapper"]{ border-radius:2px !important;
  border-color:var(--border) !important;}

.neon-band{
  position:relative; border-radius:4px; padding:36px 20px 28px;
  background:linear-gradient(180deg, rgba(0,240,255,.05), rgba(5,7,13,.4) 55%),
    linear-gradient(180deg,#0a1020 0%, #05070d 100%);
  border:1px solid rgba(0,240,255,.3);
  box-shadow:0 0 30px rgba(0,240,255,.12), inset 0 0 40px rgba(0,240,255,.05);}
.neon-band::before, .neon-band::after{
  content:''; position:absolute; width:26px; height:26px; border:2px solid var(--neon-c);}
.neon-band::before{ top:-2px; left:-2px; border-right:none; border-bottom:none;}
.neon-band::after{ bottom:-2px; right:-2px; border-left:none; border-top:none;}
.neon-title{
  font-family:var(--disp); font-weight:900;
  font-size:clamp(1.9rem, 5.4vw, 3.3rem); line-height:1.12; text-align:center;
  color:#fff;
  text-shadow:0 0 6px rgba(0,240,255,.8), 0 0 22px rgba(0,240,255,.45),
              0 0 44px rgba(255,43,214,.35);}
.neon-sub{ text-align:center; color:#e8fbff; font-size:1.08rem; font-weight:700; margin-top:12px;
  text-shadow:0 0 10px rgba(0,240,255,.5);}
.neon-tag{ text-align:center; color:var(--muted); font-size:.9rem; margin-top:8px;
  font-family:var(--hud); letter-spacing:.12em;}
.badge-row{ text-align:center; margin-top:16px; }

.hk-badge{ display:inline-flex; align-items:center; gap:6px;
  background:rgba(0,20,30,.5); border:1px solid var(--border); color:var(--neon-c);
  border-radius:2px; padding:5px 14px; font-size:.8rem; font-weight:700;
  font-family:var(--hud); letter-spacing:.08em;
  clip-path:polygon(8px 0,100% 0,100% calc(100% - 8px),calc(100% - 8px) 100%,0 100%,0 8px);}
.feature-row{ text-align:center; margin-top:16px; }
.feature-chip{ display:inline-flex; align-items:center; gap:6px;
  background:rgba(0,16,26,.55); border:1px solid var(--border); color:var(--text);
  border-radius:2px; padding:9px 15px; margin:4px; font-size:.86rem; font-weight:600;
  transition:all .15s ease;}
.feature-chip:hover{ border-color:var(--neon-m); color:#ffd9f6;
  box-shadow:0 0 14px rgba(255,43,214,.3);}

.street-sign{ display:inline-flex; align-items:center; gap:10px;
  background:linear-gradient(90deg, rgba(0,240,255,.1), transparent);
  border-left:3px solid var(--neon-c); color:var(--neon-c);
  padding:.4em 1.1em; border-radius:0;
  font-family:var(--disp); font-weight:800; letter-spacing:.16em; font-size:1rem;
  text-shadow:0 0 10px rgba(0,240,255,.7);}
.street-sign::before{ content:'\25B8'; color:var(--neon-m); text-shadow:0 0 8px var(--neon-m);}

.hkcard{ position:relative; width:292px; margin:0 auto; border-radius:18px; padding:9px;
  background:linear-gradient(155deg,var(--c1) 0%,var(--c2) 100%); color:#1c1710;
  box-shadow:0 16px 34px rgba(0,0,0,.5), 0 0 26px color-mix(in srgb, var(--c1) 32%, transparent),
  inset 0 1px 0 rgba(255,255,255,.5);
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
  color:#fff; text-shadow:0 0 6px #fff, 0 0 14px #ffd23f, 0 2px 3px rgba(0,0,0,.4);}
.hkcard.rare2 .hkcard-art::after{ content:''; position:absolute; inset:0; z-index:1;
  background:linear-gradient(115deg,transparent 32%,rgba(255,255,255,.8) 46%,rgba(255,43,214,.3) 52%,rgba(255,255,255,0) 62%);
  transform:translateX(-130%); animation:holoshine 3s infinite;}
@keyframes holoshine{ 0%{transform:translateX(-130%);} 55%,100%{transform:translateX(130%);} }
.hkmove{ display:flex; justify-content:space-between; align-items:baseline; gap:8px;
  padding:4px 8px; margin:4px 0 0; background:rgba(255,255,255,.88);
  border:1px solid #e6dcc0; border-radius:8px; font-size:.78rem; font-weight:700;
  color:#3a2c14;}
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
.hpbar{ height:12px; border-radius:2px; background:#0a1420; border:1px solid rgba(0,240,255,.3);
  overflow:hidden; }
.hpfill{ height:100%; transition:width .5s ease, background .5s ease;
  background:linear-gradient(90deg,#0aff9d,#00f0ff);
  box-shadow:0 0 10px rgba(0,240,255,.6);}
.hplbl{ font-size:.72rem; color:#9fe8ff; display:flex; justify-content:space-between;
  margin-top:3px; font-weight:800; font-family:var(--hud);}
.stchip{ display:inline-block; padding:2px 9px; border-radius:2px; font-size:.66rem;
  font-weight:800; margin:3px 4px 0 0; border:1px solid var(--neon-m); color:#ffd9f6;
  font-family:var(--hud); background:rgba(255,43,214,.08);}
.chip-buff{ border-color:#39ff14; color:#b6ffb0; background:rgba(57,255,20,.07);}
.chip-shield{ border-color:var(--neon-c); color:#9fe8ff; background:rgba(0,240,255,.07);}
.benchchip{ display:inline-flex; align-items:center; gap:5px; background:rgba(0,16,26,.6);
  border:1px solid var(--border); padding:3px 9px; border-radius:2px; font-size:.72rem;
  color:#cfe8ff; margin:3px 4px 0 0; font-weight:600; font-family:var(--hud);}
.benchchip.dead{ opacity:.35; text-decoration:line-through; }
.vs-badge{ font-family:var(--disp); font-size:1.8rem; text-align:center; font-weight:900;
  color:#fff; text-shadow:0 0 8px var(--neon-m), 0 0 26px var(--neon-c); }
.stage-dot{ display:inline-block; width:12px; height:12px; border-radius:2px;
  border:1.5px solid var(--neon-c); margin:0 4px; transform:rotate(45deg);}
.stage-dot.done{ background:#39ff14; border-color:#39ff14; box-shadow:0 0 8px #39ff14;}
.stage-dot.now{ background:var(--neon-c); box-shadow:0 0 10px var(--neon-c);}

.tchart{ border-collapse:collapse; margin:10px auto; border:1px solid rgba(0,240,255,.3);}
.tchart th, .tchart td{ border:1px solid rgba(0,240,255,.16); padding:6px 10px;
  text-align:center; font-size:.82rem; background:rgba(0,10,20,.5); font-family:var(--hud);}
.tchart th{ background:rgba(0,240,255,.1); color:var(--neon-c);}
.tchart td.rowhead{ background:rgba(0,240,255,.08); font-weight:800;}
.tchart .x15{ color:#39ff14; font-weight:900;}
.tchart .x075{ color:#ff2bd6; font-weight:900;}
.tchart .x10{ color:var(--muted); }

.credit{ text-align:center; color:var(--muted); font-size:.74rem; margin-top:18px;
  line-height:1.7; font-family:var(--hud); letter-spacing:.05em;}

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

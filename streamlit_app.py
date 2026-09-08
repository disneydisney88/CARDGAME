# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — Pokémon-style card game with Hong Kong flavour.

60 original cards (zh-HK / EN / JA / KO), turn-based battles vs AI,
8-bit sound effects. 100% free, no ads. Run: streamlit run streamlit_app.py
"""
import random

import streamlit as st

import hkmon_data as D
import hkmon_i18n as I18N
import hkmon_engine as E
import hkmon_sfx as SFX
import hkmon_styles as STY
from hkmon_i18n import t

st.set_page_config(page_title="HK-MON 港精靈 Card Game", page_icon="🀄", layout="wide")

PAGES = ["home", "deck", "battle", "library", "help"]
LANG_BY_LABEL = {label: code for code, label in I18N.LANGS}


# ----------------------------------------------------------------- state ----
def _init_state():
    defaults = {
        "lang": "zh", "sound": True, "page": "home",
        "deck_id": "d1", "diff": "normal", "mode": "quick",
        "battle": None, "wins": 0, "losses": 0, "streak": 0,
        "ui_sfx": [], "surrender_arm": False,
        "featured": random.sample(D.MONSTERS, 3),
        "lib_types": [], "lib_rarity": "all", "lib_q": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


_init_state()


def lang():
    return st.session_state.lang


def ui_sfx(name):
    st.session_state.ui_sfx.append(name)


def go(page):
    st.session_state.page = page
    st.session_state.surrender_arm = False


def _score():
    b = st.session_state.battle
    if b and b["over"] and not b.get("scored"):
        if b["win"]:
            st.session_state.wins += 1
            st.session_state.streak += 1
        else:
            st.session_state.losses += 1
            st.session_state.streak = 0
        b["scored"] = True


# ------------------------------------------------------------- callbacks ----
def cb_nav():
    st.session_state.page = st.session_state.nav
    st.session_state.surrender_arm = False
    ui_sfx("click")


def cb_lang():
    st.session_state.lang = LANG_BY_LABEL.get(st.session_state.lang_box, "zh")


def cb_start_battle():
    st.session_state.battle = E.start_battle(
        st.session_state.lang, st.session_state.deck_id,
        st.session_state.diff, st.session_state.mode)
    st.session_state.page = "battle"
    ui_sfx("switch")


def cb_action(kind, arg=None):
    b = st.session_state.battle
    if b is None or b["over"]:
        return
    E.player_action(b, kind, arg)
    _score()


def cb_surrender():
    st.session_state.surrender_arm = True


def cb_surrender_yes():
    b = st.session_state.battle
    if b and not b["over"]:
        b["over"] = True
        b["win"] = False
        b["pending"] = None
        b["sfx"].append("lose")
        b["log"].append(t(b["lang"], "m_lose"))
        _score()
    st.session_state.surrender_arm = False


def cb_next_stage():
    b = st.session_state.battle
    if b and b["win"] and b["mode"] == "gauntlet" and b["stage"] < 3:
        carried_log = b["log"]
        st.session_state.battle = E.next_stage_state(b)
        st.session_state.battle["log"] = carried_log + st.session_state.battle["log"]
    ui_sfx("switch")


def cb_rematch():
    b = st.session_state.battle or {}
    st.session_state.battle = E.start_battle(
        st.session_state.lang, st.session_state.deck_id,
        st.session_state.diff, b.get("mode", "quick"), stage=1)
    st.session_state.page = "battle"
    ui_sfx("switch")


def cb_home():
    go("home")
    ui_sfx("click")


# ---------------------------------------------------------------- sidebar ---
with st.sidebar:
    st.markdown(
        f'<div style="text-align:center;font-weight:900;font-size:1.3rem;'
        f'color:#ffd23f;text-shadow:0 0 12px #ff8800;">🀄 {t(lang(),"app_title")}</div>',
        unsafe_allow_html=True)
    st.caption(t(lang(), "tagline"))

    st.selectbox("🌐", options=[lb for _, lb in I18N.LANGS],
                 index=[c for c, _ in I18N.LANGS].index(st.session_state.lang),
                 key="lang_box", on_change=cb_lang)
    st.session_state.lang = LANG_BY_LABEL.get(st.session_state.lang_box, st.session_state.lang)

    st.toggle(t(lang(), "sound_label"), key="sound")

    if st.button(t(lang(), "sound_test")):
        if st.session_state.sound:
            SFX.play("win")

    st.divider()
    labels = {"home": t(lang(), "nav_home"), "deck": t(lang(), "nav_deck"),
              "library": t(lang(), "nav_lib"), "help": t(lang(), "nav_help")}
    nav_opts = ["home", "deck", "library", "help"]
    b_now = st.session_state.battle
    if b_now is not None and not b_now.get("over") and st.session_state.page == "battle":
        nav_opts.insert(1, "battle")
        labels["battle"] = t(lang(), "nav_battle_active")
    nav_choice = st.radio("nav", options=nav_opts,
                          index=nav_opts.index(st.session_state.page)
                          if st.session_state.page in nav_opts else 0,
                          format_func=lambda p: labels.get(p, p),
                          label_visibility="collapsed")
    if nav_choice != st.session_state.page:
        st.session_state.page = nav_choice
        st.session_state.surrender_arm = False
        ui_sfx("click")
        st.rerun()

    st.divider()
    w, l, s = st.session_state.wins, st.session_state.losses, st.session_state.streak
    st.markdown(f"**{t(lang(),'record')}**　`{w} {t(lang(),'wins')} · {l} {t(lang(),'losses')}`"
                f"　🔥 {s} {t(lang(),'streak')}")

    if st.button(t(lang(), "reset")):
        st.session_state.battle = None
        go("home")
        st.rerun()

    st.divider()
    st.caption(t(lang(), "credits"))

STY.inject_css()

# ------------------------------------------------------------------ home ----
if st.session_state.page == "home":
    st.markdown(
        f'''<div class="neon-band">
        <div class="badge-row"><span class="hk-badge">{t(lang(),"hero_badge")}</span></div>
        <div class="neon-title">{t(lang(),"hero_title")}</div>
        <div class="neon-sub">{t(lang(),"hero_sub")}</div>
        <div class="neon-tag">{t(lang(),"tagline")}</div>
        <div class="badge-row">
          <span class="hk-badge">♻️ FREE</span>
          <span class="hk-badge">🔊 8-BIT SFX</span>
          <span class="hk-badge">🈯 繁中 / EN / 日本語 / 한국어</span>
          <span class="hk-badge">🀄 60 CARDS</span>
        </div></div>''', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    if c1.button(t(lang(), "cta_start"), type="primary"):
        go("deck")
        st.rerun()
    if c2.button(t(lang(), "cta_lib")):
        go("library")
        st.rerun()
    if c3.button(t(lang(), "cta_help")):
        go("help")
        st.rerun()

    st.markdown(f'<div class="feature-row">'
                f'<span class="feature-chip">{t(lang(),"feat1")}</span>'
                f'<span class="feature-chip">{t(lang(),"feat2")}</span>'
                f'<span class="feature-chip">{t(lang(),"feat3")}</span>'
                f'<span class="feature-chip">{t(lang(),"feat4")}</span></div>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span class="street-sign">{t(lang(),"featured")}</span>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    for col, card in zip((fc1, fc2, fc3), st.session_state.featured):
        with col:
            st.markdown(STY.card_html(card, lang()), unsafe_allow_html=True)

    st.markdown(f'<div class="credit">{t(lang(),"credits")}<br>{t(lang(),"notaffiliated")}</div>',
                unsafe_allow_html=True)

# ------------------------------------------------------------------ deck ----
elif st.session_state.page == "deck":
    st.markdown(f'<span class="street-sign">{t(lang(),"deck_title")}</span>', unsafe_allow_html=True)
    st.caption(t(lang(), "deck_sub"))

    st.markdown(f"**{t(lang(),'mode_title')}**")
    msel = st.segmented_control("mode", ["quick", "gauntlet"],
                                format_func=lambda m: t(lang(), "mode_quick" if m == "quick" else "mode_gauntlet"),
                                selection_mode="single", default=st.session_state.mode, key="mode_sel")
    if msel:
        st.session_state.mode = msel[0] if isinstance(msel, list) else msel

    st.markdown(f"**{t(lang(),'diff_title')}**")
    dsel = st.segmented_control("diff", ["easy", "normal", "hard"],
                                format_func=lambda d: t(lang(), f"diff_{d}"),
                                selection_mode="single", default=st.session_state.diff, key="diff_sel")
    if dsel:
        st.session_state.diff = dsel[0] if isinstance(dsel, list) else dsel

    deck_ids = [d["id"] for d in D.CHOOSABLE_DECKS]
    psel = st.pills("deck", deck_ids,
                    format_func=lambda did: f'{D.DECK[did]["emoji"]} {D.DECK[did]["name"][lang()]}',
                    selection_mode="single", default=st.session_state.deck_id, key="deck_pills")
    if psel:
        st.session_state.deck_id = psel[0] if isinstance(psel, list) else psel

    deck = D.DECK[st.session_state.deck_id]
    mons = deck["mons"] if not deck.get("random") else random.sample([m["id"] for m in D.MONSTERS], 5)
    items = deck["items"] if not deck.get("random") else random.sample([i["id"] for i in D.ITEMS], 3)
    cols = st.columns(8)
    for col, mid in zip(cols[:5], mons):
        with col:
            st.markdown(STY.card_html(D.MON[mid], lang(), small=True), unsafe_allow_html=True)
    for col, iid in zip(cols[5:], items):
        with col:
            st.markdown(STY.card_html(D.ITEM[iid], lang(), small=True), unsafe_allow_html=True)
    if deck.get("random"):
        st.caption("🎲 " + deck["desc"][lang()])

    if st.button(f"⚔️ {t(lang(),'start')}", type="primary"):
        cb_start_battle()
        st.rerun()

# ---------------------------------------------------------------- battle ----
elif st.session_state.page == "battle":
    b = st.session_state.battle
    if b is None:
        st.session_state.page = "deck"
        st.rerun()

    L = b["lang"]
    p = E.active(b, "p")
    e = E.active(b, "e")
    pcard, ecard = D.MON[p["id"]], D.MON[e["id"]]
    hit = b.get("hit")

    # header: stage dots / turn / surrender
    h1, h2, h3 = st.columns([1.1, 1.2, 0.7])
    with h1:
        if b["mode"] == "gauntlet":
            dots = ""
            for s in (1, 2, 3):
                cls = "done" if s < b["stage"] else ("now" if s == b["stage"] else "")
                dots += f'<span class="stage-dot {cls}"></span>'
            st.markdown(dots + f' <b>{t(L,"stage",n=b["stage"])}</b>', unsafe_allow_html=True)
    with h2:
        st.markdown(f"<div style='text-align:center'><b>{t(L,'turn')} {b['turn']}</b></div>",
                    unsafe_allow_html=True)
    with h3:
        if not b["over"] and not b["pending"]:
            if st.button(t(L, "surrender")):
                cb_surrender()
                st.rerun()
    if st.session_state.surrender_arm and not b["over"]:
        st.warning(t(L, "surrender_again"))
        if st.button("⚠️ " + t(L, "surrender")):
            cb_surrender_yes()
            st.rerun()

    if b["over"]:
        # ---------------- result ----------------
        st.markdown("---")
        if b["win"]:
            st.markdown(f"<h1 style='text-align:center;color:#ffd23f;"
                        f"text-shadow:0 0 22px #ff8800;'>{t(L,'result_title_win')}</h1>",
                        unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:1.1rem;'>{t(L,'m_win')}</p>",
                        unsafe_allow_html=True)
            st.balloons()
        else:
            st.markdown(f"<h1 style='text-align:center;color:#8a93b5;'>{t(L,'result_title_lose')}</h1>",
                        unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:1.1rem;'>{t(L,'m_lose')}</p>",
                        unsafe_allow_html=True)
            st.snow()
        r1, r2, r3 = st.columns(3)
        if b["mode"] == "gauntlet" and b["win"] and b["stage"] < 3:
            if r1.button(t(L, "btn_next"), type="primary"):
                cb_next_stage()
                st.rerun()
        if b["mode"] == "gauntlet" and b["win"] and b["stage"] == 3:
            st.markdown(f"<h2 style='text-align:center;'>🏆 {t(L,'m_champion')}</h2>",
                        unsafe_allow_html=True)
        if r2.button(t(L, "btn_rematch")):
            cb_rematch()
            st.rerun()
        if r3.button(t(L, "btn_home")):
            cb_home()
            st.rerun()
    else:
        # ---------------- board ----------------
        b1, bmid, b2 = st.columns([1.15, 0.5, 1.15])
        with b1:
            you = t(L, "you")
            st.markdown(f"<div style='text-align:center;font-weight:900;color:#7ef0a2;'>🟢 {you}</div>",
                        unsafe_allow_html=True)
            st.markdown(STY.card_html(pcard, L, shake=hit in ("p", "pe")), unsafe_allow_html=True)
            st.markdown(STY.hp_bar(p, L, pcard["name"][L]), unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center'><small>{t(L,'bench')}:</small><br>"
                        + STY.bench_chips_html(b["p"], b["pa"], L) + "</div>", unsafe_allow_html=True)
        with bmid:
            st.markdown(f'<div class="vs-badge" style="margin-top:90px;">VS</div>', unsafe_allow_html=True)
        with b2:
            foe = t(L, "enemy")
            deck_name = D.DECK[b["enemy_deck_id"]]["name"][L]
            st.markdown(f"<div style='text-align:center;font-weight:900;color:#ff9f9f;'>🔴 {foe} · {deck_name}</div>",
                        unsafe_allow_html=True)
            st.markdown(STY.card_html(ecard, L, shake=hit in ("e", "ep")), unsafe_allow_html=True)
            st.markdown(STY.hp_bar(e, L, ecard["name"][L]), unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center'><small>{t(L,'bench')}:</small><br>"
                        + STY.bench_chips_html(b["e"], b["ea"], L) + "</div>", unsafe_allow_html=True)

        # ---------------- actions ----------------
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            if b["pending"] == "switch":
                st.error(t(L, "replace_title"))
                cands = [i for i, f in enumerate(b["p"]) if f["hp"] > 0]
                opts = [f'{D.MON[b["p"][i]["id"]]["emoji"]} {D.MON[b["p"][i]["id"]]["name"][L]} '
                        f'({b["p"][i]["hp"]}/{b["p"][i]["mhp"]})' for i in cands]
                sel = st.radio("replace", opts, index=0, key="rep_sel", label_visibility="collapsed")
                idx = cands[opts.index(sel)] if sel in opts else cands[0]
                if st.button(f"✅ {t(L,'confirm')}", type="primary"):
                    cb_action("replace", idx)
                    st.rerun()
            else:
                m1 = D.MOVE1[pcard["type"]][b["p"].index(p)]
                m2 = pcard["move2"]
                mult1 = D.eff_mult(pcard["type"], ecard["type"])
                tag1 = " 🔥×1.5" if mult1 > 1 else (" 🛡×0.75" if mult1 < 1 else "")
                a1, a2, a3, a4 = st.columns([1.1, 1.1, 1, 1])
                if a1.button(f"⚔️ {t(L,'atk1')}: {m1['name'][L]} {m1['power']}{tag1}", type="primary"):
                    cb_action("move1")
                    st.rerun()
                cd = p["cd2"]
                if a2.button(f"🌟 {t(L,'atk2')}: {m2['name'][L]} {m2['power']}"
                             + (f"　⏳ {t(L,'cooldown',n=cd)}" if cd else ""), disabled=cd > 0):
                    cb_action("move2")
                    st.rerun()
                with a3.expander(t(L, "switch_panel")):
                    bench = [i for i, f in enumerate(b["p"]) if f["hp"] > 0 and i != b["pa"]]
                    if not bench:
                        st.caption(t(L, "empty_bench"))
                    else:
                        bopts = [f'{D.MON[b["p"][i]["id"]]["emoji"]} {D.MON[b["p"][i]["id"]]["name"][L]} '
                                 f'({b["p"][i]["hp"]}/{b["p"][i]["mhp"]})' for i in bench]
                        bsel = st.radio("switch_to", bopts, index=0, key="sw_sel",
                                        label_visibility="collapsed")
                        bidx = bench[bopts.index(bsel)] if bsel in bopts else bench[0]
                        if st.button(f"✅ {t(L, 'go_switch')}", key="sw_go"):
                            cb_action("switch", bidx)
                            st.rerun()
                with a4.expander(t(L, "items_panel")):
                    if not b["pitems"]:
                        st.caption(t(L, "empty_bench"))
                    else:
                        iopts = [f'{D.ITEM[iid]["emoji"]} {D.ITEM[iid]["name"][L]}' for iid in b["pitems"]]
                        isel = st.radio("item_sel", iopts, index=0, key="it_sel",
                                        label_visibility="collapsed")
                        iid = b["pitems"][iopts.index(isel)] if isel in iopts else b["pitems"][0]
                        if st.button(f"🎒 {t(L,'use')}", key="it_go"):
                            cb_action("item", iid)
                            st.rerun()

        # ---------------- log ----------------
        with st.expander(t(L, "battle_log"), expanded=True):
            for line in b["log"][-40:]:
                st.markdown(f"- {line}")

    # play queued battle sounds, then clear anim flags
    if st.session_state.sound:
        for sname in b["sfx"]:
            SFX.play(sname)
    b["sfx"] = []
    b["hit"] = None

# --------------------------------------------------------------- library ----
elif st.session_state.page == "library":
    st.markdown(f'<span class="street-sign">{t(lang(),"lib_title")}</span>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        sel_types = st.pills(t(lang(), "filter_type"),
                             [f'{D.TYPES[ty]["emoji"]} {D.TYPES[ty]["name"][lang()]}' for ty in D.TYPE_ORDER],
                             selection_mode="multi", key="lib_type_pills")
        type_by_label = {f'{D.TYPES[ty]["emoji"]} {D.TYPES[ty]["name"][lang()]}': ty for ty in D.TYPE_ORDER}
        st.session_state.lib_types = [type_by_label[x] for x in (sel_types or [])]
    with f2:
        rar_opts = ["all", "0", "1", "2"]
        rar_labels = {"all": "—", "0": t(lang(), "rarity0"), "1": t(lang(), "rarity1"), "2": t(lang(), "rarity2")}
        sel_rar = st.pills(t(lang(), "filter_rarity"), rar_opts,
                           format_func=lambda r: rar_labels[r],
                           selection_mode="single", default=st.session_state.lib_rarity,
                           key="lib_rar_pills")
        st.session_state.lib_rarity = (sel_rar[0] if isinstance(sel_rar, list) else sel_rar) or "all"
    with f3:
        st.session_state.lib_q = st.session_state.get("lib_q_input", "").strip()
        st.text_input(t(lang(), "search"), key="lib_q_input", placeholder=t(lang(), "search"))

    cards = D.all_cards()
    if st.session_state.lib_types:
        if st.session_state.lib_q:
            q = st.session_state.lib_q.lower()
            cards = [c for c in cards if c["type"] in st.session_state.lib_types
                     and any(q in c["name"][l].lower() for l in ("zh", "en", "ja", "ko"))]
        else:
            cards = [c for c in cards if c["type"] in st.session_state.lib_types]
    elif st.session_state.lib_q:
        q = st.session_state.lib_q.lower()
        cards = [c for c in cards if any(q in c["name"][l].lower() for l in ("zh", "en", "ja", "ko"))]
    if st.session_state.lib_rarity != "all":
        cards = [c for c in cards if str(c["rarity"]) == st.session_state.lib_rarity]

    st.caption(t(lang(), "lib_count", n=len(cards)))
    cols = st.columns(3)
    for i, card in enumerate(cards):
        with cols[i % 3]:
            st.markdown(STY.card_html(card, lang()), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------ help ----
elif st.session_state.page == "help":
    st.markdown(f'<span class="street-sign">{t(lang(),"rules_title")}</span>', unsafe_allow_html=True)
    for key in ("rule1", "rule2", "rule3", "rule4", "rule5", "rule6", "rule7", "rule8"):
        st.markdown(t(lang(), key))
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span class="street-sign">{t(lang(),"type_title")}</span>', unsafe_allow_html=True)
    st.markdown(STY.type_chart_html(lang()), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span class="street-sign">{t(lang(),"items_title")}</span>', unsafe_allow_html=True)
    icols = st.columns(4)
    for i, item in enumerate(D.ITEMS):
        with icols[i % 4]:
            st.markdown(STY.card_html(item, lang(), small=True), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span class="street-sign">{t(lang(),"tips_title")}</span>', unsafe_allow_html=True)
    st.info(t(lang(), "tips"))
    st.markdown(f'<div class="credit">{t(lang(),"credits")}<br>{t(lang(),"notaffiliated")}</div>',
                unsafe_allow_html=True)

# ------------------------------------------------------------------ sfx -----
for sname in st.session_state.ui_sfx:
    if st.session_state.sound:
        SFX.play(sname)
st.session_state.ui_sfx = []

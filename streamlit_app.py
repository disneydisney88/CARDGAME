# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — Pokémon-style card game with Hong Kong flavour.

60 original cards (zh-HK / EN / JA / KO), turn-based battles vs AI,
hotseat 2P + online room PvP, 8-bit sound effects, persistent scoreboard.
100% free, no ads. Run: streamlit run streamlit_app.py
"""
import random

import streamlit as st

import hkmon_accounts as ACC
import hkmon_arena as AR
import hkmon_boards as XB
import hkmon_data as D
import hkmon_i18n as I18N
import hkmon_engine as E
import hkmon_mahjong as MJ
import hkmon_rooms as R
import hkmon_scores as SCORES
import hkmon_sfx as SFX
import hkmon_styles as STY
import hkmon_table as TBL
import hkmon_xiangqi as XQ
from hkmon_i18n import t

st.set_page_config(page_title="HK-MON 港精靈 Card Game", page_icon="🀄", layout="wide")

PAGES = ["home", "deck", "pvp", "battle", "library", "help"]
LANG_BY_LABEL = {label: code for code, label in I18N.LANGS}


# ----------------------------------------------------------------- state ----
def _init_state():
    defaults = {
        "lang": "zh", "sound": True, "page": "home",
        "deck_id": "d1", "diff": "normal", "mode": "quick",
        "battle": None, "wins": 0, "losses": 0, "streak": 0,
        "ui_sfx": [], "surrender_arm": False,
        "featured": random.sample(D.MONSTERS, 3),
        "lib_types": [], "lib_rarity": "all",
        # player / pvp
        "player_name": "", "p2_name": "", "user": None, "login_mode": "login",
        "room_code": None, "room_ver": 0, "online_role": None,  # None|host|guest
        "p2_wants_rematch": False, "guest_asked_rematch": False,
        "guest_sent": False, "room_gone": False,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)
    try:  # shareable deep links: /?page=games etc.
        qa = st.query_args
        pg = qa.get("page") if isinstance(qa, dict) else (qa.get("page") if hasattr(qa, "get") else None)
        if pg and pg in PAGES_LATER:
            st.session_state.page = pg
    except Exception:
        pass


PAGES_LATER = ["home", "deck", "pvp", "battle", "games", "library", "help"]
_init_state()


def lang():
    return st.session_state.lang


def ui_sfx(name):
    st.session_state.ui_sfx.append(name)


def go(page):
    st.session_state.page = page
    st.session_state.surrender_arm = False


def _app_rerun():
    try:
        st.rerun(scope="app")
    except Exception:
        pass


def _display_name(side):
    """Human-readable label for a pvp side."""
    if side == "p":
        return st.session_state.player_name.strip()[:12] or t(lang(), "p1")
    return st.session_state.p2_name.strip()[:12] or t(lang(), "p2")


def _record(name, win, pvp):
    u = st.session_state.get("user")
    if u:
        ACC.update_stats(u, games=1,
                         **({"wins": 1} if win else {"losses": 1}),
                         **({"pvp_wins": 1} if (pvp and win) else {}))


def _score():
    """Score bookkeeping for vs-AI modes."""
    b = st.session_state.battle
    if b and b["over"] and not b.get("scored_ai"):
        if b["win"]:
            st.session_state.wins += 1
            st.session_state.streak += 1
        else:
            st.session_state.losses += 1
            st.session_state.streak = 0
        _record(st.session_state.player_name, b["win"], pvp=False)
        b["scored_ai"] = True


# ------------------------------------------------------------- callbacks ----
def cb_lang():
    st.session_state.lang = LANG_BY_LABEL.get(st.session_state.lang_box, "zh")
    if st.session_state.get("user"):
        ACC.save_settings(st.session_state.user, lang=st.session_state.lang)


def cb_sound():
    if st.session_state.get("user"):
        ACC.save_settings(st.session_state.user, sound=st.session_state.sound)


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
        b["winner"] = "e"
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


# ------------------------------------------------------- pvp callbacks ------
def cb_pvp_start_hotseat():
    p1 = _display_name("p")
    p2 = _display_name("e")
    st.session_state.battle = E.start_battle(
        st.session_state.lang, st.session_state.pv_p1_deck,
        mode="hotseat", labels={"p": p1, "e": p2},
        enemy_deck_id=st.session_state.pv_p2_deck)
    st.session_state.page = "battle"
    ui_sfx("switch")


def cb_online_create():
    st.session_state.room_gone = False
    code = R.create_room(st.session_state.lang, st.session_state.on_p1_deck)
    st.session_state.room_code = code
    st.session_state.online_role = "host"
    st.session_state.side = "p"
    ui_sfx("click")


def cb_online_join():
    code = st.session_state.get("join_code_input", "").strip().upper()
    st.session_state.room_gone = False
    if len(code) < 3:
        st.session_state.join_error = True
        return
    ok = R.join_room(code, st.session_state.on_p2_deck,
                     name=st.session_state.player_name.strip()[:12])
    st.session_state.join_error = not ok
    if ok:
        st.session_state.room_code = code
        st.session_state.online_role = "guest"
        st.session_state.side = "e"
        ui_sfx("click")


def cb_host_start():
    code = st.session_state.room_code
    room = R.read_room(code)
    if not room or not room.get("p2"):
        return
    p2_label = (room["p2"].get("name") or "").strip() or _display_name("e")
    b = E.start_battle(
        st.session_state.lang, st.session_state.on_p1_deck,
        mode="online", labels={"p": _display_name("p"), "e": p2_label},
        enemy_deck_id=room["p2"]["deck"])
    st.session_state.battle = b
    R.clear_rematch(code)
    st.session_state.p2_wants_rematch = False
    R.sync_state(code, b, status="playing")
    st.session_state.room_ver = R.read_state(code)[1]
    st.session_state.page = "battle"
    ui_sfx("switch")


def _host_sync(b):
    """Record host score when finished, then publish state."""
    code = st.session_state.room_code
    if b["over"] and not b.get("scored_host"):
        _record(st.session_state.player_name, b.get("winner") == "p", pvp=True)
        b["scored_host"] = True
    R.sync_state(code, b)
    st.session_state.room_ver = R.read_state(code)[1]


def cb_pvp_act(kind, arg=None, side="p"):
    """Hotseat / online-host action dispatch."""
    b = st.session_state.battle
    if b is None or b["over"]:
        return
    role = st.session_state.get("online_role")
    if role == "guest":
        R.post_request(st.session_state.room_code, "e", kind, arg)
        st.session_state.guest_sent = True
        return
    if role == "host":
        side = "p"
    if b.get("to_act") != side and b.get("pending") != side:
        return
    E.pvp_action(b, side, kind, arg)
    if role == "host":
        _host_sync(b)


def cb_pvp_surrender(side="p"):
    b = st.session_state.battle
    if b is None or b["over"]:
        return
    role = st.session_state.get("online_role")
    if role == "guest":
        R.post_request(st.session_state.room_code, "e", "surrender")
        return
    if role == "host":
        side = "p"
    E.pvp_surrender(b, side)
    if role == "host":
        _host_sync(b)


def cb_rematch_hotseat():
    st.session_state.battle = E.start_battle(
        st.session_state.lang, st.session_state.battle["deck_id"],
        mode="hotseat", labels=st.session_state.battle["labels"],
        enemy_deck_id=st.session_state.battle["enemy_deck_id"])
    st.session_state.page = "battle"
    ui_sfx("switch")


def cb_host_rematch():
    code = st.session_state.room_code
    b = st.session_state.battle
    nb = E.start_battle(
        st.session_state.lang, b["deck_id"], mode="online",
        labels=b["labels"], enemy_deck_id=b["enemy_deck_id"])
    st.session_state.battle = nb
    R.clear_rematch(code)
    st.session_state.p2_wants_rematch = False
    R.sync_state(code, nb, status="playing")
    st.session_state.room_ver = R.read_state(code)[1]
    ui_sfx("switch")


def cb_guest_rematch():
    R.post_request(st.session_state.room_code, "e", "rematch")
    st.session_state.guest_asked_rematch = True


def cb_back_room():
    st.session_state.page = "pvp"
    ui_sfx("click")


# ------------------------------------------------------- xiangqi callback ---
def _xq_ai_move():
    b = st.session_state.xq_board
    depth = 3 if st.session_state.xq_mode == "hard" else 2
    jitter = 0 if st.session_state.xq_mode == "hard" else 6
    mv = XQ.best_move(b, "b", depth=depth, jitter=jitter)
    if mv:
        st.session_state.xq_hist.append((list(b), "b"))
        cap = XQ.apply_move(b, mv)
        st.session_state.xq_last = list(mv)
        if cap:
            st.session_state.xq_voice.append(f"食{XQ.CHAR[cap]}")
        st.session_state.xq_turn = "r"
        if not XQ.legal_moves(b, "r"):
            st.session_state.xq_over = "b"
            st.session_state.xq_voice.append("絕殺")
            st.session_state.xq_voice.append("黑方勝")
        elif XQ.in_check(b, "r"):
            st.session_state.xq_voice.append("將軍")


def cb_xq_click(idx):
    b = st.session_state.xq_board
    if b is None or st.session_state.xq_over:
        return
    turn = st.session_state.xq_turn
    mode = st.session_state.xq_mode
    if mode != "p2" and turn != "r":
        return
    sel = st.session_state.xq_sel
    legal = XQ.legal_moves(b, turn)
    if sel is not None and (sel, idx) in legal:
        st.session_state.xq_hist.append((list(b), turn))
        cap = XQ.apply_move(b, (sel, idx))
        st.session_state.xq_last = [sel, idx]
        st.session_state.xq_sel = None
        if cap:
            st.session_state.xq_voice.append(f"食{XQ.CHAR[cap]}")
        opp = "b" if turn == "r" else "r"
        st.session_state.xq_turn = opp
        if not XQ.legal_moves(b, opp):
            st.session_state.xq_over = turn
            st.session_state.xq_voice.append("絕殺")
            st.session_state.xq_voice.append("紅方勝" if turn == "r" else "黑方勝")
        elif XQ.in_check(b, opp):
            st.session_state.xq_voice.append("將軍")
        elif mode != "p2" and opp == "b":
            _xq_ai_move()
    elif b[idx] and b[idx][0] == turn:
        st.session_state.xq_sel = idx
    else:
        st.session_state.xq_sel = None


# ----------------------------------------------------- polling fragments ----
@st.fragment(run_every="2s")
def frag_host_wait():
    code = st.session_state.get("room_code")
    if not code or st.session_state.get("online_role") != "host":
        return
    if st.session_state.get("page") != "pvp":
        return
    room = R.read_room(code)
    if not room:
        if not st.session_state.get("room_gone"):
            st.session_state.room_gone = True
            _app_rerun()
        return
    joined = room.get("p2") is not None
    if joined != st.session_state.get("_p2_joined_prev", False):
        st.session_state._p2_joined_prev = joined
        st.session_state.room_snapshot = room
        _app_rerun()
    st.session_state.room_snapshot = room


@st.fragment(run_every="2s")
def frag_guest():
    code = st.session_state.get("room_code")
    if not code or st.session_state.get("online_role") != "guest":
        return
    state, ver = R.read_state(code)
    if state is None:
        return
    if st.session_state.get("page") == "battle":
        if ver != st.session_state.get("room_ver"):
            st.session_state.battle = state
            st.session_state.room_ver = ver
            st.session_state.guest_sent = False
            _app_rerun()
    elif st.session_state.get("page") == "pvp":
        room = R.read_room(code)
        if room and room.get("status") == "playing" and state:
            st.session_state.battle = state
            st.session_state.room_ver = ver
            st.session_state.page = "battle"
            _app_rerun()


@st.fragment(run_every="2s")
def frag_host_battle():
    code = st.session_state.get("room_code")
    b = st.session_state.get("battle")
    if (not code or st.session_state.get("online_role") != "host"
            or st.session_state.get("page") != "battle" or not b):
        return
    room = R.read_room(code)
    if room and room.get("rematch_p2") and not st.session_state.get("p2_wants_rematch"):
        st.session_state.p2_wants_rematch = True
        _app_rerun()
    reqs = R.consume_requests(code)
    applied = False
    for r in reqs:
        if r["kind"] == "rematch":
            continue
        if b["over"]:
            continue
        if r["kind"] == "surrender":
            E.pvp_surrender(b, "e")
        else:
            E.pvp_action(b, "e", r["kind"], r.get("arg"))
        applied = True
    if applied:
        st.session_state.battle = b
        _host_sync(b)
        _app_rerun()


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

    st.toggle(t(lang(), "sound_label"), key="sound", on_change=cb_sound)

    if st.button(t(lang(), "sound_test")):
        if st.session_state.sound:
            SFX.play("win")

    st.divider()
    labels = {"home": t(lang(), "nav_home"), "deck": t(lang(), "nav_deck"),
              "pvp": t(lang(), "nav_pvp"), "games": t(lang(), "nav_games"),
              "library": t(lang(), "nav_lib"), "help": t(lang(), "nav_help")}
    nav_opts = ["home", "deck", "pvp", "games", "library", "help"]
    b_now = st.session_state.battle
    if b_now is not None and not b_now.get("over") and st.session_state.page == "battle":
        nav_opts.insert(2, "battle")
        labels["battle"] = "🔴 " + t(lang(), "nav_battle_active")
    for p in nav_opts:
        mark = "▸ " if p == st.session_state.page else "　"
        if st.button(mark + labels.get(p, p), key=f"nav_{p}"):
            if st.session_state.page != p:
                st.session_state.page = p
                st.session_state.surrender_arm = False
                ui_sfx("click")
            st.rerun()

    st.divider()
    st.divider()
    # ---------------- account login / save ----------------
    if st.session_state.get("user"):
        u = st.session_state.user
        st.markdown(f"👤 **{u}**")
        stg = ACC.stats_of(u)
        st.markdown(f"`{stg['wins']}W · {stg['losses']}L` 🏆{stg['best']}　"
                    f"🤝{stg['pvp_wins']}　🀄{stg['mj_score']}　♟{stg['xq_wins']}")
        if st.button(t(lang(), "btn_logout"), key="logout_btn"):
            ACC.save_settings(u, lang=st.session_state.lang, sound=st.session_state.sound)
            st.session_state.user = None
            st.rerun()
    else:
        with st.expander("🔑 " + t(lang(), "login_title")):
            st.text_input(t(lang(), "username"), max_chars=16, key="login_name")
            st.text_input(t(lang(), "password"), type="password", max_chars=32, key="login_pw")
            b1, b2 = st.columns(2)
            if b1.button(t(lang(), "btn_login"), key="do_login", type="primary"):
                ok, msg = ACC.login(st.session_state.get("login_name", ""),
                                    st.session_state.get("login_pw", ""))
                if ok:
                    st.session_state.user = st.session_state.login_name.strip()
                    rec = ACC.get(st.session_state.user) or {}
                    if rec.get("lang") in ("zh", "en", "ja", "ko"):
                        st.session_state.lang = rec["lang"]
                    if rec.get("sound") is not None:
                        st.session_state.sound = bool(rec["sound"])
                    st.session_state.login_msg = ("ok", t(st.session_state.lang, "login_welcome"))
                    st.rerun()
                else:
                    st.error(t(lang(), "login_bad" if msg in ("nouser", "badpw") else "login_short"))
            if b2.button(t(lang(), "btn_register"), key="do_register"):
                ok, msg = ACC.register(st.session_state.get("login_name", ""),
                                       st.session_state.get("login_pw", ""))
                if ok:
                    st.session_state.user = st.session_state.login_name.strip()
                    st.session_state.login_msg = ("ok", t(st.session_state.lang, "login_welcome"))
                    st.rerun()
                else:
                    st.error(t(lang(), "user_exists" if msg == "exists" else "login_short"))
        if st.session_state.get("login_msg"):
            kind, txt = st.session_state.login_msg
            (st.success if kind == "ok" else st.error)(txt)
            st.session_state.login_msg = None
        st.caption(t(lang(), "guest_hint"))
        st.text_input(t(lang(), "nickname"), max_chars=12, key="player_name_input")
        st.session_state.player_name = st.session_state.get("player_name_input", "").strip()

    if not st.session_state.get("user"):
        st.session_state.player_name = st.session_state.get("player_name_input", "").strip()
    else:
        st.session_state.player_name = st.session_state.user

    w, l, s = st.session_state.wins, st.session_state.losses, st.session_state.streak
    st.markdown(f"**{t(lang(),'record')}**　`{w} {t(lang(),'wins')} · {l} {t(lang(),'losses')}`"
                f"　🔥 {s} {t(lang(),'streak')}")

    with st.expander(t(lang(), "leaderboard")):
        rows = ACC.top(8)
        if not rows:
            st.caption(t(lang(), "no_scores"))
        for i, r in enumerate(rows, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            st.markdown(f"{medal} **{r['name']}**　`{r['wins']}{t(lang(),'wins')}`"
                        f"　🏆{r['best']}　🎮{r['games']}")

    st.divider()
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
          <span class="hk-badge">🤝 2P</span>
        </div></div>''', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button(t(lang(), "cta_start"), type="primary"):
        go("deck")
        st.rerun()
    if c2.button(t(lang(), "nav_pvp")):
        go("pvp")
        st.rerun()
    if c3.button(t(lang(), "nav_games")):
        go("games")
        st.rerun()
    if c4.button(t(lang(), "cta_lib")):
        go("library")
        st.rerun()
    if c5.button(t(lang(), "cta_help")):
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

# ------------------------------------------------------------------- pvp ----
elif st.session_state.page == "pvp":
    st.markdown(f'<span class="street-sign">{t(lang(),"pvp_title")}</span>', unsafe_allow_html=True)

    sub = st.segmented_control("pvp_mode", ["hotseat", "online"],
                               format_func=lambda m: t(lang(), "pvp_hotseat" if m == "hotseat" else "pvp_online"),
                               selection_mode="single", default="hotseat", key="pvp_sub")

    deck_ids = [d["id"] for d in D.CHOOSABLE_DECKS]
    deck_label = lambda did: f'{D.DECK[did]["emoji"]} {D.DECK[did]["name"][lang()]}'

    if sub == "hotseat":
        st.caption(t(lang(), "hotseat_desc"))
        st.text_input(f'👤 {t(lang(),"p2_pick")} — {t(lang(),"p2")}', max_chars=12,
                      key="p2_name_input")
        st.session_state.p2_name = st.session_state.get("p2_name_input", "").strip()

        st.markdown(f"**{t(lang(),'p1_pick')}**")
        s1 = st.pills("p1_deck", deck_ids, format_func=deck_label,
                      selection_mode="single", default="d1", key="pv_p1_deck")
        st.markdown(f"**{t(lang(),'p2_pick')}**")
        s2 = st.pills("p2_deck", deck_ids, format_func=deck_label,
                      selection_mode="single", default="d3", key="pv_p2_deck")
        st.session_state.pv_p1_deck = (s1[0] if isinstance(s1, list) else s1) or "d1"
        st.session_state.pv_p2_deck = (s2[0] if isinstance(s2, list) else s2) or "d3"

        if st.button(f"⚔️ {t(lang(),'pvp_start')}", type="primary"):
            cb_pvp_start_hotseat()
            st.rerun()
    else:
        st.caption(t(lang(), "online_desc"))
        st.info(t(lang(), "online_note"))

        if st.session_state.get("room_code"):
            code = st.session_state.room_code
            room = R.read_room(code)
            st.markdown(f"### {t(lang(),'room_code_label')}: ` {code} `")
            st.caption(t(lang(), "share_link"))

            if st.session_state.online_role == "host":
                frag_host_wait()
                p2 = (room or {}).get("p2")
                if not p2:
                    st.warning(t(lang(), "waiting_p2"))
                else:
                    st.success(t(lang(), "p2_joined"))
                    who = (p2.get("name") or "").strip()
                    if who:
                        st.caption(f"👤 {who}")
                    if st.button(t(lang(), "host_start"), type="primary"):
                        cb_host_start()
                        st.rerun()
            else:
                st.info(t(lang(), "waiting_host"))
                frag_guest()
                if st.button(t(lang(), "back_to_room")):
                    cb_back_room()
                    st.rerun()
        else:
            a, b_ = st.columns(2)
            with a:
                st.markdown(f"**{t(lang(),'online_create')}**")
                cs = st.pills("on_p1_deck", deck_ids, format_func=deck_label,
                              selection_mode="single", default="d1", key="on_p1_deck")
                st.session_state.on_p1_deck = (cs[0] if isinstance(cs, list) else cs) or "d1"
                if st.button(t(lang(), "online_create"), type="primary"):
                    cb_online_create()
                    st.rerun()
            with b_:
                st.markdown(f"**{t(lang(),'online_join')}**")
                js = st.pills("on_p2_deck", deck_ids, format_func=deck_label,
                              selection_mode="single", default="d3", key="on_p2_deck")
                st.session_state.on_p2_deck = (js[0] if isinstance(js, list) else js) or "d3"
                st.text_input(t(lang(), "enter_code"), max_chars=4, key="join_code_input")
                if st.session_state.get("join_error"):
                    st.error(t(lang(), "code_not_found"))
                if st.button(t(lang(), "join")):
                    cb_online_join()
                    st.rerun()

# ---------------------------------------------------------------- battle ----
elif st.session_state.page == "battle":
    b = st.session_state.battle
    if b is None:
        st.session_state.page = "deck"
        st.rerun()

    L = b["lang"]
    role = st.session_state.get("online_role")
    pvpish = b["mode"] in ("hotseat", "online")
    if pvpish:
        cur_side = b["pending"] or b["to_act"]
        my_side = "e" if (role == "guest" and b["mode"] == "online") else             (cur_side if b["mode"] == "hotseat" else "p")
    else:
        cur_side = "p"
        my_side = "p"

    view = AR.build_arena(b, my_side, st.session_state.get("arena_panel"))
    res = AR.ARENA(key=f"arena-{my_side}", data=view,
                   on_act_change=lambda: None, on_bench_change=lambda: None,
                   on_item_change=lambda: None, on_panel_change=lambda: None)
    act = getattr(res, "act", None)
    benchv = getattr(res, "bench", None)
    itemv = getattr(res, "item", None)
    panv = getattr(res, "panel", None)

    if panv:
        st.session_state.arena_panel = None if panv == "none" else panv
        st.rerun()
    acted = False
    if not b["over"]:
        if act == "surrender":
            if pvpish:
                cb_pvp_surrender(my_side)
            else:
                cb_surrender_yes()
            acted = True
        elif act in ("move1", "move2"):
            if pvpish:
                cb_pvp_act(act, side=my_side)
            else:
                cb_action(act)
            acted = True
        elif benchv is not None:
            kind = "replace" if (pvpish and b["pending"] == my_side) else ("replace" if b["pending"] else "switch")
            if pvpish:
                cb_pvp_act(kind, benchv, side=my_side)
            else:
                cb_action(kind, benchv)
            acted = True
        elif itemv:
            if pvpish:
                cb_pvp_act("item", itemv, side=my_side)
            else:
                cb_action("item", itemv)
            acted = True
    if acted:
        st.rerun()

    if st.session_state.surrender_arm and not b["over"] and not pvpish:
        st.warning(t(L, "surrender_again"))
        if st.button("⚠️ " + t(L, "surrender"), key="sur_confirm"):
            cb_surrender_yes()
            st.rerun()

    # -------- result buttons --------
    if b["over"]:
        r1, r2, r3 = st.columns(3)
        if pvpish:
            winner_label = b["labels"].get(b.get("winner"), "")
            if b["mode"] == "hotseat":
                if b.get("winner") == "p":
                    st.session_state.wins += 1
                    st.session_state.streak += 1
                else:
                    st.session_state.losses += 1
                    st.session_state.streak = 0
                if not b.get("scored_local"):
                    _record(st.session_state.player_name, b.get("winner") == "p", pvp=True)
                    _record(st.session_state.p2_name, b.get("winner") == "e", pvp=True)
                    b["scored_local"] = True
                if r1.button(t(L, "btn_rematch"), type="primary"):
                    cb_rematch_hotseat()
                    st.rerun()
            elif role == "host":
                if st.session_state.get("p2_wants_rematch"):
                    st.info(t(L, "want_rematch"))
                if r1.button(t(L, "btn_rematch"), type="primary"):
                    cb_host_rematch()
                    st.rerun()
            else:
                if b.get("winner") == "e" and not b.get("scored_guest"):
                    _record(st.session_state.player_name, False, pvp=True)
                    b["scored_guest"] = True
                if st.session_state.get("guest_asked_rematch"):
                    st.caption(t(L, "wait_rematch"))
                elif r1.button(t(L, "ask_rematch")):
                    cb_guest_rematch()
                    st.rerun()
        else:
            _score()
            if b["win"]:
                st.balloons()
                if b["mode"] == "gauntlet" and b["stage"] == 3:
                    st.markdown(f"<h2 style='text-align:center;'>🏆 {t(L,'m_champion')}</h2>",
                                unsafe_allow_html=True)
            else:
                st.snow()
            if b["mode"] == "gauntlet" and b["win"] and b["stage"] < 3:
                if r1.button(t(L, "btn_next"), type="primary"):
                    cb_next_stage()
                    st.rerun()
        if not (pvpish and b["mode"] == "online"):
            if r2.button(t(L, "btn_rematch"), key="rm_std"):
                if pvpish:
                    cb_rematch_hotseat()
                else:
                    cb_rematch()
                st.rerun()
        if r3.button(t(L, "btn_home")):
            cb_home()
            st.rerun()

    with st.expander(t(L, "battle_log")):
        for line in b["log"][-40:]:
            st.markdown(f"- {line}")

    if b["mode"] == "online":
        if role == "host":
            frag_host_battle()
        else:
            frag_guest()

    if st.session_state.sound:
        for sname in b["sfx"]:
            SFX.play(sname)
    b["sfx"] = []
    b["hit"] = None

# ------------------------------------------------------------------ games ---
elif st.session_state.page == "games":
    st.markdown(f'<span class="street-sign">{t(lang(),"games_title")}</span>', unsafe_allow_html=True)
    st.caption(t(lang(), "games_desc"))

    try:
        _qt = st.query_args.get("tab") if hasattr(st.query_args, "get") else None
        if _qt in ("xq", "mj"):
            st.session_state.games_tab = _qt
    except Exception:
        pass
    gt = st.segmented_control("games_tab", ["xq", "mj"],
                              format_func=lambda g: t(lang(), "xq_title" if g == "xq" else "mj_title"),
                              selection_mode="single", default="xq", key="games_tab")
    tab = (gt[0] if isinstance(gt, list) else gt) or "xq"

    if tab == "xq":
        # ---------------- 象棋 ----------------
        st.session_state.setdefault("xq_board", XQ.initial_board())
        st.session_state.setdefault("xq_turn", "r")
        st.session_state.setdefault("xq_sel", None)
        st.session_state.setdefault("xq_over", None)
        st.session_state.setdefault("xq_hist", [])
        st.session_state.setdefault("xq_voice", [])
        st.session_state.setdefault("xq_mode", "easy")

        ms = st.segmented_control("xq_mode", ["p2", "easy", "hard"],
                                  format_func=lambda m: t(lang(), "xq_p2" if m == "p2" else ("xq_easy" if m == "easy" else "xq_hard")),
                                  selection_mode="single", default=st.session_state.xq_mode, key="xq_mode_sel")
        if ms:
            st.session_state.xq_mode = ms[0] if isinstance(ms, list) else ms

        k1, k2, _k3 = st.columns([1, 1, 2])
        if k1.button(t(lang(), "xq_new")):
            st.session_state.xq_board = XQ.initial_board()
            st.session_state.xq_turn = "r"
            st.session_state.xq_sel = None
            st.session_state.xq_over = None
            st.session_state.xq_hist = []
            st.session_state.xq_last = None
            st.rerun()
        if k2.button(t(lang(), "xq_undo"), disabled=not st.session_state.xq_hist):
            steps = 2 if (st.session_state.xq_mode != "p2" and len(st.session_state.xq_hist) >= 2) else 1
            for _ in range(steps):
                if st.session_state.xq_hist:
                    board_, turn_ = st.session_state.xq_hist.pop()
                    st.session_state.xq_board = board_
                    st.session_state.xq_turn = turn_
            st.session_state.xq_over = None
            st.session_state.xq_sel = None
            st.rerun()

        b_ = st.session_state.xq_board
        if st.session_state.xq_over:
            win_txt = t(lang(), "xq_win_r") if st.session_state.xq_over == "r" else t(lang(), "xq_win_b")
            st.markdown(f"<h2 style='text-align:center;color:#ffd23f;'>🏆 {win_txt}</h2>",
                        unsafe_allow_html=True)
            st.balloons()
            if st.session_state.xq_mode != "p2" and not st.session_state.get("xq_rec"):
                if st.session_state.get("user"):
                    ACC.update_stats(st.session_state.user,
                                     **({"xq_wins": 1} if st.session_state.xq_over == "r"
                                        else {"xq_losses": 1}))
                st.session_state.xq_rec = True
        else:
            if st.session_state.xq_turn == "r":
                cap = t(lang(), "xq_red_turn")
                if st.session_state.xq_mode != "p2":
                    cap += "　" + t(lang(), "xq_you_red")
                st.markdown(f"<div style='text-align:center;font-weight:900;color:#ff9f9f;'>⏳ {cap}</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center;font-weight:900;color:#9fc7ff;'>⏳ {t(lang(),'xq_black_turn')}</div>",
                            unsafe_allow_html=True)

        legal = [] if st.session_state.xq_over else XQ.legal_moves(b_, st.session_state.xq_turn)
        targets = [t2 for (f_, t2) in legal if f_ == st.session_state.xq_sel]             if st.session_state.xq_sel is not None else []
        if st.session_state.xq_turn != "r" and st.session_state.xq_mode != "p2" and not st.session_state.xq_over:
            targets = []
        xq_view = XB.build_view(b_, st.session_state.xq_sel, targets, st.session_state.get("xq_last"))
        xres = XB.XQ_BOARD(key="xq_board_ui", data=xq_view, on_sq_change=lambda: None)
        sqv = getattr(xres, "sq", None)
        if sqv is not None:
            cb_xq_click(sqv)
            st.rerun()

        for txt in st.session_state.xq_voice:
            if st.session_state.sound:
                SFX.speak(txt)
        st.session_state.xq_voice = []

    else:
        # ---------------- 麻將 ----------------
        st.caption(t(lang(), "mj_note"))
        if st.session_state.get("mj_game") is None or st.session_state.get("mj_new"):
            st.session_state.mj_game = MJ.initial_game()
            st.session_state.mj_new = False
            st.session_state.mj_sel = None
        g = st.session_state.mj_game

        if st.button(t(lang(), "mj_new")):
            st.session_state.mj_new = True
            st.rerun()

        if g["await"] is None and g["over"] is None:
            MJ.advance(g)

        if g["over"] and not g.get("rec") and st.session_state.get("user"):
            if g["over"].get("winner") == 0:
                ACC.update_stats(st.session_state.user, mj_score=g["over"].get("fan", 0))
            g["rec"] = True

        view = TBL.build_view(g, st.session_state.get("mj_sel"))
        res = TBL.MJ_TABLE(
            key="mj_table_ui", data=view,
            on_tile_click_change=lambda: None,
            on_action_change=lambda: None)
        tc = getattr(res, "tile_click", None)
        act = getattr(res, "action", None)

        acted = False
        aw = g["await"]
        if g["over"] is None and aw:
            if tc is not None and aw["type"] == "discard":
                if st.session_state.get("mj_sel") == tc:
                    MJ.human_discard(g, view["hand"][tc])
                    st.session_state.mj_sel = None
                    acted = True
                else:
                    st.session_state.mj_sel = tc
                    st.rerun()
            if act and not acted:
                if act == "confirm" and st.session_state.get("mj_sel") is not None and aw["type"] == "discard":
                    MJ.human_discard(g, view["hand"][st.session_state.mj_sel])
                    st.session_state.mj_sel = None
                    acted = True
                elif act == "zimo" and aw["type"] == "discard":
                    drawn = aw.get("drawn")
                    MJ._win_game(g, 0, drawn if drawn is not None else view["hand"][-1], True)
                    g["await"] = None
                    acted = True
                elif aw["type"] == "claim":
                    if act == "win":
                        MJ.human_claim(g, "win", None)
                        acted = True
                    elif act == "pong":
                        MJ.human_claim(g, "pong", None)
                        acted = True
                    elif act == "kong":
                        MJ.human_claim(g, "kong", None)
                        acted = True
                    elif act.startswith("chi:"):
                        MJ.human_claim(g, "chi", int(act.split(":")[1]))
                        acted = True
                    elif act == "skip":
                        MJ.skip_human_turn(g)
                        acted = True
        if acted:
            st.rerun()

        with st.expander("📜 log"):
            for line in g["log"][-12:]:
                st.markdown(f"- {line}")

        for txt in g["voice"]:
            if st.session_state.sound:
                SFX.speak(txt)
        g["voice"] = []

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

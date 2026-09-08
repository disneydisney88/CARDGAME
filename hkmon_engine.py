# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — battle engine (turn-based, AI opponent).

State dict layout (stored in st.session_state["battle"]):
{
  "p": [fighter...], "e": [fighter...],      # 5 fighters each
  "pa": 0, "ea": 0,                          # active index
  "pitems": [id...], "eitems": [id...],      # remaining item ids
  "turn": 1, "over": False, "win": False,
  "pending": None | "switch",                # player must choose replacement
  "log": [...], "sfx": [...],
  "hit": None | "p" | "e" | "pe",            # CSS shake flags for this render
  "diff": "easy"|"normal"|"hard", "mode": "quick"|"gauntlet",
  "stage": 1..3, "deck_id": ..., "enemy_deck_name": str,
}
fighter = {"id", "hp", "mhp", "status"(None|"burn"|"para"), "st_turns",
           "buff", "shield", "cd2"}
"""
import random

import hkmon_data as D
import hkmon_i18n as I18N

CRIT_CHANCE = 0.12
CRIT_MULT = 1.6
BURN_PCT = 0.06
BURN_TURNS = 3
PARA_TURNS = 2
PARA_SKIP = 0.35
SUDDEN_DEATH_TURN = 50


# --------------------------------------------------------------- helpers ----
def _mk_fighter(mon_id, hp_mult=1.0):
    card = D.MON[mon_id]
    hp = max(1, int(card["hp"] * hp_mult))
    return {"id": mon_id, "hp": hp, "mhp": hp, "status": None, "st_turns": 0,
            "buff": 0, "shield": False, "cd2": 0}


def _move1(card, idx):
    tpl = D.MOVE1[card["type"]][idx % 4]
    return tpl


def _name(lang, card_id):
    card = D.MON.get(card_id) or D.ITEM[card_id]
    return card["name"][lang]


def _log(state, key, **kw):
    state["log"].append(I18N.t(state["lang"], key, **kw))


def _sfx(state, name):
    state["sfx"].append(name)


def _hit_fx(state, sides):
    state["hit"] = sides


def active(state, side):
    return state[side][state["pa" if side == "p" else "ea"]]


def alive(side_list):
    return [f for f in side_list if f["hp"] > 0]


# ------------------------------------------------------------ battle init ---
def random_deck_ids():
    mons = random.sample([m["id"] for m in D.MONSTERS], 5)
    items = random.sample([i["id"] for i in D.ITEMS], 3)
    return mons, items


def start_battle(lang, deck_id, diff, mode, stage=1, record=None):
    """Create a fresh battle state. record = previous log to carry over."""
    deck = D.DECK[deck_id]
    if deck.get("random"):
        pmons, pitems = random_deck_ids()
    else:
        pmons, pitems = list(deck["mons"]), list(deck["items"])

    enemy_deck_id = D.GAUNTLET[stage - 1] if mode == "gauntlet" else \
        random.choice([d["id"] for d in D.CHOOSABLE_DECKS])
    edeck = D.DECK[enemy_deck_id]
    if edeck.get("random"):
        emons, _ = random_deck_ids()
    else:
        emons = list(edeck["mons"])
    random.shuffle(emons)
    eitems = random.sample(["i01", "i02", "i03", "i04", "i08"], 2)

    hp_mult = {"easy": 0.85, "normal": 1.0, "hard": 1.15}[diff]
    if mode == "gauntlet":
        hp_mult *= 1.0 + 0.05 * (stage - 1)

    state = {
        "lang": lang, "diff": diff, "mode": mode, "stage": stage,
        "deck_id": deck_id, "enemy_deck_id": enemy_deck_id,
        "p": [_mk_fighter(m) for m in pmons],
        "e": [_mk_fighter(m, hp_mult) for m in emons],
        "pa": 0, "ea": 0,
        "pitems": list(pitems), "eitems": eitems,
        "turn": 1, "over": False, "win": False, "pending": None,
        "log": list(record or []), "sfx": [], "hit": None,
        "enemy_switched_this_round": False,
    }
    # player's lead: first alive
    state["pa"] = 0
    _log(state, "m_battle_start", n=(stage if mode == "gauntlet" else 1),
         e=edeck["name"][lang])
    _sfx(state, "switch")
    return state


# --------------------------------------------------------------- damage -----
def _mult(atk_f, def_f):
    at = D.MON[atk_f["id"]]["type"]
    dt = D.MON[def_f["id"]]["type"]
    return D.eff_mult(at, dt)


def _apply_damage(state, atk_side, move, move_name, is_move2):
    """Attacker's active hits defender's active. Returns dmg dealt."""
    atk = active(state, atk_side)
    def_side = "e" if atk_side == "p" else "p"
    dfd = active(state, def_side)
    lang = state["lang"]
    p_label = I18N.t(lang, "you") if atk_side == "p" else I18N.t(lang, "enemy")

    _log(state, "m_use", p=p_label, m=move_name)

    mult = _mult(atk, dfd)
    crit = random.random() < CRIT_CHANCE
    dmg = move["power"] + atk["buff"]
    dmg = dmg * mult * random.uniform(0.9, 1.1)
    if crit:
        dmg *= CRIT_MULT
    if dfd["shield"]:
        dmg *= 0.5
        dfd["shield"] = False
    dmg = max(1, round(dmg))

    dfd["hp"] = max(0, dfd["hp"] - dmg)
    atk["buff"] = 0

    _log(state, "m_dmg", d=dmg)
    if crit:
        _log(state, "m_crit")
        _sfx(state, "crit")
    elif mult > 1:
        _log(state, "m_super")
    elif mult < 1:
        _log(state, "m_weak")

    sfx = "special" if is_move2 else "attack"
    if "crit" not in state["sfx"]:
        _sfx(state, sfx)
    _hit_fx(state, "pe" if atk_side == "p" else "ep")

    # move effects
    eff = move.get("effect") or {}
    if eff.get("status") and dfd["hp"] > 0 and dfd["status"] is None:
        if random.random() < eff["chance"]:
            if eff["status"] == "burn":
                dfd["status"] = "burn"
                dfd["st_turns"] = BURN_TURNS
                _log(state, "m_burn_set", n=_name(lang, dfd["id"]))
                _sfx(state, "burn")
            else:
                dfd["status"] = "para"
                dfd["st_turns"] = PARA_TURNS
                _log(state, "m_para_set", n=_name(lang, dfd["id"]))
                _sfx(state, "para")
    if eff.get("heal_pct") and atk["hp"] > 0:
        heal = min(round(atk["mhp"] * eff["heal_pct"]), atk["mhp"] - atk["hp"])
        if heal > 0:
            atk["hp"] += heal
            _log(state, "m_heal", n=_name(lang, atk["id"]), d=heal)
            _sfx(state, "heal")
    if eff.get("buff") and atk["hp"] > 0:
        atk["buff"] += eff["buff"]
        _log(state, "m_buff", n=_name(lang, atk["id"]))
        _sfx(state, "buff")

    return dmg


def _check_faints(state):
    """Handle faints. Returns 'over' if battle ended."""
    lang = state["lang"]
    # enemy side
    ea = state["e"][state["ea"]]
    if ea["hp"] <= 0:
        _log(state, "m_faint", n=_name(lang, ea["id"]))
        _sfx(state, "ko")
        if not alive(state["e"]):
            state["over"] = True
            state["win"] = True
            _sfx(state, "win")
            _log(state, "m_win" if state["mode"] == "quick" else "m_stage_clear")
            if state["mode"] == "gauntlet" and state["stage"] == 3:
                state["log"].pop()  # replace stage-clear with champion text
                state["log"].append(I18N.t(lang, "m_champion"))
            return "over"
        # AI picks best replacement
        best, best_score = None, -1e9
        pa_type = D.MON[active(state, "p")["id"]]["type"]
        for i, f in enumerate(state["e"]):
            if f["hp"] <= 0:
                continue
            score = f["hp"] / f["mhp"] + D.eff_mult(D.MON[f["id"]]["type"], pa_type)
            if score > best_score:
                best, best_score = i, score
        state["ea"] = best
        _log(state, "m_switch", p=I18N.t(lang, "enemy"), n=_name(lang, state["e"][best]["id"]))
    # player side
    pa = state["p"][state["pa"]]
    if pa["hp"] <= 0:
        _log(state, "m_faint", n=_name(lang, pa["id"]))
        _sfx(state, "ko")
        if not alive(state["p"]):
            state["over"] = True
            state["win"] = False
            _sfx(state, "lose")
            _log(state, "m_lose")
            return "over"
        state["pending"] = "switch"
    return None


# ------------------------------------------------------------ player turn ---
def player_move(state, key):
    """key: 'move1' | 'move2'."""
    p = active(state, "p")
    card = D.MON[p["id"]]
    if key == "move1":
        mv = _move1(card, state["p"].index(p))
        _apply_damage(state, "p", mv, mv["name"][state["lang"]], False)
    else:
        if p["cd2"] > 0:
            return
        mv = card["move2"]
        p["cd2"] = mv["cd"]
        _apply_damage(state, "p", mv, mv["name"][state["lang"]], True)


def switch_mon(state, side, idx):
    cur = state["pa" if side == "p" else "ea"]
    if idx == cur:
        return
    state["pa" if side == "p" else "ea"] = idx
    lang = state["lang"]
    f = state[side][idx]
    f["status"] = None          # switching clears status
    f["st_turns"] = 0
    f["buff"] = 0
    f["shield"] = False
    label = I18N.t(lang, "you") if side == "p" else I18N.t(lang, "enemy")
    _log(state, "m_switch", p=label, n=_name(lang, f["id"]))
    _sfx(state, "switch")


def use_item(state, side, item_id):
    lang = state["lang"]
    items = state["pitems"] if side == "p" else state["eitems"]
    if item_id not in items:
        return
    items.remove(item_id)
    it = D.ITEM[item_id]
    eff = it["effect"]
    label = I18N.t(lang, "you") if side == "p" else I18N.t(lang, "enemy")
    _log(state, "m_item", p=label, i=it["name"][lang])

    def act(side_f):
        return side_f

    own = active(state, side)
    foe_side = "e" if side == "p" else "p"
    foe = active(state, foe_side)
    kind = eff["kind"]
    n = eff.get("n", 0)

    if kind == "heal":
        heal = min(n, own["mhp"] - own["hp"])
        own["hp"] += heal
        _log(state, "m_heal", n=_name(lang, own["id"]), d=heal)
        _sfx(state, "heal")
    elif kind == "buff":
        own["buff"] += n
        _log(state, "m_buff", n=_name(lang, own["id"]))
        _sfx(state, "buff")
    elif kind == "shield":
        own["shield"] = True
        _log(state, "m_shield", n=_name(lang, own["id"]))
        _sfx(state, "shield")
    elif kind == "cure":
        own["status"] = None
        own["st_turns"] = 0
        own["hp"] = min(own["mhp"], own["hp"] + n)
        _log(state, "m_cure", n=_name(lang, own["id"]))
        _log(state, "m_heal", n=_name(lang, own["id"]), d=n)
        _sfx(state, "heal")
    elif kind == "heal_cure_burn":
        if own["status"] == "burn":
            own["status"] = None
            own["st_turns"] = 0
            _log(state, "m_cure", n=_name(lang, own["id"]))
        own["hp"] = min(own["mhp"], own["hp"] + n)
        _log(state, "m_heal", n=_name(lang, own["id"]), d=n)
        _sfx(state, "heal")
    elif kind == "reset_cd":
        own["cd2"] = 0
        own["hp"] = min(own["mhp"], own["hp"] + n)
        _log(state, "m_cd_reset", n=_name(lang, own["id"]))
        _log(state, "m_heal", n=_name(lang, own["id"]), d=n)
        _sfx(state, "buff")
    elif kind == "para_enemy":
        if foe["status"] is None:
            foe["status"] = "para"
            foe["st_turns"] = PARA_TURNS
            _log(state, "m_para_set", n=_name(lang, foe["id"]))
        else:
            _log(state, "m_para_set", n=_name(lang, foe["id"]))
        _sfx(state, "para")
        _hit_fx(state, "ep" if side == "p" else "pe")
    elif kind == "force_switch":
        if alive(state[foe_side]):
            cands = [i for i, f in enumerate(state[foe_side]) if f["hp"] > 0 and i != state["ea" if foe_side == "e" else "pa"]]
            if cands:
                idx = random.choice(cands)
                # quiet switch (no free clear-buff): reuse switch_mon for consistency
                switch_mon(state, foe_side, idx)
                _log(state, "m_forced", n=_name(lang, state[foe_side][idx]["id"]))
    elif kind == "direct":
        if foe["shield"]:
            dmg = max(1, n // 2)
            foe["shield"] = False
        else:
            dmg = n
        foe["hp"] = max(0, foe["hp"] - dmg)
        _log(state, "m_direct", d=dmg)
        _sfx(state, "attack")
        _hit_fx(state, "ep" if side == "p" else "pe")
    elif kind == "bench_heal":
        for f in state[side]:
            if f["hp"] > 0 and f is not own:
                f["hp"] = min(f["mhp"], f["hp"] + n)
        _log(state, "m_bench_heal", d=n)
        _sfx(state, "heal")
    elif kind == "add_cd_enemy":
        foe["cd2"] += n
        _log(state, "m_delay")
        _sfx(state, "para")
        _hit_fx(state, "ep" if side == "p" else "pe")


# --------------------------------------------------------------- AI turn ----
def _est_dmg(atk, dfd, move):
    return (move["power"] + atk["buff"]) * _mult(atk, dfd)


def ai_action(state):
    """Enemy picks attack / item / switch, then executes it."""
    if state["over"]:
        return
    diff = state["diff"]
    e = active(state, "e")
    p = active(state, "p")
    lang = state["lang"]

    # maybe use an item first (normal/hard)
    if diff != "easy" and state["eitems"]:
        e_hp_pct = e["hp"] / e["mhp"]
        heal_ids = [i for i in state["eitems"] if D.ITEM[i]["effect"]["kind"] in ("heal", "heal_cure_burn", "cure")]
        if e_hp_pct < 0.35 and heal_ids:
            use_item(state, "e", heal_ids[0])
            return
        shield_ids = [i for i in state["eitems"] if D.ITEM[i]["effect"]["kind"] == "shield"]
        if e_hp_pct < 0.55 and shield_ids and random.random() < 0.5:
            use_item(state, "e", shield_ids[0])
            return
        direct_ids = [i for i in state["eitems"] if D.ITEM[i]["effect"]["kind"] == "direct"]
        if direct_ids and p["hp"] / p["mhp"] < 0.3:
            use_item(state, "e", direct_ids[0])
            return

    # hard: opportunistic switch to a better matchup
    if diff == "hard" and random.random() < 0.25 and e["hp"] / e["mhp"] > 0.5:
        cur = _est_dmg(e, p, D.MOVE1[D.MON[e["id"]]["type"]][0])
        best, best_gain = None, 1.0
        p_type = D.MON[p["id"]]["type"]
        for i, f in enumerate(state["e"]):
            if f["hp"] <= 0 or i == state["ea"]:
                continue
            gain = D.eff_mult(D.MON[f["id"]]["type"], p_type) / max(D.eff_mult(D.MON[e["id"]]["type"], p_type), 0.1)
            if gain > best_gain:
                best, best_gain = i, gain
        if best is not None:
            switch_mon(state, "e", best)
            return

    # paralysis skip
    if e["status"] == "para" and random.random() < PARA_SKIP:
        _log(state, "m_para_skip", n=_name(lang, e["id"]))
        return

    # choose a move
    card = D.MON[e["id"]]
    mv1 = _move1(card, state["e"].index(e))
    can2 = e["cd2"] == 0
    est1 = _est_dmg(e, p, mv1)
    est2 = _est_dmg(e, p, card["move2"]) if can2 else -1

    if diff == "easy":
        use2 = can2 and random.random() < 0.5
    elif diff == "normal":
        use2 = can2 and (est2 > est1 * 1.15 or random.random() < 0.4)
    else:
        use2 = can2 and (est2 >= p["hp"] or est2 > est1 * 1.1)

    if use2:
        e["cd2"] = card["move2"]["cd"]
        _apply_damage(state, "e", card["move2"], card["move2"]["name"][lang], True)
    else:
        _apply_damage(state, "e", mv1, mv1["name"][lang], False)


# -------------------------------------------------------------- round end ---
def end_round(state):
    """Status ticks, cooldowns, sudden death; then turn++."""
    if state["over"]:
        return
    lang = state["lang"]
    for side in ("p", "e"):
        f = state[side][state["pa" if side == "p" else "ea"]]
        if f["hp"] <= 0:
            continue
        if f["status"] == "burn":
            dmg = max(3, round(f["mhp"] * BURN_PCT))
            f["hp"] = max(0, f["hp"] - dmg)
            _log(state, "m_burn_tick", n=_name(lang, f["id"]), d=dmg)
            if f["hp"] <= 0 and _check_faints(state) == "over":
                return
        if f["st_turns"] > 0:
            f["st_turns"] -= 1
            if f["st_turns"] == 0:
                f["status"] = None
        if f["cd2"] > 0:
            f["cd2"] -= 1
    if state["turn"] >= SUDDEN_DEATH_TURN:
        if state["turn"] == SUDDEN_DEATH_TURN:
            _log(state, "m_sudden")
        for side in ("p", "e"):
            f = state[side][state["pa" if side == "p" else "ea"]]
            f["hp"] = max(0, f["hp"] - max(3, round(f["mhp"] * 0.05)))
        if _check_faints(state) == "over":
            return
    state["turn"] += 1


# ------------------------------------------------------- full round flow ----
def next_stage_state(state):
    """Next gauntlet stage: carry the player's team over, healed by 30%."""
    healed = []
    for f in state["p"]:
        nf = dict(f)
        if nf["hp"] > 0:
            nf["hp"] = min(nf["mhp"], nf["hp"] + round(nf["mhp"] * 0.3))
        nf["status"] = None
        nf["st_turns"] = 0
        nf["buff"] = 0
        nf["shield"] = False
        nf["cd2"] = 0
        healed.append(nf)
    new = start_battle(state["lang"], state["deck_id"], state["diff"], "gauntlet",
                       stage=state["stage"] + 1)
    new["p"] = healed
    new["pitems"] = list(state["pitems"])
    return new


def player_action(state, kind, arg=None):
    """Run one full round after the player's chosen action."""
    if state["over"]:
        return
    if kind == "replace":
        # mandatory switch after a faint; opponent does NOT act again
        switch_mon(state, "p", arg)
        state["pending"] = None
        end_round(state)
        return
    if state["pending"]:
        return

    if kind == "move1":
        player_move(state, "move1")
    elif kind == "move2":
        player_move(state, "move2")
    elif kind == "item":
        use_item(state, "p", arg)
    elif kind == "switch":
        switch_mon(state, "p", arg)

    if _check_faints(state) == "over":
        return
    ai_action(state)
    if _check_faints(state) == "over":
        return
    end_round(state)

# -*- coding: utf-8 -*-
"""HK-MON 榕樹頭 — 中式麻將 (Hong Kong style, simplified casual rules).

- 136 tiles, no flowers. Tile id 0..33: 0-8 萬, 9-17 筒, 18-26 索,
  27東 28南 29西 30北 31中 32發 33白.
- You are player 0 (dealer). Three bots.
- Claims: 胡 / 碰 / 槓 (明槓, with replacement draw) / 上 (chi, next player only).
  (No 暗槓/加槓/花牌 — casual rules.)
- Fan: 雞糊1 · 自摸+1 · 門前清+1 · 對對胡+1 · 混一色+2 · 清一色+4 · 十三幺13.
"""
import random

SUIT_OF = ["m"] * 9 + ["p"] * 9 + ["s"] * 9 + ["z"] * 7
IS_HONOR = lambda t: t >= 27
NAMES = (
    ["一萬", "二萬", "三萬", "四萬", "五萬", "六萬", "七萬", "八萬", "九萬"]
    + ["一筒", "二筒", "三筒", "四筒", "五筒", "六筒", "七筒", "八筒", "九筒"]
    + ["一索", "二索", "三索", "四索", "五索", "六索", "七索", "八索", "九索"]
    + ["東", "南", "西", "北", "紅中", "發財", "白板"]
)
ORPHANS = (0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33)
BOT_NAMES = ("西家·強伯", "南家·佳仔", "北家·霞姐")


# ------------------------------------------------------------- win logic ----
def _rec_sets(cs, need):
    """Can counts form exactly `need` melds (triplets/runs)?"""
    if need == 0:
        return all(v == 0 for v in cs)
    i = next((k for k, v in enumerate(cs) if v > 0), None)
    if i is None:
        return False
    if cs[i] >= 3:  # triplet
        cs[i] -= 3
        if _rec_sets(cs, need - 1):
            cs[i] += 3
            return True
        cs[i] += 3
    if i < 27 and SUIT_OF[i] != "z" and i % 9 <= 6:  # run
        if cs[i + 1] > 0 and cs[i + 2] > 0:
            cs[i] -= 1
            cs[i + 1] -= 1
            cs[i + 2] -= 1
            if _rec_sets(cs, need - 1):
                cs[i] += 1
                cs[i + 1] += 1
                cs[i + 2] += 1
                return True
            cs[i] += 1
            cs[i + 1] += 1
            cs[i + 2] += 1
    return False


def decompose(counts, melds_n):
    """Return (pair_tile, hand_sets) if counts form a winning hand, else None.
    hand_sets: list of ('pong', t) / ('chi', low_t)."""
    need = 4 - melds_n
    if sum(counts) != 3 * need + 2:
        return None
    cs = list(counts)
    for pt in range(34):
        if cs[pt] >= 2:
            cs[pt] -= 2
            if _rec_sets(cs, need):
                cs[pt] += 2
                # re-derive sets greedily for fan display
                sets_ = []
                tmp = list(counts)
                tmp[pt] -= 2
                for _ in range(need):
                    k = next(k for k, v in enumerate(tmp) if v > 0)
                    if tmp[k] >= 3:
                        tmp[k] -= 3
                        sets_.append(("pong", k))
                    else:
                        tmp[k] -= 1
                        tmp[k + 1] -= 1
                        tmp[k + 2] -= 1
                        sets_.append(("chi", k))
                return pt, sets_
            cs[pt] += 2
    return None


def can_win(counts, melds_n):
    return decompose(counts, melds_n) is not None


def is_thirteen_orphans(counts, melds_n):
    if melds_n:
        return False
    singles = sum(1 for t in ORPHANS if counts[t] >= 1)
    pair = any(counts[t] == 2 for t in ORPHANS)
    total = sum(counts[t] for t in ORPHANS)
    return singles == 13 and pair and total == 14


def fan_of(counts, melds, selfdraw):
    """Return (fan, [labels]). melds = list of (kind, tile)."""
    melds_n = len(melds)
    dec = decompose(counts, melds_n)
    thirteen = is_thirteen_orphans(counts, melds_n)
    fan, labels = 1, ["雞糊"]
    if thirteen:
        return 13, ["十三幺"]
    if dec is None:
        return fan, labels
    pair, hand_sets = dec
    all_sets = list(hand_sets) + [(k if k != "kong" else "pong", t) for k, t in melds]
    suits = {SUIT_OF[t] for _, t in all_sets} | {SUIT_OF[pair]}
    suits |= {SUIT_OF[t] for k, t in melds}
    if len(melds) == 0:
        fan += 1
        labels.append("門前清")
    if selfdraw:
        fan += 1
        labels.append("自摸")
    if all(k == "pong" for k, _ in all_sets):
        fan += 1
        labels.append("對對胡")
    nonz = {s for s in suits if s != "z"}
    if len(nonz) == 1 and "z" in suits:
        fan += 2
        labels.append("混一色")
    elif len(nonz) == 1 and "z" not in suits:
        fan += 4
        labels.append("清一色")
    return fan, labels


# ------------------------------------------------------------ game setup ----
def initial_game(names=None):
    wall = [t for t in range(34) for _ in range(4)]
    random.shuffle(wall)
    g = {
        "hands": [[0] * 34 for _ in range(4)],
        "melds": [[], [], [], []],
        "rivers": [[], [], [], []],
        "wall": wall,
        "turn": 0,
        "await": None,
        "over": None,
        "scores": [0, 0, 0, 0],
        "log": [],
        "voice": [],
        "names": names or ("你",) + BOT_NAMES,
    }
    for _ in range(13):
        for p in range(4):
            g["hands"][p][wall.pop(0)] += 1
    return g


def sorted_hand(counts):
    order = sorted(t for t in range(34) for _ in range(counts[t]))
    return order


def chi_options(counts, tile):
    """Possible chi sets using `tile` (you hold the other two)."""
    out = []
    if SUIT_OF[tile] == "z":
        return out
    low0 = tile - tile % 9
    for lo in (tile - 2, tile - 1, tile):
        if lo >= low0 and lo + 2 <= low0 + 8 and lo >= 0:
            others = [x for x in (lo, lo + 1, lo + 2) if x != tile]
            if all(counts[x] > 0 for x in others):
                out.append(lo)
    return out


def claim_options(g, p, tile, frm):
    """What player p can do with the just-discarded tile."""
    hand = g["hands"][p]
    opts = {}
    test = list(hand)
    test[tile] += 1
    if can_win(test, len(g["melds"][p])) or is_thirteen_orphans(test, len(g["melds"][p])):
        opts["win"] = True
    if hand[tile] == 3:
        opts["kong"] = True
    if hand[tile] == 2:
        opts["pong"] = True
    if frm == (p - 1) % 4:
        chis = chi_options(hand, tile)
        if chis:
            opts["chi"] = chis
    return opts


# ------------------------------------------------------------------- bots ----
def _hand_value(cs):
    """(complete_sets, partial_sets) — greedy extraction for bot evaluation."""
    tmp = list(cs)
    complete = 0
    for t in range(34):
        complete += tmp[t] // 3
        tmp[t] %= 3
    for t in range(27):
        if SUIT_OF[t] == "z":
            continue
        while t % 9 <= 6 and tmp[t] > 0 and tmp[t + 1] > 0 and tmp[t + 2] > 0:
            tmp[t] -= 1
            tmp[t + 1] -= 1
            tmp[t + 2] -= 1
            complete += 1
    partial = 0
    for t in range(34):
        if tmp[t] >= 2:
            partial += 1
            tmp[t] -= 2
    for t in range(27):
        if SUIT_OF[t] == "z":
            continue
        if t % 9 <= 7 and tmp[t] > 0 and tmp[t + 1] > 0:
            partial += 1
            tmp[t] -= 1
            tmp[t + 1] -= 1
        if tmp[t] > 0 and t % 9 <= 6 and tmp[t + 2] > 0:
            partial += 1
            tmp[t] -= 1
            tmp[t + 2] -= 1
    return complete, partial


def bot_discard(g, p):
    hand = g["hands"][p]
    melds_n = len(g["melds"][p])
    best, best_sc = None, -1e9
    for t in range(34):
        if hand[t] == 0:
            continue
        hand[t] -= 1
        complete, partial = _hand_value(hand)
        hand[t] += 1
        sc = complete * 100 + partial * 22
        if SUIT_OF[t] == "z" and complete + partial > 0:
            sc -= 8  # honors are harder to use
        elif t % 9 in (0, 8):
            sc -= 4  # terminals
        sc += random.uniform(0, 3)
        if sc > best_sc:
            best_sc, best = sc, t
    return best


def bot_claim(g, p, tile, frm):
    opts = claim_options(g, p, tile, frm)
    if "win" in opts:
        return "win"
    if "kong" in opts:
        return "kong"
    if "pong" in opts and random.random() < 0.85:
        return "pong"
    if "chi" in opts and random.random() < 0.35:
        return "chi"
    return None


# ------------------------------------------------------------ game engine ----
def _do_claim_meld(g, p, kind, tile, frm, chi_lo=None):
    hand = g["hands"][p]
    if kind == "pong":
        for _ in range(2):
            hand[tile] -= 1
        g["melds"][p].append(("pong", tile))
        g["log"].append(f"{g['names'][p]} 碰 {NAMES[tile]}")
        g["voice"].append("碰！")
    elif kind == "kong":
        for _ in range(3):
            hand[tile] -= 1
        g["melds"][p].append(("kong", tile))
        if len(g["wall"]) > 14:  # replacement draw
            g["hands"][p][g["wall"].pop(0)] += 1
        g["log"].append(f"{g['names'][p]} 槓 {NAMES[tile]}")
        g["voice"].append("槓！")
    elif kind == "chi":
        for x in (chi_lo, chi_lo + 1, chi_lo + 2):
            if x != tile:
                hand[x] -= 1
        g["melds"][p].append(("chi", chi_lo))
        g["log"].append(f"{g['names'][p]} 上 {NAMES[chi_lo]}{NAMES[chi_lo+1]}{NAMES[chi_lo+2]}")
        g["voice"].append("上！")
    g["turn"] = p
    g["meld_discard"] = p  # after a meld you discard WITHOUT drawing


def _win_game(g, p, tile, selfdraw):
    hand = list(g["hands"][p])
    if not selfdraw:
        hand[tile] += 1
    fan, labels = fan_of(hand, g["melds"][p], selfdraw)
    if is_thirteen_orphans(hand, len(g["melds"][p])):
        fan, labels = 13, ["十三幺"]
    g["scores"][p] += fan
    how = "自摸糊！" if selfdraw else "食糊！"
    g["over"] = {"winner": p, "tile": tile, "fan": fan, "labels": labels}
    g["log"].append(f"🎉 {g['names'][p]} {how} {NAMES[tile]}（{fan} 番：{'、'.join(labels)}）")
    g["voice"].append("自摸" if selfdraw else "食糊")


def _apply_discard(g, p, tile):
    g["hands"][p][tile] -= 1
    g["rivers"][p].append(tile)
    g["log"].append(f"{g['names'][p]} 打出 {NAMES[tile]}")


def _bots_claim_or_pass(g, tile, frm):
    """After a discard, let bots claim. Returns True if a bot claimed."""
    order = [(frm + k) % 4 for k in (1, 2, 3)]
    # wins first
    for p in order:
        if p == 0:
            continue
        if "win" in claim_options(g, p, tile, frm):
            _win_game(g, p, tile, False)
            return True
    for p in order:
        if p == 0:
            continue
        c = bot_claim(g, p, tile, frm)
        if c in ("pong", "kong"):
            _do_claim_meld(g, p, c, tile, frm)
            return True
        if c == "chi":
            lo = random.choice(claim_options(g, p, tile, frm)["chi"])
            _do_claim_meld(g, p, "chi", tile, frm, chi_lo=lo)
            return True
    return False


def _claim_window(g, p, dt):
    """After p discarded dt: human options first, then bots."""
    human_opts = claim_options(g, 0, dt, p)
    if human_opts:
        g["await"] = {"type": "claim", "tile": dt, "from": p, "opts": human_opts}
        return True
    if _bots_claim_or_pass(g, dt, p):
        return True
    g["turn"] = (p + 1) % 4
    return False


def advance(g):
    """Run the game until a human decision is needed or the hand ends."""
    while g["over"] is None:
        if g["await"]:
            return
        p = g["turn"]
        # after a meld: discard immediately, no draw
        if g.get("meld_discard") is not None:
            if p == 0:
                g["await"] = {"type": "discard", "drawn": None}
                return
            g["meld_discard"] = None
            dt = bot_discard(g, p)
            _apply_discard(g, p, dt)
            _claim_window(g, p, dt)
            continue
        if len(g["wall"]) <= 14:
            g["over"] = {"winner": None, "fan": 0, "labels": ["流局"]}
            g["log"].append("牌牆打完，流局。")
            g["voice"].append("流局")
            return
        tile = g["wall"].pop(0)
        g["hands"][p][tile] += 1
        if p == 0:  # human turn: decide discard / 自摸
            g["await"] = {"type": "discard", "drawn": tile}
            return
        # bot turn
        if can_win(g["hands"][p], len(g["melds"][p])) or is_thirteen_orphans(g["hands"][p], len(g["melds"][p])):
            _win_game(g, p, tile, True)
            return
        dt = bot_discard(g, p)
        _apply_discard(g, p, dt)
        _claim_window(g, p, dt)


def human_discard(g, tile):
    """Human discards `tile`; resolve bot claims; continue."""
    _apply_discard(g, 0, tile)
    g["await"] = None
    g["meld_discard"] = None
    _claim_window(g, 0, tile)
    advance(g)


def human_claim(g, kind, arg):
    """Human claimed the pending discard."""
    aw = g["await"]
    tile, frm = aw["tile"], aw["from"]
    g["await"] = None
    if kind == "win":
        _win_game(g, 0, tile, False)
        return
    if kind == "skip":
        if _bots_claim_or_pass(g, tile, frm):
            advance(g)
            return
        g["turn"] = (frm + 1) % 4
        advance(g)
        return
    _do_claim_meld(g, 0, kind, tile, frm, chi_lo=arg)
    g["await"] = {"type": "discard", "drawn": None}


def skip_human_turn(g):
    """Human chose not to claim; bots may still claim."""
    aw = g["await"]
    g["await"] = None
    tile, frm = aw["tile"], aw["from"]
    if _bots_claim_or_pass(g, tile, frm):
        advance(g)
        return
    g["turn"] = (frm + 1) % 4
    advance(g)

# -*- coding: utf-8 -*-
"""HK-MON 榕樹頭 — 魚蝦蟹 (Fish-Prawn-Crab dice game, HK street rules).

Six symbols: 魚 fish · 蝦 prawn · 蟹 crab · 雞 chicken · 葫蘆 gourd · 銅錢 coin.
Bet on symbols; banker rolls 3 dice. Symbol appears n times → win n× stake.
Triple (圍骰) → banker sweeps every bet (classic house rule).
Chips are saved to the player's account (fsc_chips).
"""
import random

SYMBOLS = [
    {"id": 0, "char": "魚", "emoji": "🐟", "color": "#1b3f8f", "zh": "魚", "en": "Fish", "ja": "魚", "ko": "물고기"},
    {"id": 1, "char": "蝦", "emoji": "🦐", "color": "#c0392b", "zh": "蝦", "en": "Prawn", "ja": "エビ", "ko": "새우"},
    {"id": 2, "char": "蟹", "emoji": "🦀", "color": "#1e8449", "zh": "蟹", "en": "Crab", "ja": "カニ", "ko": "게"},
    {"id": 3, "char": "雞", "emoji": "🐓", "color": "#b8860b", "zh": "雞", "en": "Chicken", "ja": "ニワトリ", "ko": "닭"},
    {"id": 4, "char": "葫", "emoji": "🍐", "color": "#6c3483", "zh": "葫蘆", "en": "Gourd", "ja": "ヒョウタン", "ko": "호리병"},
    {"id": 5, "char": "錢", "emoji": "🪙", "color": "#7d6608", "zh": "銅錢", "en": "Coin", "ja": "銅銭", "ko": "동전"},
]
CHIP_STEPS = [10, 50, 100, 500]
START_CHIPS = 1000


def new_game(chips=None):
    return {
        "chips": START_CHIPS if chips is None else max(0, int(chips)),
        "bets": {s["id"]: 0 for s in SYMBOLS},   # symbol_id -> stake
        "chip": 50,                               # current chip denomination
        "dice": None,                             # [a, b, c]
        "last_result": None,                      # {"net": ±n, "hits": {id: count}, "triple": bool}
        "voice": [],
        "rolls": 0,
        "net_peak": 0,
    }


def place_bet(g, symbol_id):
    if g["dice"] is not None:        # must clear the table before next round
        return
    sid = int(symbol_id)
    if g["chips"] < g["chip"]:
        return
    g["bets"][sid] += g["chip"]
    g["chips"] -= g["chip"]


def clear_bets(g):
    if g["dice"] is not None:
        return
    for sid, amt in g["bets"].items():
        if amt:
            g["chips"] += amt
            g["bets"][sid] = 0


def set_chip(g, value):
    if value in CHIP_STEPS:
        g["chip"] = value


def roll(g):
    if g["dice"] is not None:
        return
    total_stake = sum(g["bets"].values())
    if total_stake <= 0:
        return
    dice = [random.randrange(6) for _ in range(3)]
    g["dice"] = dice
    g["rolls"] += 1
    triple = len(set(dice)) == 1
    counts = {s: dice.count(s) for s in range(6)}
    returned = 0
    hits = {}
    for sid, stake in g["bets"].items():
        n = counts.get(sid, 0)
        if n > 0 and not triple:
            returned += stake * (1 + n)   # stake back + n times profit
            hits[sid] = n
    net = returned - total_stake
    g["chips"] += returned
    g["last_result"] = {"net": net, "hits": hits, "triple": triple,
                        "dice": dice,
                        "names": [SYMBOLS[d]["zh"] for d in dice]}
    if triple:
        g["voice"].append("圍骰！全收！")
    elif net > 0:
        g["voice"].append("中咗！")
        for sid, n in hits.items():
            g["voice"].append(f"{SYMBOLS[sid]['zh']}中{n}派")
    elif net == 0:
        g["voice"].append("打和")
    else:
        g["voice"].append("食晒")

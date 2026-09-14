# -*- coding: utf-8 -*-
"""HK-MON 榕樹頭 — 港式大富翁 (simplified HK Monopoly, you + 2 bots).

24-tile loop of Hong Kong locations. Buy / upgrade / collect rent,
機會 & 命運 cards, tax, start bonus. 30 rounds or last one standing.
"""
import random

START_BONUS = 2000
START_CASH = 15000
MAX_ROUNDS = 30
TAX = 800

# group: key, color
GROUPS = {
    "g1": "#c9a227", "g2": "#c0392b", "g3": "#1e8449",
    "g4": "#1b4f8f", "g5": "#6c3483",
}


def T(zh, en, group, price):
    return {"zh": zh, "en": en, "group": group, "price": price}


TILE_PROPS = {
    1: T("上環", "Sheung Wan", "g1", 700),
    3: T("中環", "Central", "g1", 1200),
    4: T("灣仔", "Wan Chai", "g1", 800),
    6: T("銅鑼灣", "Causeway Bay", "g1", 1000),
    8: T("深水埗", "Sham Shui Po", "g2", 700),
    10: T("旺角", "Mong Kok", "g2", 900),
    12: T("尖沙咀", "Tsim Sha Tsui", "g2", 1100),
    14: T("油麻地", "Yau Ma Tei", "g2", 850),
    15: T("蘭桂坊", "Lan Kwai Fong", "g5", 1050),
    16: T("廟街夜市", "Temple St Night Mkt", "g5", 950),
    18: T("荃灣", "Tsuen Wan", "g3", 600),
    19: T("沙田", "Sha Tin", "g3", 650),
    21: T("大埔", "Tai Po", "g3", 550),
    22: T("東涌", "Tung Chung", "g4", 650),
    23: T("長洲", "Cheung Chau", "g4", 450),
}

SPECIAL = {
    0: {"kind": "start", "zh": "起點", "en": "START"},
    2: {"kind": "chance", "zh": "機會", "en": "Chance"},
    5: {"kind": "fate", "zh": "命運", "en": "Fate"},
    7: {"kind": "tax", "zh": "稅務局", "en": "Tax Office"},
    9: {"kind": "chance", "zh": "機會", "en": "Chance"},
    11: {"kind": "park", "zh": "太平山", "en": "The Peak"},
    13: {"kind": "fate", "zh": "命運", "en": "Fate"},
    17: {"kind": "chance", "zh": "機會", "en": "Chance"},
    20: {"kind": "fate", "zh": "命運", "en": "Fate"},
}

CARDS = [
    {"text": {"zh": "政府派糖，+$800", "en": "Sweeteners! +$800", "ja": "景気対策 +$800", "ko": "정부 지원금 +$800"},
     "cash": 800},
    {"text": {"zh": "亂過馬路罰款，-$500", "en": "Jaywalking fine −$500", "ja": "横断罰金 −$500", "ko": "무단횡단 벌금 −$500"},
     "cash": -500},
    {"text": {"zh": "財爺派錢，+$1000", "en": "FS gives cash +$1000", "ja": "財政司 +$1000", "ko": "재정관료 +$1000"},
     "cash": 1000},
    {"text": {"zh": "MTR故障，後退 3 格", "en": "MTR breakdown, back 3", "ja": "MTR故障 3マス後退", "ko": "MTR 고장 3칸 후퇴"},
     "move": -3},
    {"text": {"zh": "搭叮叮兜風，前進 2 格", "en": "Tram ride, forward 2", "ja": "トラムで2マス前進", "ko": "트램타고 2칸 전진"},
     "move": 2},
    {"text": {"zh": "生日快樂！其他人各俾你 $300", "en": "Birthday! Everyone pays $300", "ja": "誕生日！全員$300", "ko": "생일! 전원 $300"},
     "birthday": 300},
    {"text": {"zh": "返起點領 $2000", "en": "Back to START +$2000", "ja": "スタートへ +$2000", "ko": "시작으로 +$2000"},
     "goto": 0},
]

BOT_NAMES = ("強伯", "霞姐")


def rent_of(t, level):
    return int(t["price"] * 0.4) * level


def upgrade_cost(t):
    return t["price"] // 2


def new_game():
    return {
        "pos": [0, 0, 0],
        "cash": [START_CASH, START_CASH, START_CASH],
        "own": {},          # tile -> {"owner": p, "level": 1}
        "round": 1,
        "turn": 0,          # whose roll is next (0 = human)
        "await": None,      # {"type":"buy"/"upgrade", "tile": t}
        "over": None,       # {"winner": p|-1, "reason": str}
        "dice": None,
        "log": [],
        "voice": [],
        "alive": [True, True, True],
        "names": ("你",) + BOT_NAMES,
    }


def tile_name(g, t):
    pr = TILE_PROPS.get(t)
    return pr["zh"] if pr else SPECIAL[t]["zh"]


def net_worth(g, p):
    return g["cash"][p] + sum(v["price"] for t, v in TILE_PROPS.items()
                              if g["own"].get(t, {}).get("owner") == p) + \
        sum(TILE_PROPS[t]["price"] // 2 * (v["level"] - 1)
            for t, v in g["own"].items() if v["owner"] == p)


def _pay(g, p, amount, to=None):
    """Pay; auto-sell upgrades/properties if short. Returns False if bankrupt."""
    g["cash"][p] -= amount
    while g["cash"][p] < 0:
        mine = [(t, v) for t, v in g["own"].items() if v["owner"] == p]
        if not mine:
            break
        # sell the cheapest upgrade first, else the cheapest property
        up = [(TILE_PROPS[t]["price"] // 2, t) for t, v in mine if v["level"] > 1]
        if up:
            gain, t = min(up)
            g["own"][t]["level"] -= 1
            g["cash"][p] += gain
            g["log"].append(f"{g['names'][p]} 賣出 {tile_name(g, t)} 一層樓，套現 ${gain}")
        else:
            gain, t = min((TILE_PROPS[t]["price"] // 2, t) for t, v in mine)
            del g["own"][t]
            g["cash"][p] += gain
            g["log"].append(f"{g['names'][p]} 賣樓！{tile_name(g, t)} 套現 ${gain}")
    if g["cash"][p] < 0:
        g["alive"][p] = False
        g["log"].append(f"💥 {g['names'][p]} 破產！")
        g["voice"].append("破產")
        for t, v in list(g["own"].items()):
            if v["owner"] == p:
                del g["own"][t]
        return False
    if to is not None:
        g["cash"][to] += amount
    return True


def _move(g, p, steps):
    g["pos"][p] = (g["pos"][p] + steps) % 24
    if g["pos"][p] < steps or (steps < 0 and g["pos"][p] >= 24 + steps):
        pass
    # start bonus when passing tile 0
    old = g["pos"][p] - steps
    crossed = (old + steps) >= 24 or (old + steps < 0 and steps < 0)
    if (old % 24) + steps >= 24:
        g["cash"][p] += START_BONUS
        g["log"].append(f"{g['names'][p]} 經過起點 +${START_BONUS}")
    return g["pos"][p]


def _land(g, p, human_stops=False):
    """Resolve landing. Returns await dict if the human must decide."""
    t = g["pos"][p]
    if t in TILE_PROPS:
        prop = TILE_PROPS[t]
        own = g["own"].get(t)
        if own is None:
            if human_stops:
                g["await"] = {"type": "buy", "tile": t}
                return g["await"]
            # bot
            if g["cash"][p] >= prop["price"] + 800:
                g["cash"][p] -= prop["price"]
                g["own"][t] = {"owner": p, "level": 1}
                g["log"].append(f"{g['names'][p]} 買入 {prop['zh']} ${prop['price']}")
                g["voice"].append(f"買起{prop['zh']}")
            return None
        if own["owner"] == p:
            cost = upgrade_cost(prop)
            if own["level"] < 3 and g["cash"][p] >= cost + 800:
                if human_stops:
                    g["await"] = {"type": "upgrade", "tile": t}
                    return g["await"]
                if random.random() < 0.5:
                    g["cash"][p] -= cost
                    g["own"][t]["level"] += 1
                    g["log"].append(f"{g['names'][p]} 升級 {prop['zh']} 至 Lv{own['level'] + 1}")
                return None
            return None
        if g["alive"][own["owner"]]:
            rent = rent_of(prop, own["level"])
            # monopoly bonus: own whole group → double rent
            grp = [tt for tt, vv in TILE_PROPS.items() if vv["group"] == prop["group"]]
            if all(g["own"].get(tt, {}).get("owner") == own["owner"] for tt in grp):
                rent *= 2
            g["log"].append(f"{g['names'][p]} 俾租 ${rent} 俾 {g['names'][own['owner']]}")
            g["voice"].append(f"俾租{rent}蚊")
            _pay(g, p, rent, to=own["owner"])
        return None
    if t in SPECIAL:
        kind = SPECIAL[t]["kind"]
        if kind == "tax":
            g["log"].append(f"{g['names'][p]} 交稅 ${TAX}")
            _pay(g, p, TAX)
        elif kind in ("chance", "fate"):
            card = random.choice(CARDS)
            g["log"].append(f"{g['names'][p]} 抽到：{card['text']['zh']}")
            g["voice"].append(card["text"]["zh"])
            if "cash" in card:
                if card["cash"] >= 0:
                    g["cash"][p] += card["cash"]
                else:
                    _pay(g, p, -card["cash"])
            if "move" in card:
                _move(g, p, card["move"])
                _land(g, p, human_stops=False) if p != 0 else _land(g, p, human_stops=True)
                return g["await"]
            if "birthday" in card:
                for q in range(3):
                    if q != p and g["alive"][q]:
                        _pay(g, q, card["birthday"], to=p)
            if "goto" in card:
                g["pos"][p] = card["goto"]
                g["cash"][p] += START_BONUS
                _land(g, p, human_stops=(p == 0))
                return g["await"]
        # park/start: nothing
    return None


def roll(g):
    """Human rolls; then bots phase unless a decision is awaited."""
    if g["await"] or g["over"]:
        return
    _do_roll(g, 0)
    if g["over"]:
        return
    if not g["await"]:
        _bots_phase(g)


def _do_roll(g, p):
    d1, d2 = random.randrange(1, 7), random.randrange(1, 7)
    g["dice"] = [d1, d2]
    g["log"].append(f"🎲 {g['names'][p]} 擲到 {d1}+{d2}")
    g["voice"].append(f"擲到{d1}點{d2}點")
    _move(g, p, d1 + d2)
    _land(g, p, human_stops=(p == 0))


def decide(g, kind, arg=None):
    """Human resolves a buy/upgrade await."""
    aw = g["await"]
    if not aw:
        return
    t = aw["tile"]
    prop = TILE_PROPS[t]
    if kind == "buy" and aw["type"] == "buy" and g["cash"][0] >= prop["price"]:
        g["cash"][0] -= prop["price"]
        g["own"][t] = {"owner": 0, "level": 1}
        g["log"].append(f"你 買入 {prop['zh']} ${prop['price']}")
        g["voice"].append(f"買起{prop['zh']}")
    elif kind == "upgrade" and aw["type"] == "upgrade" and g["cash"][0] >= upgrade_cost(prop):
        g["cash"][0] -= upgrade_cost(prop)
        g["own"][t]["level"] += 1
        g["log"].append(f"你 升級 {prop['zh']} 至 Lv{g['own'][t]['level']}")
        g["voice"].append("升級")
    g["await"] = None
    _bots_phase(g)


def skip(g):
    g["await"] = None
    _bots_phase(g)


def _bots_phase(g):
    for p in (1, 2):
        if not g["alive"][p]:
            continue
        _do_roll(g, p)
        if g["await"]:            # bots never await; safety
            g["await"] = None
        if g["over"]:
            return
    _end_round(g)


def _end_round(g):
    if any(not a for a in g["alive"]):
        if not g["alive"][0]:
            others = [p for p in range(1, 3) if g["alive"][p]]
            winner = max(others, key=lambda p: net_worth(g, p)) if others else -1
            g["over"] = {"winner": winner, "reason": "你破產咗"}
            g["voice"].append("破產")
            return
        alive = [p for p in range(3) if g["alive"][p]]
        if len(alive) == 1:
            g["over"] = {"winner": alive[0], "reason": "最後生存"}
            g["voice"].append("勝出")
            return
    if g["round"] >= MAX_ROUNDS:
        worth = [(net_worth(g, p), p) for p in range(3) if g["alive"][p]]
        worth.sort(reverse=True)
        g["over"] = {"winner": worth[0][1] if worth else -1,
                     "reason": f"{MAX_ROUNDS} 回合完，最多資產"}
        g["voice"].append("遊戲結束")
        return
    g["round"] += 1
    g["turn"] = 0
    g["dice"] = None


def check_over(g):
    if not g["alive"][0]:
        g["over"] = {"winner": 1 if g["alive"][1] else (2 if g["alive"][2] else -1),
                     "reason": "你破產咗"}

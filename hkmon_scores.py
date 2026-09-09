# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — persistent scoreboard (file-backed, shared by all users).

Stored next to the app; survives across sessions/visitors while the app
container is alive (cleared if the cloud container restarts)."""
import json
import os
import threading
import time

_LOCK = threading.Lock()
_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.json")


def _load():
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(data):
    tmp = _PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, _PATH)


def _key(name):
    return (name or "").strip().lower()[:16]


def record(name, win, pvp=False):
    name = (name or "").strip()[:16]
    if not name:
        return
    k = _key(name)
    with _LOCK:
        data = _load()
        rec = data.get(k) or {"name": name, "wins": 0, "losses": 0,
                              "streak": 0, "best": 0, "games": 0,
                              "pvp_wins": 0, "ts": 0}
        rec["name"] = name
        rec["games"] += 1
        if win:
            rec["wins"] += 1
            rec["streak"] += 1
            rec["best"] = max(rec["best"], rec["streak"])
            if pvp:
                rec["pvp_wins"] += 1
        else:
            rec["losses"] += 1
            rec["streak"] = 0
        rec["ts"] = time.time()
        data[k] = rec
        _save(data)


def get(name):
    with _LOCK:
        return _load().get(_key(name))


def top(n=10):
    with _LOCK:
        data = _load()
    recs = sorted(data.values(),
                  key=lambda r: (r.get("wins", 0), r.get("best", 0)), reverse=True)
    return recs[:n]

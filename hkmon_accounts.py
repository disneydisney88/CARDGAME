# -*- coding: utf-8 -*-
"""HK-MON — user accounts + persistent save (file-backed).

Stored next to the app (accounts.json). Passwords are salted SHA-256 —
casual protection for a free game, not bank-grade. Each account carries
game stats + UI settings (language / sound) so a login restores your save.
"""
import hashlib
import json
import os
import secrets
import threading
import time

_LOCK = threading.Lock()
_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.json")

DEFAULT_STATS = {
    "wins": 0, "losses": 0, "streak": 0, "best": 0, "games": 0,
    "pvp_wins": 0, "mj_score": 0, "xq_wins": 0, "xq_losses": 0,
}


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


def _hash(pw, salt):
    return hashlib.sha256((salt + pw).encode("utf-8")).hexdigest()


def _new_rec(name, pw):
    salt = secrets.token_hex(8)
    rec = {"name": name.strip()[:16], "salt": salt, "pw": _hash(pw, salt),
           "created": time.time(), "lang": None, "sound": None}
    rec.update(dict(DEFAULT_STATS))
    return rec


def register(name, pw):
    name = (name or "").strip()[:16]
    if len(name) < 2 or len(pw or "") < 2:
        return False, "short"
    k = _key(name)
    with _LOCK:
        data = _load()
        if k in data:
            return False, "exists"
        data[k] = _new_rec(name, pw)
        _save(data)
    return True, "ok"


def login(name, pw):
    name = (name or "").strip()[:16]
    k = _key(name)
    with _LOCK:
        rec = _load().get(k)
    if not rec:
        return False, "nouser"
    if _hash(pw or "", rec.get("salt", "")) != rec.get("pw"):
        return False, "badpw"
    return True, "ok"


def _mutate(name, fn):
    k = _key(name)
    with _LOCK:
        data = _load()
        rec = data.get(k)
        if not rec:
            return None
        fn(rec)
        rec["ts"] = time.time()
        _save(data)
        return json.loads(json.dumps(rec))


def update_stats(name, **deltas):
    """Add deltas, e.g. update_stats(u, wins=1, games=1)."""
    def fn(rec):
        for k, v in deltas.items():
            if k in rec and isinstance(rec[k], (int, float)):
                rec[k] += v
            else:
                rec[k] = v
        if "wins" in deltas and deltas["wins"] > 0:
            rec["streak"] = rec.get("streak", 0) + 1
            rec["best"] = max(rec.get("best", 0), rec["streak"])
        elif "losses" in deltas and deltas["losses"] > 0:
            rec["streak"] = 0
    return _mutate(name, fn)


def set_stats(name, **values):
    """Set absolute values, e.g. set_stats(u, streak=3)."""
    def fn(rec):
        rec.update(values)
    return _mutate(name, fn)


def save_settings(name, lang=None, sound=None):
    def fn(rec):
        if lang:
            rec["lang"] = lang
        if sound is not None:
            rec["sound"] = bool(sound)
    return _mutate(name, fn)


def get(name):
    with _LOCK:
        rec = _load().get(_key(name))
    return json.loads(json.dumps(rec)) if rec else None


def stats_of(name):
    rec = get(name) or {}
    out = dict(DEFAULT_STATS)
    out.update({k: v for k, v in rec.items() if k in DEFAULT_STATS})
    return out


def top(n=10, key="wins"):
    with _LOCK:
        data = _load()
    recs = [r for r in data.values() if isinstance(r, dict)]
    return sorted(recs, key=lambda r: (r.get(key, 0), r.get("best", 0)), reverse=True)[:n]

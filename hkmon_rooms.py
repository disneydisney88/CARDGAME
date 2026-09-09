# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — tiny file-backed room store for online PvP.

On Streamlit Community Cloud every visitor of an app is served by the same
container, so a JSON file next to the app is a shared store between all
sessions (it is wiped when the container restarts — fine for casual play).

All access goes through a process-wide lock with atomic writes, so
concurrent sessions don't corrupt the file.
"""
import json
import os
import secrets
import string
import threading
import time

_LOCK = threading.Lock()
_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rooms.json")
TTL = 3 * 3600  # rooms die 3h after last activity
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _load():
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def _save(data):
    tmp = _PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, _PATH)


def _sweep(data):
    now = time.time()
    dead = [c for c, r in data.items()
            if now - r.get("last_seen", 0) > TTL]
    for c in dead:
        data.pop(c, None)


def _new_code(data):
    for _ in range(50):
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(4))
        if code not in data:
            return code
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(5))


def create_room(lang, deck_id):
    with _LOCK:
        data = _load()
        _sweep(data)
        code = _new_code(data)
        data[code] = {
            "created": time.time(), "last_seen": time.time(),
            "status": "waiting",          # waiting -> playing -> finished
            "version": 1,
            "p1": {"deck": deck_id, "ready": True},
            "p2": None,
            "rematch_p2": False,
            "state": None,
            "requests": [],
        }
        _save(data)
        return code


def join_room(code, deck_id, name=""):
    code = (code or "").strip().upper()
    with _LOCK:
        data = _load()
        room = data.get(code)
        if not room or room["p2"] is not None:
            return False
        room["p2"] = {"deck": deck_id, "ready": True,
                      "name": (name or "").strip()[:12]}
        room["last_seen"] = time.time()
        _save(data)
        return True


def touch(code):
    with _LOCK:
        data = _load()
        room = data.get(code)
        if room:
            room["last_seen"] = time.time()
            _save(data)


def read_room(code):
    with _LOCK:
        data = _load()
        room = data.get((code or "").strip().upper())
        return json.loads(json.dumps(room)) if room else None


def post_request(code, side, kind, arg=None):
    with _LOCK:
        data = _load()
        room = data.get((code or "").strip().upper())
        if room:
            room["requests"].append({"side": side, "kind": kind,
                                     "arg": arg, "ts": time.time()})
            room["last_seen"] = time.time()
            _save(data)


def consume_requests(code):
    with _LOCK:
        data = _load()
        room = data.get((code or "").strip().upper())
        if not room:
            return []
        reqs = room.get("requests", [])
        room["requests"] = []
        if reqs:
            room["last_seen"] = time.time()
        _save(data)
        return reqs


def sync_state(code, state, status=None):
    """Host publishes the authoritative battle state (bumps version)."""
    with _LOCK:
        data = _load()
        room = data.get((code or "").strip().upper())
        if not room:
            return
        room["state"] = json.loads(json.dumps(state))
        room["version"] = room.get("version", 0) + 1
        if status:
            room["status"] = status
        room["last_seen"] = time.time()
        _save(data)


def read_state(code):
    room = read_room(code)
    if not room:
        return None, -1
    return room.get("state"), room.get("version", -1)


def rematch_p2_flag(code, requested=False):
    """Guest asks for rematch / host checks the flag."""
    with _LOCK:
        data = _load()
        room = data.get((code or "").strip().upper())
        if not room:
            return False
        if requested:
            room["rematch_p2"] = True
            room["last_seen"] = time.time()
            _save(data)
            return True
        return bool(room.get("rematch_p2"))


def clear_rematch(code):
    with _LOCK:
        data = _load()
        room = data.get((code or "").strip().upper())
        if room:
            room["rematch_p2"] = False
            room["requests"] = []
            _save(data)

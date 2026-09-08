# -*- coding: utf-8 -*-
"""HK-MON 港精靈 — tiny 8-bit sound effects.

Sounds are synthesised at first use (pure stdlib: wave/struct/math),
cached as base64 WAV, and played through a Custom Component v2 that
calls Audio.play() in the page context (so it works after the user's
click — no download UI, no extra dependencies).
"""
import base64
import io
import math
import random
import struct
import wave

import streamlit as st

SR = 11025
VOL = 0.32
_CACHE = {}


# ------------------------------------------------------------- synthesis ----
def _samples(dur):
    return bytearray(int(SR * dur))


def _write_tone(buf, start, dur, f0, f1=None, kind="sine", vol=VOL):
    f1 = f0 if f1 is None else f1
    n = int(SR * dur)
    for i in range(n):
        t = i / SR
        f = f0 + (f1 - f0) * (i / n)
        ph = 2 * math.pi * f * t
        if kind == "square":
            v = 1.0 if math.sin(ph) >= 0 else -1.0
        elif kind == "saw":
            v = 2 * ((f * t) % 1.0) - 1.0
        elif kind == "tri":
            v = 2 / math.pi * math.asin(math.sin(ph))
        else:
            v = math.sin(ph)
        idx = start + i
        if 0 <= idx < len(buf):
            decay = 1.0 - (i / n) * 0.35
            buf[idx] = max(0, min(255, 128 + int(v * 127 * vol * decay)))


def _write_noise(buf, start, dur, vol=VOL):
    n = int(SR * dur)
    v = 0
    for i in range(n):
        v = int(0.6 * v + 0.4 * random.randint(-127, 127))
        idx = start + i
        if 0 <= idx < len(buf):
            decay = 1.0 - i / n
            buf[idx] = max(0, min(255, 128 + int(v / 127 * 127 * vol * decay)))


def _wav_bytes(buf):
    bio = io.BytesIO()
    w = wave.open(bio, "wb")
    w.setnchannels(1)
    w.setsampwidth(1)
    w.setframerate(SR)
    w.writeframes(bytes(buf))
    w.close()
    return bio.getvalue()


def _build(name):
    if name == "click":
        buf = _samples(0.05)
        _write_tone(buf, 0, 0.05, 1500, 1200, "square")
    elif name == "attack":
        buf = _samples(0.24)
        _write_tone(buf, 0, 0.16, 700, 180, "saw")
        _write_noise(buf, 160, 0.08, VOL * 0.8)
    elif name == "special":
        buf = _samples(0.34)
        _write_tone(buf, 0, 0.14, 950, 420, "sine", VOL * 1.2)
        _write_tone(buf, 140, 0.10, 220, 160, "square", VOL)
        _write_noise(buf, 240, 0.10, VOL * 0.9)
    elif name == "crit":
        buf = _samples(0.40)
        _write_tone(buf, 0, 0.16, 700, 150, "saw", VOL * 1.2)
        _write_noise(buf, 150, 0.10, VOL)
        _write_tone(buf, 250, 0.15, 1300, 1900, "sine", VOL * 1.1)
    elif name == "ko":
        buf = _samples(0.38)
        _write_tone(buf, 0, 0.38, 420, 55, "square", VOL * 1.1)
    elif name == "heal":
        buf = _samples(0.30)
        _write_tone(buf, 0, 0.09, 523, 523, "sine", VOL * 1.2)
        _write_tone(buf, 90, 0.09, 659, 659, "sine", VOL * 1.2)
        _write_tone(buf, 180, 0.12, 784, 784, "sine", VOL * 1.2)
    elif name == "buff":
        buf = _samples(0.20)
        _write_tone(buf, 0, 0.20, 300, 950, "square", VOL)
    elif name == "shield":
        buf = _samples(0.22)
        _write_tone(buf, 0, 0.08, 950, 900, "square", VOL)
        _write_tone(buf, 110, 0.11, 760, 700, "square", VOL)
    elif name == "para":
        buf = _samples(0.24)
        for k in range(3):
            _write_tone(buf, k * 80, 0.06, 130, 120, "square", VOL * 1.15)
    elif name == "burn":
        buf = _samples(0.30)
        _write_noise(buf, 0, 0.30, VOL)
    elif name == "switch":
        buf = _samples(0.14)
        _write_tone(buf, 0, 0.14, 480, 1050, "sine", VOL * 1.15)
    elif name == "win":
        buf = _samples(0.75)
        _write_tone(buf, 0, 0.13, 523, 523, "sine", VOL * 1.25)
        _write_tone(buf, 130, 0.13, 659, 659, "sine", VOL * 1.25)
        _write_tone(buf, 260, 0.13, 784, 784, "sine", VOL * 1.25)
        _write_tone(buf, 390, 0.36, 1046, 1046, "sine", VOL * 1.3)
    elif name == "lose":
        buf = _samples(0.72)
        _write_tone(buf, 0, 0.18, 392, 392, "sine", VOL * 1.2)
        _write_tone(buf, 180, 0.18, 330, 330, "sine", VOL * 1.2)
        _write_tone(buf, 360, 0.36, 262, 240, "sine", VOL * 1.2)
    else:
        buf = _samples(0.05)
        _write_tone(buf, 0, 0.05, 1000, 1000, "square")
    return base64.b64encode(_wav_bytes(buf)).decode()


def b64(name):
    if name not in _CACHE:
        _CACHE[name] = _build(name)
    return _CACHE[name]


# ------------------------------------------------------------ CCv2 player ---
# Declared once at import. The JS runs in the app's page context, so the
# browser's sticky user activation (any prior click) allows playback.
_PLAYER = st.components.v2.component(
    "hkmon_sfx_player",
    html="<div style='display:none'></div>",
    js=(
        "export default function (component) {\n"
        "  const d = component.data || {}\n"
        "  if (!d.src) return\n"
        "  try {\n"
        "    const a = new Audio(d.src)\n"
        "    a.volume = typeof d.vol === 'number' ? d.vol : 0.4\n"
        "    a.play().catch(() => {})\n"
        "  } catch (e) {}\n"
        "  return {}\n"
        "}\n"
    ),
)

_SFX_SEQ = 0


def play(name, volume=0.42):
    """Mount one shot of the given sound. Unique key each call so the
    component re-runs and the sound plays on every event."""
    global _SFX_SEQ
    _SFX_SEQ += 1
    try:
        _PLAYER(
            data={"src": "data:audio/wav;base64," + b64(name), "vol": volume},
            key=f"hkmon-sfx-{name}-{_SFX_SEQ}",
        )
    except Exception:
        pass

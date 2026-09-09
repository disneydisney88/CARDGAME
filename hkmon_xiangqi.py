# -*- coding: utf-8 -*-
"""HK-MON 榕樹頭 — 象棋 (Xiangqi) rules + AI.

Board: list of 90 cells (index = row*9+col). Row 0 is the top (Black's
back rank), row 9 the bottom (Red's back rank). Cell = None or (side, kind)
where side 'r'/'b' and kind in K A B N R C P.
"""
import random

RED, BLACK = "r", "b"

CHAR = {
    ("r", "K"): "帥", ("r", "A"): "仕", ("r", "B"): "相",
    ("r", "N"): "傌", ("r", "R"): "俥", ("r", "C"): "炮", ("r", "P"): "兵",
    ("b", "K"): "將", ("b", "A"): "士", ("b", "B"): "象",
    ("b", "N"): "馬", ("b", "R"): "車", ("b", "C"): "砲", ("b", "P"): "卒",
}
VAL = {"K": 10000, "R": 90, "C": 45, "N": 40, "B": 20, "A": 20, "P": 10}
INF = 10 ** 9


def initial_board():
    b = [None] * 90
    back = ["R", "N", "B", "A", "K", "A", "B", "N", "R"]
    for c, k in enumerate(back):
        b[c] = (BLACK, k)
        b[9 * 9 + c] = (RED, k)
    for c in (1, 7):
        b[2 * 9 + c] = (BLACK, "C")
        b[7 * 9 + c] = (RED, "C")
    for c in (0, 2, 4, 6, 8):
        b[3 * 9 + c] = (BLACK, "P")
        b[6 * 9 + c] = (RED, "P")
    return b


def in_palace(r, c, side):
    if not (3 <= c <= 5):
        return False
    return r <= 2 if side == BLACK else r >= 7


def pseudo_moves(board, pos):
    """Pseudo-legal target squares (includes flying-general capture)."""
    piece = board[pos]
    if not piece:
        return []
    side, kind = piece
    r, c = divmod(pos, 9)
    out = []

    def add(rr, cc):
        if 0 <= rr < 10 and 0 <= cc < 9:
            t = board[rr * 9 + cc]
            if t is None or t[0] != side:
                out.append(rr * 9 + cc)

    if kind == "K":
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if in_palace(rr, cc, side):
                add(rr, cc)
        for dr in (-1, 1):  # flying general: capture opposing king on open file
            rr = r + dr
            while 0 <= rr < 10:
                t = board[rr * 9 + c]
                if t is not None:
                    if t[0] != side and t[1] == "K":
                        out.append(rr * 9 + c)
                    break
                rr += dr
    elif kind == "A":
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            rr, cc = r + dr, c + dc
            if in_palace(rr, cc, side):
                add(rr, cc)
    elif kind == "B":
        for dr, dc in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            rr, cc = r + dr, c + dc
            er, ec = r + dr // 2, c + dc // 2
            if 0 <= rr < 10 and 0 <= cc < 9 and board[er * 9 + ec] is None:
                if (side == RED and rr >= 5) or (side == BLACK and rr <= 4):
                    add(rr, cc)
    elif kind == "N":
        for dr, dc, lr, lc in ((2, 1, 1, 0), (2, -1, 1, 0), (-2, 1, -1, 0), (-2, -1, -1, 0),
                               (1, 2, 0, 1), (-1, 2, 0, 1), (1, -2, 0, -1), (-1, -2, 0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < 10 and 0 <= cc < 9 and board[(r + lr) * 9 + (c + lc)] is None:
                add(rr, cc)
    elif kind in ("R", "C"):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            jumped = False
            while 0 <= rr < 10 and 0 <= cc < 9:
                t = board[rr * 9 + cc]
                if kind == "R":
                    if t is None:
                        out.append(rr * 9 + cc)
                    else:
                        if t[0] != side:
                            out.append(rr * 9 + cc)
                        break
                else:
                    if not jumped:
                        if t is None:
                            out.append(rr * 9 + cc)
                        else:
                            jumped = True
                    elif t is not None:
                        if t[0] != side:
                            out.append(rr * 9 + cc)
                        break
                rr += dr
                cc += dc
    elif kind == "P":
        fwd = -1 if side == RED else 1
        add(r + fwd, c)
        crossed = (r <= 4) if side == RED else (r >= 5)
        if crossed:
            add(r, c - 1)
            add(r, c + 1)
    return out


def find_king(board, side):
    for i, p in enumerate(board):
        if p and p[0] == side and p[1] == "K":
            return i
    return None


def kings_facing(board):
    kr, kb = find_king(board, RED), find_king(board, BLACK)
    if kr is None or kb is None or kr % 9 != kb % 9:
        return False
    c = kr % 9
    r1, r2 = sorted((kr // 9, kb // 9))
    for rr in range(r1 + 1, r2):
        if board[rr * 9 + c] is not None:
            return False
    return True


def in_check(board, side):
    k = find_king(board, side)
    if k is None:
        return True
    foe = BLACK if side == RED else RED
    for i, p in enumerate(board):
        if p and p[0] == foe and k in pseudo_moves(board, i):
            return True
    return kings_facing(board)


def legal_moves(board, side):
    out = []
    for i, p in enumerate(board):
        if p and p[0] == side:
            for t in pseudo_moves(board, i):
                cap = board[t]
                board[t] = board[i]
                board[i] = None
                ok = not in_check(board, side)
                board[i] = board[t]
                board[t] = cap
                if ok:
                    out.append((i, t))
    return out


def apply_move(board, mv):
    """Returns captured piece (for undo/voice)."""
    i, t = mv
    cap = board[t]
    board[t] = board[i]
    board[i] = None
    return cap


def evaluate(board):
    """Material score from Red's perspective, with small positional terms."""
    s = 0
    for i, p in enumerate(board):
        if not p:
            continue
        v = VAL[p[1]]
        r = i // 9
        if p[1] == "P":
            if (p[0] == RED and r <= 4) or (p[0] == BLACK and r >= 5):
                v += 10
        elif p[1] in ("N", "C"):
            c = i % 9
            if 2 <= c <= 6:
                v += 3
        s += v if p[0] == RED else -v
    return s


def _search(board, side, depth, alpha, beta):
    """Pseudo-legal alpha-beta; king capture = mate (avoids legality scan)."""
    if depth == 0:
        return evaluate(board) if side == RED else -evaluate(board)
    foe = BLACK if side == RED else RED
    best = -INF
    moves = []
    for i, p in enumerate(board):
        if p and p[0] == side:
            for t in pseudo_moves(board, i):
                cap = board[t]
                pri = VAL[cap[1]] if cap else 0
                moves.append((pri, i, t))
    moves.sort(reverse=True)
    if not moves:
        return -100000 - depth
    for _, i, t in moves:
        cap = board[t]
        if cap and cap[1] == "K":
            return 100000 + depth
        board[t] = board[i]
        board[i] = None
        sc = -_search(board, foe, depth - 1, -beta, -alpha)
        board[i] = board[t]
        board[t] = cap
        if sc > best:
            best = sc
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best


def best_move(board, side, depth=3, jitter=0):
    """Root search over legal moves. Returns (i, t) or None."""
    moves = legal_moves(board, side)
    if not moves:
        return None
    foe = BLACK if side == RED else RED
    scored = []
    for i, t in moves:
        pri = VAL[board[t][1]] if board[t] else 0
        scored.append((pri, i, t))
    scored.sort(reverse=True)
    best, best_sc = None, -INF
    alpha = -INF
    for _, i, t in scored:
        cap = board[t]
        board[t] = board[i]
        board[i] = None
        sc = -_search(board, foe, depth - 1, -INF, -alpha)
        board[i] = board[t]
        board[t] = cap
        if jitter:
            sc += random.uniform(-jitter, jitter)
        if sc > best_sc:
            best_sc, best = sc, (i, t)
            alpha = max(alpha, sc)
    return best

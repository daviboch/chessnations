# piece_attacks.py

from .piece_movement_common import (
    BOARD_SIZE,
    EMPTY,
    WHITE_PAWN, BLACK_PAWN,
    WHITE_SHAMAN, BLACK_SHAMAN,
    WHITE_BISON, BLACK_BISON,
    WHITE_TOTEM, BLACK_TOTEM,
    WHITE_ROOK, BLACK_ROOK,
    WHITE_KNIGHT, BLACK_KNIGHT,
    WHITE_BISHOP, BLACK_BISHOP,
    WHITE_QUEEN, BLACK_QUEEN,
    WHITE_KING, BLACK_KING,
    is_white_piece, is_black_piece,
    in_bounds
)

def is_square_attacked(bstate, row, col, by_white):
    """
    Ritorna True se la casella (row, col) è attaccata da un pezzo
    del colore specificato (by_white = True => attaccata dai bianchi).
    """
    for rr in range(BOARD_SIZE):
        for cc in range(BOARD_SIZE):
            piece = bstate[rr][cc]
            if piece == EMPTY:
                continue
            if by_white:
                if not is_white_piece(piece):
                    continue
            else:
                if not is_black_piece(piece):
                    continue

            # Genera pseudo-attacchi di quel pezzo specifico
            attacks = _get_pseudo_attacks_of_piece(bstate, rr, cc)
            if (row, col) in attacks:
                return True
    return False

def _get_pseudo_attacks_of_piece(bstate, rr, cc):
    """
    Restituisce le caselle che il pezzo in (rr,cc) potrebbe "attaccare" (senza considerare scacco al proprio Re).
    Richiama le varianti `_pseudo_*` in base al tipo di pezzo.
    """
    p = bstate[rr][cc]
    if p in (WHITE_BISON, BLACK_BISON):
        return _pseudo_bison_attacks(bstate, rr, cc)
    elif p in (WHITE_TOTEM, BLACK_TOTEM):
        return _pseudo_totem_attacks(bstate, rr, cc)
    elif p in (WHITE_PAWN, BLACK_PAWN):
        return _pseudo_pawn_attacks(bstate, rr, cc)
    elif p in (WHITE_ROOK, BLACK_ROOK):
        return _pseudo_rook_attacks(bstate, rr, cc)
    elif p in (WHITE_KNIGHT, BLACK_KNIGHT):
        return _pseudo_knight_attacks(rr, cc)
    elif p in (WHITE_BISHOP, BLACK_BISHOP):
        return _pseudo_bishop_attacks(bstate, rr, cc)
    elif p in (WHITE_SHAMAN, BLACK_SHAMAN):
        return _pseudo_shaman_attacks(bstate, rr, cc)
    elif p in (WHITE_QUEEN, BLACK_QUEEN):
        ro = _pseudo_rook_attacks(bstate, rr, cc)
        bi = _pseudo_bishop_attacks(bstate, rr, cc)
        return ro + bi
    elif p in (WHITE_KING, BLACK_KING):
        return _pseudo_king_attacks(rr, cc)
    return []

def _pseudo_bison_attacks(bstate, r, c):
    # Come una Rook “infinita”: si ferma quando incontra un pezzo
    out = []
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    for (dr, dc) in directions:
        rr, cc = r, c
        while True:
            rr += dr
            cc += dc
            if not in_bounds(rr, cc):
                break
            out.append((rr, cc))
            if bstate[rr][cc] != EMPTY:
                break
    return out

def _pseudo_pawn_attacks(bstate, r, c):
    p = bstate[r][c]
    pIsWhite = is_white_piece(p)
    direction = -1 if pIsWhite else 1
    rr = r + direction
    out = []
    for dc in [-1, 1]:
        cc = c + dc
        if in_bounds(rr, cc):
            out.append((rr, cc))
    return out

def _pseudo_rook_attacks(bstate, r, c):
    out = []
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    for (dr, dc) in dirs:
        rr, cc = r, c
        while True:
            rr += dr
            cc += dc
            if not in_bounds(rr, cc):
                break
            out.append((rr, cc))
            if bstate[rr][cc] != EMPTY:
                break
    return out

def _pseudo_knight_attacks(r, c):
    out = []
    steps = [(-2,-1), (-2,1), (2,-1), (2,1), (1,-2), (1,2), (-1,-2), (-1,2)]
    for (dr, dc) in steps:
        rr, cc = r+dr, c+dc
        if in_bounds(rr, cc):
            out.append((rr, cc))
    return out

def _pseudo_bishop_attacks(bstate, r, c):
    out = []
    dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for (dr, dc) in dirs:
        rr, cc = r, c
        while True:
            rr += dr
            cc += dc
            if not in_bounds(rr, cc):
                break
            out.append((rr, cc))
            if bstate[rr][cc] != EMPTY:
                break
    return out

def _pseudo_shaman_attacks(bstate, r, c):
    out = []
    dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for (dr, dc) in dirs:
        r1, c1 = r+dr, c+dc
        if in_bounds(r1, c1):
            out.append((r1, c1))
            r2, c2 = r1+dr, c1+dc
            if in_bounds(r2, c2):
                out.append((r2, c2))
    return out

def _pseudo_king_attacks(r, c):
    out = []
    for dr in [-1,0,1]:
        for dc in [-1,0,1]:
            if dr == 0 and dc == 0:
                continue
            rr = r + dr
            cc = c + dc
            if in_bounds(rr, cc):
                out.append((rr, cc))
    return out

def _pseudo_totem_attacks(bstate, r, c):
    """
    TOTEM: per calcolo scacco,
      - Attacca le 8 caselle adiacenti (movimento Re),
    """
    p = bstate[r][c]
    out = []

    # Attacchi adiacenti (King-like)
    for dr in [-1,0,1]:
        for dc in [-1,0,1]:
            if dr == 0 and dc == 0:
                continue
            rr, cc = r+dr, c+dc
            if in_bounds(rr, cc):
                out.append((rr, cc))
    return out

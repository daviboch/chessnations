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

# (MODIFICA QUI) - adesso 'is_square_attacked' riceve 'board_obj'
def is_square_attacked(board_obj, row, col, by_white):
    """
    Ritorna True se la casella (row, col) è attaccata 
    da un pezzo del colore specificato (by_white).
    """
    bstate = board_obj.board  # estraiamo la matrice di caselle

    for rr in range(BOARD_SIZE):
        for cc in range(BOARD_SIZE):
            piece = bstate[rr][cc]
            if piece == EMPTY:
                continue
            # Se stiamo verificando 'by_white=True', allora 
            # consideriamo solo i pezzi bianchi, e viceversa
            if by_white:
                if not is_white_piece(piece):
                    continue
            else:
                if not is_black_piece(piece):
                    continue

            # (MODIFICA QUI) - richiamiamo la nuova funzione 
            # _get_pseudo_attacks_of_piece(board_obj, rr, cc)
            attacks = _get_pseudo_attacks_of_piece(board_obj, rr, cc)
            if (row, col) in attacks:
                return True
    return False

# (MODIFICA QUI) - anche '_get_pseudo_attacks_of_piece' ora riceve 'board_obj'
def _get_pseudo_attacks_of_piece(board_obj, r, c):
    """
    Restituisce la lista di caselle attaccate (pseudo-attacchi) 
    dal pezzo in (r,c), inclusa la logica TOTEM + poteri ereditati.
    """
    bstate = board_obj.board
    p = bstate[r][c]

    if p in (WHITE_BISON, BLACK_BISON):
        return _pseudo_bison_attacks(board_obj, r, c)
    elif p in (WHITE_TOTEM, BLACK_TOTEM):
        return _pseudo_totem_attacks(board_obj, r, c)  # (MODIFICA QUI)
    elif p in (WHITE_PAWN, BLACK_PAWN):
        return _pseudo_pawn_attacks(board_obj, r, c)
    elif p in (WHITE_ROOK, BLACK_ROOK):
        return _pseudo_rook_attacks(board_obj, r, c)
    elif p in (WHITE_KNIGHT, BLACK_KNIGHT):
        return _pseudo_knight_attacks(board_obj, r, c)
    elif p in (WHITE_BISHOP, BLACK_BISHOP):
        return _pseudo_bishop_attacks(board_obj, r, c)
    elif p in (WHITE_SHAMAN, BLACK_SHAMAN):
        return _pseudo_shaman_attacks(board_obj, r, c)
    elif p in (WHITE_QUEEN, BLACK_QUEEN):
        ro = _pseudo_rook_attacks(board_obj, r, c)
        bi = _pseudo_bishop_attacks(board_obj, r, c)
        return ro + bi
    elif p in (WHITE_KING, BLACK_KING):
        return _pseudo_king_attacks(board_obj, r, c)

    return []

def _pseudo_bison_attacks(board_obj, r, c):
    """
    Il Bisonte "attacca" come una Torre estesa (scorre in 4 direzioni
    e si ferma appena incontra un pezzo).
    """
    bstate = board_obj.board
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

def _pseudo_pawn_attacks(board_obj, r, c):
    """
    Un pedone 'attacca' solo in diagonale avanti (1 passo).
    """
    bstate = board_obj.board
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

def _pseudo_rook_attacks(board_obj, r, c):
    """
    Una Torre attacca scorrendo in orizzontale/verticale
    finché non incontra un pezzo o il bordo.
    """
    bstate = board_obj.board
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

def _pseudo_knight_attacks(board_obj, r, c):
    """
    Un Cavallo attacca le 8 posizioni a L.
    """
    out = []
    steps = [(-2,-1), (-2,1), (2,-1), (2,1), (1,-2), (1,2), (-1,-2), (-1,2)]
    for (dr, dc) in steps:
        rr, cc = r+dr, c+dc
        if in_bounds(rr, cc):
            out.append((rr, cc))
    return out

def _pseudo_bishop_attacks(board_obj, r, c):
    """
    Un Alfiere attacca scorrendo in diagonale 
    finché non incontra un pezzo o il bordo.
    """
    bstate = board_obj.board
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

def _pseudo_shaman_attacks(board_obj, r, c):
    """
    Lo Sciamano (base) attacca max 2 caselle in diagonale.
    """
    bstate = board_obj.board
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

def _pseudo_king_attacks(board_obj, r, c):
    """
    Il Re attacca le 8 posizioni adiacenti.
    """
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

# (MODIFICA QUI) - TOTEM deve includere anche gli attacchi ereditati
def _pseudo_totem_attacks(board_obj, r, c):
    """
    TOTEM: unisce 
      - attacchi "King-like" (1 passo attorno) 
      + attacchi ereditati, se esistono.
    """
    bstate = board_obj.board
    piece = bstate[r][c]
    out = []

    # 1) Attacchi base (King-like)
    for dr in [-1,0,1]:
        for dc in [-1,0,1]:
            if dr==0 and dc==0:
                continue
            rr = r + dr
            cc = c + dc
            if in_bounds(rr, cc):
                out.append((rr, cc))

    # 2) Se TOTEM ha ereditato un potere (BISHOP, ROOK, KNIGHT, etc.), 
    #    aggiungiamo anche quegli attacchi
    if is_white_piece(piece):
        inherited_power = board_obj.white_totem_inherited
    else:
        inherited_power = board_obj.black_totem_inherited

    if inherited_power is not None:
        out_inherited = _pseudo_inherited_attacks(board_obj, r, c, inherited_power)
        out.extend(out_inherited)

    return out

# (MODIFICA QUI) - funzione di supporto per gli attacchi "ereditati"
def _pseudo_inherited_attacks(board_obj, r, c, power_str):
    """
    Dato un 'power_str' come 'ROOK','BISHOP','KNIGHT','SHAMAN','BISON','KING', ecc.,
    ritorna l'elenco di caselle attaccate come se fosse quel pezzo.
    """
    if power_str == "ROOK":
        return _pseudo_rook_attacks(board_obj, r, c)
    elif power_str == "BISHOP":
        return _pseudo_bishop_attacks(board_obj, r, c)
    elif power_str == "KNIGHT":
        return _pseudo_knight_attacks(board_obj, r, c)
    elif power_str == "SHAMAN":
        return _pseudo_shaman_attacks(board_obj, r, c)
    elif power_str == "BISON":
        return _pseudo_bison_attacks(board_obj, r, c)
    elif power_str == "KING":
        return _pseudo_king_attacks(board_obj, r, c)
    elif power_str == "TOTEM":
        # TOTEM ereditato? (caso raro: Totem che cattura Totem)
        # In tal caso, puoi farlo comportare come un re 
        # o unire di nuovo la logica TOTEM.
        return _pseudo_king_attacks(board_obj, r, c)
    return []

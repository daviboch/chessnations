# native_piece_movement.py

from .piece_movement_common import (
    BOARD_SIZE,
    EMPTY,
    WHITE_TOTEM, BLACK_TOTEM,
    WHITE_BISON, BLACK_BISON,
    WHITE_SHAMAN, BLACK_SHAMAN,
    is_white_piece, is_black_piece,
    in_bounds
)

def get_totem_moves(board, r, c):
    """
    TOTEM semplificato:
      - Si MUOVE di 1 passo in qualsiasi direzione,
      - PUÒ CATTURARE entro 3 caselle “in stile Regina” se non ci sono pezzi in mezzo.
    """
    p = board[r][c]
    moves = []

    # (1) Spostamento come un Re (un solo passo)
    for dr in [-1,0,1]:
        for dc in [-1,0,1]:
            if dr == 0 and dc == 0:
                continue
            rr, cc = r+dr, c+dc
            if in_bounds(rr, cc):
                occ = board[rr][cc]
                if occ == EMPTY or is_white_piece(p) != is_white_piece(occ):
                    moves.append((rr, cc))

    # (2) Cattura “a distanza 3” (linee+diagonali), senza salto
    directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
    for (dr, dc) in directions:
        step_r, step_c = r, c
        for _ in range(3):  # max 3 caselle
            step_r += dr
            step_c += dc
            if not in_bounds(step_r, step_c):
                break
            occ = board[step_r][step_c]
            if occ != EMPTY:
                # Se è un pezzo avversario, possiamo catturarlo
                if is_white_piece(p) != is_white_piece(occ):
                    moves.append((step_r, step_c))
                break
    return moves

def get_bison_moves(board, r, c):
    """
    Bisonte: muove come una Rook (verticale/orizzontale), fermandosi se incontra un pezzo.
    Se il pezzo incontrato è un pedone avversario, tenta di spingerlo avanti di 1 (se c’è spazio);
    altrimenti, cattura come una Rook standard (se è un pezzo diverso dal pedone).
    (La spinta vera e propria avviene altrove, ma qui la generazione pseudo-legale è simile alla Rook.)
    """
    p = board[r][c]
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
            if board[rr][cc] != EMPTY:
                break
    return out

def get_shaman_moves(board, r, c):
    """
    Shaman: max due caselle in diagonale. Se la prima è vuota, “salta” alla seconda.
    Rimosso il blocco dei cavalli/bisoni avversari (la cattura funziona come un Bishop corto).
    """
    p = board[r][c]
    out = []
    dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for (dr, dc) in dirs:
        r1, c1 = r+dr, c+dc
        if in_bounds(r1, c1):
            occ1 = board[r1][c1]
            # primo passo
            if occ1 == EMPTY or is_white_piece(p) != is_white_piece(occ1):
                out.append((r1, c1))

            # secondo passo
            r2, c2 = r1+dr, c1+dc
            if in_bounds(r2, c2):
                occ2 = board[r2][c2]
                # se la prima era vuota, salti direttamente alla seconda
                if occ1 == EMPTY:
                    if occ2 == EMPTY or is_white_piece(p) != is_white_piece(occ2):
                        out.append((r2, c2))
                else:
                    # se la prima era occupata, puoi comunque colpire la seconda?
                    if occ2 == EMPTY or is_white_piece(p) != is_white_piece(occ2):
                        out.append((r2, c2))
    return out

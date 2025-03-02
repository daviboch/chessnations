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
      - Si MUOVE di 1 passo in qualsiasi direzione
      - (RIMOSSA la cattura a distanza 3)
    """
    p = board[r][c]
    moves = []

    # (1) Spostamento/cattura a una sola casella di distanza, stile Re
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                occ = board[rr][cc]
                # se casella vuota o c'è un pezzo avversario => si può muovere/catturare
                if occ == EMPTY or is_white_piece(p) != is_white_piece(occ):
                    moves.append((rr, cc))

    return moves


def get_bison_moves(board, r, c):
    """
    Bisonte (versione "nativi"):
    - Muove come una Rook (verticale/orizzontale), fermandosi se incontra un pezzo.
    - Se incontra un pedone avversario, lo "spinge" (vedi moves.py).
    - [Nuova Regola] "Richiamo dello Sciamano": se su una diagonale libera
      (nessun pezzo in mezzo) c'è uno Sciamano amico, il Bisonte può muoversi
      in quella diagonale come un Alfiere (fino a blocco).
    """
    p = board[r][c]
    out = []

    # (1) Movimenti base (stile Rook), come prima
    dirs_rook = [(1,0), (-1,0), (0,1), (0,-1)]
    for (dr, dc) in dirs_rook:
        rr, cc = r, c
        while True:
            rr += dr
            cc += dc
            if not in_bounds(rr, cc):
                break
            out.append((rr, cc))
            if board[rr][cc] != EMPTY:
                break

    # (2) Richiamo dello Sciamano
    my_is_white = is_white_piece(p)
    dirs_diag = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for (dr, dc) in dirs_diag:
        rr, cc = r, c
        found_shaman_same_color = False
        path_clear = True
        while True:
            rr += dr
            cc += dc
            if not in_bounds(rr, cc):
                break
            occupant = board[rr][cc]
            if occupant != EMPTY:
                if (my_is_white and occupant == WHITE_SHAMAN) or ((not my_is_white) and occupant == BLACK_SHAMAN):
                    found_shaman_same_color = True
                else:
                    path_clear = False
                break

        if found_shaman_same_color and path_clear:
            # Vogliamo la casella appena prima dello Sciamano
            prev_r = rr - dr
            prev_c = cc - dc
            if in_bounds(prev_r, prev_c):
                # Niente catture: dev'essere vuota
                if board[prev_r][prev_c] == EMPTY:
                    out.append((prev_r, prev_c))

    return out


def get_shaman_moves(board, r, c):
    """
    Shaman: max due caselle in diagonale. Se la prima è vuota, “salta” alla seconda.
    La cattura funziona come un Bishop "corto".
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

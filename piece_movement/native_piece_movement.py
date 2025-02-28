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

    # (2) Richiamo dello Sciamano: se c'è uno Sciamano amico su una diagonale
    #     e nessun pezzo in mezzo, muove come un Alfiere su quella diagonale.
    #     Cerchiamo in ognuna delle 4 diagonali se esiste uno Sciamano amico.

    my_is_white = is_white_piece(p)
    # Cerchiamo TOTTI i possibili "shaman" in diagonale: se ne troviamo almeno uno, sblocchiamo la diagonale
    # Metodo: per ogni diagonale, facciamo una scansione passo-passo:
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
                # Se troviamo un pezzo
                if (my_is_white and occupant == WHITE_SHAMAN) or ((not my_is_white) and occupant == BLACK_SHAMAN):
                    # Sciamano amico trovato => sblocco la diagonale
                    found_shaman_same_color = True
                else:
                    # Bloccato da un altro pezzo (o sciamano avversario)
                    path_clear = False
                break
        # Se found_shaman_same_color = True => quella diagonale è "sbloccata"
        if found_shaman_same_color and path_clear:
            # Ora aggiungiamo le mosse stile Alfiere (finché non troviamo un pezzo)
            rr2, cc2 = r, c
            while True:
                rr2 += dr
                cc2 += dc
                if not in_bounds(rr2, cc2):
                    break
                out.append((rr2, cc2))
                if board[rr2][cc2] != EMPTY:
                    break

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

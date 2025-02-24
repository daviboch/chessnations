# classic_piece_movement.py

from .piece_movement_common import (
    BOARD_SIZE,
    EMPTY,
    WHITE_PAWN, BLACK_PAWN,
    WHITE_ROOK, BLACK_ROOK,
    WHITE_KNIGHT, BLACK_KNIGHT,
    WHITE_BISHOP, BLACK_BISHOP,
    WHITE_QUEEN, BLACK_QUEEN,
    WHITE_KING, BLACK_KING,
    is_white_piece, is_black_piece,
    in_bounds
)

def get_pawn_moves(board, r, c):
    p = board[r][c]
    pIsWhite = is_white_piece(p)
    moves = []
    direction = -1 if pIsWhite else 1
    fr = r + direction

    # singolo passo
    if in_bounds(fr, c) and board[fr][c] == EMPTY:
        moves.append((fr, c))
        # doppio passo iniziale
        if pIsWhite and r == 6:
            if board[5][c] == EMPTY and board[4][c] == EMPTY:
                moves.append((4, c))
        elif (not pIsWhite) and r == 1:
            if board[2][c] == EMPTY and board[3][c] == EMPTY:
                moves.append((3, c))

    # catture diagonali pedone
    for dc in [-1, 1]:
        cc = c + dc
        if in_bounds(fr, cc):
            occ = board[fr][cc]
            if occ != EMPTY:
                # controlla se è avversario
                if is_white_piece(p) != is_white_piece(occ):
                    moves.append((fr, cc))

    return moves

def get_rook_moves(board, r, c):
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
            occ = board[rr][cc]
            if occ == EMPTY:
                out.append((rr, cc))
            else:
                if is_white_piece(p) != is_white_piece(occ):
                    out.append((rr, cc))
                break
    return out

def get_knight_moves(board, r, c):
    p = board[r][c]
    out = []
    steps = [(-2,-1), (-2,1), (2,-1), (2,1), (1,-2), (1,2), (-1,-2), (-1,2)]
    for (dr, dc) in steps:
        rr, cc = r+dr, c+dc
        if in_bounds(rr, cc):
            occ = board[rr][cc]
            if occ == EMPTY or is_white_piece(p) != is_white_piece(occ):
                out.append((rr, cc))
    return out

def get_bishop_moves(board, r, c):
    p = board[r][c]
    out = []
    dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for (dr, dc) in dirs:
        rr, cc = r, c
        while True:
            rr += dr
            cc += dc
            if not in_bounds(rr, cc):
                break
            occ = board[rr][cc]
            if occ == EMPTY:
                out.append((rr, cc))
            else:
                if is_white_piece(p) != is_white_piece(occ):
                    out.append((rr, cc))
                break
    return out

def get_queen_moves(board, r, c):
    # La Regina (Queen) combina i movimenti di Rook e Bishop
    rook_part = get_rook_moves(board, r, c)
    bishop_part = get_bishop_moves(board, r, c)
    return rook_part + bishop_part

def get_king_moves(board, r, c):
    p = board[r][c]
    out = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            rr, cc = r+dr, c+dc
            if in_bounds(rr, cc):
                occ = board[rr][cc]
                if occ == EMPTY or is_white_piece(p) != is_white_piece(occ):
                    out.append((rr, cc))
    return out

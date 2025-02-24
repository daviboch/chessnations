# piece_movement_common.py

BOARD_SIZE = 8

EMPTY           = 0
WHITE_PAWN      = 1
BLACK_PAWN      = 2
WHITE_TOTEM     = 3
BLACK_TOTEM     = 4
WHITE_BISON     = 5
BLACK_BISON     = 6
WHITE_SHAMAN    = 7
BLACK_SHAMAN    = 8
WHITE_ROOK      = 9
BLACK_ROOK      = 10
WHITE_KNIGHT    = 11
BLACK_KNIGHT    = 12
WHITE_BISHOP    = 13
BLACK_BISHOP    = 14
WHITE_QUEEN     = 15
BLACK_QUEEN     = 16
WHITE_KING      = 17
BLACK_KING      = 18

PIECE_NAME_MAP = {
    EMPTY:         "EMPTY",
    WHITE_PAWN:    "WHITE_PAWN",
    BLACK_PAWN:    "BLACK_PAWN",
    WHITE_TOTEM:   "WHITE_TOTEM",
    BLACK_TOTEM:   "BLACK_TOTEM",
    WHITE_BISON:   "WHITE_BISON",
    BLACK_BISON:   "BLACK_BISON",
    WHITE_SHAMAN:  "WHITE_SHAMAN",
    BLACK_SHAMAN:  "BLACK_SHAMAN",
    WHITE_ROOK:    "WHITE_ROOK",
    BLACK_ROOK:    "BLACK_ROOK",
    WHITE_KNIGHT:  "WHITE_KNIGHT",
    BLACK_KNIGHT:  "BLACK_KNIGHT",
    WHITE_BISHOP:  "WHITE_BISHOP",
    BLACK_BISHOP:  "BLACK_BISHOP",
    WHITE_QUEEN:   "WHITE_QUEEN",
    BLACK_QUEEN:   "BLACK_QUEEN",
    WHITE_KING:    "WHITE_KING",
    BLACK_KING:    "BLACK_KING",
}

def is_white_piece(p):
    return (p != EMPTY) and ((p & 1) == 1)

def is_black_piece(p):
    return (p != EMPTY) and ((p & 1) == 0)

def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def find_king(bstate, white):
    """
    Restituisce la posizione (r, c) del Re bianco o nero.
    Se non trovato, ritorna (None, None).
    """
    king = WHITE_KING if white else BLACK_KING
    for rr in range(BOARD_SIZE):
        for cc in range(BOARD_SIZE):
            if bstate[rr][cc] == king:
                return (rr, cc)
    return (None, None)


# Coordinatore dei movimenti (pseudo-legali) di tutti i pezzi:
# chiama le funzioni giuste in base al tipo di pezzo.
from .classic_piece_movement import (
    get_pawn_moves,   # Pawn bianco/nero
    get_rook_moves,
    get_knight_moves,
    get_bishop_moves,
    get_queen_moves,
    get_king_moves
)
from .native_piece_movement import (
    get_totem_moves,
    get_bison_moves,
    get_shaman_moves
)

def get_all_pseudo_moves_for_square(board, turn_white, r, c):
    """
    Ritorna TUTTE le mosse pseudo-legali di un pezzo in (r,c),
    basate sui pattern di movimento e cattura, senza controllo dello scacco.
    """
    p = board[r][c]
    if p == EMPTY:
        return []
    # Controllo colore
    if turn_white and not is_white_piece(p):
        return []
    if (not turn_white) and not is_black_piece(p):
        return []

    if p in (WHITE_PAWN, BLACK_PAWN):
        return get_pawn_moves(board, r, c)
    elif p in (WHITE_ROOK, BLACK_ROOK):
        return get_rook_moves(board, r, c)
    elif p in (WHITE_BISON, BLACK_BISON):
        return get_bison_moves(board, r, c)
    elif p in (WHITE_KNIGHT, BLACK_KNIGHT):
        return get_knight_moves(board, r, c)
    elif p in (WHITE_BISHOP, BLACK_BISHOP):
        return get_bishop_moves(board, r, c)
    elif p in (WHITE_SHAMAN, BLACK_SHAMAN):
        return get_shaman_moves(board, r, c)
    elif p in (WHITE_QUEEN, BLACK_QUEEN):
        return get_queen_moves(board, r, c)
    elif p in (WHITE_KING, BLACK_KING):
        return get_king_moves(board, r, c)
    elif p in (WHITE_TOTEM, BLACK_TOTEM):
        return get_totem_moves(board, r, c)

    return []

# evaluation.py

import random
from piece_movement.piece_movement_common import (
    EMPTY,
    WHITE_PAWN, BLACK_PAWN,
    WHITE_KNIGHT, BLACK_KNIGHT,
    WHITE_BISHOP, BLACK_BISHOP,
    WHITE_SHAMAN, BLACK_SHAMAN,
    WHITE_BISON, BLACK_BISON,
    WHITE_ROOK, BLACK_ROOK,
    WHITE_TOTEM, BLACK_TOTEM,
    WHITE_QUEEN, BLACK_QUEEN,
    WHITE_KING, BLACK_KING,
    is_white_piece, is_black_piece
)

################################################################################
# Valori base per il materiale (base) + PST
################################################################################

PIECE_VALUE = {
    WHITE_PAWN: 1,   BLACK_PAWN: 1,
    WHITE_KNIGHT: 3, BLACK_KNIGHT: 3,
    WHITE_BISHOP: 3, BLACK_BISHOP: 3,
    WHITE_SHAMAN: 3, BLACK_SHAMAN: 3,  # simile a Bishop/Knight
    WHITE_BISON: 4,  BLACK_BISON: 4,  
    WHITE_ROOK: 5,   BLACK_ROOK: 5,
    WHITE_TOTEM: 4,  BLACK_TOTEM: 4,
    WHITE_QUEEN: 9,  BLACK_QUEEN: 9,
    WHITE_KING: 999, BLACK_KING: 999
}


# Esempi di Piece-Square Tables per i pezzi bianchi (quelli neri sono riflessi).
PST_WHITE_PAWN = [
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [ 0.2,  0.2,  0.2,  0.2,  0.2,  0.2,  0.2,  0.2],
    [ 0.1,  0.1,  0.2,  0.3,  0.3,  0.2,  0.1,  0.1],
    [ 0.05, 0.05, 0.1,  0.25, 0.25, 0.1,  0.05, 0.05],
    [ 0.0,  0.0,  0.0,  0.2,  0.2,  0.0,  0.0,  0.0],
    [-0.05,-0.05,-0.05, 0.0,  0.0, -0.05,-0.05,-0.05],
    [ 0.2,  0.2,  0.0, -0.2, -0.2,  0.0,  0.2,  0.2],
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
]

PST_WHITE_KNIGHT = [
    [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5],
    [-0.4, -0.2,  0.0,  0.0,  0.0,  0.0, -0.2, -0.4],
    [-0.3,  0.0,  0.1,  0.15, 0.15, 0.1,  0.0, -0.3],
    [-0.3,  0.05, 0.15, 0.2,  0.2,  0.15, 0.05,-0.3],
    [-0.3,  0.0,  0.15, 0.2,  0.2,  0.15, 0.0, -0.3],
    [-0.3,  0.05, 0.1,  0.15, 0.15, 0.1,  0.05,-0.3],
    [-0.4, -0.2,  0.0,  0.05, 0.05, 0.0, -0.2, -0.4],
    [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5]
]

PST_WHITE_BISHOP = [
    [-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2],
    [-0.1,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.1],
    [-0.1,  0.0,  0.05, 0.1,  0.1,  0.05, 0.0, -0.1],
    [-0.1,  0.05, 0.05, 0.1,  0.1,  0.05, 0.05,-0.1],
    [-0.1,  0.0,  0.1,  0.1,  0.1,  0.1,  0.0, -0.1],
    [-0.1,  0.1,  0.1,  0.1,  0.1,  0.1,  0.1, -0.1],
    [-0.1,  0.05, 0.0,  0.0,  0.0,  0.0,  0.05,-0.1],
    [-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2]
]

PST_WHITE_ROOK = [
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [ 0.05, 0.1,  0.1,  0.1,  0.1,  0.1,  0.1,  0.05],
    [-0.05, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.05],
    [-0.05, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.05],
    [-0.05, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.05],
    [-0.05, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.05],
    [ 0.05, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.05],
    [ 0.0,  0.0,  0.0,  0.05, 0.05, 0.0,  0.0,  0.0]
]

PST_WHITE_QUEEN = [
    [-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2],
    [-0.1,  0.0,  0.05,  0.0,   0.0,   0.05, 0.0, -0.1],
    [-0.1,  0.05, 0.05,  0.05,  0.05,  0.05, 0.05,-0.1],
    [-0.05, 0.0,  0.05,  0.05,  0.05,  0.05, 0.0, -0.05],
    [-0.05, 0.0,  0.05,  0.05,  0.05,  0.05, 0.0, -0.05],
    [-0.1,  0.05, 0.05,  0.05,  0.05,  0.05, 0.05, -0.1],
    [-0.1,  0.0,  0.05,  0.0,   0.0,   0.05, 0.0,  -0.1],
    [-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2]
]

PST_WHITE_KING = [
    [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
    [-0.3, -0.4, -0.4, -0.45,-0.45,-0.4, -0.4, -0.3],
    [-0.3, -0.4, -0.4, -0.4, -0.4, -0.4, -0.4, -0.3],
    [-0.3, -0.4, -0.4, -0.35,-0.35,-0.4, -0.4, -0.3],
    [-0.2, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.2],
    [-0.1, -0.2, -0.2, -0.2, -0.2, -0.2, -0.2, -0.1],
    [ 0.2,  0.2,  0.0,  0.0,   0.0,  0.0,  0.2,  0.2],
    [ 0.2,  0.3,  0.1,  0.0,   0.0,  0.1,  0.3,  0.2]
]

PST_WHITE_DICT = {
    WHITE_PAWN:   PST_WHITE_PAWN,
    WHITE_KNIGHT: PST_WHITE_KNIGHT,
    WHITE_BISHOP: PST_WHITE_BISHOP,
    WHITE_ROOK:   PST_WHITE_ROOK,
    WHITE_QUEEN:  PST_WHITE_QUEEN,
    WHITE_KING:   PST_WHITE_KING,
    # Pezzi speciali
    WHITE_SHAMAN: PST_WHITE_BISHOP,
    WHITE_BISON:  PST_WHITE_ROOK,
    WHITE_TOTEM:  PST_WHITE_KNIGHT
}

def get_pst_value(piece, row, col):
    """
    Restituisce il bonus/malus della PST corrispondente. 
    Se il pezzo è nero, riflettiamo la riga.
    """
    is_white = is_white_piece(piece)
    if is_white:
        base_table = PST_WHITE_DICT.get(piece, None)
        if base_table is None:
            return 0.0
        return base_table[row][col]
    else:
        # Converti il pezzo nero al corrispettivo bianco (p-1 se p è pari)
        white_equiv = piece - 1  
        base_table = PST_WHITE_DICT.get(white_equiv, None)
        if base_table is None:
            return 0.0
        mirrored_row = 7 - row
        return base_table[mirrored_row][col]


################################################################################
# Funzione per mostrare il materiale (esclusi i Re), come in vecchia versione
################################################################################

def compute_material_display(board_obj):
    """
    Mostra il materiale senza contare i Re, utile per debug.
    """
    w, b = 0, 0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p in (WHITE_KING, BLACK_KING):
                continue
            if p != EMPTY:
                if is_white_piece(p):
                    w += PIECE_VALUE.get(p, 0)
                else:
                    b += PIECE_VALUE.get(p, 0)
    return w, b


################################################################################
# 2) FUNZIONE PRINCIPALE DI VALUTAZIONE (SINGLE PASS)
################################################################################

def static_evaluation(board_obj, noise_level=1.0):
    """
    Restituisce un punteggio (positivo = vantaggio bianco, negativo = vantaggio nero).
      - Material + PST
      - Bishop pair
      - Rook su colonna aperta
      - King safety più incisiva
      - Rumore modulabile

    Se noise_level=0.0 => nessun rumore, valutazione deterministica.
    """
    import random

    white_mat = 0.0
    black_mat = 0.0
    white_bishops = 0
    black_bishops = 0
    white_rooks_positions = []
    black_rooks_positions = []

    any_pawns_in_col = [0]*8  # Per la "open file"
    white_king_pos = None
    black_king_pos = None

    # Single pass
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p == EMPTY:
                continue

            base_val = PIECE_VALUE.get(p, 0)
            pst_val = get_pst_value(p, r, c)

            if is_white_piece(p):
                white_mat += (base_val + pst_val)
                if p in (WHITE_BISHOP, WHITE_SHAMAN):
                    white_bishops += 1
                if p == WHITE_ROOK:
                    white_rooks_positions.append((r,c))
                if p == WHITE_PAWN:
                    any_pawns_in_col[c] += 1
                if p == WHITE_KING:
                    white_king_pos = (r,c)
            else:
                black_mat += (base_val + pst_val)
                if p in (BLACK_BISHOP, BLACK_SHAMAN):
                    black_bishops += 1
                if p == BLACK_ROOK:
                    black_rooks_positions.append((r,c))
                if p == BLACK_PAWN:
                    any_pawns_in_col[c] += 1
                if p == BLACK_KING:
                    black_king_pos = (r,c)

    # bishop pair
    if white_bishops >= 2:
        white_mat += 0.3
    if black_bishops >= 2:
        black_mat += 0.3

    # rook on open file
    for (rr,cc) in white_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            white_mat += 0.25
    for (rr,cc) in black_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            black_mat += 0.25

    # king safety: penalizzo di più se in check
    if board_obj.is_in_check(True):
        white_mat -= 2.0
    if board_obj.is_in_check(False):
        black_mat -= 2.0

    score = white_mat - black_mat

    # noise modulabile
    if noise_level > 0:
        random_part = (random.random() * 2.0 - 1.0) * noise_level
        score += random_part

    return score

def deterministic_evaluation(board_obj):
    """
    Identico a static_evaluation ma senza rumore.
    """
    return static_evaluation(board_obj, noise_level=0.0)

def evaluation_breakdown(board_obj):
    """
    Restituisce un dizionario con i principali contributi.
    Per semplicità, qui calcoliamo la valutazione come se fosse static_evaluation(...,noise=0).
    """
    score = static_evaluation(board_obj, noise_level=0.0)
    breakdown_dict = {
        "score": score,
        "info": "Valutazione PST, bishop pair, rook open file, king safety, no noise",
    }
    return breakdown_dict

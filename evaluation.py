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

###############################################################################
# 1) Definizione cache di rumore e funzioni correlate
###############################################################################

NOISE_CACHE = {}

def clear_noise_cache():
    """
    Svuota la cache del rumore, così alla prossima mossa si rigenerano
    offset differenti (per ogni posizione).
    """
    NOISE_CACHE.clear()

def get_position_noise(board_obj, amplitude=0.0):
    """
    Restituisce un offset di rumore (float) associato in modo stabile
    alla posizione corrente, usando un seed derivato da board_obj.game_noise_seed
    e dall'hash di posizione. Se amplitude <= 0, restituisce 0.
    """
    if amplitude <= 0.0:
        return 0.0

    pos_key = board_position_hash(board_obj)
    if pos_key in NOISE_CACHE:
        return NOISE_CACHE[pos_key]

    # Creiamo un seme unendo il seme di partita con la stringa pos_key
    big_seed = str(getattr(board_obj, "game_noise_seed", 0)) + pos_key
    numeric_seed = abs(hash(big_seed)) % 1000000000
    rstate = random.Random(numeric_seed)

    offset = (rstate.random() * 2.0 - 1.0) * amplitude
    NOISE_CACHE[pos_key] = offset
    return offset

def board_position_hash(board_obj):
    """
    Restituisce una stringa univoca che codifica la scacchiera e il turno.
    """
    rows = []
    for r in range(8):
        row_pieces = []
        for c in range(8):
            row_pieces.append(str(board_obj.board[r][c]))
        rows.append(",".join(row_pieces))
    turn_char = "W" if board_obj.turn_white else "B"
    return f"{'/'.join(rows)} {turn_char}"


################################################################################
# Valori base per il materiale (base) + PST
################################################################################

PIECE_VALUE = {
    WHITE_PAWN: 1,   BLACK_PAWN: 1,
    WHITE_KNIGHT: 3, BLACK_KNIGHT: 3,
    WHITE_BISHOP: 3, BLACK_BISHOP: 3,
    WHITE_SHAMAN: 3, BLACK_SHAMAN: 3,
    WHITE_BISON: 4,  BLACK_BISON: 4,
    WHITE_ROOK: 5,   BLACK_ROOK: 5,
    WHITE_TOTEM: 4,  BLACK_TOTEM: 4,
    WHITE_QUEEN: 9,  BLACK_QUEEN: 9,
    WHITE_KING: 999, BLACK_KING: 999
}

# Esempio di PST per alcuni pezzi
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
    [-0.4, -0.2,  0.0,  0.05, 0.05,  0.0, -0.2, -0.4],
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

# ... e così via per PST_WHITE_ROOK, PST_WHITE_QUEEN, PST_WHITE_KING ...

PST_WHITE_DICT = {
    WHITE_PAWN:   PST_WHITE_PAWN,
    WHITE_KNIGHT: PST_WHITE_KNIGHT,
    WHITE_BISHOP: PST_WHITE_BISHOP,
    # ...
}


################################################################################
# Funzione PST
################################################################################

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
        white_equiv = piece - 1
        base_table = PST_WHITE_DICT.get(white_equiv, None)
        if base_table is None:
            return 0.0
        mirrored_row = 7 - row
        return base_table[mirrored_row][col]


################################################################################
# compute_material_display
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
# advanced_king_safety
################################################################################

def advanced_king_safety(board_obj, white=True):
    """
    Restituisce un malus > 0 se il Re 'white' è in scacco,
    e calcola la gravità (poche mosse di difesa = maggiore malus).
    """
    if not board_obj.is_in_check(white):
        return 0.0

    penalty = 1.0
    all_legal = board_obj.get_all_legal_moves(white)

    king_piece = WHITE_KING if white else BLACK_KING
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == king_piece:
                king_pos = (r, c)
                break
        if king_pos is not None:
            break

    if king_pos is None:
        return 10.0

    (kr, kc) = king_pos
    can_resolve_without_king = False
    for (fr, fc, tr, tc) in all_legal:
        if (fr, fc) != (kr, kc):
            can_resolve_without_king = True
            break

    if can_resolve_without_king:
        return penalty  # 1.0

    king_moves = []
    for (fr, fc, tr, tc) in all_legal:
        if (fr, fc) == (kr, kc):
            king_moves.append((tr, tc))

    n_king_moves = len(king_moves)
    if n_king_moves == 2:
        penalty += 1
    elif n_king_moves == 1:
        penalty += 2
    elif n_king_moves == 0:
        penalty += 100

    return penalty


################################################################################
# static_evaluation
################################################################################

def static_evaluation(board_obj, noise_amplitude=0.8):
    """
    Restituisce un punteggio (positivo = vantaggio bianco, negativo = vantaggio nero).
      - Material + PST
      - Bishop pair
      - Rook su colonna aperta
      - King safety
      - Rumore deterministico (dipende da questa posizione)
    """
    white_mat = 0.0
    black_mat = 0.0
    white_bishops = 0
    black_bishops = 0
    white_rooks_positions = []
    black_rooks_positions = []
    any_pawns_in_col = [0]*8

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
                    white_rooks_positions.append((r, c))
                if p == WHITE_PAWN:
                    any_pawns_in_col[c] += 1
            else:
                black_mat += (base_val + pst_val)
                if p in (BLACK_BISHOP, BLACK_SHAMAN):
                    black_bishops += 1
                if p == BLACK_ROOK:
                    black_rooks_positions.append((r, c))
                if p == BLACK_PAWN:
                    any_pawns_in_col[c] += 1

    # bishop pair
    if white_bishops >= 2:
        white_mat += 0.3
    if black_bishops >= 2:
        black_mat += 0.3

    # rook on open file
    for (rr, cc) in white_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            white_mat += 0.25
    for (rr, cc) in black_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            black_mat += 0.25

    # king safety
    white_mat -= advanced_king_safety(board_obj, white=True)
    black_mat -= advanced_king_safety(board_obj, white=False)

    # punteggio
    score = white_mat - black_mat

    # aggiunta rumore (posizione-dipendente, stabile finché non si resetta la cache)
    if noise_amplitude > 0.0:
        offset = get_position_noise(board_obj, amplitude=noise_amplitude)
        score += offset

    return score


################################################################################
# evaluation_breakdown
################################################################################

def evaluation_breakdown(board_obj, noise_amplitude=0.8):
    """
    Come static_evaluation, ma mostra i vari contributi a terminale.
    """
    white_mat = 0.0
    black_mat = 0.0

    contributions = {
        "WhiteMaterial": 0.0,
        "BlackMaterial": 0.0,
        "WhitePST": 0.0,
        "BlackPST": 0.0,
        "WhiteBishopPair": 0.0,
        "BlackBishopPair": 0.0,
        "WhiteRookOpenFile": 0.0,
        "BlackRookOpenFile": 0.0,
        "WhiteKingSafetyPenalty": 0.0,
        "BlackKingSafetyPenalty": 0.0,
        "Noise": 0.0
    }

    white_bishops = 0
    black_bishops = 0
    white_rooks_positions = []
    black_rooks_positions = []
    any_pawns_in_col = [0]*8

    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p == EMPTY:
                continue

            base_val = PIECE_VALUE.get(p, 0)
            pst_val = get_pst_value(p, r, c)

            if is_white_piece(p):
                white_mat += base_val
                contributions["WhiteMaterial"] += base_val

                white_mat += pst_val
                contributions["WhitePST"] += pst_val

                if p in (WHITE_BISHOP, WHITE_SHAMAN):
                    white_bishops += 1
                if p == WHITE_ROOK:
                    white_rooks_positions.append((r, c))
                if p == WHITE_PAWN:
                    any_pawns_in_col[c] += 1
            else:
                black_mat += base_val
                contributions["BlackMaterial"] += base_val

                black_mat += pst_val
                contributions["BlackPST"] += pst_val

                if p in (BLACK_BISHOP, BLACK_SHAMAN):
                    black_bishops += 1
                if p == BLACK_ROOK:
                    black_rooks_positions.append((r, c))
                if p == BLACK_PAWN:
                    any_pawns_in_col[c] += 1

    # bishop pair
    if white_bishops >= 2:
        white_mat += 0.3
        contributions["WhiteBishopPair"] = 0.3
    if black_bishops >= 2:
        black_mat += 0.3
        contributions["BlackBishopPair"] = 0.3

    # rook on open file
    rook_bonus = 0.25
    for (rr, cc) in white_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            white_mat += rook_bonus
            contributions["WhiteRookOpenFile"] += rook_bonus
    for (rr, cc) in black_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            black_mat += rook_bonus
            contributions["BlackRookOpenFile"] += rook_bonus

    # king safety
    w_king_pen = advanced_king_safety(board_obj, white=True)
    b_king_pen = advanced_king_safety(board_obj, white=False)
    white_mat -= w_king_pen
    black_mat -= b_king_pen
    contributions["WhiteKingSafetyPenalty"] = w_king_pen
    contributions["BlackKingSafetyPenalty"] = b_king_pen

    # punteggio
    score = white_mat - black_mat

    # eventuale noise
    noise_val = 0.0
    if noise_amplitude > 0.0:
        noise_val = get_position_noise(board_obj, amplitude=noise_amplitude)
        contributions["Noise"] = noise_val
    final_score = score + noise_val

    # Stampa
    print("=== EVALUATION BREAKDOWN ===")
    for k, v in contributions.items():
        print(f"{k}: {v:.3f}")
    print(f"WhiteMat parziale: {white_mat:.3f}, BlackMat parziale: {black_mat:.3f}")
    print(f"Final Score (white advantage) = {final_score:.3f}")
    print("================================\n")

    return final_score

def deterministic_evaluation(board_obj):
    """
    Esempio di funzione identica a static_evaluation con rumore=0, 
    se vuoi mantenere compatibilità con codice esistente.
    """
    return static_evaluation(board_obj, noise_amplitude=0.0)
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

def advanced_king_safety(board_obj, white=True):
    """
    Restituisce un valore > 0 se il Re 'white' (True=bianco, False=nero) è in pericolo.
    1) -1 se il Re è in scacco
    2) Se non ci sono mosse di altri pezzi che risolvano lo scacco,
       si guarda la mobilità del Re e si aumenta il malus:
         - +1 se il Re ha solo 2 mosse legali
         - +2 se il Re ha solo 1 mossa legale
         - +100 se non ha mosse legali (matto o quasi)
    Se il Re non è in scacco, la penalità è 0.
    """
    # Se il Re non è in scacco, niente malus.
    if not board_obj.is_in_check(white):
        return 0.0

    # Partiamo con un malus base di 1.
    penalty = 1.0

    # Recuperiamo TUTTE le mosse legali del colore. Se esiste una mossa che
    # risolve lo scacco senza muovere il Re, il malus extra non si applica.
    all_legal = board_obj.get_all_legal_moves(white)

    # Troviamo la posizione del Re
    from piece_movement.piece_movement_common import (
        WHITE_KING, BLACK_KING, is_white_piece
    )
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
        # Situazione anomala (Re non trovato), come fallback applichiamo un malus alto
        return 10.0

    # Verifichiamo se c'è una mossa di un pezzo diverso dal Re che risolva lo scacco
    # (bloccare, catturare la minaccia, ecc.)
    # Se esiste, usciamo col solo malus base.
    can_resolve_without_king = False
    for (fr, fc, tr, tc) in all_legal:
        # Se la mossa non è del Re, allora è un pezzo diverso
        if (fr, fc) != king_pos:
            can_resolve_without_king = True
            break

    if can_resolve_without_king:
        # C'è un modo di parare lo scacco senza spostare il Re
        return penalty  # rimane 1.0 e basta.

    # Se siamo qui, l'unica via per uscire dallo scacco è muovere il Re.
    # Vediamo quante mosse legali *del Re* ci sono.
    king_moves = []
    for (fr, fc, tr, tc) in all_legal:
        if (fr, fc) == king_pos:
            king_moves.append((tr, tc))

    n_king_moves = len(king_moves)
    if n_king_moves == 2:
        penalty += 1   # 1 + 1 = 2
    elif n_king_moves == 1:
        penalty += 2   # 1 + 2 = 3
    elif n_king_moves == 0:
        penalty += 100 # 1 + 100 = 101 (simuliamo matto “quasi infinito”)

    return penalty


def static_evaluation(board_obj, noise_level=0.0):
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
    white_mat -= advanced_king_safety(board_obj, white=True)
    black_mat -= advanced_king_safety(board_obj, white=False)

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

def evaluation_breakdown(board_obj, noise_level=0.0):
    """
    Esegue una valutazione simile a static_evaluation, ma:
      - Raccoglie i vari contributi (material, PST, bishop pair, rook open file, king safety, noise)
      - Li stampa a terminale
      - Restituisce il punteggio finale

    Integra advanced_king_safety per valutare la pericolosità dello scacco.
    """
    import random
    from piece_movement.piece_movement_common import (
        EMPTY, BOARD_SIZE,
        WHITE_PAWN, BLACK_PAWN,
        WHITE_BISHOP, BLACK_BISHOP,
        WHITE_SHAMAN, BLACK_SHAMAN,
        WHITE_ROOK, BLACK_ROOK,
        WHITE_KING, BLACK_KING,
        is_white_piece, is_black_piece
    )

    # Assumiamo che PIECE_VALUE, PST_WHITE_DICT, get_pst_value ecc. siano definiti altrove
    # e importati in questo contesto (come nel codice precedente).
    # Riprendo i riferimenti di es.:

    # from evaluation import PIECE_VALUE, get_pst_value

    # Per semplicità qui li cito come se fossero disponibili globalmente.

    white_mat = 0.0
    black_mat = 0.0

    # Per tracciare i contributi parziali
    contributions = {
        "WhiteMaterial": 0.0,
        "BlackMaterial": 0.0,
        "WhitePST": 0.0,
        "BlackPST": 0.0,
        "WhiteBishopPair": 0.0,
        "BlackBishopPair": 0.0,
        "WhiteRookOpenFile": 0.0,
        "BlackRookOpenFile": 0.0,
        "WhiteKingSafetyPenalty": 0.0,  # con advanced_king_safety
        "BlackKingSafetyPenalty": 0.0,
        "Noise": 0.0
    }

    white_bishops = 0
    black_bishops = 0
    white_rooks_positions = []
    black_rooks_positions = []
    any_pawns_in_col = [0]*8

    # Single pass
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
                    white_rooks_positions.append((r,c))
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
                    black_rooks_positions.append((r,c))
                if p == BLACK_PAWN:
                    any_pawns_in_col[c] += 1

    # bishop pair
    if white_bishops >= 2:
        contributions["WhiteBishopPair"] = 0.3
        white_mat += 0.3
    if black_bishops >= 2:
        contributions["BlackBishopPair"] = 0.3
        black_mat += 0.3

    # rook on open file
    rook_open_file_bonus = 0.25
    for (rr, cc) in white_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            contributions["WhiteRookOpenFile"] += rook_open_file_bonus
            white_mat += rook_open_file_bonus
    for (rr, cc) in black_rooks_positions:
        if any_pawns_in_col[cc] == 0:
            contributions["BlackRookOpenFile"] += rook_open_file_bonus
            black_mat += rook_open_file_bonus

    # advanced king safety
    white_king_penalty = advanced_king_safety(board_obj, white=True)
    black_king_penalty = advanced_king_safety(board_obj, white=False)
    contributions["WhiteKingSafetyPenalty"] = white_king_penalty
    contributions["BlackKingSafetyPenalty"] = black_king_penalty
    white_mat -= white_king_penalty
    black_mat -= black_king_penalty

    # Noise
    noise_val = 0.0
    if noise_level > 0.0:
        noise_val = (random.random() * 2 - 1) * noise_level
        contributions["Noise"] = noise_val

    final_score = (white_mat - black_mat) + noise_val

    # Stampa a terminale
    print("=== EVALUATION BREAKDOWN (advanced king safety) ===")
    for k, v in contributions.items():
        print(f"{k}: {v:.3f}")

    print(f"WhiteMat (parziale): {white_mat:.3f}, BlackMat (parziale): {black_mat:.3f}")
    print(f"Final Score (white advantage) = {final_score:.3f}")
    print("================================\n")

    return final_score

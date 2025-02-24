# evaluation.py

from customboard import CustomBoard
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

# Valori base per il materiale
# (Abbiamo lasciato TOTEM a 4 come riferimento)
PIECE_VALUE = {
    WHITE_PAWN: 1,   BLACK_PAWN: 1,
    WHITE_KNIGHT: 3, BLACK_KNIGHT: 3,
    WHITE_BISHOP: 3, BLACK_BISHOP: 3,
    WHITE_SHAMAN: 3, BLACK_SHAMAN: 3,  # simile a Bishop/Knight
    WHITE_BISON: 4,  BLACK_BISON: 4,  # leggermente superiore a un Rook? a piacere
    WHITE_ROOK: 5,   BLACK_ROOK: 5,
    WHITE_TOTEM: 4,  BLACK_TOTEM: 4,  # Totem fisso
    WHITE_QUEEN: 9,  BLACK_QUEEN: 9,
    WHITE_KING: 999, BLACK_KING: 999,
    EMPTY: 0
}

def compute_material(board_obj: CustomBoard):
    w, b = 0, 0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p == EMPTY:
                continue
            if is_white_piece(p):
                w += PIECE_VALUE[p]
            else:
                b += PIECE_VALUE[p]
    return w, b

def compute_material_display(board_obj: CustomBoard):
    """
    Mostra il materiale senza contare i Re, utile per debug
    """
    w, b = 0, 0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p in (WHITE_KING, BLACK_KING):
                continue
            if p != EMPTY:
                if is_white_piece(p):
                    w += PIECE_VALUE[p]
                else:
                    b += PIECE_VALUE[p]
    return w, b

def count_center_control(board_obj: CustomBoard):
    # Valuta il controllo del centro (quattro caselle centrali)
    w, b = 0, 0
    for (r, c) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
        p = board_obj.board[r][c]
        if p != EMPTY:
            if is_white_piece(p):
                w += 0.25
            else:
                b += 0.25
    return w, b

def white_king_safety(board_obj: CustomBoard):
    return -1 if board_obj.is_in_check(True) else 0

def black_king_safety(board_obj: CustomBoard):
    return -1 if board_obj.is_in_check(False) else 0

def white_pawn_advancement_bonus(board_obj: CustomBoard):
    bonus = 0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == WHITE_PAWN and r < 6:
                bonus += (6 - r) / 4.0
    return bonus

def white_piece_development_bonus(board_obj: CustomBoard):
    bonus = 0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p != EMPTY and is_white_piece(p) and p != WHITE_PAWN and r != 7:
                bonus += 0.75
    return bonus

def black_pawn_advancement_bonus(board_obj: CustomBoard):
    bonus = 0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == BLACK_PAWN and r > 1:
                bonus += (r - 1) / 4.0
    return bonus

def black_piece_development_bonus(board_obj: CustomBoard):
    bonus = 0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p != EMPTY and is_black_piece(p) and p != BLACK_PAWN and r != 0:
                bonus += 0.75
    return bonus

def white_castling_bonus(board_obj: CustomBoard):
    # Riconosce se il Re bianco è in una posizione di arrocco (0,2,6,7) su ultima traversa
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == WHITE_KING and r == 7 and c in (0,2,6,7):
                return 0.95
    return 0

def black_castling_bonus(board_obj: CustomBoard):
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == BLACK_KING and r == 0 and c in (0,2,6,7):
                return 0.95
    return 0

def get_noise(board_obj: CustomBoard):
    # se vuoi disabilitare, puoi restituire 0
    h = abs(hash(str(board_obj.board) + str(board_obj.game_noise_seed)))
    return ((h % 21) - 10) / 30.0

def white_passed_pawn_bonus(board_obj: CustomBoard):
    bonus = 0.0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == WHITE_PAWN:
                passed = True
                for rr in range(0, r):
                    for cc in [c-1, c, c+1]:
                        if 0 <= cc < 8:
                            if board_obj.board[rr][cc] == BLACK_PAWN:
                                passed = False
                if passed:
                    bonus += 0.25
    return bonus

def black_passed_pawn_bonus(board_obj: CustomBoard):
    bonus = 0.0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == BLACK_PAWN:
                passed = True
                for rr in range(r+1, 8):
                    for cc in [c-1, c, c+1]:
                        if 0 <= cc < 8:
                            if board_obj.board[rr][cc] == WHITE_PAWN:
                                passed = False
                if passed:
                    bonus += 0.25
    return bonus

def passed_pawn_bonus(board_obj: CustomBoard):
    return white_passed_pawn_bonus(board_obj) - black_passed_pawn_bonus(board_obj)

def white_doubled_pawn_penalty(board_obj: CustomBoard):
    penalty = 0.0
    for c in range(8):
        count = 0
        for r in range(8):
            if board_obj.board[r][c] == WHITE_PAWN:
                count += 1
        if count > 1:
            penalty += (count - 1) * 0.125
    return penalty

def black_doubled_pawn_penalty(board_obj: CustomBoard):
    penalty = 0.0
    for c in range(8):
        count = 0
        for r in range(8):
            if board_obj.board[r][c] == BLACK_PAWN:
                count += 1
        if count > 1:
            penalty += (count - 1) * 0.125
    return penalty

def doubled_pawn_penalty_diff(board_obj: CustomBoard):
    return black_doubled_pawn_penalty(board_obj) - white_doubled_pawn_penalty(board_obj)

def white_pawn_attack_penalty(board_obj: CustomBoard):
    """
    Penalizza i pezzi bianchi (diversi dal pedone) se sono attaccabili da un pedone nero.
    """
    penalty = 0.0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p != EMPTY and p != WHITE_PAWN and is_white_piece(p):
                if r - 1 >= 0:
                    if (c - 1 >= 0 and board_obj.board[r - 1][c - 1] == BLACK_PAWN) or \
                       (c + 1 < 8 and board_obj.board[r - 1][c + 1] == BLACK_PAWN):
                        penalty += 0.25
    return penalty

def black_pawn_attack_penalty(board_obj: CustomBoard):
    penalty = 0.0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p != EMPTY and p != BLACK_PAWN and is_black_piece(p):
                if r + 1 < 8:
                    if (c - 1 >= 0 and board_obj.board[r + 1][c - 1] == WHITE_PAWN) or \
                       (c + 1 < 8 and board_obj.board[r + 1][c + 1] == WHITE_PAWN):
                        penalty += 0.25
    return penalty

def pawn_attack_penalty_diff(board_obj: CustomBoard):
    return white_pawn_attack_penalty(board_obj) - black_pawn_attack_penalty(board_obj)

def static_evaluation(board_obj: CustomBoard):
    m_diff = compute_material(board_obj)[0] - compute_material(board_obj)[1]
    c_diff = count_center_control(board_obj)[0] - count_center_control(board_obj)[1]
    k_diff = white_king_safety(board_obj) - black_king_safety(board_obj)
    p_diff = white_pawn_advancement_bonus(board_obj) - black_pawn_advancement_bonus(board_obj)
    d_diff = white_piece_development_bonus(board_obj) - black_piece_development_bonus(board_obj)
    cast_diff = white_castling_bonus(board_obj) - black_castling_bonus(board_obj)
    noise = get_noise(board_obj)
    passed_bonus = passed_pawn_bonus(board_obj)
    doubled_diff = doubled_pawn_penalty_diff(board_obj)
    pawn_attack_pen = pawn_attack_penalty_diff(board_obj)
    return (m_diff + c_diff + k_diff + p_diff + d_diff + cast_diff + noise
            + passed_bonus - doubled_diff - pawn_attack_pen)

def deterministic_evaluation(board_obj: CustomBoard):
    # identico ma senza noise
    m_diff = compute_material(board_obj)[0] - compute_material(board_obj)[1]
    c_diff = count_center_control(board_obj)[0] - count_center_control(board_obj)[1]
    k_diff = white_king_safety(board_obj) - black_king_safety(board_obj)
    p_diff = white_pawn_advancement_bonus(board_obj) - black_pawn_advancement_bonus(board_obj)
    d_diff = white_piece_development_bonus(board_obj) - black_piece_development_bonus(board_obj)
    cast_diff = white_castling_bonus(board_obj) - black_castling_bonus(board_obj)
    passed_bonus = passed_pawn_bonus(board_obj)
    doubled_diff = doubled_pawn_penalty_diff(board_obj)
    pawn_attack_pen = pawn_attack_penalty_diff(board_obj)
    return (m_diff + c_diff + k_diff + p_diff + d_diff + cast_diff
            + passed_bonus - doubled_diff - pawn_attack_pen)

def evaluation_breakdown(board_obj: CustomBoard):
    m_diff = compute_material(board_obj)[0] - compute_material(board_obj)[1]
    c_diff = count_center_control(board_obj)[0] - count_center_control(board_obj)[1]
    k_diff = white_king_safety(board_obj) - black_king_safety(board_obj)
    wp_bonus = white_pawn_advancement_bonus(board_obj)
    bp_bonus = black_pawn_advancement_bonus(board_obj)
    p_diff = wp_bonus - bp_bonus
    wp_dev = white_piece_development_bonus(board_obj)
    bp_dev = black_piece_development_bonus(board_obj)
    d_diff = wp_dev - bp_dev
    cast_diff = white_castling_bonus(board_obj) - black_castling_bonus(board_obj)
    passed_bonus = passed_pawn_bonus(board_obj)
    doubled_diff = doubled_pawn_penalty_diff(board_obj)
    noise = get_noise(board_obj)
    pawn_attack_pen = pawn_attack_penalty_diff(board_obj)
    total = (m_diff + c_diff + k_diff + p_diff + d_diff
             + cast_diff + noise + passed_bonus - doubled_diff - pawn_attack_pen)
    return {
        "material_diff": m_diff,
        "center_diff": c_diff,
        "king_diff": k_diff,
        "pawn_adv_diff": p_diff,
        "piece_dev_diff": d_diff,
        "cast_diff": cast_diff,
        "passed_pawn_bonus": passed_bonus,
        "doubled_pawn_penalty_diff": doubled_diff,
        "pawn_attack_penalty": pawn_attack_pen,
        "noise": noise,
        "total": total
    }

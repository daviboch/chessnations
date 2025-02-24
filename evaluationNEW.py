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
PIECE_VALUE = {
    WHITE_PAWN: 1,   BLACK_PAWN: 1,
    WHITE_KNIGHT: 3, BLACK_KNIGHT: 3,
    WHITE_BISHOP: 3, BLACK_BISHOP: 3,
    WHITE_SHAMAN: 3, BLACK_SHAMAN: 3,
    WHITE_BISON: 4,  BLACK_BISON: 4,
    WHITE_ROOK: 5,   BLACK_ROOK: 5,
    WHITE_TOTEM: 4,  BLACK_TOTEM: 4,
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

def count_center_control(board_obj: CustomBoard):
    """
    Migliorata: bonus per chi OCCUPA le 4 caselle centrali
    + piccolo bonus anche se può ATTACCARE (in modo semplificato) quelle caselle.
    """
    center_squares = [(3,3), (3,4), (4,3), (4,4)]
    w_score, b_score = 0.0, 0.0

    for (r, c) in center_squares:
        occupant = board_obj.board[r][c]
        if occupant != EMPTY:
            if is_white_piece(occupant):
                w_score += 0.25
            else:
                b_score += 0.25

    # Semplice attacco: per ogni pezzo controlliamo se potrebbe raggiungere
    # una delle 4 caselle in una mossa (non consideriamo blocchi, scacchi, ecc.)
    # Esempio semplificato solo per pedoni, cavalieri, re, e un check basilare
    # per alfiere, torre, donna su linee libere. 
    # NB: se hai già un sistema di generazione mosse, puoi sostituire questa parte con un "get_attacks".
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p == EMPTY:
                continue

            if is_white_piece(p):
                color_sign = 1
            else:
                color_sign = -1

            # Piccolo valore di controllo a disposizione
            control_value = 0.05

            if p in (WHITE_PAWN, BLACK_PAWN):
                # Attacchi pedone (ipotizzando bianchi dal basso verso l'alto)
                attack_row = r - color_sign
                for attack_col in [c-1, c+1]:
                    if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                        if (attack_row, attack_col) in center_squares:
                            if color_sign == 1:  # white
                                w_score += control_value
                            else:               # black
                                b_score += control_value

            elif p in (WHITE_KNIGHT, BLACK_KNIGHT):
                knight_moves = [
                    (r+2, c+1), (r+2, c-1), (r-2, c+1), (r-2, c-1),
                    (r+1, c+2), (r+1, c-2), (r-1, c+2), (r-1, c-2)
                ]
                for (rr, cc) in knight_moves:
                    if 0 <= rr < 8 and 0 <= cc < 8:
                        if (rr, cc) in center_squares:
                            if color_sign == 1:
                                w_score += control_value
                            else:
                                b_score += control_value

            elif p in (WHITE_KING, BLACK_KING):
                king_moves = [
                    (r+1, c), (r-1, c), (r, c+1), (r, c-1),
                    (r+1, c+1), (r+1, c-1), (r-1, c+1), (r-1, c-1)
                ]
                for (rr, cc) in king_moves:
                    if 0 <= rr < 8 and 0 <= cc < 8:
                        if (rr, cc) in center_squares:
                            if color_sign == 1:
                                w_score += control_value
                            else:
                                b_score += control_value

            elif p in (WHITE_BISHOP, BLACK_BISHOP, WHITE_SHAMAN, BLACK_SHAMAN):
                # Per semplicità, controlliamo diagonali finché non usciamo
                # (o troviamo un pezzo). Non è perfetto, ma sufficiente come esempio veloce.
                directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
                for d_r, d_c in directions:
                    rr, cc = r, c
                    while True:
                        rr += d_r
                        cc += d_c
                        if not (0 <= rr < 8 and 0 <= cc < 8):
                            break
                        # se incontriamo un pezzo, ci fermiamo
                        if board_obj.board[rr][cc] != EMPTY and (rr, cc) != (r, c):
                            # se è una delle caselle centrali la "possiamo attaccare" 
                            # ma poi non proseguiamo
                            if (rr, cc) in center_squares:
                                if color_sign == 1:
                                    w_score += control_value
                                else:
                                    b_score += control_value
                            break
                        if (rr, cc) in center_squares:
                            if color_sign == 1:
                                w_score += control_value
                            else:
                                b_score += control_value
            elif p in (WHITE_ROOK, BLACK_ROOK):
                # Controllo lineare
                directions = [(-1,0), (1,0), (0,-1), (0,1)]
                for d_r, d_c in directions:
                    rr, cc = r, c
                    while True:
                        rr += d_r
                        cc += d_c
                        if not (0 <= rr < 8 and 0 <= cc < 8):
                            break
                        if board_obj.board[rr][cc] != EMPTY and (rr, cc) != (r, c):
                            if (rr, cc) in center_squares:
                                if color_sign == 1:
                                    w_score += control_value
                                else:
                                    b_score += control_value
                            break
                        if (rr, cc) in center_squares:
                            if color_sign == 1:
                                w_score += control_value
                            else:
                                b_score += control_value

            elif p in (WHITE_QUEEN, BLACK_QUEEN, WHITE_BISON, BLACK_BISON):
                # Faccio una fusione di linee e diagonali (rozza) 
                directions = [(-1,0), (1,0), (0,-1), (0,1),
                              (-1,-1), (-1,1), (1,-1), (1,1)]
                for d_r, d_c in directions:
                    rr, cc = r, c
                    while True:
                        rr += d_r
                        cc += d_c
                        if not (0 <= rr < 8 and 0 <= cc < 8):
                            break
                        if board_obj.board[rr][cc] != EMPTY and (rr, cc) != (r, c):
                            if (rr, cc) in center_squares:
                                if color_sign == 1:
                                    w_score += control_value
                                else:
                                    b_score += control_value
                            break
                        if (rr, cc) in center_squares:
                            if color_sign == 1:
                                w_score += control_value
                            else:
                                b_score += control_value

    return w_score, b_score

def white_king_safety(board_obj: CustomBoard):
    """
    Penalizza di 1 se in scacco + piccolo bonus se il Re ha pedoni davanti.
    """
    penalty = -1 if board_obj.is_in_check(True) else 0
    bonus = 0.0

    # Troviamo il re
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == WHITE_KING:
                king_pos = (r, c)
                break
        if king_pos is not None:
            break
    
    if king_pos:
        kr, kc = king_pos
        # Se i pedoni (riga kr-1 o kr-2) ci sono, diamo un bonus
        # (verificando anche le colonne a fianco)
        for row_check in [kr-1, kr-2]:
            if 0 <= row_check < 8:
                for col_check in [kc-1, kc, kc+1]:
                    if 0 <= col_check < 8:
                        if board_obj.board[row_check][col_check] == WHITE_PAWN:
                            bonus += 0.1
    
    return penalty + bonus

def black_king_safety(board_obj: CustomBoard):
    """
    Penalizza di 1 se in scacco + piccolo bonus se il Re ha pedoni davanti (per i neri
    davanti = riga maggiore).
    """
    penalty = -1 if board_obj.is_in_check(False) else 0
    bonus = 0.0

    king_pos = None
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == BLACK_KING:
                king_pos = (r, c)
                break
        if king_pos is not None:
            break

    if king_pos:
        kr, kc = king_pos
        # Se i pedoni neri stanno nelle righe kr+1/kr+2, bonus
        for row_check in [kr+1, kr+2]:
            if 0 <= row_check < 8:
                for col_check in [kc-1, kc, kc+1]:
                    if 0 <= col_check < 8:
                        if board_obj.board[row_check][col_check] == BLACK_PAWN:
                            bonus += 0.1

    return penalty + bonus

def white_pawn_advancement_bonus(board_obj: CustomBoard):
    bonus = 0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == WHITE_PAWN and r < 6:
                bonus += (6 - r) / 4.0
    return bonus

def black_pawn_advancement_bonus(board_obj: CustomBoard):
    bonus = 0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == BLACK_PAWN and r > 1:
                bonus += (r - 1) / 4.0
    return bonus

def white_castling_bonus(board_obj: CustomBoard):
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
    h = abs(hash(str(board_obj.board) + str(board_obj.game_noise_seed)))
    return ((h % 21) - 10) / 30.0

def white_passed_pawn_bonus(board_obj: CustomBoard):
    """
    Ora correggiamo il range per i bianchi: se i bianchi sono in basso, 
    le caselle 'davanti' a un pedone bianco stanno in riga < r.
    """
    bonus = 0.0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == WHITE_PAWN:
                passed = True
                # controlliamo da r-1 fino a 0
                for rr in range(r-1, -1, -1):
                    for cc in [c-1, c, c+1]:
                        if 0 <= cc < 8:
                            if board_obj.board[rr][cc] == BLACK_PAWN:
                                passed = False
                                break
                    if not passed:
                        break
                if passed:
                    bonus += 0.25
    return bonus

def black_passed_pawn_bonus(board_obj: CustomBoard):
    bonus = 0.0
    for r in range(8):
        for c in range(8):
            if board_obj.board[r][c] == BLACK_PAWN:
                passed = True
                # controlliamo da r+1 fino a 7
                for rr in range(r+1, 8):
                    for cc in [c-1, c, c+1]:
                        if 0 <= cc < 8:
                            if board_obj.board[rr][cc] == WHITE_PAWN:
                                passed = False
                                break
                    if not passed:
                        break
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

def compute_mobility(board_obj: CustomBoard):
    """
    Piccolo bonus di mobilità: somma del numero di pseudo-mosse
    disponibili per bianchi e neri, e usiamo la differenza.
    Se hai già una funzione per contare le mosse legali, usala.
    Qui ipotizziamo board_obj.get_legal_moves(side) -> lista mosse.
    """
    # Se non esiste, metti un conteggio fittizio di 0
    try:
        white_moves = len(board_obj.get_legal_moves(True))
        black_moves = len(board_obj.get_legal_moves(False))
    except:
        white_moves, black_moves = 0, 0

    return 0.02 * (white_moves - black_moves)

def static_evaluation(board_obj: CustomBoard):
    w_mat, b_mat = compute_material(board_obj)
    m_diff = w_mat - b_mat

    # Migliorato il controllo del centro
    w_center, b_center = count_center_control(board_obj)
    c_diff = w_center - b_center

    # Sicurezza del Re con penalità + piccolo bonus
    k_diff = white_king_safety(board_obj) - black_king_safety(board_obj)

    # Bonus avanzamento pedoni
    p_diff = (white_pawn_advancement_bonus(board_obj)
              - black_pawn_advancement_bonus(board_obj))

    # Bonus sviluppo (resta come prima)
    d_diff = white_piece_development_bonus(board_obj) - black_piece_development_bonus(board_obj)

    # Bonus arrocco
    cast_diff = white_castling_bonus(board_obj) - black_castling_bonus(board_obj)

    # Noise
    noise = get_noise(board_obj)

    # Pedoni passati
    passed_bonus = passed_pawn_bonus(board_obj)

    # Penalità pedoni doppiati
    doubled_diff = doubled_pawn_penalty_diff(board_obj)

    # Penalità pezzi attaccati da pedoni
    pawn_attack_pen = pawn_attack_penalty_diff(board_obj)

    # Aggiunta mobilità
    mobility_diff = compute_mobility(board_obj)

    return (m_diff + c_diff + k_diff
            + p_diff + d_diff + cast_diff + noise
            + passed_bonus - doubled_diff - pawn_attack_pen
            + mobility_diff)

def deterministic_evaluation(board_obj: CustomBoard):
    w_mat, b_mat = compute_material(board_obj)
    m_diff = w_mat - b_mat

    w_center, b_center = count_center_control(board_obj)
    c_diff = w_center - b_center

    k_diff = white_king_safety(board_obj) - black_king_safety(board_obj)
    p_diff = (white_pawn_advancement_bonus(board_obj)
              - black_pawn_advancement_bonus(board_obj))
    d_diff = white_piece_development_bonus(board_obj) - black_piece_development_bonus(board_obj)
    cast_diff = white_castling_bonus(board_obj) - black_castling_bonus(board_obj)
    passed_bonus = passed_pawn_bonus(board_obj)
    doubled_diff = doubled_pawn_penalty_diff(board_obj)
    pawn_attack_pen = pawn_attack_penalty_diff(board_obj)
    mobility_diff = compute_mobility(board_obj)

    return (m_diff + c_diff + k_diff
            + p_diff + d_diff + cast_diff
            + passed_bonus - doubled_diff - pawn_attack_pen
            + mobility_diff)

def white_piece_development_bonus(board_obj: CustomBoard):
    """
    Rimasta uguale, ma potresti anche variare leggermente se vuoi
    penalizzare pezzi bianchi rimasti in ultima traversa (r == 7).
    """
    bonus = 0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p != EMPTY and is_white_piece(p) and p != WHITE_PAWN and r != 7:
                bonus += 0.75
    return bonus

def black_piece_development_bonus(board_obj: CustomBoard):
    bonus = 0
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p != EMPTY and is_black_piece(p) and p != BLACK_PAWN and r != 0:
                bonus += 0.75
    return bonus

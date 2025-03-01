# moves.py

from piece_movement.piece_movement_common import (
    BOARD_SIZE, EMPTY,
    WHITE_PAWN, BLACK_PAWN,
    WHITE_KNIGHT, BLACK_KNIGHT,
    WHITE_TOTEM, BLACK_TOTEM,
    WHITE_BISON, BLACK_BISON,
    WHITE_SHAMAN, BLACK_SHAMAN,
    WHITE_BISHOP, BLACK_BISHOP,
    WHITE_ROOK, BLACK_ROOK,
    WHITE_KING, BLACK_KING,
    WHITE_QUEEN, BLACK_QUEEN,
    is_white_piece, is_black_piece,
    in_bounds, get_all_pseudo_moves_for_square
)

from piece_movement.piece_attacks import is_square_attacked  # usa la versione aggiornata

# -------------------------------------------------------
# Sezione "Arrocco" (ex board_castling.py)
# -------------------------------------------------------
def white_castle_short_inplace_classical(board_obj):
    if board_obj.white_king_moved or board_obj.white_right_rook_moved:
        return False
    if is_in_check(board_obj, True):
        return False
    if (board_obj.board[7][5] != EMPTY or board_obj.board[7][6] != EMPTY):
        return False
    if board_obj.board[7][7] != WHITE_ROOK:
        return False
    old_king = board_obj.board[7][4]
    old_rook = board_obj.board[7][7]
    board_obj.board[7][4] = EMPTY
    board_obj.board[7][7] = EMPTY
    board_obj.board[7][6] = old_king
    board_obj.board[7][5] = old_rook
    if is_in_check(board_obj, True):
        board_obj.board[7][4] = old_king
        board_obj.board[7][7] = old_rook
        board_obj.board[7][6] = EMPTY
        board_obj.board[7][5] = EMPTY
        return False
    board_obj.white_king_moved = True
    board_obj.white_right_rook_moved = True
    return True

def white_castle_long_inplace_classical(board_obj):
    if board_obj.white_king_moved or board_obj.white_left_rook_moved:
        return False
    if is_in_check(board_obj, True):
        return False
    if (board_obj.board[7][1] != EMPTY or
        board_obj.board[7][2] != EMPTY or
        board_obj.board[7][3] != EMPTY):
        return False
    if board_obj.board[7][0] != WHITE_ROOK:
        return False
    old_king = board_obj.board[7][4]
    old_rook = board_obj.board[7][0]
    board_obj.board[7][4] = EMPTY
    board_obj.board[7][0] = EMPTY
    board_obj.board[7][2] = old_king
    board_obj.board[7][3] = old_rook
    if is_in_check(board_obj, True):
        board_obj.board[7][4] = old_king
        board_obj.board[7][0] = old_rook
        board_obj.board[7][2] = EMPTY
        board_obj.board[7][3] = EMPTY
        return False
    board_obj.white_king_moved = True
    board_obj.white_left_rook_moved = True
    return True

def black_castle_short_inplace_classical(board_obj):
    if board_obj.black_king_moved or board_obj.black_right_rook_moved:
        return False
    if is_in_check(board_obj, False):
        return False
    if (board_obj.board[0][5] != EMPTY or board_obj.board[0][6] != EMPTY):
        return False
    if board_obj.board[0][7] != BLACK_ROOK:
        return False
    old_king = board_obj.board[0][4]
    old_rook = board_obj.board[0][7]
    board_obj.board[0][4] = EMPTY
    board_obj.board[0][7] = EMPTY
    board_obj.board[0][6] = old_king
    board_obj.board[0][5] = old_rook
    if is_in_check(board_obj, False):
        board_obj.board[0][4] = old_king
        board_obj.board[0][7] = old_rook
        board_obj.board[0][6] = EMPTY
        board_obj.board[0][5] = EMPTY
        return False
    board_obj.black_king_moved = True
    board_obj.black_right_rook_moved = True
    return True

def black_castle_long_inplace_classical(board_obj):
    if board_obj.black_king_moved or board_obj.black_left_rook_moved:
        return False
    if is_in_check(board_obj, False):
        return False
    if (board_obj.board[0][1] != EMPTY or
        board_obj.board[0][2] != EMPTY or
        board_obj.board[0][3] != EMPTY):
        return False
    if board_obj.board[0][0] != BLACK_ROOK:
        return False
    old_king = board_obj.board[0][4]
    old_rook = board_obj.board[0][0]
    board_obj.board[0][4] = EMPTY
    board_obj.board[0][0] = EMPTY
    board_obj.board[0][2] = old_king
    board_obj.board[0][3] = old_rook
    if is_in_check(board_obj, False):
        board_obj.board[0][4] = old_king
        board_obj.board[0][0] = old_rook
        board_obj.board[0][2] = EMPTY
        board_obj.board[0][3] = EMPTY
        return False
    board_obj.black_king_moved = True
    board_obj.black_left_rook_moved = True
    return True

def white_castle_short_inplace_nativi(board_obj):
    if board_obj.white_king_moved or board_obj.white_right_rook_moved:
        return False
    if is_in_check(board_obj, True):
        return False
    if (board_obj.board[7][5] != EMPTY or board_obj.board[7][6] != EMPTY):
        return False
    if board_obj.board[7][7] != WHITE_TOTEM:
        return False
    old_king = board_obj.board[7][4]
    old_totem = board_obj.board[7][7]
    board_obj.board[7][4] = EMPTY
    board_obj.board[7][7] = EMPTY
    board_obj.board[7][6] = old_king
    board_obj.board[7][5] = old_totem
    if is_in_check(board_obj, True):
        board_obj.board[7][4] = old_king
        board_obj.board[7][7] = old_totem
        board_obj.board[7][6] = EMPTY
        board_obj.board[7][5] = EMPTY
        return False
    board_obj.white_king_moved = True
    board_obj.white_right_rook_moved = True
    return True

def white_castle_long_inplace_nativi(board_obj):
    if board_obj.white_king_moved or board_obj.white_left_rook_moved:
        return False
    if is_in_check(board_obj, True):
        return False
    if (board_obj.board[7][1] != EMPTY or
        board_obj.board[7][2] != EMPTY or
        board_obj.board[7][3] != EMPTY):
        return False
    if board_obj.board[7][0] != WHITE_TOTEM:
        return False
    old_king = board_obj.board[7][4]
    old_totem = board_obj.board[7][0]
    board_obj.board[7][4] = EMPTY
    board_obj.board[7][0] = EMPTY
    board_obj.board[7][2] = old_king
    board_obj.board[7][3] = old_totem
    if is_in_check(board_obj, True):
        board_obj.board[7][4] = old_king
        board_obj.board[7][0] = old_totem
        board_obj.board[7][2] = EMPTY
        board_obj.board[7][3] = EMPTY
        return False
    board_obj.white_king_moved = True
    board_obj.white_left_rook_moved = True
    return True

def black_castle_short_inplace_nativi(board_obj):
    if board_obj.black_king_moved or board_obj.black_right_rook_moved:
        return False
    if is_in_check(board_obj, False):
        return False
    if (board_obj.board[0][5] != EMPTY or board_obj.board[0][6] != EMPTY):
        return False
    if board_obj.board[0][7] != BLACK_TOTEM:
        return False
    old_king = board_obj.board[0][4]
    old_totem = board_obj.board[0][7]
    board_obj.board[0][4] = EMPTY
    board_obj.board[0][7] = EMPTY
    board_obj.board[0][6] = old_king
    board_obj.board[0][5] = old_totem
    if is_in_check(board_obj, False):
        board_obj.board[0][4] = old_king
        board_obj.board[0][7] = old_totem
        board_obj.board[0][6] = EMPTY
        board_obj.board[0][5] = EMPTY
        return False
    board_obj.black_king_moved = True
    board_obj.black_right_rook_moved = True
    return True

def black_castle_long_inplace_nativi(board_obj):
    if board_obj.black_king_moved or board_obj.black_left_rook_moved:
        return False
    if is_in_check(board_obj, False):
        return False
    if (board_obj.board[0][1] != EMPTY or
        board_obj.board[0][2] != EMPTY or
        board_obj.board[0][3] != EMPTY):
        return False
    if board_obj.board[0][0] != BLACK_TOTEM:
        return False
    old_king = board_obj.board[0][4]
    old_totem = board_obj.board[0][0]
    board_obj.board[0][4] = EMPTY
    board_obj.board[0][0] = EMPTY
    board_obj.board[0][2] = old_king
    board_obj.board[0][3] = old_totem
    if is_in_check(board_obj, False):
        board_obj.board[0][4] = old_king
        board_obj.board[0][0] = old_totem
        board_obj.board[0][2] = EMPTY
        board_obj.board[0][3] = EMPTY
        return False
    board_obj.black_king_moved = True
    board_obj.black_left_rook_moved = True
    return True

# -------------------------------------------------------
# Sezione "board_state.py" (scacco, patta, vincitore)
# -------------------------------------------------------
def find_king_position(board_obj, white):
    king = WHITE_KING if white else BLACK_KING
    for rr in range(BOARD_SIZE):
        for cc in range(BOARD_SIZE):
            if board_obj.board[rr][cc] == king:
                return (rr, cc)
    return (None, None)

def is_in_check(board_obj, white=True):
    kr, kc = find_king_position(board_obj, white)
    if kr is None:
        return False
    # (MODIFICA QUI) --> passiamo board_obj, non board_obj.board
    return is_square_attacked(board_obj, kr, kc, by_white=(not white))

def is_game_over(board_obj):
    return board_obj.game_over

def get_winner(board_obj):
    return board_obj.winner

# -------------------------------------------------------
# [SHAMAN FREEZE RULE] Funzioni di supporto
# -------------------------------------------------------
def is_animal(piece):
    """Restituisce True se p è un Cavallo o Bisonte (di qualunque colore)."""
    return piece in (WHITE_KNIGHT, BLACK_KNIGHT, WHITE_BISON, BLACK_BISON)

def is_piece_frozen_by_enemy_shaman(board_obj, r, c):
    """
    Un pezzo “animale” (Cavallo o Bisonte) è congelato se,
    in una delle 4 caselle adiacenti (in linea retta),
    c'è uno Sciamano nemico.
    """
    p = board_obj.board[r][c]
    if not is_animal(p):
        return False

    my_color_is_white = is_white_piece(p)
    for (dr, dc) in [(-1,0),(1,0),(0,-1),(0,1)]:
        rr = r + dr
        cc = c + dc
        if in_bounds(rr, cc):
            occupant = board_obj.board[rr][cc]
            if my_color_is_white:
                if occupant == BLACK_SHAMAN:
                    return True
            else:
                if occupant == WHITE_SHAMAN:
                    return True
    return False

# -------------------------------------------------------
# Sezione "board_moves.py"
# -------------------------------------------------------
def can_move_piece(board_obj, piece):
    if piece == EMPTY:
        return False
    if board_obj.turn_white and not is_white_piece(piece):
        return False
    if (not board_obj.turn_white) and not is_black_piece(piece):
        return False
    return True

def get_all_legal_moves(board_obj, white=True):
    out = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board_obj.board[r][c]
            if p == EMPTY:
                continue
            if white and not is_white_piece(p):
                continue
            if (not white) and not is_black_piece(p):
                continue
            candidate = get_legal_moves_for_square(board_obj, r, c)
            for (rr, cc) in candidate:
                out.append((r, c, rr, cc))
    return out

def get_legal_moves_for_square(board_obj, r, c):
    p = board_obj.board[r][c]
    if p == EMPTY:
        return []
    if not can_move_piece(board_obj, p):
        return []

    # [SHAMAN FREEZE RULE]
    if is_piece_frozen_by_enemy_shaman(board_obj, r, c):
        return []

    pseudo = get_all_pseudo_moves_for_square(board_obj, board_obj.turn_white, r, c)
    real_moves = []
    for (rr, cc) in pseudo:
        if not does_move_leave_king_in_check(board_obj, r, c, rr, cc):
            real_moves.append((rr, cc))

    # Arrocco (classici / nativi)
    if p == WHITE_KING and board_obj.white_faction == "classici" and board_obj.turn_white \
       and not board_obj.white_king_moved and (r, c) == (7, 4):
        if (not board_obj.white_right_rook_moved) \
           and board_obj.board[7][5] == EMPTY and board_obj.board[7][6] == EMPTY \
           and board_obj.board[7][7] == WHITE_ROOK \
           and (not is_in_check(board_obj, True)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,5)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,6)):
            real_moves.append((7, 6))
        if (not board_obj.white_left_rook_moved) \
           and (board_obj.board[7][1] == EMPTY and board_obj.board[7][2] == EMPTY and board_obj.board[7][3] == EMPTY) \
           and board_obj.board[7][0] == WHITE_ROOK \
           and (not is_in_check(board_obj, True)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,3)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,2)):
            real_moves.append((7, 2))

    if p == BLACK_KING and board_obj.black_faction == "classici" and (not board_obj.turn_white) \
       and not board_obj.black_king_moved and (r, c) == (0, 4):
        if (not board_obj.black_right_rook_moved) \
           and board_obj.board[0][5] == EMPTY and board_obj.board[0][6] == EMPTY \
           and board_obj.board[0][7] == BLACK_ROOK \
           and (not is_in_check(board_obj, False)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,5)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,6)):
            real_moves.append((0, 6))
        if (not board_obj.black_left_rook_moved) \
           and (board_obj.board[0][1] == EMPTY and board_obj.board[0][2] == EMPTY and board_obj.board[0][3] == EMPTY) \
           and board_obj.board[0][0] == BLACK_ROOK \
           and (not is_in_check(board_obj, False)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,3)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,2)):
            real_moves.append((0, 2))

    if p == WHITE_KING and board_obj.white_faction == "nativi" and board_obj.turn_white \
       and not board_obj.white_king_moved and (r, c) == (7, 4):
        if (not board_obj.white_right_rook_moved) \
           and board_obj.board[7][5] == EMPTY and board_obj.board[7][6] == EMPTY \
           and board_obj.board[7][7] == WHITE_TOTEM \
           and (not is_in_check(board_obj, True)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,5)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,6)):
            real_moves.append((7, 6))
        if (not board_obj.white_left_rook_moved) \
           and (board_obj.board[7][1] == EMPTY and board_obj.board[7][2] == EMPTY and board_obj.board[7][3] == EMPTY) \
           and board_obj.board[7][0] == WHITE_TOTEM \
           and (not is_in_check(board_obj, True)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,3)) \
           and (not does_move_leave_king_in_check(board_obj, 7,4,7,2)):
            real_moves.append((7, 2))

    if p == BLACK_KING and board_obj.black_faction == "nativi" and (not board_obj.turn_white) \
       and not board_obj.black_king_moved and (r, c) == (0, 4):
        if (not board_obj.black_right_rook_moved) \
           and board_obj.board[0][5] == EMPTY and board_obj.board[0][6] == EMPTY \
           and board_obj.board[0][7] == BLACK_TOTEM \
           and (not is_in_check(board_obj, False)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,5)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,6)):
            real_moves.append((0, 6))
        if (not board_obj.black_left_rook_moved) \
           and (board_obj.board[0][1] == EMPTY and board_obj.board[0][2] == EMPTY and board_obj.board[0][3] == EMPTY) \
           and board_obj.board[0][0] == BLACK_TOTEM \
           and (not is_in_check(board_obj, False)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,3)) \
           and (not does_move_leave_king_in_check(board_obj, 0,4,0,2)):
            real_moves.append((0, 2))

    return real_moves

def make_move(board_obj, fr, fc, tr, tc, promotion_piece=None):
    if board_obj.game_over:
        return False
    mover = board_obj.board[fr][fc]
    if not can_move_piece(board_obj, mover):
        return False

    valid_moves = get_legal_moves_for_square(board_obj, fr, fc)
    if (tr, tc) not in valid_moves:
        return False

    move_info = make_move_in_place(board_obj, fr, fc, tr, tc, promotion_piece)
    if not move_info["move_done"]:
        return False

    move_str = f"{mover}@({fr},{fc})->({tr},{tc})"
    board_obj.move_history.append(move_str)

    check_end_of_game(board_obj)
    return True

piece_class_map = {
    WHITE_ROOK:   "ROOK",
    BLACK_ROOK:   "ROOK",
    WHITE_BISHOP: "BISHOP",
    BLACK_BISHOP: "BISHOP",
    WHITE_KNIGHT: "KNIGHT",
    BLACK_KNIGHT: "KNIGHT",
    WHITE_KING:   "KING",
    BLACK_KING:   "KING",
    WHITE_SHAMAN: "SHAMAN",
    BLACK_SHAMAN: "SHAMAN",
    WHITE_BISON:  "BISON",
    BLACK_BISON:  "BISON",
    WHITE_TOTEM:  "TOTEM",
    BLACK_TOTEM:  "TOTEM"
}

def make_move_in_place(board_obj, fr, fc, tr, tc, promotion_piece=None):
    move_info = {"move_done": False}
    if board_obj.game_over:
        return move_info

    mover = board_obj.board[fr][fc]
    if not can_move_piece(board_obj, mover):
        return move_info

    move_info["board_before"] = [row[:] for row in board_obj.board]
    move_info["white_king_moved"] = board_obj.white_king_moved
    move_info["white_left_rook_moved"] = board_obj.white_left_rook_moved
    move_info["white_right_rook_moved"] = board_obj.white_right_rook_moved
    move_info["black_king_moved"] = board_obj.black_king_moved
    move_info["black_left_rook_moved"] = board_obj.black_left_rook_moved
    move_info["black_right_rook_moved"] = board_obj.black_right_rook_moved

    move_info["white_totem_inherited"] = board_obj.white_totem_inherited
    move_info["black_totem_inherited"] = board_obj.black_totem_inherited

    move_info["turn_white"] = board_obj.turn_white
    move_info["game_over"] = board_obj.game_over
    move_info["winner"] = board_obj.winner

    ok = _apply_normal_move(board_obj, fr, fc, tr, tc, promotion_piece)
    if not ok:
        return move_info

    board_obj.turn_white = not board_obj.turn_white
    move_info["move_done"] = True
    return move_info

def undo_move_in_place(board_obj, move_info):
    if not move_info.get("move_done", False):
        return

    board_obj.board = [row[:] for row in move_info["board_before"]]
    board_obj.white_king_moved = move_info["white_king_moved"]
    board_obj.white_left_rook_moved = move_info["white_left_rook_moved"]
    board_obj.white_right_rook_moved = move_info["white_right_rook_moved"]
    board_obj.black_king_moved = move_info["black_king_moved"]
    board_obj.black_left_rook_moved = move_info["black_left_rook_moved"]
    board_obj.black_right_rook_moved = move_info["black_right_rook_moved"]

    board_obj.white_totem_inherited = move_info["white_totem_inherited"]
    board_obj.black_totem_inherited = move_info["black_totem_inherited"]

    board_obj.turn_white = move_info["turn_white"]
    board_obj.game_over = move_info["game_over"]
    board_obj.winner = move_info["winner"]

def _apply_normal_move(board_obj, fr, fc, tr, tc, promotion_piece):
    mover = board_obj.board[fr][fc]
    occupant = board_obj.board[tr][tc]

    # Arrocco classico
    if mover == WHITE_KING and board_obj.white_faction == "classici":
        if (fr, fc) == (7,4) and (tr, tc) == (7,6):
            return white_castle_short_inplace_classical(board_obj)
        if (fr, fc) == (7,4) and (tr, tc) == (7,2):
            return white_castle_long_inplace_classical(board_obj)

    if mover == BLACK_KING and board_obj.black_faction == "classici":
        if (fr, fc) == (0,4) and (tr, tc) == (0,6):
            return black_castle_short_inplace_classical(board_obj)
        if (fr, fc) == (0,4) and (tr, tc) == (0,2):
            return black_castle_long_inplace_classical(board_obj)

    # Arrocco nativi
    if mover == WHITE_KING and board_obj.white_faction == "nativi":
        if (fr, fc) == (7,4) and (tr, tc) == (7,6):
            return white_castle_short_inplace_nativi(board_obj)
        if (fr, fc) == (7,4) and (tr, tc) == (7,2):
            return white_castle_long_inplace_nativi(board_obj)

    if mover == BLACK_KING and board_obj.black_faction == "nativi":
        if (fr, fc) == (0,4) and (tr, tc) == (0,6):
            return black_castle_short_inplace_nativi(board_obj)
        if (fr, fc) == (0,4) and (tr, tc) == (0,2):
            return black_castle_long_inplace_nativi(board_obj)

    # Aggiorna flag Re/Torri/Totem
    if mover == WHITE_KING:
        board_obj.white_king_moved = True
    if mover == BLACK_KING:
        board_obj.black_king_moved = True

    if mover in (WHITE_ROOK, WHITE_TOTEM):
        if (fr, fc) == (7, 0):
            board_obj.white_left_rook_moved = True
        elif (fr, fc) == (7, 7):
            board_obj.white_right_rook_moved = True
    if mover in (BLACK_ROOK, BLACK_TOTEM):
        if (fr, fc) == (0, 0):
            board_obj.black_left_rook_moved = True
        elif (fr, fc) == (0, 7):
            board_obj.black_right_rook_moved = True

    # Promozione pedoni
    if mover == WHITE_PAWN and tr == 0:
        if occupant != EMPTY and is_white_piece(occupant):
            return False
        board_obj.board[tr][tc] = WHITE_QUEEN
        board_obj.board[fr][fc] = EMPTY
        _check_inherit_power(board_obj, mover, occupant)
        return True
    if mover == BLACK_PAWN and tr == 7:
        if occupant != EMPTY and is_black_piece(occupant):
            return False
        board_obj.board[tr][tc] = BLACK_QUEEN
        board_obj.board[fr][fc] = EMPTY
        _check_inherit_power(board_obj, mover, occupant)
        return True

    # Bisonte
    if mover in (WHITE_BISON, BLACK_BISON):
        return _apply_bison_move(board_obj, fr, fc, tr, tc)

    # Cattura standard
    if occupant != EMPTY:
        if is_white_piece(mover) == is_white_piece(occupant):
            return False
        if occupant in (WHITE_BISON, BLACK_BISON) and mover in (WHITE_PAWN, BLACK_PAWN):
            return False

    board_obj.board[tr][tc] = mover
    board_obj.board[fr][fc] = EMPTY

    _check_inherit_power(board_obj, mover, occupant)
    return True

def _apply_bison_move(board_obj, fr, fc, tr, tc):
    bison = board_obj.board[fr][fc]
    board_obj.board[fr][fc] = EMPTY
    occupant = board_obj.board[tr][tc]

    if occupant == EMPTY:
        board_obj.board[tr][tc] = bison
    else:
        if is_white_piece(bison) == is_white_piece(occupant):
            board_obj.board[fr][fc] = bison
            return False
        if occupant in (WHITE_PAWN, BLACK_PAWN):
            dr = tr - fr
            dc = tc - fc
            if dr != 0:
                dr //= abs(dr)
            if dc != 0:
                dc //= abs(dc)
            push_r = tr + dr
            push_c = tc + dc
            if in_bounds(push_r, push_c) and board_obj.board[push_r][push_c] == EMPTY:
                board_obj.board[push_r][push_c] = occupant
                board_obj.board[tr][tc] = bison
            else:
                board_obj.board[fr][fc] = bison
                return False
        else:
            board_obj.board[tr][tc] = bison

    _check_inherit_power(board_obj, bison, occupant)
    return True

def does_move_leave_king_in_check(board_obj, fr, fc, tr, tc):
    if board_obj.game_over:
        return True
    mover = board_obj.board[fr][fc]

    if not can_move_piece(board_obj, mover):
        return True

    move_info = make_move_in_place(board_obj, fr, fc, tr, tc)
    if not move_info["move_done"]:
        return True

    mover_is_white = is_white_piece(mover)
    in_check_now = is_in_check(board_obj, mover_is_white)
    undo_move_in_place(board_obj, move_info)
    return in_check_now

def check_end_of_game(board_obj):
    if board_obj.game_over:
        return
    moves = get_all_legal_moves(board_obj, board_obj.turn_white)
    if not moves:
        if is_in_check(board_obj, board_obj.turn_white):
            board_obj.game_over = True
            board_obj.winner = "Black" if board_obj.turn_white else "White"
        else:
            board_obj.game_over = True
            board_obj.winner = "Draw"

def _check_inherit_power(board_obj, mover, occupant):
    if occupant in (WHITE_PAWN, BLACK_PAWN, WHITE_QUEEN, BLACK_QUEEN, EMPTY):
        return
    if is_white_piece(mover):
        if occupant in piece_class_map:
            board_obj.white_totem_inherited = piece_class_map[occupant]
    else:
        if occupant in piece_class_map:
            board_obj.black_totem_inherited = piece_class_map[occupant]

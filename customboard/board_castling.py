# board_castling.py

from piece_movement.piece_movement_common import (
    EMPTY,
    WHITE_KING, BLACK_KING,
    WHITE_ROOK, BLACK_ROOK,
    WHITE_TOTEM, BLACK_TOTEM
    #is_in_check
)

from .board_state import is_in_check

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

# board_state.py

from piece_movement.piece_attacks import is_white_piece, is_square_attacked
from piece_movement.piece_movement_common import find_king 

def is_in_check(board_obj, white=True):
    kpos = find_king(board_obj.board, white)
    if not kpos or kpos[0] is None:
        return False
    (kr, kc) = kpos
    return is_square_attacked(board_obj.board, kr, kc, by_white=(not white))

def is_game_over(board_obj):
    return board_obj.game_over

def get_winner(board_obj):
    return board_obj.winner

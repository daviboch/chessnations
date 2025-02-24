# board_main.py

from piece_movement.piece_movement_common import (
    EMPTY,
    BOARD_SIZE,
    WHITE_PAWN, BLACK_PAWN,
    WHITE_TOTEM, BLACK_TOTEM,
    WHITE_BISON, BLACK_BISON,
    WHITE_SHAMAN, BLACK_SHAMAN,
    WHITE_ROOK, BLACK_ROOK,
    WHITE_KNIGHT, BLACK_KNIGHT,
    WHITE_BISHOP, BLACK_BISHOP,
    WHITE_QUEEN, BLACK_QUEEN,
    WHITE_KING, BLACK_KING,
    is_white_piece, is_black_piece
)
from .board_setup import _setup_initial_board
from .board_moves import (
    can_move_piece,
    get_all_legal_moves,
    get_legal_moves_for_square,
    make_move_in_place,
    undo_move_in_place,
    make_move
)
from .board_state import (
    is_game_over,
    get_winner
)

class CustomBoard:
    def __init__(self, parent=None, white_faction="nativi", black_faction="classici"):
        self.parent = parent
        self.white_faction = white_faction
        self.black_faction = black_faction

        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn_white = True
        self.move_history = []
        self.game_over = False
        self.winner = None

        self.white_king_moved = False
        self.white_left_rook_moved = False
        self.white_right_rook_moved = False

        self.black_king_moved = False
        self.black_left_rook_moved = False
        self.black_right_rook_moved = False

        # Inizializza la scacchiera
        _setup_initial_board(self)

    def can_move_piece(self, piece):
        return can_move_piece(self, piece)

    def is_game_over(self):
        return is_game_over(self)

    def get_winner(self):
        return get_winner(self)

    def is_in_check(self, white=True):
        # import locale per evitare import circolari
        from .board_state import is_in_check
        return is_in_check(self, white)

    def get_all_legal_moves(self, white=True):
        return get_all_legal_moves(self, white)

    def get_legal_moves_for_square(self, r, c):
        return get_legal_moves_for_square(self, r, c)

    #def does_move_leave_king_in_check(self, fr, fc, tr, tc):
    #    return does_move_leave_king_in_check(self, fr, fc, tr, tc)

    def make_move(self, fr, fc, tr, tc, promotion_piece=None):
        return make_move(self, fr, fc, tr, tc, promotion_piece)

    def make_move_in_place(self, fr, fc, tr, tc, promotion_piece=None):
        return make_move_in_place(self, fr, fc, tr, tc, promotion_piece)

    def undo_move_in_place(self, move_info):
        return undo_move_in_place(self, move_info)

    #def check_end_of_game(self):
    #    return check_end_of_game(self)

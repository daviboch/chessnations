# board_setup.py

from piece_movement.piece_movement_common import (
    EMPTY,
    BOARD_SIZE,
    BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING,
    BLACK_PAWN, BLACK_TOTEM, BLACK_BISON, BLACK_SHAMAN,
    WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN, WHITE_KING,
    WHITE_PAWN, WHITE_TOTEM, WHITE_BISON, WHITE_SHAMAN
)

def _setup_initial_board(board_obj):
    # Neri
    if board_obj.black_faction == "classici":
        board_obj.board[0] = [
            BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN,
            BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK
        ]
        for c in range(BOARD_SIZE):
            board_obj.board[1][c] = BLACK_PAWN
    else:
        # Nativi neri
        board_obj.board[0] = [
            BLACK_TOTEM, BLACK_BISON, BLACK_SHAMAN, BLACK_QUEEN,
            BLACK_KING, BLACK_SHAMAN, BLACK_BISON, BLACK_TOTEM
        ]
        for c in range(BOARD_SIZE):
            board_obj.board[1][c] = BLACK_PAWN

    # Bianchi
    if board_obj.white_faction == "classici":
        board_obj.board[7] = [
            WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN,
            WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK
        ]
        for c in range(BOARD_SIZE):
            board_obj.board[6][c] = WHITE_PAWN
    else:
        # Nativi bianchi
        board_obj.board[7] = [
            WHITE_TOTEM, WHITE_BISON, WHITE_SHAMAN, WHITE_QUEEN,
            WHITE_KING, WHITE_SHAMAN, WHITE_BISON, WHITE_TOTEM
        ]
        for c in range(BOARD_SIZE):
            board_obj.board[6][c] = WHITE_PAWN

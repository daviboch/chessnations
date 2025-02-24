# board.py

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

def _setup_initial_board(board_obj):
    """
    Funzione che imposta la disposizione iniziale dei pezzi sulla scacchiera,
    spostata da board_setup.py.
    """
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


class CustomBoard:
    """
    Classe principale che sostituisce board_main.py, raggruppando anche la parte
    di board_setup.py e board_state.py. La logica delle mosse (board_moves e board_castling)
    è spostata su moves.py.
    """
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

    # ---------------------------
    # Metodi "stato di gioco"
    # ---------------------------
    def is_game_over(self):
        """
        Ritorna True se la partita risulta terminata (matto o patta).
        Prima era is_game_over() in board_state.py.
        """
        from .moves import is_game_over
        return is_game_over(self)

    def get_winner(self):
        """
        Ritorna il vincitore ("White", "Black" o "Draw"), oppure None se la partita non è finita.
        Prima era get_winner() in board_state.py.
        """
        from .moves import get_winner
        return get_winner(self)

    def is_in_check(self, white=True):
        """
        Restituisce True se il Re bianco/nero è sotto scacco.
        Prima era definito in board_state.py, poi richiamato da board_main.py.
        """
        from .moves import is_in_check
        return is_in_check(self, white)

    # ---------------------------
    # Metodi di supporto / alias
    # ---------------------------
    def can_move_piece(self, piece):
        """
        Controlla se 'piece' è muovibile in base al turno.
        Prima era in board_moves.py (funzione can_move_piece).
        """
        from .moves import can_move_piece
        return can_move_piece(self, piece)

    def get_all_legal_moves(self, white=True):
        """
        Ritorna tutte le mosse legali per il colore specificato.
        Prima era get_all_legal_moves in board_moves.py.
        """
        from .moves import get_all_legal_moves
        return get_all_legal_moves(self, white)

    def get_legal_moves_for_square(self, r, c):
        """
        Ritorna tutte le mosse legali di un pezzo in (r, c).
        Prima in board_moves.py.
        """
        from .moves import get_legal_moves_for_square
        return get_legal_moves_for_square(self, r, c)

    def make_move(self, fr, fc, tr, tc, promotion_piece=None):
        """
        Esegue una mossa se è valida, e aggiorna lo stato (move_history, fine partita, ecc.).
        Prima era in board_moves.py.
        """
        from .moves import make_move
        return make_move(self, fr, fc, tr, tc, promotion_piece)

    def make_move_in_place(self, fr, fc, tr, tc, promotion_piece=None):
        """
        Variante in-place della mossa, usata ad esempio dall'IA e per i controlli di scacco.
        Prima in board_moves.py.
        """
        from .moves import make_move_in_place
        return make_move_in_place(self, fr, fc, tr, tc, promotion_piece)

    def undo_move_in_place(self, move_info):
        """
        Annulla l'ultima mossa, usando i dati salvati in move_info.
        Prima era in board_moves.py.
        """
        from .moves import undo_move_in_place
        return undo_move_in_place(self, move_info)

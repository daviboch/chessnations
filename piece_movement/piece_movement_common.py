# piece_movement_common.py

BOARD_SIZE = 8

EMPTY           = 0
WHITE_PAWN      = 1
BLACK_PAWN      = 2
WHITE_TOTEM     = 3
BLACK_TOTEM     = 4
WHITE_BISON     = 5
BLACK_BISON     = 6
WHITE_SHAMAN    = 7
BLACK_SHAMAN    = 8
WHITE_ROOK      = 9
BLACK_ROOK      = 10
WHITE_KNIGHT    = 11
BLACK_KNIGHT    = 12
WHITE_BISHOP    = 13
BLACK_BISHOP    = 14
WHITE_QUEEN     = 15
BLACK_QUEEN     = 16
WHITE_KING      = 17
BLACK_KING      = 18

PIECE_NAME_MAP = {
    EMPTY:         "EMPTY",
    WHITE_PAWN:    "WHITE_PAWN",
    BLACK_PAWN:    "BLACK_PAWN",
    WHITE_TOTEM:   "WHITE_TOTEM",
    BLACK_TOTEM:   "BLACK_TOTEM",
    WHITE_BISON:   "WHITE_BISON",
    BLACK_BISON:   "BLACK_BISON",
    WHITE_SHAMAN:  "WHITE_SHAMAN",
    BLACK_SHAMAN:  "BLACK_SHAMAN",
    WHITE_ROOK:    "WHITE_ROOK",
    BLACK_ROOK:    "BLACK_ROOK",
    WHITE_KNIGHT:  "WHITE_KNIGHT",
    BLACK_KNIGHT:  "BLACK_KNIGHT",
    WHITE_BISHOP:  "WHITE_BISHOP",
    BLACK_BISHOP:  "BLACK_BISHOP",
    WHITE_QUEEN:   "WHITE_QUEEN",
    BLACK_QUEEN:   "BLACK_QUEEN",
    WHITE_KING:    "WHITE_KING",
    BLACK_KING:    "BLACK_KING",
}

def is_white_piece(p):
    return (p != EMPTY) and ((p & 1) == 1)

def is_black_piece(p):
    return (p != EMPTY) and ((p & 1) == 0)

def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def find_king(bstate, white):
    """
    Restituisce la posizione (r, c) del Re bianco o nero.
    Se non trovato, ritorna (None, None).
    """
    king = WHITE_KING if white else BLACK_KING
    for rr in range(BOARD_SIZE):
        for cc in range(BOARD_SIZE):
            if bstate[rr][cc] == king:
                return (rr, cc)
    return (None, None)

# --------------------------------------------------------------------------
# Import delle funzioni di movimento "classico" e "nativo" (senza abilità speciali).
# --------------------------------------------------------------------------
from .classic_piece_movement import (
    get_pawn_moves,
    get_rook_moves,
    get_knight_moves,
    get_bishop_moves,
    get_queen_moves,
    get_king_moves
)
from .native_piece_movement import (
    get_totem_moves,  # Non più usato direttamente, ma lasciato per compatibilità
    get_bison_moves,
    get_shaman_moves
)

# Piccolo dispatcher per “potere ereditato” base (senza abilità speciali).
def get_inherited_moves_basic(board, r, c, piece_class: str):
    """
    Ritorna le mosse "base" del pezzo indicato da piece_class.
    Non includiamo abilità extra come freeze, push, etc.
    """
    if piece_class == "KNIGHT":
        return get_knight_moves(board, r, c)
    elif piece_class == "BISHOP":
        return get_bishop_moves(board, r, c)
    elif piece_class == "ROOK":
        return get_rook_moves(board, r, c)
    elif piece_class == "KING":
        # Se ereditato = KING, di fatto è un duplicato del re. 
        # Potremmo aggiungere, ma TOTEM già si muove come Re,
        # quindi potrebbe diventare solo un allargamento di scelte?
        return get_king_moves(board, r, c)
    elif piece_class == "SHAMAN":
        # "base" => consideriamo come un "mini-bishop a 2 passi" (es. get_shaman_moves),
        # ma se vogliamo evitare freeze/salto speciale potremmo simulare un bishop.
        # Per semplicità, usiamo la funzione "get_shaman_moves" pura
        # (che fa salti diagonali di 2) ma NON c'è freeze qui
        return get_shaman_moves(board, r, c)
    elif piece_class == "BISON":
        # Il Bison "puro" muove come una Rook + diagonali con "richiamo"
        # ma con push del pedone. Se non vogliamo la push e la "richiamo",
        # potremmo ridurlo a get_rook_moves. Oppure usiamo get_bison_moves
        # se vogliamo la parte di diagonale? 
        # Per non perdere del tutto la "forma" bison, useremo get_bison_moves,
        # ma occhio che in 'moves.py' la push si realizza in _apply_bison_move.
        # In questa sede, restituisce la geometria (Rook + eventuale diagonale).
        # Non scatena freeze, né logiche extra. Va bene.
        return get_bison_moves(board, r, c)
    elif piece_class == "TOTEM":
        # In caso un TOTEM catturi un TOTEM, e "erediti TOTEM"? 
        # Attualmente era un Re "allungato". Ora è ridotto a Re base.
        # Usiamo get_king_moves come fallback.
        return get_king_moves(board, r, c)
    return []

def get_all_pseudo_moves_for_square(board_obj, turn_white, r, c):
    """
    Ritorna TUTTE le mosse pseudo-legali di un pezzo in (r,c),
    basate sui pattern di movimento e cattura, ma SENZA considerare
    lo scacco al proprio Re (questo controllo avverrà dopo).
    Adesso accettiamo board_obj per poter gestire il TOTEM ereditato.
    """
    p = board_obj.board[r][c]
    if p == EMPTY:
        return []
    # Controllo colore
    if turn_white and not is_white_piece(p):
        return []
    if (not turn_white) and not is_black_piece(p):
        return []

    # 1) Gestione TOTEM con potere ereditato
    if p in (WHITE_TOTEM, BLACK_TOTEM):
        moves = []
        # a) Movimento base da Re
        moves += get_king_moves(board_obj.board, r, c)

        # b) Se c’è un potere ereditato, aggiungiamo quella geometria.
        if is_white_piece(p):
            inherited = board_obj.white_totem_inherited
        else:
            inherited = board_obj.black_totem_inherited

        if inherited is not None:
            inherited_moves = get_inherited_moves_basic(board_obj.board, r, c, inherited)
            # Uniamo le mosse, evitando duplicati
            # (in certi casi potremmo unire tranquillamente, oppure usare set)
            all_set = set(moves + inherited_moves)
            moves = list(all_set)

        return moves

    # 2) Altrimenti seguiamo la normale logica per gli altri pezzi
    if p in (WHITE_PAWN, BLACK_PAWN):
        return get_pawn_moves(board_obj.board, r, c)
    elif p in (WHITE_ROOK, BLACK_ROOK):
        return get_rook_moves(board_obj.board, r, c)
    elif p in (WHITE_BISON, BLACK_BISON):
        return get_bison_moves(board_obj.board, r, c)
    elif p in (WHITE_KNIGHT, BLACK_KNIGHT):
        return get_knight_moves(board_obj.board, r, c)
    elif p in (WHITE_BISHOP, BLACK_BISHOP):
        return get_bishop_moves(board_obj.board, r, c)
    elif p in (WHITE_SHAMAN, BLACK_SHAMAN):
        return get_shaman_moves(board_obj.board, r, c)
    elif p in (WHITE_QUEEN, BLACK_QUEEN):
        return get_queen_moves(board_obj.board, r, c)
    elif p in (WHITE_KING, BLACK_KING):
        return get_king_moves(board_obj.board, r, c)
    # TOTEM era già gestito sopra
    return []

# ai_engine.py

import time
import random

from customboard import CustomBoard
from piece_movement.piece_movement_common import (
    EMPTY,
    WHITE_PAWN, BLACK_PAWN,
    WHITE_KING, BLACK_KING,
    is_white_piece, is_black_piece
)
from evaluation import (
    static_evaluation,
    deterministic_evaluation,
    evaluation_breakdown,
    PIECE_VALUE
)

DEBUG_MODE = True

def board_position_hash(board_obj):
    rows = []
    for r in range(8):
        row_pieces = []
        for c in range(8):
            row_pieces.append(str(board_obj.board[r][c]))
        rows.append(",".join(row_pieces))
    turn_char = "W" if board_obj.turn_white else "B"
    return f"{'/'.join(rows)} {turn_char}"

USE_MOVE_ORDERING = True
USE_TRANSPOSITION = True
MAX_DEPTH_TT = 64

USE_NULL_MOVE = True
USE_QUIESCENCE = False
NULL_MOVE_REDUCTION = 1
QUIESCENCE_MAX_DEPTH = 3

USE_ASPIRATION_WINDOW = True
ASPIRATION_DELTA = 0.75

TRANSPOSITION_TABLE = {}

expansions_count = 0
prunes_count = 0
aspiration_fails_count = 0
tt_hits_count = 0

def reset_debug_counters():
    global expansions_count, prunes_count, aspiration_fails_count, tt_hits_count
    expansions_count = 0
    prunes_count = 0
    aspiration_fails_count = 0
    tt_hits_count = 0

def print_debug_counters(prefix=""):
    if DEBUG_MODE:
        print(f"[DEBUG] {prefix} expansions={expansions_count}, prunes={prunes_count}, "
              f"aspirationFails={aspiration_fails_count}, ttHits={tt_hits_count}")

def mvv_lva_score(board_obj: CustomBoard, move):
    (fr, fc, tr, tc) = move
    attacker = board_obj.board[fr][fc]
    victim = board_obj.board[tr][tc]
    if victim == EMPTY or victim == attacker:
        return -1
    val_victim = PIECE_VALUE.get(victim, 0)
    val_attacker = PIECE_VALUE.get(attacker, 0)
    return 100 * val_victim - val_attacker

def order_moves(board_obj: CustomBoard, moves: list, pv_move=None) -> list:
    if not USE_MOVE_ORDERING:
        return moves

    if pv_move and pv_move in moves:
        sorted_rest = sorted(
            [m for m in moves if m != pv_move],
            key=lambda mv: mvv_lva_score(board_obj, mv),
            reverse=True
        )
        return [pv_move] + sorted_rest
    else:
        return sorted(
            moves,
            key=lambda mv: mvv_lva_score(board_obj, mv),
            reverse=True
        )

def quiescence_search(board_obj: CustomBoard, alpha: float, beta: float, depth_q: int = 0) -> float:
    global prunes_count
    if depth_q > QUIESCENCE_MAX_DEPTH or board_obj.is_game_over():
        return static_evaluation(board_obj)

    stand_pat = static_evaluation(board_obj)
    if board_obj.turn_white:
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if stand_pat < beta:
            beta = stand_pat

    moves = board_obj.get_all_legal_moves(board_obj.turn_white)
    captures = []
    for mv in moves:
        (fr, fc, tr, tc) = mv
        occupant = board_obj.board[tr][tc]
        mover = board_obj.board[fr][fc]
        if occupant != EMPTY and occupant != mover:
            captures.append(mv)

    captures = order_moves(board_obj, captures, pv_move=None)

    if board_obj.turn_white:
        for mv in captures:
            (fr, fc, tr, tc) = mv
            move_info = board_obj.make_move_in_place(fr, fc, tr, tc)
            if not move_info["move_done"]:
                continue
            val = quiescence_search(board_obj, alpha, beta, depth_q + 1)
            board_obj.undo_move_in_place(move_info)
            if val > alpha:
                alpha = val
            if alpha >= beta:
                prunes_count += 1
                return beta
        return alpha
    else:
        for mv in captures:
            (fr, fc, tr, tc) = mv
            move_info = board_obj.make_move_in_place(fr, fc, tr, tc)
            if not move_info["move_done"]:
                continue
            val = quiescence_search(board_obj, alpha, beta, depth_q + 1)
            board_obj.undo_move_in_place(move_info)
            if val < beta:
                beta = val
            if beta <= alpha:
                prunes_count += 1
                return alpha
        return beta

def minimax_alpha_beta(board_obj: CustomBoard, depth: int, alpha: float, beta: float,
                       last_was_capture: bool=False, pv_move=None):
    global expansions_count, prunes_count, tt_hits_count
    expansions_count += 1

    if depth <= 0 or board_obj.is_game_over():
        if last_was_capture and USE_QUIESCENCE:
            q_val = quiescence_search(board_obj, alpha, beta, 0)
            return (q_val, [])
        else:
            return (static_evaluation(board_obj), [])

    pos_hash = None
    if USE_TRANSPOSITION:
        pos_hash = board_position_hash(board_obj)
        if pos_hash in TRANSPOSITION_TABLE:
            (stored_depth, stored_score, stored_line) = TRANSPOSITION_TABLE[pos_hash]
            if stored_depth >= depth:
                tt_hits_count += 1
                return (stored_score, stored_line)

    moves = board_obj.get_all_legal_moves(board_obj.turn_white)
    if not moves:
        # Nessuna mossa
        if last_was_capture and USE_QUIESCENCE:
            val = quiescence_search(board_obj, alpha, beta, 0)
            if USE_TRANSPOSITION and pos_hash:
                TRANSPOSITION_TABLE[pos_hash] = (depth, val, [])
            return (val, [])
        else:
            val = static_evaluation(board_obj)
            if USE_TRANSPOSITION and pos_hash:
                TRANSPOSITION_TABLE[pos_hash] = (depth, val, [])
            return (val, [])

    is_maximizing = board_obj.turn_white
    best_line = []
    best_val = -float('inf') if is_maximizing else float('inf')

    # NULL MOVE
    if USE_NULL_MOVE and depth >= 2 and board_obj.turn_white and (not board_obj.is_in_check(True)):
        def can_do_null_move(bobj: CustomBoard)->bool:
            return not bobj.is_in_check(bobj.turn_white)
        def do_null_move(bobj: CustomBoard):
            bobj.turn_white = not bobj.turn_white
        def undo_null_move(bobj: CustomBoard):
            bobj.turn_white = not bobj.turn_white

        if can_do_null_move(board_obj):
            do_null_move(board_obj)
            null_depth = depth - 1 - NULL_MOVE_REDUCTION
            if null_depth < 0:
                null_depth = 0
            val_null, _ = minimax_alpha_beta(board_obj, null_depth, alpha, beta,
                                             last_was_capture=False, pv_move=None)
            undo_null_move(board_obj)
            if is_maximizing:
                if val_null >= beta:
                    prunes_count += 1
                    return (beta, [])
            else:
                if val_null <= alpha:
                    prunes_count += 1
                    return (alpha, [])

    ordered_moves = order_moves(board_obj, moves, pv_move)

    if is_maximizing:
        for mv in ordered_moves:
            (fr, fc, tr, tc) = mv
            captured_piece = board_obj.board[tr][tc]
            move_info = board_obj.make_move_in_place(fr, fc, tr, tc)
            if not move_info["move_done"]:
                continue
            new_last_was_capture = (captured_piece != EMPTY and captured_piece not in (WHITE_PAWN, BLACK_PAWN))
            val, sub_line = minimax_alpha_beta(
                board_obj, depth-1, alpha, beta,
                last_was_capture=new_last_was_capture,
                pv_move=None
            )
            board_obj.undo_move_in_place(move_info)

            if val > best_val:
                best_val = val
                best_line = [mv] + sub_line
            alpha = max(alpha, best_val)
            if alpha >= beta:
                prunes_count += 1
                break
    else:
        for mv in ordered_moves:
            (fr, fc, tr, tc) = mv
            captured_piece = board_obj.board[tr][tc]
            move_info = board_obj.make_move_in_place(fr, fc, tr, tc)
            if not move_info["move_done"]:
                continue
            new_last_was_capture = (captured_piece != EMPTY and captured_piece not in (WHITE_PAWN, BLACK_PAWN))
            val, sub_line = minimax_alpha_beta(
                board_obj, depth-1, alpha, beta,
                last_was_capture=new_last_was_capture,
                pv_move=None
            )
            board_obj.undo_move_in_place(move_info)

            if val < best_val:
                best_val = val
                best_line = [mv] + sub_line
            beta = min(beta, best_val)
            if beta <= alpha:
                prunes_count += 1
                break

    if USE_TRANSPOSITION and pos_hash:
        TRANSPOSITION_TABLE[pos_hash] = (depth, best_val, best_line)

    return (best_val, best_line)

def minimax_decision(board_obj: CustomBoard, depth: int, alpha=-float('inf'), beta=float('inf'), pv_move=None):
    global expansions_count, prunes_count, tt_hits_count

    moves = board_obj.get_all_legal_moves(board_obj.turn_white)
    if not moves:
        return (None, [])

    is_maximizing = board_obj.turn_white
    best_val = -float('inf') if is_maximizing else float('inf')
    best_line = []

    ordered_moves = order_moves(board_obj, moves, pv_move)

    for mv in ordered_moves:
        (fr, fc, tr, tc) = mv
        captured_piece = board_obj.board[tr][tc]
        move_info = board_obj.make_move_in_place(fr, fc, tr, tc)
        if not move_info["move_done"]:
            continue
        new_last_was_capture = (captured_piece != EMPTY and captured_piece not in (WHITE_PAWN, BLACK_PAWN))
        val, sub_line = minimax_alpha_beta(
            board_obj, depth-1, alpha, beta,
            last_was_capture=new_last_was_capture,
            pv_move=None
        )
        board_obj.undo_move_in_place(move_info)

        if is_maximizing:
            if val > best_val:
                best_val = val
                best_line = [mv] + sub_line
            alpha = max(alpha, best_val)
            if alpha >= beta:
                prunes_count += 1
                break
        else:
            if val < best_val:
                best_val = val
                best_line = [mv] + sub_line
            beta = min(beta, best_val)
            if beta <= alpha:
                prunes_count += 1
                break

    return (best_val, best_line)

def iterative_deepening_decision(board_obj: CustomBoard, max_depth=4, max_time=6):
    global expansions_count, prunes_count, aspiration_fails_count, tt_hits_count
    reset_debug_counters()

    best_move = None
    best_line = []
    start_time = time.time()
    prev_val = 0.0

    prev_pv_move = None

    for d in range(1, max_depth+1):
        iteration_start_time = time.time()

        if USE_ASPIRATION_WINDOW and d > 1:
            alpha_asp = prev_val - ASPIRATION_DELTA
            beta_asp  = prev_val + ASPIRATION_DELTA
            val, line = minimax_decision(board_obj, d, alpha_asp, beta_asp, pv_move=prev_pv_move)
            if val is not None and (val <= alpha_asp or val >= beta_asp):
                aspiration_fails_count += 1
                val, line = minimax_decision(board_obj, d, -float('inf'), float('inf'), pv_move=prev_pv_move)
        else:
            val, line = minimax_decision(board_obj, d, -float('inf'), float('inf'), pv_move=prev_pv_move)

        iteration_time = time.time() - iteration_start_time

        if line:
            best_move = line[0]
            best_line = line
        if val is not None:
            prev_val = val

        prev_pv_move = best_move

        if DEBUG_MODE:
            from chessapp import convert_move_to_algebraic_detailed
            if best_move:
                human_move = convert_move_to_algebraic_detailed(best_move, board_obj)
            else:
                human_move = "None"
            print(f"[DEBUG] ID Depth {d}: best move = {human_move}, val = {val}, time={iteration_time:.3f}s")
            print_debug_counters(prefix=f"Depth {d} (after)")

        total_elapsed = time.time() - start_time
        if total_elapsed > max_time:
            break

    return best_move

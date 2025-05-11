import chess
import math
import time
from piece_square_table import (
    pst_pawn, pst_knight, pst_bishop, pst_rook,
    pst_queen, pst_king, pst_king_end, flip
)
from collections import defaultdict

# 1) Helpers --------------------------------------------------------------

def is_endgame(board: chess.Board) -> bool:
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + \
             len(board.pieces(chess.QUEEN, chess.BLACK))
    minors = sum(len(board.pieces(pt, c))
                 for pt in (chess.ROOK, chess.BISHOP, chess.KNIGHT)
                 for c in (chess.WHITE, chess.BLACK))
    return queens == 0 or (queens == 1 and minors <= 1)

def is_passed(board: chess.Board, sq: int, color: bool) -> bool:
    f, r = chess.square_file(sq), chess.square_rank(sq)
    enemy = not color
    for df in (-1, 0, +1):
        nf = f + df
        if 0 <= nf < 8:
            for nr in (range(r+1, 8) if color else range(0, r)):
                if board.piece_at(chess.square(nf, nr)) == chess.Piece(chess.PAWN, enemy):
                    return False
    return True

def count_doubled_pawns(board: chess.Board, color: bool) -> int:
    files = defaultdict(int)
    for sq in board.pieces(chess.PAWN, color):
        files[chess.square_file(sq)] += 1
    return sum(cnt - 1 for cnt in files.values() if cnt > 1)

# 2) Quiescence -----------------------------------------------------------

def quiesce(board: chess.Board, alpha: float, beta: float) -> float:
    stand = evaluate(board)
    if stand >= beta:
        return beta
    if stand > alpha:
        alpha = stand

    for move in board.generate_legal_moves():
        if board.is_capture(move):
            board.push(move)
            score = -quiesce(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha

# 3) Evaluation -----------------------------------------------------------

def evaluate(board: chess.Board) -> int:
    # Terminal checks
    if board.is_checkmate():
        return 9999 if board.turn == chess.BLACK else -9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    if board.is_fivefold_repetition() or board.can_claim_threefold_repetition():
        return 0

    # Material
    def cnt(pt, col): return len(board.pieces(pt, col))
    wp, bp = cnt(chess.PAWN, chess.WHITE), cnt(chess.PAWN, chess.BLACK)
    wn, bn = cnt(chess.KNIGHT, chess.WHITE), cnt(chess.KNIGHT, chess.BLACK)
    wb, bb = cnt(chess.BISHOP, chess.WHITE), cnt(chess.BISHOP, chess.BLACK)
    wr, br = cnt(chess.ROOK, chess.WHITE), cnt(chess.ROOK, chess.BLACK)
    wq, bq = cnt(chess.QUEEN, chess.WHITE), cnt(chess.QUEEN, chess.BLACK)

    mat = 100*(wp-bp) + 300*(wn-bn) + 300*(wb-bb) + 500*(wr-br) + 900*(wq-bq)

    # PST
    pst = 0
    # White
    for sq in board.pieces(chess.PAWN,   chess.WHITE): pst += pst_pawn[sq]
    for sq in board.pieces(chess.KNIGHT, chess.WHITE): pst += pst_knight[sq]
    for sq in board.pieces(chess.BISHOP, chess.WHITE): pst += pst_bishop[sq]
    for sq in board.pieces(chess.ROOK,   chess.WHITE): pst += pst_rook[sq]
    for sq in board.pieces(chess.QUEEN,  chess.WHITE): pst += pst_queen[sq]
    king_tbl = pst_king_end if is_endgame(board) else pst_king
    for sq in board.pieces(chess.KING, chess.WHITE): pst += king_tbl[sq]
    # Black
    for sq in board.pieces(chess.PAWN,   chess.BLACK): pst -= pst_pawn[flip[sq]]
    for sq in board.pieces(chess.KNIGHT, chess.BLACK): pst -= pst_knight[flip[sq]]
    for sq in board.pieces(chess.BISHOP, chess.BLACK): pst -= pst_bishop[flip[sq]]
    for sq in board.pieces(chess.ROOK,   chess.BLACK): pst -= pst_rook[flip[sq]]
    for sq in board.pieces(chess.QUEEN,  chess.BLACK): pst -= pst_queen[flip[sq]]
    for sq in board.pieces(chess.KING,   chess.BLACK): pst -= king_tbl[flip[sq]]

    # Doubled pawns
    pst -= 30 * count_doubled_pawns(board, chess.WHITE)
    pst += 30 * count_doubled_pawns(board, chess.BLACK)

    # Passed pawns
    for sq in board.pieces(chess.PAWN, chess.WHITE):
        if is_passed(board, sq, chess.WHITE):
            pst += 20 * chess.square_rank(sq)
    for sq in board.pieces(chess.PAWN, chess.BLACK):
        if is_passed(board, sq, chess.BLACK):
            pst -= 20 * (7 - chess.square_rank(sq))

    # Pawn chains (fixed indexing)
    for sq in board.pieces(chess.PAWN, chess.WHITE):
        f, r = chess.square_file(sq), chess.square_rank(sq)
        for df in (-1, +1):
            nf, nr = f+df, r-1
            if 0 <= nf < 8 and 0 <= nr < 8:
                nb = chess.square(nf, nr)
                if board.piece_at(nb) == chess.Piece(chess.PAWN, chess.WHITE):
                    pst += 10
    for sq in board.pieces(chess.PAWN, chess.BLACK):
        f, r = chess.square_file(sq), chess.square_rank(sq)
        for df in (-1, +1):
            nf, nr = f+df, r+1
            if 0 <= nf < 8 and 0 <= nr < 8:
                nb = chess.square(nf, nr)
                if board.piece_at(nb) == chess.Piece(chess.PAWN, chess.BLACK):
                    pst -= 10

    # Isolated pawns
    for color, sign in ((chess.WHITE, +1), (chess.BLACK, -1)):
        files = {chess.square_file(sq) for sq in board.pieces(chess.PAWN, color)}
        for sq in board.pieces(chess.PAWN, color):
            f = chess.square_file(sq)
            if all(adj not in files for adj in (f-1, f+1)):
                pst -= 15 * sign

    # Pawn mobility
    for color, sign in ((chess.WHITE, +1), (chess.BLACK, -1)):
        dir_ = 8 if color==chess.WHITE else -8
        for sq in board.pieces(chess.PAWN, color):
            to_sq = sq + dir_
            if 0 <= to_sq < 64 and board.piece_at(to_sq) is None:
                pst += 5 * sign

    # In‐check bonus/penalty
    if board.is_check():
        pst += -100 if board.turn==chess.WHITE else +100

    score = mat + pst
    return score if board.turn==chess.WHITE else -score

# 4) Negamax with quiescence and alpha‐beta --------------------------------

def negamax(board, depth, alpha, beta, start_time, allowed_ms):
    if board.is_game_over():
        return evaluate(board)
    if time.time()-start_time >= allowed_ms/1000:
        return evaluate(board)
    if depth <= 0:
        return quiesce(board, alpha, beta)

    max_score = -math.inf
    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth-1, -beta, -alpha, start_time, allowed_ms)
        board.pop()
        if score > max_score:
            max_score = score
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return max_score

def find_best_move(board, depth=5, allowed_time_ms=1000):
    # **DEBUG**: inspect root position
    print("DEBUG legal moves:", list(board.legal_moves))
    print("DEBUG eval startpos:", evaluate(board))

    start_time = time.time()
    best_move, best_score = None, -math.inf
    alpha, beta = -math.inf, math.inf

    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth-1, -beta, -alpha, start_time, allowed_time_ms)
        board.pop()
        if score > best_score:
            best_score, best_move = score, move
        alpha = max(alpha, score)

    return best_move

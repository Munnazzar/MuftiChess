import chess
import math
import time
from piece_square_table import *

def evaluate(board):
    allwp = board.pieces(chess.PAWN, chess.WHITE)
    wp = len(allwp)
    allwn = board.pieces(chess.KNIGHT, chess.WHITE)
    wn = len(allwn)
    allwb = board.pieces(chess.BISHOP, chess.WHITE)
    wb = len(allwb)
    allwr = board.pieces(chess.ROOK, chess.WHITE)
    wr = len(allwr)
    allwq = board.pieces(chess.QUEEN, chess.WHITE)
    wq = len(allwq)
    allbp = board.pieces(chess.PAWN, chess.BLACK)
    bp = len(allbp)
    allbn = board.pieces(chess.KNIGHT, chess.BLACK)
    bn = len(allbn)
    allbb = board.pieces(chess.BISHOP, chess.BLACK)
    bb = len(allbb)
    allbr = board.pieces(chess.ROOK, chess.BLACK)
    br = len(allbr)
    allbq = board.pieces(chess.QUEEN, chess.BLACK)
    bq = len(allbq)

    
    PAWN_SCORE = 100
    BISHOP_KNIGHT_SCORE = 300
    ROOK_SCORE = 500
    QUEEN_SCORE = 900
    #100 points for pawns, 300 for bishops/knights, 500 for rooks, 900 for queen
    relative_material_score = 100*(wp-bp) + 300*(wn-bn) + 300*(wb-bb) + 500*(wr-br) + 900*(wq-bq)
    
    white_pawn_sum = sum(pst_pawn[i] for i in allwp)
    white_bishop_sum = sum(pst_bishop[i] for i in allwb)
    white_knight_sum = sum(pst_knight[i] for i in allwn)
    white_rook_sum = sum(pst_rook[i] for i in allwr)
    white_queen_sum = sum(pst_queen[i] for i in allwq)
    white_king_sum = sum(pst_king[i] for i in board.pieces(chess.KING, chess.WHITE))
    black_pawn_sum = sum(pst_pawn[flip[i]] for i in allbp)
    black_bishop_sum = sum(pst_bishop[flip[i]] for i in allbb)
    black_knight_sum = sum(pst_knight[flip[i]] for i in allbn)
    black_rook_sum = sum(pst_rook[flip[i]] for i in allbr)
    black_queen_sum = sum(pst_queen[flip[i]] for i in allbq)
    black_king_sum = sum(pst_king[flip[i]] for i in board.pieces(chess.KING, chess.BLACK))

    totalScore = (
    relative_material_score
    + white_pawn_sum + white_bishop_sum + white_knight_sum
    + white_rook_sum + white_queen_sum + white_king_sum
    - black_pawn_sum - black_bishop_sum - black_knight_sum
    - black_rook_sum - black_queen_sum - black_king_sum
    )

    if board.turn == chess.BLACK:
        totalScore = -totalScore
    return totalScore
    

def min_max(board, depth, startTime, alpha, beta, is_maximizing, allowed_time):
    currTime = time.time()
    timeDiff = currTime-startTime
    if depth<=0 or board.is_game_over() or timeDiff>=allowed_time:
        return evaluate(board)
    if is_maximizing:
        bestMove = -math.inf
        for move in board.legal_moves:
            board.push(move)
            val = min_max(board, depth-1, startTime, alpha, beta, not is_maximizing, allowed_time)
            board.pop()
            bestMove = max(bestMove, val)
            alpha = max(alpha, bestMove)
            if beta<=alpha:
                break
        return bestMove
    else:
        bestMove = math.inf
        for move in board.legal_moves:
            board.push(move)
            val = min_max(board, depth-1, startTime, alpha, beta, not is_maximizing, allowed_time)
            board.pop()
            bestMove = min(bestMove, val)
            beta = min(beta, bestMove)
            if beta<=alpha:
                break
        return bestMove

def find_best_move(board, is_white, depth=5, allowed_time=15000000):
    bestMove = -math.inf if is_white else math.inf
    returnMove = None
    for move in board.legal_moves:
        board.push(move)
        val = min_max(board, depth-1, time.time(), -math.inf, math.inf, not is_white, allowed_time)
        board.pop()
        if ( is_white and val>bestMove ) or ( not is_white and val<bestMove ):
            bestMove = val
            returnMove = move
    return returnMove
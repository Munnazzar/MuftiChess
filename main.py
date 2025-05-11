import chess
import time
from evaluator import *

def main():
    firstTurn = int(input("1: You go First\n2: Mufti goes First\n"))
    bishopOrKnight = int(input("1:Bishop\n2:Knight\n"))
    if firstTurn not in (1, 2):
        exit()
    elif bishopOrKnight not in (1, 2):
        exit()
    if bishopOrKnight == 1:
        board = chess.Board("rbqqkqqr/pppppppp/8/8/8/8/PPPPPPPP/RBQQKQQR w KQkq - 0 1")
    else:
        board = chess.Board("rnqqkqqr/pppppppp/8/8/8/8/PPPPPPPP/RNQQKQQR w KQkq - 0 1")
            
    is_white = True
    print()
    print(board)
    print()
    if firstTurn==1:
        while not board.is_game_over():
            userMove = None
            print("Your Move: ")
            while True:
                try:
                    userMove = board.parse_san(input())
                except ValueError:
                    print("Sneaky Boi, this not a valid move")
                    continue
                except:
                    print("SOMETHING WENT WRONG AGAIN MAN!!!")
                    exit()
                break
            board.push(userMove)
            print()
            print(board)
            print()
            muftiMove = find_best_move(board, not is_white, 5)
            board.push(muftiMove)
            print(f"Mufti played: {muftiMove}")
            print()
            print(board)
            print()
    else:
        while not board.is_game_over():
            muftiMove = find_best_move(board, is_white, 5)
            board.push(muftiMove)
            print()
            print("Mufti Played: ")
            print()
            print(board)
            print()
            print("Your Move: ")
            while True:
                try:
                    userMove = board.parse_san(input())
                except ValueError:
                    print("Sneaky Boi, this not a valid move")
                    continue
                except:
                    print("SOMETHING WENT WRONG AGAIN MAN!!!")
                    exit()
                break
            board.push(userMove)
            print()
            print(board)
            print()
    exit()


main()
import sys, chess, time
from evaluator import find_best_move

def safe_print(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

class MuftiUCIEngine:
    def __init__(self):
        self.board = chess.Board()

    def uci_loop(self):
        while True:
            try:
                line = input().strip()
            except EOFError:
                break

            if not line:
                continue

            if line == "uci":
                safe_print("id name MuftiEngine")
                safe_print("id author You")
                safe_print("uciok")
            elif line == "isready":
                safe_print("readyok")
            elif line.startswith("position"):
                self.set_position(line)
            elif line.startswith("go"):
                self.go(line)
            elif line == "ucinewgame":
                self.board.reset()
            elif line == "quit":
                break

    def set_position(self, line):
        parts = line.split()
        if "startpos" in parts:
            self.board.reset()
            if "moves" in parts:
                for mv in parts[parts.index("moves")+1:]:
                    self.board.push_uci(mv)
        elif "fen" in parts:
            idx = parts.index("fen") + 1
            fen = " ".join(parts[idx:idx+6])
            self.board.set_fen(fen)
            if "moves" in parts:
                for mv in parts[parts.index("moves")+1:]:
                    self.board.push_uci(mv)

    def go(self, line):
        try:
            cmds = line.split()
            movetime = wtime = btime = None
            i = 1
            while i < len(cmds):
                if cmds[i] == "movetime":
                    movetime = int(cmds[i+1])
                elif cmds[i] == "wtime":
                    wtime = int(cmds[i+1])
                elif cmds[i] == "btime":
                    btime = int(cmds[i+1])
                i += 2

            if movetime is not None:
                allowed_ms = movetime
            elif self.board.turn == chess.WHITE and wtime is not None:
                allowed_ms = wtime // 50
            elif self.board.turn == chess.BLACK and btime is not None:
                allowed_ms = btime // 50
            else:
                allowed_ms = 1000

            best_move = find_best_move(
                self.board,
                depth=6,
                allowed_time_ms=allowed_ms
            )

            if best_move is None:
                safe_print("bestmove 0000")
            else:
                self.board.push(best_move)
                safe_print(f"bestmove {best_move.uci()}")

        except Exception as e:
            safe_print(f"# engine error in go(): {e}")
            safe_print("bestmove 0000")


if __name__ == "__main__":
    MuftiUCIEngine().uci_loop()

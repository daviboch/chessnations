# main.py
import cProfile
import pstats
from chessapp import ChessApp
import tkinter as tk

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

    profiler.disable()
    stats = pstats.Stats(profiler).strip_dirs().sort_stats('cumulative')
    stats.print_stats(600)


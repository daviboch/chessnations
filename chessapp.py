# chessapp.py

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import os, random, time

try:
    LANCZOS_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS_FILTER = Image.LANCZOS

from customboard import CustomBoard

from evaluation import (
    compute_material_display,
    deterministic_evaluation,
    evaluation_breakdown
)
from ai_engine import (
    iterative_deepening_decision,
    evaluation_breakdown,
    TRANSPOSITION_TABLE
)
from piece_movement.piece_movement_common import (
    BOARD_SIZE,
    EMPTY,
    WHITE_PAWN, BLACK_PAWN,
    WHITE_TOTEM, BLACK_TOTEM,
    WHITE_BISON, BLACK_BISON,
    WHITE_SHAMAN, BLACK_SHAMAN,
    WHITE_ROOK, BLACK_ROOK,
    WHITE_KNIGHT, BLACK_KNIGHT,
    WHITE_BISHOP, BLACK_BISHOP,
    WHITE_QUEEN, BLACK_QUEEN,
    WHITE_KING, BLACK_KING,
    is_white_piece, is_black_piece,
    PIECE_NAME_MAP
)

def convert_move_to_algebraic_detailed(move: tuple, board_before: CustomBoard) -> str:
    (fr, fc, tr, tc) = move
    mover = board_before.board[fr][fc]
    start = f"{chr(ord('a') + fc)}{8 - fr}"
    dest = f"{chr(ord('a') + tc)}{8 - tr}"
    piece_str = PIECE_NAME_MAP.get(mover, str(mover))
    move_str = f"{piece_str} from {start} to {dest}"
    return move_str

def convert_move_to_algebraic(raw_move: str) -> str:
    parts = raw_move.split('@')
    if len(parts) < 2:
        return raw_move
    piece_part = parts[0]  # es. "17"
    coords_part = '@'.join(parts[1:])
    arrow_split = coords_part.split('->')
    if len(arrow_split) != 2:
        return raw_move
    
    start_str = arrow_split[0].strip().strip('()')  # "7,4"
    end_str   = arrow_split[1].strip().strip('()')  # "7,6"

    try:
        # Convertiamo piece_part in int e usiamo PIECE_NAME_MAP
        piece_id = int(piece_part)
        piece_name = PIECE_NAME_MAP.get(piece_id, str(piece_id))
    except:
        # Se c'è un problema, lasciamo la stringa così com'è
        piece_name = piece_part

    try:
        fr, fc = map(int, start_str.split(','))
        tr, tc = map(int, end_str.split(','))
    except:
        return raw_move

    start_file = chr(ord('a') + fc)
    start_rank = str(8 - fr)
    end_file   = chr(ord('a') + tc)
    end_rank   = str(8 - tr)

    return f"{piece_name} from {start_file}{start_rank} to {end_file}{end_rank}"

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess (Enum+2D) - simplified nativi")
        self.margin = 20
        self.cell_size = 60
        canvas_width = 8*self.cell_size + 2*self.margin
        canvas_height= 8*self.cell_size + 2*self.margin
        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="#d8e2dc")
        self.canvas.grid(row=0, column=0, rowspan=8)

        self.status_label = tk.Label(self.root, text="Mode not selected", font=("Helvetica",16,"bold"), fg="#003049")
        self.status_label.grid(row=8, column=0, pady=5)

        self.material_label = tk.Label(self.root, text="", font=("Helvetica",12), fg="black")
        self.material_label.grid(row=9, column=0, sticky="w", padx=10)

        self.evaluation_label = tk.Label(self.root, text="", font=("Helvetica",12), fg="black")
        self.evaluation_label.grid(row=10, column=0, sticky="w", padx=10)

        self.moves_listbox = tk.Listbox(self.root, width=30, height=25)
        self.moves_listbox.grid(row=0, column=1, rowspan=8, padx=10)

        self.newgame_button = tk.Button(self.root, text="New Game", command=self.new_game)
        self.newgame_button.grid(row=8, column=1, pady=2)

        self.export_button = tk.Button(self.root, text="Export (fake PGN)", command=self.export_pgn)
        self.export_button.grid(row=9, column=1, pady=2)

        self.savepos_button = tk.Button(self.root, text="Save Position", command=self.save_position)
        self.savepos_button.grid(row=10, column=1, pady=2)

        self.loadpos_button = tk.Button(self.root, text="Load Position", command=self.load_position)
        self.loadpos_button.grid(row=11, column=1, pady=2)

        # Scelta fazioni iniziali
        white_faction_choice = simpledialog.askinteger("Fazione per i Bianchi",
            "Scegli la fazione per i Bianchi:\n1) Classici\n2) Nativi",
            minvalue=1, maxvalue=2)
        white_faction = "classici" if white_faction_choice==1 else "nativi"

        black_faction_choice = simpledialog.askinteger("Fazione per i Neri",
            "Scegli la fazione per i Neri:\n1) Classici\n2) Nativi",
            minvalue=1, maxvalue=2)
        black_faction = "classici" if black_faction_choice==1 else "nativi"

        self.game_board = CustomBoard(
            white_faction=white_faction,
            black_faction=black_faction
        )

        self.selected_square = None
        self.piece_images = {}
        self.load_piece_images()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

        random.seed(time.time())
        self.game_board.game_noise_seed = random.randint(0, 1000000)
        print("Prima partita, seed =", self.game_board.game_noise_seed)

        # Scelta modalità
        self.mode = simpledialog.askinteger(
            "Modalità di gioco",
            "Scegli modalità:\n1) Player vs Player\n2) Player (White) vs AI (Black)\n3) AI vs AI",
            minvalue=1, maxvalue=3
        )
        if self.mode == 1:
            self.status_label.config(text="Player vs Player")
        elif self.mode == 2:
            self.status_label.config(text="Player (White) vs AI (Black)")
            if not self.game_board.turn_white:
                self.root.after(200, self.ai_move)
        elif self.mode == 3:
            self.status_label.config(text="AI vs AI")
            self.root.after(200, self.ai_move)

    def update_evaluation(self):
        w_disp, b_disp = compute_material_display(self.game_board)
        diff_disp = w_disp - b_disp
        material_text = f"Material (excl. King): White {w_disp} - Black {b_disp} (diff: {diff_disp})"
        det_eval = deterministic_evaluation(self.game_board)
        eval_text = f"Evaluation (deterministic): {det_eval:.2f}"
        self.material_label.config(text=material_text)
        self.evaluation_label.config(text=eval_text)

    def new_game(self):
        from ai_engine import TRANSPOSITION_TABLE
        TRANSPOSITION_TABLE.clear()

        white_faction_choice = simpledialog.askinteger("Fazione per i Bianchi",
            "Scegli la fazione per i Bianchi:\n1) Classici\n2) Nativi",
            minvalue=1, maxvalue=2)
        white_faction = "classici" if white_faction_choice==1 else "nativi"

        black_faction_choice = simpledialog.askinteger("Fazione per i Neri",
            "Scegli la fazione per i Neri:\n1) Classici\n2) Nativi",
            minvalue=1, maxvalue=2)
        black_faction = "classici" if black_faction_choice==1 else "nativi"

        self.game_board = CustomBoard(white_faction=white_faction, black_faction=black_faction)
        random.seed(time.time())
        self.game_board.game_noise_seed = random.randint(0,1000000)
        print("Nuova partita, seed =", self.game_board.game_noise_seed)

        self.selected_square = None
        self.draw_board()
        self.update_status()
        self.update_moves_list()

        self.mode = simpledialog.askinteger("Modalità di gioco",
            "Scegli modalità:\n1) Player vs Player\n2) Player (White) vs AI (Black)\n3) AI vs AI",
            minvalue=1, maxvalue=3)
        if self.mode == 1:
            self.status_label.config(text="Player vs Player")
        elif self.mode == 2:
            self.status_label.config(text="Player (White) vs AI (Black)")
            if not self.game_board.turn_white:
                self.root.after(200, self.ai_move)
        elif self.mode == 3:
            self.status_label.config(text="AI vs AI")
            self.root.after(200, self.ai_move)

    def load_piece_images(self):
        piece_filenames = {
            WHITE_PAWN:   "wpawn.png",
            WHITE_TOTEM:  "wtotem.png",
            WHITE_BISON:  "wbison.png",
            WHITE_SHAMAN: "wshaman.png",
            WHITE_ROOK:   "wrook.png",
            WHITE_KNIGHT: "wknight.png",
            WHITE_BISHOP: "wbishop.png",
            WHITE_QUEEN:  "wqueen.png",
            WHITE_KING:   "wking.png",
            BLACK_PAWN:   "bpawn.png",
            BLACK_ROOK:   "brook.png",
            BLACK_KNIGHT: "bknight.png",
            BLACK_BISHOP: "bbishop.png",
            BLACK_QUEEN:  "bqueen.png",
            BLACK_KING:   "bking.png",
            BLACK_TOTEM:  "btotem.png",
            BLACK_BISON:  "bbison.png",
            BLACK_SHAMAN: "bshaman.png",
        }
        bg_light = (240,217,181,255)
        bg_dark  = (181,136,99,255)
        for p, filename in piece_filenames.items():
            try:
                img_path = f"images/{filename}"
                from PIL import Image
                base_img = Image.open(img_path).convert("RGBA")
                light_bg = Image.new("RGBA", base_img.size, bg_light)
                dark_bg  = Image.new("RGBA", base_img.size, bg_dark)
                light_comp = Image.alpha_composite(light_bg, base_img).resize((self.cell_size, self.cell_size), LANCZOS_FILTER)
                dark_comp  = Image.alpha_composite(dark_bg, base_img).resize((self.cell_size, self.cell_size), LANCZOS_FILTER)

                from PIL import ImageTk
                self.piece_images.setdefault(p, {})
                self.piece_images[p]["light"] = ImageTk.PhotoImage(light_comp)
                self.piece_images[p]["dark"]  = ImageTk.PhotoImage(dark_comp)
            except Exception as e:
                print(f"Could not load piece {p} => {filename}: {e}")

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#f0d9b5", "#b58863"]
        offset = self.margin
        for r in range(8):
            for c in range(8):
                color = colors[(r+c)%2]
                x1 = offset + c*self.cell_size
                y1 = offset + r*self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1,y1,x2,y2, fill=color, outline="")

        for r in range(8):
            for c in range(8):
                piece = self.game_board.board[r][c]
                if piece != EMPTY:
                    imgs = self.piece_images.get(piece, {})
                    img = imgs.get("light") if ((r+c)%2==0) else imgs.get("dark")
                    if img is not None:
                        x1 = offset + c*self.cell_size
                        y1 = offset + r*self.cell_size
                        self.canvas.create_image(x1,y1, image=img, anchor="nw")

        font_coords = ("Helvetica",10,"bold")
        for c in range(8):
            file_label = chr(ord('a') + c)
            x = offset + c*self.cell_size + self.cell_size/2
            y = offset + 8*self.cell_size + 10
            self.canvas.create_text(x, y, text=file_label, font=font_coords)
        for r in range(8):
            rank_label = 8 - r
            x = offset - 10
            y = offset + r*self.cell_size + self.cell_size/2
            self.canvas.create_text(x, y, text=str(rank_label), font=font_coords)

    def highlight_legal_moves(self, fr, fc):
        moves = self.game_board.get_legal_moves_for_square(fr, fc)
        offset = self.margin
        for (tr, tc) in moves:
            x1 = offset + tc*self.cell_size
            y1 = offset + tr*self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1,y1,x2,y2, outline="green", width=2)

    def on_click(self, event):
        if self.game_board.is_game_over():
            return
        col = (event.x - self.margin) // self.cell_size
        row = (event.y - self.margin) // self.cell_size
        if row<0 or row>=8 or col<0 or col>=8:
            return

        if self.selected_square is None:
            piece = self.game_board.board[row][col]
            if piece != EMPTY and self.game_board.can_move_piece(piece):
                self.selected_square = (row, col)
                self.highlight_legal_moves(row, col)
        else:
            fr, fc = self.selected_square
            if (fr, fc) == (row, col):
                self.selected_square = None
                self.draw_board()
                return
            mover = self.game_board.board[fr][fc]
            ok = self.game_board.make_move(fr, fc, row, col)
            self.selected_square = None
            self.draw_board()
            if ok:
                move_str = f"{mover}@({fr},{fc})->({row},{col})"
                self.game_board.move_history.append(move_str)
                self.moves_listbox.insert(tk.END, convert_move_to_algebraic(move_str))
                self.update_evaluation()
                self.update_status()
                if self.game_board.is_game_over():
                    messagebox.showinfo("Game Over", f"Winner: {self.game_board.winner}")
                else:
                    if self.mode==2 and not self.game_board.turn_white:
                        self.root.after(200, self.ai_move)
                    elif self.mode==3:
                        self.root.after(200, self.ai_move)

    def update_status(self):
        if self.game_board.is_game_over():
            self.status_label.config(text=f"Game Over. Winner: {self.game_board.winner}")
        else:
            turn_str = "White" if self.game_board.turn_white else "Black"
            self.status_label.config(text=f"Turn: {turn_str}")

    def update_moves_list(self):
        self.moves_listbox.delete(0, tk.END)
        for mv in self.game_board.move_history:
            self.moves_listbox.insert(tk.END, convert_move_to_algebraic(mv))

    def export_pgn(self):
        lines = []
        for idx, mv in enumerate(self.game_board.move_history):
            algeb = convert_move_to_algebraic(mv)
            if idx%2==0:
                move_num = (idx//2)+1
                lines.append(f"{move_num}. {algeb}")
            else:
                lines[-1] += f" {algeb}"
        pgn_text = "\n".join(lines)
        print("Fake PGN:\n", pgn_text)

    def save_position(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if not filename:
            return
        try:
            with open(filename,"w") as f:
                # Scrivi la board (8 righe)
                for r in range(8):
                    row_pieces = [str(self.game_board.board[r][c]) for c in range(8)]
                    f.write(",".join(row_pieces)+"\n")
                # game_over, winner, turn
                f.write("GAME_OVER:\n")
                f.write(f"{self.game_board.game_over}\n")
                winner_str = self.game_board.winner if self.game_board.winner else "None"
                f.write(f"WINNER:{winner_str}\n")
                turn_str = "W" if self.game_board.turn_white else "B"
                f.write(f"Turn:{turn_str}\n")

                # Salva i flag di arrocco
                f.write(f"WHITE_KING_MOVED:{self.game_board.white_king_moved}\n")
                f.write(f"WHITE_LEFT_ROOK_MOVED:{self.game_board.white_left_rook_moved}\n")
                f.write(f"WHITE_RIGHT_ROOK_MOVED:{self.game_board.white_right_rook_moved}\n")
                f.write(f"BLACK_KING_MOVED:{self.game_board.black_king_moved}\n")
                f.write(f"BLACK_LEFT_ROOK_MOVED:{self.game_board.black_left_rook_moved}\n")
                f.write(f"BLACK_RIGHT_ROOK_MOVED:{self.game_board.black_right_rook_moved}\n")

                # Salva i poteri ereditati
                if self.game_board.white_totem_inherited is None:
                    f.write("WHITE_TOTEM_INHERITED:NONE\n")
                else:
                    f.write(f"WHITE_TOTEM_INHERITED:{self.game_board.white_totem_inherited}\n")

                if self.game_board.black_totem_inherited is None:
                    f.write("BLACK_TOTEM_INHERITED:NONE\n")
                else:
                    f.write(f"BLACK_TOTEM_INHERITED:{self.game_board.black_totem_inherited}\n")

                # Move history
                f.write("MOVE_HISTORY:\n")
                for move_item in self.game_board.move_history:
                    f.write(move_item+"\n")

            messagebox.showinfo("Save","Posizione salvata con successo!")
        except Exception as e:
            messagebox.showerror("Error", f"Errore durante il salvataggio:\n{e}")

    def load_position(self):
        filename = filedialog.askopenfilename()
        if not filename:
            return
        try:
            with open(filename,"r") as f:
                lines = [line.rstrip("\n") for line in f]
            if len(lines)<8:
                messagebox.showerror("Error","File non valido o troppo corto.")
                return
            new_board = CustomBoard()
            random.seed(time.time())
            new_board.game_noise_seed = random.randint(0, 1000000)
            print("Partita caricata, nuovo seed =", new_board.game_noise_seed)
            new_board.move_history.clear()

            # --- Caricamento scacchiera (8 righe) ---
            for r in range(8):
                row_line = lines[r].strip()
                piece_names = row_line.split(",")
                if len(piece_names)!=8:
                    messagebox.showerror("Error", f"Riga {r+1} non valida (8 pezzi).")
                    return
                for c in range(8):
                    new_board.board[r][c] = int(piece_names[c])

            idx = 8
            # Legge GAME_OVER:
            if idx>=len(lines) or not lines[idx].startswith("GAME_OVER:"):
                messagebox.showerror("Error","Formato file non corretto (GAME_OVER).")
                return
            idx+=1
            val_go = lines[idx].strip() if idx<len(lines) else ""
            new_board.game_over = (val_go=="True")
            idx+=1

            # WINNER:
            if idx>=len(lines) or not lines[idx].startswith("WINNER:"):
                messagebox.showerror("Error","Formato file non corretto (WINNER).")
                return
            winner_val = lines[idx].split(":",1)[1].strip()
            if winner_val=="None":
                new_board.winner = None
            else:
                new_board.winner = winner_val
            idx+=1

            # Turn:
            if idx>=len(lines) or not lines[idx].startswith("Turn:"):
                messagebox.showerror("Error","Formato file non corretto (Turn).")
                return
            turn_str = lines[idx].split(":",1)[1].strip()
            new_board.turn_white = (turn_str=="W")
            idx+=1

            # Flag arrocco:
            def parse_bool(line_str, prefix):
                if not line_str.startswith(prefix):
                    messagebox.showerror("Error", f"Formato file non corretto ({prefix}).")
                    return None
                val = line_str.split(":",1)[1].strip()
                return (val=="True")

            # WHITE_KING_MOVED
            if idx<len(lines):
                wkm = parse_bool(lines[idx], "WHITE_KING_MOVED")
                if wkm is None: return
                new_board.white_king_moved = wkm
                idx+=1

            # WHITE_LEFT_ROOK_MOVED
            if idx<len(lines):
                wlrm = parse_bool(lines[idx], "WHITE_LEFT_ROOK_MOVED")
                if wlrm is None: return
                new_board.white_left_rook_moved = wlrm
                idx+=1

            # WHITE_RIGHT_ROOK_MOVED
            if idx<len(lines):
                wrrm = parse_bool(lines[idx], "WHITE_RIGHT_ROOK_MOVED")
                if wrrm is None: return
                new_board.white_right_rook_moved = wrrm
                idx+=1

            # BLACK_KING_MOVED
            if idx<len(lines):
                bkm = parse_bool(lines[idx], "BLACK_KING_MOVED")
                if bkm is None: return
                new_board.black_king_moved = bkm
                idx+=1

            # BLACK_LEFT_ROOK_MOVED
            if idx<len(lines):
                blrm = parse_bool(lines[idx], "BLACK_LEFT_ROOK_MOVED")
                if blrm is None: return
                new_board.black_left_rook_moved = blrm
                idx+=1

            # BLACK_RIGHT_ROOK_MOVED
            if idx<len(lines):
                brrm = parse_bool(lines[idx], "BLACK_RIGHT_ROOK_MOVED")
                if brrm is None: return
                new_board.black_right_rook_moved = brrm
                idx+=1

            # WHITE_TOTEM_INHERITED
            if idx<len(lines) and lines[idx].startswith("WHITE_TOTEM_INHERITED:"):
                wti_str = lines[idx].split(":",1)[1].strip()
                if wti_str == "NONE":
                    new_board.white_totem_inherited = None
                else:
                    new_board.white_totem_inherited = wti_str
                idx+=1

            # BLACK_TOTEM_INHERITED
            if idx<len(lines) and lines[idx].startswith("BLACK_TOTEM_INHERITED:"):
                bti_str = lines[idx].split(":",1)[1].strip()
                if bti_str == "NONE":
                    new_board.black_totem_inherited = None
                else:
                    new_board.black_totem_inherited = bti_str
                idx+=1

            # MOVE_HISTORY:
            if idx<len(lines) and lines[idx].strip()=="MOVE_HISTORY:":
                idx+=1
                while idx<len(lines):
                    mh_line = lines[idx].strip()
                    if mh_line:
                        new_board.move_history.append(mh_line)
                    idx+=1

            self.game_board = new_board
            self.selected_square = None
            self.draw_board()
            self.update_evaluation()
            self.update_status()
            self.update_moves_list()
            messagebox.showinfo("Load","Posizione caricata correttamente!")
        except Exception as e:
            messagebox.showerror("Error",f"Errore caricamento:\n{e}")

    def ai_move(self):
        if self.game_board.is_game_over():
            return
        from ai_engine import iterative_deepening_decision, evaluation_breakdown
        if self.mode==2:
            if self.game_board.turn_white:
                return
            mv = iterative_deepening_decision(self.game_board, max_depth=4, max_time=10)
            if mv is None:
                return
            (fr, fc, tr, tc) = mv
            mover = self.game_board.board[fr][fc]
            ok = self.game_board.make_move(fr, fc, tr, tc)
            if ok:
                move_str = f"{mover}@({fr},{fc})->({tr},{tc})"
                self.game_board.move_history.append(move_str)
                self.moves_listbox.insert(tk.END, convert_move_to_algebraic(move_str))
                self.update_evaluation()
                self.draw_board()
                self.update_status()
                print("-----")
                print("New evaluation after black move:")
                print(evaluation_breakdown(self.game_board))
                print()
                if self.game_board.is_game_over():
                    messagebox.showinfo("Game Over", f"Winner: {self.game_board.winner}")
        elif self.mode==3:
            if self.game_board.is_game_over():
                return
            depth=4
            mv = iterative_deepening_decision(self.game_board, max_depth=depth, max_time=10)
            if mv is None:
                return
            (fr, fc, tr, tc) = mv
            mover = self.game_board.board[fr][fc]
            ok = self.game_board.make_move(fr, fc, tr, tc)
            if ok:
                move_str = f"{mover}@({fr},{fc})->({tr},{tc})"
                self.game_board.move_history.append(move_str)
                self.moves_listbox.insert(tk.END, convert_move_to_algebraic(move_str))
                self.update_evaluation()
                self.draw_board()
                self.update_status()
                print("-----")
                if self.game_board.turn_white:
                    print("New evaluation after move of black:")
                else:
                    print("New evaluation after move of white:")
                print(evaluation_breakdown(self.game_board))
                print()
                if not self.game_board.is_game_over():
                    self.root.after(200, self.ai_move)

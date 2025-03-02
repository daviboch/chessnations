import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os, random, time
from evaluation import clear_noise_cache


try:
    LANCZOS_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS_FILTER = Image.LANCZOS

from customboard import CustomBoard

from evaluation import (
    compute_material_display,
    deterministic_evaluation
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

###############################################################################
# Configurazioni grafiche
###############################################################################
CELL_SIZE = 60
MARGIN = 20

# Colore della casella di partenza dell'ultima mossa
HIGHLIGHT_COLOR = "#f7f79a"

# Colori base della scacchiera
LIGHT_COLOR = "#f0d9b5"
DARK_COLOR  = "#b58863"

# Fattore di ingrandimento pezzo sulla casella di arrivo
SCALE_FACTOR = 1.18

###############################################################################
# Funzioni di conversione mosse
###############################################################################
def convert_move_to_algebraic(raw_move: str) -> str:
    """
    Converte una stringa di mossa nel formato "mover@(fr,fc)->(tr,tc)" 
    in un formato algebrico "PieceName from e2 to e4", sfruttando PIECE_NAME_MAP.
    """
    parts = raw_move.split('@')
    if len(parts) < 2:
        return raw_move
    piece_part = parts[0]
    coords_part = '@'.join(parts[1:])
    arrow_split = coords_part.split('->')
    if len(arrow_split) != 2:
        return raw_move
    
    start_str = arrow_split[0].strip().strip('()')
    end_str   = arrow_split[1].strip().strip('()')

    try:
        piece_id = int(piece_part)
        piece_name = PIECE_NAME_MAP.get(piece_id, str(piece_id))
    except ValueError:
        piece_name = piece_part

    try:
        fr, fc = map(int, start_str.split(','))
        tr, tc = map(int, end_str.split(','))
    except ValueError:
        return raw_move

    start_file = chr(ord('a') + fc)
    start_rank = str(8 - fr)
    end_file   = chr(ord('a') + tc)
    end_rank   = str(8 - tr)

    return f"{piece_name} from {start_file}{start_rank} to {end_file}{end_rank}"

def convert_move_to_algebraic_detailed(move: tuple, board_before: CustomBoard) -> str:
    """
    Variante 'dettagliata': prende una tupla (fr, fc, tr, tc) e un CustomBoard 
    per ricavare il nome del pezzo, e restituisce ad es. 'WHITE_KNIGHT from e2 to c3'.
    """
    (fr, fc, tr, tc) = move
    mover = board_before.board[fr][fc]
    start = f"{chr(ord('a') + fc)}{8 - fr}"
    dest = f"{chr(ord('a') + tc)}{8 - tr}"
    piece_str = PIECE_NAME_MAP.get(mover, str(mover))
    return f"{piece_str} from {start} to {dest}"

def ask_option_dialog(parent, title, prompt, options):
    """
    Mostra una finestra di dialogo con:
      - un messaggio `prompt`
      - un menù a tendina con la lista `options`
      - un pulsante OK
    Restituisce la stringa selezionata.
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)

    dialog.transient(parent)            
    dialog.grab_set()                  
    dialog.attributes("-topmost", True)
    dialog.lift()                      

    var_choice = tk.StringVar(dialog)
    var_choice.set(options[0])  

    label = tk.Label(dialog, text=prompt, font=("Helvetica", 14))
    label.pack(padx=10, pady=10)

    menu = tk.OptionMenu(dialog, var_choice, *options)
    menu.config(font=("Helvetica", 14))
    menu.pack(padx=10, pady=5)

    def on_ok():
        dialog.destroy()

    btn_ok = tk.Button(dialog, text="OK", font=("Helvetica", 14), command=on_ok)
    btn_ok.pack(pady=10)

    dialog.focus_force()
    parent.wait_window(dialog)

    return var_choice.get()

###############################################################################
# Classe GUI
###############################################################################
class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess (Enum+2D) - Transparent Pieces + bigger last move")

        canvas_width = 8 * CELL_SIZE + 2*MARGIN
        canvas_height= 8 * CELL_SIZE + 2*MARGIN

        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="#d8e2dc")
        self.canvas.grid(row=0, column=0, rowspan=8)

        self.status_label = tk.Label(self.root, text="Mode not selected", font=("Helvetica",20,"bold"), fg="#003049")
        self.status_label.grid(row=8, column=0, pady=5)

        self.material_label = tk.Label(self.root, text="", font=("Helvetica",14), fg="black")
        self.material_label.grid(row=9, column=0, sticky="w", padx=10)

        self.evaluation_label = tk.Label(self.root, text="", font=("Helvetica",14), fg="black")
        self.evaluation_label.grid(row=10, column=0, sticky="w", padx=10)

        self.moves_listbox = tk.Listbox(self.root, width=30, height=30)
        self.moves_listbox.grid(row=0, column=1, rowspan=8, padx=10)

        self.newgame_button = tk.Button(self.root, text="New Game", command=self.new_game)
        self.newgame_button.grid(row=8, column=1, pady=2)

        self.export_button = tk.Button(self.root, text="Export (fake PGN)", command=self.export_pgn)
        self.export_button.grid(row=9, column=1, pady=2)

        self.savepos_button = tk.Button(self.root, text="Save Position", command=self.save_position)
        self.savepos_button.grid(row=10, column=1, pady=2)

        self.loadpos_button = tk.Button(self.root, text="Load Position", command=self.load_position)
        self.loadpos_button.grid(row=11, column=1, pady=2)

        self.last_move_from = None
        self.last_move_to = None
        self.selected_square = None
        self.game_board = None
        self.mode = None

        # Dizionari di immagini (pezzi in dimensioni normale e ingrandita)
        self.piece_images_normal = {}
        self.piece_images_enlarged = {}

        self.setup_new_game()

    def setup_new_game(self):
        TRANSPOSITION_TABLE.clear()

        faction_bianchi = ask_option_dialog(
            self.root,
            "Fazione Bianchi",
            "Scegli la fazione per i Bianchi:",
            ["Classici", "Nativi"]
        )
        if faction_bianchi == "Classici":
            white_faction = "classici"
        else:
            white_faction = "nativi"

        faction_neri = ask_option_dialog(
            self.root,
            "Fazione Neri",
            "Scegli la fazione per i Neri:",
            ["Classici", "Nativi"]
        )
        if faction_neri == "Classici":
            black_faction = "classici"
        else:
            black_faction = "nativi"

        self.game_board = CustomBoard(white_faction=white_faction, black_faction=black_faction)
        random.seed(time.time())
        self.game_board.game_noise_seed = random.randint(0, 1000000)
        print("Nuova partita, seed =", self.game_board.game_noise_seed)

        self.selected_square = None
        self.last_move_from = None
        self.last_move_to = None

        mode_str = ask_option_dialog(
            self.root,
            "Modalità di gioco",
            "Scegli la modalità:",
            ["Player vs Player", "Player (White) vs AI (Black)", "AI vs AI"]
        )
        if mode_str == "Player vs Player":
            self.mode = 1
            self.status_label.config(text="Player vs Player")
        elif mode_str == "Player (White) vs AI (Black)":
            self.mode = 2
            self.status_label.config(text="Player (White) vs AI (Black)")
        else:
            self.mode = 3
            self.status_label.config(text="AI vs AI")

        self.load_piece_images()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

        self.moves_listbox.delete(0, tk.END)
        self.update_evaluation()

        # Avvio dell'AI se necessario
        if self.mode == 2 and not self.game_board.turn_white:
            self.root.after(200, self.ai_move)
        elif self.mode == 3:
            self.root.after(200, self.ai_move)

    def new_game(self):
        self.setup_new_game()

    def load_piece_images(self):
        """
        Carica le immagini dei pezzi in due dimensioni (normale e ingrandita),
        mantenendo la trasparenza attorno al pezzo.
        """
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

        enlarged_size = int(CELL_SIZE * SCALE_FACTOR)

        for p, filename in piece_filenames.items():
            try:
                img_path = f"images/{filename}"
                base_img = Image.open(img_path).convert("RGBA")
                normal_img = base_img.resize((CELL_SIZE, CELL_SIZE), LANCZOS_FILTER)
                enlarged_img = base_img.resize((enlarged_size, enlarged_size), LANCZOS_FILTER)

                self.piece_images_normal[p] = ImageTk.PhotoImage(normal_img)
                self.piece_images_enlarged[p] = ImageTk.PhotoImage(enlarged_img)

            except Exception as e:
                print(f"Could not load piece {p} => {filename}: {e}")

    def draw_board(self):
        """
        Disegna la scacchiera e i pezzi:
         - Casella di partenza dell'ultima mossa in giallo
         - Casella di arrivo con pezzo ingrandito
        """
        self.canvas.delete("all")

        # Disegno celle
        for r in range(8):
            for c in range(8):
                if (r, c) == self.last_move_from:
                    color = HIGHLIGHT_COLOR
                else:
                    color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR

                x1 = MARGIN + c*CELL_SIZE
                y1 = MARGIN + r*CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # Disegno pezzi
        for r in range(8):
            for c in range(8):
                piece = self.game_board.board[r][c]
                if piece == EMPTY:
                    continue

                if (r, c) == self.last_move_to:
                    # Usa versione ingrandita
                    img = self.piece_images_enlarged.get(piece)
                    if img:
                        enlarged_size = int(CELL_SIZE * SCALE_FACTOR)
                        offset_x = MARGIN + c*CELL_SIZE - (enlarged_size - CELL_SIZE)//2
                        offset_y = MARGIN + r*CELL_SIZE - (enlarged_size - CELL_SIZE)//2
                        self.canvas.create_image(offset_x, offset_y, image=img, anchor="nw")
                else:
                    img = self.piece_images_normal.get(piece)
                    if img:
                        x1 = MARGIN + c*CELL_SIZE
                        y1 = MARGIN + r*CELL_SIZE
                        self.canvas.create_image(x1, y1, image=img, anchor="nw")

        # Coordinate file/rank
        font_coords = ("Helvetica", 14, "bold")
        for cc in range(8):
            file_label = chr(ord('a') + cc)
            x = MARGIN + cc * CELL_SIZE + CELL_SIZE/2
            y = MARGIN + 8 * CELL_SIZE + 10
            self.canvas.create_text(x, y, text=file_label, font=font_coords)

        for rr in range(8):
            rank_label = 8 - rr
            x = MARGIN - 10
            y = MARGIN + rr * CELL_SIZE + CELL_SIZE/2
            self.canvas.create_text(x, y, text=str(rank_label), font=font_coords)

    def highlight_legal_moves(self, fr, fc):
        moves = self.game_board.get_legal_moves_for_square(fr, fc)
        for (tr, tc) in moves:
            x1 = MARGIN + tc*CELL_SIZE
            y1 = MARGIN + tr*CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=4)

    def on_click(self, event):
        if self.game_board.is_game_over():
            return

        col = (event.x - MARGIN) // CELL_SIZE
        row = (event.y - MARGIN) // CELL_SIZE
        if not (0 <= row < 8 and 0 <= col < 8):
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
            occupant = self.game_board.board[row][col]

            ok = self.game_board.make_move(fr, fc, row, col)
            self.selected_square = None
            if ok:
                # Salviamo l'ultima mossa
                move_str = f"{mover}@({fr},{fc})->({row},{col})"
                self.last_move_from = (fr, fc)
                self.last_move_to   = (row, col)

                # Inseriamo la mossa nella Listbox con il suo testo algebrico
                idx = self.moves_listbox.size()
                algebraic = convert_move_to_algebraic(move_str)
                self.moves_listbox.insert(tk.END, algebraic)

                # Di default, se è una cattura la segniamo in rosso
                color = "black"
                if occupant != EMPTY:
                    color = "red"

                # Se ORA il re di chi deve muovere è in check, coloriamo in verde
                if self.game_board.is_in_check(self.game_board.turn_white):
                    color = "green"
                    check_king_color = "White" if self.game_board.turn_white else "Black"
                    self.status_label.config(text=f"CHECK! {check_king_color} King is in check.")
                else:
                    self.update_status()

                # Applica il colore
                self.moves_listbox.itemconfig(idx, fg=color)

                self.draw_board()
                self.update_evaluation()

                if self.game_board.is_game_over():
                    messagebox.showinfo("Game Over", f"Winner: {self.game_board.winner}")
                else:
                    if self.mode == 2 and not self.game_board.turn_white:
                        self.root.after(200, self.ai_move)
                    elif self.mode == 3:
                        self.root.after(200, self.ai_move)
            else:
                self.draw_board()

    def ai_move(self):
        if self.game_board.is_game_over():
            return

        mv = iterative_deepening_decision(self.game_board, max_depth=4, max_time=60)
        if mv is None:
            return

        (fr, fc, tr, tc) = mv
        mover = self.game_board.board[fr][fc]
        occupant = self.game_board.board[tr][tc]

        ok = self.game_board.make_move(fr, fc, tr, tc)
        if ok:
            move_str = f"{mover}@({fr},{fc})->({tr},{tc})"
            self.last_move_from = (fr, fc)
            self.last_move_to   = (tr, tc)

            idx = self.moves_listbox.size()
            algebraic = convert_move_to_algebraic(move_str)
            self.moves_listbox.insert(tk.END, algebraic)

            # Di default, se è cattura => rosso
            color = "black"
            if occupant != EMPTY:
                color = "red"

            # Controlliamo lo scacco sul colore che ora deve muovere
            if self.game_board.is_in_check(self.game_board.turn_white):
                color = "green"
                check_king_color = "White" if self.game_board.turn_white else "Black"
                self.status_label.config(text=f"CHECK! {check_king_color} King is in check.")
            else:
                self.update_status()

            self.moves_listbox.itemconfig(idx, fg=color)

            self.game_board.move_history.append(move_str)
            self.update_evaluation()
            self.draw_board()
            print("-----")
            if self.game_board.turn_white:
                print("New evaluation after move of black:")
            else:
                print("New evaluation after move of white:")
            print(evaluation_breakdown(self.game_board))
            print()

            clear_noise_cache()

            if self.game_board.is_game_over():
                messagebox.showinfo("Game Over", f"Winner: {self.game_board.winner}")
            else:
                if self.mode == 3:
                    self.root.after(200, self.ai_move)

    def update_evaluation(self):
        w_disp, b_disp = compute_material_display(self.game_board)
        diff_disp = w_disp - b_disp
        material_text = f"Material (excl. King): White {w_disp} - Black {b_disp} (diff: {diff_disp})"
        det_eval = deterministic_evaluation(self.game_board)
        eval_text = f"Evaluation (deterministic): {det_eval:.2f}"
        self.material_label.config(text=material_text)
        self.evaluation_label.config(text=eval_text)

    def update_status(self):
        if self.game_board.is_game_over():
            self.status_label.config(text=f"Game Over. Winner: {self.game_board.winner}")
        else:
            turn_str = "White" if self.game_board.turn_white else "Black"
            self.status_label.config(text=f"Turn: {turn_str}")

    def export_pgn(self):
        lines = []
        for idx, mv in enumerate(self.game_board.move_history):
            algeb = convert_move_to_algebraic(mv)
            if idx % 2 == 0:
                move_num = (idx // 2) + 1
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
                for r in range(8):
                    row_pieces = [str(self.game_board.board[r][c]) for c in range(8)]
                    f.write(",".join(row_pieces)+"\n")
                f.write("GAME_OVER:\n")
                f.write(f"{self.game_board.game_over}\n")
                winner_str = self.game_board.winner if self.game_board.winner else "None"
                f.write(f"WINNER:{winner_str}\n")
                turn_str = "W" if self.game_board.turn_white else "B"
                f.write(f"Turn:{turn_str}\n")

                f.write(f"WHITE_KING_MOVED:{self.game_board.white_king_moved}\n")
                f.write(f"WHITE_LEFT_ROOK_MOVED:{self.game_board.white_left_rook_moved}\n")
                f.write(f"WHITE_RIGHT_ROOK_MOVED:{self.game_board.white_right_rook_moved}\n")
                f.write(f"BLACK_KING_MOVED:{self.game_board.black_king_moved}\n")
                f.write(f"BLACK_LEFT_ROOK_MOVED:{self.game_board.black_left_rook_moved}\n")
                f.write(f"BLACK_RIGHT_ROOK_MOVED:{self.game_board.black_right_rook_moved}\n")

                if self.game_board.white_totem_inherited is None:
                    f.write("WHITE_TOTEM_INHERITED:NONE\n")
                else:
                    f.write(f"WHITE_TOTEM_INHERITED:{self.game_board.white_totem_inherited}\n")

                if self.game_board.black_totem_inherited is None:
                    f.write("BLACK_TOTEM_INHERITED:NONE\n")
                else:
                    f.write(f"BLACK_TOTEM_INHERITED:{self.game_board.black_totem_inherited}\n")

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
            from customboard import CustomBoard
            new_board = CustomBoard()
            random.seed(time.time())
            new_board.game_noise_seed = random.randint(0,1000000)
            print("Partita caricata, nuovo seed =", new_board.game_noise_seed)
            new_board.move_history.clear()

            for r in range(8):
                row_line = lines[r].strip()
                piece_names = row_line.split(",")
                if len(piece_names)!=8:
                    messagebox.showerror("Error", f"Riga {r+1} non valida (8 pezzi).")
                    return
                for c in range(8):
                    new_board.board[r][c] = int(piece_names[c])

            idx = 8
            if idx>=len(lines) or not lines[idx].startswith("GAME_OVER:"):
                messagebox.showerror("Error","Formato file non corretto (GAME_OVER).")
                return
            idx+=1
            val_go = lines[idx].strip() if idx<len(lines) else ""
            new_board.game_over = (val_go=="True")
            idx+=1

            if idx>=len(lines) or not lines[idx].startswith("WINNER:"):
                messagebox.showerror("Error","Formato file non corretto (WINNER).")
                return
            winner_val = lines[idx].split(":",1)[1].strip()
            if winner_val=="None":
                new_board.winner = None
            else:
                new_board.winner = winner_val
            idx+=1

            if idx>=len(lines) or not lines[idx].startswith("Turn:"):
                messagebox.showerror("Error","Formato file non corretto (Turn).")
                return
            turn_str = lines[idx].split(":",1)[1].strip()
            new_board.turn_white = (turn_str=="W")
            idx+=1

            def parse_bool(line_str, prefix):
                if not line_str.startswith(prefix):
                    messagebox.showerror("Error", f"Formato file non corretto ({prefix}).")
                    return None
                val = line_str.split(":",1)[1].strip()
                return (val=="True")

            if idx<len(lines):
                wkm = parse_bool(lines[idx], "WHITE_KING_MOVED")
                if wkm is None: return
                new_board.white_king_moved = wkm
                idx+=1

            if idx<len(lines):
                wlrm = parse_bool(lines[idx], "WHITE_LEFT_ROOK_MOVED")
                if wlrm is None: return
                new_board.white_left_rook_moved = wlrm
                idx+=1

            if idx<len(lines):
                wrrm = parse_bool(lines[idx], "WHITE_RIGHT_ROOK_MOVED")
                if wrrm is None: return
                new_board.white_right_rook_moved = wrrm
                idx+=1

            if idx<len(lines):
                bkm = parse_bool(lines[idx], "BLACK_KING_MOVED")
                if bkm is None: return
                new_board.black_king_moved = bkm
                idx+=1

            if idx<len(lines):
                blrm = parse_bool(lines[idx], "BLACK_LEFT_ROOK_MOVED")
                if blrm is None: return
                new_board.black_left_rook_moved = blrm
                idx+=1

            if idx<len(lines):
                brrm = parse_bool(lines[idx], "BLACK_RIGHT_ROOK_MOVED")
                if brrm is None: return
                new_board.black_right_rook_moved = brrm
                idx+=1

            if idx<len(lines) and lines[idx].startswith("WHITE_TOTEM_INHERITED:"):
                wti_str = lines[idx].split(":",1)[1].strip()
                if wti_str == "NONE":
                    new_board.white_totem_inherited = None
                else:
                    new_board.white_totem_inherited = wti_str
                idx+=1

            if idx<len(lines) and lines[idx].startswith("BLACK_TOTEM_INHERITED:"):
                bti_str = lines[idx].split(":",1)[1].strip()
                if bti_str == "NONE":
                    new_board.black_totem_inherited = None
                else:
                    new_board.black_totem_inherited = bti_str
                idx+=1

            if idx<len(lines) and lines[idx].strip()=="MOVE_HISTORY:":
                idx+=1
                while idx<len(lines):
                    mh_line = lines[idx].strip()
                    if mh_line:
                        new_board.move_history.append(mh_line)
                    idx+=1

            self.game_board = new_board
            self.selected_square = None
            self.last_move_from = None
            self.last_move_to = None
            self.draw_board()
            self.update_evaluation()
            self.update_status()

            self.moves_listbox.delete(0, tk.END)
            for mv in new_board.move_history:
                self.moves_listbox.insert(tk.END, convert_move_to_algebraic(mv))

            messagebox.showinfo("Load","Posizione caricata correttamente!")
        except Exception as e:
            messagebox.showerror("Error", f"Errore caricamento:\n{e}")

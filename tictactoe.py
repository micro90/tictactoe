"""Tic Tac Toe GUI Application (Player vs Computer).

Provides a Tkinter desktop screen where a user can play Tic Tac Toe against
the computer, automatically determines and highlights the winner (or draw)
at the end of each game, tracks scores across games, and provides New Game
and Exit buttons.
"""

import random
import sys
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Tuple

APP_VERSION: str = "1.3.0"
__version__: str = APP_VERSION

WINNING_COMBINATIONS: List[Tuple[int, int, int]] = [
    (0, 1, 2),  # Top row
    (3, 4, 5),  # Middle row
    (6, 7, 8),  # Bottom row
    (0, 3, 6),  # Left column
    (1, 4, 7),  # Middle column
    (2, 5, 8),  # Right column
    (0, 4, 8),  # Main diagonal
    (2, 4, 6),  # Anti-diagonal
]


class TicTacToeLogic:
    """Core game state and winner/AI logic for Tic Tac Toe."""

    def __init__(self) -> None:
        self.board: List[str] = [""] * 9
        self.current_turn: str = "X"  # Player is X, Computer is O
        self.game_over: bool = False
        self.winner: Optional[str] = None  # "X", "O", or "Draw"
        self.winning_line: Optional[Tuple[int, int, int]] = None

    def reset(self) -> None:
        """Reset board state for a new game."""
        self.board = [""] * 9
        self.current_turn = "X"
        self.game_over = False
        self.winner = None
        self.winning_line = None

    def make_move(self, index: int, symbol: str) -> bool:
        """Place a symbol on the board and evaluate if the game has ended."""
        if self.game_over or index < 0 or index >= 9 or self.board[index] != "":
            return False

        self.board[index] = symbol
        winner, line = self.check_winner(self.board)
        if winner is not None:
            self.game_over = True
            self.winner = winner
            self.winning_line = line
        else:
            self.current_turn = "O" if symbol == "X" else "X"
        return True

    @staticmethod
    def check_winner(
        board: List[str],
    ) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
        """Return ('X' or 'O', winning_triple) if someone won, ('Draw', None) if full, else (None, None)."""
        for a, b, c in WINNING_COMBINATIONS:
            if board[a] != "" and board[a] == board[b] == board[c]:
                return board[a], (a, b, c)
        if all(cell != "" for cell in board):
            return "Draw", None
        return None, None

    def choose_computer_move(self) -> Optional[int]:
        """Select a move for the computer ('O').

        Uses tactical checks (win immediately if possible, block player win if
        needed, take center/corners/edges) so games feel responsive and fun.
        """
        available = [i for i, cell in enumerate(self.board) if cell == ""]
        if not available or self.game_over:
            return None

        # 1. If computer can win this turn, take the winning move
        for idx in available:
            test_board = self.board.copy()
            test_board[idx] = "O"
            winner, _ = self.check_winner(test_board)
            if winner == "O":
                return idx

        # 2. If player is about to win next turn, block them
        for idx in available:
            test_board = self.board.copy()
            test_board[idx] = "X"
            winner, _ = self.check_winner(test_board)
            if winner == "X":
                return idx

        # 3. Take center if free
        if 4 in available:
            return 4

        # 4. Take an available corner
        corners = [i for i in (0, 2, 6, 8) if i in available]
        if corners:
            return random.choice(corners)

        # 5. Otherwise pick any remaining space
        return random.choice(available)


class TicTacToeApp:
    """Graphical interface for playing Tic Tac Toe against the computer."""

    VERSION: str = APP_VERSION

    BG_THEMES: List[Tuple[str, str, str]] = [
        ("Deep Teal", "#162d3a", "#224254"),
        ("Midnight Indigo", "#1b2240", "#29335c"),
        ("Forest Slate", "#1b3329", "#284a3c"),
        ("Classic Dark", "#1e1e2e", "#313244"),
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic Tac Toe - Player vs Computer")
        self.root.geometry("440x640")
        self.root.resizable(False, False)

        self.theme_index: int = 0
        self.bg_color: str = self.BG_THEMES[self.theme_index][1]
        self.surface_color: str = self.BG_THEMES[self.theme_index][2]
        self.root.configure(bg=self.bg_color)

        self.logic = TicTacToeLogic()
        self.player_name: str = "Player"
        self.player_name_var = tk.StringVar(root, value=self.player_name)
        self.dropdown_var = tk.StringVar(root, value="Menu ▾")
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.buttons: List[tk.Button] = []

        self._build_menu()
        self._build_ui()

    def _build_menu(self) -> None:
        """Create the application drop-down menu bar with a Version option."""
        self.menu_bar = tk.Menu(self.root)
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(
            label=f"Version (v{self.VERSION})",
            command=self.show_version,
        )
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.root.config(menu=self.menu_bar)

    def _build_ui(self) -> None:
        # Top Header Frame with Title and Drop-down Menu
        self.header_frame = tk.Frame(self.root, bg=self.bg_color)
        self.header_frame.pack(fill="x", padx=24, pady=(10, 4))

        self.title_label = tk.Label(
            self.header_frame,
            text="Tic Tac Toe",
            font=("Segoe UI", 22, "bold"),
            fg="#cdd6f4",
            bg=self.bg_color,
        )
        self.title_label.pack(side="left")

        self.version_dropdown = tk.OptionMenu(
            self.header_frame,
            self.dropdown_var,
            f"Version: v{self.VERSION}",
            "New Game",
            "Change Theme",
            "Exit",
            command=self._on_dropdown_select,
        )
        self.version_dropdown.config(
            font=("Segoe UI", 9, "bold"),
            bg=self.surface_color,
            fg="#cdd6f4",
            activebackground="#45475a",
            activeforeground="#cdd6f4",
            highlightthickness=0,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.version_dropdown["menu"].config(
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg="#cdd6f4",
            activebackground="#89b4fa",
            activeforeground="#11111b",
        )
        self.version_dropdown.pack(side="right", pady=(6, 0))

        # Player Name Entry Row
        self.name_frame = tk.Frame(self.root, bg=self.bg_color)
        self.name_frame.pack(pady=(0, 6))

        self.name_prompt_label = tk.Label(
            self.name_frame,
            text="Player Name:",
            font=("Segoe UI", 10, "bold"),
            fg="#cdd6f4",
            bg=self.bg_color,
        )
        self.name_prompt_label.pack(side="left", padx=(0, 6))

        self.name_entry = tk.Entry(
            self.name_frame,
            textvariable=self.player_name_var,
            font=("Segoe UI", 10),
            width=16,
            bg=self.surface_color,
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            bd=4,
        )
        self.name_entry.pack(side="left", padx=(0, 6))
        self.name_entry.bind("<Return>", lambda _e: self.apply_player_name())
        self.name_entry.bind("<FocusOut>", lambda _e: self.apply_player_name())

        self.set_name_btn = tk.Button(
            self.name_frame,
            text="Set Name",
            font=("Segoe UI", 9, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            activeforeground="#11111b",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.apply_player_name,
        )
        self.set_name_btn.pack(side="left")

        # Scoreboard Label
        self.score_label = tk.Label(
            self.root,
            text=self._score_text(),
            font=("Segoe UI", 11),
            fg="#a6adc8",
            bg=self.bg_color,
        )
        self.score_label.pack(pady=(0, 8))

        # Status / Winner Banner
        self.status_label = tk.Label(
            self.root,
            text=self._turn_text(),
            font=("Segoe UI", 13, "bold"),
            fg="#89b4fa",
            bg=self.surface_color,
            padx=12,
            pady=8,
            width=34,
        )
        self.status_label.pack(pady=(0, 12))

        # 3x3 Grid Frame
        self.grid_frame = tk.Frame(self.root, bg=self.bg_color)
        self.grid_frame.pack(pady=4)

        for i in range(9):
            btn = tk.Button(
                self.grid_frame,
                text="",
                font=("Segoe UI", 26, "bold"),
                width=4,
                height=1,
                bg=self.surface_color,
                fg="#cdd6f4",
                activebackground="#45475a",
                activeforeground="#cdd6f4",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda idx=i: self.on_cell_click(idx),
            )
            row, col = divmod(i, 3)
            btn.grid(row=row, column=col, padx=5, pady=5, ipadx=8, ipady=8)
            self.buttons.append(btn)

        # Bottom Control Bar (New Game + Background + Exit Buttons)
        self.controls_frame = tk.Frame(self.root, bg=self.bg_color)
        self.controls_frame.pack(fill="x", padx=24, pady=(16, 12))

        self.new_game_btn = tk.Button(
            self.controls_frame,
            text="New Game",
            font=("Segoe UI", 10, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            activeforeground="#11111b",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.reset_game,
        )
        self.new_game_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.bg_btn = tk.Button(
            self.controls_frame,
            text="Change BG",
            font=("Segoe UI", 10, "bold"),
            bg="#cba6f7",
            fg="#11111b",
            activebackground="#d9bcef",
            activeforeground="#11111b",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.change_background_color,
        )
        self.bg_btn.pack(side="left", expand=True, fill="x", padx=6)

        self.exit_btn = tk.Button(
            self.controls_frame,
            text="Exit",
            font=("Segoe UI", 10, "bold"),
            bg="#f38ba8",
            fg="#11111b",
            activebackground="#eba0ac",
            activeforeground="#11111b",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.exit_game,
        )
        self.exit_btn.pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _turn_text(self) -> str:
        return f"{self.player_name}'s Turn (X) — Click any square"

    def _score_text(self) -> str:
        return (
            f"{self.player_name} (X): {self.scores['X']}   |   "
            f"Computer (O): {self.scores['O']}   |   "
            f"Draws: {self.scores['Draw']}"
        )

    def apply_player_name(self, name: Optional[str] = None) -> None:
        """Update the player's display name from the entry or provided string."""
        if name is not None:
            self.player_name_var.set(name)
        raw_name = self.player_name_var.get().strip()
        self.player_name = raw_name if raw_name else "Player"
        self.player_name_var.set(self.player_name)
        self.score_label.config(text=self._score_text())
        if not self.logic.game_over and self.logic.current_turn == "X":
            self.status_label.config(text=self._turn_text(), fg="#89b4fa")
        elif self.logic.game_over and self.logic.winner == "X":
            self.status_label.config(
                text=f"🎉 Winner: {self.player_name} (X) won the game!",
                fg="#a6e3a1",
            )

    def change_background_color(
        self, bg_color: Optional[str] = None, surface_color: Optional[str] = None
    ) -> None:
        """Cycle to the next background theme or apply a custom background color."""
        if bg_color is not None:
            self.bg_color = bg_color
            self.surface_color = surface_color or self.surface_color
        else:
            self.theme_index = (self.theme_index + 1) % len(self.BG_THEMES)
            _, self.bg_color, self.surface_color = self.BG_THEMES[self.theme_index]

        self.root.configure(bg=self.bg_color)
        for widget in (
            self.header_frame,
            self.title_label,
            self.name_frame,
            self.name_prompt_label,
            self.score_label,
            self.grid_frame,
            self.controls_frame,
        ):
            widget.configure(bg=self.bg_color)

        self.name_entry.configure(bg=self.surface_color)
        self.status_label.configure(bg=self.surface_color)
        self.version_dropdown.configure(bg=self.surface_color)
        self.version_dropdown["menu"].configure(bg=self.surface_color)

        winning_indices = set(self.logic.winning_line or ())
        for idx, btn in enumerate(self.buttons):
            if idx not in winning_indices:
                btn.configure(bg=self.surface_color)

    def show_version(self, show_dialog: bool = True) -> str:
        """Display the application version number and return the version string."""
        version_text = f"Tic Tac Toe v{self.VERSION}"
        self.status_label.config(text=f"ℹ️ {version_text}", fg="#89b4fa")
        if show_dialog:
            messagebox.showinfo("Application Version", version_text, parent=self.root)
        return version_text

    def _on_dropdown_select(self, selection: str) -> None:
        """Handle selection from the header drop-down menu."""
        self.dropdown_var.set("Menu ▾")
        if selection.startswith("Version"):
            self.show_version()
        elif selection == "New Game":
            self.reset_game()
        elif selection == "Change Theme":
            self.change_background_color()
        elif selection == "Exit":
            self.exit_game()

    def on_cell_click(self, index: int) -> None:
        """Handle player clicking a board cell."""
        self.apply_player_name()
        if self.logic.game_over or self.logic.current_turn != "X":
            return

        if not self.logic.make_move(index, "X"):
            return

        self._update_button(index, "X")

        if self.logic.game_over:
            self._finish_game()
            return

        self.status_label.config(text="Computer (O) is thinking...", fg="#f9e2af")
        self.root.after(250, self._computer_turn)

    def _computer_turn(self) -> None:
        """Execute the computer's move."""
        if self.logic.game_over or self.logic.current_turn != "O":
            return

        move = self.logic.choose_computer_move()
        if move is not None:
            self.logic.make_move(move, "O")
            self._update_button(move, "O")

        if self.logic.game_over:
            self._finish_game()
        else:
            self.status_label.config(
                text=self._turn_text(), fg="#89b4fa"
            )

    def _update_button(self, index: int, symbol: str) -> None:
        color = "#89b4fa" if symbol == "X" else "#fab387"
        self.buttons[index].config(text=symbol, fg=color)

    def _finish_game(self) -> None:
        """Highlight winner and update status banner & scoreboard."""
        winner = self.logic.winner
        if winner in self.scores:
            self.scores[winner] += 1
            self.score_label.config(text=self._score_text())

        if self.logic.winning_line:
            win_bg = "#a6e3a1" if winner == "X" else "#f38ba8"
            for idx in self.logic.winning_line:
                self.buttons[idx].config(bg=win_bg, fg="#11111b")

        if winner == "X":
            msg = f"🎉 Winner: {self.player_name} (X) won the game!"
            self.status_label.config(text=msg, fg="#a6e3a1")
        elif winner == "O":
            msg = "🤖 Winner: Computer (O) won the game!"
            self.status_label.config(text=msg, fg="#f38ba8")
        else:
            msg = "🤝 Game Over: It's a Draw!"
            self.status_label.config(text=msg, fg="#f9e2af")

    def reset_game(self) -> None:
        """Start a fresh round of Tic Tac Toe."""
        self.logic.reset()
        for btn in self.buttons:
            btn.config(text="", bg=self.surface_color, fg="#cdd6f4")
        self.status_label.config(
            text=self._turn_text(), fg="#89b4fa"
        )

    def exit_game(self) -> None:
        """Close the application."""
        self.root.destroy()


def run_self_test() -> int:
    """Verify game logic, winner detection, computer AI, and GUI initialization."""
    # 1. Test Player X winning row
    game = TicTacToeLogic()
    game.make_move(0, "X")
    game.make_move(3, "O")
    game.make_move(1, "X")
    game.make_move(4, "O")
    game.make_move(2, "X")
    assert game.game_over is True, "Game should be over when X completes top row"
    assert game.winner == "X", f"Expected X to win, got {game.winner}"
    assert game.winning_line == (0, 1, 2), f"Unexpected winning line {game.winning_line}"

    # 2. Test Computer O winning diagonal & blocking logic
    game2 = TicTacToeLogic()
    game2.board = [
        "O", "X", "X",
        "",  "O", "",
        "",  "",  "",
    ]
    ai_move = game2.choose_computer_move()
    assert ai_move == 8, f"Expected AI to take winning move 8, got {ai_move}"
    game2.make_move(ai_move, "O")
    assert game2.game_over is True and game2.winner == "O"

    # 3. Test Draw detection
    game3 = TicTacToeLogic()
    game3.board = [
        "X", "O", "X",
        "X", "O", "O",
        "O", "X", "",
    ]
    game3.make_move(8, "X")
    assert game3.game_over is True and game3.winner == "Draw"

    # 4. Test GUI creation, player name entry, background color change, move simulation, reset, and Exit button
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.update_idletasks()

    # Verify default changed background colour and cycling background colour
    initial_bg = app.bg_color
    assert initial_bg == "#162d3a" and root.cget("bg") == initial_bg
    app.change_background_color()
    assert app.bg_color != initial_bg and root.cget("bg") == app.bg_color

    # Verify entering player name updates scoreboard and status labels
    app.player_name_var.set("Alice")
    app.apply_player_name()
    assert app.player_name == "Alice"
    assert "Alice (X):" in app.score_label.cget("text")
    assert "Alice's Turn (X)" in app.status_label.cget("text")

    # Verify version drop-down menu options and show_version behavior
    assert app.VERSION == APP_VERSION and len(APP_VERSION) > 0
    help_menu_label = app.help_menu.entrycget(0, "label")
    assert APP_VERSION in help_menu_label, f"Expected version in Help menu label, got {help_menu_label}"
    dropdown_menu = app.version_dropdown["menu"]
    dropdown_first_label = dropdown_menu.entrycget(0, "label")
    assert APP_VERSION in dropdown_first_label, f"Expected version in dropdown label, got {dropdown_first_label}"
    version_output = app.show_version(show_dialog=False)
    assert APP_VERSION in version_output
    assert APP_VERSION in app.status_label.cget("text")

    app.on_cell_click(4)  # Player clicks center
    root.update_idletasks()
    assert app.logic.board[4] == "X"
    app.reset_game()
    assert all(cell == "" for cell in app.logic.board)
    app.exit_game()
    print("SELF_TEST_PASSED")
    return 0


def main() -> None:
    if "--self-test" in sys.argv:
        sys.exit(run_self_test())

    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

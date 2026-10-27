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

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic Tac Toe - Player vs Computer")
        self.root.geometry("420x540")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.logic = TicTacToeLogic()
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.buttons: List[tk.Button] = []

        self._build_ui()

    def _build_ui(self) -> None:
        # Title Label
        title_label = tk.Label(
            self.root,
            text="Tic Tac Toe",
            font=("Segoe UI", 22, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e",
        )
        title_label.pack(pady=(16, 4))

        # Scoreboard Label
        self.score_label = tk.Label(
            self.root,
            text=self._score_text(),
            font=("Segoe UI", 11),
            fg="#a6adc8",
            bg="#1e1e2e",
        )
        self.score_label.pack(pady=(0, 8))

        # Status / Winner Banner
        self.status_label = tk.Label(
            self.root,
            text="Your Turn (X) — Click any square",
            font=("Segoe UI", 13, "bold"),
            fg="#89b4fa",
            bg="#313244",
            padx=12,
            pady=8,
            width=32,
        )
        self.status_label.pack(pady=(0, 14))

        # 3x3 Grid Frame
        grid_frame = tk.Frame(self.root, bg="#1e1e2e")
        grid_frame.pack(pady=4)

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Segoe UI", 26, "bold"),
                width=4,
                height=1,
                bg="#313244",
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

        # Bottom Control Bar (New Game + Exit Buttons)
        controls_frame = tk.Frame(self.root, bg="#1e1e2e")
        controls_frame.pack(fill="x", padx=32, pady=(20, 14))

        self.new_game_btn = tk.Button(
            controls_frame,
            text="New Game",
            font=("Segoe UI", 11, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            activeforeground="#11111b",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.reset_game,
        )
        self.new_game_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.exit_btn = tk.Button(
            controls_frame,
            text="Exit",
            font=("Segoe UI", 11, "bold"),
            bg="#f38ba8",
            fg="#11111b",
            activebackground="#eba0ac",
            activeforeground="#11111b",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.exit_game,
        )
        self.exit_btn.pack(side="right", expand=True, fill="x", padx=(8, 0))

    def _score_text(self) -> str:
        return (
            f"You (X): {self.scores['X']}   |   "
            f"Computer (O): {self.scores['O']}   |   "
            f"Draws: {self.scores['Draw']}"
        )

    def on_cell_click(self, index: int) -> None:
        """Handle player clicking a board cell."""
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
                text="Your Turn (X) — Click any square", fg="#89b4fa"
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
            msg = "🎉 Winner: You (X) won the game!"
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
            btn.config(text="", bg="#313244", fg="#cdd6f4")
        self.status_label.config(
            text="Your Turn (X) — Click any square", fg="#89b4fa"
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

    # 4. Test GUI creation, move simulation, reset, and Exit button
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.update_idletasks()
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

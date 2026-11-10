# Implemented features

## Issue #1: change the background colour
- New Deep Teal default theme (#162d3a background / #224254 surface) plus
  selectable `BG_THEMES`; "Change BG" button in the bottom bar cycles themes.

## Issue #2: enter player name
- Player name input bar ("Set Name"); scoreboard, turn indicator, and winner
  banner display the entered name via `apply_player_name`.

## Verification
- `run_self_test` extended to assert theme cycling and player-name updates;
  `python tictactoe.py --self-test` exits 0 (`SELF_TEST_PASSED`).

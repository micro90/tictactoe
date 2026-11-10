# Implemented features

## Issue #3: add version number feature
- App version constant `APP_VERSION = "v1.3.0"` in tictactoe.py.
- `Help` menu on the menu bar with a "Version (v1.3.0)" option, plus a
  theme-styled `Menu ▾` drop-down with "Version: v1.3.0" — selecting either
  shows the version in the status banner and an info dialog (`show_version`).
- Drop-down restyles with the active background theme.

## Verification
- `run_self_test` asserts the version string in both menus and exercises
  `show_version`; `python tictactoe.py --self-test` exits 0.
- Independently rebuilt via PyInstaller (`tictactoe.spec`), copied to repo
  root: PE32+ GUI, `./tictactoe.exe --self-test` exits 0.

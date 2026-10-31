# Levita performance policy 1.1

Pure policy helpers for Thermalright Levita preview and LCD frame rates.

- The physical display defaults to 15 FPS. Values up to 30 FPS are regular
  choices; 60 FPS remains an explicit experimental opt-in.
- Unexpected ticker failures step down through a bounded fallback chain until
  the safe 15-FPS target is reached.
- Game activity can be signalled by Feral GameMode, Gamescope, an explicit
  process allow-list or the user's manual switch.
- Idle process/GameMode observation uses a ten-second interval so it does not
  create needless local helper-process churn.
- The module deliberately has no CPU/GPU-load heuristic, generic Wayland window
  inspection, USB access or hardware ownership.

The surrounding Qt surface performs asynchronous process observation and keeps
preview FPS separate from the physical LCD FPS.

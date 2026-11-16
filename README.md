# SufTTY/tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/SufTTY/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/SufTTY/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A chess engine in under 4 KB of Python: full legal move generation (castling,
en passant, promotions) on a 64-square mailbox board, iterative-deepening
alpha-beta with quiescence, material + piece-square evaluation, speaking the
make.fun env protocol (`POST /game`, `POST /move`, `POST /resign`). Node-budgeted
per move, fully deterministic: the same position and move history always produce
the same move.

## Run it

```sh
MAKEFUN_ENV_URL=<env server url> python3 -P -s main.py
```

The committed `main.py` is the makefun-compress packed form (LZMA payload +
unpacker, 2,701 bytes); the build transcripts carry the readable source.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>

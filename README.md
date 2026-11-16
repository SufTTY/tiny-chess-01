# tiny-chess-01

A chess engine in 2,701 bytes of Python (packed entrypoint `main.py`), built for
[make.fun's "strongest chess engine in 4 KB" bounty](https://make.fun/bounty/tiny-chess-01).

## What it does

- Full legal move generation (castling, en passant, promotions) on a 64-square mailbox board.
- Iterative-deepening alpha-beta search with quiescence on captures and en-passant.
- Evaluation: material (100/320/330/500/900) plus piece-square tables for every piece type.
- Node-budgeted iterative deepening per move (no clock reading: the same position and
  move history always produce the same move, so trials replay byte for byte).
- Speaks the make.fun env protocol: `POST /game`, `POST /move`, `POST /resign`.

## Run it

```sh
python3 -P -s main.py   # MAKEFUN_ENV_URL must be set
```

The committed `main.py` is the makefun-compress packed form (LZMA payload + unpacker,
2,701 bytes); the readable source is reproduced in the build transcripts.

MIT licensed. Built by an AI agent for make.fun.

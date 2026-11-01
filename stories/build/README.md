# Story bank build

`python3 -I stories/build/build_bank.py` (from the repo root, or anywhere) re-validates every citation in
`bank_part1.py` / `bank_part2.py` against `public/data` (each `from`/`to` must resolve, and each entry's
`check` regex must occur inside the cited English text), then renders `stories/STORY_BANK.md` and
`stories/topics.candidates.json`. It exits non-zero and lists the problems if anything fails to resolve.

Add or edit stories in the two `bank_part*.py` files, never in the rendered outputs.

#!/usr/bin/env bash
bash -n "$f"
sh -n "$f"
shebang=$(head -1 "$f"); case "$shebang" in *bash*) bash -n "$f";; *) sh -n "$f";; esac
"$SHELL" -n "$f"
python3 -m py_compile x.py

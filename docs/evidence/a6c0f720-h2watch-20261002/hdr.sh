#!/bin/bash
cd /home/hakudoukai/a2/wt-a6c0-h2watch
echo "# HEAD=$(git rev-parse HEAD)"
echo "# porcelain_lines=$(git status --porcelain | wc -l)"
for f in shim/hakudokai/hakudokai_hermes2_reverse_watcher.sh shim/hakudokai/lib/hermes2_reverse_guard.sh tests/test_hermes2_reverse_wake_dedup.py; do
  echo "# sha256=$(sha256sum "$f" | cut -c1-64) blob=$(git rev-parse HEAD:"$f") crlf=$(grep -c $'\r' "$f") $f"
done
echo "# ran_at=$(date -Is)"

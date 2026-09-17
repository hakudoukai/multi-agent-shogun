#!/usr/bin/env bash
ls -l /dev/fd/0 2>&1 | sed "s/^/fd0: /"; lsof -p $$ 2>/dev/null | awk "\$4 ~ /^0/ {print \"fd0->\", \$9}"

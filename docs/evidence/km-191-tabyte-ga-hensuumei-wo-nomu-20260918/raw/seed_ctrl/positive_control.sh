#!/usr/bin/env bash
set -u
rc=0
echo "rc=$rc★"          # 乙 code
echo "rc=${rc}★"        # 甲
echo "rc=$rc:"          # 半角: 乙でない
echo "$rc"★             # 丙
# echo "rc=$rc★"        # 註の乙
cat <<'EOF2'
rc=$rc★ (展開無の heredoc)
EOF2

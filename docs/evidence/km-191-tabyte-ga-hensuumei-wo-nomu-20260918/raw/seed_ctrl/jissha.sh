# km-191 實射の種(己の束)。引数: <shell> <LANG値>。同じ一行を set -u 有/無で。
SH=$1; L=$2
run(){ desc=$1; shift; out=$(env LANG="$L" LC_ALL="$L" "$SH" -c "$*" 2>&1); rc=$?; printf '  %-38s rc=%s out=[%s]\n' "$desc" "$rc" "$out"; }
echo "--- shell=$SH LANG=$L ($(env LANG="$L" LC_ALL="$L" "$SH" -c 'echo ${BASH_VERSION:-zsh $ZSH_VERSION}'))"
run 'set -u 有: "rc=$rc★"'            'set -u; rc=0; echo "rc=$rc★"'
run 'set -u 無: "rc=$rc★"'            'rc=0; echo "rc=$rc★"'
run 'set -u 有: "rc=${rc}★"(甲)'      'set -u; rc=0; echo "rc=${rc}★"'
run 'set -u 有: "rc=$rc:"(半角・陰性)'  'set -u; rc=0; echo "rc=$rc:"'
run 'set -u 有: "rc=$rc"★(丙)'        'set -u; rc=0; echo "rc=$rc"★'

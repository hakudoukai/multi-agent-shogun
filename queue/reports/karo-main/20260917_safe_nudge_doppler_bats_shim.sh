#!/usr/bin/env bash
# /tmp/bats_shim.sh <file.bats> — ★bats ではない★。bats 無き機で bats file の論理を走らせる最小の器。
# 為る事: @test "名" { → 函数化 / load / run(status,output,lines) / setup_file / setup / teardown / BATS_TEST_TMPDIR。
# 為らぬ事: skip・bats-assert・timing・TAP の細部。CI の bats 走行を代へる物ではない。
set -u
F="$(realpath "$1")"; export BATS_TEST_FILENAME="$F"
T=$(mktemp -d /tmp/shim.XXXXXX)
mapfile -t NAMES < <(command grep -E '^@test ' "$F" | sed -E 's/^@test "([^"]*)".*/\1/')
sed -E 's/^@test "[^"]*" \{/bats_test_FUNC() {/' "$F" | awk '/bats_test_FUNC\(\)/{n++; sub("bats_test_FUNC","bats_test_"n)} {print}' > "$T/t.sh"
load() { local p="$1"; [[ "$p" != /* ]] && p="$(dirname "$BATS_TEST_FILENAME")/$p"; [[ -f "$p" ]] || p="$p.bash"; source "$p"; }
run() { local e="$-"; set +e; output="$("$@" 2>&1)"; status=$?; [[ "$e" == *e* ]] && set -e; mapfile -t lines <<<"$output"; return 0; }
source "$T/t.sh"
if declare -f setup_file >/dev/null; then setup_file || { echo "not ok - setup_file failed"; echo "1..0 (shim)"; exit 1; }; fi
pass=0; fail=0
for i in $(seq 1 ${#NAMES[@]}); do
  export BATS_TEST_TMPDIR; BATS_TEST_TMPDIR=$(mktemp -d "$T/test$i.XXXX")
  ( set -e; if declare -f setup >/dev/null; then setup; fi; "bats_test_$i"; if declare -f teardown >/dev/null; then teardown; fi ) > "$T/out$i" 2>&1
  rc=$?
  if [ "$rc" -eq 0 ]; then echo "ok $i ${NAMES[$((i-1))]}"; pass=$((pass+1))
  else echo "not ok $i ${NAMES[$((i-1))]}  (rc=$rc)"; sed 's/^/#   /' "$T/out$i" | tail -4; fail=$((fail+1)); fi
done
echo "1..${#NAMES[@]}  pass=$pass fail=$fail  runner=SHIM(not bats) bash=$BASH_VERSION"
[ "$fail" -eq 0 ]

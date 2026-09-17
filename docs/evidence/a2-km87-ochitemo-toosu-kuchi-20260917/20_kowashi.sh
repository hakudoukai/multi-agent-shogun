#!/bin/bash
# ★写しだけを走らせる。生器も実箱も一字も触らぬ。★
# 使ひ方: bash 20_kowashi.sh <case> ; 出目は _after/20_<case>.{rc,out,err,verdict}
B="$(cd "$(dirname "$0")" && pwd)"
UT="$B/utsushi/stop_hook_inbox.sh"
CASE="${1:?case required}"
ROOT="$B/hako/$CASE"
AID="testseat"
rm -rf "$ROOT"; mkdir -p "$ROOT/queue/inbox"
INBOX="$ROOT/queue/inbox/${AID}.yaml"

mk_inbox() {  # $1 = 未読件数
  { echo "messages:"
    local i=1
    while [ "$i" -le "$1" ]; do
      echo "- content: 'ためし便 $i'"
      echo "  from: karo-mac"
      echo "  id: msg_test_$i"
      echo "  read: false"
      i=$((i+1))
    done
    echo "- content: '既読の便'"
    echo "  from: karo-mac"
    echo "  id: msg_read_1"
    echo "  read: true"
  } > "$INBOX"
}

STDIN_JSON='{"stop_hook_active": false, "last_assistant_message": "ためし"}'
ACTIVE_JSON='{"stop_hook_active": true, "last_assistant_message": "ためし"}'
IN="$STDIN_JSON"
PATH_OVERRIDE=""
STDIN_MODE="normal"

case "$CASE" in
  n6)   mk_inbox 6 ;;                                   # 宣した fail-open(>5)
  n0)   mk_inbox 0 ;;                                   # 陰性対照: 真に0
  n3)   mk_inbox 3 ;;                                   # 陰性対照: 真に3
  nA0)  mk_inbox 0; IN="$ACTIVE_JSON" ;;                # active・真に0
  nA3)  mk_inbox 3; IN="$ACTIVE_JSON" ;;                # active・真に3
  k_nofile)  mk_inbox 3; rm -f "$INBOX" ;;              # 箱を消す(主路)
  k_dir)     mk_inbox 3; rm -f "$INBOX"; mkdir -p "$INBOX" ;;   # 箱を dir に
  k_perm)    mk_inbox 3; chmod 000 "$INBOX" ;;          # 箱の権 000
  k_grepfail) mk_inbox 3; PATH_OVERRIDE="$ROOT/shimbin:$PATH"; mkdir -p "$ROOT/shimbin"
             printf '#!/bin/sh\nexit 2\n' > "$ROOT/shimbin/grep"; chmod +x "$ROOT/shimbin/grep" ;;
  kA_nofile) mk_inbox 3; rm -f "$INBOX"; IN="$ACTIVE_JSON" ;;   # active路・箱無
  kA_dir)    mk_inbox 3; rm -f "$INBOX"; mkdir -p "$INBOX"; IN="$ACTIVE_JSON" ;;
  kA_perm)   mk_inbox 3; chmod 000 "$INBOX"; IN="$ACTIVE_JSON" ;;
  kA_grepfail) mk_inbox 3; IN="$ACTIVE_JSON"; PATH_OVERRIDE="$ROOT/shimbin:$PATH"; mkdir -p "$ROOT/shimbin"
             printf '#!/bin/sh\nexit 2\n' > "$ROOT/shimbin/grep"; chmod +x "$ROOT/shimbin/grep" ;;
  k_badjson) mk_inbox 3; IN='{"stop_hook_active": TRUE, broken' ;;
  k_bigline) mk_inbox 3; python3 -c "
import sys
sys.stdout.write('x'*100000+'\n')" >> "$INBOX" ;;
  k_notmux)  mk_inbox 3 ;;                              # TMUX_PANE 有・tmux 落ち
  k_fifo)    mk_inbox 3; rm -f "$INBOX"; mkfifo "$INBOX" ;;
  kA_fifo)   mk_inbox 3; rm -f "$INBOX"; mkfifo "$INBOX"; IN="$ACTIVE_JSON" ;;
  k_nostdin) mk_inbox 3; STDIN_MODE="fifo" ;;           # stdin を開いたまま閉ぢぬ
  *) echo "unknown case: $CASE" >&2; exit 2 ;;
esac

RUNPATH="$PATH"
[ -n "$PATH_OVERRIDE" ] && RUNPATH="$PATH_OVERRIDE"

ENVARGS=(env "__STOP_HOOK_SCRIPT_DIR=$ROOT" "IDLE_FLAG_DIR=$ROOT" "PATH=$RUNPATH")
if [ "$CASE" = "k_notmux" ]; then
  # TMUX_PANE は在るが tmux は PATH に無い → L99 が落ちる
  mkdir -p "$ROOT/emptybin"
  ENVARGS=(env "__STOP_HOOK_SCRIPT_DIR=$ROOT" "IDLE_FLAG_DIR=$ROOT" "PATH=$ROOT/emptybin:/usr/bin:/bin" "TMUX_PANE=%999")
else
  ENVARGS+=("__STOP_HOOK_AGENT_ID=$AID")
fi

T0=$(date +%s)
if [ "$STDIN_MODE" = "fifo" ]; then
  SFIFO="$ROOT/stdin.fifo"; mkfifo "$SFIFO"
  sleep 300 > "$SFIFO" &   # 書き手が閉ぢぬ = EOF が来ぬ
  HOLDER=$!
  gtimeout 60 "${ENVARGS[@]}" bash "$UT" < "$SFIFO" > "$B/_after/20_${CASE}.out" 2> "$B/_after/20_${CASE}.err"
  RC=$?
  kill "$HOLDER" 2>/dev/null
else
  printf '%s' "$IN" | gtimeout 60 "${ENVARGS[@]}" bash "$UT" > "$B/_after/20_${CASE}.out" 2> "$B/_after/20_${CASE}.err"
  RC=$?
fi
T1=$(date +%s)
echo "$RC" > "$B/_after/20_${CASE}.rc"

OUTB=$(wc -c < "$B/_after/20_${CASE}.out" | tr -d ' ')
ERRL=$(grep -c '' "$B/_after/20_${CASE}.err"); GRC=$?
[ "$GRC" -gt 1 ] && ERRL="測れぬ(grep rc=$GRC)"
if grep -q '"decision"' "$B/_after/20_${CASE}.out" 2>/dev/null; then
  VERD="止められた(block)"
elif [ "$RC" -eq 124 ]; then
  VERD="★止★(60秒で己が止めた)"
elif [ "$RC" -eq 0 ] && [ "$OUTB" -eq 0 ]; then
  VERD="★眠つた(approve・stdout 0byte)★"
else
  VERD="其の他(rc=$RC out=${OUTB}byte)"
fi
{
  echo "case      = $CASE"
  echo "rc        = $RC"
  echo "秒        = $((T1-T0))"
  echo "stdout    = ${OUTB} byte"
  echo "stderr 行 = ${ERRL}"
  echo "判定      = $VERD"
} > "$B/_after/20_${CASE}.verdict"
cat "$B/_after/20_${CASE}.verdict"

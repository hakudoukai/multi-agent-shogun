#!/bin/bash
# ★両対照★ ―― 旗 ASW_PROCESS_TIMEOUT の 14 形 × 版 を、
#   ★生器の写しを実際に daemon として走らせて★ 測る。生器(scripts/)へは一字も書かぬ。
#
# 觀る物(出目4欄):
#   rc          … gtimeout 下の終了符。★-9 = 期待どほり刻限まで生きて居た★
#                 (`gtimeout -s KILL` ゆゑ SIGKILL=9 ―― 124 ではない。實測で正した)
#   stdout byte … 走の stdout の大きさ
#   stderr 行   … ★trace を除いた★ 器自身の stderr 行数(PS4 印で分ける)
#   未読処理    … trace 中の `process_unread timeout` の呼び回数(0=処理せぬ / ≧1=処理する)
#
# 砂箱: SCRIPT_DIR は 写しの置き場の親 ∴ suna/<runid>/ に閉ぢる。
#   scripts/ を置かぬ故 inbox_write.sh 等の呼びは空振り(|| true で吸はれる)。
#   pane は実在せぬ session 名 ―― tmux は「can't find session」で倒れる(実測済)。
set -u
R=/Users/momizimac/multi-agent-shogun
B="$(cd "$(dirname "$0")/.." && pwd)"
SEC="${KM88_SEC:-12}"
TMO="${KM88_TMO:-2}"
PANE='km88nopane:0.0'
AG='km88a'

# 形の名 → 値の建て方。★値は python で建てる★(改行・全角を shell の字面に晒さぬ為)
# ★shell の grep は ugrep ―― .gitignore を honor する(本 repo の .gitignore 7行目は裸の `*`)。
#   束の中の紙を数へさせると ★0 を返し得る★ ∴ /usr/bin/grep を名指す★
forms="${KM88_FORMS:-f01_unset f02_empty f03_blank_sp f04_zero f05_one f06_two f07_true f08_minus1 f09_mark_nl f10_lead_nl f11_zeropad f12_plus1 f13_lead_sp1 f14_zen_zero}"

printf 'ver\tform\tenv_hyouki\trc\tstdout_byte\tstderr_gyou_ki\ttrace_gyou\tpu_timeout\tpu_event\tpu_startup\tfixflag_ji\n'

for ver in "$@"; do
  for f in $forms; do
    D="$B/suna/${ver}_${f}"
    rm -rf "$D"; mkdir -p "$D/ki" "$D/queue/inbox" "$D/queue/metrics" "$D/.venv/bin" "$D/idle"
    cp "$B/ki/${ver}.sh" "$D/ki/w.sh"
    printf '#!/bin/bash\nexec %s/.venv/bin/python3 "$@"\n' "$R" > "$D/.venv/bin/python3"
    chmod +x "$D/.venv/bin/python3"
    cat > "$D/queue/inbox/${AG}.yaml" <<'YEOF'
messages:
- content: km88 未読の種(砂箱・実害無し)
  expires_at: null
  from: km88
  id: msg_km88_0001
  read: false
  supersedes: null
  timestamp: '2026-09-17T12:00:00'
  type: notification
YEOF
    # 値を建てる(python が env を組んで exec する ―― 改行も全角もそのまま渡る)
    /usr/bin/env python3 - "$D" "$f" "$SEC" "$TMO" "$PANE" "$AG" "$R" <<'PEOF'
# -*- coding: utf-8 -*-
import os, subprocess, sys
D, f, SEC, TMO, PANE, AG, R = sys.argv[1:8]
VALS = {
 'f01_unset':    None,
 'f02_empty':    '',
 'f03_blank_sp': ' ',
 'f04_zero':     '0',
 'f05_one':      '1',
 'f06_two':      '2',
 'f07_true':     'true',
 'f08_minus1':   '-1',
 'f09_mark_nl':  '␊1',
 'f10_lead_nl':  '\n1',
 'f11_zeropad':  '01',
 'f12_plus1':    '+1',
 'f13_lead_sp1': ' 1',
 'f14_zen_zero': '０',
}
v = VALS[f]
e = dict(os.environ)
e.pop('ASW_PROCESS_TIMEOUT', None)
if v is not None:
    e['ASW_PROCESS_TIMEOUT'] = v
e['WATCH_BACKEND']   = 'fswatch'
e['INOTIFY_TIMEOUT'] = TMO
e['IDLE_FLAG_DIR']   = D + '/idle'
e['APPROVAL_ALERT_FILE'] = D + '/approval'
e['PS4'] = '#TR# '
open(D + '/env_hyouki.txt', 'w', encoding='utf-8').write(
    ('(未設定)' if v is None else repr(v)) + '\n')
out = open(D + '/out.txt', 'wb')
err = open(D + '/err.txt', 'wb')
p = subprocess.run(['/opt/homebrew/bin/gtimeout', '-s', 'KILL', SEC,
                    '/bin/bash', '-x', D + '/ki/w.sh', AG, PANE, 'claude'],
                   stdout=out, stderr=err, env=e, cwd=D)
rc = p.returncode          # ★管を通さず直後に取る★
out.close(); err.close()
open(D + '/rc.txt', 'w').write('%d\n' % rc)
# ★空の流れも一行として書く★(0byte の紙は臺帳の條④で除かれ「臺帳外」に化ける)
for nm in ('out.txt', 'err.txt'):
    q = D + '/' + nm
    n = os.path.getsize(q)
    open(D + '/' + nm + '.bytes', 'w').write('%d\n' % n)
    if n == 0:
        open(q, 'w', encoding='utf-8').write(
            '★空である旨★ %s に一字も無し(0 byte)\n' % nm)
PEOF
    rc="$(cat "$D/rc.txt" 2>/dev/null || echo 99)"
    ob="$(cat "$D/out.txt.bytes")"   # ★空を一行に書き替へる前の生の byte 数★
    # ★trace 行と器自身の stderr 行を分ける★(PS4='#TR# ' ゆゑ trace は ^#+TR#)
    tg="$(/usr/bin/grep -c -E '^#+TR# ' "$D/err.txt")"; [ -z "$tg" ] && tg=0
    eg="$(/usr/bin/grep -c -v -E '^#+TR# ' "$D/err.txt")"; [ -z "$eg" ] && eg=0
    put="$(/usr/bin/grep -c -E '^#+TR# process_unread timeout$' "$D/err.txt")"
    pue="$(/usr/bin/grep -c -E '^#+TR# process_unread event$' "$D/err.txt")"
    pus="$(/usr/bin/grep -c -E '^#+TR# process_unread startup$' "$D/err.txt")"
    ff="$(/usr/bin/grep -c -E '^#+TR# fix_flag ASW_PROCESS_TIMEOUT ' "$D/err.txt")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$ver" "$f" "$(tr -d '\n' < "$D/env_hyouki.txt")" "$rc" "$ob" "$eg" "$tg" "$put" "$pue" "$pus" "$ff"
  done
done

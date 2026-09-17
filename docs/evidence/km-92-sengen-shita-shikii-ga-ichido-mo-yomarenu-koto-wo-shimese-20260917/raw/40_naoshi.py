# -*- coding: utf-8 -*-
"""40 直し(第81弾 km-92 ㋓・二走= 41 初走の S2_max_int(2^63-1 が永久 FRESH)を受け上限 253402300799 を足した・初走は .first)―― 写し raw/00_target_detect_stale.sh から ★逐語の錨★ で三箇所を置き換へ(各 count==1 を assert・行番を焼かぬ)、直した写しを raw/40_utsushi/scripts/lib/detect_stale.sh に置く(CLI・test の写しも同じ樹へ)。bash -n・diff・sha16/bytes/行 を刷る。生器へ 0 字。
㋐ 閾を「讀ませる」(宣を消す側は捨てる・理由は README ㊄)/ ㋒ date の方言を python3 fromisoformat(本 lib が既に依る・enter_restart_common_watchdog.sh L221 と同 idiom)へ・出目を 數字のみ + 比較器そのもの [ -gt 0 ] で検む(裁 seq323062⑷ 甲)・閾も同じ作法で検め倒す時は名指す(同 乙)。"""
import os, sys, re, time, subprocess, hashlib, shutil, difflib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
SRC = D + '/raw/00_target_detect_stale.sh'; T = D + '/raw/40_utsushi'; DST = T + '/scripts/lib/detect_stale.sh'
s0 = open(SRC, encoding='utf-8').read(); s = s0
def rep(old, new):
    global s; n = s.count(old); assert n == 1, f'錨が {n} 箇所(1 でなければ打たぬ): {old[:60]!r}'; s = s.replace(old, new)
# ―― 一 ―― L33 の宣: 既定を一箇所に置き、未設定のみ既定へ(空・空白は函数が名指す)
rep('DETECT_STALE_STALE_SEC="${DETECT_STALE_STALE_SEC:-120}"   # 設計 §1.2 verbatim\n',
    '_DETECT_STALE_STALE_SEC_DEFAULT=120   # 設計 §1.2 verbatim (stale 閾値 = response_by_time 超過 120s)\n'
    '# ★km-92 (2026-09-17)★ `:-` → `-`: 未設定のみ既定へ。空 / 空白 / 非數 は _detect_stale_stale_sec が名指して倒す (裁 seq323062⑷ 乙)。\n'
    'DETECT_STALE_STALE_SEC="${DETECT_STALE_STALE_SEC-$_DETECT_STALE_STALE_SEC_DEFAULT}"\n')
# ―― 二 ―― 閾を讀む函数(_detect_stale_log の直後・status enum の直前)
rep('# status enum 正本 (設計 §2 (1)、Codex T1 是正)\n',
'''# ★km-92 (2026-09-17) 閾を讀む★: DETECT_STALE_STALE_SEC (設計 §1.2 verbatim 120s) は宣のみで讀手 0 であつた
#   (repo 全体 `git grep` 1 行 = 宣其の物、閾を 999999 / abc にしても出目が変はらぬ = km-92 raw/30_kansu.txt)。
#   本函数が閾を ★比較に使ふのと同じ演算子 `[ -ge 0 ]` で検め★ (裁 seq323062⑷ 甲)、空 / 空白のみ / 非數 / 負 /
#   桁溢れ を ★名指して★ 既定へ倒す (同 乙)。stdout に有効値 (數字のみ) を刷る。rc は常に 0 (倒す事は失敗ではない、log に残す)。
_detect_stale_stale_sec() {
    local raw="${DETECT_STALE_STALE_SEC-}"
    local default="${_DETECT_STALE_STALE_SEC_DEFAULT:-120}"
    case "$raw" in
        '')
            _detect_stale_log "WARN" "stale_sec_empty: DETECT_STALE_STALE_SEC='' → 既定 ${default} へ倒す"
            printf '%s' "$default"; return 0 ;;
        *[![:space:]]*) ;;
        *)
            _detect_stale_log "WARN" "stale_sec_blank: DETECT_STALE_STALE_SEC='${raw}' (空白のみ) → 既定 ${default} へ倒す"
            printf '%s' "$default"; return 0 ;;
    esac
    case "$raw" in
        *[!0-9]*)
            _detect_stale_log "WARN" "stale_sec_malformed: DETECT_STALE_STALE_SEC='${raw}' (數字のみを受ける) → 既定 ${default} へ倒す"
            printf '%s' "$default"; return 0 ;;
    esac
    # 甲: 比較器そのもので検む (桁溢れ 2^63 は bash の [ が rc=2 で拒む = 30_kansu 実測)
    if ! [ "$raw" -ge 0 ] 2>/dev/null; then
        _detect_stale_log "WARN" "stale_sec_out_of_range: DETECT_STALE_STALE_SEC='${raw}' (比較器 [ -ge 0 ] rc≠0) → 既定 ${default} へ倒す"
        printf '%s' "$default"; return 0
    fi
    printf '%s' "$raw"; return 0
}

# status enum 正本 (設計 §2 (1)、Codex T1 是正)
''')
# ―― 三 ―― deadline の parse と番人
rep('''    local deadline_epoch
    deadline_epoch=$(date -d "$response_by_time" +%s 2>/dev/null || echo "0")
    if [ "$deadline_epoch" -le 0 ]; then
        _detect_stale_log "ANOMALY" "deadline_malformed: corr_id=${safe_id} response_by_time='${response_by_time}' (parse 不能 = auto-poke 禁)"
        return 2
    fi
    if [ "$now" -lt "$deadline_epoch" ]; then
        _detect_stale_log "FRESH" "corr_id=${safe_id} response_by_time=${response_by_time} not yet stale"
        return 1
    fi
''',
'''    # ★km-92 (2026-09-17) 方言と番人★
    #   旧: `date -d` は GNU 語法 ── BSD (macOS) では `illegal option -- d` rc=1 → `|| echo "0"` → ★正しい時刻も悉く
    #       deadline_malformed★ (km-92 raw/20_date.txt / 30_kansu 姿B)。且つ `[ "$deadline_epoch" -le 0 ]` は非數
    #       (abc / 空 / 1e3 / 2^63 / 改行入り) で rc=2 → if 偽 → 次の `[ now -lt … ]` も rc=2 → 偽 → ★STALE 候補へ
    #       落ちて auto-poke★ (30_kansu 姿S: abc / 空 / 2^63 / 1e3 が悉く enqueued=1)。註「parse 不能 → ANOMALY」は嘘であつた。
    #   新: python3 (本 lib が既に json で 5 箇所依る) の fromisoformat で方言無しに epoch へ (Z / ±hh:mm / ±hhmm /
    #       naive を受ける、enter_restart_common_watchdog.sh の `fromisoformat(….replace('Z','+00:00'))` と同 idiom)。
    #       出目は ★數字のみ★ を受け、其の上で比較器そのもの `[ -gt 0 ]` で検む (桁溢れは bash の [ が rc=2 で拒む)。
    #       何れも外れれば ANOMALY (fail-closed)。python3 が無ければ rc 127 → 空 → ANOMALY。
    local deadline_epoch
    deadline_epoch=$(printf '%s' "$response_by_time" | python3 -c 'import sys, re
from datetime import datetime
s = sys.stdin.read().strip()
if s.endswith("Z") or s.endswith("z"): s = s[:-1] + "+00:00"
s = re.sub(r"([+-]\\d\\d)(\\d\\d)$", r"\\1:\\2", s)
try: print(int(datetime.fromisoformat(s).timestamp()))
except Exception: sys.exit(1)' 2>/dev/null) || deadline_epoch=""
    case "$deadline_epoch" in
        ''|*[!0-9]*)
            _detect_stale_log "ANOMALY" "deadline_malformed: corr_id=${safe_id} response_by_time='${response_by_time}' epoch='${deadline_epoch}' (parse 不能 or 非數 = auto-poke 禁)"
            return 2 ;;
    esac
    #   上限 253402300799 = 9999-12-31T23:59:59Z (fromisoformat の上限)。parser が壊れて 2^63-1 を刷つても
    #   ★永久 FRESH★ に成らぬ様、比較器そのもの [ -gt 0 ] と [ -le 上限 ] の両側で検む (41 二走 S2_max_int が FRESH であつた疵)。
    if ! [ "$deadline_epoch" -gt 0 ] 2>/dev/null || ! [ "$deadline_epoch" -le 253402300799 ] 2>/dev/null; then
        _detect_stale_log "ANOMALY" "deadline_out_of_range: corr_id=${safe_id} response_by_time='${response_by_time}' epoch='${deadline_epoch}' (比較器 [ -gt 0 ] && [ -le 253402300799 ] rc≠0 = auto-poke 禁)"
        return 2
    fi
    # ★閾を讀む★: stale = now ≥ deadline + DETECT_STALE_STALE_SEC (設計 §1.2「response_by_time 超過 120s」)。
    #   `now - sec < deadline` の形で比較する (deadline + sec の桁溢れを避ける)。
    local stale_sec
    stale_sec=$(_detect_stale_stale_sec)
    if [ $((now - stale_sec)) -lt "$deadline_epoch" ]; then
        _detect_stale_log "FRESH" "corr_id=${safe_id} response_by_time=${response_by_time} not yet stale (deadline_epoch=${deadline_epoch} stale_sec=${stale_sec} now=${now})"
        return 1
    fi
''')
os.makedirs(T + '/scripts/lib', exist_ok=True); os.makedirs(T + '/scripts/tests', exist_ok=True)
open(DST, 'w', encoding='utf-8', newline='\n').write(s)
for f in ('fukuincho_detect_stale_cli.sh', 'tests/test_detect_stale.sh', 'tests/test_fukuincho_detect_stale_cli.sh'): shutil.copyfile(D + '/raw/utsushi/scripts/' + f, T + '/scripts/' + f)
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]; b0 = s0.encode('utf-8'); b1 = s.encode('utf-8')
p = subprocess.run(['/bin/bash', '-n', DST], capture_output=True, text=True)
diff = list(difflib.unified_diff(s0.split('\n'), s.split('\n'), 'a/scripts/lib/detect_stale.sh', 'b/scripts/lib/detect_stale.sh', lineterm='', n=3))
K.kaku(D + '/raw/40_diff.txt', '\n'.join(diff))
adds = sum(1 for l in diff[2:] if l.startswith('+')); dels = sum(1 for l in diff[2:] if l.startswith('-'))
out = [f'# 40 直し ㋓ / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 錨 3 箇所(各 count 1 を assert・行番を焼かぬ)',
       f'前: raw/00_target_detect_stale.sh sha16 {sha16(b0)} {len(b0)}B {b0.count(b"\n")}行 / 後: raw/40_utsushi/scripts/lib/detect_stale.sh sha16 {sha16(b1)} sha256 {hashlib.sha256(b1).hexdigest()} {len(b1)}B {b1.count(b"\n")}行',
       f'bash -n rc {p.returncode} {p.stderr.strip()[:200]} / diff +{adds} -{dels} 行(raw/40_diff.txt) / CRLF {b1.count(b"\r")} / 末尾改行 {"一つ" if b1.endswith(b"\n") and not b1.endswith(b"\n\n") else "★疵★"} / 行末空白 {sum(1 for l in s.split(chr(10)) if l != l.rstrip())} 行',
       '三箇所: 一= 宣 `:-`→`-` + 既定を _DETECT_STALE_STALE_SEC_DEFAULT に一本化 / 二= _detect_stale_stale_sec(閾を同じ演算子で検め・空/空白/非數/負/桁溢れを名指して既定へ) / 三= date -d → python3 fromisoformat・出目 數字のみ + [ -gt 0 ]・stale= now-sec < deadline で閾を讀む',
       '捨てた側(宣を消す): 設計 §1.2 の承認値(50a1b936 verbatim・副院長令 341654e4 の表)を実装から消す事に成り、正本と器の食ひ違ひを「器を正本へ合はせる」でなく「正本の値を無かつた事にする」で解く形ゆゑ捨てた。加へて宣は唯一の外からの調整口(cron 側 env)であり、消せば閾は焼き込みに成る。',
       '捨てた側(date -d を残し BSD -j -f を fallback に足す): 方言二本を保つ事に成り、BSD -j -f は書式一本ゆゑ Z / naive / ±hh:mm を拒む(20_date 実測: past_Z rc1・past_+0900 のみ通る)= 三本目の方言が要る。python3 は本 lib が既に json で依る(新依存 0)。']
K.kaku(D + '/raw/40_naoshi.txt', '\n'.join(out)); print('\n'.join(out)); print('\n'.join(diff)[:6000])

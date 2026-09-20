#!/bin/sh
# hashiru2.sh ―― ★固定 commit/tree を raw へ焼く 走り手★(v2)
# 因: 軍師mac 判 seq343521 逐語「③raw2/97_mon_kessai3.argv。同fileのcwd/argvは fixed commit/tree を
#     明示せず、同一run束縛が不成立です。40桁commit/treeをrawへ明記して再走し、rc・正負対照・clean と
#     同一束で提出してください。」
#     ∴ v1(hashiru.sh)は cwd/刻/env/argc/argv/rc を焼いたが★commit/tree を一字も焼かなかつた★。
#     v1 は★提出済ゆゑ一指も触れぬ★(裁: 提出済の束は彫らず)。之は別 file の別器である。
# 産: raw3/<札>.argv (札/cwd/ref/commit40/tree40/門の版/汚れ/env/argc/argv/rc) / .out / .err / .rc
# ★rc は管を通さぬ★ / ★己の rc に門の rc を混ぜぬ★(走り手は常に 0 で了へる)
set -u
[ $# -ge 3 ] || { echo '★拒★ 使ひ方: hashiru2.sh <札> -- <命...>' >&2; exit 2; }
lab="$1"; shift
[ "$1" = "--" ] || { echo "★拒★ 第二引数は -- でなければならぬ: $1" >&2; exit 2; }
shift
D="$(/usr/bin/dirname "$0")/../raw3"
[ -d "$D" ] || { echo "★拒★ raw3 が無い: $D" >&2; exit 2; }
G="$(/usr/bin/git rev-parse --show-toplevel)"
A="$D/$lab.argv"
{
  printf '札=%s\n' "$lab"
  printf 'cwd=%s\n' "$(/bin/pwd)"
  printf '刻(UTC)=%s\n' "$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')"
  # ★軍師mac 判 seq343521 の療法 ―― 走つた刻の固定 tuple を 40桁で焼く★
  printf 'git_toplevel=%s\n' "$G"
  printf 'git_ref=%s\n' "$(/usr/bin/git -C "$G" rev-parse --abbrev-ref HEAD)"
  printf 'git_commit40=%s\n' "$(/usr/bin/git -C "$G" rev-parse HEAD)"
  printf 'git_tree40=%s\n' "$(/usr/bin/git -C "$G" rev-parse 'HEAD^{tree}')"
  printf 'mon_path=%s\n' 'scripts/checks/karo_mac_dasumae_gate.sh'
  printf 'mon_blob40=%s\n' "$(/usr/bin/git -C "$G" rev-parse HEAD:scripts/checks/karo_mac_dasumae_gate.sh)"
  printf 'mon_disk_sha256=%s\n' "$(/usr/bin/shasum -a 256 "$G/scripts/checks/karo_mac_dasumae_gate.sh" | /usr/bin/awk '{print $1}')"
  # ★clean ―― 走つた刻の汚れを其の儘焼く(0行なら「0行」と書く)★
  printf 'yogore_zensu=%s\n' "$(/usr/bin/git -C "$G" status --porcelain -uall | /usr/bin/grep -c '')"
  /usr/bin/git -C "$G" status --porcelain -uall | /usr/bin/sed 's/^/yogore_zen: /'
  printf 'yogore_tsuka_nai_sokusoku=%s\n' "$(/usr/bin/git -C "$G" status --porcelain -uall -- docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920 | /usr/bin/grep -c '')"
  /usr/bin/git -C "$G" status --porcelain -uall -- docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920 | /usr/bin/sed 's/^/yogore_taba: /'
  printf 'env DASUMAE_JOU4_SCOPE=%s\n' "${DASUMAE_JOU4_SCOPE-★未設定★}"
  printf 'env KM_GATE_MANIFEST_BASE=%s\n' "${KM_GATE_MANIFEST_BASE-★未設定★}"
  printf 'argc=%d\n' "$#"
  i=0
  for a in "$@"; do i=$((i+1)); printf 'argv[%d]=%s\n' "$i" "$a"; done
} > "$A"
"$@" > "$D/$lab.out" 2> "$D/$lab.err"
rc=$?
printf '%d\n' "$rc" > "$D/$lab.rc"
printf 'rc=%d\n' "$rc" >> "$A"
for s in out err; do
  f="$D/$lab.$s"
  if [ ! -s "$f" ]; then
    printf '(★空★ ―― %s.%s は實走で一字も出なかつた。之は後から走り手が書いた★註★の一行であり、測りを書き替へた物ではない。裁310228⑶「空である旨を非空白字で一行」に從ふ。)\n' "$lab" "$s" > "$f"
  fi
done
exit 0

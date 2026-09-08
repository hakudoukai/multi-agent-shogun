#!/usr/bin/env bash
# audit_disk_pressure.sh ― 4PC ディスク圧の常設計器（★読取専★）
#
# ★此の器は 消す/移す/圧す を 一指も行はぬ★
#   rm / mv / gzip / xz / fstrim / truncate / docker prune の類を ★一語も書いて居らぬ★。
#   讀むのは df・stat・/proc・ls のみ。書くのは ★己の標準出力★ だけである。
#
# ★静かな時は黙る★（受入④）
#   閾値を超えた対象が無ければ 標準出力は ★空★。cron/常設で回して差支へ無い。
#
# ★母数と「測れなかつた」は別値（受入②・合算するな）★
#   targets_total / measured / unmeasured / exceeded を ★別々の key★ で出す。
#   ★「測れなかつた」を 0 と書かぬ・measured に足さぬ★。
#   ★測れなかつた対象は 黙らせぬ★ ―― 但し ★出し方を改めた（2026-09-08 18:1x 実測の後）★。
#   ★食ひ違ひの開示★: 初めは 測り漏れを ★一件一行★ で出した。第三PC で実際に走らせると
#   ★18 行★ 出て、受入④『★閾値超のみ 1 行(静かな時は黙る器)★』と ★字面で食ひ違つた★。
#   因は ★no-silent-failure と『静かな時は黙る』が 同じ走で真正面から衝突する★ 事に在る。
#   ★両立の形★: 測り漏れが ★既知で恒常★（他 PC は経路無し／drvfs は別母数）である間は
#     ・既定 …… ★要約 一行★（DISKUNMEASURED_SUMMARY）に纏める＝黙らぬが 騒がぬ。
#     ・--report … 一件一行の内訳も出す（数へ直せる様に）。
#   ★之は 令を『読み替へた』ものではなく 令の二つの受入が衝突した所を 数で示して
#   埋めた ものである。★選び直すのは 判ずる者の権★ ―― 埋め方が誤りなら 既定を戻せる様
#   一件一行の道（--report）を ★残して在る★。
#
# ★条(十四)を器に鋳込む（受入③・陽性対照）★
#   走る度に まづ selftest を通す。★対照は 二段に分けて在る（下記の疵に因る）★:
#     ㋐ 令の指定値 …… second vhdx 相当（total 225GiB / used 99GiB）
#     ㋑ 閾から作る値 … 今の閾を ★必ず超える★ 値／★必ず下回る★ 値 を その場で組む
#   ★㋑ と 陰性が 期待通りでなければ 実測の数を ★一つも出さず★ exit 3★。
#   ★selftest は 合成値であり 実測ではない★（second の vhdx を当席は讀めぬ ―― 下記 ★測れぬ理★）。
#
# ★★対照の疵の開示（走らせて初めて出た・2026-09-08 18:17 実測）★★
#   初めは ㋐ だけを exit の条件に置いた。すると DP_ABS_MAX_GIB を 100 以上へ上げた
#   ★其れだけで★ 器が rc=3 で死んだ（実測: 閾 100/200/300 の三本 悉く rc=3・出力 0 行）。
#   因は ★㋐ の used=99GiB が 閾 100 を超えられぬ★ 事に在る。
#   ∴ ★★閾に依る対照を 絶対値で置くと 閾を動かした途端 対照ごと死ぬ★★。
#   之は器の思ひ違ひであつて ★条(十四)が誤りなのではない★ ―― 条は正しく働き
#   『動く筈の物が動かぬ ∴ 数を出さぬ』と ★正しく止めた★。止め方は正・置き方が誤り。
#   ★手当★: ㋑（閾から組む対照）を exit の条件とし、★㋐ は残して stderr に述べる★。
#   ★㋐ を exit 条件から外した事は ★令の指定を弱めた★ 事に当たる ⇒ ★開示して裁を仰ぐ★。
#   （黙つて外せば『令の値で対照した』と読まれる。★㋐ が今の閾で當たるか否かは 毎走 stderr に出る★。）
#
# ★測れぬ理（走る前から判つて居る不利）★
#   (a) 当席が local に測れるのは ★己の PC 一台★。他 3 台は 経路が要り ―― ★経路は 打つ前に申す約束★ ゆゑ
#       既定では ★打たぬ★。故に unmeasured=3（why=no_route_not_requested）と ★別値で★ 出る。
#   (b) df は ★瞬間値★ である。圧の ★増え方★ は映さぬ。
#   (c) vhdx は Windows 側の file であり、加へて /mnt/c は I/O error を返す事が在る。
#       ∴ ★/mnt 配下は 触らず skip し unmeasured に数へる★（★触つて固まらぬ為でもある★）。
#   (c)★更め 2026-09-08 18:09★（前の行は ★消さず★ 残す・下が今の実）:
#       ★床は 16:15:31 に戻つて居る★（A1 の器が捉へ 家老が 18:00 に実測）――
#       ∴ ★『/mnt/c が I/O error』は 今は当たらぬ★。★但し skip は続ける★。理由が
#       『I/O error だから』から ★『drvfs は 此の PC の圧ではなく Windows 側の圧であり
#         PC の母数と混ぜれば 母数が二重に成る』★ へ ★入れ替はつた★ のである。
#       ★『触れぬ』は同じでも 理由が違ふ ―― 理由を書き換へずに残すのは 次の者が
#       『I/O error が直つたのだから測れる筈』と読んで 母数を壊さぬ為である。★
#
# ★何処で走らせるか（規は『走らせ方』まで書く・追令 2026-09-08 18:09:59）★
#   ★器は 一本きり★。★複製するな（no-repo-copies）★ ―― 4PC の残 3 台も
#   ★各 PC の席が 己の PC で 此の同じ一本を走らせる★ のが前提である。
#   ・前提 …… bash / coreutils(df,date,hostname,grep,wc) のみ。★特別な導入は要らぬ★。
#              python も git も DB も ★要らぬ★。
#   ・要る権限 … ★一般利用者で足りる★（df は root を要さぬ）。★sudo を要する所は 一つも無い★。
#              root で走らせる必要も ★無い★（読取専ゆゑ 権限を上げる理由が無い）。
#   ・走らせる席 … 各 PC の席（main/second/mac）が ★己の PC で★ 走らせる。
#              ★third の席が 他 PC へ経路を打つて測りに行く事は しない★（追令②）。
#              経路が要る場合は ★上へ請ふ★ ―― 器が勝手に経路を張る事は ★無い★。
#              ★担保の書き方を更める★: 初めは『此の file に ssh の一語も書いて居らぬ』
#              と書いたが、★其の註記自身が ssh と書いて居る★ ゆゑ ★偽であつた★。
#              正しい担保は ★『実行される行に 経路を張る呼出(ssh/scp/curl/wget/nc)が
#              一つも無い』★ である ―― 註釈行を除いて数へれば ★0★（下の一行で検められる）:
#                grep -vE '^\s*#' "$0" | grep -cE '(ssh|scp|curl|wget|nc)[[:space:]]'
#   ・出力の置き所 … ★標準出力のみ★。器は file を一つも作らぬ。
#              捕へたい席は 己の側で `> 己の置き所` へ落とす。★器は置き所を決めぬ★
#              （決めれば 各 PC の床の違ひで壊れ、器が『書く物』に成つて 読取専が崩れる）。
#   ・突き合はせ … 各 PC の生出力を ★一箇所へ集めるのは 人（家老/上）の仕事★ とする。
#              器は自分から どこへも送らぬ。
#
# 使ひ方:
#   audit_disk_pressure.sh                 … 静かな時は黙る（閾値超と測り漏れのみ 1 行づつ）
#   audit_disk_pressure.sh --report        … 母数の summary も出す
#   audit_disk_pressure.sh --selftest-only … selftest だけ回して結果を述べる
# 閾値（env で上書き可）:
#   DP_PCT_MAX=85     … 使用率(%) 之以上で 1 行
#   DP_ABS_MAX_GIB=80 … 実消費(GiB) 之以上で 1 行（vhdx の様に率が低くても嵩む物の為）
set -uo pipefail

DP_PCT_MAX="${DP_PCT_MAX:-85}"
DP_ABS_MAX_GIB="${DP_ABS_MAX_GIB:-80}"
GIB=$((1024*1024*1024))
AS_OF="$(date -Is)"
HOST="$(hostname 2>/dev/null || echo unknown)"

# ── 判定核（★之だけが「閾値超か否か」を決める・selftest も実測も 同じ此処を通る★）──
# 引数: target total_bytes used_bytes  → 超えて居れば 1 行 印字して 0 を返す／超えねば 何も出さず 1 を返す
judge() {
  local target="$1" total="$2" used="$3" pct reason=""
  if [ "$total" -gt 0 ]; then pct=$(( used * 100 / total )); else pct=0; fi
  if [ "$pct" -ge "$DP_PCT_MAX" ]; then reason="pct"; fi
  if [ "$used" -ge $(( DP_ABS_MAX_GIB * GIB )) ]; then
    if [ -n "$reason" ]; then reason="pct+abs"; else reason="abs"; fi
  fi
  [ -z "$reason" ] && return 1
  printf 'DISKPRESS host=%s target=%s total_gib=%s used_gib=%s pct=%s reason=%s as_of=%s\n' \
    "$HOST" "$target" "$(( total / GIB ))" "$(( used / GIB ))" "$pct" "$reason" "$AS_OF"
  return 0
}

# ── selftest（★陽性と陰性を 同じ走に置く★）──
selftest() {
  local canon rc_canon rel_tot rel_hi rel_lo pos neg rc_pos rc_neg
  # ㋐ 令の指定値（225GiB 中 99GiB）― ★exit の条件には用ゐぬ・述べるのみ★
  canon="$(judge selftest-canon-vhdx $(( 225 * GIB )) $(( 99 * GIB )))"; rc_canon=$?
  # ㋑ 閾から組む対照 ― ★何処へ閾を動かしても 必ず超える／必ず下回る★
  rel_tot=$(( (DP_ABS_MAX_GIB + 100) * GIB ))          # 閾より十分大きい total
  # ★疵の手当 二つ目（実測 18:20 で出た）★: 初め rel_hi=rel_tot*(pct+5)/100 と置いた所、
  # DP_PCT_MAX=99 の走で ★used(9464GiB) > total(9100GiB)・pct=104★ ―― ★在り得ぬ入力★ に成つた。
  # 器が動く証にはなるが ★現に起き得ぬ値で対照しては 対照の意味が薄い★。
  # ∴ ★used=total（満杯・pct=100）★ を陽性に用ゐる ―― ★在り得る値で 必ず超える★。
  # （pct_max>100 が指されても rel_tot は abs 閾より 100GiB 大きいゆゑ abs で當たる。）
  rel_hi=$rel_tot                                      # 満杯＝pct 100・abs も超える
  rel_lo=0                                             # 必ず下回る（used 0）
  pos="$(judge selftest-positive "$rel_tot" "$rel_hi")"; rc_pos=$?
  neg="$(judge selftest-negative "$rel_tot" "$rel_lo")"; rc_neg=$?
  if [ "$rc_pos" -ne 0 ] || [ -z "$pos" ]; then
    printf 'SELFTEST result=FAILED_TO_STAND leg=positive_relative note=%s\n' \
      '閾から組んだ陽性で行が出なんだ ―― ★器が動いて居らぬ ∴ 数は出さぬ★' >&2
    return 1
  fi
  if [ "$rc_neg" -eq 0 ] || [ -n "$neg" ]; then
    printf 'SELFTEST result=FAILED_TO_STAND leg=negative note=%s\n' \
      '陰性(used 0)で行が出た ―― ★陰性が汚れて居る ∴ 数は出さぬ★' >&2
    return 1
  fi
  printf 'SELFTEST result=STANDS positive_line=%s negative=silent note=%s\n' \
    "$(printf '%s' "$pos" | tr ' ' ',')" '★合成値であり実測に非ず★' >&2
  # ㋐ の顛末を ★必ず述べる★（黙つて外さぬ為）
  if [ "$rc_canon" -eq 0 ]; then
    printf 'SELFTEST_CANON leg=vhdx_225_99 result=FIRES abs_max_gib=%s pct_max=%s note=%s\n' \
      "$DP_ABS_MAX_GIB" "$DP_PCT_MAX" '★令の指定値は今の閾で當たる★' >&2
  else
    printf 'SELFTEST_CANON leg=vhdx_225_99 result=SILENT abs_max_gib=%s pct_max=%s note=%s\n' \
      "$DP_ABS_MAX_GIB" "$DP_PCT_MAX" '★令の指定値は今の閾では當たらぬ(閾が99GiBより上)・exitは止めぬ・開示済★' >&2
  fi
  return 0
}

# ── local の測り（★讀取のみ★）──
# /mnt 配下・drvfs・9p・tmpfs・overlay は ★測らず unmeasured に数へる★（触つて固まらぬ為）
measure_local() {
  local line src size used mnt fstype
  df -P -B1 -T 2>/dev/null | tail -n +2 | while read -r src fstype size used _avail _pct mnt; do
    case "$mnt" in
      /mnt/*|/proc*|/sys*|/dev*|/run*)
        printf 'DISKUNMEASURED host=%s target=%s why=%s as_of=%s\n' \
          "$HOST" "$mnt" "skipped_not_local_or_volatile" "$AS_OF"; continue;;
    esac
    case "$fstype" in
      drvfs|9p|tmpfs|devtmpfs|overlay|squashfs|proc|sysfs|cgroup*|none)
        printf 'DISKUNMEASURED host=%s target=%s why=%s as_of=%s\n' \
          "$HOST" "$mnt" "skipped_fstype_${fstype}" "$AS_OF"; continue;;
    esac
    judge "$mnt" "$size" "$used" || true
  done
}

# ── 4PC の母数（★測れぬ 3 台を 0 と書かず unmeasured として出す★）──
# 経路（SSH）は ★打つ前に申す約束★ ゆゑ 既定では打たぬ。DP_REMOTE=1 の時のみ 申告済みとして試みる。
declare -a PCS=(main second third mac)
SELF_PC="${DP_SELF_PC:-third}"
remote_targets() {
  local pc
  for pc in "${PCS[@]}"; do
    [ "$pc" = "$SELF_PC" ] && continue
    printf 'DISKUNMEASURED host=%s target=pc:%s why=%s as_of=%s\n' \
      "$HOST" "$pc" "no_route_not_requested" "$AS_OF"
  done
}

MODE="${1:-}"
if ! selftest; then
  printf 'ABORT reason=selftest_did_not_stand note=%s\n' '★条(十四)＝動く筈の物が動かねば 数を出さぬ★' >&2
  exit 3
fi
[ "$MODE" = "--selftest-only" ] && exit 0

OUT="$( { measure_local; remote_targets; } )"
PRESS="$(printf '%s\n' "$OUT" | grep '^DISKPRESS ' || true)"
UNMEA="$(printf '%s\n' "$OUT" | grep '^DISKUNMEASURED ' || true)"
n_unmeas=$(printf '%s' "$UNMEA" | grep -c '^DISKUNMEASURED ' || true)
n_pcun=$(printf '%s' "$UNMEA" | grep -c 'target=pc:' || true)
n_locun=$(( n_unmeas - n_pcun ))
# ★閾値超は 常に 一件一行★（之が受入④の本体）
[ -n "$PRESS" ] && printf '%s\n' "$PRESS"
# ★測り漏れは 既定 要約一行／--report で内訳★（★合算せぬ＝pc と local を別の key で出す★）
if [ "$n_unmeas" -gt 0 ]; then
  printf 'DISKUNMEASURED_SUMMARY host=%s pc_unmeasured=%s local_skipped=%s note=%s as_of=%s\n' \
    "$HOST" "$n_pcun" "$n_locun" "★別の母数ゆゑ足して居らぬ・内訳は--report★" "$AS_OF"
  [ "$MODE" = "--report" ] && printf '%s\n' "$UNMEA"
fi

if [ "$MODE" = "--report" ]; then
  n_press=$(printf '%s' "$PRESS" | grep -c '^DISKPRESS ' || true)
  n_local=$(df -P -B1 -T 2>/dev/null | tail -n +2 | wc -l)
  n_pc=${#PCS[@]}
  # ★合算するな★: local mount と PC は 別の母数ゆゑ 別の key で出す
  printf 'SUMMARY as_of=%s host=%s pc_targets_total=%s pc_measured=%s pc_unmeasured=%s local_mounts_seen=%s exceeded=%s unmeasured_lines=%s\n' \
    "$AS_OF" "$HOST" "$n_pc" 1 "$(( n_pc - 1 ))" "$n_local" "$n_press" "$n_unmeas"
  printf 'NOTE 母数は二つ在り 足し合はせて居らぬ: ★PC の母数(4)★ と ★此の PC の mount の母数(%s)★。\n' "$n_local"
  printf 'NOTE ★measured=1 は「此の PC のみ」の意であり 残 3 台は unmeasured である（0 ではない）★\n'
fi
exit 0

#!/bin/bash
# 85_saisou.sh ―― km-97 REVISE の治し①: ★頭を固定して器を再走★する。提出済 raw/ は一指も触れず、出目は raw2/ へ。
# 用法: bash <束>/driver/85_saisou.sh <束>      (repo 根で呼ぶ・束は根相対)
# 手順: A 刻と頭を焼く(HEAD/基点/untracked 数/門 sha)  B raw/ の sha を先に焼く(不動の證の前半)
#       C 器 10/15/20/30/35/40/50/60 を raw2/ へ再走(各 rc を焼く)  D 己の束が R1 の hit に混じる数を数へる
#       E 前寸法を焼いてから慣例の正規化(末尾空白/CR 剥ぎ・EOF 改行丁度1)・R5 .nul を gzip
#       F 前→後の比較表(87_hikaku.py)  G raw/ の sha を再び焼き cmp(不動の證の後半)
# 禁: raw/ へ書かぬ・箱へ書かぬ(50 は IW_NAME_TEST_ONLY=1 で L75 止まり)・refs を触らぬ。
set -u
B="${1:?束(根相対)を渡せ}"
ROOT=/Users/momizimac/multi-agent-shogun
cd "$ROOT" || exit 2
[ -d "$B/raw" ] || { echo "提出済 raw 無し: $B/raw" >&2; exit 2; }
[ -e "$B/raw2" ] && { echo "raw2 が既に在る ―― 上書きせぬ(新しい名にせよ)" >&2; exit 2; }
mkdir "$B/raw2" || exit 2
O="$B/raw2"; G=/usr/bin/grep; D="$B/driver"
BASE=4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1   # origin/main(據ゑる基点・86_sueru.sh と同じ値)
TS=$(date '+%Y-%m-%dT%H:%M:%S%z')
rc_all=0

# ---- A 刻と頭
{ echo "刻=$TS"
  echo "HEAD(歩いた disk の頭)=$(git rev-parse HEAD) branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "基点(據ゑる親)=$BASE origin/main=$(git rev-parse origin/main) 同=$([ "$BASE" = "$(git rev-parse origin/main)" ] && echo yes || echo NO)"
  n_un=$(git status --porcelain 2>/dev/null | $G -c '^??'); echo "untracked(git status --porcelain ^??)=$n_un"
  n_mod=$(git status --porcelain 2>/dev/null | $G -vc '^??'); echo "tracked_changed(^?? 以外)=$n_mod"
  echo "門 scripts/inbox_write.sh sha16=$(shasum -a 256 scripts/inbox_write.sh | cut -c1-16) lines=$($G -c '' scripts/inbox_write.sh) mtime=$(stat -f %Sm scripts/inbox_write.sh)"
  echo "註: 歩くのは disk であつて commit ではない。disk = HEAD の tree + untracked $n_un 口 + 変更 $n_mod 口。∴ 出目は HEAD 一つに縛れぬ。"
} > "$O/00_atama.txt"

# ---- B raw/ の sha(前)
( cd "$B" && find raw -type f | LC_ALL=C sort | while IFS= read -r f; do shasum -a 256 "$f"; done ) > "$O/01_raw_mae_sha.txt"
echo "raw_mae_files=$($G -c '' "$O/01_raw_mae_sha.txt")"

# ---- C 再走
run(){ # run <名> <cmd...>   stdout→raw2/02_<名>.log, rc→02_driver_rc.txt
  local name="$1"; shift; local rc
  "$@" > "$O/02_${name}.log" 2> "$O/02_${name}.err"; rc=$?
  echo "${name}_rc=$rc" >> "$O/02_driver_rc.txt"; [ "$rc" -eq 0 ] || rc_all=1
  echo "[$name] rc=$rc $(head -1 "$O/02_${name}.log" | cut -c1-120)"
}
: > "$O/02_driver_rc.txt"
run 10_aruki     bash "$D/10_aruki.sh" "$O"
run 15_aruki_R5  bash "$D/15_aruki_R5.sh" "$O"
run 20_ps        python3 -B "$D/20_ps_utsushi.py" "$O"
run 30_gyou      bash "$D/30_gyou.sh" "$B/raw/12_utsuwa_list.txt" "$O/30_gyou_all.txt"
run 35_dai2      bash "$D/35_aruki_dai2.sh" "$O"
run 40_hako      python3 -B "$D/40_hako_jinkou.py" "$O"
run 50_mon       bash "$D/50_mon_jissou.sh" "$O"
for r in R1 R2 R3 R4; do run "60_$r" python3 -B "$D/60_bunrui.py" "$O" "$r" "$O/10_${r}_hits.txt"; done
run 60_R5        python3 -B "$D/60_bunrui.py" "$O" R5 "$O/15_R5_hits.txt"

# ---- D 己の束が R1 hit に混じる数(字面の prefix で除く ―― path ゆゑ除ける・process は除けぬ)
{ echo "# 己の束 = ./$B/  ―― R1 hits の内、此の prefix を持つ行"
  self=$($G -c -F "./$B/" "$O/10_R1_hits.txt"); echo "self_hits=$self"
  ev=$($G -c -F './docs/evidence/' "$O/10_R1_hits.txt"); echo "docs_evidence_hits=$ev"
  ev_mae=$($G -c -F './docs/evidence/' "$B/raw/10_R1_hits.txt"); echo "docs_evidence_hits_mae=$ev_mae"
  self_mae=$($G -c -F "./$B/" "$B/raw/10_R1_hits.txt"); echo "self_hits_mae=$self_mae"
  all=$($G -c '' "$O/10_R1_hits.txt"); echo "R1_hits=$all R1_hits_minus_self=$((all-self))"
} > "$O/03_jiko.txt"; cat "$O/03_jiko.txt"

# ---- E 前寸法 → 正規化 → gzip
{ echo "# 前寸法(正規化/gzip の前) 刻=$(date '+%Y-%m-%dT%H:%M:%S%z')  path bytes lines(grep -c '') sha256"
  ( cd "$B" && find raw2 -type f -not -name 95_mae_sunpou.txt | LC_ALL=C sort | while IFS= read -r f; do printf '%s %s %s %s\n' "$f" "$(stat -f %z "$f")" "$($G -c '' "$f")" "$(shasum -a 256 "$f" | cut -d' ' -f1)"; done ); } > "$O/95_mae_sunpou.txt"
( cd "$B" && find raw2 -type f -not -name '*.nul' -not -name '*.gz' -not -name 95_mae_sunpou.txt | while IFS= read -r f; do
    [ -s "$f" ] || continue; perl -pi -e 's/[ \t\r]+$//' "$f"; perl -0pi -e 's/\n+\z/\n/' "$f"; done )
[ -f "$O/15_R5_files.nul" ] && gzip -9 "$O/15_R5_files.nul"

# ---- F 比較表
python3 -B "$D/87_hikaku.py" "$B/raw" "$O" > "$O/90_hikaku.txt" 2> "$O/90_hikaku.err"; echo "hikaku_rc=$?" >> "$O/02_driver_rc.txt"
cat "$O/90_hikaku.txt"

# ---- G raw/ の sha(後)と cmp
( cd "$B" && find raw -type f | LC_ALL=C sort | while IFS= read -r f; do shasum -a 256 "$f"; done ) > "$O/01_raw_ato_sha.txt"
if cmp -s "$O/01_raw_mae_sha.txt" "$O/01_raw_ato_sha.txt"; then fudou=yes; else fudou=NO; rc_all=1; fi
{ echo "raw_fudou=$fudou files_mae=$($G -c '' "$O/01_raw_mae_sha.txt") files_ato=$($G -c '' "$O/01_raw_ato_sha.txt") cmp_rc=$(cmp -s "$O/01_raw_mae_sha.txt" "$O/01_raw_ato_sha.txt"; echo $?)"
  echo "註: 前半(01_raw_mae_sha)は再走の前に、後半(01_raw_ato_sha)は正規化と gzip の後に焼いた。raw/ は其の間 一度も書かれて居らぬ事の證。"; } > "$O/91_raw_fudou.txt"
cat "$O/91_raw_fudou.txt"
echo "85_saisou rc_all=$rc_all 刻=$(date '+%Y-%m-%dT%H:%M:%S%z')"
exit $rc_all

#!/bin/bash
# 86_sueru.sh ―― km-97 REVISE の治し③: 束を ★新枝へ据ゑる★。共有 index と HEAD を汚さぬ plumbing のみ(checkout/merge/rebase/push 無し)。
# 用法: bash <束>/driver/86_sueru.sh <束(根相対)> <commit message file>     (repo 根で呼ぶ)
# 手順: 0 番人(基点が手許に在る・枝が未だ無い)  1 仮 index に基点の tree を読む  2 束の全 file を hash-object -w → update-index
#       3 write-tree → commit-tree -p 基点 → update-ref(旧値=零40=★新設專用★)
#       4 検め: (a) ls-tree(-C 根・--full-tree・出目に README.md が在る事を対照) と disk の名列の異
#               (b) blob id(rev-parse <c>:<path>) と hash-object <path> の異   (c) 基点は新頭の祖先か  (d) ref の読み戻し
# 出目は悉く _gate/86_sueru_<TS>.txt(己の log ゆゑ disk 側の名列から★宣して除く★・commit には入らぬ)。
set -u
B="${1:?束(根相対)を渡せ}"; MSG="${2:?commit message file を渡せ}"
ROOT=/Users/momizimac/multi-agent-shogun; cd "$ROOT" || exit 2
BASE=4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1        # origin/main(85_saisou.sh 00_atama と同じ値)
REF=refs/heads/ashigaru-mac-1/km-97-hako-wo-umu-michi-wa-ikutsu-aruka-20260917
TS=$(date '+%Y%m%dT%H%M%S'); LOG="$B/_gate/86_sueru_$TS.txt"; G=/usr/bin/grep
[ -f "$MSG" ] || { echo "message file 無し: $MSG" >&2; exit 2; }
say(){ echo "$*" | tee -a "$LOG"; }
say "刻=$(date '+%Y-%m-%dT%H:%M:%S%z') 束=$B 基点=$BASE 枝=$REF 己のlog=$LOG(除)"
# ---- 0 番人
git cat-file -e "$BASE^{commit}"; rc=$?; say "基点 cat-file -e rc=$rc"; [ $rc -eq 0 ] || exit 3
git show-ref --verify -q "$REF"; rc=$?; say "枝 既存か show-ref rc=$rc(1=無し=可)"; [ $rc -eq 1 ] || { say "枝が既に在る ―― 新設專用ゆゑ止む"; exit 4; }
say "origin/main=$(git rev-parse origin/main) 同=$([ "$(git rev-parse origin/main)" = "$BASE" ] && echo yes || echo NO)"
# ---- 1 仮 index
GIT_INDEX_FILE=$(mktemp /tmp/ashigaru-mac-1_idx.XXXXXX) || exit 5; rm -f "$GIT_INDEX_FILE"; export GIT_INDEX_FILE
git read-tree "$BASE"; rc=$?; say "read-tree rc=$rc"; [ $rc -eq 0 ] || exit 5
# ---- 2 束の file を仮 index へ(己の log だけ除く)
n=0; bad=0
while IFS= read -r -d '' f; do
  s=$(git hash-object -w "$f") || { bad=$((bad+1)); continue; }
  git update-index --add --cacheinfo "100644,$s,$f" || bad=$((bad+1))
  n=$((n+1))
done < <(find "$B" -type f -not -name "86_sueru_${TS}*" -print0 | LC_ALL=C sort -z)
say "index へ足した file=$n 失敗=$bad"; [ $bad -eq 0 ] || exit 6
# ---- 3 tree → commit → ref
t=$(git write-tree) || exit 7; say "tree=$t"
c=$(git commit-tree "$t" -p "$BASE" -F "$MSG") || exit 8; say "commit=$c"
git update-ref "$REF" "$c" 0000000000000000000000000000000000000000; rc=$?; say "update-ref rc=$rc(旧値=零40=新設專用)"; [ $rc -eq 0 ] || exit 9
rm -f "$GIT_INDEX_FILE"; unset GIT_INDEX_FILE
# ---- 4 検め
git -C "$ROOT" ls-tree -r --full-tree --name-only "$c" -- "$B/" | LC_ALL=C sort > "$B/_gate/86_sueru_${TS}_lstree.txt"
find "$B" -type f -not -name "86_sueru_${TS}*" | LC_ALL=C sort > "$B/_gate/86_sueru_${TS}_disk.txt"
pc=$($G -c -F "$B/README.md" "$B/_gate/86_sueru_${TS}_lstree.txt"); say "(a) 対照: ls-tree の出目に README.md 在り=$pc"; [ "$pc" -ge 1 ] || { say "対照が鳴らぬ ―― ls-tree の出目が信じられぬゆゑ止む"; exit 10; }
nls=$($G -c '' "$B/_gate/86_sueru_${TS}_lstree.txt"); nd=$($G -c '' "$B/_gate/86_sueru_${TS}_disk.txt")
ndiff=$(LC_ALL=C diff "$B/_gate/86_sueru_${TS}_disk.txt" "$B/_gate/86_sueru_${TS}_lstree.txt" | $G -c '^[<>]')
say "(a) 名列 disk=$nd commit=$nls 異(diff 行)=$ndiff"
mis=0; chk=0
while IFS= read -r f; do
  chk=$((chk+1)); b1=$(git rev-parse -q --verify "$c:$f" 2>/dev/null); b2=$(git hash-object "$f")
  [ -n "$b1" ] && [ "$b1" = "$b2" ] || { mis=$((mis+1)); say "  blob 異: $f commit=${b1:-無} disk=$b2"; }
done < "$B/_gate/86_sueru_${TS}_disk.txt"
say "(b) blob 照合 file=$chk 異=$mis"
git merge-base --is-ancestor "$BASE" "$c"; rc=$?; say "(c) 基点は新頭の祖先か rc=$rc  rev-list --count 基点..新頭=$(git rev-list --count "$BASE..$c")"
say "(c) diff --stat 基点..新頭: $(git diff --stat "$BASE" "$c" | tail -1)"
say "(d) ref 読み戻し $(git rev-parse "$REF") 同=$([ "$(git rev-parse "$REF")" = "$c" ] && echo yes || echo NO)  遠隔 ref(手許の写しのみ・fetch せず)=$(git for-each-ref refs/remotes | $G -c -F 'km-97-hako')"
say "HEAD(共有 worktree)は動かず: $(git rev-parse --abbrev-ref HEAD) $(git rev-parse HEAD)"
say "結: 枝 ${REF#refs/heads/}＝$c 親=$BASE 名列異=$ndiff blob異=$mis"
[ "$ndiff" -eq 0 ] && [ "$mis" -eq 0 ] && [ "$rc" -eq 0 ]; exit $?

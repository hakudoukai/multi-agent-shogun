#!/bin/bash
# km-91 _after/40 ―― ★温 recipe で自枝へ據ゑる★(worktree の生 file を書き換へぬ)
#   札 scope_in⑸ の逐語手順に從ふ。親は札の指す通り main。
#   證: 據ゑる前後で `git status --porcelain` の ★本数★ と ★中身★ が動かぬ事。
set -u
R="$1"; SRC="$2"; BR="$3"; MSGF="$4"
cd "$R" || exit 9

# ── 據ゑる前の porcelain（本数と中身の両方を録る。stderr は別に落とす=數に混ぜぬ）──
git status --porcelain > /tmp/km91_porc_before.txt 2> /tmp/km91_porc_before.err
PB=$(grep -c '' /tmp/km91_porc_before.txt)
echo "porcelain 前  本数=$PB  (stderr 行=$(grep -c '' /tmp/km91_porc_before.err) ―― 之は數に入れぬ)"
echo "  stderr 逐語: $(head -1 /tmp/km91_porc_before.err)"
echo "  束が porcelain に出て居るか: $(grep -c 'km-91-bannin' /tmp/km91_porc_before.txt) 行"
echo

# ── 温 recipe ──
export GIT_INDEX_FILE=$(mktemp -u /tmp/km91_idx_XXXXXX)
echo "GIT_INDEX_FILE=$GIT_INDEX_FILE  (存在=$([ -e "$GIT_INDEX_FILE" ] && echo 有 || echo 無))"
git read-tree "$(git rev-parse main)"; echo "read-tree rc=$?  (親 main=$(git rev-parse main))"

BLOB=$(git hash-object -w "$SRC"); echo "blob=$BLOB  (元=$SRC)"
git update-index --add --cacheinfo 100644,"$BLOB",scripts/stop_hook_inbox.sh; echo "update-index rc=$?"
TREE=$(git write-tree); echo "tree=$TREE  write-tree rc=$?"
CMT=$(git commit-tree "$TREE" -p "$(git rev-parse main)" -F "$MSGF"); echo "commit=$CMT  commit-tree rc=$?"
git update-ref "refs/heads/$BR" "$CMT"; echo "update-ref rc=$?  枝=refs/heads/$BR"
unset GIT_INDEX_FILE
echo "GIT_INDEX_FILE 解除後の設定有無: $([ -n "${GIT_INDEX_FILE+x}" ] && echo ★残つて居る★ || echo 無し)"
echo

# ── 據ゑた物の検め ──
echo "## 據ゑた commit"
git --no-pager log -1 --format='sha=%H%nparent=%P%ntree=%T%nsubject=%s' "refs/heads/$BR"
echo "## 其の commit が触る file（親 main との差の file 一覧）"
git --no-pager diff --name-only main "refs/heads/$BR"; echo "→ file 数=$(git diff --name-only main "refs/heads/$BR" | grep -c '')"
echo "## 束の外を触つて居らぬか（scripts/stop_hook_inbox.sh 以外が在れば★違反★）"
OUT=$(git diff --name-only main "refs/heads/$BR" | grep -v '^scripts/stop_hook_inbox\.sh$' | grep -c '')
echo "束外(＝的の一本以外) file 数=$OUT  $([ "$OUT" -eq 0 ] && echo '★0=可★' || echo '★違反★')"
echo "## 據ゑた blob は写しと一致するか"
echo "commit 内 blob sha256 = $(git cat-file -p "$(git rev-parse "refs/heads/$BR":scripts/stop_hook_inbox.sh)" | shasum -a 256 | cut -c1-16)"
echo "写し      sha256      = $(shasum -a 256 "$SRC" | cut -c1-16)"
echo

# ── 據ゑた後の porcelain ──
git status --porcelain > /tmp/km91_porc_after.txt 2> /tmp/km91_porc_after.err
PA=$(grep -c '' /tmp/km91_porc_after.txt)
echo "porcelain 後  本数=$PA"
echo "★前後の本数 $PB → $PA  差=$((PA-PB))  $([ "$PA" -eq "$PB" ] && echo '★不動=可★' || echo '★動いた★')"
diff /tmp/km91_porc_before.txt /tmp/km91_porc_after.txt > /tmp/km91_porc.diff 2>&1
echo "★中身の差 diff rc=$?  差分行=$(grep -c '' /tmp/km91_porc.diff)  (0 行=中身も不動)"
[ -s /tmp/km91_porc.diff ] && { echo "--- 中身の差（逐語）---"; cat /tmp/km91_porc.diff; }
echo
echo "## worktree の生 file は動いて居らぬか"
echo "worktree blob = $(git hash-object scripts/stop_hook_inbox.sh)  (測る前=8bcea32981614611053393ac0b73cbc2947ea0df)"
echo "worktree sha256 = $(shasum -a 256 scripts/stop_hook_inbox.sh | cut -c1-16)  (凍結時=f1b49820e234a1ee)"

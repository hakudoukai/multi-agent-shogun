#!/usr/bin/env bash
# 50 ―― switch_cli.sh の resolve_pane() を★引数を与へて★測る(裁337393⑶「未測を残すな」)。
#
# ★全体を走らせぬ理由その1(受入⑺)★: 371行以降は send-keys へ至る。
# ★全体を走らせぬ理由その2(新発見・此処で初めて刷る)★:
#   switch_cli.sh L39 `source lib/_section18_roles.sh` は此の Mac(/bin/bash 3.2.57・
#   homebrew bash 不在)では L108 `declare -A SECTION18_ROLE_ALIASES=(...)` が
#   `-A` 非対応ゆゑ添字を算術文脈と誤読し、`set -u` 下で
#   "line 108: shogun: unbound variable" を発して★即死★する
#   (rc≠0・set -e により呼び出し元 switch_cli.sh も其の場で落ちる)。
#   ∴ switch_cli.sh は★実際には、此の環境では、如何なる引数でも L39 で既に落ちて居り、
#     resolve_pane() へ到達し得ぬ★(km-215 の外・pane_identity.sh の bash3.2 declare -A
#     既知疵と★同根・別箇所★。既知疵の対象= pane_identity.sh L104。本件の対象=
#     lib/_section18_roles.sh L108 ―― 之は★新たに此処で見つけた箇所★であり、
#     二器(switch_cli.sh/watcher_supervisor_third.sh)の★何れの不触にも当たらぬ★が、
#     器自体の編集範囲(§18 lib)は km-215 二器の外ゆゑ★直さぬ★)。
#   ★之を隠して測定を諦めるのではなく、実引数で測れる所まで測り、測れぬ所を「測れぬ」と
#     宣する★(第一条・數の規律)。
#
# 測る対象: resolve_pane() の Phase 1 (L68 據ゑ+新WARN) と pane_base (L92 據ゑ+新WARN)。
# ★§18 種別分岐(section18_is_secondpc_agent/section18_mainpc_pane_index)は
#   最小 stub に置換へる★(常に「見つからず」を返す) ―― 之は resolve_pane() 自体の
#   改修箇所(Phase1/pane_base)ではなく、其の先の分岐(§18 lib・本件の外)である。
#   stub である事を★下の出力に明記する★。
set -uo pipefail
cd "$(dirname "$0")/../../../.."   # → repo root (worktree)
PROJECT_ROOT="$(pwd)"
SCRIPT="scripts/switch_cli.sh"

source "${PROJECT_ROOT}/lib/cli_adapter.sh"

# ★stub★(§18 lib はこの環境で source 不能・本件の外・常に「見つからず」)
section18_is_secondpc_agent() { return 1; }
section18_mainpc_pane_index() { return 1; }

LOG_FILE="${PROJECT_ROOT}/logs/switch_cli.log"
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [switch_cli/km215-measure] $*"
    echo "$msg" >&2
}

# resolve_pane() 本体を SCRIPT(編集済 = 本弾の據ゑ後)から抽出して eval する(改変せず其の儘)
FUNC_SRC=$(awk '/^resolve_pane\(\) \{/{p=1} p{print} p&&/^}/{exit}' "$SCRIPT")
eval "$FUNC_SRC"

echo "★stub 明記★: section18_is_secondpc_agent / section18_mainpc_pane_index は常に rc=1 を返す最小 stub(理由=上記コメント逐語)。"
echo ""

for AGENT in ashigaru2 ashigaru-mac-2 gunshi; do
    echo "=== argv=\"$AGENT\" ==="
    out=$(resolve_pane "$AGENT" 2>err.$$.tmp)
    rc=$?
    err=$(cat err.$$.tmp); rm -f err.$$.tmp
    echo "cwd=$PROJECT_ROOT"
    echo "argv=resolve_pane $AGENT"
    echo "rc=$rc"
    echo "stdout=${out:-<空>}"
    echo "stderr="
    echo "$err" | sed 's/^/  /'
    echo ""
done

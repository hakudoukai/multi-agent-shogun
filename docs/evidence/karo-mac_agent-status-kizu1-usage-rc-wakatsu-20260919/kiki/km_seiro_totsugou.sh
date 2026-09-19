#!/usr/bin/env bash
# km_seiro_totsugou.sh ―― ★正路の出が据ゑる前後で変はつて居らぬか★を byte で突合
# ★作法★ argv は★一語ずつ位置引数★で渡す（zsh の中で書くと一語に潰れる＝62 の疵）
# 引数: $1=前版の path  $2=後版の path
set -uo pipefail
OLD="${1:?}"; NEW="${2:?}"
echo "# 前版 = ${OLD}  sha=$(shasum -a 256 "$OLD" | awk '{print $1}')"
echo "# 後版 = ${NEW}  sha=$(shasum -a 256 "$NEW" | awk '{print $1}')"
echo "# bash = ${BASH_VERSION}  刻=$(date '+%Y-%m-%dT%H:%M:%S%z')"
cmp1() {   # cmp1 <argv...>
    local o1 r1 o2 r2 s1 s2
    o1=$(/bin/bash "$OLD" "$@" 2>&1); r1=$?
    o2=$(/bin/bash "$NEW" "$@" 2>&1); r2=$?
    s1=$(printf '%s' "$o1" | shasum -a 256 | awk '{print $1}')
    s2=$(printf '%s' "$o2" | shasum -a 256 | awk '{print $1}')
    echo "-----------------------------------------------------------------"
    echo "argv = [$*]"
    echo "  前版 rc=${r1} 出sha=${s1} 行=$(printf '%s' "$o1" | grep -c '' || true)"
    echo "  後版 rc=${r2} 出sha=${s2} 行=$(printf '%s' "$o2" | grep -c '' || true)"
    if [[ "$s1" == "$s2" ]]; then
        echo "  ★出は byte 一致★"
    else
        echo "  ★不一致 ―― 差を刷る（時で動く欄か、疵かを判ずる為）★"
        diff <(printf '%s\n' "$o1") <(printf '%s\n' "$o2") | sed 's/^/    /'
    fi
}
cmp1 --session multiagent-mac
cmp1 --lang ja
cmp1 --lang en
cmp1
cmp1 --session multiagent-mac --panes 0

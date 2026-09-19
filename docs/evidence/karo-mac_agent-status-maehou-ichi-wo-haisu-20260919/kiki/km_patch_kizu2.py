# -*- coding: utf-8 -*-
import io, hashlib, sys
F = "scripts/agent_status.sh"
s = io.open(F, encoding="utf-8").read()
sha0 = hashlib.sha256(s.encode()).hexdigest()
print("前 sha256=%s 行=%d byte=%d" % (sha0, s.count("\n"), len(s.encode())))

def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "REFUSE %s hit=%d (1でない)" % (tag, n)
    s = s.replace(old, new)
    print("  彫 %-10s hit=1" % tag)

# ── ㋐ state_label へ「曖昧」の顔を足す（rc=3）──
rep('''            2) echo "N/A" ;;
        esac''',
'''            2) echo "N/A" ;;
            3) echo "AMBIG" ;;
        esac''', "㋐en")
rep('''            2) echo "不在" ;;
        esac''',
'''            2) echo "不在" ;;
            3) echo "曖昧" ;;
        esac''', "㋐ja")

# ── ㋑ 度數に的の顔を足す ──
rep('''N_NOPY=0; N_SHAPE=0; N_READERR=0; N_PYDIE=0; N_BOX_NG=0; N_MULTI=0''',
'''N_NOPY=0; N_SHAPE=0; N_READERR=0; N_PYDIE=0; N_BOX_NG=0; N_MULTI=0
# ─── 的（pane）の顔の度數 ―― ★「席が無い」と「的が曖昧」と「寫像が使へぬ」は別の事★
N_BYID=0; N_AMBIG=0; N_NOSESS=0; N_NOPANE=0''', "㋑度數")

# ── ㋒ 解決器を据ゑる（PANE_BASE の直後）──
rep('''PANE_BASE=$(tmux show-options -gv pane-base-index 2>/dev/null || echo 0)
''',
'''PANE_BASE=$(tmux show-options -gv pane-base-index 2>/dev/null || echo 0)

# ─── ★的は @agent_id の完全一致で解く★（委員長裁 seq337507⑶ 疵② / 同 337482 採用形）───
# 実測(2026-09-19 当機 tmux 3.7b ―― 推さず測つた):
#   ⑴ `-t =名` は has-session では効く(rc=1)が、★list-panes では効かぬ★
#      (`list-panes -s -t =multiagent` が rc=0 で multiagent-mac の四席を返す。
#       誤りの字面が "can't find window" ゆゑ window 的と解され session 部へ掛からぬ)
#   ⑵ display-message は★不在の的でも rc=0★（`-t %99999` も rc=0）。
#      更に窓/pane が外れると★其の session の現用 pane へ黙つて倒れる★
#      (`-t multiagent:agents.4` → %7 = 別席の生席)。∴ rc で不在を判じてはならぬ。
#   ∴ 信ずるに足る形は ★pane_id(%N)★ のみ。悉皆列挙して @agent_id で一致を取る。
# 出目: 0=一件のみ(pane_id を stdout へ) / 3=★二件以上=曖昧ゆゑ当てぬ★ / 1=零件
km_pane_id_by_agent_id() {
    local want="$1" ids n
    ids=$(tmux list-panes -a -F '#{pane_id} #{@agent_id}' 2>/dev/null \\
          | awk -v w="$want" '$2==w {print $1}') || true
    [[ -z "$ids" ]] && return 1
    n=$(printf '%s\\n' "$ids" | awk 'END{print NR}')
    if [[ "$n" -ne 1 ]]; then
        return 3
    fi
    printf '%s' "$ids"
    return 0
}
''', "㋒解決器")

# ── ㋓ print_agent_row に「強ひる出目」を受けさせる ──
rep('''# Args: $1=agent, $2=pane_target ("" → pane state を 不在 で表示)
print_agent_row() {
    local agent="$1"
    local pane_target="$2"
''',
'''# Args: $1=agent, $2=pane_target ("" → pane state を 不在 で表示)
#       $3=強ひる出目（任意・"" なら実測する）―― ★3=曖昧★ を「不在」に畳まぬ為
print_agent_row() {
    local agent="$1"
    local pane_target="$2"
    local forced_rc="${3:-}"
''', "㋓引数")

rep('''    local rc pane_state
    if [[ -n "$pane_target" ]]; then''',
'''    local rc pane_state
    if [[ -n "$forced_rc" ]]; then
        rc="$forced_rc"
    elif [[ -n "$pane_target" ]]; then''', "㋓分岐")

# ── ㋔ 固定寫像＋前方一致を廃す（本疵）──
rep('''# MainPC: pane lookup 有り (multiagent:agents.0..4)
for i in "${!MAINPC_AGENTS[@]}"; do
    agent="${MAINPC_AGENTS[$i]}"
    pane_idx=$((PANE_BASE + i))
    pane_target="multiagent:agents.${pane_idx}"
    print_agent_row "$agent" "$pane_target"
done''',
'''# ─── MainPC: ★固定寫像＋前方一致を廃す★（委員長裁 seq337507⑶ 疵② ―― 最優先）───
# 旧: pane_target="multiagent:agents.${pane_idx}"
#   当機に session `multiagent` は無く `multiagent-mac` のみ在る。tmux の -t は前方一致ゆゑ
#   ★六行 悉く別レーンの生席へ当たつて居た★（実測 2026-09-19T13:07:49+0900）:
#     0→%68 家老mac / 1→%72 專任1 / 2→%7 專任2 / 3→%125 專任3 /
#     4→%7・5→%7（index 不在ゆゑ現用 pane へ倒れ、capture だけ rc=1 ∴ ★偽の待機中★）
# 新: ①@agent_id 完全一致→%N ②二件以上=★曖昧ゆゑ当てぬ★ ③零件は固定寫像へ倒れる前に
#     session の完全一致(=名 は has-session では効く)と index の実在を列挙で検め、
#     満たさねば ★不在★ で止まる(fail-closed)。★前方一致の的は一つも作らぬ。★
FIXED_SESSION="multiagent"
FIXED_SESSION_OK=false
if tmux has-session -t "=${FIXED_SESSION}" 2>/dev/null; then
    FIXED_SESSION_OK=true
fi
for i in "${!MAINPC_AGENTS[@]}"; do
    agent="${MAINPC_AGENTS[$i]}"
    pane_idx=$((PANE_BASE + i))
    pane_target=""
    forced_rc=""
    rc_res=0
    pane_target=$(km_pane_id_by_agent_id "$agent" 2>/dev/null) || rc_res=$?
    if [[ "$rc_res" -eq 0 ]]; then
        N_BYID=$((N_BYID + 1))
    elif [[ "$rc_res" -eq 3 ]]; then
        # ★二件以上★ = 当てれば別席を撃ち得る ∴ 的を作らぬ（曖昧の顔で刷る）
        N_AMBIG=$((N_AMBIG + 1)); pane_target=""; forced_rc=3
    else
        pane_target=""
        if $FIXED_SESSION_OK; then
            # session が★完全一致で在る★時のみ寫像を使ふ。index の実在も列挙で検める
            # （display-message の rc は不在を判じられぬ ―― 上の実測⑵）
            pane_target=$(tmux list-panes -a -F '#{session_name} #{window_name} #{pane_index} #{pane_id}' 2>/dev/null \\
                | awk -v s="$FIXED_SESSION" -v x="$pane_idx" '$1==s && $2=="agents" && $3==x {print $4; exit}') || true
            if [[ -z "$pane_target" ]]; then
                N_NOPANE=$((N_NOPANE + 1))
            fi
        else
            N_NOSESS=$((N_NOSESS + 1))
        fi
    fi
    print_agent_row "$agent" "$pane_target" "$forced_rc"
done''', "㋔本疵")

# ── ㋕ 結語へ的の度數を足す ──
rep(''' ／ 箱: 数に非ざる顔=%d\\n' \\
    "$N_SEKI" "$N_YOMETA" "$N_NOTAMA" "$N_NOFILE" "$N_PARSE_NG" \\
    "$N_SHAPE" "$N_READERR" "$N_NOPY" "$N_PYDIE" "$N_MULTI" "$N_BOX_NG" >&2''',
''' ／ 箱: 数に非ざる顔=%d ／ 的: @agent_idで解けた=%d ★曖昧=%d★ 寫像不能(session無)=%d 寫像不能(pane無)=%d\\n' \\
    "$N_SEKI" "$N_YOMETA" "$N_NOTAMA" "$N_NOFILE" "$N_PARSE_NG" \\
    "$N_SHAPE" "$N_READERR" "$N_NOPY" "$N_PYDIE" "$N_MULTI" "$N_BOX_NG" \\
    "$N_BYID" "$N_AMBIG" "$N_NOSESS" "$N_NOPANE" >&2''', "㋕結語")

rep('''if [[ $((N_PARSE_NG + N_SHAPE + N_READERR + N_PYDIE + N_MULTI + N_BOX_NG)) -gt 0 ]]; then
    printf '[agent_status] ★黙らぬ★ 上の顔は「弾が無い」ではない。★帳が読めて居らぬ★。\\n' >&2
fi''',
'''if [[ $((N_PARSE_NG + N_SHAPE + N_READERR + N_PYDIE + N_MULTI + N_BOX_NG)) -gt 0 ]]; then
    printf '[agent_status] ★黙らぬ★ 上の顔は「弾が無い」ではない。★帳が読めて居らぬ★。\\n' >&2
fi
if [[ "$N_AMBIG" -gt 0 ]]; then
    printf '[agent_status] ★黙らぬ★ @agent_id が二席以上に在る席が %d ―― 当てれば別席を撃ち得る ∴ ★当てなかつた★。\\n' "$N_AMBIG" >&2
fi''', "㋕黙らぬ")

io.open(F, "w", encoding="utf-8").write(s)
sha1 = hashlib.sha256(s.encode()).hexdigest()
print("後 sha256=%s 行=%d byte=%d" % (sha1, s.count("\n"), len(s.encode())))
print("★前方一致の的が残つて居らぬかの検算★")
for bad in ['pane_target="multiagent:agents.', '-t multiagent', '-t "multiagent']:
    print("  残 %-34s = %d" % (bad, s.count(bad)))

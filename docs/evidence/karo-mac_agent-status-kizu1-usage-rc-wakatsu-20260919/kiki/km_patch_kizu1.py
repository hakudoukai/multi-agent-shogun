# -*- coding: utf-8 -*-
"""km_patch_kizu1.py ―― 裁337507⑶疵① を据ゑる器（家老mac・2026-09-19）

★何を直すか★
  ⑴ `--lang/--session/--panes` に値が無い時、bash の内部診断
     (`line 28: $2: unbound variable`) で死んで居た ―― usage で閉ぢる。
  ⑵ 出目を分ける: ★使ひ方の誤=1 / 器の死=2★（裁337507⑶疵① 逐語）。
  ⑶ 併せ、値が★空★・値が★旗に見える★形の★静かな失敗★を閉ぢる
     （実測: `--session ""` は黙つて現用 session へ倒れ、`--lang --session` は
       値を食はれて project 路へ倒れた。悉く rc=0）。
  ⑷ ★器の死★ の門を二つ入口に立てる: tmux が機に無い / 共用 lib が読めぬ。

★作法★ str.replace は必ず count を assert する（黙つて据ゑぬのを防ぐ）。
"""
import io, sys, hashlib

P = sys.argv[1]
src = io.open(P, encoding="utf-8").read()
before_sha = hashlib.sha256(src.encode()).hexdigest()
src_orig = src
n_done = 0

def rep(a, b, want=1):
    global src, n_done
    c = src.count(a)
    assert c == want, "REFUSE 当たり %d 件（%d を期す）: %r" % (c, want, a[:60])
    src = src.replace(a, b)
    n_done += 1

# ─── ⑴ 出目の規律 + usage + 値の検め を Parse args の前へ置く ───
A1 = "# ─── Parse args ───\n"
B1 = '''# ─── ★出目の規律★（委員長裁 seq337507⑶疵①「usage で閉ぢ rc を分けよ」）───
#   rc=0 … 測れた（`--help` も 0）
#   rc=1 … ★使ひ方の誤★ = 呼び手の argv が誤つて居る
#           （未知の旗 / 値を取る旗に値が無い / 値が空 / 値が旗に見える /
#             session 名が当たらぬ / --panes に該当無 / tmux 外で --session 無し）
#   rc=2 … ★器の死★ = 呼び手に非は無く、機に走る物が無い
#           （tmux が機に無い / 共用 lib が読めぬ）
# ★据ゑる前の実測★(docs/evidence/karo-mac_agent-status-kizu1-usage-rc-wakatsu-20260919/raw/50_before.txt):
#   ㋓㋔㋕ 値が無いと `line 28: $2: unbound variable` が出て rc=1 ―― usage は出ぬ。
#   ㋙ 未知の旗も rc=1 ∴ ★呼び手の誤りと器の死が同じ出目に潰れて居た★。
#   ㋖ `--lang ""`      → rc=0（黙つて空の言語）
#   ㋗ `--session ""`   → rc=0（★黙つて現用 session へ倒れた★＝別の物を測る）
#   ㋘ `--lang --session` → rc=0（値を食はれ project 路へ倒れた）
readonly KM_RC_OK=0
readonly KM_RC_USAGE=1
readonly KM_RC_KIKI=2

# ★使ひ方★ ―― 誤りは stderr へ、`--help` は stdout へ（$1 = 1 か 2）
km_usage() {
    local fd="${1:-1}"
    {
        echo "Usage: agent_status.sh [--session NAME] [--panes 0,1,2] [--lang en|ja]"
        echo ""
        echo "Options:"
        echo "  --session NAME   Tmux session to scan (default: auto-detect)"
        echo "  --panes N,N,N    Comma-separated pane indices to check"
        echo "  --lang en|ja     Output language (default: ja)"
        echo ""
        echo "Without options, reads config/settings.yaml for agent definitions."
        echo ""
        echo "Exit codes:"
        echo "  0  measured"
        echo "  ${KM_RC_USAGE}  usage error: unknown flag / missing or empty value / no such session"
        echo "  ${KM_RC_KIKI}  instrument unusable: tmux absent / shared lib unreadable"
    } >&"$fd"
}

# ★値を取る旗を検める★ ―― 値が無い時に $2 を触つてはならぬ（set -u で shell が死ぬ）
#   $1=旗の名 / $2=残りの引数の数($#) / $3=次の語（無ければ空）
km_need_value() {
    local flag="$1" argc="$2" nxt="${3-}"
    if [[ "$argc" -lt 2 ]]; then
        echo "Error: ${flag} は値を要るが、値が無い" >&2
        km_usage 2
        return 1
    fi
    if [[ -z "$nxt" ]]; then
        echo "Error: ${flag} の値が空である（黙つて既定へ倒さぬ）" >&2
        km_usage 2
        return 1
    fi
    case "$nxt" in
        --*)
            echo "Error: ${flag} の値が旗に見える（'${nxt}'）―― 値を落として居らぬか" >&2
            km_usage 2
            return 1
            ;;
    esac
    return 0
}

# ─── Parse args ───
'''
rep(A1, B1)

# ─── ⑵ case の腕 を据ゑ替へる ───
A2 = '''        --lang)    LANG_MODE="$2"; shift 2 ;;
        --session) SESSION_NAME="$2"; STANDALONE=true; shift 2 ;;
        --panes)   MANUAL_PANES="$2"; STANDALONE=true; shift 2 ;;
        --help|-h)
            echo "Usage: agent_status.sh [--session NAME] [--panes 0,1,2] [--lang en|ja]"
            echo ""
            echo "Options:"
            echo "  --session NAME   Tmux session to scan (default: auto-detect)"
            echo "  --panes N,N,N    Comma-separated pane indices to check"
            echo "  --lang en|ja     Output language (default: ja)"
            echo ""
            echo "Without options, reads config/settings.yaml for agent definitions."
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
'''
B2 = '''        --lang)
            km_need_value --lang "$#" "${2-}" || exit "$KM_RC_USAGE"
            LANG_MODE="$2"; shift 2 ;;
        --session)
            km_need_value --session "$#" "${2-}" || exit "$KM_RC_USAGE"
            SESSION_NAME="$2"; STANDALONE=true; shift 2 ;;
        --panes)
            km_need_value --panes "$#" "${2-}" || exit "$KM_RC_USAGE"
            MANUAL_PANES="$2"; STANDALONE=true; shift 2 ;;
        --help|-h)
            km_usage 1
            exit "$KM_RC_OK"
            ;;
        *)
            # ★誤りは stderr へ★（旧形は stdout へ出して居た＝出を集める器が黙つて呑む）
            echo "Error: 未知の旗: $1" >&2
            km_usage 2
            exit "$KM_RC_USAGE"
            ;;
'''
rep(A2, B2)

# ─── ⑶ 器の死 の門 二つ を lib 読込の前へ ───
A3 = '''# ─── Load shared library ───
source "$SCRIPT_DIR/lib/agent_status.sh"
source "$SCRIPT_DIR/lib/_section18_roles.sh"
'''
B3 = '''# ─── ★器の死★ 其の一: tmux が機に無い（裁337507⑶疵①「器の死=2」）───
# 実測(raw/51_tmux_fuzai_project.txt ―― tmux のみを PATH から抜いた・据ゑる前):
#   ⑴ standalone 路 → rc=1「session 'multiagent-mac' は完全一致で存在せぬ」＝★偽の因★
#      （session は在る。無いのは器である。呼び手の argv を咎めて居た）
#   ⑵ project 路    → ★rc=0★ で表を刷る。表の中身は正直（Pane=不在・Status=---・
#      母數行が「的: @agent_idで解けた=0 / 寫像不能(session無)=6」と宣す）が、
#      ★何一つ測れて居らぬのに「通」を返す★。rc だけを読む呼び手は「正常」と解す。
# ∴ 門を入口に立て rc=2 で止める。★此処は 2>/dev/null で呑まぬ★。
if ! command -v tmux >/dev/null 2>&1; then
    echo "Error: tmux が機に無い ―― 本器は tmux の pane を測る物ゆゑ何も測れぬ" >&2
    echo "       （呼び手の誤りではない。rc=${KM_RC_KIKI} ＝ 器の死）" >&2
    exit "$KM_RC_KIKI"
fi

# ─── ★器の死★ 其の二: 共用 lib が読めぬ ───
# 旧形は `source` が失敗すると set -e で rc=1 ＝★使ひ方の誤と同じ顔★に成つて居た。
for _lib in "$SCRIPT_DIR/lib/agent_status.sh" "$SCRIPT_DIR/lib/_section18_roles.sh"; do
    if [[ ! -r "$_lib" ]]; then
        echo "Error: 共用 lib が読めぬ: ${_lib}" >&2
        echo "       （呼び手の誤りではない。rc=${KM_RC_KIKI} ＝ 器の死）" >&2
        exit "$KM_RC_KIKI"
    fi
done

# ─── Load shared library ───
source "$SCRIPT_DIR/lib/agent_status.sh"
source "$SCRIPT_DIR/lib/_section18_roles.sh"
'''
rep(A3, B3)

# ─── ⑷ 疵② で据ゑた三つの死を「使ひ方の誤」と字で宣す（値は 1 の儘・振舞不変）───
rep('''            echo "Error: not inside a tmux session and --session not specified" >&2
            exit 1
''', '''            echo "Error: not inside a tmux session and --session not specified" >&2
            exit "$KM_RC_USAGE"   # ★使ひ方の誤★（値は旧と同じ 1・振舞は変へぬ）
''')
rep('''        echo "Error: session '${SESSION_NAME}' は完全一致で存在せぬ（前方一致では当てぬ）" >&2
        exit 1
''', '''        echo "Error: session '${SESSION_NAME}' は完全一致で存在せぬ（前方一致では当てぬ）" >&2
        exit "$KM_RC_USAGE"   # ★使ひ方の誤★（値は旧と同じ 1）
''')
rep('''        echo "Error: session '${SESSION_NAME}' に該当する pane が無い（--panes の指定を含む）" >&2
        exit 1
''', '''        echo "Error: session '${SESSION_NAME}' に該当する pane が無い（--panes の指定を含む）" >&2
        exit "$KM_RC_USAGE"   # ★使ひ方の誤★（値は旧と同じ 1）
''')

# ─── ⑸ L196 の註（tmux 無き所で走るのが並）を実装に追随させる ───
rep('''# ★此の 2>/dev/null は外さぬ★（命⑶ 後段・理由）―― tmux が無い所（CI・素の shell）で
# 走る事が設計上の並(standalone mode)であり、其の時の「tmux 無し」は ★既に別の顔★
# （不在 / 0）を持つ。黙つて数を偽る類ではない。下の三つ（session 名・pane 一覧・
# @agent_id）も同じ理由で残す。帳の parse とは別の事である。
''', '''# ★此の 2>/dev/null は外さぬ★（命⑶ 後段・理由）―― 黙つて数を偽る類ではない。
# 下の三つ（session 名・pane 一覧・@agent_id）も同じ理由で残す。帳の parse とは別の事である。
# ★2026-09-19 追随（裁337507⑶疵①）★ ―― 旧註は「tmux が無い所（CI・素の shell）で
# 走る事が設計上の並(standalone mode)」と書いて居たが、★実装が変はつた★:
# tmux 不在は★入口の門で rc=2（器の死）として止まる★（上の km_need_value の下）。
# ∴ 此処へ到る時 tmux は★必ず在る★。此の `|| echo 0` が覆ふのは
# 「tmux は在るが pane-base-index が未設定」の場合★のみ★である。
''')

after_sha = hashlib.sha256(src.encode()).hexdigest()
n_line_b = src_orig.count("\n")          # 行 = 改行の数（末尾に改行が在る形）
n_line_a = src.count("\n")
io.open(P, "w", encoding="utf-8").write(src)
print("据ゑた箇所 = %d" % n_done)
print("sha256 前 = %s" % before_sha)
print("sha256 後 = %s" % after_sha)
print("byte 前後 = %d → %d" % (len(src_orig.encode()), len(src.encode())))
print("行   前後 = %d → %d" % (n_line_b, n_line_a))

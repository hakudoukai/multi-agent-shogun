# -*- coding: utf-8 -*-
"""km_patch_hako.py ―― scripts/agent_status.sh の母數行へ「messages鍵無=N」を常設する彫り器

裁 seq337507⑵ 逐語: 「箱の同型=潜在ゆゑ触れぬが正。但し母數行へ messages鍵無=N を
常設し顕在化を見える形に。」

∴ ★表の顔（行の Inbox 欄）は一切変へぬ★。get_unread_count の出目を二欄
「<顔> <旗>」にして ★一度の歩き★ で旗を持ち帰り、母數行へ常設する（0 でも刷る）。

argv: <据ゑる file>
出目: 据ゑた箇所の数を刷り、一つでも当たらねば ★assert で止まる★（黙つて通さぬ）
"""
import io, sys, hashlib

path = sys.argv[1]
src = io.open(path, encoding="utf-8").read()
sha_before = hashlib.sha256(src.encode("utf-8")).hexdigest()
n = [0]

def rep(a, b, want=1):
    """★字面が want 回 在ることを検めてから彫る★（str.replace は当たらずとも黙る）"""
    c = src_holder[0].count(a)
    assert c == want, "REFUSE 当たり %d 回（want=%d）: %r" % (c, want, a[:60])
    src_holder[0] = src_holder[0].replace(a, b, want)
    n[0] += want

src_holder = [src]

# ─── ㋐ 度數の宣言（★0 でも刷る為 ここで宣す★）───
rep(
"""N_NOPY=0; N_SHAPE=0; N_READERR=0; N_PYDIE=0; N_BOX_NG=0; N_MULTI=0""",
"""N_NOPY=0; N_SHAPE=0; N_READERR=0; N_PYDIE=0; N_BOX_NG=0; N_MULTI=0
# ─── 箱の★潜在★の顔（委員長裁 seq337507⑵）───
# `data.get('messages', [])` は ★messages 鍵の無い箱★ と ★空の箱★ を同型にする。
# 表の顔は双方 0 ゆゑ「未読が無い」と読まれる ―― 実は ★測れて居らぬ★。
# 裁は「触れぬが正・但し母數行へ常設」ゆゑ ★表は変へず★ 母數行で顕在化させる（0 でも刷る）。
N_BOX_NOKEY=0; N_BOX_KARA=0""")

# ─── ㋑ 箱の顔の凡例（二欄である事を註に書く）───
rep(
"""    # ★2>/dev/null を外した★（命⑶）。箱の顔: -=箱無 !=parse不能 S=形違 E=讀めぬ P=器無 X=器落""",
"""    # ★2>/dev/null を外した★（命⑶）。箱の顔: -=箱無 !=parse不能 S=形違 E=讀めぬ P=器無 X=器落
    # ★出目は二欄「<顔> <旗>」★（裁337507⑵）。旗 = k:messages鍵在 / n:★鍵無 dict★ /
    #   e:空帳(None ゆゑ鍵も無い) / -:判ぜず。★表に刷るのは顔だけ★ ―― 旗は母數行の為に持ち帰る
    #   （箱を二度歩かぬ＝一度の歩きで済ませる）。""")

# ─── ㋒ 器無・箱無も二欄で返す ───
rep(
"""    if ! $PYTHON_AVAILABLE; then
        echo "P"
        return
    fi
    if [[ ! -f "$inbox_file" ]]; then
        echo "-"
        return
    fi""",
"""    if ! $PYTHON_AVAILABLE; then
        echo "P -"
        return
    fi
    if [[ ! -f "$inbox_file" ]]; then
        echo "- -"
        return
    fi""")

# ─── ㋓ parse 不能 / 讀めぬ ───
rep("""    print('!'); sys.exit(0)""", """    print('! -'); sys.exit(0)""")
rep("""    print('E'); sys.exit(0)""", """    print('E -'); sys.exit(0)""")

# ─── ㋔ 空帳（None）―― ★鍵も無い★ ゆゑ旗 e ───
rep(
"""if data is None:
    print(0); sys.exit(0)""",
"""if data is None:
    sys.stderr.write('[agent_status] no-key %s: 空帳ゆゑ messages 鍵も無い ―― 顔は 0 だが「未読が無い」ではない\\n' % p)
    print('0 e'); sys.exit(0)""")

# ─── ㋕ 形違（頂が dict でない）は旗を判ぜず ───
rep(
"""    print('S'); sys.exit(0)
msgs = data.get('messages', [])
if not isinstance(msgs, list):""",
"""    print('S -'); sys.exit(0)
if 'messages' not in data:
    sys.stderr.write('[agent_status] no-key %s: messages 鍵が無い ―― 顔は 0 だが「未読が無い」ではない\\n' % p)
    print('0 n'); sys.exit(0)
msgs = data['messages']
if not isinstance(msgs, list):""")

# ─── ㋖ messages が list でない ―― ★鍵は在る★ ゆゑ旗 k ───
rep(
"""    print('S'); sys.exit(0)
print(sum(1 for m in msgs if isinstance(m, dict) and not m.get('read', False)))""",
"""    print('S k'); sys.exit(0)
print('%d k' % sum(1 for m in msgs if isinstance(m, dict) and not m.get('read', False)))""")

# ─── ㋗ 器落 ───
rep("""" || echo "X\"""", """" || echo "X -\"""")

# ─── ㋘ 呼び手 ―― 二欄で受け、★表に刷るのは顔だけ★ ───
rep(
"""    # Unread inbox
    local unread
    unread=$(get_unread_count "$agent")
    case "$unread" in
        "!"|"S"|"E"|"P"|"X") N_BOX_NG=$((N_BOX_NG + 1)) ;;
    esac""",
"""    # Unread inbox ―― 出目は二欄「<顔> <旗>」（裁337507⑵）
    local box_out unread box_flag
    box_out=$(get_unread_count "$agent")
    # bash 3.2 でも読める形（here-string）。欄が落ちたら「判ぜず」へ倒す（黙つて 0 にせぬ）
    read -r unread box_flag <<< "$box_out"
    unread="${unread:--}"
    box_flag="${box_flag:--}"
    case "$unread" in
        "!"|"S"|"E"|"P"|"X") N_BOX_NG=$((N_BOX_NG + 1)) ;;
    esac
    # ★messages 鍵の無い箱を数へる★（空帳は「鍵も無い」ゆゑ内数として両方に立つ）
    case "$box_flag" in
        n) N_BOX_NOKEY=$((N_BOX_NOKEY + 1)) ;;
        e) N_BOX_NOKEY=$((N_BOX_NOKEY + 1)); N_BOX_KARA=$((N_BOX_KARA + 1)) ;;
    esac""")

# ─── ㋙ 結語 ―― 母數行へ★常設★（0 でも刷る）───
rep(
"""／ 箱: 数に非ざる顔=%d ／""",
"""／ 箱: 数に非ざる顔=%d ★messages鍵無=%d★(内 空帳=%d) ／""")
rep(
"""    "$N_SHAPE" "$N_READERR" "$N_NOPY" "$N_PYDIE" "$N_MULTI" "$N_BOX_NG" \\""",
"""    "$N_SHAPE" "$N_READERR" "$N_NOPY" "$N_PYDIE" "$N_MULTI" "$N_BOX_NG" "$N_BOX_NOKEY" "$N_BOX_KARA" \\""")

# ─── ㋚ >0 の時のみ 註一行（★「読めぬ」ではない★ゆゑ黙らぬ の和には入れぬ）───
rep(
"""if [[ "$N_AMBIG" -gt 0 ]]; then""",
"""if [[ "$N_BOX_NOKEY" -gt 0 ]]; then
    # ★「読めぬ」ではない★ ―― 帳は読めて居る。読めた上で ★0 と区別が付かぬ★ のである。
    # ∴ 上の★黙らぬ★（parse不能等の和）には入れず、別の註として立てる。
    printf '[agent_status] ★註★ messages 鍵の無い箱=%d（内 空帳=%d）―― 表の顔は 0 と刷るが「未読が無い」ではない。★0 と区別が付かぬ★。\\n' \\
        "$N_BOX_NOKEY" "$N_BOX_KARA" >&2
fi
if [[ "$N_AMBIG" -gt 0 ]]; then""")

out = src_holder[0]
assert out != src
io.open(path, "w", encoding="utf-8").write(out)
print("据ゑた箇所 = %d" % n[0])
print("sha256 前 = %s" % sha_before)
print("sha256 後 = %s" % hashlib.sha256(out.encode("utf-8")).hexdigest())
print("byte %d → %d / 行 %d → %d" % (len(src.encode("utf-8")), len(out.encode("utf-8")),
                                     src.count("\n"), out.count("\n")))

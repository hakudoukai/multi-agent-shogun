#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問一 ―― scripts/stop_hook_inbox.sh の「註 ⇔ 實装」を ★帯★ で測る器。

★此の器は的を走らせぬ。★ 開いて ★字★ を讀むのみ(札 問一「据ゑ替へるな・走らせるな」)。
∴ 出す數は「實行の觀測」ではなく ★字から導いた模型の出目★ である ―― 其の旨を毎回刷る。

形:
  ㋐ 註が宣る条件 ―― 行番号 + ★逐語★
  ㋑ 實装が分岐する条件 ―― 行番号 + ★逐語★
  ㋒ 未讀數 n を 0 / 1〜5 / 6以上 の三帯に分け、註の宣と實装の出目を並べる
  ㋓ 閾 MASS_UNREAD_THRESHOLD の既定値と env 上書き

★錨の検め(guard)★: 模型が寄る行の逐語が食ひ違へば ★何も刷らずに rc=3 で落ちる★。
  (法「A guard that only measures is not a guard」―― 測るだけの器は番人ではない)
"""
import hashlib
import os
import subprocess
import sys

TARGET = "scripts/stop_hook_inbox.sh"

# ★模型が寄る錨★ = (行番号, 其の行に ★含まれて居らねばならぬ★ 字)
ANCHORS = [
    (68, "Allow it to stop this time to prevent loops."),
    (70, 'if [ "$STOP_HOOK_ACTIVE" = "True" ]; then'),
    (71, "Agent is going idle (exit 0) regardless of unread count."),
    (93, "UNREAD_COUNT=$(grep -cE '^  read: false$' \"$INBOX\" 2>/dev/null || true)"),
    (94, 'if [ "${UNREAD_COUNT:-0}" -eq 0 ]; then'),
    (95, "exit 0"),
    (97, "fall through to block response"),
    (140, "UNREAD_COUNT=$(grep -cE '^  read: false$' \"$INBOX\" 2>/dev/null || true)"),
    (146, "MASS_UNREAD_THRESHOLD=${MASS_UNREAD_THRESHOLD:-5}"),
    (147, 'if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then'),
    (151, "exit 0"),
    (155, 'if [ "${UNREAD_COUNT:-0}" -eq 0 ]; then'),
    (175, "exit 0"),
    (220, "print(json.dumps({'decision': 'block'"),
]


def main():
    if not os.path.isfile(TARGET):
        sys.stderr.write("★的が無い: %s★ ―― 「無い」は path を宣して言ふ\n" % TARGET)
        return 2
    raw = open(TARGET, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    lines = raw.decode("utf-8").split("\n")   # 1-origin で引く為に後で +1
    nlines = len(lines) - (1 if raw.endswith(b"\n") else 0)

    # ―― 錨の検め(先に落とす) ――
    bad = []
    for ln, must in ANCHORS:
        got = lines[ln - 1] if 0 < ln <= len(lines) else "<行が無い>"
        if must not in got:
            bad.append((ln, must, got))
    if bad:
        sys.stderr.write("★錨が食ひ違ふ ―― 模型は此の版に当たらぬ。數を出さぬ(fail-closed)★\n")
        for ln, must, got in bad:
            sys.stderr.write("  L%-4d 期待に含む字=%r\n        實の行   =%r\n" % (ln, must, got))
        return 3

    print("的 path=%s sha256=%s bytes=%d lines=%d" % (TARGET, sha, len(raw), nlines))
    print("測り方 = ★開いて字を讀んだのみ。走らせて居らぬ。★ ∴ 下の出目は ★模型★ である。")
    print("")

    print("【㊀ ㋐ 註が宣る条件 ―― 逐語】")
    for ln in (66, 67, 68, 71, 72, 73, 74, 97):
        print("  L%-4d| %s" % (ln, lines[ln - 1]))
    print("  ★註の内で ★宣★ に当たるは L71 の一文★ ―― 「regardless of unread count」。")
    print("  ★同じ file の L97 は ★逆★ を宣る ―― 「未読あり → fall through to block response」。")
    print("  ∴ 食ひ違ふは ★註 ⇔ 實装★ のみに非ず。★註 ⇔ 註★ でもある(L71 ⇔ L97)。")
    print("")

    print("【㊀ ㋑ 實装が分岐する条件 ―― 逐語】")
    for ln in (70, 93, 94, 95, 96, 99, 140, 146, 147, 150, 151, 155, 173, 174, 175, 178, 220):
        print("  L%-4d| %s" % (ln, lines[ln - 1]))
    print("")

    # ―― ㋓ 閾 ――
    print("【㊀ ㋓ 閾 MASS_UNREAD_THRESHOLD】")
    print("  L146 逐語 : %s" % lines[145])
    print("  既定値    = 5 ―― `${VAR:-5}` ゆゑ ★未設定でも空文字でも 5★ に倒れる")
    print("  env 上書き= ★可★。hook は Claude Code が起こす子 process ゆゑ、")
    print("              親の環境に MASS_UNREAD_THRESHOLD が在れば其れが勝つ。")
    print("  ★註★ 非數(例 'abc')を入れた時の振舞ひは ★別の器で測る(20_)★ ―― 此処では宣らぬ。")
    print("")

    # ―― ㋒ 帯 ――
    print("【㊀ ㋒ 帯 ―― 未讀數 n に對する 註の宣 ⇔ 實装の出目】")
    print("  ★模型の前提(三つ。崩れれば出目も崩れる)★")
    print("   前提1: stop_hook_active=True の枝に入つて居る(L70 が真)。L71 の宣は此の枝の物ゆゑ。")
    print("   前提2: L93 で數へた n と L140 で數へ直した n が ★同じ★。")
    print("          ★箱は測る間にも育つ(法「The box grows while you measure it」)★ ∴ 之は前提であつて事実ではない。")
    print("          食ひ違へば出目は ★L140 の値★ に従ふ。")
    print("   前提3: 中途で exit する枝(L132 `[ ! -f $INBOX ]` 等)に落ちて居らぬ。")
    print("")
    hdr = "  %-8s | %-26s | %-34s | %s" % ("n(未讀)", "註 L71 の宣", "實装の出目(行で示す)", "一致/★食ひ違ひ★")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    rows = []
    for n in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        decl = "exit 0(idle へ)"
        if n == 0:
            impl, where = "exit 0", "L94 真 → L95"
        elif n <= 5:
            impl, where = "★block★", "L94 偽 → 落ちて L147 偽 → L155 偽 → L220"
        else:
            impl, where = "exit 0", "L94 偽 → 落ちて L147 ★真★ → L151"
        agree = "一致" if impl == "exit 0" else "★食ひ違ひ★"
        rows.append((n, impl, agree))
        print("  %-8s | %-26s | %-34s | %s" % (n, decl, where, agree))
    print("")
    agree_set = [n for n, impl, a in rows if a == "一致"]
    dis_set = [n for n, impl, a in rows if a != "一致"]
    print("  ★一致する n★     = {0} ∪ {6,7,8,…} ―― 測つた範囲では %s" % agree_set)
    print("  ★食ひ違ふ n★     = %s ―― ★閉區間 [1,5]★" % dis_set)
    print("  ★∴ 註と實装が食ひ違ふのは ★帯 1〜5 のみ★。0 でも 6 以上でも食ひ違はぬ。★")
    print("  ★∴ 「未讀 1 件で ★無限に★ 塞がれる」は ★言ひ過ぎ★ ―― 塞がるのは帯である(家老の裁が正)。★")
    print("  ★然れど 6 以上で一致するのは ★同じ理由で★ ではない★ ――")
    print("      n=0 は L71 の宣ふ通りの道(同じ枝)、n>=6 は ★別の番人(L147 mass-unread guard)★ が")
    print("      偶々同じ出目へ倒した物。★出目が同じでも理由が違ふ ∴ 片方が消えれば食ひ違ひは 6 以上へ延びる。★")
    print("")

    # ―― 待ちの器の在否(此の席で) ――
    rc = subprocess.run(["/usr/bin/which", "inotifywait"], capture_output=True)
    have = rc.returncode == 0
    print("【㊀ 付 ―― 帯 1〜5 に落ちた時、此の席では ★間が空かぬ★】")
    print("  L84/L164 `command -v inotifywait` ―― 此の機(darwin)での在否 = %s (which rc=%d)"
          % ("★在り★" if have else "★無し★", rc.returncode))
    if not have:
        print("  ∴ L85-88 と L165-167 の ★10 秒の待ち★ は ★一度も起きぬ★。")
        print("  ∴ 帯 1〜5 で block → 再発火 → また block の輪は ★待ち無しで回る★。")
        print("  ★註★ 之は『輪が無限』の証ではない ―― 席が未讀を落とせば輪は止む。")
        print("      測つたのは ★輪一周に間が無い★ 事のみ。")
    print("")
    print("★此の器の出目は模型である。實行の觀測ではない。★ 的 sha256=%s" % sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())

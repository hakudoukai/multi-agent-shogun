#!/usr/bin/env python3
"""karo_mac_manifest_verify.py ―― 台帳(manifest)の全件照合。

由来: 2026-09-09。家老mac が同じ照合を ★その場限りの sed/awk で七度 書き直し★、
      七度とも 別の形で落ちた(0/0・実体無 11・実体無 19・無 5 …)。
      ★席ごとに台帳の書き方が違ふ★ のが因で、席に落度は無い。

      ★同じ物を測る器は 一本に据ゑよ。書き直す度に 新しい壊れ方が生まれる。★

受ける形(実測で見た全て):
    path=<p> sha256=<64>
    path=<p>  sha256=<64> bytes=.. lines=..
    <p> sha256=<64> bytes=.. lines=..
    <label> = <p> sha256=<64>        (例: registry = frontend/...)

    ★台帳の書き手への條(委員長裁 seq321127⑵ / 321257)★
      ・★宣は要★ ―― どの本形で書いたかを臺帳の頭に明示せよ(落ち防止ではなく読み手の判別用)
      ・★引用符は禁(新規に書く行のみ)★ ―― 一重も二重も禁(C形は3器全損の実測)
      ・★既存行は拒まぬ★ ―― 引用符を含む既存行は ★旧形★ として通し、件数のみ報せる
        (委員長裁 seq321353⑴ 逐語:「引用符禁は★新規に書く行★にのみ適用＝既存行は拒否せず
         『旧形』札で通し件数を報せる」)
    # で始まる行は註(基点の宣言など)ゆゑ数へぬ。

基点は複数試す(repo が跨る為・a2 の B5-3 が実例)。

usage: karo_mac_manifest_verify.py <manifest> [base ...]
出力  : 一致/相違/実体無/読めぬ行 の数と、その名
rc    : 0=全件一致 / 1=相違・実体無・読めぬ行 のいずれか / 2=器の誤り

★2026-09-10 是正(総監督 裁 seq298712 ②)★:
    旧版は ★path 候補が一つも取れぬ行★ を「実体無」に数へた。
    然れど「実体無」は『path は読めたが disk に物が無い』の意であり、
    『行そのものが読めぬ』とは別事である ―― ★診立てが人を誤らせる。★
    実害: 2026-09-10 家老mac が自作の台帳を ★裸の file 名★ で書き、
          「一致 0 / 実体無 3」と出た。真因は『行が読めぬ』であつたに
          もかかはらず、家老は disk を疑ひ 半刻を費した。
    ∴ ★読めぬ行★ を第四の数として分けた。器は path 候補を
      「'/' を含む語」でしか取らぬ ―― 裸の file 名は ./ を冠して書け。
"""
import hashlib
import os
import re
import sys

SHA = re.compile(r"sha256=([0-9a-f]{64})")


def paths_of(line: str):
    r"""1 行から path 候補を取り出す。順に試す。

    ★2026-09-12 止血(総監督裁 seq307881/307874 ⑵)★:
        旧版は ``path=(\S+)`` の一本しか持たず、★名に空白が在ると其處で切り落した★。
        切り落した儘 disk に問ふ故、出目は「実体無」となり ★盤を責めた★。
        (實測 2026-09-12: 名に空白二つの一本を 素/quote/CRLF の三綴りで載せた臺帳、
         三枚悉く「一致 0 / 実体無 1」。紙は byte 正であつた。)
        ∴ ⑴照合の前に ``\r`` を剥ぎ ⑵quote された名を受け ⑶非貪欲で空白を許す。
        可逆: 此の函數を控(…bak-20260912-shiketsu-failopen)へ戻せば旧挙動。
    """
    def _dequote(t):
        t = t.strip()
        if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
            t = t[1:-1]          # ★旧形★の括りを剥ぐ(拒まぬ為・裁321353⑴)
        return t

    out = []
    line = line.replace("\r", "")          # ★照合の前に \r を剥ぐ★(CRLF の臺帳を LF と同じに読む)
    # ★案甲-鎖★ 順＝②①③・鎖(if-not-m 連鎖＝候補は一つ)
    m = re.search(r"(?:^|\s)path=(.+?)[ \t]+sha256=", line)  # ②非貪欲
    if not m:
        m = re.search(r'(?:^|\s)path=([^\s"\']+)', line)  # ①本形
    if not m:
        m = re.search(r"(?:^|\s)path=(\S+)", line)  # ③従来形
    if m:
        out.append(_dequote(m.group(1)))
    # '=' の右・sha256 でない・'/' を含む語
    for tok in line.split():
        if tok.startswith("sha256=") or tok.startswith("bytes=") or tok.startswith("lines="):
            continue
        t = tok.split("=", 1)[-1] if tok.startswith("path=") else tok
        t = _dequote(t)
        if "/" in t and t not in out:
            out.append(t)
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    man = argv[1]
    # ★2026-09-12 止血(総監督裁 seq307881/307874 ⑴ ―― default-deny 側へ揃へる)★
    #   旧版の既定基点は第一に ★""(= cwd 相対)★ であつた。故に ★同じ臺帳・同じ刻でも
    #   立つて居る場所で出目が変つた★ ―― 實測: repo 根 rc=1「出すな」/ fixtures 配下 rc=0「出してよい」。
    #   ★赤→青 の向きに開く(fail-open)★。
    #   ∴ 既定基点を ★器自身の在處から導いた repo 根★(cwd に依らぬ)へ据ゑる。
    #   引数で基点を渡した時は其れを尊ぶ(従来通り・明示は cwd 相対で宜しい)。
    #   可逆: 此の三行を控へ戻せば旧挙動。
    if argv[2:]:
        bases = argv[2:]
        base_src = "引数(明示)"
    else:
        _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bases = [_root + os.sep,
                 os.path.join(_root, "queue", "reports") + os.sep,
                 "/Users/momizimac/DentalBI/.claude/worktrees/dino-story-engine/"]
        base_src = "既定(器の在處から導いた repo 根 %s ―― ★cwd に依らぬ★)" % _root
    if not os.path.isfile(man):
        print(f"★台帳が無い: {man}★", file=sys.stderr)
        return 2

    ok = ng = miss = unreadable = 0
    kyuukei = 0          # ★旧形★(引用符を含む既存行・拒まず通す)
    kyuu_rows = []
    bad = []
    for raw in open(man, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # ★2026-09-17 委員長裁 seq321353⑴ ―― 引用符禁は ★新規に書く行のみ★★
        #   逐語:「引用符禁は★新規に書く行★にのみ適用＝既存行は拒否せず『旧形』札で
        #   通し件数を報せる(既存台帳を一斉に赤にするのは器の目的=新しい落ちの防止に反する)」
        #   ★之は拒まぬ★ ―― 数へて報せる丈である(守りではなく数へ)。新規の落ち防止は
        #   頭註の條(書き手への申し渡し)が担ふ。
        #   ★前版(裁321257)は此処で拒んでゐた★ ―― 実測 962/4445本・17650/74452行が赤に
        #   なる為、委員長が改めた。前版の控 = …/karo_mac_manifest_verify.py.after321257
        #   ★戻し方(一手)★ cp -p docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/\
        #     karo_mac_manifest_verify.py.before scripts/checks/karo_mac_manifest_verify.py
        if '"' in line or "'" in line:
            kyuukei += 1
            kyuu_rows.append(line[:100])
            # ★continue せぬ★ ―― 旧形も照合へ進める(拒まぬ)
        m = SHA.search(line)
        if not m:
            continue
        want = m.group(1)
        cands = paths_of(line)
        if not cands:
            # ★「実体無」と混ぜるな★ ―― path 候補が一本も取れて居らぬ。
            #   disk を疑ふ前に ★台帳の行の書き方★ を疑へ。
            unreadable += 1
            bad.append(("読めぬ行", line[:100]))
            continue
        found = None
        for p in cands:
            for b in bases:
                cand = os.path.join(b, p) if b else p
                if os.path.isfile(cand):
                    found = (p, cand)
                    break
            if found:
                break
        if not found:
            miss += 1
            bad.append(("実体無", cands[0][:100]))
            continue
        p, cand = found
        got = hashlib.sha256(open(cand, "rb").read()).hexdigest()
        if got == want:
            ok += 1
        else:
            ng += 1
            bad.append(("相違", p))

    print(f"台帳 {man}")
    # ★數は「何處から測つたか」を伴はねば讀めぬ★(裁 seq307874⑴ の教へ)
    print(f"  cwd  {os.getcwd()}")
    print(f"  基点 {base_src}")
    print(f"  一致 ★{ok}★ / 相違 {ng} / 実体無 {miss} / 読めぬ行 {unreadable}"
          f"  (母數 {ok + ng + miss + unreadable})")
    print(f"  ★旧形(引用符を含む行)★ {kyuukei} 行 ―― ★拒んで居らぬ★(裁 seq321353⑴)")
    if kyuukei:
        print("  ★註★ 旧形は ★通した★ ―― 上の 母數 に含まれ、rc を赤にせぬ。")
        print("       ★新規に書く行では引用符を用ゐるな★(頭註の條)。既存行の書き換へは求めぬ。")
        for r in kyuu_rows[:5]:
            print(f"    ★旧形★ {r}")
        if len(kyuu_rows) > 5:
            print(f"    … 他 {len(kyuu_rows) - 5} 行(母數 {kyuukei})")
    if unreadable:
        print("  ★註★ ★読めぬ行★ は ★実体無 とは別事★ ―― ★disk を疑ふな。行を疑へ。★")
        print("       器が path と看做すは ★'/' を含む語★ のみ。裸の file 名は取れぬ。")
        print("       直し方: 台帳の path に ★./ を冠す★ か、基点を第二引数で渡せ。")
    if miss:
        print("  ★註★ ★実体無★ は ★『disk に物が無い』とは限らぬ★ ―― ★基点(場所)が違ふ★ 事が在る。")
        print("       上の『基点』行を先に読み、次に ★臺帳を作つた樹の根★ で当て直せ。")
    if ng:
        # ★相違 は「疵」とは限らぬ ―― 版 が違ふ丈 の事 が在る(2026-09-09 実例)。
        #   a2 の B5-5 で 家老 が 枝 の樹 で当て 相違 1 を得たが、
        #   a2 が紙 に名指した版(bcc1d3626)で当てれば ★逐語 一致★ で あつた。
        #   ★台帳 は「何處 の物 か」を持つが「何時 の版 か」は 器 が知らぬ。★
        print("  ★註★ 相違 は ★疵 とは限らぬ★ ―― ★測る樹 の版 が 台帳 を作つた時 と違ふ★ 事 が在る。")
        print("       断ずる前 に ⑴紙 に書かれた版 を読み ⑵其の版 で当て直せ。")
        print("       例: git show <版>:<path> | shasum -a 256")
    for kind, name in bad[:20]:
        print(f"    ★{kind}★ {name}")
    return 0 if (ng == 0 and miss == 0 and unreadable == 0 and ok > 0) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

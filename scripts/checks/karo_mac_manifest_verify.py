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
    """1 行から path 候補を取り出す。順に試す。"""
    out = []
    m = re.search(r"(?:^|\s)path=(\S+)", line)
    if m:
        out.append(m.group(1))
    # '=' の右・sha256 でない・'/' を含む語
    for tok in line.split():
        if tok.startswith("sha256=") or tok.startswith("bytes=") or tok.startswith("lines="):
            continue
        t = tok.split("=", 1)[-1] if tok.startswith("path=") else tok
        if "/" in t and t not in out:
            out.append(t)
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    man = argv[1]
    bases = argv[2:] or ["", "queue/reports/",
                         "/Users/momizimac/DentalBI/.claude/worktrees/dino-story-engine/"]
    if not os.path.isfile(man):
        print(f"★台帳が無い: {man}★", file=sys.stderr)
        return 2

    ok = ng = miss = unreadable = 0
    bad = []
    for raw in open(man, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
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
    print(f"  一致 ★{ok}★ / 相違 {ng} / 実体無 {miss} / 読めぬ行 {unreadable}"
          f"  (母數 {ok + ng + miss + unreadable})")
    if unreadable:
        print("  ★註★ ★読めぬ行★ は ★実体無 とは別事★ ―― ★disk を疑ふな。行を疑へ。★")
        print("       器が path と看做すは ★'/' を含む語★ のみ。裸の file 名は取れぬ。")
        print("       直し方: 台帳の path に ★./ を冠す★ か、基点を第二引数で渡せ。")
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

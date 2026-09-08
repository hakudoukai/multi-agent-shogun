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
出力  : 一致/相違/実体無 の数と、相違・実体無の名
rc    : 0=全件一致 / 1=相違または実体無 / 2=器の誤り
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

    ok = ng = miss = 0
    bad = []
    for raw in open(man, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = SHA.search(line)
        if not m:
            continue
        want = m.group(1)
        found = None
        for p in paths_of(line):
            for b in bases:
                cand = os.path.join(b, p) if b else p
                if os.path.isfile(cand):
                    found = (p, cand)
                    break
            if found:
                break
        if not found:
            miss += 1
            bad.append(("実体無", line.split()[0][:100]))
            continue
        p, cand = found
        got = hashlib.sha256(open(cand, "rb").read()).hexdigest()
        if got == want:
            ok += 1
        else:
            ng += 1
            bad.append(("相違", p))

    print(f"台帳 {man}")
    print(f"  一致 ★{ok}★ / 相違 {ng} / 実体無 {miss}  (母數 {ok + ng + miss})")
    for kind, name in bad[:20]:
        print(f"    ★{kind}★ {name}")
    return 0 if (ng == 0 and miss == 0 and ok > 0) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

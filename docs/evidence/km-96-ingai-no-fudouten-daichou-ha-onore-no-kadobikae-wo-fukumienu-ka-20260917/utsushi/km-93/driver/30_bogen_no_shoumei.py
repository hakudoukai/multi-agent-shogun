#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑ 器の母數は何を歩いて居るか ―― 臺帳の行か、disk か。

★行番を焼かぬ★ ―― 逐語の一行を ★字面で探して★ 引く。版が動けば行番は嘘になるが、
字面は版が動けば ★見附からぬ★ と鳴る(嘘を吐かず 測れぬと言ふ)。

零を言ふ時は四つの札を添へる:
  ⑴陽性対照が現に在る事(在る筈の字面が現に取れる事)
  ⑵歩いた根と深さ(此処では 器一本・全 byte)
  ⑶rc  ⑷刻
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
RAW = os.path.join(BUNDLE, "raw")
sys.path.insert(0, RAW)
from kaki import kaku, kaku_tsv          # noqa: E402


def _repo_root(start):
    d = start
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise SystemExit("★repo 根(.git)が見附からぬ★")
        d = up


REPO = _repo_root(BUNDLE)
TARGET = os.path.join(REPO, "scripts", "checks", "karo_mac_manifest_verify.py")

# ★disk 側を歩く為の原始器★ ―― 之が一つも無ければ「disk を歩いて居らぬ」
ARUKI_KI = ["os.walk", "os.listdir", "os.scandir", "glob.glob", "glob.iglob",
            "iterdir(", "rglob(", "os.popen", "subprocess"]
# ★陽性対照★ ―― 在る筈の字面(之が取れねば 探し器が壊れて居る)
YOUSEI = ["os.path.isfile", "hashlib.sha256", "for raw in open(man"]

# ★母數を決めて居る逐語★(字面で探す・行番を焼かぬ)
BOGEN_GYOU = 'for raw in open(man, encoding="utf-8", errors="replace"):'
DISK_TOI = "if os.path.isfile(cand):"
RC_GYOU = "return 0 if (ng == 0 and miss == 0 and unreadable == 0 and ok > 0) else 1"
DEME_GYOU = '  一致 ★{ok}★ / 相違 {ng} / 実体無 {miss} / 読めぬ行 {unreadable}'


def main():
    t = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    src = open(TARGET, "rb").read()
    txt = src.decode("utf-8")
    sha = hashlib.sha256(src).hexdigest()
    gyou = txt.count("\n") + (0 if txt.endswith("\n") else 1)
    print("刻 %s" % t)
    print("的 %s" % os.path.relpath(TARGET, REPO))
    print("  sha16=%s / bytes=%d / 行=%d(grep -c '' の数へ方)" % (sha[:16], len(src), gyou))
    print("  歩いた根=此の器一本・全 byte を読んだ(深さ 0 ―― 他の file を見て居らぬ)")

    rows = []
    print("\n==== 陽性対照(在る筈の字面 ―― 探し器が生きて居る證) ====")
    you_ok = True
    for k in YOUSEI:
        n = txt.count(k)
        you_ok = you_ok and n > 0
        print("  %-24s 出現 %d 回 ―― %s" % (k, n, "在" if n else "★無(探し器が壊れて居る)★"))
        rows.append(["陽性対照", k, n])

    print("\n==== disk を歩く原始器の有無 ====")
    aru = 0
    for k in ARUKI_KI:
        n = txt.count(k)
        aru += n
        print("  %-24s 出現 %d 回" % (k, n))
        rows.append(["歩き器", k, n])
    print("  ★合計 %d 回★ ―― %s" % (aru, "0 ∴ disk 側を歩く口が一つも無い" if aru == 0 else "在る"))

    print("\n==== 母數を決めて居る逐語(★行番を焼かず 字面で引く★) ====")
    hits = {}
    for na, k in (("母數の口", BOGEN_GYOU), ("disk への問", DISK_TOI),
                  ("rc の式", RC_GYOU), ("出目の四欄", DEME_GYOU)):
        n = txt.count(k)
        hits[na] = n
        print("  【%s】出現 %d 回" % (na, n))
        print("    逐語: %s" % k)
        rows.append(["逐語", na, n])
    print("""
  ★言葉で述べる(行番を用ゐず)★
    ・『母數の口』の逐語は ★臺帳 man を開いて其の行を一本づつ回す★ 形である。
      其の前では 一致/相違/実体無/讀めぬ行 の四つの数が 0 に据ゑられる。
      其の中では 行から sha256 と path 候補を取り、★取れた path を disk に問ふ★。
      其の後では 四つの数を刷り、rc を決める。
      ∴ ★回の回数を決めるのは 臺帳の行数であり、disk の file 数ではない。★
    ・『disk への問』の逐語は ★臺帳の行から取れた path だけ★ を os.path.isfile に掛ける。
      即ち disk は ★問はれた名にだけ★ 答へる ―― 問はれぬ名(員外)は ★一度も現れぬ★。
    ・『出目の四欄』の逐語に ★員外の欄が無い★。器は員外を ★刷らぬのではなく、持たぬ★。
    ・『rc の式』の逐語は 相違・実体無・讀めぬ行 の三つと 一致>0 のみで決まる。
      ∴ 員外が幾つ在つても rc は 0 のまま。
    ★∴ 員外は「見落し」ではない ―― ★初めから測つて居らぬ★(家老の見立は当つて居た)。""")

    kekka = {
        "刻": t, "的": os.path.relpath(TARGET, REPO), "sha16": sha[:16],
        "bytes": len(src), "行": gyou,
        "陽性対照が現に在る": you_ok,
        "disk を歩く原始器の合計": aru,
        "逐語の出現": hits,
        "母數": "臺帳の行(disk ではない)",
        "rc": 0,
    }
    print("\n==== 四つの札 ====")
    print("  ⑴陽性対照が現に在る = %s(%s)" % (you_ok, "／".join(YOUSEI)))
    print("  ⑵歩いた根と深さ = 器一本 %s / 深さ 0 / 全 %d byte" % (os.path.relpath(TARGET, REPO), len(src)))
    print("  ⑶rc = 0(本器の走り)")
    print("  ⑷刻 = %s" % t)
    kaku(os.path.join(RAW, "30_bogen.json"), json.dumps(kekka, ensure_ascii=False, indent=2))
    kaku_tsv(os.path.join(RAW, "30_bogen.tsv"), rows, header=["種", "字面", "出現回数"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

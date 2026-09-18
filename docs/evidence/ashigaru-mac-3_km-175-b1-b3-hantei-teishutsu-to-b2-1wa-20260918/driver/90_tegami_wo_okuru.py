# -*- coding: utf-8 -*-
"""★便を送る器★(家老令 km-153 ㋓ ―― km-159 の己の疵⑵『便を臺帳凍結後に端末で組んだ』の治め)
使ひ方: python3 -B driver/90_tegami_wo_okuru.py <胴の紙> --to karo|gunshi [--parent-seq N] [--dry]
 ・字を ★送る前に★ 数へ、300 字を超えたら ★送らずに落ちる★(裁の條)。100 字は註(目安)であり條ではない。
 ・rc は subprocess の returncode ―― ★管を通さぬ★。out/err は kaki で書く ∴ ★0byte を作らぬ★(裁 seq310228⑶)。
 ・送つた後 ★胴を読み返す★(第八の番人) ―― DB 便は `sb read seq <N>`、箱便は箱の尾。合はねば落ちる。
 ・控は _letters/ へ、一覧は _letters/90_tegami_choudai.tsv へ ★追記★ する。
四札: 刻=各行 / 根=repo 根 / rc=送り器の returncode / 対照=--dry(送らず字だけ数へる走り)。"""
import os
import re
import sys
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

JOU_JI = 300
CHUU_JI = 100
SB = os.path.expanduser("~/bin/sb-ashigaru-mac-3")
SB_READ = os.path.expanduser("~/bin/sb")

def kazu(s):
    return len(s)

def okuru(doupath, ate, parent=None, dry=False):
    dou = open(doupath, encoding="utf-8").read()
    assert dou.endswith("\n") and not dou.endswith("\n\n"), "★胴の紙は改行丁度1で終はらねばならぬ(門の條④)★"
    dou = dou[:-1]
    assert "\n" not in dou, "★胴は一行で書け(箱の yaml と DB の胴を割らぬ為)★"
    ji = kazu(dou)
    if ji > JOU_JI:
        raise SystemExit("★%d 字 ―― 條の 300 字を超えた。★送らずに止める★(%d 字 截れ)" % (ji, ji - JOU_JI))
    tag = os.path.splitext(os.path.basename(doupath))[0]
    koku = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    if dry:
        print("dry: %s 宛=%s %d 字(條 %d・註 %d)%s" % (tag, ate, ji, JOU_JI, CHUU_JI,
              "" if ji <= CHUU_JI else " ―― 註を超ゆるが條内"))
        return [koku, tag, ate, ji, "dry", "-", "-", "-", "★送つて居らぬ(対照)★"]
    if ate == "gunshi":
        cmd = [SB, "write", "letter", dou, "--to", "gunshi-mac"] + (["--parent-seq", str(parent)] if parent else [])
    elif ate == "karo":
        cmd = ["bash", "scripts/inbox_write.sh", "karo-mac", dou, "report", "ashigaru-mac-3"]
    else:
        raise SystemExit("★宛『%s』を知らぬ ―― 推測して送らぬ★" % ate)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    out = p.stdout.decode("utf-8", "replace"); err = p.stderr.decode("utf-8", "replace")
    for suf, body in (("send.out", out), ("send.err", err), ("send.rc", str(p.returncode) + "\n")):
        kaku(os.path.join(BUNDLE, "_letters", "%s.%s" % (tag, suf)), body)
    # ―― seq を引く(★parent_seq を拾はぬ★ ―― 前に字が続く seq= は除く) ――
    seqs = re.findall(r"(?:^|[^A-Za-z_])seq=(\d+)", out + "\n" + err)
    seq = seqs[-1] if seqs else "-"
    # ―― 第八の番人 ―― 送つた胴を読み返す ――
    itchi = "★読み返して居らぬ★"
    if ate == "gunshi" and seq != "-":
        r = subprocess.run([SB_READ, "read", "seq", seq], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        yomi = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
        kaku(os.path.join(BUNDLE, "_letters", "%s.yomikaeshi.txt" % tag), yomi)
        itchi = "★一致(胴を逐語で確かめた)★" if dou[:60] in yomi else "★食ひ違ひ ―― 胴が違ふ★"
        assert "食ひ違ひ" not in itchi, itchi + "(seq=%s)" % seq
    elif ate == "karo":
        hako = "queue/inbox/karo-mac.yaml"
        body = open(hako, encoding="utf-8", errors="replace").read()
        itchi = "★一致(箱の尾で確かめた)★" if dou[:40] in body else "★箱に見えぬ ―― 送れて居らぬ★"
        kaku(os.path.join(BUNDLE, "_letters", "%s.yomikaeshi.txt" % tag),
             "箱=%s\n胴の頭 40 字が箱に在るか: %s\n箱の寸法=%d byte\n" % (hako, itchi, len(body)))
        assert "見えぬ" not in itchi, itchi
    assert p.returncode == 0, "★送り器 rc=%d ―― 送れて居らぬ★ %s" % (p.returncode, err.strip()[:160])
    return [koku, tag, ate, ji, p.returncode, seq, (str(parent) if parent else "-"),
            hashlib.sha256(dou.encode("utf-8")).hexdigest()[:16], itchi]

def choudai(row):
    p = os.path.join(BUNDLE, "_letters", "90_tegami_choudai.tsv")
    rows = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8").read().split("\n")[1:]:
            if ln.strip():
                rows.append(ln.split("\t"))
    rows.append([str(x) for x in row])
    kaku_tsv(p, rows, header=["刻", "胴の紙", "宛", "字", "送り rc", "seq", "parent_seq", "胴 sha256(16)", "読み返し"])

if __name__ == "__main__":
    a = sys.argv[1:]
    assert a, "使ひ方: 90_tegami_wo_okuru.py <胴の紙> --to karo|gunshi [--parent-seq N] [--dry]"
    dou = a[0]
    ate = a[a.index("--to") + 1] if "--to" in a else None
    par = a[a.index("--parent-seq") + 1] if "--parent-seq" in a else None
    row = okuru(dou, ate, par, dry=("--dry" in a))
    choudai(row)
    print("便: %s 宛=%s %s字 rc=%s seq=%s parent=%s %s" % (row[1], row[2], row[3], row[4], row[5], row[6], row[8]))

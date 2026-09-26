# -*- coding: utf-8 -*-
# km-199 再測（2026-09-26・專任1）―― 己の送つた便を取り戻す路を、今日の器で走らせる。
# ★読むのみ★: ~/bin/sb read（karo_mac_read.py・SELECT のみ）と file の読取だけ。便は出さぬ・板へ書かぬ。
# 各呼出の stdout/stderr/rc を raw/20_calls/ へ一件づつ置く（rc は subprocess から直に取る・管を通さぬ）。
import os, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "20_calls")
SB = os.path.expanduser("~/bin/sb")

CALLS = [
    # (名, argv)
    ("r1_seq_334180", [SB, "read", "seq", "334180"]),
    ("r1_seq_334181", [SB, "read", "seq", "334181"]),
    ("r1_seq_334182", [SB, "read", "seq", "334182"]),
    ("r1_seq_334183", [SB, "read", "seq", "334183"]),
    ("r1_seq_334184", [SB, "read", "seq", "334184"]),
    ("r1_seq_334185", [SB, "read", "seq", "334185"]),
    ("r1_seq_378724", [SB, "read", "seq", "378724"]),
    ("r1_seq_378725", [SB, "read", "seq", "378725"]),
    ("r2_seqs_334180-334185", [SB, "read", "seqs", "334180-334185"]),
    ("r2_seqs_378724,378725", [SB, "read", "seqs", "378724,378725"]),
    ("r3_sent_karo-mac", [SB, "read", "sent", "karo-mac"]),
    ("r3_sent_gunshi-mac", [SB, "read", "sent", "gunshi-mac"]),
    ("r3_sent_iincho", [SB, "read", "sent", "iincho"]),
    ("r4_inbox_20", [SB, "read", "inbox", "20"]),
    ("r4_inbox_200", [SB, "read", "inbox", "200"]),
]


def run(name, argv):
    p = subprocess.run(argv, capture_output=True, text=True)
    for ext, v in (("out", p.stdout), ("err", p.stderr), ("rc", f"{p.returncode}\n")):
        with open(os.path.join(OUT, f"{name}.{ext}"), "w", encoding="utf-8") as f:
            f.write(v)
    print(f"{name} rc={p.returncode} out={len(p.stdout)}字 err={len(p.stderr)}字")
    return p


def main():
    os.makedirs(OUT, exist_ok=True)
    print("# 刻", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
    for name, argv in CALLS:
        run(name, argv)
    # ⑦ pcid ―― 378724 の id を seqs の出目から引き、其の先頭8桁で引く
    s = open(os.path.join(OUT, "r2_seqs_378724,378725.out"), encoding="utf-8").read()
    ids = [ln.split(":", 1)[1].strip() for ln in s.splitlines() if ln.startswith("  id: ")]
    print("ids", ids)
    for i in ids:
        run(f"r7_pcid_{i[:8]}", [SB, "read", "pcid", i[:8]])
    print("# 了", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

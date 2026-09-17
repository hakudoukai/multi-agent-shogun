#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋒ 家老の実測を貴席の器で再現する ―― km-89 束(440本・臺帳427項・員外13)。

家老の宣: 「條① が rc=0『一致』と出る」。之を己の手で再現し、合はねば ★家老の数が誤り★ と書く。
貴席(專任2)は km-89 の臺帳を建てた者ゆゑ、再現の責は貴席に在る。

★km-89 束へは一字も書かぬ★ ―― 照合器も門も読取のみ。
出目は本弾の raw/ へ置く。
"""
import hashlib
import json
import os
import subprocess
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
VERIFY = os.path.join(REPO, "scripts", "checks", "karo_mac_manifest_verify.py")
GATE = os.path.join(REPO, "scripts", "checks", "karo_mac_dasumae_gate.sh")
KM89 = os.path.join(REPO, "docs", "evidence",
                    "km-89-oya-ga-mamorazu-ko-ga-kuraberu-kuchi-wo-ryoutaishou-de-hakare-20260917")


def koku():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 20), b""):
            h.update(buf)
    return h.hexdigest()[:16]


def aruki(root):
    """★S_ISREG のみ数へる★(FIFO は open() で止まる ―― 数へに混ぜぬ)。"""
    sei, higa, fukasa = [], [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        d = os.path.relpath(dirpath, root)
        fukasa = max(fukasa, 0 if d == "." else d.count(os.sep) + 1)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            if os.path.islink(full):
                higa.append((rel, "symlink"))
            elif os.path.isfile(full):
                sei.append(rel)
            else:
                higa.append((rel, "非regular"))
    return sei, higa, fukasa


def yomite():
    import importlib.util
    spec = importlib.util.spec_from_file_location("km_verify", VERIFY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    t0 = koku()
    mod = yomite()
    man = os.path.join(KM89, "MANIFEST.txt")
    print("刻(始) %s" % t0)
    print("的束   %s" % os.path.relpath(KM89, REPO))
    print("臺帳   MANIFEST.txt sha16=%s bytes=%d" % (sha16(man), os.path.getsize(man)))
    print("照合器 sha16=%s / 門 sha16=%s" % (sha16(VERIFY), sha16(GATE)))

    disk, higa, fukasa = aruki(KM89)
    rows, chuu, yomenu = [], 0, 0
    for raw in open(man, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            chuu += 1
            continue
        c = mod.paths_of(line)
        if not c:
            yomenu += 1
            continue
        rows.append(c[0])
    dset = set(rows)
    ingai = sorted(x for x in disk if x not in dset)
    jittai_nashi = sorted(x for x in dset if not os.path.isfile(os.path.join(KM89, x)))

    print("\n==== 己の歩き(器に問はず) ====")
    print("  歩いた根   %s" % os.path.relpath(KM89, REPO))
    print("  歩きの深さ %d" % fukasa)
    print("  disk 本(regular) %d / 非regular %d" % (len(disk), len(higa)))
    print("  臺帳 註行 %d / path行 %d / 讀めぬ行 %d / 相異なる path %d"
          % (chuu, len(rows), yomenu, len(dset)))
    print("  ★員外(disk有・臺帳無) %d★" % len(ingai))
    for x in ingai:
        print("    員外 %s" % x)
    print("  実体無(臺帳有・disk無) %d" % len(jittai_nashi))

    # ―― 條① 単体(照合器を 基点 "." で直に)
    e = dict(os.environ)
    p = subprocess.run([sys.executable, "-B", VERIFY, "MANIFEST.txt", "."],
                       cwd=KM89, capture_output=True, text=True, env=e)
    kaku(os.path.join(RAW, "20_km89_verify.out"), p.stdout)
    kaku(os.path.join(RAW, "20_km89_verify.err"), p.stderr)
    kaku(os.path.join(RAW, "20_km89_verify.rc"), str(p.returncode))
    print("\n==== 條① 単体(照合器・基点 '.') rc=%d ====" % p.returncode)
    for ln in p.stdout.rstrip("\n").split("\n"):
        print("  | %s" % ln)

    # ―― 門を ★全440本★ argv で通す(家老の「全歩き」を再現)
    e2 = dict(os.environ)
    e2["KM_GATE_MANIFEST_BASE"] = "."
    g = subprocess.run(["bash", GATE, "MANIFEST.txt"] + disk,
                       cwd=KM89, capture_output=True, text=True, env=e2)
    kaku(os.path.join(RAW, "20_km89_gate_zenaruki.out"), g.stdout)
    kaku(os.path.join(RAW, "20_km89_gate_zenaruki.err"), g.stderr)
    kaku(os.path.join(RAW, "20_km89_gate_zenaruki.rc"), str(g.returncode))
    kaku(os.path.join(RAW, "20_km89_gate_zenaruki.argv"), "\n".join(disk))
    jou1 = [ln for ln in g.stderr.split("\n") if "條①" in ln]
    print("\n==== 門 全歩き(argv %d 本) rc=%d ====" % (len(disk), g.returncode))
    print("  ---- 條① の逐語 ----")
    for ln in jou1:
        print("  | %s" % ln)
    print("  ---- 門 全體の判定行 ----")
    for ln in g.stderr.split("\n"):
        if any(k in ln for k in ("條②", "條③", "條④", "條⑤", "★出す")):
            print("  | %s" % ln)

    karou = {"束 本": 440, "臺帳 項": 427, "員外": 13, "條① rc": 0}
    mine = {"束 本": len(disk), "臺帳 項": len(rows), "員外": len(ingai),
            "條① rc": p.returncode}
    print("\n==== 家老の宣との突合 ====")
    au = True
    for k in karou:
        ok = karou[k] == mine[k]
        au = au and ok
        print("  %s : 家老 %s / 己 %s ―― %s" % (k, karou[k], mine[k], "一致" if ok else "★相異★"))
    print("  ★悉く一致か = %s★" % au)
    if au:
        print("  ∴ 家老の実測を再現した ―― ★員外 13 を抱へた儘 條① は rc=0『一致』と言ふ★")
    else:
        print("  ∴ ★家老の数が誤り★ ―― 上の相異を見よ")

    kaku(os.path.join(RAW, "20_km89_ingai.txt"), "\n".join(ingai))
    kaku(os.path.join(RAW, "20_km89_saigen.json"), json.dumps(
        {"刻(始)": t0, "刻(了)": koku(), "歩いた根": os.path.relpath(KM89, REPO),
         "歩きの深さ": fukasa, "家老の宣": karou, "己の実測": mine, "悉く一致": au,
         "員外の名": ingai, "実体無の名": jittai_nashi,
         "門 全歩き rc": g.returncode, "門 argv 本": len(disk),
         "條① の逐語": jou1}, ensure_ascii=False, indent=2))
    kaku_tsv(os.path.join(RAW, "20_km89_totsugou.tsv"),
             [[k, karou[k], mine[k], "一致" if karou[k] == mine[k] else "相異"] for k in karou],
             header=["項", "家老の宣", "己の実測", "判"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

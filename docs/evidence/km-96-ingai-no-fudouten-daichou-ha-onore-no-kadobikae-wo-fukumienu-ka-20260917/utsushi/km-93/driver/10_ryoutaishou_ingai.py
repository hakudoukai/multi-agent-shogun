#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐ 條① は員外(disk有・臺帳無)を一件でも検出するか ―― 両対照で示す。

  陽性対照 = 臺帳に書かぬ file を ★1本★ 置いた束(員外 1)
  陰性対照 = 員外 0 の束
  二つを ★同じ器・同じ基点★(照合器へ base="." / 門へ KM_GATE_MANIFEST_BASE=.)で通す。

★対照は検出子自身の物である★ ―― 臺帳は書き手 karo_mac_manifest_append.py で建て、
讀み手は scripts/checks/karo_mac_manifest_verify.py 其の物、門は karo_mac_dasumae_gate.sh
其の物を呼ぶ。作り直した模型では無い。

★員外の数は器に問へぬ★(之が本弾の主張) ∴ 己の歩きで別に数へ、対照が現に在る事を示す。
出目は raw/ へ置く。/tmp へは置かぬ。
"""
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
def _repo_root(start):
    """★根は .git を見附けて決める★ ―― dirname を数へると束の深さが変つた時に嘘になる
    (實測 2026-09-17 13:19: dirname 二段で docs/ を根と誤り FileNotFoundError で落ちた。
     其の走りは raw/09_driver_ochita_repo_root.* に残して在る)。"""
    d = start
    while True:
        if os.path.isdir(os.path.join(d, ".git")) or os.path.isfile(os.path.join(d, ".git")):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise SystemExit("★repo 根(.git)が見附からぬ: %s から登つた★" % start)
        d = up


REPO = _repo_root(BUNDLE)
RAW = os.path.join(BUNDLE, "raw")
sys.path.insert(0, RAW)
from kaki import kaku, kaku_tsv          # noqa: E402

VERIFY = os.path.join(REPO, "scripts", "checks", "karo_mac_manifest_verify.py")
APPEND = os.path.join(REPO, "scripts", "checks", "karo_mac_manifest_append.py")
GATE = os.path.join(REPO, "scripts", "checks", "karo_mac_dasumae_gate.sh")


def koku():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 20), b""):
            h.update(buf)
    return h.hexdigest()[:16]


def aruki(root):
    """★己の歩き★ ―― 根の下の全 regular file を束内相対で返す。
    非 regular(FIFO/socket/dir link)は別に返す ―― open() で止まる物を数へに混ぜぬ。"""
    seihou, higa, fukasa = [], [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        d = os.path.relpath(dirpath, root)
        fukasa = max(fukasa, 0 if d == "." else d.count(os.sep) + 1)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            st = os.lstat(full)
            if os.path.isfile(full) and not os.path.islink(full):
                seihou.append(rel)
            else:
                higa.append((rel, oct(st.st_mode)))
    return seihou, higa, fukasa


def daichou_gyou(man):
    """臺帳の path 行を ★讀み手其の物の取出し★ で拾ふ(己で regex を書き直さぬ)。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("km_verify", VERIFY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out, chuu = [], 0
    for raw in open(man, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            chuu += 1
            continue
        c = mod.paths_of(line)
        out.append(c[0] if c else None)
    return out, chuu


def hashiru(cmd, cwd, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def kizuku(name, ingai_hon, kesu=0):
    """対照の束を建てる。ingai_hon = 臺帳へ載せぬ file の本数。

    ★歩き根と臺帳の置場を分ける★ ―― 初版は臺帳を歩き根の中へ置いた故、
    ★陰性対照の員外が 0 に成らなんだ(MANIFEST.txt 自身が己の員外)★。
    其の走り = raw/09b_driver_innsei_ingai1.* / raw/09b_taishou_mae/ に残して在る。
    之は本弾 ㋔ の「束が己の門控を含む」問題の ★最小の形★ である。
    ∴ 臺帳は <対照>/ へ、測る物は <対照>/mono/ へ置き、★歩き根 = mono★ とする。
    臺帳の path は <対照> から見た相対(mono/…)ゆゑ 基点 "." で当たる。
    """
    d = os.path.join(RAW, "taishou", name)
    mono = os.path.join(d, "mono")
    os.makedirs(mono, exist_ok=True)
    nosreru = []
    for i in (1, 2):
        p = os.path.join(mono, "noseru_%d.txt" % i)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("対照 %s の載せる紙 %d\n" % (name, i))
        nosreru.append(p)
    man = os.path.join(d, "MANIFEST.txt")
    if os.path.exists(man):
        os.remove(man)
    # ★臺帳は書き手其の物で建てる★ ―― cd して束内相対にする(裁 seq322699)
    rc, out, err = hashiru([sys.executable, "-B", APPEND, "MANIFEST.txt"]
                           + [os.path.join("mono", os.path.basename(p)) for p in nosreru],
                           cwd=d)
    if rc != 0:
        print("★臺帳が建たぬ rc=%d★\n%s\n%s" % (rc, out, err), file=sys.stderr)
        sys.exit(2)
    nosenu = []
    for i in range(1, ingai_hon + 1):
        p = os.path.join(mono, "NOSENU_ingai_%d.txt" % i)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("★之は臺帳に一行も書かれて居らぬ ―― 員外 %d★\n" % i)
        nosenu.append(p)
    # ★丙(恒真でない證)★ 臺帳へ載せた紙を disk から消す → 實體無 で鳴る筈
    keshita = []
    for p2 in nosreru[:kesu]:
        os.remove(p2)
        keshita.append(os.path.relpath(p2, d))
    return d, mono, man, nosreru, nosenu, out, keshita


def hakaru(name, ingai_hon, kesu=0):
    d, mono, man, noseru, nosenu, append_out, keshita = kizuku(name, ingai_hon, kesu)
    # ★歩き根 = mono★。名は臺帳と揃へる為 <対照> からの相対(mono/…)へ直す。
    disk_raw, higa, fukasa = aruki(mono)
    disk = [os.path.join("mono", x) for x in disk_raw]
    daichou, chuu = daichou_gyou(man)
    daichou_set = set(x for x in daichou if x)
    # ★員外 = disk に在り臺帳に無い★
    ingai = sorted(x for x in disk if x not in daichou_set)
    jittai_nashi = sorted(x for x in daichou_set if not os.path.isfile(os.path.join(d, x)))

    # ―― 照合器を ★同じ基点★ で通す
    v_rc, v_out, v_err = hashiru([sys.executable, "-B", VERIFY, "MANIFEST.txt", "."], cwd=d)
    # ―― 門を ★同じ基点★ で通す(argv = 臺帳に載せた紙のみ = km-89 と同じ作法)
    g_argv = [os.path.join("mono", os.path.basename(p)) for p in noseru
              if os.path.isfile(p)]
    g_rc, g_out, g_err = hashiru(["bash", GATE, "MANIFEST.txt"] + g_argv,
                                 cwd=d, env={"KM_GATE_MANIFEST_BASE": "."})

    rec = {
        "対照": name,
        "刻": koku(),
        "束": os.path.relpath(d, BUNDLE),
        "歩いた根": os.path.relpath(mono, REPO),
        "臺帳の置場(歩き根の外)": os.path.relpath(man, REPO),
        "歩きの深さ": fukasa,
        "disk 本(regular)": len(disk),
        "非regular 本": len(higa),
        "臺帳 註行": chuu,
        "臺帳 path行": len(daichou),
        "★員外(己の歩き)★": len(ingai),
        "臺帳へ載せた後 消した本": keshita,
        "員外の名": ingai,
        "実体無(己の歩き)": len(jittai_nashi),
        "陽性対照の実在": [
            {"名": os.path.relpath(p, d), "sha16": sha16(p), "bytes": os.path.getsize(p)}
            for p in nosenu],
        "照合器 rc": v_rc,
        "門 rc": g_rc,
    }
    tag = name
    kaku(os.path.join(RAW, "10_%s_verify.out" % tag), v_out)
    kaku(os.path.join(RAW, "10_%s_verify.err" % tag), v_err)
    kaku(os.path.join(RAW, "10_%s_verify.rc" % tag), str(v_rc))
    kaku(os.path.join(RAW, "10_%s_gate.out" % tag), g_out)
    kaku(os.path.join(RAW, "10_%s_gate.err" % tag), g_err)
    kaku(os.path.join(RAW, "10_%s_gate.rc" % tag), str(g_rc))
    kaku(os.path.join(RAW, "10_%s_append.out" % tag), append_out)
    kaku(os.path.join(RAW, "10_%s_daichou.txt" % tag), open(man, encoding="utf-8").read())
    return rec, v_out, g_err


def main():
    print("刻 %s" % koku())
    print("照合器 %s sha16=%s" % (os.path.relpath(VERIFY, REPO), sha16(VERIFY)))
    print("門     %s sha16=%s" % (os.path.relpath(GATE, REPO), sha16(GATE)))
    recs = []
    for name, ingai, kesu in (("you", 1, 0), ("in", 0, 0), ("hei", 0, 1)):
        rec, v_out, g_err = hakaru(name, ingai, kesu)
        recs.append(rec)
        print("\n==== 対照 %s (員外を %d 本 置いた / 載せた後 %d 本 消した) ===="
              % (name, ingai, kesu))
        for k, v in rec.items():
            print("  %s = %s" % (k, v))
        print("  ---- 照合器の逐語 ----")
        for ln in v_out.rstrip("\n").split("\n"):
            print("    | %s" % ln)
        print("  ---- 門の 條① の逐語 ----")
        for ln in g_err.rstrip("\n").split("\n"):
            if "條①" in ln:
                print("    | %s" % ln)
    kaku(os.path.join(RAW, "10_ryoutaishou.json"),
         json.dumps(recs, ensure_ascii=False, indent=2))
    kaku_tsv(os.path.join(RAW, "10_ryoutaishou.tsv"),
             [[r["対照"], r["disk 本(regular)"], r["臺帳 path行"], r["★員外(己の歩き)★"],
               r["照合器 rc"], r["門 rc"], r["刻"]] for r in recs],
             header=["対照", "disk本(regular)", "臺帳path行(行)", "員外本(己の歩き)",
                     "照合器rc", "門rc", "刻"])
    byname = {r["対照"]: r for r in recs}
    you, inn, hei = byname["you"], byname["in"], byname["hei"]
    print("\n==== 断 ====")
    for na, r in (("陽性(員外 1)", you), ("陰性(員外 0)", inn), ("丙(實體無 1)", hei)):
        print("  %s 員外=%d 照合器 rc=%d / 門 rc=%d"
              % (na, r["★員外(己の歩き)★"], r["照合器 rc"], r["門 rc"]))
    onaji = (you["照合器 rc"] == inn["照合器 rc"]) and (you["門 rc"] == inn["門 rc"])
    print("  ★陽性と陰性の出目が同一か = %s★" % onaji)
    print("  ★丙で鳴るか(恒真でない證) = %s★ (照合器 rc=%d)"
          % (hei["照合器 rc"] != 0, hei["照合器 rc"]))
    if onaji and hei["照合器 rc"] != 0:
        print("  ∴ ★器は鳴る器である。然るに 條① は員外を一件も検出せぬ★")
    elif not onaji:
        print("  ∴ 條① は員外を検出した ―― ★家老の見立が誤り★")
    else:
        print("  ∴ ★丙でも鳴らぬ ―― 器か対照の建て方を疑へ(断を下すな)★")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""員外(臺帳に載らぬ disk の物)を数へ、★名指しで列べる★ 器。兼 ★丙案 第六條★。

読み手は ★門の照合器 其の物★ を import して使ふ(karo_mac_manifest_verify.paths_of)。
己で正規表現を書き直せば ★十五番目の方言★ が生まれる ―― 同じ物は同じ器で読む。

usage: 20_ingai.py <臺帳> <根> [--rokujou] [--hikae-nori <相対path>]...
  --rokujou      : ★第六條★ として判ずる ―― 員外が ★己の控のみ★ なら rc=0、他が混れば rc=1
  --hikae-nori   : 「己の控」と看做す接頭(既定 = 臺帳自身 と _gate/)
rc: 0=(既定)歩けた/(第六條)員外は己の控のみ / 1=第六條に落ちた / 2=器の誤り
"""
import importlib.util, os, stat, sys, time

VERIFY = "/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_manifest_verify.py"

def yomite():
    spec = importlib.util.spec_from_file_location("km_verify", VERIFY)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.paths_of, mod.SHA

def seiki(p):
    p = p.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return os.path.normpath(p)

def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr); return 2
    man, root = argv[1], argv[2]
    rokujou = "--rokujou" in argv[3:]
    nori = []
    a = argv[3:]
    for i, t in enumerate(a):
        if t == "--hikae-nori" and i + 1 < len(a):
            nori.append(seiki(a[i + 1]))
    if not os.path.isfile(man): print("★臺帳が無い: %s★" % man, file=sys.stderr); return 2
    if not os.path.isdir(root): print("★根が無い: %s★" % root, file=sys.stderr); return 2
    paths_of, SHA = yomite()

    nose, yomenu = set(), 0
    for raw in open(man, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not SHA.search(line):
            yomenu += 1        # ★sha 欄が 64hex でない行 ―― 照合器は此の行を ★見ぬ★★
            continue
        c = paths_of(line)
        if c:
            nose.add(seiki(c[0]))
        else:
            yomenu += 1

    disk, hijou = set(), []
    for dp, dns, fns in os.walk(root):
        dns.sort(); fns.sort()
        for fn in fns:
            p = os.path.join(dp, fn)
            st = os.lstat(p)
            if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode):
                hijou.append(p); continue
            disk.add(seiki(os.path.relpath(p, root)))

    if not nori:
        nori = [seiki(os.path.relpath(os.path.abspath(man), os.path.abspath(root)))
                if os.path.abspath(man).startswith(os.path.abspath(root) + os.sep) else "\0none",
                "_gate"]
    ingai = sorted(disk - nose)
    def ha_hikae(rel):
        for n in nori:
            if rel == n or rel.startswith(n + "/"):
                return True
        return False
    hikae = [x for x in ingai if ha_hikae(x)]
    hoka = [x for x in ingai if not ha_hikae(x)]

    print("刻 %s" % time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    print("臺帳 %s" % os.path.abspath(man))
    print("根 %s / 深さ 無限(os.walk)" % os.path.abspath(root))
    print("控の則 %s" % " , ".join(nori))
    print("臺帳の載せた本数 %d / 照合器が見ぬ行 %d" % (len(nose), yomenu))
    print("disk の常なる file %d / 非regular %d" % (len(disk), len(hijou)))
    print("★員外 %d★(内 己の控 %d / 他 %d)" % (len(ingai), len(hikae), len(hoka)))
    for x in hikae:
        print("  控 %s" % x.encode("unicode_escape").decode("ascii"))
    for x in hoka:
        print("  ★他★ %s" % x.encode("unicode_escape").decode("ascii"))
    nose_nashi = sorted(nose - disk)
    print("臺帳に在り disk に無し %d" % len(nose_nashi))
    for x in nose_nashi[:20]:
        print("  ★臺帳のみ★ %s" % x)
    if rokujou:
        if hoka:
            print("★第六條 落 ―― 員外に『己の控』でない物が %d 本★" % len(hoka))
            return 1
        print("★第六條 通 ―― 員外は己の控のみ(%d 本)★" % len(hikae))
        return 0
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

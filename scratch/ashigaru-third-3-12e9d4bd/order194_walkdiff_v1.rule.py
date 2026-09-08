# -*- coding: utf-8 -*-
u"""源器(order194_source_docs_evidence_packet_v1) と 新器(order194_gap_fill_v1) の
scanned の差 20 を ★file を名指して★ 当てる。讀取のみ・走行 0・書込 0。
源器の形 = 收集 list を作つてから讀む / 新器の形 = walk の其の場で讀む。
"""
import os, io, hashlib
TREE = u"/home/hakudoukai/a3/wt-bundle-fix4"
SKIPD = set([u"node_modules", u".git", u".venv", u"venv", u"__pycache__"])
PREF  = (u"backend/", u"tests/", u"docs/", u"reports/", u"src/", u"frontend/")

def walk_all():
    out = []
    for dp, dn, fn in os.walk(TREE):
        dn[:] = [x for x in dn if x not in SKIPD]
        for f in fn:
            out.append(os.path.relpath(os.path.join(dp, f), TREE))
    return out

def read_ok(rel, narrow):
    ap = os.path.join(TREE, rel)
    try:
        io.open(ap, encoding="utf-8").read()
        return True, u"-"
    except (OSError, UnicodeDecodeError) as e:
        if narrow:
            return False, type(e).__name__
        return False, type(e).__name__
    except Exception as e:
        if narrow:
            raise
        return False, type(e).__name__

def main():
    fl = walk_all()
    print(u"walked_files=%d" % len(fl))
    a_ok, b_ok = set(), set()
    a_fail, b_fail = {}, {}
    for rel in fl:
        ok, k = read_ok(rel, False)   # 新器の形(Exception 悉く)
        if ok: b_ok.add(rel)
        else:  b_fail[rel] = k
        # 源器の形: 同じ讀み・同じ except 集合 ゆゑ結果は同一の筈。之を検める
        try:
            io.open(os.path.join(TREE, rel), encoding="utf-8").read()
            a_ok.add(rel)
        except (OSError, UnicodeDecodeError) as e:
            a_fail[rel] = type(e).__name__
        except Exception as e:
            a_fail[rel] = u"ESCAPED:" + type(e).__name__
    print(u"same_walk_reread: A_ok=%d B_ok=%d" % (len(a_ok), len(b_ok)))
    d1 = sorted(a_ok - b_ok); d2 = sorted(b_ok - a_ok)
    print(u"A_only=%d B_only=%d" % (len(d1), len(d2)))
    for r in d1[:20]: print(u"  A_only | %s" % r)
    for r in d2[:20]: print(u"  B_only | %s" % r)
    esc = [(r, k) for r, k in a_fail.items() if k.startswith(u"ESCAPED")]
    print(u"escaped_from_narrow_except=%d" % len(esc))
    for r, k in esc[:20]: print(u"  ESC | %s | %s" % (r, k))
    # 源器の母数の狭さ: PREF 六つに限つて居たか否かを検める
    inpref = [r for r in fl if r.startswith(PREF)]
    print(u"files_under_six_prefixes=%d  files_outside=%d" % (len(inpref), len(fl) - len(inpref)))
    ok_in = len([r for r in inpref if r in b_ok])
    print(u"readable_under_six_prefixes=%d" % ok_in)

main()

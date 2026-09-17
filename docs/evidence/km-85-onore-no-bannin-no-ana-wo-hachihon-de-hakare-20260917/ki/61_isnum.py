# -*- coding: utf-8 -*-
"""61 ―― ㋔ の裏付け。註が「default-deny」と名乗る is_num を ★逐語で切り出して★ 毒十値に当てる。
   併せて甲(num_same_op)・甲甲(num_same_op && -ge 0)を同じ値へ当て、三者の答の違ひを出す。
   ★生器へは一字も書かぬ。切片の sha16 を生器の同行と照らして證す。★"""
import os, sys, io, time, hashlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kaki as K
BUNDLE = os.path.abspath(os.path.join(HERE, "..")); UTS = os.path.join(BUNDLE, "utsushi")
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
REL_IS, GYO_IS = "scripts/checks/karo_mac_dasumae_gate.sh", 29
REL_SA, GYO_SA = "scripts/checks/karo_mac_dasumae_gate.sh", 36

def gyou(rel, n):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read().split("\n")[n - 1]

def sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

is_src, sa_src = gyou(REL_IS, GYO_IS), gyou(REL_SA, GYO_SA)
assert is_src.startswith("is_num()"), is_src
assert sa_src.startswith("num_same_op()"), sa_src

H = os.path.join(UTS, "hei_isnum.sh")
K.kaku(H, u"\n".join([
    u"#!/bin/bash",
    u"# ★寫し器★ hei_isnum(㋔ の裏付け・型=丙) ―― %s:%d と :%d の★逐語一行づつ★" % (REL_IS, GYO_IS, GYO_SA),
    u"#   作つた刻=%s ／ 生器へは一字も書いて居らぬ" % time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    u"set -u",
    u"# ===== 寫し ここから(逐語) =====",
    is_src, sa_src,
    u"# ===== 寫し ここまで =====",
    u"# ===== 附録(當席の駆動部) =====",
    u'v="${1-}"',
    u'if is_num "$v"; then a=通; else a=落; fi',
    u'if num_same_op "$v"; then b=通; else b=落; fi',
    u'if num_same_op "$v" && [ "$v" -ge 0 ] 2>/dev/null; then c=通; else c=落; fi',
    u'printf "%s\\t%s\\t%s\\n" "$a" "$b" "$c"',
]))

# 切片の同一を證す
with io.open(H, encoding="utf-8") as fh:
    body = fh.read().split(u"# ===== 寫し ここから(逐語) =====\n")[1].split(u"\n# ===== 寫し ここまで")[0]
onaji = (sha16(body) == sha16(is_src + u"\n" + sa_src))

DOKU = ["0", "-0", "-5", "4294967295", "4294967296", "9223372036854775807",
        "9223372036854775808", "020", "", "+10", "7", "abc", "99999999999999999999"]
rows = []
for v in DOKU:
    pr = subprocess.run(["/bin/bash", H, v], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o = pr.stdout.decode().strip().split("\t")
    a, b, c = (o + ["?", "?", "?"])[:3]
    rows.append([v if v != "" else u"空文字", a, b, c,
                 u"三者一致" if a == b == c else u"★割れた★",
                 pr.returncode, pr.stderr.decode().strip().replace("\n", u"␊") or u"―"])
K.kaku_tsv(os.path.join(BUNDLE, "nama", "61_isnum.tsv"), rows,
           ["#毒値", "is_num(旧・註が default-deny と名乗る器)", "num_same_op(甲の中身)",
            "num_same_op && -ge0(甲の全形)", "三者", "rc", "外の声"])
L = [u"= 61 ―― ㋔ 裏付け ―― is_num / num_same_op / 甲の全形 を同じ毒へ当てる =",
     u"刻=%s" % time.strftime("%Y-%m-%dT%H:%M:%S%z"),
     u"切片 = %s:%d ・ %s:%d(逐語一行づつ) ／ 切片 sha16 一致 = %s"
     % (REL_IS, GYO_IS, REL_SA, GYO_SA, u"○" if onaji else u"★相違★"),
     u"  %s:%d 逐語 = %s" % (REL_IS, GYO_IS, is_src),
     u"  %s:%d 逐語 = %s" % (REL_SA, GYO_SA, sa_src), u""]
L.append(u"  %-22s %-8s %-8s %-8s %s" % (u"毒値", u"is_num", u"甲の中身", u"甲の全形", u"三者"))
for r in rows:
    L.append(u"  %-22s %-8s %-8s %-8s %s" % (r[0], r[1], r[2], r[3], r[4]))
wareta = [r[0] for r in rows if r[4] != u"三者一致"]
L.append(u"")
L.append(u"★三者の答が割れた毒値 = %d 値 : %s★" % (len(wareta), u" / ".join(wareta)))
tsuu = [r[0] for r in rows if r[1] == u"通"]
L.append(u"  is_num が「數」と讀んだ値 = %s" % u" / ".join(tsuu))
L.append(u"  ∴ %s:82 の註「既存の is_num → 測れぬは通さぬ(default-deny)」は" % REL_IS)
L.append(u"    ★2^63 以上の十進に対して成り立たぬ★ ―― 同じ file の L32-34 が其れを自ら書いて居る")
K.kaku(os.path.join(BUNDLE, "nama", "61_isnum.txt"), u"\n".join(L))
sys.stderr.write("61 done rows=%d 一致=%s\n" % (len(rows), onaji))
sys.exit(0 if onaji and rows else 5)

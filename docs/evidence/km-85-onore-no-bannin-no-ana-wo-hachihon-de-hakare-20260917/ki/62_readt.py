# -*- coding: utf-8 -*-
"""62 ―― ㋕ 案丙 の裏付け ―― `read -t <値>` の空打ち(dry-run)を 14 値へ当てる。
★rc では分けられぬ事★ と ★stderr でなら分けられる事★ を同じ表で示す。生器へは触れぬ。"""
import os, sys, subprocess, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki as K
BUNDLE = os.path.abspath(os.path.join(HERE, ".."))
BASH = "/bin/bash"

ATAI = ["0", "-0", "-5", "4294967295", "4294967296", "9223372036854775807",
        "9223372036854775808", "020", "", "+10", "7", "abc", "10", "300", "2", "60"]
NA = {"": u"空文字"}

ver = subprocess.run([BASH, "-c", "echo $BASH_VERSION"], stdout=subprocess.PIPE).stdout.decode().strip()
rows, L = [], []
L.append(u"= 62 ―― ㋕ 案丙 の裏付け ―― `read -t <値>` の空打ち =")
L.append(u"刻=%s  走らせた器=%s (BASH_VERSION=%s)" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), BASH, ver))
L.append(u"打つた形(逐語) = %s -c 'read -t \"$1\" _ < /dev/null' _ <値>" % BASH)
L.append(u"★/dev/null ゆゑ待たぬ ―― 測るのは『bash が其の時限指定を受けるか』のみ★")
L.append(u"")
L.append(u"  %-22s %-5s %-6s %s" % (u"値", u"rc", u"stderr", u"stderr 逐語(有る時)"))
for v in ATAI:
    pr = subprocess.run([BASH, "-c", 'read -t "$1" _ < /dev/null', "_", v],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    err = pr.stderr.decode("utf-8", "replace").replace("\n", u"␊").strip(u"␊")
    na = NA.get(v, v)
    rows.append([na, pr.returncode, len(pr.stderr), u"○受けた" if not err else u"×拒んだ", err or u"―"])
    L.append(u"  %-22s %-5s %-6s %s" % (na, pr.returncode, len(pr.stderr), err or u"―"))

rcs = sorted(set(r[1] for r in rows))
uke = [r[0] for r in rows if r[3] == u"○受けた"]
kobamu = [r[0] for r in rows if r[3] == u"×拒んだ"]
L.append(u"")
L.append(u"★rc の異なり = %d 種 %s ―― ∴ ★rc では分けられぬ★" % (len(rcs), rcs))
L.append(u"★bash が受けた値 = %d : %s★" % (len(uke), u" / ".join(uke)))
L.append(u"★bash が拒んだ値 = %d : %s★" % (len(kobamu), u" / ".join(kobamu)))
L.append(u"")
L.append(u"★案丙 が閉ぢる★ = 拒んだ %d 値。★案丙 が閉ぢぬ★ = 受けた %d 値 ―― 内 4294967295 は約136年待つ。" % (len(kobamu), len(uke)))
GENYOU = ["10", "60", "2", "300"]
g = [(x, u"○受けた" if x in uke else u"×拒んだ") for x in GENYOU]
L.append(u"★現用の値(repo 内に実在する物)を名指して測る = %s★" % u" / ".join("%s:%s" % t for t in g))
L.append(u"  ∴ 案丙 の誤鳴り = %d 件(測つた上での數。見込みではない)" % sum(1 for _, j in g if j != u"○受けた"))
K.kaku_tsv(os.path.join(BUNDLE, "nama", "62_readt.tsv"), rows,
           ["#値", "rc", "stderr byte", "判", "stderr 逐語"])
K.kaku(os.path.join(BUNDLE, "nama", "62_readt.txt"), u"\n".join(L))
sys.stderr.write("62 done n=%d rc種=%d 受=%d 拒=%d\n" % (len(rows), len(rcs), len(uke), len(kobamu)))

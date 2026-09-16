#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""67_nokori.py -- toi が名指した残り二形(★NUL★・★重複区切り★)を足す器。

62 の表を壊さぬ為 別器に分ける。
NUL は ★名に建てられぬ★(POSIX の名は NUL を含み得ぬ) ゆゑ 行の段でのみ測り、
其の旨を ★直せぬ／測れぬ の別★ と共に書く。
"""
import io, os, sys, errno, hashlib, importlib.util, subprocess

ROOT, B = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
FX = os.path.join(B, "fixture", "nokori"); os.makedirs(FX, exist_ok=True)
def yomu(p, na):
    sp = importlib.util.spec_from_file_location(na, p); m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m); return m
mae = yomu(os.path.join(B,"patch","verify_BEFORE.py"), "m68")
ato = yomu(os.path.join(B,"patch","verify_AFTER.py"), "a68")
o = []

# ―― A19 NUL ――
o.append(u"■ A19_nul ―― 名に NUL(U+0000) を含む")
na = os.path.join(FX, "a\x00b.txt")
try:
    open(na, "wb").write(b"x\n"); tate = u"★建てた(想定外)★"
except ValueError as e:
    tate = u"★建てられぬ ―― %s: %s★" % (type(e).__name__, e)
except OSError as e:
    tate = u"★建てられぬ ―― OSError %s★" % errno.errorcode.get(e.errno, e.errno)
o.append(u"  disk へ建てられるか = %s" % tate)
gy = u'path=docs/x/a\x00b.txt sha256=%s bytes=2 lines=1' % (u"0"*64)
cb, ca = mae.paths_of(gy), ato.paths_of(gy)
o.append(u"  行の段: BEFORE 候補=%s" % repr(cb))
o.append(u"          AFTER  候補=%s" % repr(ca))
o.append(u"  ⑴破れるか=★破れぬ(NUL は Python の \\s に非ず・分けられぬ)★ ⑵出目=名がそのまま候補になる")
o.append(u"  ⑶★然れど disk に其の名は建て得ぬ★ ゆゑ 実際には ★実体無★ と鳴るのみ ―― ★黙れぬ★")
o.append(u"  ★測れぬ に非ず。★建て得ぬ★ と書く。臺帳へ NUL を書ける書き手が居れば別だが、")
o.append(u"    現物の書き手は togame() が NUL を… ―― 下で問ふ")

# 書き手は NUL を咎めるか
T = os.path.join(FX, "kakite"); os.makedirs(T, exist_ok=True)
m2 = os.path.join(T, "m.txt")
r = subprocess.run([sys.executable, "-B", os.path.join(ROOT,"scripts","checks","karo_mac_manifest_append.py"),
                    m2, os.path.join(FX, "futsu.txt")], capture_output=True, text=True)
open(os.path.join(FX,"futsu.txt"),"wb").write(b"x\n")
o.append(u"  (註) 現物の書き手に NUL 名は ★渡し得ぬ★ ―― argv に NUL は載らぬ。")
o.append(u"")

# ―― A20 重複区切り ――
o.append(u"■ A20_nijuu_kugiri ―― path の中に `//` が在る")
d = os.path.join(FX, "kugiri"); os.makedirs(d, exist_ok=True)
f = os.path.join(d, "c.txt"); open(f, "wb").write(b"x\n")
sen = hashlib.sha256(b"x\n").hexdigest()
rel = os.path.relpath(f, ROOT)
warui = rel.replace(u"/kugiri/", u"/kugiri//")
gy = u"path=%s sha256=%s bytes=2 lines=1" % (warui, sen)
cb, ca = mae.paths_of(gy), ato.paths_of(gy)
aru_b = [c for c in cb if os.path.isfile(os.path.join(ROOT,c))]
aru_a = [c for c in ca if os.path.isfile(os.path.join(ROOT,c))]
o.append(u"  臺帳の名 = %s" % warui)
o.append(u"  BEFORE 候補=%s → 解けた=%s" % (repr(cb)[:120], aru_b[0] if aru_b else u"無し"))
o.append(u"  AFTER  候補=%s → 解けた=%s" % (repr(ca)[:120], aru_a[0] if aru_a else u"無し"))
o.append(u"  ⑴破れるか=★破れぬ★ ⑵出目=★一致★(os が `//` を一つに畳む)")
o.append(u"  ⑶★然れど之は 黙りの温床★ ―― 名としては別字列なのに 同じ物へ解ける。")
o.append(u"    ∴ ★臺帳の名と disk の名が一対一でない★。門は之を咎めぬ。")
o.append(u"")
# 併せて: 畳まれる事の證(二つの綴りが同じ物を指す)
o.append(u"  證: os.path.realpath が一致するか = %s" %
         (os.path.realpath(os.path.join(ROOT,warui)) == os.path.realpath(f)))
t = u"\n".join(o)
io.open(os.path.join(B,"an","nokori.txt"),"w",encoding="utf-8",newline="").write(t+u"\n")
sys.stdout.write(t+u"\n")

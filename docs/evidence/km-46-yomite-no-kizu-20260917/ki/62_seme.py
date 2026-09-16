#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""62_seme.py -- ★名の形ごとに一本ずつ 対照を建て、讀手 paths_of を攻める器★。

為す事(形ごと):
  ⑴ disk に其の名の物を建てる(建てられぬ形は建てぬ ―― ★建てなんだ事を書く★)
  ⑵ ★現物の書き手★ karo_mac_manifest_append.py に一本だけ渡し、rc と 書かれた行 を取る
  ⑶ 書き手が拒んだ(rc=3)形は ★旧い臺帳に在り得る行★ を手で綴り、其の旨を札にする
  ⑷ 其の行を BEFORE / AFTER の paths_of に食はせ、★第一候補★ と ★候補の数★ を取る
  ⑸ 一行の臺帳を建て、BEFORE / AFTER の現物の照合器を走らせ 一致/相違/実体無/読めぬ行 と rc を取る
出す物: <出し先>/kata.tsv (一形一行) と <出し先>/mon/<形>.{before,after}.{out,err}
"""
import io, os, subprocess, sys, importlib.util, unicodedata

ROOT = os.path.abspath(sys.argv[1])          # repo 根
B = os.path.abspath(sys.argv[2])             # 束
R = os.path.join(B, "fixture", "kata")
AN = os.path.join(B, "an")
MON = os.path.join(AN, "mon")
MAN = os.path.join(AN, "man")
for d in (R, AN, MON, MAN):
    os.makedirs(d, exist_ok=True)

APPEND = os.path.join(ROOT, "scripts", "checks", "karo_mac_manifest_append.py")
VB = os.path.join(B, "patch", "verify_BEFORE.py")
VA = os.path.join(B, "patch", "verify_AFTER.py")


def load(p, nm):
    spec = importlib.util.spec_from_file_location(nm, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

before = load(VB, "vb")
after = load(VA, "va")

SHA64 = "a" * 64
# (札, 部屋, 名, 註, disk へ建てるか)
KATA = [
    ("A01_kiyoi",      "A01", u"kiyoi.txt",                      u"清い名(陽性対照)", True),
    ("A02_hankaku",    "A02", u"a b.txt",                        u"半角空白", True),
    ("A03_tab",        "A03", u"a\tb.txt",                       u"TAB", True),
    ("A04_zenkaku",    "A04", u"a　b.txt",                   u"全角空白 U+3000", True),
    ("A05_nbsp",       "A05", u"a b.txt",                   u"NBSP U+00A0", True),
    ("A06_u2028",      "A06", u"a b.txt",                   u"LINE SEPARATOR U+2028", True),
    ("A07_zwsp",       "A07", u"a​b.txt",                   u"ZWSP U+200B(★空白に非ず★)", True),
    ("A08_u205f",      "A08", u"a b.txt",                   u"MEDIUM MATH SPACE U+205F", True),
    ("A09_sha8",       "A09", u"a sha256=deadbeef b.txt",        u"名に ` sha256=<8hex>`(km-45 の三本)", True),
    ("A10_sha64",      "A10", u"a sha256=" + "b" * 64 + u" c.txt", u"名に ` sha256=<64hex>`", True),
    ("A11_ikoru",      "A11", u"a=b.txt",                        u"`=` を含む(空白無)", True),
    ("A12_koron",      "A12", u"a:b.txt",                        u"`:` を含む", True),
    ("A13_hyphen",     "A13", u"-hajime.txt",                    u"先頭が `-`", True),
    ("A14_chodai",     "A14", (u"n" * 180) + u".txt",            u"長大名(184字)", True),
    ("A15_matsubi",    "A15", u"matsubi .txt",                   u"名の末に空白", True),
    ("A16_atama",      "A16", u" atama.txt",                     u"名の頭に空白", True),
    ("A17_sharp",      "A17", u"#chu.txt",                       u"先頭が `#`(註と紛れる)", True),
    ("A18_path_ikoru", "A18", u"path=x.txt",                     u"名が `path=` で始まる", True),
    ("B01_futae",      "B01", u'wa"rui.txt',                     u"二重引用符", True),
    ("B02_hitoe",      "B02", u"wa'rui2.txt",                    u"一重引用符", True),
    ("B03_lf",         "B03", u"a\nb.txt",                       u"改行 LF(★disk に建てぬ★)", False),
    ("B04_cr",         "B04", u"a\rb.txt",                       u"復帰 CR(★disk に建てぬ★)", False),
]


def kaku_tegaki(rel, sha):
    u"""書き手が拒んだ形を ★旧い臺帳に在り得る綴り★ で手で綴る(空白含めば括る)。

    ★sha は 現物の digest を用んる★ ―― 偽の sha だと 候補が解けても 必ず 相違 になり、
    ★「黙つて別の物を讀む」を 右も左も 見失ふ★。
    """
    if any(c in rel for c in u" \t"):
        return u'path="%s" sha256=%s bytes=5 lines=1' % (rel, sha)
    return u'path=%s sha256=%s bytes=5 lines=1' % (rel, sha)


def toku(cands, bases, root):
    u"""main() の解き方を 写し取る ―― ★何處の物を実際に讀むか★ を出す。"""
    for p in cands:
        for b in bases:
            c = os.path.join(b, p) if b else p
            if os.path.isfile(c):
                return os.path.abspath(c)
    return None


rows = []
for fuda, heya, na, chu, tateru in KATA:
    d = os.path.join(R, heya)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, na)
    tateta = False
    tate_riyuu = u"★建てぬ(束の歩きと門を毒する故)★"
    if tateru:
        try:
            with open(p, "wb") as fh:
                fh.write(b"km46\n")
            tateta = os.path.isfile(p)
            tate_riyuu = u"建てた" if tateta else u"★建たなんだ★"
        except OSError as e:
            tate_riyuu = u"★建たぬ(OSError %s)★" % e.errno
    rel = os.path.relpath(p, ROOT)

    # ⑵ 現物の書き手
    kaki_rc, gyou, kaki_de = None, None, u""
    if tateta:
        m1 = os.path.join(MAN, fuda + u".kaki.txt")
        if os.path.exists(m1):
            os.remove(m1)
        r = subprocess.run([sys.executable, "-B", APPEND, m1, p],
                           cwd=ROOT, capture_output=True, text=True)
        kaki_rc = r.returncode
        kaki_de = (r.stderr or u"").strip().replace(u"\n", u" / ")[:160]
        if kaki_rc == 0 and os.path.isfile(m1):
            gy = [l for l in io.open(m1, encoding="utf-8").read().split(u"\n")
                  if l and not l.startswith(u"#")]
            gyou = gy[-1] if gy else None
    honsha = None
    if tateta:
        import hashlib
        honsha = hashlib.sha256(open(p, "rb").read()).hexdigest()
    tegaki = False
    if gyou is None:
        gyou = kaku_tegaki(rel, honsha or SHA64)
        tegaki = True

    # ⑷ paths_of 二枚
    cb = before.paths_of(gyou)
    ca = after.paths_of(gyou)

    # ⑸ 現物の照合器 二枚(一行の臺帳)
    m2 = os.path.join(MAN, fuda + u".one.txt")
    io.open(m2, "w", encoding="utf-8", newline="").write(gyou + u"\n")
    de = {}
    for nm, v in ((u"before", VB), (u"after", VA)):
        r = subprocess.run([sys.executable, "-B", v, m2, ROOT + os.sep],
                           cwd=ROOT, capture_output=True, text=True)
        io.open(os.path.join(MON, u"%s.%s.out" % (fuda, nm)), "w",
                encoding="utf-8", newline="").write(r.stdout)
        io.open(os.path.join(MON, u"%s.%s.err" % (fuda, nm)), "w",
                encoding="utf-8", newline="").write(r.stderr)
        atari = u"?"
        for l in r.stdout.split(u"\n"):
            if l.strip().startswith(u"一致"):
                atari = l.strip().replace(u"★", u"")
                break
        de[nm] = (r.returncode, atari)

    # ★何處の物を 実際に讀むか★(main と同じ基点の並び)
    bases = [ROOT + os.sep]
    tb, ta = toku(cb, bases, ROOT), toku(ca, bases, ROOT)
    mato = os.path.abspath(p) if tateta else None
    def sabaki(t):
        if mato is None:
            return u"★測れぬ(disk に物を建てて居らぬ)★"
        if t is None:
            return u"実体無"
        if os.path.realpath(t) == os.path.realpath(mato):
            return u"★正(狙った物)★"
        return u"★黙つて別の物★"
    rows.append(dict(toku_b=sabaki(tb), toku_a=sabaki(ta),
                     tb=tb, ta=ta, honsha=honsha,
                     fuda=fuda, chu=chu, na=na, tate=tate_riyuu, rel=rel,
                     kaki_rc=kaki_rc, kaki_de=kaki_de, tegaki=tegaki, gyou=gyou,
                     cb=cb, ca=ca,
                     b_rc=de[u"before"][0], b_at=de[u"before"][1],
                     a_rc=de[u"after"][0], a_at=de[u"after"][1]))

# 出す
def mie(s):
    u"""目に見えぬ字を codepoint で顕す。"""
    o = []
    for ch in s:
        if ch == u"\n":
            o.append(u"<LF>")
        elif ch == u"\r":
            o.append(u"<CR>")
        elif ch == u"\t":
            o.append(u"<TAB>")
        elif unicodedata.category(ch) in (u"Zs", u"Zl", u"Zp", u"Cf") and ch != u" ":
            o.append(u"<U+%04X>" % ord(ch))
        else:
            o.append(ch)
    return u"".join(o)


out = [u"\t".join([u"札", u"註", u"名(顕)", u"建", u"書き手rc", u"綴り",
                   u"BEFORE第一候補(顕)", u"BEFORE候補数", u"AFTER第一候補(顕)", u"AFTER候補数",
                   u"BEFORE rc", u"BEFORE 出目", u"AFTER rc", u"AFTER 出目", u"変つたか",
                   u"BEFORE 何を讀んだか", u"AFTER 何を讀んだか"])]
for r in rows:
    kawatta = u"★変つた★" if (r["b_rc"], r["b_at"]) != (r["a_rc"], r["a_at"]) or r["cb"] != r["ca"] else u"不変"
    out.append(u"\t".join([
        r["fuda"], r["chu"], mie(r["na"]), r["tate"],
        u"-" if r["kaki_rc"] is None else str(r["kaki_rc"]),
        u"手書き(書き手が拒んだ/建てられぬ故)" if r["tegaki"] else u"現物の書き手",
        mie(r["cb"][0]) if r["cb"] else u"★無★", str(len(r["cb"])),
        mie(r["ca"][0]) if r["ca"] else u"★無★", str(len(r["ca"])),
        str(r["b_rc"]), r["b_at"], str(r["a_rc"]), r["a_at"], kawatta,
        r["toku_b"], r["toku_a"]]))
io.open(os.path.join(AN, u"kata.tsv"), "w", encoding="utf-8", newline="").write(u"\n".join(out) + u"\n")
sys.stderr.write(u"★形=%d 建てた=%d 手書き=%d★\n"
                 % (len(rows), sum(1 for r in rows if r["tate"] == u"建てた"),
                    sum(1 for r in rows if r["tegaki"])))

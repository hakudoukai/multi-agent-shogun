# -*- coding: utf-8 -*-
"""40 ―― ㋑ 呼び方を三に分け、file:行 で名指す器。
  甲 = num_same_op v ★かつ★ 同じ行で [ v -ge 0 ] を重ねる(範囲を見る)
  乙 = num_same_op v ★単独★(否定 ! を含む) ―― ★範囲を見ぬ★
  丙 = 右の何れでもない
判の根は★disk の字面のみ★。憶測で分けぬ。分けの式(正規)は出目に刷る。
併せて「其の呼び口を通る閾が何本か」を fix_threshold の呼び手から機械で数へる。"""
import os, sys, re, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki as K
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BUNDLE = os.path.abspath(os.path.join(HERE, ".."))

# 的 = 30 の出目(31_teigi.tsv)の内 scripts/ の生器のみ。此処は札の宣ではなく★己の測り★から引く
TEIGI = os.path.join(BUNDLE, "nama", "31_teigi.tsv")

# ―― 分けの式(宣) ――
RE_DEF  = re.compile(r'^\s*num_same_op\s*\(\s*\)\s*\{')
RE_CALL = re.compile(r'(?<![A-Za-z0-9_])num_same_op(?![A-Za-z0-9_])')
RE_CMT  = re.compile(r'^\s*#')
# ★条件部の抜き方(宣)★ `if <条件>; then …` の <条件> のみを型の根とする。
#   then 以降の胴(eval / return 等)は型に関はらぬ ―― 見るのは「何を検めたか」だけ。
RE_JOU  = re.compile(r'^\s*if\s+(.*?)\s*;\s*then\b')
# 甲 = 条件が num_same_op v ★かつ★ [ v -ge … ] の二段
RE_KOU  = re.compile(r'^!?\s*num_same_op\s+"?\$?\{?[A-Za-z0-9_]+\}?"?\s*&&\s*\[\s*"?\$?\{?[A-Za-z0-9_]+\}?"?\s+-ge\s+[^]]*\]\s*$')
# 乙 = 条件が num_same_op <語> ただ一つ(先頭の ! は許す)。他の検めを継がぬ
RE_OTSU = re.compile(r'^!?\s*num_same_op\s+"?\$?\{?[A-Za-z0-9_]+\}?"?\s*$')
RE_FIX  = re.compile(r'^\s*fix_threshold\s+"?([A-Za-z0-9_$\{\}]+)"?\s+"?([^\s"]+)"?\s+"?([A-Za-z0-9_$\{\}]+)"?')

def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]

t0 = time.time(); kiz = time.strftime("%Y-%m-%dT%H:%M:%S%z")

mato = []
with open(TEIGI, encoding="utf-8") as fh:
    head = fh.readline().rstrip("\n").split("\t")
    if head[:2] != [u"層", u"file"]:
        sys.stderr.write("40 測れぬ: 31_teigi.tsv の冠が望みの形でない %r\n" % (head,))
        sys.exit(3)
    for ln in fh:
        c = ln.rstrip("\n").split("\t")
        if len(c) < 2:
            continue
        rel = c[1]
        if rel.startswith("scripts/") and rel not in mato:
            mato.append(rel)
mato.sort()
if len(mato) != 8:
    sys.stderr.write("40 測れぬ: 的 file = %d (望み 8) ―― 零を黙って出さぬ\n" % len(mato))
    sys.exit(4)

rows, shirase, kou, otsu, hei = [], [], [], [], []
shiki_all = 0
for rel in mato:
    p = os.path.join(ROOT, rel)
    src = open(p, encoding="utf-8").read().split("\n")
    # 呼び口(定義行・註行を除く num_same_op 出現行)
    yobi = []
    for i, ln in enumerate(src, 1):
        if not RE_CALL.search(ln):
            continue
        if RE_DEF.match(ln) or RE_CMT.match(ln):
            continue
        yobi.append((i, ln))
    # 此の器を通る閾(fix_threshold の呼び手)
    shiki = []
    for i, ln in enumerate(src, 1):
        m = RE_FIX.match(ln)
        if m:
            shiki.append((i, m.group(1), m.group(2), m.group(3)))
    for i, ln in yobi:
        mj = RE_JOU.match(ln)
        jou = mj.group(1) if mj else ln.strip()
        if RE_KOU.match(jou):
            kata = u"甲"; kou.append((rel, i))
        elif RE_OTSU.match(jou):
            kata = u"乙"; otsu.append((rel, i))
        else:
            kata = u"丙"; hei.append((rel, i))
        if shiki:
            shiki_n = len(shiki)
            shiki_s = " ".join("%s(既定%s)→%s" % (a, b, c) for _, a, b, c in shiki)
        else:
            # fix_threshold を経ぬ直呼び ―― 呼び行の変数名を其の儘の閾とする
            m = re.search(r'num_same_op\s+"?\$\{?([A-Za-z0-9_]+)\}?"?', ln)
            nm = m.group(1) if m else u"(引けぬ)"
            shiki_n = 1
            shiki_s = u"%s(直呼び・fix_threshold を経ぬ)" % nm
        shiki_all += shiki_n
        rows.append([rel, i, kata, sha16(p), shiki_n, ln.strip(), shiki_s])

# 輪(for _t in NAME:既定 …)で fix_threshold を回す呼び手の実数
RE_WA = re.compile(r'^\s*for\s+_t\s+in\s+(.*)$')
wa = {}
for rel in mato:
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read().split("\n")
    for i, ln in enumerate(src, 1):
        m = RE_WA.match(ln)
        if not m:
            continue
        blob, j = ln, i
        while blob.rstrip().endswith("\\") and j < len(src):
            blob += src[j]; j += 1
        names = re.findall(r'(?<![A-Za-z0-9_])([A-Z][A-Z0-9_]+):([0-9]+)', blob)
        if names:
            wa[rel] = (i, names)

K.kaku_tsv(os.path.join(BUNDLE, "nama", "40_bunrui.tsv"), rows,
           ["#生器", "呼び手行", "型", "sha16", "通す閾の本數", "呼び行(逐語)", "通す閾の名(既定)→受け皿"])

L = []
L.append(u"= 40 ―― ㋑ 呼び方の三分類(甲 / 乙 / 丙) =")
L.append(u"刻=%s  経過=%.2f 秒  rc=0" % (kiz, time.time() - t0))
L.append(u"歩き根=%s  的=nama/31_teigi.tsv の内 scripts/ のみ(★札の宣ではなく 30 の実測から引いた★)" % ROOT)
L.append(u"的 file = %d 本  呼び口 = %d 口" % (len(mato), len(rows)))
L.append(u"")
L.append(u"-- 分けの式(宣・此の器の字面其の物) --")
L.append(u"  条件部の抜き: %s  ―― 抜けぬ行は行全体を条件と見做す" % RE_JOU.pattern)
L.append(u"  甲: %s" % RE_KOU.pattern)
L.append(u"  乙: %s" % RE_OTSU.pattern)
L.append(u"  丙: 右の二つに当たらぬ物")
L.append(u"  ★排他性★: 一口は必ず一型にのみ入る(甲→乙→丙 の順に当てる)。甲∧乙 の重なりは構造上生ぜぬ")
L.append(u"    ―― 甲は条件の末に `] ` を要し、乙は num_same_op の引数で条件が尽きる事を要する。")
L.append(u"")
L.append(u"★甲 = %d 本 / 乙 = %d 本 / 丙 = %d 本★  (和 %d = 呼び口 %d)"
         % (len(kou), len(otsu), len(hei), len(kou) + len(otsu) + len(hei), len(rows)))
L.append(u"★本弾の要 ―― 乙 = %d 本★" % len(otsu))
L.append(u"  家老の見立 = 三本(stop_hook_inbox:65 / karo_mac_gate4:93 / karo_mac_dasumae_gate:60)")
mitate = [("scripts/stop_hook_inbox.sh", 65), ("scripts/checks/karo_mac_gate4.sh", 93),
          ("scripts/checks/karo_mac_dasumae_gate.sh", 60)]
L.append(u"  当席の測り = %s" % (" / ".join("%s:%d" % (a, b) for a, b in otsu)))
L.append(u"  ★見立⇔測り = %s★" % (u"一致" if sorted(otsu) == sorted(mitate) else u"★相違★"))
L.append(u"")
L.append(u"-- 型別の口(file:行 逐語) --")
for kata, lst in ((u"甲", kou), (u"乙", otsu), (u"丙", hei)):
    L.append(u"[%s] %d 口" % (kata, len(lst)))
    for rel, i in lst:
        r = [x for x in rows if x[0] == rel and x[1] == i][0]
        L.append(u"  %s:%d\t%s" % (rel, i, r[5]))
        L.append(u"      通す閾 %d 本 = %s" % (r[4], r[6]))
L.append(u"")
L.append(u"-- 何が違ふのか(字面から言へる事のみ) --")
L.append(u"  甲: num_same_op が通した後、★同じ演算子 [ -ge ] で 0 以上か★を重ねて見る。")
L.append(u"      ∴ 負(-5 等)は第二の関で落ちる。★但し 2^63 未満の巨大値は両関とも通る。★")
L.append(u"  乙: num_same_op 単独。num_same_op は [ v -ge 0 ] の rc が 0 でも 1 でも通す形ゆゑ、")
L.append(u"      ★「0 以上か」を見て居らぬ ―― 見たのは「比較器が扱へるか」だけ★。")
L.append(u"      ∴ 負も 2^63 未満の巨大値も素通りして下流へ入る。")
L.append(u"  ★両型に共通の穴★: 上限が無い。9223372036854775807 は甲でも乙でも通る。")
L.append(u"")
L.append(u"-- 母數の別(同じ「本」で二つを数へぬ為) --")
L.append(u"  呼び口(if 一行)  = %d 口 ―― 札の宣と同じ数へ方" % len(rows))
L.append(u"  通す閾(値の本数) = %d 本 ―― 一口が何本の閾を通すかは器ごとに違ふ" % shiki_all)
kou_s = sum(r[4] for r in rows if r[2] == u"甲")
otsu_s = sum(r[4] for r in rows if r[2] == u"乙")
L.append(u"    内 甲を通る閾 = %d 本 / ★乙を通る閾 = %d 本★" % (kou_s, otsu_s))
L.append(u"  ★但し上の「本」は fix_threshold ★呼び手行★ の数である ―― 輪で回す口が在る★")
if wa:
    tsuika = 0
    for rel, (i, names) in sorted(wa.items()):
        L.append(u"    %s:%d は for の輪で %d 個の名を回す = %s"
                 % (rel, i, len(names), " ".join("%s:%s" % (a, b) for a, b in names)))
        tsuika += len(names) - 1
    L.append(u"    ∴ ★値の本数で数へ直せば %d + %d = %d 本★(内 甲 %d / 乙 %d)"
             % (shiki_all, tsuika, shiki_all + tsuika, kou_s + tsuika, otsu_s))
else:
    L.append(u"    輪で回す口 = 0(∴ 呼び手行の数 = 値の本数)")
K.kaku(os.path.join(BUNDLE, "nama", "40_bunrui.txt"), u"\n".join(L))
sys.stderr.write("40 done kou=%d otsu=%d hei=%d shiki=%d\n" % (len(kou), len(otsu), len(hei), shiki_all))

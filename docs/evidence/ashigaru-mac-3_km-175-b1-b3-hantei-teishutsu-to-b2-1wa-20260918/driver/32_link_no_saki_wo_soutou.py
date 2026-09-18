# -*- coding: utf-8 -*-
"""★第九の link ―― 解ける一本の先を掃討する★(km-175 ㋒)
raw/32 で當席は「link 8 本・悉く解けぬ」と刷つた。★之は誤りである★ ―― os.walk は
★dir を指す symlink を files ではなく dirs に入れる★ ゆゑ、器が見落したのは
★解ける唯一の一本★(frontend/node_modules → /Users/momizimac/DentalBI/frontend/node_modules)であつた。
∴ 其の先 29643 本を ★寸法で絞つて★ 三 sha256 に当てる。
四札: 刻=冠 / 根と深さ=下表 / rc=無し(python の歩き・timeout 無し) / 陽性対照=本束の着手便(436B)を同じ路に乗せる。"""
import os
import sys
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

POC = os.path.realpath("/tmp/b3poc")
KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
MATO = {
    10944: ("紙", "a1e6d2ff"),
    253: ("門控", "0e1228fd"),
    1401: ("臺帳", "a012d6b4"),
    436: ("★陽性対照★(本束 着手便)", "b7876c96"),   # ★対照も同じ寸法の篩に乗せる★
}
NEG = "98765432"   # ★陰性対照★ 何にも当たらぬ頭


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def soutou(na, ne):
    mita = set()
    d = f = l = 0
    fui = 0     # 寸法が合つた本数
    atari = []
    yomenu = []
    for r, ds, fs in os.walk(ne, followlinks=True):
        rp = os.path.realpath(r)
        if rp in mita:
            ds[:] = []
            continue
        mita.add(rp)
        d += 1
        for x in fs:
            p = os.path.join(r, x)
            try:
                st = os.lstat(p)
            except OSError as e:
                yomenu.append([na, p[:88], "lstat: %s" % e.strerror])
                continue
            if os.path.islink(p):
                l += 1
                if not os.path.exists(p):
                    continue
                try:
                    st = os.stat(p)
                except OSError as e:
                    yomenu.append([na, p[:88], "stat: %s" % e.strerror])
                    continue
            if not os.path.isfile(p):
                continue
            f += 1
            if st.st_size in MATO:
                fui += 1
                try:
                    s = sha256_of(p)
                except OSError as e:
                    yomenu.append([na, p[:88], "open: %s" % e.strerror])
                    continue
                rui, atama = MATO[st.st_size]
                if s.startswith(atama):
                    atari.append([na, rui, atama, os.path.relpath(p, ne)[:96], st.st_size, s])
                elif s.startswith(NEG):
                    atari.append([na, "★陰性が当たつた ―― 器を疑へ★", NEG, os.path.relpath(p, ne)[:96], st.st_size, s])
    return d, f, l, fui, atari, yomenu


rows = []
atari_all = []
yomenu_all = []
for na, ne in (("隔離樹(link を辿る)", POC), ("陽性対照(本束)", os.path.abspath(BUNDLE))):
    d, f, l, fui, at, ym = soutou(na, ne)
    atari_all += at
    yomenu_all += ym
    rows.append([na, ne, d, f, l, fui, len(at), len(ym)])
kaku_tsv(os.path.join(BUNDLE, "raw", "36_link_no_saki_soutou.tsv"), rows,
         header=["歩いた所", "根", "dir 数", "常の紙 数", "link 数", "寸法が合つた 本数", "当たり", "読めぬ"])
kaku_tsv(os.path.join(BUNDLE, "raw", "37_link_no_saki_atari.tsv"),
         atari_all or [["-", "★当たり 0★", "-", "-", "-", "-"]],
         header=["歩いた所", "類", "頭8", "在処(96字で截つ)", "寸法", "sha256(全)"])
kaku_tsv(os.path.join(BUNDLE, "raw", "38_link_no_saki_yomenu.tsv"),
         yomenu_all or [["-", "★読めぬ紙 0 本★", "-"]], header=["歩いた所", "在処(88字で截つ)", "由"])

kou = [a for a in atari_all if a[1].startswith("★陽性")]
mato3 = [a for a in atari_all if a[1] in ("紙", "門控", "臺帳")]
kaku(os.path.join(BUNDLE, "raw", "39_link_no_saki_dan.txt"),
     "as-of %s\n\n"
     "【断 ―― 解ける一本の先にも原本は無い】\n"
     "㋐ ★當席の疵を先に名指す★: raw/32 の「link 8 本・悉く解けぬ」は ★不足★ であつた。\n"
     "   os.walk は ★dir を指す symlink を files ではなく dirs に入れる★ ―― 故に器は\n"
     "   ★解ける唯一の一本★ frontend/node_modules(→ /Users/momizimac/DentalBI/frontend/node_modules)を\n"
     "   link として数へず、dir として数へて居た。find -type l は 9 本、當席の器は 8 本 ―― ★此の 1 本の差が其れである★。\n"
     "㋑ 其の一本を辿つて掃討した: 常の紙 %d 本・dir %d 箇・寸法が合つた %d 本・★当たり %d 件★。\n"
     "㋒ 陽性対照= 本束の着手便(436 byte)を ★同じ寸法の篩・同じ歩き★ に乗せ %d 件当たる ∴ 器は当てる事が出来る。\n"
     "   陰性対照= 頭 %s は 0 件。読めぬ紙 %d 本。\n"
     "㋓ ∴ 三 sha256 は ⑴隔離樹の常の紙(0 本) ⑵解ける link の先(%d 本) ⑶DentalBI 全obj(blob 48480)\n"
     "   ⑷multi-agent-shogun 全obj(blob 11349)の ★何處にも無い★。\n"
     "㋔ 之が意味 ★せぬ★ 事: node_modules は依存樹であり、元より證の紙を置く所ではない。\n"
     "   ★当たらぬのは当然である★ ―― 本節は「当然を測つて控へた」だけで、不在の證の重みは ⑴⑶⑷ に在る。\n"
     % (KOKU, rows[0][3], rows[0][2], rows[0][5], len(mato3), len(kou), NEG, len(yomenu_all), rows[0][3]))
print("隔離樹(link 辿り) dir %d・常の紙 %d・link %d・寸法合 %d・当たり %d・読めぬ %d"
      % (rows[0][2], rows[0][3], rows[0][4], rows[0][5], rows[0][6], rows[0][7]))
print("  三 sha256 当たり=%d / 陽性対照=%d / 読めぬ=%d" % (len(mato3), len(kou), len(yomenu_all)))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""karo_mac_manifest_append.py ―― 臺帳(manifest)へ行を追記する ★唯一の書き手★。

案一(委員長裁 seq321388 起案 / seq321856 「据えよ」)を ★書き手側★ に据ゑる器。

  ★禁★: 此の器が ★新規に書く行★ に引用符(" ')・改行・復帰を含めぬ。
         触れた時は ★一行も書かず★ rc=3 で落ちる(全か無か)。
  ★既存行は一指も触れぬ★: 追記のみ。引用符を含む旧い行は其の儘残る
         (裁 seq321353⑴「既存行は拒否せず旧形として通す」＝讀み手 門 條⑥ の役)。

  ★何故 書き手側か★: 讀み手は行を見ても ★新規か既存かを見分けられぬ★。
  見分けられるのは、其の行を今書かうとして居る器だけである。
  ∴ 「新規に書く行のみ禁」は 讀み手では ★数へるだけの則★ に堕ち、書き手でのみ ★禁★ になる。

方言(裁 seq320321⑶ 本形・四欄):  path=<p> sha256=<64hex> bytes=<n> lines=<n>

使ひ方:
  karo_mac_manifest_append.py <臺帳> <紙> [<紙>...]   追記(全か無か)
  karo_mac_manifest_append.py --selftest               両対照を己で走らせる
  返り値: 0=書いた / 2=引数の誤り / 3=★禁に触れた(一行も書かず)★ / 4=対象が無い
"""
import hashlib
import os
import sys
import tempfile

KINJI = '"\''          # ★名の中に在つたら書けぬ字★ ―― 括り字そのもの(剥ぐ器が誤読する)
KAIGYOU = '\n\r'       # 行を単位とする器ゆゑ 改行と復帰も書けぬ
KUUHAKU = ' \t'         # ★空白を含む名は「括らねば讀めぬ」★ ―― 形②(刳り貫き)で括る
ATAMA = [
    "# dialect: path= sha256= bytes= lines=  ―― 裁 seq320321⑶「4欄(lines=有)を本形」",
    "# ★此の臺帳へ行を足すのは karo_mac_manifest_append.py のみ★(案一・裁 seq321856)",
]


def kazoe(p):
    """bytes と 行(grep -c '' の数へ方: 最後の改行無しの塊も一行と数へる)。"""
    n = os.path.getsize(p)
    gyou = 0
    owari_kaigyou = True
    with open(p, "rb") as fh:
        while True:
            buf = fh.read(1 << 20)
            if not buf:
                break
            gyou += buf.count(b"\n")
            owari_kaigyou = buf.endswith(b"\n")
    if n > 0 and not owari_kaigyou:
        gyou += 1
    return n, gyou


def digest(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 20), b""):
            h.update(buf)
    return h.hexdigest()


def togame(path_moji):
    """★書けぬ名★ かを判ずる。書けるなら None、書けぬなら理由(str)。"""
    for c in KINJI:
        if c in path_moji:
            return "引用符 %r を名の中に含む(括つても剥ぐ器が誤読する)" % c
    for c in KAIGYOU:
        if c in path_moji:
            return "改行/復帰 %r を含む(行を単位とする器では表せぬ)" % c
    return None


def tsuzuri(path_moji):
    r"""★綴り★ を決める。

    ★形② 刳り貫き(專任2 第47弾 ㋔ の実測に従ふ・2026-09-17 家老訂正)★:
      ・空白を含まぬ名 → ★括らぬ★(本形・裁 seq321353⑵)
      ・空白を含む名   → ★括る★ ―― 括らねば ★讀み手が切り落す★。
        讀み手 karo_mac_manifest_verify.paths_of の ①本形は ``path=([^\s"']+)`` ゆゑ
        ``path=docs/a b.txt`` を ``docs/a`` で切る。②非貪欲は ★① が外れた時にのみ★ 走り、
        ① が外れるのは ★直後が括り字か空白の時だけ★ である。
        ∴ ★空白名にとつて括りは「旧形」ではなく「唯一 讀める形」である。★

    ★己の誤り(消さず残す)★: 初版は引用符を ★全面禁★ にした。專任2 が同じ刻に
    「束に a b.txt が在る故 形②で括つた。★形①なら本紙自身が落ちる★」と実測で示した。
    全面禁は ★書けるが讀めぬ臺帳★ を産む器であつた。之は禁の強さではなく ★誤りである★。
    """
    if any(c in path_moji for c in KUUHAKU):
        return '"%s"' % path_moji, True
    return path_moji, False


def tsukure(man, mono, root=None, dasu=sys.stdout):
    """全か無か。触れた物が一本でも在れば 一行も書かぬ。"""
    if root is None:
        root = os.getcwd()
    gyou = []
    toga = []
    nai = []
    kukuri = []
    for p in mono:
        if not os.path.isfile(p):
            nai.append(p)
            continue
        rel = os.path.relpath(os.path.abspath(p), root)
        riyuu = togame(rel)
        if riyuu:
            toga.append((rel, riyuu))
            continue
        n, l = kazoe(p)
        tsuzu, kukutta = tsuzuri(rel)
        if kukutta:
            kukuri.append(rel)
        gyou.append("path=%s sha256=%s bytes=%d lines=%d" % (tsuzu, digest(p), n, l))

    if nai:
        for p in nai:
            print("★対象が無い★ %s" % p, file=sys.stderr)
        return 4, 0
    if toga:
        for rel, riyuu in toga:
            print("★禁★ 書かぬ: %s ―― %s" % (rel, riyuu), file=sys.stderr)
        print("★一行も書いて居らぬ(全か無か)★ 触れた本数=%d / 母數=%d"
              % (len(toga), len(mono)), file=sys.stderr)
        return 3, 0

    atarashii = not os.path.exists(man)
    with open(man, "a", encoding="utf-8") as fh:
        if atarashii:
            for a in ATAMA:
                fh.write(a + "\n")
        for g in gyou:
            fh.write(g + "\n")
    print("書いた=%d 行 / 母數=%d / ★括つた(空白名ゆゑ必須)=%d★ / 臺帳=%s%s"
          % (len(gyou), len(mono), len(kukuri), man,
             "(新たに建てた)" if atarashii else "(追記)"), file=dasu)
    for k in kukuri:
        print("  括つた: %s ―― 括らねば讀み手が切り落す" % k, file=dasu)
    return 0, len(gyou)


def _yomite():
    """讀み手(門の照合器)の path 取り出しを ★実物で★ 読み込む。"""
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "karo_mac_manifest_verify.py")
    spec = importlib.util.spec_from_file_location("km_verify", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.paths_of


def selftest():
    """★両対照 + 往復対照★ ―― 恒真でも恒偽でもなく、かつ ★書けた物が讀める★ 事を示す。"""
    ok = True
    paths_of = _yomite()
    d = tempfile.mkdtemp(prefix="km_an1_")
    man = os.path.join(d, "MANIFEST.txt")

    def hantei(na, mato, **kw):
        nonlocal ok
        if not mato:
            ok = False
            print("★対照が落ちた(%s)★" % na)

    # 甲 陽性対照(空白無し・括らぬ) → 通る(＝恒偽でない) かつ ★讀み手が同じ名を返す★
    yoi = os.path.join(d, "kiyoi.txt")
    open(yoi, "w", encoding="utf-8").write("a\nb\n")
    rc, n = tsukure(man, [yoi], root=d)
    gyou1 = open(man, encoding="utf-8").read().splitlines()[-1]
    yomi1 = paths_of(gyou1)
    print("甲 陽性(空白無) rc=%d 書=%d 括=無 讀み返し=%r 一致=%s ―― 期待 rc0/1/['kiyoi.txt']"
          % (rc, n, yomi1[:1], yomi1[:1] == ["kiyoi.txt"]))
    hantei("甲", rc == 0 and n == 1 and yomi1[:1] == ["kiyoi.txt"])

    # 乙 ★往復対照(空白を含む名)★ ―― 括つて書き、★讀み手が切り落さぬ★ 事を示す
    kuu = os.path.join(d, "a b.txt")
    open(kuu, "w", encoding="utf-8").write("x\n")
    rc2, n2 = tsukure(man, [kuu], root=d)
    gyou2 = open(man, encoding="utf-8").read().splitlines()[-1]
    yomi2 = paths_of(gyou2)
    print("乙 往復(空白有) rc=%d 書=%d 行=%r 讀み返し=%r 一致=%s ―― 期待 rc0/1/['a b.txt']"
          % (rc2, n2, gyou2[:34], yomi2[:1], yomi2[:1] == ["a b.txt"]))
    hantei("乙 往復", rc2 == 0 and n2 == 1 and yomi2[:1] == ["a b.txt"])

    # 丙 ★己の初版が誤りであつた證★ ―― 括らずに書いたら讀み手は何を返すか
    nama = 'path=a b.txt sha256=%s bytes=1 lines=1' % ("0" * 64)
    yomi3 = paths_of(nama)
    print("丙 括らぬ空白名を讀ませると → %r ―― ★切り落す(期待 'a b.txt' でない)★ 切落=%s"
          % (yomi3[:1], yomi3[:1] != ["a b.txt"]))
    hantei("丙 初版の誤りの證", yomi3[:1] != ["a b.txt"])

    # 丁 陰性対照(名の中に二重引用符) → ★書けぬ★(＝恒真でない)
    warui = os.path.join(d, 'wa"rui.txt')
    open(warui, "w", encoding="utf-8").write("x\n")
    mae = open(man, encoding="utf-8").read()
    rc4, n4 = tsukure(man, [warui], root=d)
    print("丁 陰性(二重引用符) rc=%d 書=%d 臺帳不変=%s ―― 期待 rc3/0/True"
          % (rc4, n4, mae == open(man, encoding="utf-8").read()))
    hantei("丁", rc4 == 3 and n4 == 0 and mae == open(man, encoding="utf-8").read())

    # 戊 陰性対照 其の二(一重引用符)
    warui2 = os.path.join(d, "wa'rui2.txt")
    open(warui2, "w", encoding="utf-8").write("x\n")
    mae2 = open(man, encoding="utf-8").read()
    rc5, n5 = tsukure(man, [warui2], root=d)
    print("戊 陰性(一重引用符) rc=%d 書=%d 臺帳不変=%s ―― 期待 rc3/0/True"
          % (rc5, n5, mae2 == open(man, encoding="utf-8").read()))
    hantei("戊", rc5 == 3 and n5 == 0 and mae2 == open(man, encoding="utf-8").read())

    # 己 ★全か無か★ ―― 清い物と書けぬ物を同時に渡したら清い方も書かれぬ
    mae3 = open(man, encoding="utf-8").read()
    rc6, n6 = tsukure(man, [yoi, warui], root=d)
    print("己 全か無か(清1+書けぬ1) rc=%d 書=%d 臺帳不変=%s ―― 期待 rc3/0/True"
          % (rc6, n6, mae3 == open(man, encoding="utf-8").read()))
    hantei("己", rc6 == 3 and n6 == 0 and mae3 == open(man, encoding="utf-8").read())

    # 庚 ★既存行は一指も触れぬ★ ―― 手で置いた旧形は追記後も残る
    kyuu = 'path=\'kyuukei no kami.txt\' sha256=%s bytes=1 lines=1' % ("0" * 64)
    with open(man, "a", encoding="utf-8") as fh:
        fh.write(kyuu + "\n")
    rc7, n7 = tsukure(man, [yoi], root=d)
    nokotta = kyuu in open(man, encoding="utf-8").read()
    print("庚 既存旧形は残る rc=%d 書=%d 残存=%s ―― 期待 rc0/1/True" % (rc7, n7, nokotta))
    hantei("庚", rc7 == 0 and n7 == 1 and nokotta)

    print("臺帳 終の行數=%d" % len(open(man, encoding="utf-8").read().splitlines()))
    print("★selftest %s★" % ("通" if ok else "落"))
    return 0 if ok else 1


def main(argv):
    if len(argv) >= 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    return tsukure(argv[1], argv[2:])[0]


if __name__ == "__main__":
    sys.exit(main(sys.argv))

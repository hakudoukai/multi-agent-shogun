#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋓ 直しの案を ★⑶(c1486ca1)の現物から★ 建てる器。

★手で打ち直さぬ★ ―― ⑶ を読み、逐語の置換を当てて案を産む。置換が當らねば assert で死ぬ
(memory「str.replace patch must assert count」―― 當らぬ置換は器を黙つて素通りさせる)。

案の三:
  案戊  則②の捕り物から ★末尾の 欄=値 を剥ぐ★ (方言乙 のみを狙ふ・km-117 で既に測つた物と同形)
  案庚  方言丙(sha が前)の為に ★第四の則★ を足す ―― path= から行末まで捕り、末尾の 欄=値 を剥ぐ
  案己  案戊 ＋ 案庚 (両方)

★戻し方★は各案の頭の註に逐語で書く。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

MOTO = os.path.join(BUNDLE, "_ki", "san_c1486ca1.py")
AN = os.path.join(BUNDLE, "_an")

# ―― 剥ぎの一行(三案で共有する逐語)
HAGI = ('    _t = re.sub(r"(?:[ \\t]+[A-Za-z_][A-Za-z0-9_]*=[^ \\t]*)+$", "", _t)\n'
        "    _t = _dequote(_t)\n")

# 案戊 = 則②の捕り物に剥ぎを当てる
MOTO_BO = ("    m2 = re.search(r\"(?:^|\\s)path=(.+?)[ \\t]+sha256=\", line)\n"
           "    if m2:\n"
           "        _t = _dequote(m2.group(1))\n"
           "        if _t:\n")
ATO_BO = ("    m2 = re.search(r\"(?:^|\\s)path=(.+?)[ \\t]+sha256=\", line)\n"
          "    if m2:\n"
          "        # ★案戊★ 則②の非貪欲は path= から次の sha256= まで ★他の欄ごと★ 呑む。\n"
          "        #   ★剥ぎを _dequote の ★前★ に置く★ ―― 後に置くと _dequote の .strip() が\n"
          "        #   ★名の末尾の空白を食ふ★(km-120 ㋒ 実測: km-83/MANIFEST.txt:270 の\n"
          "        #   `path=\\\"40_doku/otsu_suna/ \\\"` = 名が空白一字で終る現物の行が 偽の赤 に成る)。\n"
          "        # 戻し方: 次の二行を `_t = _dequote(m2.group(1))` 一行へ戻せば ⑶(c1486ca1)。\n"
          "        _t = re.sub(r\"(?:[ \\t]+[A-Za-z_][A-Za-z0-9_]*=[^ \\t]*)+$\", \"\", m2.group(1))\n"
          "        _t = _dequote(_t)\n"
          "        if _t:\n")

# 案庚 = 第四の則(行末まで捕り、末尾の欄を剥ぐ)を for の前に足す
MOTO_KOU = ("    for _pat in (r'(?:^|\\s)path=([^\\s\"\\']+)',  # ①本形")
ATO_KOU = (
    "    # ★案庚★ 方言丙(``sha256=`` が ``path=`` より前)では則②が構造上當らぬ。\n"
    "    #   其の時 ①③ は空白で切る故 ★短縮 `a` だけが候補に成る★(km-120 ㋐ 丙の五面)。\n"
    "    #   ∴ path= から★行末まで★捕り、末尾の ``欄=値`` を剥いだ物を ★唯一の候補★ とする。\n"
    "    #   戻し方: 次の `if not m2:` の塊を除けば ⑶(c1486ca1) へ戻る。\n"
    "    if not m2:\n"
    "        m4 = re.search(r\"(?:^|\\s)path=(.+)$\", line)\n"
    "        if m4:\n"
    "            _t = re.sub(r\"(?:[ \\t]+[A-Za-z_][A-Za-z0-9_]*=[^ \\t]*)+$\", \"\", m4.group(1))\n"
    "            _t = _dequote(_t)\n"
    "            if _t:\n"
    "                return [_t]\n"
    + MOTO_KOU)


def tateru(name, henkan):
    s = open(MOTO, encoding="utf-8").read()
    for moto, ato, nani in henkan:
        n = s.count(moto)
        assert n == 1, "★置換が %d 箇所に當つた(1 を期待)★ 案=%s 何=%s" % (n, name, nani)
        s = s.replace(moto, ato, 1)
    p = os.path.join(AN, name + ".py")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)
    return p


def main():
    log = ["# ㋓ 案を建てた(元 = _ki/san_c1486ca1.py = ⑶ = 枝 karo-mac/daini-no-for-wo-nozoku-20260917 の commit c1486ca1)"]
    tama = [("an_bo_km120", [(MOTO_BO, ATO_BO, "案戊の剥ぎ")]),
            ("an_kou_km120", [(MOTO_KOU, ATO_KOU, "案庚の第四則")]),
            ("an_ki_km120", [(MOTO_BO, ATO_BO, "案戊の剥ぎ"), (MOTO_KOU, ATO_KOU, "案庚の第四則")])]
    import hashlib
    for name, henkan in tama:
        p = tateru(name, henkan)
        b = open(p, "rb").read()
        log.append("%s\t%s\tsha256=%s\tbytes=%d\tlines=%d"
                   % (name, os.path.relpath(p, BUNDLE), hashlib.sha256(b).hexdigest(),
                      len(b), b.count(b"\n")))
    # ★己を検める★ ―― 建てた案が python として読めるか
    import py_compile
    for name, _ in tama:
        p = os.path.join(AN, name + ".py")
        try:
            py_compile.compile(p, cfile=os.path.join(BUNDLE, "raw", "_pyc_" + name), doraise=True)
            log.append("py_compile %s = 可" % name)
        except Exception as e:  # noqa: BLE001
            log.append("py_compile %s = ★不可★ %s" % (name, e))
        finally:
            q = os.path.join(BUNDLE, "raw", "_pyc_" + name)
            if os.path.exists(q):
                os.remove(q)
    kaku(os.path.join(BUNDLE, "raw", "30_an_wo_tateta.txt"), "\n".join(log))
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())

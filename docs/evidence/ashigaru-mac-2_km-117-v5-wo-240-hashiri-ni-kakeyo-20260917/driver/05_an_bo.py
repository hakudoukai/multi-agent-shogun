#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★三択の外★ の一本を建てて測る ―― 案戊 = v5 −(第二の for)＋(則②の捕り物から末尾の欄を剥ぐ)。

何故建てるか: ㋓ で ★負対照(区辛・清い行)が 方言乙 で落ちる★ 事が出た。
v5・案甲鎖・案乙 は rc1(偽の赤)。因は則②の非貪欲が `path=` から次の `sha256=` まで
★他の欄ごと★ 呑む事に在る(捕り物 = 'kiyoi.txt bytes=6 lines=1')。

★「①へ落とす」路は採れぬ★ ―― 測つた:
  候補を二本(②の捕り物・①の捕り物)にすると 区甲(prefix=file・実名無・宣sha=sha(prefix))で
  短縮 'a' が昇り ★偽の通★ に成る。之は此の一連の作業が塞がうとして居る当の穴である。
∴ 候補を増やさず ★捕り物其の物を正す★: 末尾に連なる `<鍵>=<値>` の欄を剥ぐ。

★之は断ではない★(㋔ の断は三択の内から出す)。家老の判断の材料として ★測つて★ 置く。
建てる物: _an/an_bo.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)

SEED = os.path.join(BUNDLE, "_an", "v5_daini_nashi.py")   # ★既に第二の for を除いた版★
DST = os.path.join(BUNDLE, "_an", "an_bo.py")

OLD = """        _t = _dequote(m2.group(1))
        if _t:"""
NEW = """        _t = _dequote(m2.group(1))
        # ★案戊★ 則②の非貪欲は `path=` から次の `sha256=` まで ★他の欄ごと★ 呑む。
        #   例: `path=kiyoi.txt bytes=6 lines=1 sha256=…` → 捕り物 'kiyoi.txt bytes=6 lines=1'
        #   ∴ 末尾に連なる `<鍵>=<値>` の欄を剥ぐ。★候補は増やさぬ★(増やせば短縮が昇る路が開く)。
        _t = re.sub(r"(?:[ \\t]+[A-Za-z_][A-Za-z0-9_]*=[^ \\t]*)+$", "", _t)
        _t = _dequote(_t)
        if _t:"""


def main():
    with open(SEED, encoding="utf-8") as fh:
        s = fh.read()
    n = s.count(OLD)
    if n != 1:
        print(f"★落ち★ 錠が {n} 本(1 本でなければ据ゑぬ)", file=sys.stderr)
        return 3
    t = s.replace(OLD, NEW, 1)
    with open(DST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(t)
    import py_compile
    py_compile.compile(DST, cfile=os.path.join(BUNDLE, "raw", "_x.pyc"), doraise=True)
    os.remove(os.path.join(BUNDLE, "raw", "_x.pyc"))
    sys.path.insert(0, HERE)
    from kaki import kaku
    kaku(os.path.join(BUNDLE, "raw", "05_an_bo_tateta.txt"),
         "# 案戊 を建てた證(km-117 ㋔ 別紙)\n"
         f"# 種 = {os.path.relpath(SEED, BUNDLE)}(v5 − 第二の for)\n"
         f"# 出 = {os.path.relpath(DST, BUNDLE)}\n"
         f"# 錠の本数 = {n}(1 でなければ据ゑぬ)\n"
         "# 足した塊(逐語):\n" + "".join("    " + x + "\n" for x in NEW.split("\n")))
    print(f"建てた: {DST}(錠 {n} 本)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

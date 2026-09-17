#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""案を三つ(＋一つ)★束の中の写し★として建てる器 ―― km-114 ㋒ の前段。

★scripts/ 配下の器には一指も触れぬ★(変更統制・札 kinshi)。
種は家老 km-113 束の _ver/ から引く(取り出さずに引いてよい・札 uketori_jouken⑹)。

建てる物(束内 _an/ の下):
  an_kou_kusari.py  案甲-鎖  則②を★無条件で先頭★・鎖(if-not-m 連鎖＝候補は一つ)
  an_kou_retsu.py   案甲-列  則②を★無条件で先頭★・列(v4 の列挙の順を替へる丈)
  an_otsu.py        案乙     行に ` sha256=` が在る時に限り則②を先頭(条件付・鎖)
  an_hei.py         案丙     v4＋★二つ以上 disk に在れば「曖昧」で鳴らす★

★字面で行番号を打たぬ★(memory「Never hardcode a line number; locate by verbatim」)。
★置換は必ず件数を検める★(memory「str.replace patch must assert count」) ―― 合はねば rc=3 で落ちる。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

SEED = os.path.join(
    BUNDLE, "..",
    "karo-mac_km-113-kuuhaku-wo-fukumu-na-ga-arawasenu-kizu-20260917", "_ver")

ANCHOR_V2_HEAD = "# ①本形"                      # ①本形
ANCHOR_V2_TAIL = "out.append(_dequote(m.group(1)))"
ANCHOR_V4_FOR = "    for _pat in ("


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read().split("\n")


def one(lines, needle, what):
    hit = [i for i, ln in enumerate(lines) if needle in ln]
    if len(hit) != 1:
        print(f"★落ち★ {what}: 錠 '{needle}' が {len(hit)} 本 "
              f"(1 本でなければ据ゑぬ)", file=sys.stderr)
        raise SystemExit(3)
    return hit[0]


def chain_block(order, cond=False):
    """鎖形(候補は一つ)の block を組む。order は '②①③' 等の並び。"""
    pat = {
        "①": (r"""r'(?:^|\s)path=([^\s"\']+)'""", "①本形"),
        "②": (r'''r"(?:^|\s)path=(.+?)[ \t]+sha256="''', "②非貪欲"),
        "③": (r'''r"(?:^|\s)path=(\S+)"''', "③従来形"),
    }
    if cond:
        a = ", ".join(pat[k][0] for k in order)
        b = ", ".join(pat[k][0] for k in "①②③")
        return [
            '    # ★案乙★ 行に ` sha256=` が在る時に限り 則② を先頭へ(条件付・鎖)',
            '    if re.search(r"[ \\t]sha256=", line):',
            f'        _pats = ({a},)',
            '    else:',
            f'        _pats = ({b},)',
            '    m = None',
            '    for _p in _pats:',
            '        m = re.search(_p, line)',
            '        if m:',
            '            break',
            '    if m:',
            '        out.append(_dequote(m.group(1)))',
        ]
    out = [f'    # ★案甲-鎖★ 順＝{order}・鎖(if-not-m 連鎖＝候補は一つ)']
    for n, k in enumerate(order):
        ind = "    " if n == 0 else "        "
        if n:
            out.append("    if not m:")
        out.append(f"{ind}m = re.search({pat[k][0]}, line)  # {pat[k][1]}")
    out += ["    if m:", "        out.append(_dequote(m.group(1)))"]
    return out


def build_chain(name, order, cond=False):
    src = read(os.path.join(SEED, "v2_originmain.py"))
    i = one(src, ANCHOR_V2_HEAD, name)
    j = one(src, ANCHOR_V2_TAIL, name)
    if j < i:
        print("★落ち★ 錠の前後が逆", file=sys.stderr)
        raise SystemExit(3)
    new = src[:i] + chain_block(order, cond) + src[j + 1:]
    return new, (i, j, len(src), len(new))


def build_retsu():
    """案甲-列 ―― v4 の列挙の★順だけ★を ②①③ へ替へる。"""
    src = read(os.path.join(SEED, "v4_naoshita.py"))
    i = one(src, ANCHOR_V4_FOR, "an_kou_retsu")
    blk = [
        '    # ★案甲-列★ v4 の列挙の★順を ②①③ へ★(列挙はその儘)',
        '    for _pat in (r"(?:^|\\s)path=(.+?)[ \\t]+sha256=",  # ②非貪欲(先頭)',
        '                 r\'(?:^|\\s)path=([^\\s"\\\']+)\',  # ①本形',
        '                 r"(?:^|\\s)path=(\\S+)"):  # ③従来形',
    ]
    new = src[:i] + blk + src[i + 3:]
    return new, (i, i + 2, len(src), len(new))


def build_hei():
    """案丙 ―― v4 ＋ 曖昧(候補が二つ以上 disk に在る)で鳴らす。"""
    src = read(os.path.join(SEED, "v4_naoshita.py"))
    n_init = one(src, "ok = ng = miss = unreadable = 0", "an_hei init")
    src[n_init] = src[n_init] + "\n    aimai = 0            # ★案丙★ 候補が二つ以上 disk に在る行"
    n_found = one(src, "        found = None", "an_hei loop")
    tail = one(src, "            if found:", "an_hei loop tail")
    blk = [
        '        # ★案丙★ 候補を★悉く disk へ問ふ★ ―― 二つ以上在れば 臺帳 の主張 が 一意に決まらぬ。',
        '        #   ★定めぬ★でなく★鳴らす★(default-deny) ―― 選んで通すのが fail-open の根であった。',
        '        hits = []',
        '        for p in cands:',
        '            for b in bases:',
        '                cand = os.path.join(b, p) if b else p',
        '                if os.path.isfile(cand):',
        '                    hits.append((p, cand))',
        '                    break',
        '        if len(hits) >= 2:',
        '            aimai += 1',
        '            bad.append(("曖昧", " ‖ ".join(h[0] for h in hits)[:100]))',
        '            continue',
        '        found = hits[0] if hits else None',
    ]
    src = src[:n_found] + blk + src[tail + 2:]
    n_pr = one(src, "一致 ★{ok}★", "an_hei print")
    src[n_pr + 1] = src[n_pr + 1].rstrip()
    # 印字の二行目(母數)の直後へ曖昧を足す
    n_bo = one(src, "(母數 {ok + ng + miss + unreadable})", "an_hei bosuu")
    src[n_bo] = src[n_bo].replace(
        "(母數 {ok + ng + miss + unreadable})",
        "曖昧 {aimai}  (母數 {ok + ng + miss + unreadable + aimai})")
    n_rc = one(src, "return 0 if (ng == 0 and miss == 0", "an_hei rc")
    src[n_rc] = src[n_rc].replace(
        "ng == 0 and miss == 0 and unreadable == 0 and ok > 0",
        "ng == 0 and miss == 0 and unreadable == 0 and aimai == 0 and ok > 0")
    return src, (n_found, tail, 0, len(src))


def main():
    outdir = os.path.join(BUNDLE, "_an")
    os.makedirs(outdir, exist_ok=True)
    rows = []
    plans = [
        ("an_kou_kusari.py", lambda: build_chain("an_kou_kusari", "②①③")),
        ("an_otsu.py", lambda: build_chain("an_otsu", "②①③", cond=True)),
        ("an_kou_retsu.py", build_retsu),
        ("an_hei.py", build_hei),
    ]
    for name, fn in plans:
        new, meta = fn()
        txt = "\n".join(new)
        if not txt.endswith("\n"):
            txt += "\n"
        with open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt)
        import py_compile
        try:
            py_compile.compile(os.path.join(outdir, name), cfile=os.path.join(
                outdir, "_x.pyc"), doraise=True)
        except Exception as e:                                  # noqa: BLE001
            print(f"★落ち★ {name} が py_compile で落ちた: {e}",
                  file=sys.stderr)
            raise SystemExit(3)
        rows.append([name, len(new), meta[0], meta[1]])
    if os.path.exists(os.path.join(outdir, "_x.pyc")):
        os.remove(os.path.join(outdir, "_x.pyc"))
    body = ["# 案を建てた証(km-114 ㋒前段)",
            "# 種 = " + os.path.relpath(SEED, BUNDLE),
            "# name\tlines\tanchor_head\tanchor_tail"]
    for r in rows:
        body.append("\t".join(str(x) for x in r))
    kaku(os.path.join(BUNDLE, "raw", "00_an_wo_tateta.txt"), "\n".join(body))
    print("\n".join(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())

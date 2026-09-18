# -*- coding: utf-8 -*-
"""種を作る ―― ★現物は後で片付け、姿(hex と sha256)は紙に残す★(km-183 の條に従ふ)。"""
import hashlib
import os
import sys

TANE = [
    # (名, bytes, 何を問ふか, 條②は鳴るべきか(法), 條③, 條④)
    ("f01_kirei.txt",        b"a\nb\n",          "清い紙(陰性対照)",                 False, False, False),
    ("f02_matsubi_space.txt", b"a \nb\n",        "行末に空白1(陽性対照)",             True,  False, False),
    ("f03_matsubi_tab.txt",  b"a\t\nb\n",        "行末に TAB(陽性対照)",              True,  False, False),
    ("f04_crlf_space.txt",   b"a \r\nb\r\n",     "CRLF かつ行末に空白 ―― 止血後は鳴るべし", True,  True,  False),
    ("f05_crlf_kirei.txt",   b"a\r\nb\r\n",      "CRLF だが空白無し ―― ②は黙るべし",   False, True,  False),
    ("f06_nurekinu.bin",     b"x \x00y\n",       "空白が NUL の直前(真の行末には空白無し)", False, False, False),
    ("f07_nul_dake.bin",     b"a\x00b\n",        "NUL 有り・空白無し",                False, False, False),
    ("f08_zenkaku.txt",      "a　\nb\n".encode("utf-8"), "行末が全角空白(見えぬ字)", False, False, False),
    ("f09_cr_nomi.bin",      b"a\rb\n",          "CR が行中(行末ではない)",            False, True,  False),
    ("f10_nul_to_space.bin", b"p \x00q \nr\n",   "NUL 直前にも真の行末にも空白",        True,  False, False),
]


def main():
    os.makedirs("_tane", exist_ok=True)
    rows = []
    for name, b, toi, j2, j3, j4 in TANE:
        p = os.path.join("_tane", name)
        with open(p, "wb") as fh:
            fh.write(b)
        rows.append([name, len(b), hashlib.sha256(b).hexdigest(), b.hex(),
                     b.count(b"\n"), b.count(b"\r"), b.count(b"\x00"), toi,
                     "鳴る" if j2 else "黙る", "鳴る" if j3 else "黙る", "鳴る" if j4 else "黙る"])
    sys.path.insert(0, "driver")
    import importlib.util
    spec = importlib.util.spec_from_file_location("K", "driver/00_kaki.py")
    K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
    K.kaku_tsv("raw/10_tane.tsv", rows,
               header=["名", "bytes", "sha256", "hex", "LF", "CR", "NUL", "問ひ",
                       "法_條②", "法_條③", "法_條④"])
    print("種=%d 本" % len(rows))


main()

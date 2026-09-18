# -*- coding: utf-8 -*-
"""km-103 着手便を組み、★字数を器で測つてから★書く(條 300 字・python3 len)。

★宣した事★:
 ・胴は本器が組む。手で写さぬ。字数も本器が `len()` で測る。
 ・★300 字を超えたら一字も本便を書かず rc=7 で止まる(fail-closed)★。下書のみ raw に残す。
 ・着手刻は `date` の出目(raw/00_chaku_toki.txt)を kaki で正して読む ―― 送つた後に付けぬ。
 ・★此の字数が意味せぬ事★: 便が★届いた★事ではない。届いたか否かは家老mac の箱の尾で別に測る。
負の対照: JOU を 10 に落とせば同じ胴が rc=7 で撥ねられ、raw に下書だけが残る事を確かめる。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_s = importlib.util.spec_from_file_location("K", os.path.join(os.path.dirname(os.path.abspath(__file__)), "00_kaki.py"))
K = importlib.util.module_from_spec(_s); _s.loader.exec_module(K)

JOU = int(os.environ.get("KM103_JOU", "300"))

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: 05_chakushu.py <束の根>\n"); return 2
    base = sys.argv[1]; raw = os.path.join(base, "raw")
    toki = open(os.path.join(raw, "00_chaku_toki.txt"), encoding="utf-8").read().strip()
    K.kaku(os.path.join(raw, "00_chaku_toki.txt"), toki)   # ★`>` の生捕りを kaki で正す★

    hon = (
        "[專任3 km-103 着手] 札 受。的=三紙(a1/a2/當方)を一表にし"
        "★甲乙丙の二義を解く★事。先に測れた事: ★三紙は器の形から揃はぬ★"
        "(a2 のみ ki/・report.md・_manifest.txt／他二席は driver/・README.md・MANIFEST.txt)"
        "∴ 讀器は三形を受ける。軸は二欄に分け欄名に焼く(甲乙丙=捨證軸／家老甲乙=器軸)。"
        "㋒は三器(NUL/grep -c/splitlines)を三紙に当て U+2028 疵を測る。"
        "讀取のみ・枝0削除・checkout 禁。★宣ETA 90〜210分(幅)★・起点=着手刻 " + toki[11:16] + "。"
    )
    ji = len(hon)
    if ji > JOU:
        sys.stderr.write("★條を超えた ∴ 一字も本便を書かず止まる(超過 %d 字)★\n" % (ji - JOU))
        K.kaku(os.path.join(raw, "05_chakushu_shitagaki.txt"), hon)
        return 7
    K.kaku(os.path.join(raw, "05_chakushu.txt"), hon)
    K.kaku(os.path.join(raw, "05_chakushu_ji.txt"),
           "字数(python3 len)=%d\n條=%d\n残り=%d\n着手刻=%s\n測つた胴=raw/05_chakushu.txt" % (ji, JOU, JOU - ji, toki))
    sys.stderr.write("字数=%d(條 %d) 着手刻=%s\n" % (ji, JOU, toki))
    return 0

sys.exit(main())

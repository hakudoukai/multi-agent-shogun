# -*- coding: utf-8 -*-
"""㋓の材料 ―― 四版が ★どの治めを載せて居るか★ を字で数へる(★字が在る事は働く事ではない★ゆゑ
㋒ の出目と併せて初めて意味を持つ。本表は單獨では根拠に成らぬ)。

usage: python3 driver/55_kinou.py <bundle_root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
K = import_module("00_kaki")

ORDER = ["9cd550fc2cf963ca0475b3448bb33483b9aede6b",
         "54e133c85832d48aa731d0ab0d105d399b9b8fbd",
         "b0bf5b05ededce4b06286dbab05cf0b616414ef2",
         "054c442eaee3886b2283f98f7c3a1ab8cb813b68"]
SHIRUSHI = [
    ("條①〜條⑤ の字", ["條①", "條②", "條③", "條④", "條⑤"]),
    ("基点の口(裁322949)", ["KM_GATE_MANIFEST_BASE"]),
    ("閾を同じ演算子で(裁322952甲)", ["num_same_op"]),
    ("未設定/空/空白を分つ(裁322952乙)", ["env_state"]),
    ("行注入の封じ(裁323980⑵)", ["␊"]),
    ("開かぬ寸法取り(裁320321⑴)", ["TIMEOUT_BIN"]),
    ("fail-open 止血(裁307881)", ["is_num"]),
    ("自己検め(--selftest)", ["--selftest"]),
]


def main(argv):
    bundle = argv[1]
    raw = os.path.join(bundle, "raw")
    txt = {}
    for b in ORDER:
        txt[b] = open(os.path.join(raw, "31_han_%s.sh" % b[:16]), encoding="utf-8", errors="surrogateescape").read()

    rows = []
    for na, keys in SHIRUSHI:
        r = [na]
        for b in ORDER:
            n = sum(txt[b].count(k) for k in keys)
            r.append("%d" % n)
        rows.append(r)
    K.kaku_tsv(os.path.join(raw, "56_kinou_hyou.tsv"), rows,
               header=["治め(字での數)"] + ["版%s" % b[:16] for b in ORDER])
    out = ["★四版が載せる治め(字の數 ―― ★働く事の證ではない★)★", ""]
    out.append("治め\t" + "\t".join("版%s" % b[:16] for b in ORDER))
    for r in rows:
        out.append("\t".join(r))
    out.append("")
    out.append("★此の表が意味せぬ事★: 字が在る事は其の治めが ★働く★ 事ではない。")
    out.append("  實測: 版54e133c は KM_GATE_MANIFEST_BASE の字を一つも持たぬが、")
    out.append("  束の中から走らせれば條①は通る(基点に ★明示の \"\"★ を渡す=cwd 相対ゆゑ)。")
    out.append("  逆に版b0bf5b0 は治めを多く載せるが、束の中でも外でも條①は落ちる。")
    K.kaku(os.path.join(raw, "57_kinou_matome.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

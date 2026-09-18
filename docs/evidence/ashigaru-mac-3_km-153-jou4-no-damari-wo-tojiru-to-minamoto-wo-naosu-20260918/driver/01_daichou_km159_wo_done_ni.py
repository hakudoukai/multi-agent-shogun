# -*- coding: utf-8 -*-
"""臺帳(queue/tasks/ashigaru-mac-3.yaml)の km-159 を assigned → done へ己の手で改める。
家老令 msg_20260918_130747_07f94db1「★臺帳の km-159 を貴殿の手で done へ改め★」に依る。
★行番号を打たず、逐語で場所を引く★(過去の疵: 行番号固定は版が動くと別の行を斬る)。
完了刻の根 = 束内 最新 mtime(己の断ではなく disk の値)。"""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module

K = import_module("00_kaki")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
DAICHOU = os.path.join(ROOT, "queue/tasks/ashigaru-mac-3.yaml")
TABA159 = os.path.join(ROOT, "docs/evidence/ashigaru-mac-3_km-159-jou5-no-na-to-jitsu-no-kuichigai-20260918")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_letters")

ANCHOR = "  task_id: km-159-jou5-no-na-to-jitsu-no-kuichigai-20260918\n  status: assigned\n"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def saishin_mtime(d):
    saki = None
    for base, _dirs, files in os.walk(d):
        for f in files:
            p = os.path.join(base, f)
            st = os.lstat(p)
            if not os.path.isfile(p):
                continue
            if saki is None or st.st_mtime > saki[0]:
                saki = (st.st_mtime, os.path.relpath(p, d))
    return saki


def main():
    sha_mae = sha(DAICHOU)
    with open(DAICHOU, encoding="utf-8") as fh:
        moto = fh.read()
    kazu = moto.count(ANCHOR)
    rows = [("欄", "値")]
    rows.append(("臺帳", os.path.relpath(DAICHOU, ROOT)))
    rows.append(("錨の逐語", ANCHOR.replace("\n", "\\n")))
    rows.append(("錨の当り数", str(kazu)))
    if kazu != 1:
        rows.append(("断", "★錨が一件でない ∴ 一字も書かぬ(fail-closed)★"))
        K.kaku_tsv(os.path.join(OUT, "00_daichou_km159_done.tsv"), rows[1:], header=rows[0])
        print("錨の当り数=%d ∴ 書かぬ" % kazu)
        return 2

    st = saishin_mtime(TABA159)
    import time
    koku = time.strftime("%Y-%m-%dT%H:%M:%S+0900", time.localtime(st[0]))
    ima = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%z"], stdout=subprocess.PIPE).stdout.decode().strip()

    atarashii = (
        "  task_id: km-159-jou5-no-na-to-jitsu-no-kuichigai-20260918\n"
        "  status: done\n"
        "  completed_at: %s\n"
        "  completed_at_no_ne: 束内 最新 mtime(%s)\n"
        "  done_ni_aratameta_kiroku: 家老令 msg_20260918_130747_07f94db1(2026-09-18T13:07:47)に依り專任3 自らが改めた(改めた刻=%s)。監査提出は先に直送済 seq=332005。\n"
        % (koku, st[1], ima)
    )
    nochi = moto.replace(ANCHOR, atarashii)
    if nochi == moto:
        print("置換が効かぬ")
        return 2
    with open(DAICHOU, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(nochi)
    sha_go = sha(DAICHOU)

    rows.append(("改めた刻", ima))
    rows.append(("completed_at", koku))
    rows.append(("completed_at の根", "束内 最新 mtime = " + st[1]))
    rows.append(("臺帳 sha256 前", sha_mae))
    rows.append(("臺帳 sha256 後", sha_go))
    rows.append(("臺帳 行数 前", str(moto.count("\n"))))
    rows.append(("臺帳 行数 後", str(nochi.count("\n"))))
    rows.append(("増えた行", str(nochi.count("\n") - moto.count("\n"))))
    rows.append(("此の數が意味せぬ事", "臺帳の札が done に成つた事は「軍師の検分が済んだ」の意ではない ―― 検分は seq=332005 で仰いだのみ"))
    K.kaku_tsv(os.path.join(OUT, "00_daichou_km159_done.tsv"), rows[1:], header=rows[0])
    print("done へ改めた: %s → %s" % (sha_mae[:16], sha_go[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

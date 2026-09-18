# -*- coding: utf-8 -*-
"""便の器 ―― ★送る前に己で測る★(胴300字が條)。
用法: python3 driver/90_fumi.py <便名> <宛> <parent_seq> <胴file>
  ・胴は argv から取らぬ(全角の shell 事故を避ける為・file 渡し)。
  ・字数は ★len(unicode)★ で測る(byte でも 行でもない ―― 単位を名に焼く)。
  ・300字超なら ★送る前に rc=1 で止まる★(分けよ・略すな)。
  ・送つた後は ★sb read seq で胴を読み返し★、一致を刷る(第八の守り)。
"""
import io, os, subprocess, sys

JOU = 300
KI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KI, "driver"))
import kaki as K

SB = os.path.expanduser("~/bin/sb-ashigaru-mac-2")
SB_READ = os.path.expanduser("~/bin/sb")


def main():
    bin_, ate, oya, dou_file = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    dou = io.open(dou_file, encoding="utf-8").read().strip()
    ji = len(dou)
    K.kaku(os.path.join(KI, "raw", "90_dou_%s.txt" % bin_), dou)
    print(u"便=%s 宛=%s parent_seq=%s ★字(unicode文字)=%d／條=%d★" % (bin_, ate, oya, ji, JOU))
    assert ji <= JOU, u"★%d字 ―― 條%d を超えた。送る前に分けよ(略すな)。★" % (ji, JOU)
    p = subprocess.run([SB, "write", "letter", dou, "--to", ate, "--parent-seq", oya],
                       capture_output=True)
    rc, out, err = p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    print(u"★rc=%d★(returncode 素・管を通さぬ)" % rc)
    print(out.strip())
    if err.strip():
        print(u"err= " + err.strip())
    with io.open(os.path.join(KI, "raw", "90_okuri.txt"), "a", encoding="utf-8", newline="\n") as fh:
        fh.write(u"%s\t%s\tparent_seq=%s\t字=%d\trc=%d\t%s\n" % (bin_, ate, oya, ji, rc, out.strip().replace("\n", " ")))
    assert rc == 0, u"★送りが rc=%d ―― 届いて居らぬ★" % rc


main()

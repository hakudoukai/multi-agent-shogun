# -*- coding: utf-8 -*-
"""90 ―― 出す前に門(karo_mac_manifest_verify.py)を再走させる(裁 seq339623 家老mac 指示逐語
「出す前 門を再走させれば條①が鳴る」への応)。

★予め判つて居る事★: raw/80_daichou_shime.txt は 80_daichou.py が manifest.txt を
建てた★後★に上書きされる自己言及の紙(己の最終sha256を manifest には載せられぬ)ゆゑ、
門を何度再走しても此の一件だけは★相違★に数へられる(器の順序上の構造であり、
90_monbikae の旧疵=実体無 とは別種)。∴ 相違=1(此の一件のみ)は★期待される出目★であり、
實體無 0・読めぬ行 0 である事が本弾の眼目(旧疵=改名前の臺帳が実体無を刷つた事)。
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

TOOL = os.path.join(ROOT, "scripts", "checks", "karo_mac_manifest_verify.py")
p = subprocess.run([sys.executable, "-B", TOOL, "manifest.txt", "."], cwd=BUNDLE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
rc = p.returncode
out = p.stdout.decode("utf-8", "replace")
err = p.stderr.decode("utf-8", "replace")

K.kaku(os.path.join(BUNDLE, "raw", "90_saido_kensho.out"), out)
K.kaku(os.path.join(BUNDLE, "raw", "90_saido_kensho.err"), err)
K.kaku(os.path.join(BUNDLE, "raw", "90_saido_kensho.rc"), u"%d\n" % rc)

print(u"rc=%d" % rc)
print(out)
if err.strip():
    print(u"[stderr] " + err)

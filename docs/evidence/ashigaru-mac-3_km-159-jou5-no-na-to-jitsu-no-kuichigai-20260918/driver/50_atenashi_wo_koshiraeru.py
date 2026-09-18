# -*- coding: utf-8 -*-
"""㋕ 当て紙を拵へる ―― ★門は直さぬ。據ゑぬ。★ git apply --check の rc までで止める。
甲(語): L255 の「超」を「以上」へ。比較器 -ge に語を合はせる ―― 挙動は ★一切変へぬ★。
乙(名実): 閾が倒れた事を印に残し、其の儘 條⑤ を通す時は ★止める★。
        即ち「既定へ倒す」を fail-closed の名に値させる為には、rc を 0 にせぬ事が要る。
四札: 刻=冠 / 根=cwd / rc=git apply --check の returncode(管を通さず) / 陽性対照=わざと壊した当て紙。"""
import os
import sys
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

GATE = "scripts/checks/karo_mac_dasumae_gate.sh"
SRC = open(GATE, encoding="utf-8").read()
WK = os.path.join(BUNDLE, "_fx", "atenashi")
os.makedirs(os.path.join(WK, "a", "scripts", "checks"), exist_ok=True)
os.makedirs(os.path.join(WK, "b", "scripts", "checks"), exist_ok=True)
AP = os.path.join(WK, "a", GATE)
BP = os.path.join(WK, "b", GATE)
open(AP, "w", encoding="utf-8", newline="\n").write(SRC)

KOU_OLD = 'say "★條⑤ 寸法 ―― byte和 ${total}(閾 ${MAXB}・裁294493)超★"'
KOU_NEW = 'say "★條⑤ 寸法 ―― byte和 ${total}(閾 ${MAXB}・裁294493)以上★"'

OTSU_OLD = '''  else
    say "條⑤ 寸法 = byte和 ${total}(閾 ${MAXB}未満)"
  fi'''
OTSU_NEW = '''  elif [ "${MAXB_TAORETA:-0}" -ne 0 ]; then
    say "條⑤ 寸法 = byte和 ${total}(倒した閾 ${MAXB}未満)"
    say "★條⑤ 閾が定まらなんだ儘 通すは fail-closed に非ず ―― 既定へ倒れるは★緩い側★である★"
    fail=1
  else
    say "條⑤ 寸法 = byte和 ${total}(閾 ${MAXB}未満)"
  fi'''

INI_OLD = 'say(){ printf \'%s\\n\' "$*" >&2; }'
INI_NEW = 'say(){ printf \'%s\\n\' "$*" >&2; }\nMAXB_TAORETA=0  # ★閾が既定へ倒れた印(裁 km-159 乙案)★'

def atenashi(name, subs, kanmuri):
    s = SRC
    for old, new in subs:
        assert s.count(old) == 1, "%s: 当たらぬ(%d件) ―― %r" % (name, s.count(old), old[:40])
        s = s.replace(old, new)
    open(BP, "w", encoding="utf-8", newline="\n").write(s)
    p = subprocess.run(["git", "diff", "--no-index", "--src-prefix=a/", "--dst-prefix=b/",
                        os.path.relpath(AP, ROOT), os.path.relpath(BP, ROOT)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    d = p.stdout.decode("utf-8")
    d = d.replace(os.path.relpath(AP, ROOT), GATE).replace(os.path.relpath(BP, ROOT), GATE)
    out = os.path.join(BUNDLE, "raw", name)
    open(out, "w", encoding="utf-8", newline="\n").write(kanmuri + d)
    q = subprocess.run(["git", "apply", "--check", out], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out, q.returncode, (q.stderr.decode("utf-8").strip() or "(何も言はず)"), d.count("\n@@") + (1 if d.startswith("@@") else 0)

rows = []
for name, subs, ki in [
    ("60_atenashi_kou_kotoba.patch", [(KOU_OLD, KOU_NEW)],
     "# 甲 ―― 語のみ。比較器(-ge)に語を合はせる。★挙動は変へぬ★。\n"),
    ("61_atenashi_otsu_meijitsu.patch", [(INI_OLD, INI_NEW), (OTSU_OLD, OTSU_NEW)],
     "# 乙 ―― 名実。倒した閾で通す時は止める。★挙動を変へる ∴ 委員長の許可無くば據ゑぬ★。\n"),
]:
    p, rc, msg, hunk = atenashi(name, subs, ki)
    rows.append([name, hunk, rc, ("当たる" if rc == 0 else "★当たらぬ★"), msg[:70]])

# ★陽性対照★ わざと外れる当て紙 ―― --check が現に rc!=0 を返す事を先に見せる
bad = os.path.join(BUNDLE, "raw", "62_atenashi_hazure_seitaishou.patch")
kaku(bad, open(os.path.join(BUNDLE, "raw", "60_atenashi_kou_kotoba.patch"),
               encoding="utf-8").read().replace("byte和 ${total}(閾 ${MAXB}・裁294493)超",
                                                "此の行は器の何處にも無い★陽性対照★"))
q = subprocess.run(["git", "apply", "--check", bad], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
rows.append(["62_atenashi_hazure_seitaishou.patch(★陽性対照★)", "-", q.returncode,
             ("当たる" if q.returncode == 0 else "★当たらぬ(=正)★"),
             (q.stderr.decode("utf-8").strip() or "(何も言はず)")[:70]])

kaku_tsv(os.path.join(BUNDLE, "raw", "50_atenashi.tsv"), rows,
         header=["当て紙", "hunk数", "git apply --check の rc", "判", "器の言"])
kaku(os.path.join(BUNDLE, "raw", "51_atenashi_kotoba_to_kikime.txt"),
     "as-of %s(UTC)\n根=%s\n★據ゑて居らぬ★ ―― git apply --check の rc までで止めた(変更統制)。\n"
     "門の現物 sha256 は臺帳に在り。当て紙は raw/60・raw/61。\n\n"
     "【刷る語 と 効き目 ―― 一行づつ対に】\n"
     "甲 刷る語: 「byte和 N(閾 M・裁294493)★超★」→「…★以上★」\n"
     "甲 効き目: 和=閾 の一点で語が真と成る。rc は一切動かぬ(三点とも今の儘)。\n"
     "乙 刷る語: 「條⑤ 寸法 = byte和 N(★倒した閾★ M未満)」+「閾が定まらなんだ儘 通すは fail-closed に非ず」\n"
     "乙 効き目: 閾が①非数②空③空白のみ④2^63以上 の時 rc 0→1 ―― 名(fail-closed)に實が追ひ付く。\n"
     "乙 の代償: 打ち間違ひ一つで門が止まる ∴ 打つ者は必ず閾を正しく綴る事に成る(之が狙ひ)。\n"
     "乙 の可逆: 当て紙を逆に当てれば旧挙動。印 MAXB_TAORETA は既定 0 ゆゑ set -u を破らぬ。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT))
print("当て紙 %d 枚(陽性対照込)" % len(rows))

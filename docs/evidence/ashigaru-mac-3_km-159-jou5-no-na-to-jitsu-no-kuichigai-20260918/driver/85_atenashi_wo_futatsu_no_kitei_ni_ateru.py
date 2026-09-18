# -*- coding: utf-8 -*-
"""★旧基底で書いた当て紙を、新基底へ当てて見せる★(家老mac 09:00:05 の命)
旧基底(共用樹 disk)で書いた raw/60(甲・語)・raw/61(乙・名実)を ★捨てず★、二つの基底へそれぞれ当て、
`git apply --check` の rc を四つ並べる。★当たらぬ★ 事は失敗ではない ―― 新基底では ★疵が既に閉ぢて居る★ 故である。
陽性対照(器が働く事の證)= 新基底から拵へた当て紙 丙 は同じ手順で rc=0 に成る。
陰性対照 = 器の何處にも無い行を消す当て紙は両基底で rc≠0。
四札: 刻=冠 / 根=cwd / rc=git apply --check の returncode(★管を通さず★) / 対照=上記二つ。"""
import os
import sys
import shutil
import hashlib
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
KYUU_SRC = open(GATE, "rb").read()
SHIN_SRC = open(os.path.join(BUNDLE, "base_gate.sh"), "rb").read()
KEN = os.path.join(BUNDLE, "_fx", "kentei")
if os.path.isdir(KEN):
    shutil.rmtree(KEN)

def sueru(na, body):
    d = os.path.join(KEN, na)
    os.makedirs(os.path.join(d, "scripts", "checks"))
    with open(os.path.join(d, GATE), "wb") as fh:
        fh.write(body)
    return d

D_KYUU = sueru("kyuu", KYUU_SRC)
D_SHIN = sueru("shin", SHIN_SRC)

def ateru(patch, d, sunao=False):
    """★git apply --check は repo の中の子dir から走らせると、其のdir の外を指す path を
    ★黙つて跳ばし rc=0 を返す★(-v で「Skipped patch」と出る) ―― 之は偽の通である。
    ∴ GIT_DIR を在らぬ路へ向け、cwd を根と看做させて当てる。sunao=True は其の疵を見せる為の素の走り。"""
    e = dict(os.environ)
    if not sunao:
        e["GIT_DIR"] = os.path.join(KEN, "arienu.git")   # ★在らぬ ―― repo 探しを断つ★
    p = subprocess.run(["git", "apply", "--check", "-v", os.path.abspath(patch)], cwd=d, env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    msg = p.stderr.decode("utf-8", "replace").strip()
    line = [l for l in msg.split("\n") if l.strip() and not l.startswith("warning:")]
    return p.returncode, (line[0] if line else "(何も言はず)")

# ―― 陽性対照: 新基底から拵へた当て紙 丙(冠に一行足すのみ・挙動を変へず) ――
hei_a = os.path.join(KEN, "hei_a", GATE)
hei_b = os.path.join(KEN, "hei_b", GATE)
for p in (hei_a, hei_b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
open(hei_a, "wb").write(SHIN_SRC)
s = SHIN_SRC.decode("utf-8")
ANCHOR = "MAXB=\"${DASUMAE_MAX_BYTES:-10485760}\""
assert s.count(ANCHOR) == 1, "丙の錨が %d 件 ―― 焼き込みを止め逐語で当て直せ" % s.count(ANCHOR)
open(hei_b, "wb").write(s.replace(ANCHOR, "# ★陽性対照(丙) ―― 器が働く事を示す為だけの一行。挙動を変へぬ。★\n" + ANCHOR).encode("utf-8"))
q = subprocess.run(["git", "diff", "--no-index", "--src-prefix=a/", "--dst-prefix=b/",
                    os.path.relpath(hei_a, ROOT), os.path.relpath(hei_b, ROOT)],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
hei_patch = os.path.join(BUNDLE, "raw", "86_atenashi_hei_shin_kitei_seitaishou.patch")
kaku(hei_patch, "# 丙 ―― ★陽性対照★ 新基底から拵へた当て紙(冠に一行)。器が働く事の證。\n"
     + q.stdout.decode("utf-8").replace(os.path.relpath(hei_a, ROOT), GATE).replace(os.path.relpath(hei_b, ROOT), GATE))

TEGAMI = [
    ("甲(語・★旧基底で書いた物★)", "raw/60_atenashi_kou_kotoba.patch"),
    ("乙(名実・★旧基底で書いた物★)", "raw/61_atenashi_otsu_meijitsu.patch"),
    ("丙(★陽性対照★・新基底で書いた物)", os.path.relpath(hei_patch, BUNDLE)),
    ("外れ(★陰性対照★・器に無い行)", "raw/62_atenashi_hazure_seitaishou.patch"),
]
rows = []
for na, rel in TEGAMI:
    p = os.path.join(BUNDLE, rel)
    rc_k, msg_k = ateru(p, D_KYUU)
    rc_s, msg_s = ateru(p, D_SHIN)
    imi = {
        ("甲", 0, 1): "旧基底には当たる / ★新基底には当たらぬ = 疵が既に閉ぢて居る★",
    }.get(("甲", rc_k, rc_s))
    if na.startswith("甲") or na.startswith("乙"):
        imi = ("★旧に当たり新に当たらぬ ―― 新基底では疵が既に無い★" if (rc_k == 0 and rc_s != 0)
               else ("両基底に当たる ―― ★疵は新基底にも残る★" if (rc_k == 0 and rc_s == 0)
                     else "★旧にすら当たらぬ ―― 当て紙か基底を疑へ★"))
    elif na.startswith("丙"):
        imi = ("★新基底に当たる(=器は働く)★" if rc_s == 0 else "★新基底にすら当たらぬ = 器を疑へ★")
    else:
        imi = ("★両基底とも当たらぬ(=正)★" if (rc_k != 0 and rc_s != 0) else "★当たつた = 陰性対照が効いて居らぬ★")
    rows.append([na, os.path.basename(rel), rc_k, ("当たる" if rc_k == 0 else "当たらぬ"),
                 rc_s, ("当たる" if rc_s == 0 else "当たらぬ"), imi, (msg_s if rc_s else msg_k)[:56]])
kaku_tsv(os.path.join(BUNDLE, "raw", "85_atenashi_futatsu_no_kitei.tsv"), rows,
         header=["当て紙", "file", "旧基底 rc", "旧基底", "新基底 rc", "新基底", "意", "器の言(56字で截つ)"])

# ―― ★器そのものの疵を見せる★ 子dir から素に走らせると陰性対照まで rc=0(偽の通)に成る ――
sunao = []
for na, rel in TEGAMI:
    p = os.path.join(BUNDLE, rel)
    rc_n, msg_n = ateru(p, D_SHIN, sunao=True)
    rc_y, msg_y = ateru(p, D_SHIN, sunao=False)
    sunao.append([na, rc_n, ("通(★偽★)" if rc_n == 0 else "落ち"), (msg_n or "-")[:46],
                  rc_y, ("通" if rc_y == 0 else "落ち"),
                  ("★素の走りは判ぜぬ★" if rc_n != rc_y else "同じ")])
kaku_tsv(os.path.join(BUNDLE, "raw", "88_apply_check_no_kizu.tsv"), sunao,
         header=["当て紙", "素の rc", "素の判", "素の言(46字で截つ)", "GIT_DIR を断つた rc", "其の判", "食ひ違ひ"])

def sha(b):
    return hashlib.sha256(b).hexdigest()

kaku(os.path.join(BUNDLE, "raw", "87_atenashi_dan.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "旧基底 sha256 %s(共用樹 disk・★未commit の三つ目の版★)\n"
     "新基底 sha256 %s(origin/main 04672e15b1edf4a02b7cea1f4f32cfb9a64e34d5)\n\n"
     "【断】\n"
     "㋐ 甲(語「超」→「以上」)は ★新基底に当たらぬ★ ―― 錨の行が新基底に 0 件。\n"
     "   新基底の逐語 = 「★條⑤ 寸法 ―― byte和 ${total}(閾 ${MAXB}・裁294493)★以上★(比べは -ge ゆゑ「超」に非ず・裁 seq330497)」\n"
     "   ∴ 當席が km-159 ㋑ で示した『和=閾 の一点で語が一つ厳しい側へずれる』は ★新基底では既に直つて居る★。\n"
     "㋑ 乙(閾が倒れた儘 通すな)も ★新基底に当たらぬ★ ―― 新基底の fix_threshold は\n"
     "   空文字・空白のみ・比較器が扱へぬ値を ★既定へ倒さず return 1 → 門は exit 2★ で止める(裁 seq330497)。\n"
     "   實測(raw/76): 形1 非数・形2 空文字・形3/3' 空白のみ・形4' 2^63・形4'' 2^64以上 の ★6形が rc 0→2★。\n"
     "㋒ ∴ ★新基底に対して當席が出すべき当て紙は無い★。疵は上流で閉ぢた ―― 之を『当て紙が失敗した』と書かぬ。\n"
     "㋓ 未設定(形0)は新基底でも既定へ倒れ rc=0 で通る。★之は穴ではないと断ずる★ ―― \n"
     "   「未設定」は値を与へて居らぬ事、「空文字」は値を与へ損ねた事であり、★別物★ である(第40弾以来の分け方)。\n"
     "   未設定まで止めれば閾を設けぬ全ての呼び手で門が死ぬ ∴ main の分け方を是とする。\n"
     "㋔ ★新基底は此の樹では其の儘走らぬ★ ―― 門が名指す karo_mac_fukashiji.py が共用樹 disk にも HEAD にも無い(raw/75)。\n"
     "   兄弟器を隣に置かねば條②④が「測れぬ」で rc=1(raw/78 陽性対照)。merge 前に門だけ差し替へると ★濡れ衣で落ちる★。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        sha(KYUU_SRC), sha(SHIN_SRC)))
print("当て紙 %d 枚を二基底へ当てた" % len(rows))
for r in rows:
    print("  %s 旧rc=%s 新rc=%s" % (r[0], r[2], r[4]))

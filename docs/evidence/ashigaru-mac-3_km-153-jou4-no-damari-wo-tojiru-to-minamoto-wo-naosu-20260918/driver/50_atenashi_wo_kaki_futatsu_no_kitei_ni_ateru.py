# -*- coding: utf-8 -*-
"""★條④の黙りを閉ぢる當て紙を書き、二つの基底へ當てて rc を示す★(家老令 km-153 ㋐ 後段)
門は変更統制 ∴ ★據ゑず材のみ★。當て紙は _fx/kentei/ の複製へのみ當て、共用樹の門には指一本触れぬ。
apply --check は ★GIT_DIR を在らぬ路へ向けて★ 走らせる(子dir から素に走らせると repo 外の path を黙つて跳ばし
偽の通 rc=0 を返す ―― km-159 raw/88 で實測した器の疵)。
四札: 刻=冠 / 根=cwd と二基底 sha256 / rc=git apply --check の returncode(★管を通さず★) / 対照=丙(陽性)と外れ(陰性)。"""
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
KYUU_SRC = open(os.path.join(BUNDLE, "_fx", "base_kyuu_disk.sh"), "rb").read()
SHIN_SRC = open(os.path.join(BUNDLE, "_fx", "base_shin_origin_main.sh"), "rb").read()
KEN = os.path.join(BUNDLE, "_fx", "kentei")
if os.path.isdir(KEN):
    shutil.rmtree(KEN)

def sueru(na, body):
    d = os.path.join(KEN, na)
    os.makedirs(os.path.join(d, "scripts", "checks"))
    open(os.path.join(d, GATE), "wb").write(body)
    return d

D_KYUU, D_SHIN = sueru("kyuu", KYUU_SRC), sueru("shin", SHIN_SRC)

# ―― 甲 ―― 旧基底の「末尾2byte 比べ」を「末尾一行」比べへ改める當て紙 ――
ks = KYUU_SRC.decode("utf-8")
KL = ks.split("\n")
WAKU = 'elif [ "$sz" -ge 2 ]; then'
hit = [i for i, l in enumerate(KL) if WAKU in l]
assert len(hit) == 1, "外枠の錨が %d 件 ―― 行番を焼き込まず錨を直せ" % len(hit)
i0 = hit[0]
indent = KL[i0][: len(KL[i0]) - len(KL[i0].lstrip())]
# 錨の行から、内側の if を閉ぢる `fi`(外枠と同じ深さ)までを一塊として引く
i1 = None
for j in range(i0 + 1, min(i0 + 20, len(KL))):
    if KL[j].strip() == "fi" and KL[j][: len(KL[j]) - len(KL[j].lstrip())] == indent:
        i1 = j
        break
assert i1 is not None, "内側の fi が引けぬ ―― 塊を取り違へて居る"
FURUI = "\n".join(KL[i0:i1 + 1]) + "\n"
assert 'last2=$(tail -c2' in FURUI and '"0a0a"' in FURUI, "塊に黙りの二行が居らぬ ―― 錨を疑へ"
assert ks.count(FURUI) == 1, "塊が %d 件 ―― 一意でなければ當てぬ" % ks.count(FURUI)

ATARASHI = "".join(indent + l + "\n" for l in [
    'elif [ "$sz" -ge 2 ]; then',
    '  # ★2026-09-18 專任3 km-153 ㋐ ―― 末尾「2 byte」ではなく末尾「一行」を見る★',
    '  #   旧: last2 が丁度 `0a0a` の時だけ鳴つた ∴ CRLF 空行(末尾二字 `0d0a`)に ★黙つた★(fx05 實測)。',
    '  #   改: 末尾行から CR を落して空なら鳴らす ∴ `0a0a` も `0d0a` も同じ口へ入る。',
    '  #   ★限界(此の當て紙が閉ぢぬ物)★: 不可視字一字だけの行(U+3000 等・末尾二字 `800a`)は閉ぢぬ。',
    '  #   之は codepoint の類を見る器が要る ―― 上流(裁 seq330497)は兄弟器 karo_mac_fukashiji.py で閉ぢた。',
    '  #   ★形を数へ上げる仕方では永久に閉ぢぬ(U+2003 等が幾らでも在る)★ ∴ 本紙は一面のみを閉ぢる材である。',
    '  local saigo saigo_rc',
    '  saigo=$(tail -n1 "$f" 2>/dev/null); saigo_rc=$?   # ★管を通さず rc を取る★',
    "  saigo=\"${saigo%$'\\r'}\"",
    '  if [ "$saigo_rc" -ne 0 ]; then',
    '    say "★條④ 測れぬ(末尾行が取れぬ・tail rc=${saigo_rc}) ―― ${f}★ ★測れぬは通さぬ(default-deny)★"',
    '    fail=1',
    '  elif [ -z "$saigo" ]; then',
    '    say "★EOF改行が複数(末尾に空行) ―― ${f}★"',
    '    fail=1',
    '  fi',
    'fi',
])

def tsukuru(na, moto_src, nochi_src, kanmuri):
    a = os.path.join(KEN, na + "_a", GATE)
    b = os.path.join(KEN, na + "_b", GATE)
    for p in (a, b):
        os.makedirs(os.path.dirname(p), exist_ok=True)
    open(a, "wb").write(moto_src)
    open(b, "wb").write(nochi_src)
    q = subprocess.run(["git", "diff", "--no-index", "--src-prefix=a/", "--dst-prefix=b/",
                        os.path.relpath(a, ROOT), os.path.relpath(b, ROOT)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = q.stdout.decode("utf-8").replace(os.path.relpath(a, ROOT), GATE).replace(os.path.relpath(b, ROOT), GATE)
    p = os.path.join(BUNDLE, "raw", "50_atenashi_" + na + ".patch")
    kaku(p, kanmuri + out)
    return p

P_KOU = tsukuru("kou_jou4", KYUU_SRC, ks.replace(FURUI, ATARASHI).encode("utf-8"),
                "# 甲 ―― ★旧基底(共用樹 disk)の條④ の黙りを閉ぢる當て紙★。據ゑるな(変更統制) ―― 材のみ。\n")
# ―― 丙 ―― 陽性対照(新基底の冠へ一行・挙動を変へぬ。器が働く事の證) ――
ss = SHIN_SRC.decode("utf-8")
AN_HEI = 'MAXB="${DASUMAE_MAX_BYTES:-10485760}"'
assert ss.count(AN_HEI) == 1, "丙の錨が %d 件" % ss.count(AN_HEI)
P_HEI = tsukuru("hei_seitaishou", SHIN_SRC,
                ss.replace(AN_HEI, "# ★陽性対照(丙) ―― 器が働く事を示す為だけの一行。挙動を変へぬ。★\n" + AN_HEI).encode("utf-8"),
                "# 丙 ―― ★陽性対照★ 新基底から拵へた當て紙(冠に一行)。當て器が働く事の證。\n")
# ―― 外れ ―― 陰性対照(何方の基底にも無い行を消す) ――
NAI = "# ★陰性対照 ―― 何方の基底にも存在せぬ此の一行(km-153)★"
assert NAI not in ks and NAI not in ss, "陰性対照の行が基底に在る ―― 対照に成らぬ"
P_HAZ = tsukuru("hazure_inseitaishou", (ss + NAI + "\n").encode("utf-8"), SHIN_SRC.decode("utf-8").encode("utf-8"),
                "# 外れ ―― ★陰性対照★ 何方の基底にも無い行を消す當て紙。両基底で當たらぬのが正。\n")

def ateru(patch, d, sunao=False):
    e = dict(os.environ)
    if not sunao:
        e["GIT_DIR"] = os.path.join(KEN, "arienu.git")   # ★在らぬ ―― repo 探しを断つ★
    p = subprocess.run(["git", "apply", "--check", "-v", os.path.abspath(patch)], cwd=d, env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    li = [l for l in p.stderr.decode("utf-8", "replace").split("\n") if l.strip() and not l.startswith("warning:")]
    return p.returncode, (li[0].strip() if li else "(何も言はず)")

def gyou(p):
    b = open(p, "rb").read().decode("utf-8")
    n = b.split("\n")
    return (len(n) - 1 if b.endswith("\n") else len(n),
            sum(1 for l in n if l.startswith("+") and not l.startswith("+++")),
            sum(1 for l in n if l.startswith("-") and not l.startswith("---")))

rows = []
for na, p in [("甲(條④の黙りを閉ぢる・旧基底で書いた)", P_KOU),
              ("丙(★陽性対照★・新基底で書いた)", P_HEI),
              ("外れ(★陰性対照★・両基底に無い行)", P_HAZ)]:
    zen, tas, hik = gyou(p)
    rc_k, msg_k = ateru(p, D_KYUU)
    rc_s, msg_s = ateru(p, D_SHIN)
    if na.startswith("甲"):
        imi = ("★旧に當たり新に當たらぬ = 疵は上流で既に閉ぢた★" if (rc_k == 0 and rc_s != 0)
               else ("両基底に當たる = 疵は新基底にも残る" if (rc_k == 0 and rc_s == 0)
                     else "★旧にすら當たらぬ ―― 當て紙を疑へ★"))
    elif na.startswith("丙"):
        imi = ("★新基底に當たる(=當て器は働く)★" if rc_s == 0 else "★新基底にすら當たらぬ = 器を疑へ★")
    else:
        imi = ("★両基底とも當たらぬ(=正)★" if (rc_k and rc_s) else "★當たつた = 陰性対照が効いて居らぬ★")
    rows.append([na, os.path.basename(p), zen, tas, hik, rc_k, ("當たる" if rc_k == 0 else "當たらぬ"),
                 rc_s, ("當たる" if rc_s == 0 else "當たらぬ"), imi, (msg_s if rc_s else msg_k)[:52]])
kaku_tsv(os.path.join(BUNDLE, "raw", "50_atenashi_apply_check.tsv"), rows,
         header=["當て紙", "file", "全行", "+行", "-行", "旧基底 rc", "旧基底", "新基底 rc", "新基底", "意", "器の言(52字で截つ)"])

# ―― 器の疵(素の走りは判ぜぬ)を此の弾でも見せる ――
su = []
for na, p in [("甲", P_KOU), ("丙", P_HEI), ("外れ", P_HAZ)]:
    rc_n, msg_n = ateru(p, D_SHIN, sunao=True)
    rc_y, _ = ateru(p, D_SHIN, sunao=False)
    # ★「素で rc=0」を一律に『偽の通』と書くな ―― 丙は真に當たる ∴ 素の 0 は判と一致する。
    #   偽である事は『判と食ひ違ふ』事で定まる(rc_n != rc_y) ―― 之を札の言葉に入れる。
    han = ("通(★偽 ―― 判と食ひ違ふ★)" if (rc_n == 0 and rc_n != rc_y)
           else ("通(判と同じ ―― 偶々當たる紙)" if rc_n == 0 else "落ち"))
    su.append([na, rc_n, han, (msg_n or "-")[:44], rc_y,
               ("通" if rc_y == 0 else "落ち"), ("★素の走りは判ぜぬ★" if rc_n != rc_y else "同じ")])
kaku_tsv(os.path.join(BUNDLE, "raw", "51_apply_check_no_kizu.tsv"), su,
         header=["當て紙", "素の rc", "素の判", "素の言(44字で截つ)", "GIT_DIR を断つた rc", "其の判", "食ひ違ひ"])

def sha(b):
    return hashlib.sha256(b).hexdigest()

kaku(os.path.join(BUNDLE, "raw", "52_atenashi_dan.txt"),
     "as-of %s(UTC)\n根=%s\n旧基底 sha256 %s\n新基底 sha256 %s\n"
     "當て紙 甲 sha256 %s(全 %d 行・+%d/-%d)\n\n"
     "【断】\n"
     "㋐ 甲は ★旧基底に當たり(rc=%s)・新基底には當たらぬ(rc=%s)★。錨 `elif [ \"$last2\" = \"0a0a\" ]` が新基底に 0 件 ―― \n"
     "   上流が裁 seq330497 で byte 比べを捨てた故である。★之を『當て紙が失敗した』と書かぬ。★\n"
     "㋑ 甲が閉ぢるのは ★空行の全 byte 形(`0a0a`/`0d0a`)★ の一面のみ。★不可視字一字の行(`800a`)は閉ぢぬ★ ―― \n"
     "   實測(raw/60): 甲を當てた旧基底でも fx06 は rc=0 で通る。形を数へ上げる仕方では閉ぢぬ ∴ 類で判ずる兄弟器が要る。\n"
     "㋒ ★據ゑて居らぬ★ ―― 當て先は _fx/kentei/ の複製のみ。共用樹の門(%s)は本弾で一字も動かして居らぬ。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        sha(KYUU_SRC), sha(SHIN_SRC), sha(open(P_KOU, "rb").read()), *gyou(P_KOU),
        rows[0][5], rows[0][7], GATE))
print("當て紙 3 枚。甲: 全%d行 +%d/-%d ―― 旧 rc=%s / 新 rc=%s" % (gyou(P_KOU)[0], gyou(P_KOU)[1], gyou(P_KOU)[2], rows[0][5], rows[0][7]))
for r in rows[1:]:
    print("  %s 旧rc=%s 新rc=%s" % (r[0], r[5], r[7]))

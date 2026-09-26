# -*- coding: utf-8 -*-
# km-199 再測 ―― 送出器の出目から seq を拾ふ抽出子の census（読むのみ）。
# 母數 = /Users/momizimac/wt/*/docs/evidence/** と repo docs/evidence/** の、名が *.sent.txt / *.sent / 送出器 stdout を
#        写した file（下の GLOBS）のうち、送出行「★<役> へ送出した★ seq=」を★一行以上★持つ物。
# 正解 = 送出行の「送出した★ seq=」直後の数（器 agent_letter.py L335 の書式そのもの）。
import os, re, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
GLOBS = [
    "/Users/momizimac/wt/*/docs/evidence/**/*.sent.txt",
    "/Users/momizimac/multi-agent-shogun/docs/evidence/**/*.sent.txt",
    os.path.join(HERE, "05_sender_out", "*.out"),
]
LINE = re.compile(r"★[^★\n]+ へ送出した★ seq=(\d+)(（parent_seq=(\d+)）)?")


def A(t):  # 家老が踏んだ形: grep -o 'seq=[0-9]*' | tail -1
    m = re.findall(r"seq=[0-9]*", t)
    return m[-1][4:] if m else None


def B(t):  # (^|[^_])seq=[0-9]+ の最初
    m = re.search(r"(^|[^_])seq=([0-9]+)", t, re.M)
    return m.group(2) if m else None


def C(t):  # 9/18 に「最短の路」と名指した sed: s/.*へ送出した★ seq=\([0-9]*\)（.*/\1/p（全角括弧に錨）
    for ln in t.splitlines():
        m = re.fullmatch(r".*へ送出した★ seq=([0-9]*)（.*", ln)
        if m:
            return m.group(1)
    return None


def C2(t):  # 錨を「送出した★ seq=」の直後の数字列に置く（括弧を要らぬ）: sed -n 's/.*へ送出した★ seq=\([0-9][0-9]*\).*/\1/p'
    for ln in t.splitlines():
        m = re.fullmatch(r".*へ送出した★ seq=([0-9][0-9]*).*", ln)
        if m:
            return m.group(1)
    return None


def D(t):  # 行頭 ★ の行の最初の seq=
    for ln in t.splitlines():
        if ln.startswith("★"):
            m = re.search(r"seq=(\d+)", ln)
            if m:
                return m.group(1)
    return None


FORMS = {"A": A, "B": B, "C": C, "C2": C2, "D": D}

files = sorted({f for g in GLOBS for f in glob.glob(g, recursive=True)})
print("# 刻", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
print(f"glob に当たつた file = {len(files)}")
have, nohave = [], []
for f in files:
    t = open(f, encoding="utf-8", errors="replace").read()
    ls = LINE.findall(t)
    (have if ls else nohave).append((f, t, ls))
print(f"送出行を持つ = {len(have)} / 持たぬ = {len(nohave)}（抽出の的が無い → 別勘定・測れぬ）")
multi = [f for f, t, ls in have if len(ls) > 1]
print(f"送出行を二行以上持つ = {len(multi)}")
wp = [x for x in have if x[2][0][2]]
np_ = [x for x in have if not x[2][0][2]]
print(f"内訳: 親あり(（parent_seq=）付き) = {len(wp)} / ★親なし★ = {len(np_)}")

res = {}
for k, fn in FORMS.items():
    for grp, lst in (("親あり", wp), ("親なし", np_)):
        tally = {"正": 0, "parent": 0, "None": 0, "他": 0}
        hit = set()
        for f, t, ls in lst:
            want, par = ls[0][0], ls[0][2]
            got = fn(t)
            if got == want:
                tally["正"] += 1; hit.add(f)
            elif got is None:
                tally["None"] += 1
            elif par and got == par:
                tally["parent"] += 1
            else:
                tally["他"] += 1
        res[(k, grp)] = hit
        print(f"  {k:2} {grp}: {tally} 和={sum(tally.values())}")

allf = {f for f, _, _ in have}
print("## 排他性（正を掴む file 集合・親あり＋親なし）")
S = {k: res[(k, '親あり')] | res[(k, '親なし')] for k in FORMS}
for a in FORMS:
    print("  " + a + ": " + " ".join(f"∩{b}={len(S[a] & S[b])}" for b in FORMS) + f" ・ 正を掴まぬ={len(allf - S[a])}")

print("## 陽性対照（今日 己が km_send.sh で出した便・raw/05）")
for n in ("km200s3.out", "km200g.out"):
    t = open(os.path.join(HERE, "05_sender_out", n), encoding="utf-8").read()
    print(f"  {n}: 行={t.strip()} → " + " ".join(f"{k}={fn(t)}" for k, fn in FORMS.items()))
print("## 親なしの送出行の例（C が落とす形・先頭3件）")
for f, t, ls in np_[:3]:
    ln = [x for x in t.splitlines() if "へ送出した★" in x][0]
    print(f"  {f} :: {ln} → C={C(t)} C2={C2(t)}")
print("## 陰性対照（送出行を持たぬ file に各形 → 何を返すか）")
neg = {k: {"None": 0, "値": 0} for k in FORMS}
for f, t, _ in nohave:
    for k, fn in FORMS.items():
        neg[k]["None" if fn(t) is None else "値"] += 1
print("  " + str(neg))
print("# 了", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))

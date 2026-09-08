#!/usr/bin/env python3
# o119: ★因果の向き★ ―― 「㋑readdir 順が真の順に近い」は ★掃いた者の証★か ★樹一般の性質★か。
#   ★四つ揃へ（走る前に 便へ出した逐語・msg_20260908_135423_ece05af7 / _f7702c05 / _48e0a383 / _9003a679）★
#   ①当て=『㋑readdir 順が真の順に近い』は ★掃いた者が readdir を辿つた証★ではなく ★樹一般の性質★かも知れぬ（因果の向き）。
#   ②検め方=帯の外の ★別刻 145 本★（窓外＝掃かれて居らぬ対照群）へ ★同じ尺★（mtime を真の順とし ㋐名/㋑readdir の逆転対）を掛ける。
#   ③外れる形（両の目が現に出得る比）=対照 145 本でも ★㋑ < ㋐/10★ が成り立てば ⇒ readdir↔mtime は樹一般の性質 ⇒『掃いた者が readdir を辿つた』の証としては ★棄てる＝第九を降ろす★。成り立たねば ⇒ 帯に特有 ⇒ ★第九は保留の儘（濃くならず 降りもせぬ）★。
#   ④不利な証（走る前に）=㋐も帯で 0.30%＝★名も時に近い＝交絡は帯でも既に在る★／別刻 145 は mtime の幅が桁違ひで塊が効く／readdir は『今の樹』の順・当時の証は無い（前弾の儘）。★見込み（実測より先に刷る）★全対 10,440・㋐ 45%・㋑ 20% ⇒ 己の当ては ★棄てられる側★ と見て居る。
#   ⑤走 1 を請ふ=器 1 本（o119_control_145_probe.py）・py_compile と突き合はせは走に数へぬ。git 実行 0（.git は logs/refs の stat と packed-refs の行の讀取のみ）・DB 讀 0 書 0 SQL 0・push/fetch/網/CI 0・現用 hook 不触・D 樹不触・Commander の箱 0 打。★許し無くば打たぬ★。
#   ★受入（家老 msg_20260908_135613_957fe336）★ ①見込みを器が実測より先に刷る ②降ろす／保留の儘 を ★三択語★ で
#     ③④の三つを結びにも ④母数 10,440 と帯 19,701 は ★別の分母★ ゆゑ ★逆転率で比べ 対数で比べるな★ ⑤器 1 本・git 実行 0。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import datetime, os

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o119_control_%s.txt" % (D, TS)
YOMI = {"帯199(除外後)": None, "対照145(別刻)": {"㋐名の辞書順": 0.45, "㋑readdir 順": 0.20}}

# ── ① 母数（前弾の落した一覧のみを材料とする）──
rows = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if not ln.startswith("#"):
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 4:
                rows.append(c)
grp  = {c[1]: c[0] for c in rows}
assert len(rows) == 345, "母数 %d（345 を前提として居る）" % len(rows)
band200 = [c[1] for c in rows if c[0] in ("空", "保つ")]
ctrl145 = [c[1] for c in rows if c[0] == "別刻"]
assert len(band200) == 200, "帯 %d" % len(band200)
assert len(ctrl145) == 145, "対照 %d" % len(ctrl145)
print("母数(引継) %d ／ 帯 %d（空+保つ）／ ★対照 別刻 %d★" % (len(rows), len(band200), len(ctrl145)))

# ── ② 除外は ★族★ で置く（o118 の条）――名を一本挙げて除くと 其の一本を選んだ事が規則に成る ──
def is_symref_family(n):
    return n.startswith("refs/") and n.rsplit("/", 1)[-1] == "HEAD"
band199 = [n for n in band200 if not is_symref_family(n)]
ctrl_ex = [n for n in ctrl145 if is_symref_family(n)]
ctrl199 = [n for n in ctrl145 if not is_symref_family(n)]
print("★帯から除いた %d 本 %s ／ 対照から除いた %d 本 %s★" % (
      len(band200) - len(band199), [n for n in band200 if is_symref_family(n)],
      len(ctrl_ex), ctrl_ex))

# ── ③ readdir 順（logs/refs 樹を 一度だけ走査・sort せぬ）──
walk = []
def rec(d, rel):
    try:
        ents = list(os.scandir(d))          # ★sort せぬ＝readdir の順★
    except OSError:
        return
    for e in ents:
        r = rel + "/" + e.name if rel else e.name
        if e.is_dir(follow_symlinks=False):
            rec(e.path, r)
        else:
            walk.append("logs/" + r)
rec(os.path.join(GIT, "logs", "refs"), "refs")
pos_w = {nm: i for i, nm in enumerate(x[len("logs/"):] for x in walk)}

# ── ④ packed-refs の行順 ──
pos_p = {}; nline = 0
with open(os.path.join(GIT, "packed-refs"), encoding="utf-8", errors="replace") as f:
    for ln in f:
        if ln.startswith(("#", "^")):
            continue
        p = ln.split()
        if len(p) >= 2:
            pos_p[p[1]] = nline; nline += 1
print("readdir 走査 %d file ／ packed-refs 行 %d" % (len(walk), nline))

def inversions(seq, rank):
    a = [rank[n] for n in seq]
    return sum(1 for x in range(len(a)) for y in range(x + 1, len(a)) if a[x] > a[y])

def measure(label, names, yomi):
    mt = {}; nomt = []
    for nm in names:
        try:
            mt[nm] = os.stat(os.path.join(GIT, "logs", nm)).st_mtime_ns
        except OSError as e:
            nomt.append((nm, type(e).__name__))
    tgt = [n for n in names if n in mt]
    if len(tgt) < 2:
        print("  %s ―― mtime 取れた %d 本 ∴ 尺を掛けられぬ" % (label, len(tgt)))
        return None
    truth = sorted(tgt, key=lambda n: (mt[n], n))
    rank  = {n: i for i, n in enumerate(truth)}
    ties  = len(tgt) - len(set(mt[n] for n in tgt))
    span  = (max(mt[n] for n in tgt) - min(mt[n] for n in tgt)) / 1e9
    tot   = len(tgt) * (len(tgt) - 1) // 2
    cands = (("㋐名の辞書順",        sorted(tgt)),
             ("㋑readdir 順",        sorted(tgt, key=lambda n: pos_w.get(n, 10 ** 9))),
             ("㋒packed-refs 行順",  sorted(tgt, key=lambda n: pos_p.get(n, 10 ** 9))))
    print("── %s ── 本数 %d ／ 全対 %d ／ mtime の幅 %.3f 秒 ／ 同値 %d 対 ／ mtime 取れぬ %d %s" % (
          label, len(tgt), tot, span, ties, len(nomt), [n for n, _ in nomt][:3]))
    print("   readdir に載る %d ／ packed-refs に載る %d" % (
          sum(1 for n in tgt if n in pos_w), sum(1 for n in tgt if n in pos_p)))
    res = {}
    for lab, seq in cands:
        inv = inversions(seq, rank)
        res[lab] = inv
        y = (yomi or {}).get(lab)
        ytxt = ""
        if y is not None:
            ytxt = "［見込 %.0f%%／差 %+.2f 点］" % (100.0 * y, 100.0 * inv / tot - 100.0 * y)
        print("   %-18s 逆転 %6d / %6d ＝ %.2f%% %s" % (lab, inv, tot, 100.0 * inv / tot, ytxt))
    ia = res["㋐名の辞書順"]; ib = res["㋑readdir 順"]
    print("   ㋐と㋒は同一順か: %s" % ("★同一★" if cands[0][1] == cands[2][1] else "違ふ"))
    return {"n": len(tgt), "tot": tot, "a": ia, "b": ib,
            "c": res["㋒packed-refs 行順"], "span": span, "ties": ties}

print("★見込み（走る前に便で送つた・実測より先に刷る）★ 対照 145: 全対 10,440 ／ ㋐ 45% ／ ㋑ 20% ―― ★実測はこの下★")
r_band = measure("帯199（除外後・陽性対照＝o118 の再現）", band199, None)
r_ctrl = measure("対照145（別刻＝掃かれて居らぬ群）",      ctrl199, YOMI["対照145(別刻)"])

# ── ⑤ 宣言した尺（比で書く・両の目が現に出得る）──
print("")
for lab, r in (("帯199", r_band), ("対照145", r_ctrl)):
    if r:
        thr = r["a"] / 10.0
        print("★宣言した尺★ %s: ㋑(%d) < ㋐(%d)/10 (=%.1f) か ⇒ %s" % (
              lab, r["b"], r["a"], thr, "★成り立つ★" if r["b"] < thr else "★成り立たぬ★"))
if r_band and r_ctrl:
    thr = r_ctrl["a"] / 10.0
    if r_ctrl["b"] < thr:
        verdict = "★降ろす★＝readdir↔mtime は ★樹一般の性質★ ⇒『掃いた者が readdir を辿つた』の証に成らぬ（第九を降ろす）"
    else:
        verdict = "★保留の儘★＝帯に固有（濃くならず 降りもせぬ・得る物は ★向きが判つた事★ のみ）"
    print("★三択語（受入②・三つを並べ 何れかを指す）★ ①降ろす ②保留の儘 ③濃くする")
    print("   ―― ★③濃くする は本弾では ★原理として出ぬ★（対照が近くない事は 第九を ★支へぬ★・向きが判るのみ）★")
    print("★三択語★: %s" % verdict)
    print("★分母が違ふ★ 帯 %d 対 ／ 対照 %d 対 ―― ★逆転率(%%)で比べ 対数で比べぬ★" % (r_band["tot"], r_ctrl["tot"]))
    print("★幅★ 帯 %.3f 秒 ／ 対照 %.0f 秒（%.1f 日）―― ★桁違ひ（走る前に書いた不利な証）★" % (
          r_band["span"], r_ctrl["span"], r_ctrl["span"] / 86400.0))

# ── ⑥ 名の一覧を落とす（五条の親類）──
mt_all = {}
for nm in ctrl199 + band199:
    try:
        mt_all[nm] = os.stat(os.path.join(GIT, "logs", nm)).st_mtime_ns
    except OSError:
        pass
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o119 群／名／mtime_ns／readdir 位置／packed 行（対照145 と 帯199）\n")
    for nm in sorted(mt_all, key=lambda n: (mt_all[n], n)):
        f.write("\t".join([grp.get(nm, "?"), nm, str(mt_all[nm]),
                           str(pos_w.get(nm, -1)), str(pos_p.get(nm, -1))]) + "\n")
print("名の一覧: %s (%d 行)" % (OUT, len(mt_all) + 1))
print("[八条目] 母数 345・帯 200・除外は族(refs/**/HEAD) ―― ★o118 の儘★。★動かしたのは 群（対照 145 を足した）★。")
print("[八条目] 尺は o118 の儘（㋑ < ㋐/10 の比）。★分母は群ごとに違ふ ∴ 率で比べる★。")

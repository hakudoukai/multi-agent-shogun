#!/usr/bin/env python3
# o117: 第八の目「★掃く/掃かぬ の切り替はり★は ★prefix の境で起きるか 内側で起きるか★」。
#   ★当て★=掃く/掃かぬは ★file ごと★ に決まつた（席=prefix ごとではない）
#           ∴ 切り替はりは prefix の境に ★寄らぬ★。
#   ★検め方（走る前に送つた）★=帯200を真の順(mtime_ns・同値は名)に並べ、隣接199対のうち
#     ㋐札(空/保つ)の入替る対 B ㋑prefix の変る対 P ㋒両方の対 O を数へる。
#     prefix ＝ 名から末尾一節を除いた所（o115 §22-3 と同じ定義）。
#   ★期待値★ E = B × P/199 ―― ★実測 O の前に刷る★（走る前に約した通り）。
#   ★外れる形（走る前に送つた）★=O が E の ★2 倍未満★ なら ★棄てる★。
#   ★不利な証（走る前に送つた）★=㋐prefix は生年と交絡(o115 §22-3) ㋑塊20 は四つの並び悉く同じ
#     ゆゑ並びを選ばぬ量(o116 §23-4) ㋒己の前科三つ（贋の名／組の名の誤り／出得ぬ閾）
#     ㋓B が小さければ E も小さく 2倍の閾は少数で容易に超え得る。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import datetime, os

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o117_switch_%s.txt" % (D, TS)

# ── ① 母数（前弾の落した一覧のみを材料とする）──
rows = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if not ln.startswith("#"):
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 4:
                rows.append(c)
grp  = {c[1]: c[0] for c in rows}
band = [c[1] for c in rows if c[0] in ("空", "保つ")]
assert len(rows) == 345, "母数 %d（345 を前提として居る）" % len(rows)
print("母数(引継) %d ／ 帯 %d 本（空 %d ／ 保つ %d）" % (
      len(rows), len(band),
      sum(1 for n in band if grp[n] == "空"),
      sum(1 for n in band if grp[n] == "保つ")))

# ── ② 真の順 ──
mt = {}; nomt = []
for nm in band:
    try:
        mt[nm] = os.stat(os.path.join(GIT, "logs", nm)).st_mtime_ns
    except OSError as e:
        nomt.append(nm)
print("mtime 取れた %d ／ 取れぬ %d %s" % (len(mt), len(nomt), nomt[:5]))
tgt   = [n for n in band if n in mt]
truth = sorted(tgt, key=lambda n: (mt[n], n))

def pre(n):
    return n.rsplit("/", 1)[0] if "/" in n else "(根)"

# ── ③ 塊（札の連なり）──
runs = 1
for i in range(1, len(truth)):
    if grp[truth[i]] != grp[truth[i-1]]:
        runs += 1
print("★塊(札の連なり)★ %d 個 ⇒ 切り替はりは %d 対（前便の『20 箇所』は誤り・19 が正）" % (runs, runs - 1))

pairs = len(truth) - 1
B = sum(1 for i in range(pairs) if grp[truth[i+1]] != grp[truth[i]])
P = sum(1 for i in range(pairs) if pre(truth[i+1]) != pre(truth[i]))
E = B * P / float(pairs)
print("隣接対 %d ／ 札の入替る対 B=%d ／ prefix の変る対 P=%d (%.1f%%)" % (pairs, B, P, 100.0*P/pairs))
print("★期待値 E = B × P/%d = %.2f★  ―― ★実測はこの下に刷る★" % (pairs, E))

O = sum(1 for i in range(pairs)
        if grp[truth[i+1]] != grp[truth[i]] and pre(truth[i+1]) != pre(truth[i]))
print("★実測 O = %d★ ／ O/E = %.2f 倍" % (O, (O/E) if E else float("nan")))
print("★宣言した尺★: O < 2E(=%.2f) なら ★棄てる★ ⇒ %s" % (
      2*E, "★棄てる★" if O < 2*E else "★棄てぬ★"))

# ── ④ 副（走る前に宣言して居らぬ ⇒ 當たりに数へぬ）──
def pre2(n):
    p = n.split("/")
    return "/".join(p[:2]) if len(p) >= 2 else n
P2 = sum(1 for i in range(pairs) if pre2(truth[i+1]) != pre2(truth[i]))
O2 = sum(1 for i in range(pairs)
         if grp[truth[i+1]] != grp[truth[i]] and pre2(truth[i+1]) != pre2(truth[i]))
E2 = B * P2 / float(pairs)
print("[副・宣言せぬ尺ゆゑ當たりに数へぬ] 粗い prefix(上二節): P2=%d E2=%.2f O2=%d" % (P2, E2, O2))

# ── ⑤ 名を残す（五十条目）──
lines = ["# o117 切り替はり対の名（真の順・mtime_ns 昇順）as_of %s" % TS,
         "# 列: 位置\t左の名\t左の札\t左のprefix\t右の名\t右の札\t右のprefix\tprefix変る?"]
for i in range(pairs):
    if grp[truth[i+1]] != grp[truth[i]]:
        a, b = truth[i], truth[i+1]
        lines.append("%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            i, a, grp[a], pre(a), b, grp[b], pre(b),
            "変る" if pre(a) != pre(b) else "同じ"))
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("名の一覧 %s （%d 行）" % (OUT, len(lines)))

# ── ⑥ 八条目（物差しを動かした分）──
print("[八条目] 母数 345 は o112 の一覧の儘・帯 200 も o116 と同じ。")
print("[八条目] ★動かしたのは尺★=o116 は『全対 19,900 の逆転』・本弾は『隣接 199 対』。")
print("[八条目] ★除いた本は無し★(o116 の post-hoc で除いた origin/HEAD も ★本弾では除かぬ★)。")

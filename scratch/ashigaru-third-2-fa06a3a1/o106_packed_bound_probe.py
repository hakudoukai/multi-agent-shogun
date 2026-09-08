#!/usr/bin/env python3
# order106 / 席 ashigaru-third-2 / as_of 2026-09-08 10:5x JST
# 問ひ = 「何れの器でも刻を持たぬ 132 本」は ★窓の内に生れ得るか★。
# 当てる器 = ★.git/packed-refs★ ―― 載る ref は ★畳んだ刻に在つた★。
#   ∴ 畳んだ刻 (mtime) が 窓の左端より ★前★ なら ―― 其の ref は窓で生れ得ぬ（下振れ源が一つ消える）。
#   ★畳んだ刻より後（＝左端より後に畳んだ）なら 何も決まらぬ ―― 其の時は「決まらぬ」と書く。★
# 註 = 分類（讀めた/空/tab 無し/file 無し）は ★o105 の規則を写した＝二重実装★。紙で開示する。
#      写す理由 = o105 は分類を刷るのみで ★名の一覧を file に残さなんだ★（＝五条の親類・己の疵、三度目）。
# 走: python process ★1本★（git 讀取 0 ―― 本弾は file を直に讀むのみ）。
import pathlib, datetime, os

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path("/mnt/c/DentalBI")
GIT  = REPO / ".git"
LOGS = GIT / "logs"
JST  = datetime.timezone(datetime.timedelta(hours=9))
def j(ts): return datetime.datetime.fromtimestamp(ts, JST).isoformat(timespec="seconds")

L = os.stat(HERE / "o98_overlap_probe.py").st_mtime
R = os.stat(HERE / "o102_run1_raw.txt").st_mtime
print("== 窓（前弾と同じ・動かして居らぬ）==")
print("左端 %s（代用）/ 右端 %s（生出力 mtime）" % (j(L), j(R)))

print("\n== ★測る前に置く（値切り）★ ==")
print("・packed-refs の mtime が 窓の左端 ★より後★ なら ―― 本器は ★何も決めぬ★。其の時は『決まらぬ』と書く。")
print("・packed-refs が言へるは ★『畳んだ刻には在つた』★ 迄 ―― ★生れた刻は本器でも出ぬ★。")
print("・窓の内に生れて ★窓の内に消えた★ ref は 本器でも見えぬ（① のまま）。")

# ―― 現 ref（二枚目を正とする・新たに落とさぬ）
NEW = HERE / "o103_refs_20260908_102945.txt"
cur = [l.split("\t")[0] for l in NEW.read_text(encoding="utf-8").split("\n") if l and not l.startswith("#")]

# ―― 分類（o105 の規則を写す）
dated, undated = [], []
for name in cur:
    p = LOGS / name
    ok = False
    if p.is_file() and p.stat().st_size > 0:
        head = p.read_text(errors="replace").split("\n")[0]
        if "\t" in head:
            try:
                int(head.split("\t")[0].split()[-2]); ok = True
            except Exception:
                ok = False
    (dated if ok else undated).append(name)
# loose file を持つ物は o105 が mtime で当てた ∴ 本器の対象から外す
loose  = [n for n in undated if (GIT / n).is_file()]
target = [n for n in undated if not (GIT / n).is_file()]
print("\n== 分類（o105 と同じ規則・合計を母数と突き合はす）==")
print("現 ref %d ＝ 刻を讀めた %d ＋ 刻を持たぬ %d（うち loose mtime で当てた %d / ★本器の的 %d★）"
      % (len(cur), len(dated), len(undated), len(loose), len(target)))
assert len(dated) + len(undated) == len(cur)

# ―― packed-refs
pr = GIT / "packed-refs"
print("\n== packed-refs ==")
if not pr.is_file():
    print("★packed-refs が無い ―― 本器は何も決めぬ（決まらぬ）★"); raise SystemExit(0)
m = pr.stat().st_mtime
lines = pr.read_text(errors="replace").split("\n")
packed = set()
for l in lines:
    if not l or l.startswith("#") or l.startswith("^"):
        continue
    parts = l.split(" ", 1)
    if len(parts) == 2:
        packed.add(parts[1].strip())
print("mtime = ★%s★ / 載る ref = ★%d 本★（行 %d）" % (j(m), len(packed), len(lines)))
print("窓の左端 %s との比 = ★%s★" % (j(L), "畳んだ刻の方が ★前★（＝決まる）" if m <= L else "畳んだ刻の方が ★後★（＝決まらぬ）"))

inside  = [n for n in target if n in packed]
outside = [n for n in target if n not in packed]
print("\n== 的 %d 本の内訳 ==" % len(target))
print("packed-refs に ★載る★ = ★%d★ / ★載らぬ★ = ★%d★" % (len(inside), len(outside)))
if outside:
    print("  載らぬ物の名（先頭 10）: %s%s" % (", ".join(outside[:10]), " …他 %d" % (len(outside)-10) if len(outside) > 10 else ""))

print("\n== 答 ==")
if m <= L:
    print("packed-refs は 窓の左端より ★前★ に畳まれて居る ∴ ★載る %d 本は 畳んだ刻に既に在つた＝窓で生れ得ぬ★。" % len(inside))
    print("★下振れ源の一つ（刻を持たぬ %d 本）は ―― %d 本が消え、★%d 本★ が残る。★" % (len(target), len(inside), len(outside)))
else:
    print("★決まらぬ★ ―― packed-refs は窓の左端より後に畳まれて居る ∴ 載る事は『窓の前から在つた』の証にならぬ。")
    print("★下振れ源は %d 本のまま 一つも消えて居らぬ。★" % len(target))
print("\n== 残る下振れ源（数へ直し）==")
print("㋑ 窓の内に生れて窓の内に消えた ref ―― ★数へられぬ（①）★")
print("㋺ 刻を持たぬまま残る ref ―― ★%d 本★" % (len(outside) if m <= L else len(target)))
print("㋩ 窓の左端が ★代用★（o98 が生出力を残さなんだ）―― ★直せぬ（①）★")

# ―― 五条の親類を塞ぐ: 的の名を file に残す
out = HERE / ("o106_undated_%s.txt" % datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S"))
body = "".join("%s\t%s\n" % (n, "packed" if n in packed else "unpacked") for n in sorted(target))
out.write_text("# 刻を持たぬ ref（log が空/tab 無し/無し・loose file も無し）/ as_of %s / %d 本\n"
               "# 1 行 = <refname>\\t<packed|unpacked>。★o105 は数のみ残し 名を残さなんだ ―― 其の埋め。★\n"
               % (j(os.stat(NEW).st_mtime), len(target)) + body, encoding="utf-8")
import hashlib
print("\n名の一覧を落とした = %s / %d 行 / sha256:16 = %s"
      % (out.name, 2 + len(target), hashlib.sha256(out.read_bytes()).hexdigest()[:16]))

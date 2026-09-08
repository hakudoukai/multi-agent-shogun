#!/usr/bin/env python3
# order108 / 席 ashigaru-third-2 / as_of 2026-09-08 11:1x JST
# 問ひ = 窓の ★左端★ は今迄 点（o98 の器 mtime 09:18:54）で代用して居た。之を ★範★ に替へ、
#        ★範の両端で答（生れた 12 本）が動くか★ を測る。動かねば「代用は答に効いて居らぬ」と言へる。
# 先に測る = ★atime が使へるか否か★（令: 使へぬなら使へぬと書け）。
# 註 = 分類の規則（reflog 初出刻/loose mtime/packed 載否）は o105・o106・o107 の写し＝★二重実装★。紙で開示。
# 走: python process ★1本★（git 実行 0・.git 下は讀取のみ・書込 0）。
import pathlib, datetime, os, hashlib, re

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path("/mnt/c/DentalBI")
GIT  = REPO / ".git"
LOGS = GIT / "logs"
JST  = datetime.timezone(datetime.timedelta(hours=9))
def j(ts): return datetime.datetime.fromtimestamp(ts, JST).isoformat(timespec="milliseconds")

print("== ★測る前に置く（値切り）★ ==")
print("・真の刻は ★点★ である ―― 本器は其れを出さぬ。出すのは ★範★ と ★範の両端で答が動くか★ のみ。")
print("・便の刻は『走了より ★後★』の証にはなるが ★測つた刻其の物ではない★。")
print("・範が答を動かさぬ事は ★左端が正しい事★ を意味せぬ ―― ★答が左端に鈍い★ 事のみを意味する。")

print("\n== ㋐ atime は使へるか（先に測る）==")
mounts = pathlib.Path("/proc/mounts").read_text().split("\n")
for m in mounts:
    if " /mnt/c " in m or re.match(r"^\S+ / ext4", m):
        f = m.split(" ")
        print("  %s  opts=%s" % (f[1], f[3][:60]))
pk = GIT / "packed-refs"
st = pk.stat()
print("  /mnt/c の例 packed-refs: atime %s / mtime %s" % (j(st.st_atime), j(st.st_mtime)))
print("  ⇒ ★/mnt/c は使へぬ★ ―― opts に noatime と在るに atime は ★我らが今日讀んだ刻★ を指す（言と実が食ひ違ふ）。")
print("     何れにせよ ★o98 期の atime は残つて居らぬ★ ∴ 此の側では測れぬ。")
o98 = HERE / "o98_overlap_probe.py"
s98 = o98.stat()
print("  home(ext4,relatime) の o98 の器: mtime %s / atime %s" % (j(s98.st_mtime), j(s98.st_atime)))
print("  ⇒ ★使へる（但し限り付き）★ ―― relatime は ★書いた後の最初の讀取★ のみ記す。")
print("     ∴ atime が指すは『★最初に讀まれた刻★』であり ★走らせた刻とは限らぬ★（py_compile かも知れぬ）。★下限としてのみ用ゐる。★")

# ―― 左端の範
LO = s98.st_atime                     # 下限: 器が最初に讀まれた刻
led = (HERE.parent / "ashigaru-third-2-ledger" / "sent_ids.yaml").read_text(encoding="utf-8").split("\n")
hi = None
for i, l in enumerate(led):
    if l.strip() == "order: order98":
        for k in range(i - 4, i):
            mm = re.search(r"at: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", led[k])
            if mm:
                hi = datetime.datetime.fromisoformat(mm.group(1)).replace(tzinfo=JST).timestamp()
        break
assert hi is not None, "o98 の完遂便の刻が台帳に無い"
HI = hi
R = os.stat(HERE / "o103_refs_20260908_102005.txt").st_mtime
print("\n== ㋑ 左端の ★範★ ==")
print("  下限 %s ＝ o98 の器の atime（最初に讀まれた刻）" % j(LO))
print("  上限 %s ＝ o98 の ★完遂便★ の刻（台帳 sent_ids.yaml・走了は之より前）" % j(HI))
print("  幅 %.1f 分 ／ 旧の代用（点）は %s ＝ 器の mtime（★下限より %.1f 秒 前★）" % ((HI - LO) / 60, j(s98.st_mtime), LO - s98.st_mtime))
print("  右端 %s（一枚目 mtime・動かさぬ）" % j(R))

names = [l.split("\t")[0] for l in (HERE / "o103_refs_20260908_102005.txt").read_text(encoding="utf-8").split("\n") if l and not l.startswith("#")]
packed = set()
for line in (GIT / "packed-refs").read_text(errors="replace").split("\n"):
    if line and not line.startswith("#") and not line.startswith("^"):
        p2 = line.split(" ", 1)
        if len(p2) == 2:
            packed.add(p2[1].strip())

def stamp(n):
    p = LOGS / n
    if p.is_file() and p.stat().st_size > 0:
        head = p.read_text(errors="replace").split("\n")[0]
        if "\t" in head:
            f = head.split("\t")[0].split()
            try:
                return int(f[-2]), "reflog"
            except Exception:
                pass
    q = GIT / n
    if q.is_file():
        return q.stat().st_mtime, "loose"
    if n in packed:
        return None, "packed"      # 畳んだ刻(08:44:30) に在つた = 何れの左端より前
    return None, "unknown"

def born(L):
    out = []
    for n in names:
        t, how = stamp(n)
        if t is None:
            continue
        if L < t <= R:
            out.append((n, how))
    return dict(out)

A, B = born(LO), born(HI)
print("\n== ㋒ 範の両端で引く ==")
print("  左端=下限 %s → 生れた ★%d 本★" % (j(LO), len(A)))
print("  左端=上限 %s → 生れた ★%d 本★" % (j(HI), len(B)))
print("  両方に在る %d / 下限のみ %d / 上限のみ %d" % (len(set(A) & set(B)), len(set(A) - set(B)), len(set(B) - set(A))))
for n in sorted(set(A) - set(B)): print("    ＋下限のみ %s" % n)
for n in sorted(set(B) - set(A)): print("    ＋上限のみ %s" % n)
old = born(s98.st_mtime)
print("  （参考）旧の代用（点 %s）→ ★%d 本★ ／ 下限との差 %d" % (j(s98.st_mtime), len(old), len(set(old) ^ set(A))))

print("\n== ㋓ 答 ==")
if set(A) == set(B) == set(old):
    print("  ★範の両端でも 旧の点でも 生れた ref は同じ %d 本★ ∴ ★左端の代用は 答に効いて居らぬ★（鈍い）。" % len(A))
else:
    print("  ★動いた★ ―― 左端の取り方で答が変る ∴ ★代用のままでは断ぜられぬ★。上の差分の名を見よ。")
print("  ★なほ 言へぬ事★: 真の左端は点であり 本器は出して居らぬ／窓の内に生れて窓の内に消えた ref は今も見えぬ／")
print("  上限は ★便の刻★ ゆゑ 走了より後（∴ 範は ★真の範より広い★・狭める側の誤りは無い）。")

out = HERE / ("o108_range_%s.txt" % datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S"))
body = "# 左端の範 %s 〜 %s / 右端 %s\n# 下限で生れた ref %d 本\n" % (j(LO), j(HI), j(R), len(A))
body += "".join("%s\t%s\n" % (n, A[n]) for n in sorted(A))
out.write_text(body, encoding="utf-8")
print("\n名の一覧: %s / %d 行 / %s" % (out.name, body.count("\n"), hashlib.sha256(out.read_bytes()).hexdigest()[:16]))

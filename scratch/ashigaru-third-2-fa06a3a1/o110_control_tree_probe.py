#!/usr/bin/env python3
# order110 / 席 ashigaru-third-2 / as_of 2026-09-08 11:2x JST
# 問ひ = o109 の 0 は「物が無かつた」側であつた。★ならば 物の在る所へ行く★ ――
#        reflog が生きて居る樹（当席 home の作業樹）を ★対照★ に立て、
#        同じ道（reflog の消え残りで「消えた ref」を拾ふ）が ★材料さへ在れば効くか★ を測る。
#        併せて ★/mnt/c 側の 0 byte 112 本の mtime を刻で束ね★「一度の出来事で空にされたか」を見る。
# 註 = ref/log の読み方は o103-o109 の写し＝★二重実装★（紙で開示）。
# 走: python process ★1本★（git 実行 0・両樹の .git は ★讀取のみ★・書込 0）。
import pathlib, datetime, os, re, collections

HERE = pathlib.Path(__file__).resolve().parent
JST  = datetime.timezone(datetime.timedelta(hours=9))
Z40  = "0" * 40
def j(ts): return datetime.datetime.fromtimestamp(ts, JST).isoformat(timespec="seconds")

MNTC = pathlib.Path("/mnt/c/DentalBI/.git")
HOME = pathlib.Path("/home/hakudoukai/multi-agent-shogun/.git")

print("== ★測る前に置く（値切り）★ ==")
print("・二つの樹は ★同じ物ではない★ ―― 齢も 使ひ方も 畳み方も違ふ。★対照であつて 同一条件の実験に非ず。★")
print("・home 側で拾へたとしても、それは『★此の道は材料が在れば効く★』までしか言はぬ。")
print("  ★/mnt/c 側で何が起きたかは 依然 何も言はぬ。★")
print("・home 側でも 0 なら ★『効く証を得ず』★ としか書かぬ（『効かぬ』とは書かぬ）。")
print("・mtime の束は ★空にした刻★ を指すとは限らぬ（file を触つた別の事でも動く）。★見当であり 証に非ず。★")

def survey(G, label):
    now = set()
    rd = G / "refs"
    for p in rd.rglob("*"):
        if p.is_file():
            now.add("refs/" + str(p.relative_to(rd)).replace(os.sep, "/"))
    n_loose = len(now)
    n_pk = 0
    pk = G / "packed-refs"
    if pk.exists():
        for l in pk.read_text(encoding="utf-8", errors="replace").split("\n"):
            if not l or l[0] in "#^":
                continue
            f = l.split(" ", 1)
            if len(f) == 2:
                now.add(f[1].strip()); n_pk += 1
    LR = G / "logs" / "refs"
    logs, zero, unparsed = {}, [], []
    for p in LR.rglob("*"):
        if not p.is_file():
            continue
        nm = "refs/" + str(p.relative_to(LR)).replace(os.sep, "/")
        st = p.stat()
        if st.st_size == 0:
            zero.append((nm, st.st_mtime)); continue
        ent = []
        for l in p.read_text(encoding="utf-8", errors="replace").split("\n"):
            if not l.strip():
                continue
            m = re.match(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .*?> (\d+) ([+-]\d{4})\t?(.*)$", l)
            if m:
                ent.append((m.group(1), m.group(2), int(m.group(3)), m.group(5)))
        if ent:
            logs[nm] = ent
        else:
            unparsed.append(nm)
    orphan = sorted(n for n in logs if n not in now)
    hd = G / "logs" / "HEAD"
    hl = len(hd.read_text(encoding="utf-8", errors="replace").split("\n")) - 1 if hd.exists() else 0
    print("\n== %s ==" % label)
    print("  今の ref: loose %d ＋ packed %d ⇒ 相異なる名 %d" % (n_loose, n_pk, len(now)))
    print("  logs/refs: file %d ＝ 讀めた %d ＋ ★0 byte %d★ ＋ 形が合はぬ %d" % (len(logs)+len(zero)+len(unparsed), len(logs), len(zero), len(unparsed)))
    print("  logs/HEAD: %d 行" % hl)
    print("  ★消え残り（log は在るが 今 ref に無い名）= %d 本★" % len(orphan))
    for nm in orphan[:12]:
        e = logs[nm]
        b = j(e[0][2]) if e[0][0] == Z40 else "★先頭が誕生に非ず★"
        print("    %-46s 誕生 %s / 最後 %s / %s" % (nm[:46], b, j(e[-1][2]), e[-1][3][:34]))
    if len(orphan) > 12:
        print("    … 他 %d 本" % (len(orphan) - 12))
    return dict(now=now, logs=logs, zero=zero, unparsed=unparsed, orphan=orphan, hl=hl)

a = survey(MNTC, "㋐ /mnt/c 側（o109 と同じ樹・再測）")
b = survey(HOME, "㋑ home 側（★対照★・reflog 生存）")

print("\n== ㋒ ★答 ―― 道は材料さへ在れば効くか★ ==")
if b["orphan"]:
    print("  home 側で ★%d 本 拾へた★ ∴ ★此の道は 材料（生きた reflog）が在れば ★現に効く★★。" % len(b["orphan"]))
    print("  ⇒ /mnt/c 側の 0 は ★道が効かぬ故ではなく 材料が無い故★ と読める（★但し 之は /mnt/c で何が起きたかを言はぬ★）。")
else:
    print("  home 側でも ★0 本★ ―― ★『効く証を得ず』★ としか書かぬ。")
    print("  因は二つ在り得 ★分けられぬ★: ①此の樹でも ref 削除時 log が共に消える ②そもそも ref を消して居らぬ。")

print("\n== ㋓ ★0 byte 112 本は 一度の出来事か★（刻で束ねる）==")
z = a["zero"]
if z:
    bym = collections.Counter(datetime.datetime.fromtimestamp(t, JST).strftime("%Y-%m-%d %H:%M") for _, t in z)
    print("  0 byte %d 本 の mtime を ★分★ で束ねた ―― 相異なる分 %d 個" % (len(z), len(bym)))
    for k, v in sorted(bym.items())[:12]:
        print("    %s  %d 本" % (k, v))
    if len(bym) > 12:
        print("    … 他 %d 分" % (len(bym) - 12))
    top = bym.most_common(1)[0]
    print("  最も多い分 %s に ★%d 本／%d 本★（%.0f%%）" % (top[0], top[1], len(z), 100.0*top[1]/len(z)))
    tops = sorted(t for _, t in z)
    print("  最も古い %s ／ 最も新しい %s ／ 幅 %.1f 日" % (j(tops[0]), j(tops[-1]), (tops[-1]-tops[0])/86400))
    nz = []
    LR = MNTC / "logs" / "refs"
    for p in LR.rglob("*"):
        if p.is_file() and p.stat().st_size > 0:
            nz.append(p.stat().st_mtime)
    if nz:
        print("  対比: 非 0 byte %d 本 の mtime 幅 %.1f 日（最古 %s / 最新 %s）" % (len(nz), (max(nz)-min(nz))/86400, j(min(nz)), j(max(nz))))
    print("  ★註★ mtime は『空にした刻』とは限らぬ ―― ★見当であり 証に非ず★（値切り 第五項）。")

# ―― 名の一覧（0 本でも落とす）
stamp = datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S")
op = HERE / ("o110_control_%s.txt" % stamp)
buf = ["# order110 対照（home 樹）と 0 byte の刻 / as_of %s" % j(datetime.datetime.now(JST).timestamp()),
       "# home 側 消え残り = %d 本 / /mnt/c 側 消え残り = %d 本" % (len(b["orphan"]), len(a["orphan"])),
       "#--- home 側 消え残り 全件（名\t誕生\t最後\t最後の msg）---"]
for nm in b["orphan"]:
    e = b["logs"][nm]
    buf.append("%s\t%s\t%s\t%s" % (nm, j(e[0][2]) if e[0][0] == Z40 else "誕生に非ず", j(e[-1][2]), e[-1][3][:60]))
buf.append("#--- /mnt/c 側 0 byte 全件（名\tmtime）---")
for nm, t in sorted(a["zero"], key=lambda x: x[1]):
    buf.append("%s\t%s" % (nm, j(t)))
with open(op, "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
print("\n名の一覧: %s（%d 行）" % (op.name, len(buf)))

print("\n== 検算 ==")
for lab, d in (("/mnt/c", a), ("home", b)):
    tot = len(d["logs"]) + len(d["zero"]) + len(d["unparsed"])
    print("  %s: file %d ＝ 讀めた %d ＋ 0 byte %d ＋ 形が合はぬ %d ／ 讀めた %d ＝ 今も在る %d ＋ 今は無い %d"
          % (lab, tot, len(d["logs"]), len(d["zero"]), len(d["unparsed"]), len(d["logs"]), len(d["logs"])-len(d["orphan"]), len(d["orphan"])))
print("  ★足して合ふ事を確かめた★")

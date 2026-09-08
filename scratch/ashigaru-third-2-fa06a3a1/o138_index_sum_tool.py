#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# o138: ★索引の『和の作り方』其の物を直す器★（家老令 msg_20260909_054051_18d4b1e9
#       「同じ形が五度なら ★和の作り方其の物★ を直せ」）。
#
# ★何を直すか★= 之迄 §1/§2 の表の cell（行数・sha16）と 見出しの和は ★手で写して居た★。
#   ∴ 紙を継ぎ足した手番で cell を打ち忘れると ★表が古びる★ ―― v19/v35/v39/v52/v57 と ★五度★ 同じ形で転んだ。
# ★如何に直すか★= 表の cell は ★file から作る★。此の器は
#   ①表の各行の名を讀み ②其の file を `wc -l` 相当と sha256 で測り ③cell を書き替へ
#   ④和を ★其の場で足して★ 「和の行」を書き替へる。★手で写す道を無くす★。
# ★之が直さぬ物★= 表に ★載つて居らぬ file★ は依然 数へられぬ（名を足すのは人の手）。
#   ∴ 本器は「cell の据ゑ置き」を殺すが「行の書き落し」は殺さぬ ―― ★別の疵である★。
# ★走に数へるか★= 数へぬ（新たに測る数は無く file の行数/digest のみ・索引の作法 v50 以来と同じ）。
# ★書込は索引 1 本のみ★（`--check` なら書かず 食ひ違ひを刷るだけ）。
import hashlib, io, os, re, sys, datetime

D    = os.path.dirname(os.path.abspath(__file__))
IDX  = os.path.join(D, "o97_handover_index_v1.md")
if "--idx" in sys.argv:                     # ★対照用★（写しに当てて 器が鳴るかを検める）
    IDX = sys.argv[sys.argv.index("--idx") + 1]
LEDG = os.path.join(os.path.dirname(D), "ashigaru-third-2-ledger", "sent_ids.yaml")
CHECK = "--check" in sys.argv

def measure(path):
    b = io.open(path, "rb").read()
    return b.count(b"\n"), hashlib.sha256(b).hexdigest()[:16]

def find(name):
    """表の cell に載る名から 実在の path を引く（scratch 二箇所 ＋ repo の器）。"""
    for cand in (os.path.join(D, name),
                 os.path.join(os.path.dirname(D), "ashigaru-third-2-ledger", name),
                 os.path.join("/home/hakudoukai/multi-agent-shogun/scripts/sweeps", name)):
        if os.path.isfile(cand):
            return cand
    return None

s = io.open(IDX, encoding="utf-8").read()
lines = s.split("\n")
missing, changed = [], []

for i, ln in enumerate(lines):
    if not ln.startswith("| `"):
        continue
    cells = ln.split(" | ")
    if len(cells) < 4:
        continue
    name = cells[0][3:].rstrip("`")
    path = find(name)
    if path is None:
        missing.append(name)          # ★測れぬ物は 数へず 名を刷る★
        continue
    n, sha = measure(path)
    old_n, old_sha = cells[1].strip(), cells[2].strip()
    # ★既に合つて居る cell は 一字も触れぬ★（註記＝食ひ違ひの開示 を消さぬ為）
    m_n   = re.search(r"[0-9][0-9,]*", old_n)
    m_sha = re.search(r"[0-9a-f]{16}", old_sha)
    same_n   = m_n   is not None and m_n.group(0).replace(",", "") == str(n)
    same_sha = m_sha is not None and m_sha.group(0) == sha
    if same_n and same_sha:
        continue
    cells[1] = u"★%s★（★器 o138 が打ち直した★／旧 cell %s）" % (format(n, ",d"), old_n)
    cells[2] = u"`%s`（旧 %s）" % (sha, old_sha)
    changed.append((name, old_n, cells[1], old_sha, cells[2]))
    lines[i] = " | ".join(cells)

s = "\n".join(lines)

# ── 紙の和（§1 の表に載る紙のみ・索引は除く＝v50 の理）──
head = s.index("## §1")
tail = s.index("## §2")
names = [l.split(" | ")[0][3:].rstrip("`") for l in s[head:tail].split("\n") if l.startswith("| `")]
tot, rows = 0, []
for nm in names:
    p = find(nm)
    if p is None:
        continue
    n, sha = measure(p)
    tot += n; rows.append((nm, n))
idx_n, idx_sha = measure(IDX)
line = (u"★§1 の和（★v59 以降 器 `o138_index_sum_tool.py` が作る・手で写さぬ★）★: "
        u"紙 ★%d 本★ の和 ★%s 行★ ／ 索引 本紙は ★和に入れぬ★（v50 の理）／ as_of %s\n"
        u"内訳: %s"
        % (len(rows), format(tot, ",d"),
           datetime.datetime.now().strftime("%Y-%m-%d %H:%M JST"),
           " ＋ ".join("%s %d" % (nm.split("_")[0], n) for nm, n in rows)))

MARK = "★§1 の和（"
if MARK in s:
    a = s.index(MARK); b = s.index("\n\n", s.index("内訳:", a))
    s = s[:a] + line + s[b:]
else:
    s = s[:tail] + line + "\n\n" + s[tail:]

print(u"紙 %d 本 ／ 和 %d 行 ／ 索引 本紙 %d 行 (%s)" % (len(rows), tot, idx_n, idx_sha))
print(u"cell を打ち直した行 = %d" % len(changed))
for nm, o1, n1, o2, n2 in changed:
    print(u"  ★据ゑ置きを直した★ %s : %s→%s ／ %s→%s" % (nm, o1, n1, o2, n2))
print(u"表に在るが file が見付からぬ名 = %d %s" % (len(missing), missing[:5]))

if CHECK:
    print(u"★--check ∴ 書かず★")
    sys.exit(1 if changed else 0)
io.open(IDX, "w", encoding="utf-8").write(s)
n2, sha2 = measure(IDX)
print(u"索引を書いた: %d 行 ／ sha16 %s（★書いた事で 索引自身の行数は変る ∴ 和には入れぬ★）" % (n2, sha2))

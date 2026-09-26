# -*- coding: utf-8 -*-
# km-200 REVISE⑤追加（親seq379502）―― 母數17本・除外4・対象13・追加2版・判定表17行の対応を、束内の根拠 file だけから組み直す（読むのみ）。
# 入力: raw/10_bosuu.txt（母數の生出力）と ../README.md（判定表）。出力は stdout。器・DB・箱には触れぬ。
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
bosuu = open(os.path.join(HERE, "10_bosuu.txt"), encoding="utf-8").read()
readme = open(os.path.join(HERE, "..", "README.md"), encoding="utf-8").read()

sec = re.split(r"^## ", bosuu, flags=re.M)
LN = re.compile(r"^(\S+) lines=(\d+) sha256=([0-9a-f]{64})$", re.M)
home = LN.findall(sec[1]); wt = LN.findall(sec[2]); om = LN.findall(sec[3])
print(f"# 母數 file の刻: {bosuu.splitlines()[0]}")
print(f"根 ~/bin の一致 = {len(home)} ・ 稼働木 inbox_write = {len(wt)} ・ origin/main inbox_write = {len(om)}")

JOGAI = {"cc_goal_from_board.py", "inbox_mark_read.py", "km_inbox_read_mark.sh", "orphan_inbox_trap.py"}  # README L21-25
names = [os.path.basename(p) for p, _, _ in home]
jogai = [n for n in names if n in JOGAI]; taisho = [n for n in names if n not in JOGAI]
print(f"除外 = {len(jogai)} ・ 対象 = {len(taisho)} ・ 除外∩対象 = {len(set(jogai) & set(taisho))} ・ 除外のうち母數に無い名 = {sorted(JOGAI - set(names))}")
print(f"追加2版（~/bin の外・母數17 に含まれぬ）: ~/bin の名との重なり = {len({os.path.basename(p) for p,_,_ in wt+om} & set(names))}")

print("\n## 実物一覧（区分 | 名 | path | 版=行数 | sha256）")
for p, l, s in home:
    n = os.path.basename(p)
    print(f"{'除外' if n in JOGAI else '対象'} | {n} | {p} | lines={l} | {s}")
for tag, rows in (("追加・稼働木", wt), ("追加・origin/main b9573b2d", om)):
    for p, l, s in rows:
        print(f"{tag} | inbox_write.sh | {p} | lines={l} | {s}")

# 判定表の行を README から取り、行 → 器（母數の名 or 追加版）へ写す
tbl = [ln for ln in readme.splitlines() if ln.startswith("| ") and not ln.startswith("| 器・路") and not ln.startswith("|---")]
tbl = [ln for ln in tbl if re.match(r"\| [A-Za-z_./-]", ln)]
ROW2KI = {}
for ln in tbl:
    k = ln.split("|")[1].strip()
    if k.startswith("inbox_write.sh 稼働木"): ROW2KI[k] = "追加・稼働木"
    elif k.startswith("inbox_write.sh origin/main"): ROW2KI[k] = "追加・origin/main"
    else: ROW2KI[k] = k.split()[0]
print(f"\n## 判定表 {len(tbl)} 行 → 器")
for k, v in ROW2KI.items():
    print(f"{k} → {v}")
kis = list(ROW2KI.values())
from collections import Counter
c = Counter(kis)
print(f"\n行に出る器の種 = {len(c)} ・ 二行に割れた器 = {sorted(k for k, n in c.items() if n > 1)}")
print(f"対象13 のうち表に行が無い = {sorted(set(taisho) - set(kis))}")
print(f"表の器のうち 対象13∪追加2 の外 = {sorted(set(kis) - set(taisho) - {'追加・稼働木', '追加・origin/main'})}")
print(f"除外4 が表に出る = {sorted(set(jogai) & set(kis))}")
n_home, n_j, n_t, n_add, n_split = len(home), len(jogai), len(taisho), len(wt) + len(om), sum(n - 1 for n in c.values())
print(f"\n## 算: 母數{n_home} − 除外{n_j} = 対象{n_t} ; 対象{n_t} + 追加{n_add} = 器{n_t + n_add} ; 器{n_t + n_add} + 割れ{n_split} = 行{n_t + n_add + n_split} ; 表の実行数 = {len(tbl)}")
ok = (n_home == 17 and n_j == 4 and n_t == 13 and n_add == 2 and n_t + n_add + n_split == len(tbl) == 17
      and not (set(taisho) - set(kis)) and not (set(jogai) & set(kis)))
print("一致" if ok else "★不一致★")
sys.exit(0 if ok else 1)

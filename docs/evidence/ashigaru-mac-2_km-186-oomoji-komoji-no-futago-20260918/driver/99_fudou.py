# -*- coding: utf-8 -*-
"""99 ―― ★共用樹が動いて居らぬ事を證する★(km-185 ㋓ と同じ條・km-186 ★境★)。
30_kyouyou_mae.txt(撃つ前)と突き合はせる。★索引 sha・HEAD・porcelain 行数の三つ★。
"""
import hashlib
import io
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


mae = io.open(os.path.join(BUNDLE, "raw", "30_kyouyou_mae.txt"), encoding="utf-8").read()
mae_head = re.search(r"^([0-9a-f]{40})$", mae, re.M).group(1)
mae_porc = int(re.search(r"porcelain 行数 ---\n(?:.*\n)*?\s*(\d+)\n", mae).group(1))
mae_idx = re.search(r"^([0-9a-f]{64})\s+-$", mae, re.M).group(1)

rc_h, head, _ = g(["rev-parse", "HEAD"])
head = head.decode().strip()
rc_i, idx, _ = g(["ls-files", "-s"])
idx_sha = hashlib.sha256(idx).hexdigest()
rc_p, porc, err_p = g(["status", "--porcelain"])
porc_n = len([l for l in porc.decode("utf-8", "replace").split("\n") if l])
rc_b, eda, _ = g(["rev-parse", "--abbrev-ref", "HEAD"])

ok_h = head == mae_head
ok_i = idx_sha == mae_idx
ok_p = porc_n == mae_porc

K.kaku(os.path.join(BUNDLE, "raw", "99_fudou.txt"), u"""★99 の〆 ―― ★共用樹は動いて居らぬ★★
刻(後) = {koku} ／ 根 = {root} ／ 枝 = {eda}
前の測り = raw/30_kyouyou_mae.txt(刻は其の紙の冠に在る)

| 見る物 | 撃つ前 | 撃つた後 | 判 |
|---|---|---|---|
| HEAD | {mh} | {ah} | {jh} |
| index(`git ls-files -s` の sha256) | {mi} | {ai} | {ji} |
| porcelain 行数 | {mp} | {ap} | {jp} |

rc = HEAD {rch} ／ ls-files {rci} ／ status {rcp}(★管を通さず returncode から取つた★)

★此の間に當席が打つた git の命★:
  ・`git worktree add`(己の場を切るのみ ―― ★共用樹の HEAD も index も動かさぬ★) × ★7 本★
    ―― a2-km186-gyaku / t1 / t2 / t3 / t4 / t5 / a2-km186(★己の物のみ★)
  ・読取(`ls-tree` `cat-file` `show` `ls-files` `status` `ls-remote` `for-each-ref`)
  ・★彫りと消しは悉く己の worktree の中★(50_hori.tsv / 35_gyaku.tsv / 40,41_shiken*.tsv)

★此の數が意味せぬ事★:
  ・porcelain の行数が同じ事は ★中身が同じ事を意味せぬ★(追跡外 dir は一行に畳まれる ―― 中で紙が
    増減しても行数は動かぬ)。★∴ 併せて HEAD と index の sha を書いた。★
  ・當席の束(docs/evidence/…)は `.gitignore:7` の裸 `*` に捕まる ―― ★書いても porcelain は黙る★。
    是は ★書けて居らぬ事を意味せぬ★。
  ・器の言(status err) = {ep}
""".format(koku=time.strftime("%Y-%m-%dT%H:%M:%S%z"), root=ROOT, eda=eda.decode().strip(),
           mh=mae_head, ah=head, jh=u"★不動★" if ok_h else u"★動いた★",
           mi=mae_idx, ai=idx_sha, ji=u"★不動★" if ok_i else u"★動いた★",
           mp=mae_porc, ap=porc_n, jp=u"★不動★" if ok_p else u"★動いた★",
           rch=rc_h, rci=rc_i, rcp=rc_p, ep=err_p.strip().replace("\n", " ⏎ ") or u"―"))
print("HEAD %s / index %s / porcelain %s" % (ok_h, ok_i, ok_p))
assert ok_h and ok_i, "★共用樹が動いた★ HEAD=%s index=%s" % (ok_h, ok_i)

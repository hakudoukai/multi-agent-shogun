# -*- coding: utf-8 -*-
"""20 ―― ★canon の側を歩く★(km-186 ㋒)。
固定 commit 6bde7170… の全 blob を歩き、双子の名を指す語を ★字面の形ごと★ に数へる。
★「大文字を指す物／小文字を指す物」の二分に畳む前に、★実際に現れた形★ を悉く出す★
  ―― 二分は ★.md が付くか否か★ と交はる(ERR-EKARTE-001 は ★error code でもある★)。
"""
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

KOTEI = "6bde7170ce574090a6139ba2dfe3aa4cb6db8634"
KOKU = time.strftime("%Y-%m-%dT%H:%M:%S%z")
SAGASHI = re.compile(r"err-ekarte-001(\.md)?", re.IGNORECASE)


def g(args, raw=True):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


rc_f, out_f, err_f = g(["ls-tree", "-r", "-z", KOTEI])
hon = []
for rec in out_f.split(b"\0"):
    if not rec:
        continue
    atama, _, p = rec.partition(b"\t")
    mode, typ, sha = atama.split()
    hon.append((p.decode("utf-8", "surrogateescape"), sha.decode(), typ.decode()))

kata = {}          # 現れた字面の形 -> 出た回数
kata_file = {}     # 形 -> 其の形を持つ file の集合
gyo = []
yomenu = 0
for path, sha, typ in hon:
    if typ != "blob":
        continue
    rc, out, err = g(["cat-file", "blob", sha])
    if rc != 0:
        yomenu += 1
        continue
    try:
        t = out.decode("utf-8")
    except UnicodeDecodeError:
        continue  # ★二進の紙は歩かぬ(字を数へられぬ)★
    ms = SAGASHI.findall(t)
    if not ms:
        continue
    zen = [m.group(0) for m in SAGASHI.finditer(t)]
    kazu = {}
    for z in zen:
        kata[z] = kata.get(z, 0) + 1
        kata_file.setdefault(z, set()).add(path)
        kazu[z] = kazu.get(z, 0) + 1
    ku = ("CLAUDE.md" if path == "CLAUDE.md" else
          "docs/" if path.startswith("docs/") else
          "instructions/" if path.startswith("instructions/") else
          "scripts/" if path.startswith("scripts/") else "その他")
    gyo.append((ku, path, str(sum(kazu.values())),
                " ／ ".join("%s=%d" % (a, b) for a, b in sorted(kazu.items()))))

gyo.sort()
K.kaku_tsv(os.path.join(BUNDLE, "raw", "20_sasu_file.tsv"), gyo,
           header=("区", "指して居る file", "当りの総数", "字面の形ごとの数"))
kgyo = [(z, str(kata[z]), str(len(kata_file[z])),
         "大文字混じり" if z.lower() != z else "悉く小文字",
         ".md 付き=%s" % str(z.lower().endswith(".md")))
        for z in sorted(kata)]
K.kaku_tsv(os.path.join(BUNDLE, "raw", "20_kata.tsv"), kgyo,
           header=("現れた字面", "出た回数", "其の形を持つ file 数", "大小", "拡張子"))

oo = sum(v for z, v in kata.items() if z.lower().endswith(".md") and z.lower() != z)
ko = sum(v for z, v in kata.items() if z.lower().endswith(".md") and z.lower() == z)
code_oo = sum(v for z, v in kata.items() if not z.lower().endswith(".md") and z.lower() != z)
code_ko = sum(v for z, v in kata.items() if not z.lower().endswith(".md") and z.lower() == z)

K.kaku(os.path.join(BUNDLE, "raw", "20_shime.txt"), u"""★20 の〆 ―― canon は孰れの名を指して居るか★
刻 = {koku} ／ 根 = {root} ／ 固定 = {kotei} ／ rc(ls-tree) = {rcf}
歩いた blob = ★{nb} 本★(固定 commit の全 blob) ／ 当つた file = ★{nf} 本★ ／ 読めぬ blob = {yo} 本
探した形 = 正規 `err-ekarte-001(\\.md)?`(★大小を問はず★)

★㋒ の二分(★.md が付く物だけ★ ―― 是が「file を指して居る」物である)★
  ・大文字混じりの名を指す当り = ★{oo}★
  ・悉く小文字の名を指す当り   = ★{ko}★

★.md の付かぬ当り(★file ではなく error code を指して居る★)★
  ・大文字混じり = {coo} ／ 悉く小文字 = {cko}
  ―― ★之を「file を指す」に混ぜると数が水増しに成る★。故に分けた。

★現れた字面の形(畳まず悉く)★
{kata}

★此の數が意味せぬ事★:
  ・当りは ★固定 commit の中身★ の話であり、★disk の中身ではない★。
  ・「.md 付き」は ★file を指す意図★ の近似である ―― 文の中で code の後に「.md」と書いた例が在れば
    ★此の器は file と読む★。逐語は 20_sasu_file.tsv を見よ。
  ・二進の紙(utf-8 で開けぬ物)は歩いて居らぬ。
  ・器の言(err) = {ef}
""".format(koku=KOKU, root=ROOT, kotei=KOTEI, rcf=rc_f, nb=len(hon), nf=len(gyo), yo=yomenu,
           oo=oo, ko=ko, coo=code_oo, cko=code_ko,
           kata=u"\n".join(u"  ・`%s` = %d 当り(file %d 本)" % (z, kata[z], len(kata_file[z])) for z in sorted(kata)) or u"  ―",
           ef=err_f.strip() or u"―"))
print("blob=%d 当file=%d 大.md=%d 小.md=%d code大=%d code小=%d" % (len(hon), len(gyo), oo, ko, code_oo, code_ko))

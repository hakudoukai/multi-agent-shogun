# -*- coding: utf-8 -*-
u"""10 ―― 其の一(前半) 母數を己の器で数へ直す。
★家老の申された「5file 36箇所」を鵜呑みにせぬ★(下命 ㋐)。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

GREP = "/usr/bin/grep"          # ★shell の grep は ugrep で .gitignore を見る★ ゆゑ名指す
PAT = "-t *[\"']\\{0,1\\}multiagent"
NE = ["scripts", "lib", "shutsujin_departure.sh"]
GONIN = ["scripts/switch_cli.sh", "scripts/watcher_supervisor_third.sh",
         "scripts/agent_status.sh", "scripts/checks/pane_identity.sh",
         "shutsujin_departure.sh"]


def hashiru(argv):
    p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (p.returncode,                                   # ★管を通さず returncode★
            p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


# ⓐ 下命の逐語 ―― `--` の後に --include を置いた形
A = [GREP, "-rn", "--", PAT, "--include=*.sh"] + NE
rc_a, out_a, err_a = hashiru(A)
# ⓑ 正した形 ―― --include を pattern の前へ
B = [GREP, "-rn", "--include=*.sh", "--", PAT] + NE
rc_b, out_b, err_b = hashiru(B)

gyo_a = [l for l in out_a.split("\n") if l]
gyo_b = [l for l in out_b.split("\n") if l]

# file 別(ⓑ)
betsu = {}
for l in gyo_b:
    betsu[l.split(":", 1)[0]] = betsu.get(l.split(":", 1)[0], 0) + 1

# 五人目 ―― 字面の器が 0 を返す file を、別の器で当たる
gonin_ji = {}
gonin_hen = {}
for f in GONIN:
    r1, o1, _ = hashiru([GREP, "-c", "--", PAT, f])
    r2, o2, _ = hashiru([GREP, "-c", "--", '-t *"\\$', f])
    gonin_ji[f] = int(o1.strip() or "0")
    gonin_hen[f] = int(o2.strip() or "0")

K.kaku(os.path.join(BUNDLE, "raw", "10_bosuu.txt"), u"""★其の一(前半) ―― 母數を己の器で数へ直した★
歩き根 = {root}（★共用樹に非ず・己の枝の樹★）／刻 = 下記 raw/00_koku.txt
器 = {grep}（★shell の `grep` は ugrep で .gitignore を見る★ ゆゑ絶対 path で名指した）

■ ⓐ 下命の逐語（`--` の後に `--include`）
  argv = {a}
  rc = ★{rc_a}★ ／ out = {na} 行 ／ err = {ea} 行
  err 逐語 = {erra}
  ★疵★: `--` の後の語は ★悉く file 名★ と読まれる。∴ `--include=*.sh` は ★濾過器として働いて居らぬ★。
        働いたのは「在らぬ file を開かうとして rc=2 を返す」事だけである。

■ ⓑ 正した形（`--include` を pattern の前へ）
  argv = {b}
  rc = ★{rc_b}★ ／ out = {nb} 行 ／ err = {eb} 行

■ ⓐ と ⓑ の出目の差 = ★{sa} 行★
  ―― ∴ 家老の申された ★36★ は ★再現する★。濾過器が死んで居ても、
     scripts/ と lib/ の非 .sh に当たる行は ★元から無かつた★ゆゑ数は動かなんだ。
     ★然れど rc は 0 でなく 2 であつた★ ―― 「数が合ふ」は「器が正しい」を意味せぬ。

■ file 別（ⓑ・母數 {nb}）
{betsu}

■ ★家老は「5 file」と申されたが、此の字面が当たるのは 4 file である★
  五人目 = scripts/agent_status.sh は ★此の字面 0 箇所★。
  ―― 因は「無事」ではない。★-t に ★変数★ を渡して居る★ゆゑ字面の器に映らぬのである。
{gonin}
  ∴ 「0 箇所」は ★危ふくない事を意味せぬ★。(下記「意味せぬ事」を見よ)

★此の數が意味せぬ事★:
  ・36 は ★`-t` の直後に literal で `multiagent` と書いた行★ の数である。
    ★`-t "$session"` の形は一行も入つて居らぬ★ ―― 上表の「変数形」がそれで、5 file 計 {henkei} 行 在る。
    此の形も前方一致し得るが、★危ふさは渡る値に依る★ゆゑ字面では断ぜられぬ。★未測である★。
  ・36 は ★当席の枝(origin/main {oya})の版★ の数である。共用樹の作業中の版では異なり得る。
  ・4 file は「他に無い」ではない ―― 歩いたのは {ne} のみ。
""".format(root=ROOT, grep=GREP, a=" ".join(A), b=" ".join(B),
           rc_a=rc_a, na=len(gyo_a), ea=len([l for l in err_a.split("\n") if l]),
           erra=err_a.strip() or u"―",
           rc_b=rc_b, nb=len(gyo_b), eb=len([l for l in err_b.split("\n") if l]),
           sa=len(set(gyo_a) ^ set(gyo_b)),
           betsu=u"\n".join(u"  {0} = {1} 箇所".format(k, betsu[k]) for k in sorted(betsu)),
           gonin=u"\n".join(u"  {0}\n    字面(-t multiagent) = {1} 箇所 ／ 変数形(-t \"$…\") = {2} 箇所"
                            .format(f, gonin_ji[f], gonin_hen[f]) for f in GONIN),
           henkei=sum(gonin_hen.values()),
           oya="6bde7170ce574090a6139ba2dfe3aa4cb6db8634", ne=" ".join(NE)))

K.kaku(os.path.join(BUNDLE, "raw", "10_zengyo.txt"), u"\n".join(gyo_b))
print("rc_a=%d rc_b=%d a=%d b=%d file=%d henkei=%d"
      % (rc_a, rc_b, len(gyo_a), len(gyo_b), len(betsu), sum(gonin_hen.values())))
assert rc_b == 0, u"★正した器が rc=%d★" % rc_b
assert len(gyo_b) == 36, u"★母數が 36 でなく %d★" % len(gyo_b)
assert set(gyo_a) == set(gyo_b), u"★ⓐとⓑの出目が違ふ★"
assert gonin_ji["scripts/agent_status.sh"] == 0, u"★五人目が 0 でない★"

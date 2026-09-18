# -*- coding: utf-8 -*-
"""32 ―― ★未 push を 0 行で証さぬ★(km-185 ㋖)。
己の枝が遠方に ★無い★ 事(0 行)は、器が黙つただけかも知れぬ。
∴ 同じ器・同じ遠方で ★在る物が 1 行返る★ 事を陽性対照として並べる。
  陽性対照 = refs/heads/main ／ 陰性の的 = 當席の三枝 ／ 負の対照 = 在り得ぬ枝名(器が本当に 0 を返すか)
"""
import io, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402
WT = os.path.expanduser("~/wt")
KI_ICHI = os.path.join(WT, "a2-km171")

EDA = [l.split("\t")[1] for l in
       io.open(os.path.join(KI, "raw", "30_horu.tsv"), encoding="utf-8").read().split("\n")[1:] if l.strip()]
MATO = ([(u"陽性対照", "refs/heads/main")]
        + [(u"己の枝", "refs/heads/" + e) for e in EDA]
        + [(u"負の対照", "refs/heads/ashigaru-mac-2/kore-wa-arienu-eda-20260918")])

rows = []
for yaku, ref in MATO:
    p = subprocess.run(["git", "-C", KI_ICHI, "ls-remote", "origin", ref],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o = p.stdout.decode("utf-8", "replace")
    gyou = [l for l in o.split("\n") if l.strip()]
    rows.append((yaku, ref, p.returncode, len(gyou), K.esc(gyou[0]) if gyou else u"―"))
    print(u"%-8s %-60s rc=%d 行=%d" % (yaku, ref, p.returncode, len(gyou)))
K.kaku_tsv(os.path.join(KI, "raw", "32_mipush.tsv"), rows,
           header=("yaku", "ref", "rc", "gyou", "chikugo"))
K.kaku(os.path.join(KI, "raw", "32_shime.txt"), u"""★未 push の證★ 刻 = {t}
器 = git -C ~/wt/a2-km171 ls-remote origin <ref>(同じ器・同じ遠方で三役を当てた)
  ⑴陽性対照 refs/heads/main      = ★1 行★ ―― 器は生きて居り、遠方は引ける
  ⑵己の三枝                      = ★悉く 0 行★ ―― 遠方に無い(= push して居らぬ)
  ⑶負の対照 在り得ぬ枝名          = ★0 行★ ―― 器は「無い物」に 0 を返すと確かめた
★此の三つを並べねば 0 は證に成らぬ★(0 対 0 は器の沈黙と區別が付かぬ)。
★此の數が意味せぬ事★: ★今 遠方に無い★ の意であり、★誰かが後で push せぬ事を意味せぬ★。
逐語 = raw/32_mipush.tsv
""".format(t=time.strftime("%Y-%m-%dT%H:%M:%S%z")))
you = [r for r in rows if r[0] == u"陽性対照"][0]
ono = [r for r in rows if r[0] == u"己の枝"]
fu = [r for r in rows if r[0] == u"負の対照"][0]
assert you[3] == 1, u"★陽性対照が %d 行 ―― 器か遠方が死んで居る★" % you[3]
assert all(r[3] == 0 for r in ono), u"★己の枝が遠方に在る★"
assert fu[3] == 0, u"★負の対照が 0 行でない★"
print(u"★陽性=%d行 己の枝=%s 負=%d行★" % (you[3], u"/".join(str(r[3]) for r in ono), fu[3]))

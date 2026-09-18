# -*- coding: utf-8 -*-
"""30 ―― ★己の樹で彫る★(km-185 ㋔)。`git add -f <path>` の後 `git commit --only <同じ path>`。
★reset を打たぬ・push せぬ・main に触れぬ・gh を叩かぬ★(裁332449)。
★add -f が要る譯★: .gitignore の 7 行目が ★裸の `*`★(allowlist 式)ゆゑ docs/evidence は悉く落ちる。
  陽性対照=束の 00_shodan.md が check-ignore rc=0 / 陰性対照=CLAUDE.md が rc=1 を ★二つ並べて★ 採る
  (片方だけでは器が黙つただけかも知れぬ)。
★未 push の證は 0 行では立たぬ★ ∴ ls-remote origin refs/heads/main が 1 行返る事を陽性対照に採る。
"""
import io, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(KI, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

KYOU = u"""
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"""

DAN = [
    ("a2-km171", u"evidence(km-171): ★受入の地面を三束で固定 ―― 403か404か／404へ／問への答★ ―― 専任2(裁332455・333060③)",
     ["docs/evidence/ashigaru-mac-2_km-171-ukeire-to-genbutsu-no-sa-wo-hakaru-403-ka-404-ka-20260918",
      "docs/evidence/ashigaru-mac-2_km-171-uke-ire-no-jimen-wo-404-he-20260918",
      "docs/evidence/ashigaru-mac-2_km-171-toi-heno-kotae-20260918"]),
    ("a2-km172", u"evidence(km-172): ★箱の写しで fail-open を実証した束を固定★ ―― 専任2(裁332455・333060③)",
     ["docs/evidence/ashigaru-mac-2_km-172-hako-no-utsushi-de-fail-open-wo-jissho-suru-20260918"]),
    ("a2-km174", u"evidence(km-174): ★大人版 認定済予約 入口一往復の束を固定★ ―― 専任2(裁332455・333060③)",
     ["docs/evidence/ashigaru-mac-2_km-174-otona-ban-yoyaku-iriguchi-ichi-oufuku-20260918"]),
]
WT = os.path.expanduser("~/wt")


def g(w, *a):
    p = subprocess.run(["git", "-C", os.path.join(WT, w)] + list(a),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


rows, ki = [], []
for w, msg, paths in DAN:
    rc_b, eda, _ = g(w, "rev-parse", "--abbrev-ref", "HEAD")
    rc_m, mae, _ = g(w, "rev-parse", "HEAD")
    # ★対照 二つ★ ―― 陽性=束の紙が ignore に落ちる / 陰性=CLAUDE.md は落ちぬ
    you = os.path.join(paths[0], "00_shodan.md")
    rc_you, o_you, _ = g(w, "check-ignore", "-v", "--", you)
    rc_in, o_in, _ = g(w, "check-ignore", "-v", "--", "CLAUDE.md")
    rc_a, _, e_a = g(w, "add", "-f", "--", *paths)
    rc_c, o_c, e_c = g(w, "commit", "--only", "-m", msg + KYOU, "--", *paths)
    rc_s, sha, _ = g(w, "rev-parse", "HEAD")
    rc_t, tree, _ = g(w, "rev-parse", "HEAD^{tree}")
    rc_n, names, _ = g(w, "diff-tree", "--no-commit-id", "-r", "--name-only", sha.strip())
    rc_st, stat, _ = g(w, "diff", "--shortstat", mae.strip(), sha.strip())
    rc_lr, lr, _ = g(w, "ls-remote", "origin", "refs/heads/main")
    rc_ch, ahead, _ = g(w, "rev-list", "--count", "origin/main.." + sha.strip())
    hon = len([l for l in names.split("\n") if l])
    rows.append((w, eda.strip(), mae.strip(), sha.strip(), tree.strip(), hon,
                 K.esc(stat.strip()), rc_a, rc_c))
    ki.append(u"""[{w}] 枝 = {e}
  親(切り元) = {mae}
  ★固定 commit(40桁) = {sha}★
  ★tree(40桁)       = {tr}★
  ★此の commit が持つ file = {hon} 本★(diff-tree --name-only の行数・rc={rcn})
  増減 = {st}  (git diff --shortstat 親..子・rc={rcst})
  add -f rc={rca} / commit --only rc={rcc}
  ignore 対照 ⑴陽性: {you} → rc={rcy} 逐語「{oy}」
             ⑵陰性: CLAUDE.md → rc={rci} 逐語「{oi}」
    ―― ★rc=0 が『落ちる』・rc=1 が『落ちぬ』。二つ並べねば器の沈黙と區別が付かぬ。★
  ★未 push の證★: origin/main..{sha8} の commit 数 = ★{ah}★(rc={rcch})
    陽性対照 = git ls-remote origin refs/heads/main の行数 = ★{lrn}★(rc={rclr})
    ―― ★0 対 0 は器が黙つただけかも知れぬ ∴ 遠方が引ける事を先に示した。★
""".format(w=w, e=eda.strip(), mae=mae.strip(), sha=sha.strip(), tr=tree.strip(), hon=hon,
           rcn=rc_n, st=K.esc(stat.strip()) or u"―", rcst=rc_st, rca=rc_a, rcc=rc_c,
           you=you, rcy=rc_you, oy=K.esc(o_you.strip()) or u"―", rci=rc_in,
           oi=K.esc(o_in.strip()) or u"―(何も刷らぬ=落ちぬ)", sha8=sha.strip()[:8],
           ah=ahead.strip(), rcch=rc_ch, lrn=len([l for l in lr.split("\n") if l]), rclr=rc_lr))
    print(u"%s rc(add)=%d rc(commit)=%d sha=%s file=%d" % (w, rc_a, rc_c, sha.strip()[:8], hon))
    assert rc_a == 0 and rc_c == 0, u"★%s 彫りが落ちた: %s / %s★" % (w, e_a, e_c)
    assert rc_you == 0 and rc_in == 1, u"★ignore の対照が立たぬ(陽性rc=%d 陰性rc=%d)★" % (rc_you, rc_in)

K.kaku_tsv(os.path.join(KI, "raw", "30_horu.tsv"), rows,
           header=("ki", "eda", "oya_sha", "kotei_sha", "tree", "file_hon", "zougen", "rc_add", "rc_commit"))
K.kaku(os.path.join(KI, "raw", "30_shime.txt"),
       u"★彫りの〆★ 刻 = %s\n\n%s\n★此の數が意味せぬ事★:\n"
       u"  ・file 本数は ★此の commit が持つ紙★ であり、束の disk の紙数と ★一致せぬ事が在る★\n"
       u"    (臺帳は __pycache__ を除く方言・彫りは disk を其の儘持つ)。差は 40 が名指す。\n"
       u"  ・未 push の 0 は ★遠方に無い★ の意であり、★誰かが後で push せぬ事を意味せぬ★。\n"
       % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), u"\n".join(ki)))

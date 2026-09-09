# -*- coding: utf-8 -*-
u"""E12: 直す前の姿(git blob)と 今の姿(作業樹)を 前後併記する。
讀取のみ(git show / status)・的の樹へ一字も書かぬ・製品走 0・DB 0。
「直す前」の定め = ★commit 47c8bc3b の blob★（刻でも版でもなく ★commit★ で定める）。
"""
import io, os, sys, hashlib, subprocess

TREE = "/home/hakudoukai/a3/wt-bundle-fix4"
PIN = "47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b"
HERE = os.path.dirname(os.path.abspath(__file__))

def git(args):
    pr = subprocess.run(["git", "-C", TREE] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pr.returncode, pr.stdout, pr.stderr

def units(text):
    sk = 0; sf = 0; ci = 0
    for ln in text.split(chr(10)):
        t = ln.lstrip()
        if t.startswith("@pytest.mark.skipif("):
            sf += 1
        elif t.startswith("@pytest.mark.skip("):
            sk += 1
        if "collect_ignore" in ln and "=" in ln:
            ci += 1
    return sk, sf, ci

out = []
def w(x):
    out.append(x)

rc, so, se = git(["rev-parse", "HEAD"])
head_now = so.decode("utf-8").strip()
w(u"## §A 的の樹と pin")
w(u"TREE=" + TREE)
w(u"HEAD_now=" + head_now + u"  PIN=" + PIN + u"  同じ=" + str(head_now == PIN))
rc, so, se = git(["status", "--porcelain"])
plines = [x for x in so.decode("utf-8").split(chr(10)) if x.strip()]
w(u"porcelain_rc=" + str(rc) + u"  porcelain_lines=" + str(len(plines)))
w(u"")

w(u"## §B porcelain の 6 行（状態符 と path）")
targets = []
for ln in plines:
    code = ln[:2]; rel = ln[3:].strip()
    if rel.startswith('"') and rel.endswith('"'):
        rel = rel[1:-1]
    w(u"  code=" + repr(code) + u"  path=" + rel)
    targets.append((code, rel))
w(u"")

w(u"## §C 前（blob@47c8bc3b）と 今（作業樹）の併記")
w(u"| # | path | 前 読めた | 前 sha256 | 前 wc/split | 前 skip/skipif/ci | 今 読めた | 今 sha256 | 今 wc/split | 今 skip/skipif/ci | CRLF |")
n_prev_ok = 0; n_prev_ng = 0; n_now_ok = 0; n_now_ng = 0
sum_prev = [0, 0, 0]; sum_now = [0, 0, 0]
rows = []
for i, (code, rel) in enumerate(targets, 1):
    rc2, blob, err = git(["show", PIN + ":" + rel])
    if rc2 == 0:
        n_prev_ok += 1
        pv_sha = hashlib.sha256(blob).hexdigest()
        pv_txt = blob.decode("utf-8", "replace")
        pv_wc = blob.count(b"\n"); pv_sp = len(pv_txt.split(chr(10)))
        a, b, c = units(pv_txt)
        sum_prev[0] += a; sum_prev[1] += b; sum_prev[2] += c
        pv = (u"現に在る", pv_sha, str(pv_wc) + u"/" + str(pv_sp), str(a) + u"/" + str(b) + u"/" + str(c))
    else:
        n_prev_ng += 1
        pv = (u"現に無い(rc=" + str(rc2) + u")", u"-", u"-", u"-")
    ap = os.path.join(TREE, rel)
    if os.path.isfile(ap):
        raw = io.open(ap, "rb").read()
        n_now_ok += 1
        nw_sha = hashlib.sha256(raw).hexdigest()
        nw_txt = raw.decode("utf-8", "replace")
        nw_wc = raw.count(b"\n"); nw_sp = len(nw_txt.split(chr(10)))
        a2, b2, c2 = units(nw_txt)
        sum_now[0] += a2; sum_now[1] += b2; sum_now[2] += c2
        crlf = str(raw.count(b"\r\n"))
        nw = (u"現に在る", nw_sha, str(nw_wc) + u"/" + str(nw_sp), str(a2) + u"/" + str(b2) + u"/" + str(c2), crlf)
    else:
        n_now_ng += 1
        nw = (u"現に無い", u"-", u"-", u"-", u"-")
    w(u"| " + str(i) + u" | " + rel + u" | " + pv[0] + u" | " + pv[1][:16] + u" | " + pv[2] + u" | " + pv[3] + u" | " + nw[0] + u" | " + nw[1][:16] + u" | " + nw[2] + u" | " + nw[3] + u" | " + nw[4] + u" |")
    rows.append((rel, pv, nw))
w(u"")

w(u"## §D 別値（令③: 現に読める物と読めぬ物を別値で）")
w(u"porcelain 母数=" + str(len(targets)))
w(u"前(blob) 読めた=" + str(n_prev_ok) + u"  読めなんだ=" + str(n_prev_ng))
w(u"今(作業樹) 読めた=" + str(n_now_ok) + u"  読めなんだ=" + str(n_now_ng))
w(u"")

w(u"## §E 単位の和（★本弾の母 = porcelain の 6 枚のみ★・464 枚の母とは別）")
w(u"前: skip=" + str(sum_prev[0]) + u"  skipif=" + str(sum_prev[1]) + u"  collect_ignore=" + str(sum_prev[2]))
w(u"今: skip=" + str(sum_now[0]) + u"  skipif=" + str(sum_now[1]) + u"  collect_ignore=" + str(sum_now[2]))
w(u"差: skip=" + str(sum_now[0] - sum_prev[0]) + u"  skipif=" + str(sum_now[1] - sum_prev[1]) + u"  collect_ignore=" + str(sum_now[2] - sum_prev[2]))
w(u"")

w(u"## §F 負の対照（差が出得る口・器が同じ物を返す形ではない事）")
same_sha = 0
for rel, pv, nw in rows:
    if pv[1] != u"-" and nw[1] != u"-" and pv[1] == nw[1]:
        same_sha += 1
w(u"前後の sha が ★同じ★ 枚数=" + str(same_sha) + u"  ★別★ 枚数=" + str(sum(1 for r, pv, nw in rows if pv[1] != u"-" and nw[1] != u"-" and pv[1] != nw[1])))
rc3, so3, se3 = git(["show", PIN + ":no_such_file_for_negative_control_o221"])
w(u"存在せぬ path を show した時の rc=" + str(rc3) + u"（0 でない事が『読めぬ』を判ずる口の証）")
w(u"")

w(u"## §G 測れぬ物（令②）")
w(u"- o193 が言ふ『24 単位 / 12 単位』は ★母集団 464 枚★ から数へた数 ∴ 本弾（母 = porcelain の枚数）では ★再現せぬ★＝別の母。")
w(u"- porcelain に挙がらぬ file の前後は 本弾では ★測定不能★（網は porcelain の行のみ）。")
w(u"- 『覆ふ試験本数』は 走らねば定まらぬ ∴ 本弾では ★測定不能★（製品走 0）。")

txt = chr(10).join(out) + chr(10)
raw_path = os.path.join(HERE, "order221_e12_before_blob.raw.txt")
io.open(raw_path, "w", encoding="utf-8").write(txt)
sys.stdout.write(txt)

# -*- coding: utf-8 -*-
"""★B1 を素で採り直す★(家老令 km-175 ㋑ + 補正 hosei_175_b1_push_zumi ㋑㋒)
家老は「未push」の判を ★rc を pipe 越しに採つた★ 物と自ら申し、素で採り直せと命じた。
∴ 本器は ★一切 pipe を通さぬ★ ―― subprocess.run の returncode を其の儘採り、出目は kaki で書く。
測るのは二つの ref が ★別物である事★ と、其の現物の寸法・blob・sha256 である。
四札: 刻=各紙の冠 / 根=repo を毎行名指す / rc=returncode(★管を通さぬ★) / 対照=在らぬ sha と在らぬ枝(下記 陰性)。"""
import os
import sys
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

DENTAL = "/Users/momizimac/DentalBI"
SHOGUN = ROOT
B1_TIP = "7a99e7556c3839293e6525671c042cb19e2c1ebe"
B1_EDA = "a2/b1-episodes-playback-20260910"
B5_TIP = "b5892684f"
B5_EDA = "a2/b1-story-engine-parity-20260910"
GEN = "frontend/src/features/child-passport/story-engine/__tests__/episodes.playback.test.tsx"
KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def g(repo, args, tmo=120):
    """★git を素で走らす ―― pipe を通さぬ★。戻りは (rc, stdout, stderr)。"""
    p = subprocess.run(["git", "-C", repo] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=tmo)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def gb(repo, args, tmo=120):
    """★bytes で採る(sha256 を採る為・text 化で壊さぬ)★"""
    p = subprocess.run(["git", "-C", repo] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=tmo)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


gyou = []   # 表の行
nama = {}   # 生の出目(kaki で書く)


def toru(na, repo, args, imi=""):
    rc, out, err = g(repo, args)
    nama[na] = "$ git -C %s %s\nrc=%d\n--- stdout\n%s\n--- stderr\n%s" % (repo, " ".join(args), rc, out, err)
    gyou.append([na, os.path.basename(repo), " ".join(args)[:58], rc,
                 (out.strip().split("\n")[0][:64] if out.strip() else "-"),
                 (err.strip().split("\n")[0][:48] if err.strip() else "-"), imi or "-"])
    return rc, out, err


# ―― ⑴ 樹を名指す(家老補正の核: repo を違へると不在の證に成らぬ) ――
toru("10_dental_toplevel", DENTAL, ["rev-parse", "--show-toplevel"], "現物の樹")
toru("11_dental_origin", DENTAL, ["remote", "get-url", "origin"], "押し先")
toru("12_shogun_b1_eda", SHOGUN, ["rev-parse", "--verify", B1_EDA], "★当repo には無い筈(rc≠0 が正)★")
toru("13_dental_b1_eda", DENTAL, ["rev-parse", "--verify", B1_EDA], "★DentalBI に在る筈(rc=0 が正)★")

# ―― ⑵ 二つの ref を別物として採る ――
rc_t, out_t, _ = toru("20_b1_tip", DENTAL, ["rev-parse", "--verify", B1_TIP + "^{commit}"], "B1 の tip")
rc_c, out_c, _ = toru("21_b1_commit", DENTAL, ["cat-file", "commit", B1_TIP], "tree/parent/刻 の源")
toru("22_b1_numstat", DENTAL, ["show", "--numstat", "--format=%H%n%T%n%P%n%ad", B1_TIP], "1 file +117 の検め")
rc_b5, out_b5, _ = toru("30_b5_tip", DENTAL, ["rev-parse", "--verify", B5_TIP + "^{commit}"], "別物の tip")
toru("31_b5_numstat", DENTAL, ["show", "--numstat", "--format=%H%n%T%n%P%n%ad", B5_TIP], "★別の現物(182行)★")

# ―― ⑶ 現物の寸法・blob・sha256(中身) ――
rc_ls, out_ls, _ = toru("40_b1_lstree", DENTAL, ["ls-tree", B1_TIP, GEN], "blob と mode")
blob = out_ls.split()[2] if rc_ls == 0 and len(out_ls.split()) >= 3 else "-"
sha256 = "-"; byte = "-"; gyou_n = "-"
if blob != "-":
    rc_sz, out_sz, _ = toru("41_b1_blob_size", DENTAL, ["cat-file", "-s", blob], "byte 数(git の言)")
    byte = out_sz.strip() if rc_sz == 0 else "-"
    rc_bl, raw, err_bl = gb(DENTAL, ["cat-file", "blob", blob])
    nama["42_b1_blob_atama"] = ("$ git -C %s cat-file blob %s\nrc=%d\n寸法=%d byte\n--- 頭 12 行\n%s"
                               % (DENTAL, blob, rc_bl, len(raw),
                                  "\n".join(raw.decode("utf-8", "replace").split("\n")[:12])))
    if rc_bl == 0:
        sha256 = hashlib.sha256(raw).hexdigest()
        gyou_n = str(raw.decode("utf-8", "replace").count("\n"))
        gyou.append(["42_b1_blob", "DentalBI", "cat-file blob %s" % blob[:12], rc_bl,
                     "%d byte / 改行 %s 個" % (len(raw), gyou_n), "-", "★中身を己の手で量つた★"])

# ―― ⑷ 押し済か(ls-remote ―― 網を通す・rc は素で採る) ――
rc_r, out_r, err_r = toru("50_ls_remote_heads", DENTAL, ["ls-remote", "--heads", "origin"], "母數と着弾の源", )
refs = [l for l in out_r.split("\n") if l.strip()]
atari_b1 = [l for l in refs if l.endswith("refs/heads/" + B1_EDA)]
atari_b5 = [l for l in refs if l.endswith("refs/heads/" + B5_EDA)]
NAI_EDA = "a2/b1-arienu-eda-98765432-negative-control"
atari_nai = [l for l in refs if l.endswith("refs/heads/" + NAI_EDA)]
rc_m, out_m, _ = toru("51_main_oite_no_tsuiseki", DENTAL, ["rev-parse", "--verify", "origin/main"],
                      "★手元の追跡ref ―― 網の實ではない★")
AMI_MAIN = [l.split("\t")[0] for l in refs if l.endswith("\trefs/heads/main")]
ami_main = AMI_MAIN[0] if len(AMI_MAIN) == 1 else "-"
gyou.append(["52_main_ami", "origin(網)", "ls-remote の refs/heads/main 行", rc_r, ami_main[:64], "-",
             "★main の實は此れ ―― 家老の申した 088961e1 と比べる★"])
# ―― 二つが食ひ違ふなら、何方が先かを rc で決める(推さぬ) ――
oyako = "-"
if ami_main != "-" and out_m.strip() and ami_main != out_m.strip():
    rc_a1, _, _ = toru("53_ami_wa_tsuiseki_no_oya", DENTAL,
                       ["merge-base", "--is-ancestor", ami_main, out_m.strip()],
                       "rc=0 なら 網 main は 追跡ref の祖")
    rc_a2, _, _ = toru("54_tsuiseki_wa_ami_no_oya", DENTAL,
                       ["merge-base", "--is-ancestor", out_m.strip(), ami_main],
                       "rc=0 なら 追跡ref は 網 main の祖")
    oyako = ("★追跡ref が網より先(手元が進んで居る ―― 網には未だ無い)★" if rc_a1 == 0 and rc_a2 != 0
             else ("★網が追跡refより先(手元が古い)★" if rc_a2 == 0 and rc_a1 != 0
                   else "★親子に非ず(枝が分かれて居る)★"))

# ―― ⑸ 陰性対照 ―― 在らぬ sha / 在らぬ枝 ――
toru("60_taishou_arienu_sha", DENTAL, ["rev-parse", "--verify", "9876543298765432987654329876543298765432^{commit}"],
     "★陰性対照 ―― rc≠0 が正★")
toru("61_taishou_arienu_eda", DENTAL, ["rev-parse", "--verify", NAI_EDA], "★陰性対照 ―― rc≠0 が正★")

for na, body in nama.items():
    kaku(os.path.join(BUNDLE, "raw", "2%s.txt" % na), "刻=%s\n%s" % (KOKU, body))
kaku_tsv(os.path.join(BUNDLE, "raw", "20_b1_sunao_no_hakari.tsv"), gyou,
         header=["名", "樹", "git の言(58字で截つ)", "rc", "出目の初行(64字で截つ)", "err の初行(48字で截つ)", "意"])

# ―― 断 ――
kom = dict(l.split(" ", 1) for l in out_c.strip().split("\n") if " " in l and not l.startswith("    ")) if rc_c == 0 else {}
kaku(os.path.join(BUNDLE, "raw", "29_b1_dan.txt"),
     "刻=%s\n根=%s(★樹を名指す ―― 当repo で探して『無い』を得ても不在の證に成らぬ★)\n\n"
     "【二つの ref は別物である】\n"
     "⑴ B1 の本体 ―― 枝=%s / tip=%s / rc(rev-parse)=%d\n"
     "   tree=%s / parent=%s\n"
     "   現物=%s\n"
     "   blob=%s / %s byte / 改行 %s 個 / sha256(中身)=%s\n"
     "⑵ 別物 ―― 枝=%s / tip(短)=%s / rc=%d ―― 加へたのは schema-types-parity.test.ts(raw/231_b5_numstat)\n\n"
     "【押し済か(ls-remote・rc は管を通さず採つた)】\n"
     "・rc=%d / 母數=%d 本\n"
     "・B1 の枝に当たる行=%d 本%s\n"
     "・別物の枝に当たる行=%d 本\n"
     "・★陰性対照★ 在らぬ枝 %s に当たる行=%d 本(0 が正)\n"
     "・★main の實(網の出目)=%s ―― 家老の申した 088961e1… と%s★\n"
     "・手元の追跡ref origin/main=%s(rc=%d) ―― ★網の實と%s★%s\n\n"
     "【之が意味せぬ事】\n"
     "・ls-remote が当たつた事は ★中身が上に在る事★ の證ではない(ref の先の obj を fetch して居らぬ)。\n"
     "・寸法や行数の一致は ★同一の證に成らぬ★(km-175 ㋒ で家老が 1401 byte の別物に当たつた通り)。\n"
     "・當席は押して居らぬ ―― 押したのは委員長(裁 seq332324)であり、本紙は ★着弾を検めた紙★ である。\n"
     % (KOKU, DENTAL, B1_EDA, B1_TIP, rc_t, kom.get("tree", "-"), kom.get("parent", "-"),
        GEN, blob, byte, gyou_n, sha256,
        B5_EDA, B5_TIP, rc_b5,
        rc_r, len(refs), len(atari_b1), ("\n  逐語= " + atari_b1[0] if atari_b1 else ""), len(atari_b5),
        NAI_EDA, len(atari_nai),
        ami_main, ("★合ふ★" if ami_main.startswith("088961e1") else "★合はぬ★"),
        out_m.strip() or "-", rc_m,
        ("同じ" if ami_main == out_m.strip() else "★食ひ違ふ★"),
        ("" if ami_main == out_m.strip() else "\n  ―― 何方が先か= " + oyako)))
print("B1 を素で採つた ―― 行 %d / tip rc=%d / b5 rc=%d / ls-remote rc=%d 母數 %d" % (len(gyou), rc_t, rc_b5, rc_r, len(refs)))
print("  blob=%s %s byte 改行 %s sha256=%s" % (blob, byte, gyou_n, sha256[:16]))
print("  B1 当たり %d / 別物 当たり %d / 陰性 %d" % (len(atari_b1), len(atari_b5), len(atari_nai)))
print("  main 網=%s / 追跡ref=%s ―― %s" % (ami_main[:12], out_m.strip()[:12],
      "同じ" if ami_main == out_m.strip() else "★食ひ違ふ(" + oyako + ")★"))

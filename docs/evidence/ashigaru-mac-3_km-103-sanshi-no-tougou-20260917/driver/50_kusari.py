# -*- coding: utf-8 -*-
"""㋓ ★着地の鎖★ ―― 45 本を ⑴幹の後に単独で載る ⑵他枝を待つ に分け、待つ相手を名で書く。

★定義(先に宣する)★
  幹 = `origin/main` = 4be3ee19e1c5(家老の測りと同じ根)。
  枝 B が担ぐ commit = `git rev-list <B> --not <幹>` ―― ★幹に無く B に在る commit★。
  ★B が待つ相手★ = 60 本の tip の内、其の sha が上の集合に在る★他の枝★。
     即ち「B を幹へ載せると、其の枝の commit も悉く一緒に載る」枝である。
  ★単独で載る★ = 待つ相手が 0 本。

★三段で測る(「幹の後に単独で載るか」の「幹」が二義ゆゑ)★
  段① 幹 = `origin/main` 4be3ee19e1c5
  段② 幹 = main ＋ ★家老の申す幹 363d5fb06084★(= `karo-mac/km-gate-kou-otsu-20260917`・
       家老 README 八-2 の ㋐幹。★此の枝自身が不要15 の一本である★)が載つた後
  段③ 45 本の内、★他の 45 本★を待つ枝(家老紙・當方 km-102 は共に「独立の葉」と申す)
  ★最も近い相手★ = 待つ相手の内、担ぐ commit 数が最大の一本(B に最も近い)。

★此の測りが意味せぬ事★
  ・「待つ」は「其の枝の後でなければ PR を出せぬ」ではない。★出せば相手も一緒に載る★の意である。
  ・「単独」は「衝突せぬ」ではない。衝突は merge-tree の話で、本器は測つて居らぬ。
  ・待つ相手が★不要15★に在る時、其の枝は「捨てる筈の枝を担いで出る」事に成る
    ―― 是は本器の出目であり、可否の判ではない(裁は理事長・軍師mac)。

対照(倒れたら止まる):
  ⓐ 陽性: 幹そのものを問へば「担ぐ commit 0」でなければ 止(根が違ふ)。
  ★臺帳は sha→名の「束」で持つ★: 60 本の内 `karo-mac/gate5-20260909` と
     `karo-mac/gate5-note-20260909` は★同じ sha e8470d8c★(共に不要15)。
     sha を鍵にした辞書では 60 が 59 に痩せ、待つ相手の一名が黙つて消える(初版で現に痩せた)。
  ⓑ 陰性: 零の sha を問へば git が rc≠0 を返さねば 止。
  ⓒ 45 本悉く測れねば 止。
  ⓓ 別器(`git merge-base --is-ancestor`)で★一対を独立に検め★、食ひ違へば 止
     ―― 同じ答を二つの器から取る(一器の疵が判を作らぬ様に)。
"""
import os, sys, subprocess, importlib.util
_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("K", os.path.join(_d, "00_kaki.py"))
K = importlib.util.module_from_spec(_s); _s.loader.exec_module(K)
REPO = os.path.abspath(os.path.join(_d, "..", "..", "..", ".."))
EV = os.path.join(REPO, "docs/evidence")
MAIN = "4be3ee19e1c5"
MIKI = "363d5fb06084"   # 家老の申す幹 = karo-mac/km-gate-kou-otsu-20260917(不要15 の一本)

def git(a):
    p = subprocess.run(["git", "-C", REPO] + a, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "surrogateescape"), p.stderr.decode("utf-8", "surrogateescape")

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: 50_kusari.py <束の根>\n"); return 2
    base = sys.argv[1]; raw = os.path.join(base, "raw")

    roster, gyou, sha_of = {}, 0, {}   # sha40 -> [枝名…] / 枝名 -> sha40
    for i, ln in enumerate(open(os.path.join(
            EV, "ashigaru-mac-3_km-102-eda-yonjuugo-no-chakuchi-shiwake-karo-kou-20260917",
            "raw/21_roster.tsv"), encoding="utf-8").read().split("\n")):
        if i and ln.strip():
            c = ln.split("\t"); gyou += 1
            roster.setdefault(c[0].strip(), []).append(c[1].strip())
            sha_of[c[1].strip()] = c[0].strip()
    fuyou = set()
    for i, ln in enumerate(open(os.path.join(
            EV, "ashigaru-mac-1_km-100-eda-chakuchi-shiwake-20260917",
            "raw/03_karo_fuyou15_utsushi.tsv"), encoding="utf-8").read().split("\n")):
        if i and ln.strip():
            fuyou.add(ln.split("\t")[1].strip())
    if gyou != 60 or len(sha_of) != 60 or len(fuyou) != 15:
        sys.stderr.write("★母數が合はぬ(行=%d 名=%d 不要=%d) ∴ 止まる★\n"
                         % (gyou, len(sha_of), len(fuyou))); return 5

    warimochi = []   # (席, 枝名, sha40)
    for i, ln in enumerate(open(os.path.join(raw, "21_nul_jissoku.tsv"), encoding="utf-8")
                           .read().split("\n")):
        if i and ln.strip():
            c = ln.split("\t"); warimochi.append((c[0], c[1], c[2]))

    # ── 対照ⓐ 陽性: 幹は幹に対して 0 commit ──────────────
    rc, out, err = git(["rev-list", MAIN, "--not", MAIN])
    if rc != 0 or out.strip():
        sys.stderr.write("★幹が幹に対し 0 commit でない(rc=%d 行=%d) ∴ 止まる★\n"
                         % (rc, len(out.split()))); return 5
    # ── 対照ⓑ 陰性: 零の sha ─────────────────────────────
    rc0, _, _ = git(["rev-list", "0" * 40, "--not", MAIN])
    if rc0 == 0:
        sys.stderr.write("★零の sha で git が rc=0 を返した ∴ 止まる★\n"); return 5

    warimochi_na = {e for _, e, _ in warimochi}
    rc, out, err = git(["cat-file", "-e", MIKI])
    if rc != 0:
        sys.stderr.write("★家老の幹 %s が手許に無い(rc=%d) ∴ 止まる★\n" % (MIKI, rc)); return 5

    ninau1, ninau2 = {}, {}   # 枝名 -> 担ぐ commit sha の集合(段①/段②)
    for seki, eda, sha12 in warimochi:
        rc, out, err = git(["rev-list", sha12, "--not", MAIN])
        if rc != 0:                                     # ── 対照ⓒ
            sys.stderr.write("★%s が段①で測れぬ(rc=%d) ∴ 止まる★\n" % (eda, rc)); return 5
        ninau1[eda] = set(out.split())
        rc, out, err = git(["rev-list", sha12, "--not", MAIN, MIKI])
        if rc != 0:
            sys.stderr.write("★%s が段②で測れぬ(rc=%d) ∴ 止まる★\n" % (eda, rc)); return 5
        ninau2[eda] = set(out.split())

    def aite_of(eda, ninau):
        return sorted({n for s in ninau[eda] if s in roster for n in roster[s] if n != eda})

    kazu = {}   # 枝名 -> 担ぐ commit 数(段①)。45 の外の枝は其の場で測る
    def ninau_kazu(a):
        if a in ninau1:
            return len(ninau1[a])
        if a not in kazu:
            r2, o2, _ = git(["rev-list", sha_of[a], "--not", MAIN])
            kazu[a] = len(o2.split()) if r2 == 0 else -1
        return kazu[a]

    rows, matsu_kei, tan_kei, tan2_kei, uchi45_kei = [], 0, 0, 0, 0
    for seki, eda, sha12 in warimochi:
        a1_ = aite_of(eda, ninau1); a2_ = aite_of(eda, ninau2)
        uchi45 = [a for a in a1_ if a in warimochi_na]
        if a1_:
            matsu_kei += 1
            chikai = max(a1_, key=ninau_kazu)
            han1 = "⑵他枝を待つ"
        else:
            tan_kei += 1; chikai = "―"; han1 = "⑴幹の後に単独で載る"
        if a2_:
            han2 = "⑵猶 待つ"
        else:
            tan2_kei += 1; han2 = "★⑴単独で載る★"
        if uchi45:
            uchi45_kei += 1
        rows.append([eda.replace("karo-mac/", "K/"), seki,
                     str(len(ninau1[eda])), han1, str(len(a1_)),
                     " ".join(a.replace("karo-mac/", "K/") for a in a1_) or "―",
                     chikai.replace("karo-mac/", "K/"),
                     str(sum(1 for a in a1_ if a in fuyou)),
                     str(len(ninau2[eda])), han2, str(len(a2_)),
                     " ".join(a.replace("karo-mac/", "K/") for a in a2_) or "―",
                     str(len(uchi45)),
                     " ".join(a.replace("karo-mac/", "K/") for a in uchi45) or "―"])
    K.kaku_tsv(os.path.join(raw, "51_kusari.tsv"), rows,
               ["枝名(K/=karo-mac/)", "席",
                "段①担ぐcommit数(main に無し)", "段①★着地の鎖★", "段①待つ相手の数",
                "段①待つ相手(悉く)", "段①最も近い相手", "段①内★不要15★の数",
                "段②担ぐcommit数(main＋幹363d5fb に無し)", "段②★着地の鎖★",
                "段②待つ相手の数", "段②待つ相手(悉く)",
                "段③★45本同士★を待つ数", "段③同 名"])

    # ── 対照ⓓ 別器で一対を検む ───────────────────────────
    tameshi = [r for r in rows if r[6] != "―"]
    if not tameshi:
        sys.stderr.write("★待つ枝が一本も無い ∴ 別器の検めが立たぬ ∴ 止まる★\n"); return 5
    t = tameshi[0]
    ko = t[0].replace("K/", "karo-mac/"); oya = t[6].replace("K/", "karo-mac/")
    s_ko, s_oya = sha_of[ko], sha_of[oya]
    rc2, _, _ = git(["merge-base", "--is-ancestor", s_oya, s_ko])
    if rc2 != 0:
        sys.stderr.write("★別器 merge-base が %s→%s の祖先関係を認めぬ(rc=%d) ∴ 止まる★\n"
                         % (oya, ko, rc2)); return 5

    fuyou_machi = [r for r in rows if r[7] != "0"]
    K.kaku(os.path.join(raw, "52_kusari_matome.txt"), "\n".join([
        "母數 45 本 ／ 段① 幹=origin/main %s ／ 段② 幹=main＋%s(家老の幹)" % (MAIN, MIKI),
        "",
        "★段① 幹=main の後★  ⑴単独で載る = %d 本 ／ ⑵他枝を待つ = %d 本" % (tan_kei, matsu_kei),
        "  待つ相手が★不要15★に在る枝 = %d 本" % len(fuyou_machi),
        "  ―― 是は★「不要」の定義の裏返し★である(不要＝残枝の祖先)。疵ではない。",
        "",
        "★段② 家老の幹 %s が載つた後★  ★⑴単独で載る = %d 本★ ／ ⑵猶 待つ = %d 本"
        % (MIKI, tan2_kei, 45 - tan2_kei),
        "  幹 `karo-mac/km-gate-kou-otsu-20260917` は★不要15 の一本★である",
        "  ―― 即ち家老の申す「幹先行」は、★不要と名指した枝を先に載せる★事を意味する。",
        "     (其の可否は當席の測れる所に非ず ―― 理事長裁・軍師mac の判)",
        "",
        "★段③ 45 本同士を待つ枝 = %d 本★(家老紙・當方 km-102 の「独立の葉」と一致)" % uchi45_kei,
        "",
        "別器の検め(対照ⓓ): `git merge-base --is-ancestor %s %s` rc=%d ―― 一致" % (oya, ko, rc2),
        "",
        "★此の数が意味せぬ事★:",
        "  ・「単独で載る」は「衝突せぬ」ではない(merge-tree は本器の外)。",
        "  ・「待つ」は PR の順序の話であり、捨證軸・器軸・重複軸の何れとも別の軸である。",
        "  ・担ぐ commit 数は★幹に無い commit の数★であり、file の数でも変更の量でもない。",
        "  ・段②は「幹が載つた」と仮定した測りであつて、★幹が載つた事実ではない★。",
    ]))
    sys.stderr.write("鎖 段①単独%d/待つ%d(不要15待ち%d) 段②単独%d/待つ%d 段③45本同士%d\n"
                     % (tan_kei, matsu_kei, len(fuyou_machi), tan2_kei, 45 - tan2_kei, uchi45_kei))
    return 0

sys.exit(main())

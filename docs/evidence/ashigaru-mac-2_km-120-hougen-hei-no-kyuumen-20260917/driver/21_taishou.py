#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋓/㋒ の対照 ―― ★己の言ひ分を、己の器で検める★。

三つ立てる。何れも ★陽性対照(鳴る筈の物)★ と ★負対照(鳴らぬ筈の物)★ を対に置く。

  対照甲: 「③sha無 の行は讀み手が飛ばす」 ―― 之が真なら、sha を剥いだ行は
          一致にも相違にも実体無にも数へられぬ。★飛ばす事自体を数で示す★。
  対照乙: 「案庚/案己 の第四則 `path=(.+)$` は ★行末まで呑む★」 ―― 欄に非ざる
          尾(註・TSV の次欄)が候補へ混ざる事を、実際の候補で示す。
  対照丙: 「空白で終る実名」 ―― 己が一度壊した行(km-83 MANIFEST.txt:270 の形)。
          ⑶と三案が★同じ候補★を出す事を示す(回帰の番人)。

★盤は束の外に立てる★(札 kinshi: 束に空白を含む名の実体を置くな)。
"""
import hashlib
import importlib.util
import os
import stat
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

KI = [("⑶_c1486ca1", "_ki/san_c1486ca1.py"), ("案戊", "_an/an_bo_km120.py"),
      ("案庚", "_an/an_kou_km120.py"), ("案己", "_an/an_ki_km120.py")]


def yomu(rel, nm):
    spec = importlib.util.spec_from_file_location("t_" + nm, os.path.join(BUNDLE, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod


def hashira(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    koku = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    ban = "/private/tmp/km120_taishou_%s_%d" % (time.strftime("%Y%m%d_%H%M%S"), os.getpid())
    os.makedirs(ban, exist_ok=True)
    mods = [(nm, yomu(rel, nm.replace("⑶", "s").replace("案", "a"))) for nm, rel in KI]
    out = ["# ㋓/㋒ 対照  刻=%s" % koku, "盤 = %s ★束の外★" % ban, ""]

    # ---- 対照甲: ③sha無 は讀み手が飛ばすか ----
    with open(os.path.join(ban, "kiyoi.txt"), "w") as f:
        f.write("kiyoi\n")
    sha_k = hashira(os.path.join(ban, "kiyoi.txt"))
    out += ["## 対照甲 ―― ★「③sha無 の行は讀み手が飛ばす」を数で示す★",
            "  同じ臺帳を三つ立て、★sha 欄の有無だけ★を違へる。他は一字も違へぬ。",
            "  ★數は語を数へて取らぬ★ ―― 器自身の凡例にも『一致』『実体無』の語が出る故、",
            "  ★結語の一行を解いて★ 母數/一致/相違/実体無 を取る(逐語の行も併せ刷る)。",
            "  ★基点は argv[2] で明示する★ ―― 既定は ★器の在處★ から導く故、",
            "  `_ki/` に置いた写しは repo 根を `docs/evidence` と誤る(実測・己の疵)。"]
    KETSU = re.compile(r"一致 ★?(\d+)★? */ *相違 (\d+) */ *実体無 (\d+) */ *読めぬ行 (\d+)"
                       r"\s*\(母數 (\d+)\)")
    for fuda, gyou in [("陽性対照(sha有・実体有)", "path=kiyoi.txt sha256=%s bytes=6 lines=1" % sha_k),
                       ("陽性対照(sha有・実体無)", "path=nai.txt sha256=%s bytes=6 lines=1" % sha_k),
                       ("★検体(sha無)★", "path=kiyoi.txt bytes=6 lines=1")]:
        mp = os.path.join(ban, "M_%s.txt" % fuda.strip("★").replace("(", "_").replace(")", "")
                          .replace("・", "_"))
        open(mp, "w").write(gyou + "\n")
        r = subprocess.run([sys.executable, "-B", os.path.join(BUNDLE, KI[0][1]), mp,
                            ban + os.sep], capture_output=True, text=True, cwd=ban)
        ze = (r.stdout or "") + (r.stderr or "")
        m = KETSU.search(ze)
        ketsu = [g for g in ze.split("\n") if "母數" in g]
        out.append("  ・%s" % fuda)
        out.append("    行   = %s" % gyou)
        out.append("    rc   = %d" % r.returncode)
        out.append("    結語 = %s" % (ketsu[0].strip() if ketsu else "★解けず★"))
        if m:
            out.append("    ★母數 = %s★(一致%s 相違%s 実体無%s 読めぬ行%s)"
                       % (m.group(5), m.group(1), m.group(2), m.group(3), m.group(4)))
        else:
            out.append("    ★結語を解けず ―― 測れぬ★")
    out += ["",
            "  ★読み方★: sha を剥いだだけで ★母數 1 → 0★。実体は同じ物が同じ場所に在る。",
            "  ∴ 讀み手は ③sha無 の行を ★母數にすら入れぬ★(main の `if not m: continue` の逐語通り)。",
            "  ∴ ③sha無 の行で候補が食ひ違つても ★判定は動かぬ★。之を『差』に数へれば嘘に成る。",
            "  ★但し之は「③sha無 の行が安全」の意ではない★ ―― 讀み手が★見ぬ★だけであり、",
            "  臺帳としては sha を宣して居らぬ行である(門の條①が別途之を咎める)。", ""]

    # ---- 対照乙: 第四則の行末呑み ----
    out += ["## 対照乙 ―― ★案庚/案己 の第四則は行末まで呑む★(★新たに壊す物★)"]
    for fuda, gyou in [
            ("欄のみ(正しく剥げる)", "sha256=%s path=a b.txt bytes=15 lines=1" % ("0" * 64)),
            ("★尾に註★", "sha256=%s path=a b.txt bytes=15 lines=1 # 註である" % ("0" * 64)),
            ("★尾に TSV の次欄★", "sha256=%s path=a b.txt bytes=15 lines=1\t次の欄" % ("0" * 64))]:
        out.append("  ・%s" % fuda)
        out.append("    行 = %s" % gyou.replace("\t", "\\t"))
        for nm, m in mods:
            out.append("      %-12s → %s" % (nm, repr(m.paths_of(gyou))))
    out += ["",
            "  ★読み方★: 欄剥ぎは ★尾に續く `KEY=VALUE` の並び★ しか剥がぬ。",
            "  註や TSV の次欄が尾に在れば ★候補名に混ざる★ ―― ⑶ の①/③ は空白で切る故、",
            "  此の一点では ★⑶ の方が壊れ難い★。案庚/案己 を据ゑるなら之を併せて呑む事に成る。", ""]

    # ---- 対照丙: 空白で終る実名(己が一度壊した形) ----
    out += ["## 対照丙 ―― ★空白で終る実名★(己が一度壊し、測つて見付けた形)",
            "  出所 = km-83-shikii-de-wa-mamorenu-tane-wo-mitsuke-yo-20260917/MANIFEST.txt:270 の形"]
    gyou = 'path="40_doku/otsu_suna/ " sha256=%s bytes=5 lines=1' % ("d" * 64)
    out.append("  行 = %s" % gyou)
    kijun = None
    for nm, m in mods:
        c = m.paths_of(gyou)
        if kijun is None:
            kijun = c
        out.append("    %-12s → %s  %s" % (nm, repr(c), "★同★" if c == kijun else "★異★"))
    out += ["",
            "  ★読み方★: 四器とも末尾の空白を保つ。⑶ と三案で候補は同一である。",
            "  ★之は「空白名が悉く治る」の意ではない★ ―― 括られた形(`path=\"…\"`)の話であり、",
            "  素の空白名(括り無し)は別の面で、下の㋐表 乙/丙 の九面に含まれる。", ""]

    # ---- 対照丁: 欄剥ぎが ★実名の中の `=`★ を食ふか(★案戊/案己 の新たに壊す物★) ----
    out += ["## 対照丁 ―― ★欄剥ぎは実名の中の `=` も食ふ★(★案戊/案己 の新たに壊す物★)",
            "  剥ぎの則は `(?:[ \\t]+[A-Za-z_][A-Za-z0-9_]*=[^ \\t]*)+$`。",
            "  ★之は『欄』と『空白と = を含む実名の尾』を区別できぬ★ ―― 字面が同じ故である。"]
    Z = "0" * 64
    for fuda, gyou in [
            ("★方言乙★ 実名に空白と `=`", "path=foo bar=1.txt sha256=%s bytes=9 lines=1" % Z),
            ("★方言乙★ 実名が `=` で終る", "path=foo bar= sha256=%s bytes=9 lines=1" % Z),
            ("方言丙 実名に空白と `=`", "sha256=%s path=foo bar=1.txt bytes=9 lines=1" % Z)]:
        out.append("  ・%s" % fuda)
        out.append("    行 = %s" % gyou)
        kijun = None
        for nm, m in mods:
            c = m.paths_of(gyou)
            if kijun is None:
                kijun = c
            out.append("      %-12s → %-28s %s" % (nm, repr(c),
                       "" if c == kijun else "★⑶より縮む=回帰★"))
    # 現物での面積(此の新たな疵が現に当たる行は幾つか)
    walk = os.path.join(os.path.dirname(os.path.dirname(BUNDLE)), "evidence")
    walk = os.path.abspath(walk)
    kazu_soto = kazu_ono = 0
    aruita = 0
    for dirpath, dirnames, filenames in os.walk(walk):
        if os.path.basename(dirpath) == "__pycache__":
            dirnames[:] = []
            continue
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                st = os.lstat(fp)
                if not stat.S_ISREG(st.st_mode):
                    continue
                t = open(fp, encoding="utf-8", errors="strict").read()
            except (OSError, UnicodeDecodeError):
                continue
            aruita += 1
            ono = os.path.abspath(fp).startswith(os.path.abspath(BUNDLE) + os.sep)
            for line in t.split("\n"):
                if line.lstrip().startswith("#") or not re.search(r"(?:^|\s)path=\S", line):
                    continue
                if not re.search(r"sha256=[0-9a-f]{64}", line):
                    continue
                a = mods[0][1].paths_of(line)
                b = mods[3][1].paths_of(line)
                # ⑶ の候補に `=` を含み、案己 が其れより縮む行
                if a and "=" in a[0] and b != a:
                    if ono:
                        kazu_ono += 1
                    else:
                        kazu_soto += 1
    out += ["",
            "  ★此の新たな疵の現物面積★(歩き根 %s / 歩いた file %d / 刻 %s)"
            % (walk, aruita, time.strftime("%Y-%m-%dT%H:%M:%S%z")),
            "    ⑶ の候補が `=` を含み、案己 が其れより縮む行:  外 = %d 行 / 己束 = %d 行"
            % (kazu_soto, kazu_ono),
            "    ★此の數が何を意味せぬか★:",
            "      ・★『其れだけの行が偽の赤に成る』の意ではない★ ―― 候補が縮んでも、",
            "        縮んだ名も元の名も ★共に disk に無い★ なら判定は動かぬ(実測: 外の1行が之)。",
            "      ・★0 であつても『起り得ぬ』の意ではない★ ―― `foo bar=1.txt` の如き名を",
            "        誰かが臺帳へ書いた其の日に ★偽の赤★ が生れる。字の形の疵であつて、",
            "        今 現物が無い事は ★将来も無い事を保証せぬ★。",
            "      ・★測つて居らぬ物★: 此の歩き根の外(他 repo・他席の worktree・未だ書かれぬ束)。", ""]

    kaku(os.path.join(BUNDLE, "raw", "21_taishou.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

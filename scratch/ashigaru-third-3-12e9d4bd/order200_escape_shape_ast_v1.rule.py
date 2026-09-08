# -*- coding: utf-8 -*-
u"""order200 ―― ★E5+E6+E7 を一弾で (ast 一発・床(31))★ + o199 の打ち直し

  ★令の逐語★ = 「★順 4 承認(order200・走 0・ast 一発)★=E5(xfail が strict か)／E6(何の床を見るか)／
    E7(assert の前か後か)⇒★107 行中 60 行が測定不能から型へ落ちる★。★E5 が strict なら ―― ★『直つた事が
    赤に成る＝直しの向きが逆に成り得る』を ★上へ回す材★ として明記せよ★★。★o199 の打ち直し(o183/o189 の
    併記表)を同じ紙に置くも正(★前紙は一字も書換へず★)★。」

  ★的の樹★ = /home/hakudoukai/a3/wt-bundle-fix4 (己の樹・ext4・家老が張つた物)
    ―― o192 が測つた樹と ★同じ★。∴ 條 o174 (器を一字も変へずに二度測れ) が打てる。

  ★先に 数を分ける★ (床(30) 何を一つと数へたか / 己の前の一行の言ひ方を正す) ――
    E6 C mark.skipif ★20★ + E7 D pytest.skip( ★40★ = ★60★  ⇒ ★型へ落ちる分★
    E5 E mark.xfail  ★9★ + F pytest.xfail( ★5★ = ★14★  ⇒ ★strict の判じ★ (型ではなく ★色★ の話)
    和 = ★74★。★60 と 14 は 別の物である★ ―― 己は前便で「107 行の内 60 行が型に落ちる」と書いた。
    ★之は C+D の 60 を指して居り E/F の 14 は含まぬ★。此処で分けて書く。

  ★走 0★ = 製品走 0 / DB 0 / network 0 / 書込 0 / git は讀取動詞のみ。ast は ★讀取★ である。
"""
import io, os, re, ast, sys, hashlib, collections

ROOT = u"/home/hakudoukai/a3/wt-bundle-fix4"
HERE = os.path.dirname(os.path.abspath(__file__))

SKIP_DIRS = (u"node_modules", u".git", u".venv", u"venv", u"__pycache__")

def files():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(u".pytest")]
        for f in fns:
            if f.endswith(u".py"): out.append(os.path.join(dp, f))
    return sorted(out)

def rd(fp):
    try: return io.open(fp, encoding="utf-8", errors="replace").read()
    except Exception: return u""

def rel(fp): return fp[len(ROOT)+1:] if fp.startswith(ROOT) else fp

# ------------------------------------------------------------------ 第零段
def stage0():
    p = os.path.abspath(__file__); s = io.open(p, encoding="utf-8").read()
    print(u"== order200 第零段 ―― ★定めを 先に 字にした★ ==")
    print(u"  規 sha16=%s wc=%d split=%d bytes=%d"
          % (hashlib.sha256(s.encode("utf-8")).hexdigest()[:16],
             s.count(chr(10)), len(s.split(chr(10))), len(s.encode("utf-8"))))
    print(u"  的の樹 = %s" % ROOT)
    print(u"  ★E6 C 20 + E7 D 40 = 60 (型へ) / E5 E 9 + F 5 = 14 (色の判じ) ―― ★別の物★★")

# ------------------------------------------------------------------ 第一段
def stage1():
    import subprocess
    print(u"\n== order200 第一段 ―― ★樹の頭★ (條 百七十三) ==")
    def g(*a):
        try: return subprocess.check_output(list(a)).decode("utf-8","replace").strip()
        except Exception as e: return u"ERR:%r" % (e,)
    h = g("git","-C",ROOT,"rev-parse","HEAD")
    b = g("git","-C",ROOT,"rev-parse","--abbrev-ref","HEAD")
    po = g("git","-C",ROOT,"status","--porcelain")
    bad = (h == u"HEAD")   # 家老 條 二百 ―― rev-parse は引けぬ時 引数を其の儘返す
    print(u"  HEAD = %s  ★引けた=%s★" % (h, u"否" if bad else u"是"))
    print(u"  branch = %s" % b)
    print(u"  porcelain = ★%d 行★" % (len(po.split(chr(10))) if po else 0))
    for ln in (po.split(chr(10)) if po else []):
        print(u"     %s" % ln)
    fs = files()
    print(u"  *.py 悉皆 = ★%d★ (除外 dir: %s)" % (len(fs), u"/".join(SKIP_DIRS)))

# ------------------------------------------------------------------ 第二段 (正の対照)
def stage2():
    print(u"\n== order200 第二段 ―― ★正の対照★ o192 の 8 種を 今日 数へ直す (條 o174) ==")
    PATS = [
     (u"A importorskip",        re.compile(r"importorskip"),                             3),
     (u"B mark.skip (無条件)",  re.compile(r"mark\.skip\s*[\(\)]|mark\.skip$"),         23),
     (u"C mark.skipif (条件付)", re.compile(r"mark\.skipif"),                            20),
     (u"D pytest.skip( (実行時)", re.compile(r"(?<![a-zA-Z0-9_.])pytest\.skip\s*\("),    40),
     (u"E mark.xfail",          re.compile(r"mark\.xfail"),                              9),
     (u"F pytest.xfail(",       re.compile(r"(?<![a-zA-Z0-9_.])pytest\.xfail\s*\("),    5),
     (u"G except ImportError",  re.compile(r"except\s+.*ImportError"),                   30),
     (u"H collect_ignore",      re.compile(r"collect_ignore"),                            1),
    ]
    fs = files()
    for nm, rg, want in PATS:
        n = 0; nf = set()
        for fp in fs:
            for ln in rd(fp).split(chr(10)):
                if rg.search(ln): n += 1; nf.add(fp)
        print(u"  %-26s 今日 行=★%3d★ file=%3d / o192 の紙=%3d ★%s★"
              % (nm, n, len(nf), want, u"一致" if n == want else u"合はぬ"))

# ------------------------------------------------------------------ 第三段 (E5)
def stage3():
    print(u"\n== order200 第三段 ―― ★E5 xfail が strict か★ ==")
    print(u"  -- ㋐ 床 (config) を 悉皆で --")
    for c in ("pytest.ini","setup.cfg","pyproject.toml","tox.ini","conftest.py"):
        fp = os.path.join(ROOT, c)
        if os.path.exists(fp):
            t = rd(fp)
            print(u"     %-16s ★現に在る★ wc=%d  xfail_strict=★%d 件★"
                  % (c, t.count(chr(10)), t.count(u"xfail_strict")))
            for ln in t.split(chr(10)):
                if ln.strip(): print(u"        逐語: %s" % ln.rstrip())
        else:
            print(u"     %-16s ★現に無い★" % c)
    print(u"  -- ㋑ 樹の悉皆で xfail_strict を (陽性対照 xfail も 同じ打で) --")
    fs = files(); ns = nx = 0; fs_s = set(); fs_x = set()
    for fp in fs:
        t = rd(fp)
        if u"xfail_strict" in t: ns += t.count(u"xfail_strict"); fs_s.add(fp)
        if u"xfail" in t:        nx += t.count(u"xfail");        fs_x.add(fp)
    print(u"     xfail_strict = ★%d 件 / file %d★" % (ns, len(fs_s)))
    print(u"     xfail        = ★%d 件 / file %d★  ← ★陽性対照★ (條 o178)" % (nx, len(fs_x)))
    print(u"  -- ㋒ 行ごとの strict= keyword を ast で --")
    tot = 0; st = collections.Counter(); rows = []
    for fp in fs:
        t = rd(fp)
        if u"xfail" not in t: continue
        try: tree = ast.parse(t)
        except Exception: continue
        for nd in ast.walk(tree):
            if not isinstance(nd, ast.Call): continue
            f = nd.func
            nm = None
            if isinstance(f, ast.Attribute): nm = f.attr
            if nm != u"xfail": continue
            tot += 1
            kw = dict((k.arg, k.value) for k in nd.keywords if k.arg)
            if u"strict" in kw:
                try: v = ast.unparse(kw[u"strict"])
                except Exception: v = u"?"
                st[u"strict=" + v] += 1
                rows.append((rel(fp), nd.lineno, u"strict=" + v))
            else:
                st[u"strict 無し"] += 1
                rows.append((rel(fp), nd.lineno, u"strict 無し"))
    print(u"     ast が見た xfail の Call = ★%d★" % tot)
    for k, v in st.most_common(): print(u"        %-14s : ★%d★" % (k, v))
    print(u"     (先頭 8 行の在処)")
    for r in rows[:8]: print(u"        %s:%d  %s" % r)
    print(u"  -- ㋓ ★判じ★ --")
    if ns == 0:
        print(u"     床 `xfail_strict` は ★現に無い★ (樹の悉皆 0 件・陽性対照 xfail は %d 件で効いて居る)" % nx)
        print(u"     ∴ ★pytest の既定 = strict False★ が効く")
    if st.get(u"strict=True", 0) == 0:
        print(u"     行の `strict=True` も ★現に無い★")
        print(u"     ⇒ ★★E/F の xfail は 悉く 非 strict である★★")
        print(u"     ⇒ ★『直つた事が赤に成る＝直しの向きが逆に成り得る』は ★現に起きて居らぬ★★")
        print(u"     ⇒ ★而して 裏返しの害が 現に在る★ ―― 非 strict では ★直つた事も 壊れた事も 同じ色★")
        print(u"        (o192:105 逐語: 「strict でなければ ★直つた事★ も ★壊れた事★ も同じ色」)")
        print(u"     ⇒ ★★上へ回す材★★ = 「E9+F5 = 14 行は ★直つても 緑のまま★ ∴ ★直した事が 誰にも見えぬ★」")

# ------------------------------------------------------------------ 第四段 (E6)
def stage4():
    print(u"\n== order200 第四段 ―― ★E6 C mark.skipif 20 行が 何の床を見るか★ (ast) ==")
    AX = [(u"env",      re.compile(r"environ|getenv|os\.env")),
          (u"version",  re.compile(r"version_info|__version__|sys\.version|VERSION")),
          (u"platform", re.compile(r"platform|sys\.platform|darwin|win32|linux")),
          (u"import",   re.compile(r"importorskip|find_spec|ImportError|module")),
          (u"flag",     re.compile(r"FLAG|ENABLE|DISABLE|SKIP_|_ON$|True|False")),
          ]
    fs = files(); tot = 0; ax = collections.Counter(); rows = []
    for fp in fs:
        t = rd(fp)
        if u"skipif" not in t: continue
        try: tree = ast.parse(t)
        except Exception: continue
        for nd in ast.walk(tree):
            if not isinstance(nd, ast.Call): continue
            f = nd.func
            if not (isinstance(f, ast.Attribute) and f.attr == u"skipif"): continue
            tot += 1
            try: cond = ast.unparse(nd.args[0]) if nd.args else u"(引数無し)"
            except Exception: cond = u"(unparse 不能)"
            hit = [nm for nm, rg in AX if rg.search(cond)]
            if not hit: hit = [u"その他"]
            for h in hit: ax[h] += 1
            rows.append((rel(fp), nd.lineno, u"+".join(hit), cond[:88]))
    print(u"  ast が見た skipif の Call = ★%d★ (o192 の紙 = 20)" % tot)
    print(u"  ★床の軸★ (★一つの条件が 二軸に掛かる事が在る ∴ 和は Call 数を超え得る★ ―― 床(30))")
    for k, v in ax.most_common(): print(u"     %-10s : ★%d★" % (k, v))
    print(u"  ★内訳 (悉皆・条件式を unparse して逐語)★")
    for r in rows: print(u"     %s:%d [%s]  %s" % r)

# ------------------------------------------------------------------ 第五段 (E7)
def stage5():
    print(u"\n== order200 第五段 ―― ★E7 D pytest.skip( 40 が assert の前か後か★ (ast) ==")
    fs = files(); tot = 0; cnt = collections.Counter(); rows = []
    for fp in fs:
        t = rd(fp)
        if u"pytest.skip" not in t: continue
        try: tree = ast.parse(t)
        except Exception: continue
        # 関数体ごとに assert の lineno を集める
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
            asserts = sorted(n.lineno for n in ast.walk(fn) if isinstance(n, ast.Assert))
            for nd in ast.walk(fn):
                if not isinstance(nd, ast.Call): continue
                f = nd.func
                if not (isinstance(f, ast.Attribute) and f.attr == u"skip"): continue
                if not (isinstance(f.value, ast.Name) and f.value.id == u"pytest"): continue
                tot += 1
                if not asserts:
                    k = u"assert 無し (検め 0)"
                elif nd.lineno < asserts[0]:
                    k = u"assert の ★前★ (検め前に降りる)"
                elif nd.lineno > asserts[-1]:
                    k = u"assert の ★後★ (検め了へて降りる)"
                else:
                    k = u"assert の ★間★ (半端な検め)"
                cnt[k] += 1
                rows.append((rel(fp), nd.lineno, fn.name, k, len(asserts)))
    print(u"  ast が見た pytest.skip の Call = ★%d★ (o192 の紙 = 40)" % tot)
    print(u"  ★但し 之は ★関数体の中★ に在る物のみ★ ―― module 直下 / conftest の物は ast.FunctionDef の外ゆゑ落ちる")
    for k, v in cnt.most_common(): print(u"     %-32s : ★%d★" % (k, v))
    print(u"  ★内訳 (悉皆)★")
    for r in rows: print(u"     %s:%d  def %s  [%s] assert数=%d" % r)

# ------------------------------------------------------------------ 第六段 (o199 の打ち直し)
def stage6():
    print(u"\n== order200 第六段 ―― ★o199 の打ち直し★ (家老 條 百九十七) ==")
    print(u"  ★order199 で A3 = ★−7 が正★ と定まつた (o180 が len() から計算) ∴ −9 を持つ紙に條 百九十七 が掛かる★")
    print(u"  ★前紙は 一字も 書き換へぬ★ ―― 此処に ★併記表★ を置くのみ (令の逐語)")
    import glob
    pats = [(u"A3 = ★-9★", u"o183 形"), (u"A3 = -9", u"規の literal 形"), (u"| A3 | −7 | −7 | −9 |", u"o185 の食ひ違ひ表")]
    for pat, nm in pats:
        rows = []
        for fp in sorted(glob.glob(os.path.join(HERE, u"*.md"))) + sorted(glob.glob(os.path.join(HERE, u"*.rule.py"))):
            t = rd(fp); c = t.count(pat)
            if c: rows.append((os.path.basename(fp), c))
        print(u"  [%s] 「%s」 ―― 度数 ★%d★ / 物 ★%d★" % (nm, pat, sum(r[1] for r in rows), len(rows)))
        for r in rows: print(u"     %-46s ×%d" % r)

# ------------------------------------------------------------------ 第七段 (器の突合)
def stage7():
    u"""★第二段が合はなんだ ∴ 條 o178 ―― 器の否を疑つたなら 器の是も疑へ★

    己は第二段で「o192 の器を一字も変へず」と書いたが ―― ★己は 正規を 写して 己の器の中で 走らせた★。
    ∴ 之は 條 o174 の破りである。此処で ★o192 の規 其の物を subprocess で走らせ★ 突合する。
    """
    import subprocess, difflib
    print(u"\n== order200 第七段 ―― ★己の写し 対 o192 の規 其の物★ (條 o174 / o178) ==")
    fn = u"order192_test_escape_census_v1.rule.py"
    fp = os.path.join(HERE, fn)
    if not os.path.exists(fp):
        print(u"  %s は ★現に無い★ ⇒ 突合 ★測定不能★" % fn); return
    sh = hashlib.sha256(io.open(fp,"rb").read()).hexdigest()[:16]
    t  = io.open(fp, encoding="utf-8").read()
    print(u"  o192 規 sha16=%s wc=%d split=%d" % (sh, t.count(chr(10)), len(t.split(chr(10)))))
    m = re.search(r"ROOT\s*=\s*u?[\"']([^\"']+)", t)
    print(u"  o192 の ROOT 逐語 = %s   己の ROOT = %s   ★%s★"
          % (m.group(1) if m else u"(取れず)", ROOT,
             u"同じ" if (m and m.group(1) == ROOT) else u"合はぬ"))
    print(u"  -- ㋐ 己が写した正規 と o192 の正規 を 逐語で 突合 --")
    mine = [u'mark\\.skip\\s*[\\(\\)]|mark\\.skip$', u'mark\\.skipif']
    for pat in mine:
        print(u"     己=%-34s o192 に ★%s★" % (pat, u"現に在る" if pat in t else u"現に無い"))
    for ln_no, ln in enumerate(t.split(chr(10)), 1):
        if u"re.compile" in ln:
            print(u"     o192:%d 逐語: %s" % (ln_no, ln.strip()))
    print(u"  -- ㋑ o192 の規 其の物を 走らせる --")
    pr = subprocess.Popen([sys.executable, fn], cwd=HERE,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    o = pr.communicate()[0].decode("utf-8","replace")
    print(u"     exit_code = %d / 出力 wc = %d" % (pr.returncode, o.count(chr(10))))
    for ln in o.split(chr(10)):
        if re.search(r"(importorskip|mark\.skip|pytest\.skip|mark\.xfail|pytest\.xfail|ImportError|collect_ignore|合計|母数|悉皆)", ln):
            print(u"     o192 出力: %s" % ln.rstrip())
    print(u"  -- ㋒ 前窓の己の数 (xfail = 51 file) を 打ち直す --")
    fs = files()
    n_walk = len([f for f in fs if u"xfail" in rd(f)])
    print(u"     今日 os.walk (除外 %s) = ★file %d★" % (u"/".join(SKIP_DIRS), n_walk))
    try:
        g = subprocess.check_output(["/usr/bin/grep","-rl","xfail",ROOT]).decode("utf-8","replace")
        gl = [x for x in g.split(chr(10)) if x]
        gpy = [x for x in gl if x.endswith(u".py")]
        gex = [x for x in gl if any((chr(47)+d+chr(47)) in x for d in SKIP_DIRS)]
        print(u"     /usr/bin/grep -rl (除外 ★無し★) = ★file %d★ / 内 *.py = ★%d★ / 内 除外 dir 配下 = ★%d★"
              % (len(gl), len(gpy), len(gex)))
        print(u"     ⇒ ★前窓の 51 は 『除外を掛けぬ grep が 見た file 数』であり 母数が違ふ★ (床(4))")
    except Exception as e:
        print(u"     /usr/bin/grep = ERR:%r ⇒ ★測定不能★" % (e,))

# ------------------------------------------------------------------ 第八段 (E6 の軸を細かく / E5 の逐語 / 母数の突合)
def stage8():
    u"""★第四段の軸が粗かつた ―― `os.name == 'nt'` も `.exists()` も「その他」へ落ちた★

    ∴ 家老 條 百九十七 (器を直したら 遡つて 併記で 打ち直せ) に従ひ ―― ★第四段は消さず★ 此処に併記する。
    """
    import collections
    print(u"\n== order200 第八段 ―― ★E6 の軸を細かく 打ち直す★ (條 百九十七・併記) ==")
    AX2 = [
      (u"㋐ file の在否", re.compile(r"\.exists\(|_has_text|Path\(|is_file\(|is_dir\(")),
      (u"㋑ platform",    re.compile(r"os\.name|sys\.platform|platform\.|'nt'|\"nt\"|darwin|win32")),
      (u"㋒ env",         re.compile(r"environ|getenv")),
      (u"㋓ version",     re.compile(r"version_info|__version__|sys\.version")),
      (u"㋔ 道具の在否",   re.compile(r"_installed|which\(|shutil\.which|ffmpeg")),
      (u"㋕ secret の有無", re.compile(r"_KEY|_URL|TOKEN|SERVICE")),
    ]
    fs = files(); tot = 0; ax = collections.Counter(); multi = 0; rows = []
    for fp in fs:
        t = rd(fp)
        if u"skipif" not in t: continue
        try: tree = ast.parse(t)
        except Exception: continue
        for nd in ast.walk(tree):
            if not isinstance(nd, ast.Call): continue
            f = nd.func
            if not (isinstance(f, ast.Attribute) and f.attr == u"skipif"): continue
            tot += 1
            try: cond = ast.unparse(nd.args[0]) if nd.args else u"(引数無し)"
            except Exception: cond = u"(unparse 不能)"
            hit = [nm for nm, rg in AX2 if rg.search(cond)]
            if len(hit) > 1: multi += 1
            if not hit: hit = [u"㋖ 何れにも当たらぬ"]
            for h in hit: ax[h] += 1
            rows.append((rel(fp), nd.lineno, u"+".join(hit)))
    print(u"  母数 (ast の skipif Call) = ★%d★" % tot)
    print(u"  ★二軸以上に掛かつた Call = ★%d★ ∴ 下の和は 母数を超え得る★ (床(30))" % multi)
    for k, v in sorted(ax.items()): print(u"     %-18s : ★%d★" % (k, v))
    print(u"  ★何れにも当たらぬ物の逐語★")
    for r in rows:
        if u"㋖" in r[2]: print(u"     %s:%d" % (r[0], r[1]))
    print(u"  ⇒ ★上へ回す材★ = 「C 32 行の条件が見る物の最大群は ★床 (env/version/platform) ではなく")
    print(u"      ★物 (fixture file・道具) の在否★ である ∴ ★其の物を置けば 飛ばずに走る★」")

    print(u"\n  -- ★E5 の strict=True 4 件の 在処を 逐語で★ --")
    for fp in fs:
        t = rd(fp)
        if u"strict=True" not in t and u"strict = True" not in t: continue
        for i, ln in enumerate(t.split(chr(10)), 1):
            if u"strict" in ln and u"True" in ln:
                print(u"     %s:%d | %s" % (rel(fp), i, ln.strip()[:150]))

    print(u"\n  -- ★母数の突合 (床(4) ―― 何れの評価器から見た N か)★ --")
    n_re_e = n_re_f = 0
    RE_E = re.compile(r"mark\.xfail"); RE_F = re.compile(r"(?<![a-zA-Z0-9_.])pytest\.xfail\s*\(")
    for fp in fs:
        for ln in rd(fp).split(chr(10)):
            if RE_E.search(ln): n_re_e += 1
            if RE_F.search(ln): n_re_f += 1
    print(u"     正規 E mark.xfail = ★%d 行★ / 正規 F pytest.xfail( = ★%d 行★ / 和 = ★%d★"
          % (n_re_e, n_re_f, n_re_e + n_re_f))
    n_ast = 0; note = []
    for fp in fs:
        t = rd(fp)
        if u"xfail" not in t: continue
        try: tree = ast.parse(t)
        except Exception: continue
        for nd in ast.walk(tree):
            if isinstance(nd, ast.Call) and isinstance(nd.func, ast.Attribute) and nd.func.attr == u"xfail":
                n_ast += 1
    print(u"     ast の xfail Call = ★%d★  ⇒ 差 = ★%d★" % (n_ast, n_re_e + n_re_f - n_ast))
    print(u"     ★差の在処★ (正規が拾ひ ast が拾はぬ行 = ★Call でない所に名が在る★ ―― 條(21)㋑)")
    for fp in fs:
        t = rd(fp)
        for i, ln in enumerate(t.split(chr(10)), 1):
            if RE_E.search(ln) or RE_F.search(ln):
                st = ln.strip()
                if not (st.startswith(u"@") or st.startswith(u"pytest.xfail") or u"= pytest.mark.xfail" in st):
                    print(u"        %s:%d | %s" % (rel(fp), i, st[:130]))

if __name__ == "__main__":
    stage0(); stage1(); stage2(); stage3(); stage4(); stage5(); stage6(); stage7(); stage8()

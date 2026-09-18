#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 50_bangai.py ―― ★裁の三口の外に落ちる file を「別行」として立てる器★(第53弾 ㋓)
#
# 何故要るか: 定義丁の條(全)は `${NAME:-N}` の形だけを口と数へる。
#   ∴ 閾を ★直に代入★ して居る file は 口=0 と出て、定義丁の母數に一つも入らぬ。
#   然し其の file が fail-open を持たぬ訳ではない ―― 條が違ふだけである。
#   本器は同じ file に二つの條を当て、★口 0 と 素 12 が併存する事★を一枚で示す。
#
# 條(甲) = 定義丁 條(全): ERE \$\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\}   (1 出現 1 口)
# 條(乙) = 第52弾の素(fail-open 地): test(1) の數比較で、取り落ちが ★rc=2★ に成り得る地
#          ―― ⑴`[ "$x" -ge "$THR" ] 2>/dev/null &&` 形 ⑵`if [ "$x" -lt "$THR" ] 2>/dev/null; then` 形
#          ★2>/dev/null は rc を隠さぬ(stderr のみ捨てる)。rc=2 は生きて then を外す。★
# 使ひ方: 50_bangai.py --mato <file> [--mato <file> ...]
import sys, os, re, time, hashlib

mato = []
av = sys.argv[1:]; i = 0
while i < len(av):
    if av[i] == '--mato' and i+1 < len(av): mato.append(av[i+1]); i += 2; continue
    sys.stderr.write(u'★測れぬ: 知らぬ引数 %s★\n' % av[i]); sys.exit(2)
if not mato:
    sys.stderr.write(u'★測れぬ: --mato を argv で渡せ(對象を字面で埋め込まぬ)★\n'); sys.exit(2)

KOU = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*):-([0-9]+)\}')
SHIKII_NA = re.compile(r'^[A-Z][A-Z0-9_]*$')
# 乙: `[` … 數比較演算子 … `]` を持ち、且つ同じ行に 2>/dev/null が在る地
OTSU = re.compile(r'\[\s+"?\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?"?\s+-(ge|gt|le|lt|eq|ne)\s+"?\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?"?\s+\]')
KAKUSHI = re.compile(r'2>\s*/dev/null')

w = sys.stdout.write
w(u'# 50_bangai ―― 裁の三口の外の file を別行で立てる / 刻= %s\n' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w(u'# 條(甲)= 定義丁 條(全) \\$\\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\\} (1 出現 1 口)\n')
w(u'# 條(乙)= test(1) の數比較 ∧ 同行に 2>/dev/null ―― 取り落ちが rc=2 に成り得る地(第52弾の「素」)\n')
w(u'# ★二條は別物である。甲=0 は「fail-open が無い」の意に非ず。★\n')
rc_all = 0
for m in mato:
    w(u'\n=== 對象= %s ===\n' % m)
    if not os.path.isfile(m):
        w(u'★測れぬ: file が無い(%s)★\n' % m); rc_all = 3; continue
    b = open(m, 'rb').read()
    try:
        s = b.decode('utf-8')
    except UnicodeDecodeError:
        w(u'★讀めぬ: 非UTF-8(%s)★\n' % m); rc_all = 3; continue
    w(u'# sha256/16= %s / bytes= %d / 行= %d\n'
      % (hashlib.sha256(b).hexdigest()[:16], len(b), s.count(u'\n')))
    lines = s.split(u'\n')
    kou_n = 0; kou_shikii = 0; rows = []
    for no, ln in enumerate(lines, 1):
        for mo in KOU.finditer(ln):
            kou_n += 1
            na, kt = mo.group(1), mo.group(2)
            chu = ln.lstrip().startswith(u'#')
            ok = bool(SHIKII_NA.match(na)) and int(kt) >= 1 and not chu
            if ok: kou_shikii += 1
            rows.append((no, na, kt, chu, ok))
    w(u'[甲] 條(全)の口= %d / 其の内 條(閾)を満たす口= %d\n' % (kou_n, kou_shikii))
    if kou_n == 0:
        w(u'  ★甲の口が一つも無い ―― 此の file は定義丁の母數に ★一行も★ 入らぬ(閾を直に代入して居る故)★\n')
    for no, na, kt, chu, ok in rows:
        w(u'  %d\t%s:-%s\t註行=%s\t閾條=%s\n' % (no, na, kt, u'真' if chu else u'偽', u'立つ' if ok else u'落つ'))
    otsu = []
    for no, ln in enumerate(lines, 1):
        mo = OTSU.search(ln)
        if mo and KAKUSHI.search(ln):
            otsu.append((no, mo.group(1), mo.group(2), mo.group(3), ln.strip()))
    w(u'[乙] 素(fail-open 地)= %d\n' % len(otsu))
    for no, l, op, r, ln in otsu:
        w(u'  %d\t左=$%s -%s 右=$%s\t%s\n' % (no, l, op, r, ln))
    # ★第52弾は「12/12 悉く素」と述べた。之は ★行(地)★ の數ではなく ★項★ の數である。
    #   ∴ 項を数へ、各項の ★生れ★(値が何處から来るか)を ★對象の中で實測した五形★ で分ける。
    #   ★疵(本弾で踏んだ)★ 初手は `N=${N:-既定}` の形だけを env 既定と見た。
    #     對象は `: "${N:=既定}"`(代入付き) を用ゐる故 一つも当たらず「外から入る=1」と刷つた。
    #     ―― 之は ★定義丁の條(全) が本 file に 0 口である真因其の物★ である(條は `:-` を要る)。
    import re as _re
    UMARE = [
        (u'env既定(:=・展開時に代入)', r'^\s*:\s*"?\$\{%s:=', True),
        (u'env既定(:-・展開時のみ)',   r'\$\{%s:-',              True),
        # ★疵(續)★ 先読みの括りを `\$\(?!\(` と書いた ―― 之は「$ + 任意の( + 字面!」で、
        #   先読みに成つて居らぬ。∴ `m5=$(count_unstarted_subphases)` を拾へなかつた。
        (u'外器の出目($(…))',          r'^\s*(?:local\s+)?%s=\$\((?!\()', True),
        (u'他器の出目(read で受く)',   r'^\s*(?:IFS=\S*\s+)?read\s+(?:-r\s+)?[^\n]*\b%s\b', True),
        (u'状態/一覧を辿る(for)',      r'^\s*for\s+%s\s+in\s',  True),
        (u'算($((…)))',                r'^\s*(?:local\s+)?%s=\$\(\(', False),
        (u'直書き',                    r'^\s*(?:local\s+)?%s=[0-9"\x27]', False),
        (u'引數で受く(local N="$k")',  r'^\s*local\s+%s="\$[0-9]',        False),
    ]
    def umare(na):
        mi = []
        for nm, pat, soto in UMARE:
            rx = _re.compile(pat % _re.escape(na))
            gyo = [k + 1 for k, l in enumerate(lines) if rx.search(l)]
            if gyo:
                mi.append((nm, soto, gyo))
        return mi
    kou_soto = 0
    w(u'[乙・項] 項の數= %d (地 %d × 左右2) ―― ★「12」は此の單位の數である★\n'
      % (len(otsu) * 2, len(otsu)))
    for no, l, op, r, ln in otsu:
        for kata, na in ((u'左', l), (u'右', r)):
            mi = umare(na)
            soto = any(x[1] for x in mi)
            if soto: kou_soto += 1
            w(u'  %d\t%s $%s\t外から入る=%s\t生れ= %s\n'
              % (no, kata, na, u'★真★' if soto else u'偽',
                 u' / '.join(u'%s@%s' % (x[0], u','.join(str(g) for g in x[2])) for x in mi)
                 or u'(代入を見ず ―― 測れぬ)'))
    w(u'[乙・項] ★外から値が入り得る項= %d / %d★\n' % (kou_soto, len(otsu) * 2))
    w(u'[併記] 甲の口= %d ／ 乙の素= %d ―― ★同じ file で二つの數が別々に立つ★\n' % (kou_n, len(otsu)))
sys.exit(rc_all)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_saisou.py <束の根> ―― km-98 の器を ★頭を固定して再走★ し、出目を `_saisou/` の新名へ置く。

★提出済の `_raw/` には一字も触れぬ★(裁: 出した紙は直さぬ)。前後は 20_cmp.py が byte で突き合はせる。

固定する頭(紙が宣した物・README の 固定基点):
  基点 = 1da2b6b9fb7fcf9a4a51be2c495b3a0fef386424
  親   = 3b413b7ef7ae871908ce4d74a4d939fdfbd8ade1 (陽性対照)
  main = 363d5fb060845171338c067ef42bfcbef8ad9188 ―― ★argv は元の通り 'main' の字を渡す★。
         固定の證は 12 行目の `main_sha` を紙へ書く事で立てる(字が動けば sha が動く)。

argv は ★出目そのものから復元した★(手の記憶でなく):
  ・`_raw/<stem>.tsv` の頭行 `tree(<rev[:8]>)` が classify の第一引数を名指す
  ・`_raw/11_hooks_base.err` の `rev=...` が 10_hooks_from_rev の引数を名指す
  ・`_raw/91_hooks_disk.err` の `rev=.claude/settings.json` が 12_hooks_from_file の引数を名指す
  ・`_raw/36|38.txt` の頭行 `# main = 4 本 / 1da2b6b9 = 6 本` が diff の四引数の並びを名指す

★母數の宣★: `_raw/` の現物 48 本の内、★器が産んだのは 10 幹 × 3 面(本体/err/rc)= 30 本★。
残る 18 本は手で測つた物(70_* の interp 探り・80_cwd・90_disk・93_base・94_diff・95_行・96_交叉・30_main_sha)で
あり ★器では再走できぬ★ ∴ 本器の的から外す。★「外した」は「無い」の意に非ず。★

cwd は ★repo の根★ に固定する(12_hooks_from_file が `.claude/settings.json` を根相対で食ふゆゑ)。
"""
import os, subprocess, sys

BASE = '1da2b6b9fb7fcf9a4a51be2c495b3a0fef386424'
OYA  = '3b413b7ef7ae871908ce4d74a4d939fdfbd8ade1'

def main():
    if len(sys.argv) != 2:
        sys.stderr.write('usage: 10_saisou.py <束の根>\n'); return 2
    B = os.path.abspath(sys.argv[1])
    if not os.path.basename(B).startswith('ashigaru-mac-2_km-98-'):
        sys.stderr.write('★束の名が km-98 に非ず★ %s\n' % B); return 3
    ROOT = subprocess.run(['git', '-C', B, 'rev-parse', '--show-toplevel'],
                          capture_output=True, text=True).stdout.strip()
    if not ROOT:
        sys.stderr.write('★repo の根を引けぬ★\n'); return 4
    S = os.path.join(B, '_saisou')
    I = os.path.join(B, '_inst')
    os.makedirs(S, exist_ok=True)

    main_sha = subprocess.run(['git', '-C', ROOT, 'rev-parse', 'main'],
                              capture_output=True, text=True).stdout.strip()
    sys.stderr.write('★頭の固定★ 基点=%s / 親=%s / main=%s\n' % (BASE, OYA, main_sha))

    def t(stem, ext, argv):
        return (stem, ext, argv)
    # 幹 → (出目の拡張子, argv)  ※tsv の入は ★再走で産んだ物★ を鎖に用ゐる
    b_tsv = os.path.join(S, '11_hooks_base.tsv')
    m_tsv = os.path.join(S, '31_hooks_main.tsv')
    d_tsv = os.path.join(S, '91_hooks_disk.tsv')
    f_tsv = os.path.join(B, '_fixture', '50_fixture_hooks.tsv')
    TBL = [
        t('11_hooks_base', 'tsv', [os.path.join(I, '10_hooks_from_rev.py'), BASE]),
        t('31_hooks_main', 'tsv', [os.path.join(I, '10_hooks_from_rev.py'), 'main']),
        t('91_hooks_disk', 'tsv', [os.path.join(I, '12_hooks_from_file.py'), '.claude/settings.json']),
        t('21_class_base', 'tsv', [os.path.join(I, '20_classify.py'), BASE, b_tsv]),
        t('32_class_main', 'tsv', [os.path.join(I, '20_classify.py'), 'main', m_tsv]),
        t('40_pos_parent', 'tsv', [os.path.join(I, '20_classify.py'), OYA, b_tsv]),
        t('51_pos_fixture', 'tsv', [os.path.join(I, '20_classify.py'), BASE, f_tsv]),
        t('92_class_disk', 'tsv', [os.path.join(I, '20_classify.py'), BASE, d_tsv]),
        t('36_diff_NAIVE_bad_key', 'txt',
          [os.path.join(I, '35_diff_hooksets.py'), m_tsv, 'main', b_tsv, '1da2b6b9']),
        t('38_diff_main_base_v2', 'txt',
          [os.path.join(I, '37_diff_hooksets_v2.py'), m_tsv, 'main', b_tsv, '1da2b6b9']),
    ]

    argv_log = ['# 10_saisou.py が実際に走らせた argv(逐語)',
                '# cwd=%s' % ROOT,
                '# main が指した sha=%s' % main_sha]
    ochi = 0
    for stem, ext, argv in TBL:
        p = subprocess.run([sys.executable, '-B'] + argv, cwd=ROOT, capture_output=True)
        open(os.path.join(S, '%s.%s' % (stem, ext)), 'wb').write(p.stdout)
        err = p.stderr
        if not err:
            err = ('# (空) ―― 此の器は stderr へ一字も出さず。0byte は門 條④ が鳴らすゆゑ、'
                   '★宣して★ 此の一行を置く。元は 0 byte。\n').encode('utf-8')
        open(os.path.join(S, '%s.err' % stem), 'wb').write(err)
        open(os.path.join(S, '%s.rc' % stem), 'w', encoding='utf-8').write('rc=%d\n' % p.returncode)
        argv_log.append('%s\t%s' % (stem, '\t'.join(argv)))
        if p.returncode != 0:
            ochi += 1
            sys.stderr.write('★落つ★ %s rc=%d\n' % (stem, p.returncode))
        else:
            sys.stderr.write('走つた %s rc=0 (%d byte)\n' % (stem, len(p.stdout)))
    open(os.path.join(S, '11_argv.txt'), 'w', encoding='utf-8').write('\n'.join(argv_log) + '\n')
    sys.stderr.write('★幹=%d / rc≠0=%d★\n' % (len(TBL), ochi))
    sys.stderr.write('★註★ 産んだのは %d 幹 × 3 面 = %d 本。`_raw/` の 48 本との差 18 本は'
                     '手で測つた物であり器では再走できぬ(器の docstring に列べた)。\n'
                     % (len(TBL), len(TBL) * 3))
    return 0 if ochi == 0 else 5

sys.exit(main())

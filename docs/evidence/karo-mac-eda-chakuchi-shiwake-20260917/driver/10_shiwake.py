#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""残45本を「着地(PR)／捨てる(理事長裁待ち)」へ仕分ける器（★読取のみ★）。
裁 seq325884: 枝は一本も消さぬ。checkout/merge/push を一切行はぬ。
測る物は四つ ―― ⑴対 origin/main 差分 file 数 ⑵自前差分 file 数 ⑶commit 数 ⑷触る領域。
★⑴は「此の枝が変へた数」では無い。origin/main が何 file 遅れて居るかである。★
"""
import subprocess, sys, os

BASE = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'   # origin/main の tip（実測で固定）
# ★臺帳の根は束内相対★ゆゑ cwd は束の中。前弾の raw は repo 根から引く。
ROOT  = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                       capture_output=True, text=True).stdout.strip()
FUYOU = os.path.join(ROOT, 'docs/evidence/karo-mac-eda-fuyou-20260917/raw/40_fuyou.tsv')
ZEN   = os.path.join(ROOT, 'docs/evidence/karo-mac-eda-fuyou-20260917/raw/20_mac_eda.tsv')

def g(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout

KIGU_NE = ('scripts/', '.claude/', '.github/', 'config/', 'instructions/', 'agents/', 'skills/')

def _is_kigu(path):
    p = path.strip('"')
    if p.startswith(KIGU_NE):
        return True
    return '/' not in p          # repo 直下(.gitignore / CLAUDE.md / shutsujin_departure.sh 等)


def kaki(path, lines):
    """★生の > 捕りを使はぬ★ ―― 末尾空白を削り・CR を除き・EOF 改行を丁度 1 に。"""
    body = '\n'.join(l.replace('\r', '').rstrip() for l in lines)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(body + '\n')

def main():
    zen = [l.rstrip('\n').split('\t') for l in open(ZEN, encoding='utf-8')][1:]
    fuyou = {l.rstrip('\n').split('\t')[1] for i, l in enumerate(open(FUYOU, encoding='utf-8')) if i}
    tips = {n: s for s, n in zen}                 # mac 枝 60 本の tip（祖先探索の母集合）
    nokori = [(s, n) for s, n in zen if n not in fuyou]

    rows, log = [], []
    log.append('刻=%s' % subprocess.run(['date', '+%Y-%m-%dT%H:%M:%S%z'],
                                        capture_output=True, text=True).stdout.strip())
    log.append('origin/main=%s' % BASE)
    log.append('mac 全枝=%d / 不要=%d / 残=%d' % (len(zen), len(fuyou), len(nokori)))

    for sha, name in nokori:
        rc_e, _ = g('cat-file', '-e', sha + '^{commit}')
        rc1, d1 = g('diff', '--name-only', '%s...%s' % (BASE, sha))
        n1 = len([x for x in d1.split('\n') if x])
        rc3, c = g('rev-list', '--count', '%s..%s' % (BASE, sha))
        ncom = c.strip()
        # ⑵ 自前差分 ―― 真の祖先である mac 枝 tip の内、最も近い物からの差分
        best, bestd = None, None
        for bn, bs in tips.items():
            if bs == sha or bn == name:
                continue
            if subprocess.run(['git', 'merge-base', '--is-ancestor', bs, sha]).returncode != 0:
                continue
            rcd, cd = g('rev-list', '--count', '%s..%s' % (bs, sha))
            dd = int(cd.strip() or 0)
            if bestd is None or dd < bestd:
                best, bestd = bn, dd
        if best is None:
            n2, jizen = -1, '測れぬ(祖先 tip 無)'
        else:
            rc2, d2 = g('diff', '--name-only', '%s..%s' % (tips[best], sha))
            f2 = [x for x in d2.split('\n') if x]
            n2 = len(f2)
            jizen = '%s(+%d commit)' % (best, bestd)
            # ★仕分けの軸 ―― 「器」の定義を先に宣する★
            # 器 = 動きに効く物(scripts/ .claude/ .github/ config/ instructions/ agents/ と repo 直下の file)
            # 紙 = docs/ と queue/ の下(証拠・札・報)。紙は消えても system の振舞は変らぬ。
            kigu = [x for x in f2 if _is_kigu(x)]
        areas = sorted({(x.split('/')[0] if '/' in x else x)
                        for x in d1.split('\n') if x})
        if best is None:
            kigu = []
        rows.append([name, sha, str(rc_e), str(n1), str(n2), str(len(kigu)), ncom, jizen,
                     '|'.join(areas), ';'.join(kigu[:12])])

    kaki('raw/10_sokutei.tsv',
         ['eda\tsha\trc_cat_file\ttai_main_files\tjizen_files\tjizen_kigu_files\tcommits\tjizen_moto\tryouiki\tkigu_no_na']
         + ['\t'.join(r) for r in rows])

    # 鎖 ―― 残 45 本の内、tip が他の tip の祖先に成つて居る対
    kusari = []
    for a_sha, a_name in nokori:
        for b_sha, b_name in nokori:
            if a_sha == b_sha:
                continue
            if subprocess.run(['git', 'merge-base', '--is-ancestor', a_sha, b_sha]).returncode == 0:
                kusari.append('%s\t%s' % (a_name, b_name))
    kaki('raw/20_kusari.tsv', ['oya\tko'] + kusari)

    log.append('測つた枝=%d / cat-file rc非零=%d' % (len(rows), sum(1 for r in rows if r[2] != '0')))
    log.append('自前が測れぬ枝=%d' % sum(1 for r in rows if r[4] == '-1'))
    log.append('鎖(祖先→子)の対=%d' % len(kusari))
    log.append('対 main 差分の最小=%d / 最大=%d' % (min(int(r[3]) for r in rows), max(int(r[3]) for r in rows)))
    log.append('自前 差分の最小=%d / 最大=%d' % (min(int(r[4]) for r in rows if r[4] != '-1'),
                                                max(int(r[4]) for r in rows)))
    kou = [r for r in rows if int(r[5]) > 0]
    log.append('★甲(自前に器の変更を含む)=%d / 乙(自前が docs/evidence の紙のみ)=%d★'
               % (len(kou), len(rows) - len(kou)))
    log.append('甲の枝=' + ' '.join(r[0] for r in kou))
    kaki('raw/30_summary.txt', log)
    print('\n'.join(log))

main()

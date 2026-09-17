#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★出目引き直し器★ ―― 10_run の 深(例外) 欄は ValueError|OverflowError|TypeError しか見ず、
time.sleep(4294967295) が上げる ★OSError: [Errno 22]★ を取り落した(當席の疵①)。
∴ 走らせ直さず、raw/<harness>/<label>.suplog を素で読んで引き直す(再走は刻を変へ、証を痩せさす)。

引く物:
  ko_kidou   : 子が起動した回数 ("starting watcher")
  kaiseki    : 子が己の口で言つた stale_sec / poll_sec (解された数)
  reigai     : traceback 最終行 (例外の類と文) ―― ★類を絞らず末行を採る★
  shi_kata   : 落ちた(fail-closed) / 黙つて別の数(silent-coerce) / 素通し(pass) の別
  matsu_ko   : ★子の待ち★  = 子が起動した走で観た呼出間差 (解が在る時のみ意味を持つ)
  matsu_oya  : ★親の再起5s★= 子が即死した走の 5s 前後の差 (子の待ちではない)
"""
import json, pathlib, re, sys

B = pathlib.Path(__file__).resolve().parent.parent
RAW = B / 'raw'

def hiku(kou):
    deme = json.loads((RAW / f'10_deme_{kou}.json').read_text(encoding='utf-8'))
    out = []
    for r in deme:
        d = RAW / kou / r['label']
        sup = pathlib.Path(str(d) + '.suplog')
        s = sup.read_text(encoding='utf-8', errors='replace') if sup.exists() else ''
        # ★類を絞らぬ★: Traceback ブロックの末行を採る
        reigai = None
        tb = re.findall(r'Traceback \(most recent call last\):\n(?:.*\n)*?([A-Za-z_][\w.]*(?:Error|Exception|Exit)[^\n]*)', s)
        if tb:
            reigai = tb[-1].strip()
        kai = re.search(r'stale_sec=(-?\d+) poll_sec=(-?\d+)', s)
        kai = (int(kai.group(1)), int(kai.group(2))) if kai else None
        # 5s ±0.3 の差は親の再起、それ以外は子の待ち
        oya = [x for x in r['sashi'] if abs(x - 5.0) < 0.3]
        ko  = [x for x in r['sashi'] if abs(x - 5.0) >= 0.3]
        if kai is None:
            shi = '落(起動前に死)'
        elif reigai:
            shi = '走り出して落'
        else:
            shi = '通'
        rec = dict(r)
        rec.update(reigai=reigai, kaiseki=kai, shi_kata=shi,
                   matsu_ko=(max(ko) if ko else None),
                   matsu_oya=(max(oya) if oya else None),
                   sup_L=s.count('\n'))
        out.append(rec)
    (RAW / f'20_hikinaoshi_{kou}.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return out

def hyou(kou, out, var):
    L = []
    L.append(f'■ harness {kou} ―― 注ぐ先= {var} / 見るのは子の出目')
    L.append('%-18s %-6s %-22s %-5s %-5s %-4s %-9s %-7s %-14s %s' % (
        '組', '種', '注いだ値(repr)', 'rc', 'outB', 'errL', '子待秒', '親再起', '死に方', '子が言つた解/例外'))
    for r in out:
        atae = r['atae'] if r['atae'] == '<未設定>' else repr(r['atae'])
        kai = '' if r['kaiseki'] is None else 'stale=%d poll=%d' % r['kaiseki']
        rei = r['reigai'] or ''
        L.append('%-18s %-6s %-22s %-5s %-5d %-4d %-9s %-7s %-14s %s' % (
            r['label'], r['tane'], atae,
            ('★時切' if r['kire'] else r['rc']), r['out_B'], r['err_L'],
            ('―' if r['matsu_ko'] is None else r['matsu_ko']),
            ('―' if r['matsu_oya'] is None else r['matsu_oya']),
            r['shi_kata'], (kai + ('  ' + rei if rei else '')).strip()))
    return '\n'.join(L)

if __name__ == '__main__':
    han = {'kou': 'POLL_SEC', 'otsu': 'STALE_SEC', 'hei': 'STALE_SEC'}
    body = []
    for kou in sys.argv[1:]:
        body.append(hyou(kou, hiku(kou), han[kou]))
    t = '\n\n'.join(body) + '\n'
    (RAW / ('20_hyou_' + '_'.join(sys.argv[1:]) + '.txt')).write_text(t, encoding='utf-8')
    print(t)

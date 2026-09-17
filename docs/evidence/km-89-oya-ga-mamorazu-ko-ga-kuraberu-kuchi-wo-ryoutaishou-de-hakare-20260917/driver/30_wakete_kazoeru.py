#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★組を分けて数へる器★ ―― 「通つた組・落ちた組・★黙つて別の数になつた組★」を分けて数へる(㋑)。

分類は ★出目のみ★ から決める(語で決めぬ):
  落_起動前    : 子が己の解(stale_sec=/poll_sec=)を一度も刷らず例外で終つた   … fail-closed
  落_走り出して : 子が解を刷つた後に例外で終つた                              … 半端(名乗つてから死ぬ)
  黙_別の数    : 子の解した數 ≠ 注いだ字面が読める數 (字面通りに読めぬ)        … ★静かな化け★
  黙_危い数    : 子の解した數 = 字面通り、然し閾の意味が壊れる(0/負)           … ★静かな fail-open★
  通          : 子の解した數 = 字面通り、意味も壊れぬ

「字面が読める數」の定義: 人が其の字を見て素直に読む數。
  '010' → 人は八進 8 と読み得る / '３００' → 全角は數字と見えるが int() が受けるとは限らぬ
  ∴ ★人の読みと int() の読みが違ふ組を「黙_別の数」と呼ぶ★。註に人の読みを併記する。
"""
import json, pathlib, sys

B = pathlib.Path(__file__).resolve().parent.parent
RAW = B / 'raw'

# 人の素直な読み (None = 數と読めぬ / 'oct' = 八進と読み得る / int = 其の數)
HITO = {
    '300': 300, '<未設定>': None, '': None, ' ': None, '0': 0, '-1': -1,
    'abc': None, '300abc': None, '010': 8, '+10': 10,
    '4294967295': 4294967295, '4294967296': 4294967296,
    '9223372036854775807': 9223372036854775807,
    '300\n': 300, '3\n0': None, ' 300 ': 300, '1_0': None, '0x10': 16, '３００': 300,
}
KITEI = {'STALE_SEC': 300, 'POLL_SEC': 10}   # 生器が己の註(L13/L14)で宣する既定
TAORERU = ('<未設定>', '')                    # 親の ${VAR:-數} が既定へ倒す入力 = 之の二つ★のみ★
HITO_CHU = {'010': '人は八進 8 と読み得る(shell の [ ] も十進・memory 既知)',
            '0x10': '人は十六進 16 と読む',
            '1_0': '人は數と読まぬ(python の下線區切のみ數)',
            '３００': '★全角數字が int() に通る(人の読み 300 と一致)―― 通る事自体が驚き★',
            '300\n': '尾の改行は目に見えぬ',
            ' 300 ': '前後の空白は目に見えぬ'}

def wakeru(r, var):
    """★分類は出目のみから★。var= 注いだ env 名(既定の値が var で違ふ故に要る)。"""
    kai = r['kaiseki']
    got = None if kai is None else (kai[0] if var == 'STALE_SEC' else kai[1])
    rei = r['reigai']
    if kai is None:
        return '落_起動前', got
    if rei:
        # 解は刷つたが後で死んだ
        return '落_走り出して', got
    if r['atae'] in TAORERU:
        # ★親の ${VAR:-數} が働いた口★ ―― 宣された既定に一致すれば「正しく倒れた」
        return ('既定_正しく倒れた' if got == KITEI[var] else '既定_宣と違ふ数へ倒れた'), got
    hito = HITO[r['atae']]
    if hito is None or (isinstance(hito, int) and hito != got):
        return '黙_別の数', got
    if got is not None and got <= 0:
        return '黙_危い数', got
    return '通', got

def main():
    han = {'kou': 'POLL_SEC', 'otsu': 'STALE_SEC', 'hei': 'STALE_SEC'}
    L, shuukei = [], {}
    for kou in sys.argv[1:]:
        var = han[kou]
        deme = json.loads((RAW / f'20_hikinaoshi_{kou}.json').read_text(encoding='utf-8'))
        L.append(f'■ {kou} (注ぐ先= {var}) ―― 組を出目で分類')
        L.append('%-18s %-22s %-14s %-22s %s' % ('組', '注いだ値(repr)', '★分類★', '子の解', '註'))
        kaz = {}
        for r in deme:
            bun, got = wakeru(r, var)
            kaz[bun] = kaz.get(bun, 0) + 1
            chu = HITO_CHU.get(r['atae'], '')
            if bun == '黙_危い数':
                chu = f'★閾が {got} ―― 意味が壊れる★ ' + chu
            if r['stale_hatsuka']:
                chu = f'★STALE 発火 {r["stale_hatsuka"]} 回(Enter 判定)★ ' + chu
            L.append('%-18s %-22s %-14s %-22s %s' % (
                r['label'], (r['atae'] if r['atae'] == '<未設定>' else repr(r['atae'])),
                bun, ('―' if got is None else got), chu))
        L.append('  ―― 数: ' + ' / '.join(f'{k}={v}' for k, v in sorted(kaz.items())) +
                 f' / 計={sum(kaz.values())} (母數 19 組)')
        L.append('')
        shuukei[kou] = kaz
    t = '\n'.join(L)
    # ★門 條④★ 行毎に尾の空白を落し、EOF 改行を丁度 1 にして出す(printf の詰め物が尾に残るゆゑ)
    t = '\n'.join(l.rstrip() for l in t.split('\n')).rstrip('\n')
    (RAW / '30_wakekazoe.txt').write_text(t + '\n', encoding='utf-8')
    (RAW / '30_wakekazoe.json').write_text(json.dumps(shuukei, ensure_ascii=False, indent=1) + '\n',
                                          encoding='utf-8')
    print(t)

if __name__ == '__main__':
    main()

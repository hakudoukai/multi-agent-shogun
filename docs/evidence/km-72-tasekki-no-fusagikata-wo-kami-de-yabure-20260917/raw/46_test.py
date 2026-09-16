# -*- coding: utf-8 -*-
"""46 `[ "$v" -ge 0 ]` の空白讀み(第72弾)―― /bin/bash 3.2.57 の test が、数の前後の 空白/tab/改行/全角空白/NBSP を許すか(rc 0=真・1=偽・2=讀めぬ)。20 の test_ge0 欄の根。"""
import sys, subprocess, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
V = [('5', '5'), (' 5', '前 空白'), ('5 ', '後 空白'), (' 5 ', '前後 空白'), ('\t5', '前 tab'), ('5\t', '後 tab'), ('\n5', '前 改行'), ('5\n', '後 改行'), ('5\n\n', '後 改行2'), ('\n5\n\n', '前後 改行'), (' 5\n', '前 空白+後 改行'), ('5 \n', '後 空白+改行'), ('　5', '前 全角空白'), ('5　', '後 全角空白'), (' 5', '前 NBSP'), ('+5', '+5'), ('-0', '-0'), ('010', '010'), ('0x10', '0x10'), ('５', '全角５'), ('9223372036854775807', '2^63-1'), ('9223372036854775808', '2^63')]
rows = [(repr(v), lab, subprocess.run(['/bin/bash', '-c', '[ "$1" -ge 0 ] 2>/dev/null', '_', v]).returncode, subprocess.run(['/bin/bash', '-c', '[ 64 -ge "$1" ] 2>/dev/null', '_', v]).returncode) for v, lab in V]
K.kaku_tsv(D + '/raw/46_test.tsv', rows, ['value_repr', 'label', 'rc_[v -ge 0]', 'rc_[64 -ge v]']); K.kaku(D + '/raw/46_test.txt', f'# 46 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / /bin/bash 3.2.57\n' + '\n'.join('\t'.join(map(str, r)) for r in rows)); print(open(D + '/raw/46_test.txt', encoding='utf-8').read())

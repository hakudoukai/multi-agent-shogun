# -*- coding: utf-8 -*-
"""07 箱読み(第72弾で初めて鎖へ入れた段・km-71b 疵①の直し)―― 着手便の後・臺帳の前に己の箱を一度読み、未読の便を id で名指す(既読化はせぬ・鳴れば rc 1 で鎖を止め、席が読む)。"""
import sys, time, yaml
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'
ms = yaml.safe_load(open(M + f'/queue/inbox/{ME}.yaml', encoding='utf-8')).get('messages') or []
un = [m for m in ms if not m.get('read')]
out = [f'# 07 箱読み / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 箱 {M}/queue/inbox/{ME}.yaml / 便 {len(ms)} / 未読 {len(un)}'] + [f'未読 {m["id"]} {m.get("timestamp")} {m.get("type")} {m.get("from")} 字数 {len(str(m.get("content", "")))}' for m in un]
K.kaku(D + '/raw/07_hako.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(1 if un else 0)

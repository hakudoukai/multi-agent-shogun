# -*- coding: utf-8 -*-
"""45 紙を門の形へ(第78弾 km-84)―― README.md を kaki.kaku(行末空白無し・LF・EOF 改行一本)で書き直す。前後の sha16 と bytes を刷る(讀み手の為)。"""
import sys, hashlib, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
p = D + '/README.md'; b = open(p, 'rb').read(); K.kaku(p, b.decode('utf-8')); a = open(p, 'rb').read()
print(f'45 紙を kaki へ / 刻 {time.strftime("%H:%M:%S")} / 前 {hashlib.sha256(b).hexdigest()[:16]} {len(b)}B → 後 {hashlib.sha256(a).hexdigest()[:16]} {len(a)}B / CRLF {b.count(b"\r")}→{a.count(b"\r")} / 行末空白 {sum(1 for l in b.split(b"\n") if l.rstrip() != l)}→{sum(1 for l in a.split(b"\n") if l.rstrip() != l)}')

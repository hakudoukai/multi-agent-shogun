#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""99_hyou.py ―― 測つた TSV 五枚を ★一枚の表★ へ綴ぢる。

㋐㋑㋒ は .nama/ban.tsv(番人へ直に当てた出目)から、
㋓ は .nama/mon_*.tsv(門を端から端まで走らせた出目)から ★引き写さず読み込む★。
㋔ だけは測定ではなく ★己の判★ ゆゑ、此の器の中に逐語で置き、由も併記する。

usage: 99_hyou.py <.nama dir>
rc   : 0=綴ぢた / 2=器の誤り
"""
import io
import os
import sys

# ㋔ ―― ★正しく鳴るべきだつたか★(測定に非ず・判である)
YOTSU = {
    u'㋐01': (u'★正★', u'未設定は既定へ倒し 清い file に鳴らぬ ―― 実測も其の通り'),
    u'㋐02': (u'★正★', u'空文字は既定へ倒す ―― 実測も其の通り'),
    u'㋐03': (u'★正★', u'空白のみは既定へ倒す ―― 実測も其の通り'),
    u'㋐04': (u'★正★', u'同上(TAB)'),
    u'㋐05': (u'★正(但し出目は locale 次第)★', u'判は正。㋑が blank/value に割れる ―― locale.tsv'),
    u'㋐06': (u'★否 ―― 拒むべき★', u'負の MB/byte/秒は閾として意味を成さぬ。実測=受けた'),
    u'㋐07': (u'★否 ―― 拒むべき★', u'「-0」も同じ。実測=受けた'),
    u'㋐08': (u'★半★', u'寸法閾なら受けてよく鳴るのが正／★時限閾では拒むべき(0=時限無し)★'),
    u'㋐09': (u'★正★', u'50 と読んで通が正 ―― 四閾とも其の通り'),
    u'㋐10': (u'★正 ―― 50 と読むべき★', u'g4 二閾と MAXB は正。★時限だけ全 file 測れぬ★'),
    u'㋐11': (u'★否 ―― 拒むは正だが刷り方が疵★', u'拒む判は正。★逐語を刷る故 門票へ行が入る★'),
    u'㋐12': (u'★否 ―― 同上★', u'同上(改行が中に在る)'),
    u'㋐13': (u'★正★', u'全角数字を拒むは正'),
    u'㋐14': (u'★正★', u'[ ] は十六進を読まぬ ―― 拒むが正'),
    u'㋐15': (u'★正★', u'八進の字面を拒むが正'),
    u'㋐16': (u'★正★', u'7 と読む。g4 は 0MB≤7 で通・MAXB は 16>7 で鳴る ―― 双方正'),
    u'㋐17': (u'★正(但し黙つて十進)★', u'[ ] は 010 を 10 と読む。八進の 8 を書いた者へは黙る'),
    u'㋐18': (u'★半★', u'寸法閾なら無害／★時限としては事実上 無限 ―― 上限を設くべき★'),
    u'㋐19': (u'★正★', u'2^63 は strtoimax が溢れる ―― 拒むが正'),
    u'㋐20': (u'★正★', u'極長桁も同じく拒むが正'),
    u'㋐21': (u'★否 ―― 受けるべき★', u'★10m は timeout(1) の正しい語法。正しい値を拒んで居る★'),
    u'㋐22': (u'―', u'env に載らぬ ―― 番人の手前で消える'),
    u'㋐23': (u'★否★', u'bash は後・getenv は前を取る ―― ★讀む器で値が違ふ★'),
}

MON = [(u'mon_gate4_maxf.tsv', u'㋓g4 MAXF'),
       (u'mon_gate4_maxt.tsv', u'㋓g4 MAXT'),
       (u'mon_dasumae_tmo.tsv', u'㋓ds TMO'),
       (u'mon_dasumae_max.tsv', u'㋓ds MAXB')]


def yomu(p):
    """TSV を 形頭(㋐NN) -> 行 の辞書にする。# は註ゆゑ落す。"""
    d = {}
    if not os.path.isfile(p):
        return d
    for ln in io.open(p, encoding='utf-8'):
        ln = ln.rstrip(u'\n')
        if not ln or ln.startswith(u'#') or ln.startswith(u'形\t'):
            continue
        c = ln.split(u'\t')
        d[c[0][:3]] = c
    return d


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(u'usage: 99_hyou.py <.nama dir>\n')
        return 2
    nama = argv[1]
    ban = yomu(os.path.join(nama, u'ban.tsv'))
    mon = [(lbl, yomu(os.path.join(nama, f))) for f, lbl in MON]
    out = []
    atama = [u'形', u'㋐逐語', u'㋐byte 列', u'㋑env_state', u'㋒rc'] + [l for l, _ in mon] + [u'㋔正しく鳴るべきだつたか']
    out.append(u'| ' + u' | '.join(atama) + u' |')
    out.append(u'|' + u'---|' * len(atama))
    for k in sorted(ban):
        c = ban[k]
        chiku = c[1].replace(u'|', u'\\|')
        byt = c[2]
        if len(byt) > 46:
            byt = byt[:46] + u'…'
        gyou = [c[0], chiku if len(chiku) <= 46 else chiku[:46] + u'…', byt, c[3], c[4]]
        for lbl, d in mon:
            r = d.get(k)
            if not r:
                gyou.append(u'―')
            elif r[1] == u'―':
                gyou.append(u'★測れぬ★')
            else:
                gyou.append((u'★鳴 rc=%s★' if r[2].startswith(u'★') else u'通 rc=%s') % r[1])
        y = YOTSU.get(k, (u'?', u''))
        gyou.append(y[0] + (u' ―― ' + y[1] if y[1] else u''))
        out.append(u'| ' + u' | '.join(gyou) + u' |')
    sys.stdout.write(u'\n'.join(out) + u'\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

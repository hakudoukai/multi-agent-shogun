#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★員外の宣を ★臺帳 grep★ で作る器★(命三・第54弾)

疵の由来: 第53弾で當席は員外を ★手で三本挙げ★、其の三本は悉く臺帳の中に在り(行9/10/11)、
真の員外 二十一本を落とした。∴ ★手で挙げるな。臺帳を讀め。★

使ひ方: 10_ingai.py <束根> <臺帳path> [己の出目(束内相対)...]
  束根   : 歩く根。臺帳の path は ★束内相対★(裁 seq322699)ゆゑ、根が違へば悉く外れる。
  己の出目: 本器が生む紙。★己を「発見」と数へぬ為に、名指しで除く★(除くのでなく ★別欄で宣する★)。
出目: TSV を stdout へ。判定・數は stderr へ。
"""
import os, re, sys, stat, datetime

ROW = re.compile(r'^path=(.*) sha256=([0-9a-f]{64}) bytes=(\d+) lines=(-?\d+)$')

def daichou(p):
    """臺帳から path を引く。★三形を受ける★(裸 / "括り" / 冠行は捨てる)。"""
    kari, nama, kanmuri, hakei = [], [], 0, 0
    for ln in open(p, encoding='utf-8').read().split('\n'):
        if not ln: continue
        if ln.startswith('#'): kanmuri += 1; continue
        m = ROW.match(ln)
        if not m: hakei += 1; continue
        v = m.group(1)
        if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
            kari.append(v[1:-1])
        else:
            nama.append(v)
    return nama, kari, kanmuri, hakei

def aruku(root):
    """disk を歩く。★S_ISREG のみ数へる★ ―― FIFO を open すれば「止」に成る(實測 km-64)。"""
    jou, hijou = [], []
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x != '__pycache__']
        for f in fs:
            ap = os.path.join(d, f)
            rp = os.path.relpath(ap, root)
            try: st = os.lstat(ap)
            except OSError: hijou.append((rp, 'lstat 不能')); continue
            if stat.S_ISREG(st.st_mode): jou.append(rp)
            else: hijou.append((rp, stat.filemode(st.st_mode)))
    return sorted(jou), sorted(hijou)

def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__); return 2
    root, man = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    jibun = set(sys.argv[3:])
    koku = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    nama, kari, kanmuri, hakei = daichou(man)
    dai = set(nama) | set(kari)
    jou, hijou = aruku(root)
    disk = set(jou)

    ingai   = sorted(disk - dai)          # disk に在り 臺帳に無し
    jittai  = sorted(dai - disk)          # 臺帳に在り disk に無し(実体無)
    ingai_ta = [x for x in ingai if x not in jibun]
    ingai_ji = [x for x in ingai if x in jibun]

    def hyouji(s):
        """★行注入封じ(形12)★: 改行/復帰/TAB を可視印へ均す ―― ★表示のみ・判定不変★。
        TSV は改行で行を、TAB で欄を割る。∴ 名に其の三字が在れば
        ★閉ぢの一字まで本物と違はぬ偽の行★ を立てられる。可視印は多byteゆゑ
        tr では置けぬ(BSD tr は byte 器・\266 は生 byte 0xB6 を吐く。實測 2026-09-17)。
        str.translate は codepoint 器ゆゑ ★UTF-8 として正しい★ 印が置ける。"""
        return s.translate({0x0a: '␊', 0x0d: '␍', 0x09: '␉'})

    w = sys.stdout.write
    w('刻\t%s\n' % koku)
    w('根\t%s\n' % hyouji(root))
    w('臺帳\t%s\n' % hyouji(os.path.relpath(man, root)))
    w('#\t欄: 別\tpath\t註\n')
    for p in ingai_ta: w('員外(他)\t%s\t―\n' % hyouji(p))
    for p in ingai_ji: w('員外(己)\t%s\t★本器が生む紙・名指しで宣す★\n' % hyouji(p))
    for p in jittai:   w('実体無\t%s\t★臺帳に在り disk に無し★\n' % hyouji(p))
    for p, m in hijou: w('非常体\t%s\t%s\n' % (hyouji(p), m))
    if not (ingai or jittai or hijou):
        w('―\t★空である旨★ 員外・実体無・非常体 いづれも0\t―\n')

    e = sys.stderr.write
    e('刻=%s\n' % koku)
    e('臺帳: 冠=%d 行(path=)=%d 内 裸=%d 括り=%d 破形=%d\n'
      % (kanmuri, len(dai), len(nama), len(kari), hakei))
    e('disk: 常体=%d 非常体=%d\n' % (len(jou), len(hijou)))
    e('★員外=%d(他=%d 己=%d) 実体無=%d★\n'
      % (len(ingai), len(ingai_ta), len(ingai_ji), len(jittai)))
    e('恆等: disk常体 %d = 臺帳∩disk %d + 員外 %d → %s\n'
      % (len(jou), len(dai & disk), len(ingai),
         '★合ふ★' if len(jou) == len(dai & disk) + len(ingai) else '★合はぬ★'))
    return 0

sys.exit(main())

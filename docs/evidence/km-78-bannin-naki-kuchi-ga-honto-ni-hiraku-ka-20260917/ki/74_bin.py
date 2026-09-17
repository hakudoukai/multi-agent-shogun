# -*- coding: utf-8 -*-
"""74 便を組む器 ―― ★番は器が振る。手で打たぬ(第55弾の疵)★ / 300字が條・100字が的"""
import io, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw'))
import kaki as K
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HON = [
 '★甲は結論のみ立つ。機構も境も偽。★二十桁はrc=2に非ず ―― read -t が時計を組まず即返る ∴ 時限切れが存在せぬ。境は20桁でなく2^63(19桁)。報せ落ちは起きるが、hookは併せて stdin を捨て INPUT_len=0 で黙つて進む(見立に無し)。',
 '★乙 立つ★(字の比べ・rc=2に成らず)。★丙 破れた ―― 四名悉く測れる★: ER_THRESHOLD_MIN=番人在(file跨ぎ) / STALE_SEC・POLL_SEC=python が int() で受け落ちる=fail-closed で騒がしい / DETECT_STALE_STALE_SEC のみ★死口★(讀む者無し)=本弾唯一の③。',
 '㋐八形×口を測つた。★40(比較器の法)と41(口の法)は別物★ ―― ${N:-D} は未設定と空を既定へ倒す ∴ 番人無き口でも其の二形は既に守られ、開くのは 空白のみ/二十桁/改行入り/既存␊ の★四形★。㋑札=①35 ②45 ③1、計81=母數(排他)。',
 '★走行中に当てられた直しは八形を悉く塞いだ(善)。然れど num_same_op は2^63未満を皆「數」と呼ぶ★ ∴ 4294967295=136年待つ・4294967296=即返る・-5=0秒で「時限切れ(-5秒経過)」と★偽の報せ★。且つ註釈は「永久に待つ」と書くが二十桁は待たぬ。塞いで居らぬ穴の名を書いて居る。',
 '㋔序1=★scripts/stop_hook_inbox.sh UNREAD_COUNT★(口5本・内生=命令の出目・抜けるは報せ ∴ 気付く路無し)。「全部直せ」は書かぬ。★但し此のfileは本弾中に二度書き換はつた ―― 直すなら版を凍結してから。★門(gate4/dasumae)も動いた。',
 '㋕意味せぬ事七つ(紙)。㋖★宣28分⇔實52分24秒=1.87倍 過小★ ―― 55の3.63倍 過大から引き直し、今度は反対へ外れた。刻を決めるのは弾の大きさでなく★己の器が何度倒れるか★で、宣の前に測れぬ。次弾は幅で宣する。疵14件は紙に全て。門控は_gate/員外。生器へ書いた字=0。',
]
N = len(HON)
out = []
for i, h in enumerate(HON, 1):
    atama = '納め%d/%d ' % (i, N)
    b = atama + h
    n = len(b)
    assert n <= 300, '★%d/%d が %d字 ―― 條300を超えた★' % (i, N, n)
    out.append(b)
    K.kaku(B + '/_bin/%02d.txt' % i, b)
rec = ['# 74 便 ―― 番は器が振つた(N=%d)' % N, '']
for i, b in enumerate(out, 1):
    rec.append('%d/%d  %d字  %s' % (i, N, len(b), b))
rec.append('')
rec.append('★條=300字 / 的=100字。最長=%d字 / 最短=%d字★' % (max(len(x) for x in out), min(len(x) for x in out)))
rec.append('★番の検め★: 頭の「納め<i>/<N>」は i を loop が振り N=len(本文) ―― 手で打つて居らぬ。')
K.kaku(B + '/raw/74_bin.txt', '\n'.join(rec))
print('\n'.join('%d/%d %d字' % (i, N, len(b)) for i, b in enumerate(out, 1)))

# -*- coding: utf-8 -*-
"""73 宣⇔實 ―― ★端点を先に定めてから引く★(第55弾の教訓)"""
import io, os, sys, datetime, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw'))
import kaki as K
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAKU = '2026-09-17T09:32:29'   # 着手便 自身の timestamp(queue/inbox/karo-mac.yaml)
SEN_MIN = 28
now = datetime.datetime.now().replace(microsecond=0)
t0 = datetime.datetime.strptime(CHAKU, '%Y-%m-%dT%H:%M:%S')
jitsu = (now - t0).total_seconds()
sen = SEN_MIN * 60
o = []
o.append('# 73 宣⇔實')
o.append('端点 = ★着手便自身の timestamp → 本器を走らせた刻★')
o.append('  (納め1/N の timestamp は ★本器より後★ ゆゑ用ゐられぬ。∴ 端点を一つ手前へ寄せた。')
o.append('   之を明記せぬと 第55弾の如く ★端点の定義で符号が反る★)')
o.append('')
o.append('着手便      %s' % CHAKU)
o.append('本器の刻    %s' % now.strftime('%Y-%m-%dT%H:%M:%S'))
o.append('宣          %d分00秒 (=%d秒)' % (SEN_MIN, sen))
o.append('實          %d分%02d秒 (=%d秒)' % (int(jitsu // 60), int(jitsu % 60), int(jitsu)))
hi = jitsu / sen
o.append('')
o.append('★實 ÷ 宣 = %.2f倍★' % hi)
o.append('向き = %s' % ('★過小(宣より長く掛かつた)★' if hi > 1 else '過大(宣より早く終つた)'))
o.append('')
o.append('第55弾 = 宣75分56秒 ⇔ 實20分56秒 = ★3.63倍 過大★')
o.append('第56弾 = 宣28分00秒 ⇔ 實%d分%02d秒 = ★%.2f倍 %s★'
         % (int(jitsu // 60), int(jitsu % 60), hi if hi > 1 else 1 / hi,
            '過小' if hi > 1 else '過大'))
o.append('')
o.append('★∴ 前弾の比で引き直した宣は、今度は反対側へ外れた。★')
K.kaku(B + '/raw/73_sen.txt', '\n'.join(o))
print('\n'.join(o[-8:]))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""95_futatabi.py ―― ★env に同名を二度★ 置いた時、讀む器で値が違ふかを測る。

由來: 第49弾の的「env に同名を二度」。shell の `export A=1; export A=2` では
      environ に一本しか残らぬ故、★生の execve★ で二本置いて測る。

usage: 95_futatabi.py <出し先.txt>
rc   : 0=測れた / 2=器の誤り
★讀取のみ。生器へ一字も書かぬ。★
"""
import ctypes
import os
import sys

ENV = [b'KM49_V=1', b'KM49_V=99999', b'PATH=/usr/bin:/bin']


def hashiru(argv):
    """生の environ(同名二本)で argv を execve し、其の stdout を返す。"""
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r); os.dup2(w, 1); os.dup2(w, 2)
        libc = ctypes.CDLL(None)
        A = (ctypes.c_char_p * (len(argv) + 1))(*(argv + [None]))
        E = (ctypes.c_char_p * (len(ENV) + 1))(*(ENV + [None]))
        libc.execve(argv[0], A, E)
        os._exit(127)
    os.close(w)
    s = os.read(r, 8192).decode('utf-8', 'replace')
    os.close(r); os.waitpid(pid, 0)
    return s.strip()


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        return 2
    gyou = []
    gyou.append('# env に同名を二度 ―― 讀む器で値が違ふか')
    gyou.append('# 置いた environ = KM49_V=1 / KM49_V=99999 (此の順・生の execve)')
    gyou.append('讀む器\t出た値\t註')
    b = hashiru([b'/bin/bash', b'-c', b'printf %s "$KM49_V"'])
    p = hashiru([b'/usr/bin/printenv', b'KM49_V'])
    e = hashiru([b'/usr/bin/env']).replace('\n', ' | ')
    gyou.append('bash ${KM49_V}\t%s\t★門は bash ―― 門が見るのは此方★' % b)
    gyou.append('printenv(getenv)\t%s\t★C の getenv は先頭を取る★' % p)
    gyou.append('env(environ 全覧)\t%s\t二本とも残つて居る' % e)
    han = '★同じ env が讀む器で二つの値を持つ★' if b != p else '両器 一致(差無し)'
    gyou.append('# 判 = %s' % han)
    with open(argv[1], 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(gyou) + '\n')
    print('\n'.join(gyou))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

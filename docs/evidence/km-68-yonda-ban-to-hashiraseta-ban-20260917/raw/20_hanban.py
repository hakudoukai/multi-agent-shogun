# -*- coding: utf-8 -*-
"""版刻器 20(第68弾・㋐)―― ★讀んだ版と走らせた版が違へば、行番号は正しい顔をして嘘を吐く。★
走らせる★直前★に、走らせる実体の ⑴ realpath ⑵ sha256 先頭16 ⑶ 総行数(grep -c '' 相当)⑷ git blob(hash-object)と HEAD の blob の異同 ⑸ 指す行番号の★其の実体の★本文 を刷り、
⑴〜⑸ を繋いだ正準文字列の sha16 を ★版札v1★ の封として末尾に刷る(專任3 71_yotsu.py の四数札と同じ形 ―― 抜き書きすれば封が合はぬ)。
--against <別の版> は同じ行番号を別の版に当て、本文が違ふ事を並べる(嘘の顔を見せる)。
★構造で塞ぐ★: load(path) は file を ★一度だけ bytes で讀み★、其の bytes を compile して module にし、同じ bytes を行に割つて返す。
∴ 行番号 → 本文 の引き当ては、走らせた bytes 其の物から行はれる。讀む物と走らせる物が同一物ゆゑ、食ひ違ふ余地が無い。
使ひ方: 20_hanban.py <実体> [--lines 133,139,152,158,160] [--against <別の版>] [--out <kaki 出し先>]
返り値: 0 = 刷れた / 2 = 実体が無い・讀めぬ"""
import os, sys, hashlib, subprocess, types, time

def kazoe_gyou(b):
    n = b.count(b'\n')
    if b and not b.endswith(b'\n'): n += 1
    return n

def git_blob(path):
    """hash-object(disk の bytes)と HEAD の blob(其の path の commit 済の版)。repo 外なら '-'。"""
    d = os.path.dirname(path)
    try:
        top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, cwd=d)
        if top.returncode != 0: return '-', '-', 'repo外'
        top = top.stdout.strip(); rel = os.path.relpath(path, top)
        ho = subprocess.run(['git', 'hash-object', '--', path], capture_output=True, text=True, cwd=top).stdout.strip()
        hd = subprocess.run(['git', 'rev-parse', '-q', '--verify', f'HEAD:{rel}'], capture_output=True, text=True, cwd=top)
        hb = hd.stdout.strip() if hd.returncode == 0 else '(HEAD に無い)'
        br = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, cwd=top).stdout.strip()
        return ho[:16], (hb[:16] if hb.startswith('(') is False else hb), ('同じ=commit 済' if ho == hb else '★違ふ=汚れて居る(disk ≠ HEAD)★') + f' 枝 {br} 根 {top}'
    except Exception as e:
        return '-', '-', f'git 測れぬ {e.__class__.__name__}'

class Han:
    """走らせる実体の版。bytes は一度だけ讀む。"""
    def __init__(self, path):
        self.path = os.path.realpath(path)
        self.b = open(self.path, 'rb').read()           # ★此の bytes だけが走り、此の bytes だけが讀まれる★
        self.sha16 = hashlib.sha256(self.b).hexdigest()[:16]
        self.gyou = kazoe_gyou(self.b)
        self.lines = self.b.decode('utf-8', 'replace').split('\n')
        self.mtime = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.stat(self.path).st_mtime))
        self.blob, self.head, self.dirty = git_blob(self.path)
        self._mod = None
    def line(self, n):
        if 1 <= n <= len(self.lines): return self.lines[n - 1]
        return f'★{n} 行目は無い(総行数 {self.gyou})★'
    def module(self, name='han_mod'):
        """★同じ bytes★ を compile して module にする(import でなく exec ―― path から二度讀まぬ)。co_filename は realpath ゆゑ settrace は此の path で当たる。"""
        if self._mod is None:
            code = compile(self.b, self.path, 'exec')
            m = types.ModuleType(name); m.__file__ = self.path
            exec(code, m.__dict__); self._mod = m
        return self._mod
    def fuda(self, nums=()):
        parts = [f'path={self.path}', f'sha16={self.sha16}', f'lines={self.gyou}', f'blob={self.blob}', f'head={self.head}']
        for n in nums: parts.append(f'L{n}={self.line(n).strip()}')
        canon = '版札v1|' + '|'.join(parts); fu = hashlib.sha256(canon.encode('utf-8')).hexdigest()[:16]
        return canon, fu

def sono_mae_ni(path, nums=(), against=None):
    """★走らせる直前に刷る★ ―― 版札の行を返す(呼ぶ側が刷る)。"""
    h = Han(path); canon, fu = h.fuda(nums)
    out = [f'★版刻(走らせる直前)★ realpath {h.path}', f'  sha16 {h.sha16} / 総行数 {h.gyou} / mtime {h.mtime} / git blob {h.blob} vs HEAD {h.head} → {h.dirty}']
    for n in nums: out.append(f'  L{n}: {h.line(n).rstrip()}')
    out.append(f'版札v1 sha16={h.sha16} lines={h.gyou} blob={h.blob} head={h.head} 行={",".join(str(n) for n in nums) or "-"} 封={fu}')
    if against:
        g = Han(against); out.append(f'--against(別の版) {g.path} sha16 {g.sha16} / 総行数 {g.gyou} / {g.dirty}')
        for n in nums:
            a, b = h.line(n).rstrip(), g.line(n).rstrip()
            out.append(f'  L{n}: {"同じ" if a == b else "★違ふ★"} | 別の版: {b}')
    return h, out

if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv: sys.stderr.write('★測れぬ: 実体の path を argv で渡せ★\n'); sys.exit(2)
    path = argv[0]; nums = []; against = None; outp = None
    i = 1
    while i < len(argv):
        if argv[i] == '--lines': nums = [int(x) for x in argv[i + 1].split(',') if x]; i += 2
        elif argv[i] == '--against': against = argv[i + 1]; i += 2
        elif argv[i] == '--out': outp = argv[i + 1]; i += 2
        else: sys.stderr.write(f'★知らぬ口 {argv[i]}★\n'); sys.exit(2)
    if not os.path.isfile(path): sys.stderr.write(f'★測れぬ: 実体が無い {path}★\n'); sys.exit(2)
    h, out = sono_mae_ni(path, nums, against)
    text = '\n'.join(out); print(text)
    if outp:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import kaki as K; K.kaku(outp, text)
    sys.exit(0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★km-89 両対照 走らせ器★ ―― 注ぐのは親の env、見るのは★子の出目★。

的 = scripts/pane_enter_watcher_supervisor.sh (寫し utsushi/)。
生器へは一字も書かぬ。実在 pane にも触れぬ (stub tmux / stub flock)。

出目4欄:
  rc       … 寫し supervisor の終了 rc
  out_B    … driver が捕へた stdout の byte 数
  err_L    … driver が捕へた stderr の行数 (supervisor の log() は tee -a >&2 ゆゑ此処へ来る)
  matsu_s  … ★子が実際に何秒待つたか★ = stub tmux の display-message 呼出間のミリ秒差の最大

三つの harness:
  甲 POLL 実待ち : MAX_OK=2 (子の loop を 2 周で止める) → sleep は丁度 1 回 → matsu_s = poll の実測
  乙 STALE 発火  : MAX_OK=5, POLL_SEC=1 → 3〜4 周廻し、STALE 発火(Enter 判定)が出るか否かを見る
  丙 死 loop     : MAX_OK=999 (pane 永在) → 子が即死する毒で supervisor が 5 秒毎に何度起し直すか
"""
import json, os, pathlib, re, subprocess, sys, time

B = pathlib.Path(__file__).resolve().parent.parent
U = B / 'utsushi'
RAW = B / 'raw'
RAW.mkdir(exist_ok=True)
SUP = U / 'pane_enter_watcher_supervisor.sh'

# ―― 贋 pane 全文 (claude TUI 入力欄の枠線構造・未送信テキスト在り) ――
PANE_TEXT = RAW / '00_nise_pane.txt'
PANE_TEXT.write_text(
    "some output line\n"
    "another line\n"
    "╭──────────────────────────────╮\n"
    "│ > km-89 未送信テキスト(贋)    │\n"
    "╰──────────────────────────────╯\n", encoding='utf-8')

# ―― 組 (label, 値, 種) ―― 種: 陰性 / 陽性(札の12本) / 陽性追加
NONE = object()   # 未設定
KUMI = [
    ('陰性_正常300_10',      '300',                    '陰性'),
    ('陰性_未設定',           NONE,                     '陰性'),
    ('陽性_空',              '',                       '陽性'),
    ('陽性_空白のみ',         ' ',                      '陽性'),
    ('陽性_0',               '0',                      '陽性'),
    ('陽性_-1',              '-1',                     '陽性'),
    ('陽性_abc',             'abc',                    '陽性'),
    ('陽性_300abc',          '300abc',                 '陽性'),
    ('陽性_010',             '010',                    '陽性'),
    ('陽性_+10',             '+10',                    '陽性'),
    ('陽性_4294967295',      '4294967295',             '陽性'),
    ('陽性_4294967296',      '4294967296',             '陽性'),
    ('陽性_2p63m1',          '9223372036854775807',    '陽性'),
    ('陽性_改行尾',           '300\n',                  '陽性'),
    # ―― 以下は札に無いが同じ受け口を突く追加の陽性 (己の判断で足した・宣す) ――
    ('追加_改行中',           '3\n0',                   '陽性追加'),
    ('追加_前後空白',         ' 300 ',                  '陽性追加'),
    ('追加_下線',            '1_0',                     '陽性追加'),
    ('追加_0x10',            '0x10',                   '陽性追加'),
    ('追加_全角300',          '３００',                  '陽性追加'),
]

def hitosou(kou, label, val, tane, *, var, fixed, max_ok, timeout, extra_env=None):
    """一走 = 寫し supervisor を一度起し、出目4欄を刻む。"""
    tag = f'{kou}_{label}'
    d = RAW / kou
    d.mkdir(exist_ok=True)
    env = dict(os.environ)
    env['PATH'] = str(U / 'stub_bin') + os.pathsep + env['PATH']
    env['KM89_STATE']      = str(d / f'{label}.state')
    env['KM89_TMUX_LOG']   = str(d / f'{label}.tmuxlog')
    env['KM89_PANE_TEXT']  = str(PANE_TEXT)
    env['KM89_MAX_OK']     = str(max_ok)
    env['KM89_LOCKFILE']   = str(d / f'{label}.lock')
    env['KM89_SUP_LOG']    = str(d / f'{label}.suplog')
    env['KM89_CHILD_LOG']  = str(d / f'{label}.childlog')
    env['LIVE'] = '0'                      # ★DRY-RUN 固定★ 実 Enter は一度も打たぬ
    for k in ('STALE_SEC', 'POLL_SEC'):
        env.pop(k, None)
    for k, v in (fixed or {}).items():
        env[k] = v
    if val is not NONE:
        env[var] = val
    for f in (env['KM89_STATE'], env['KM89_TMUX_LOG'], env['KM89_SUP_LOG'], env['KM89_CHILD_LOG']):
        pathlib.Path(f).unlink(missing_ok=True)

    t0 = time.monotonic()
    try:
        r = subprocess.run(['/bin/bash', str(SUP)], env=env, capture_output=True, timeout=timeout)
        rc, out, err, kire = r.returncode, r.stdout, r.stderr, False
    except subprocess.TimeoutExpired as e:
        rc, out, err, kire = None, e.stdout or b'', e.stderr or b'', True
    wall = time.monotonic() - t0

    # ★子が実際に何秒待つたか★ = display-message 呼出間の差の最大
    matsu, sashi = None, []
    tl = pathlib.Path(env['KM89_TMUX_LOG'])
    if tl.exists():
        ts = [float(m.group(1)) for m in
              re.finditer(r'^([0-9.]+) argv=display-message', tl.read_text(encoding='utf-8', errors='replace'), re.M)]
        sashi = [round(b - a, 3) for a, b in zip(ts, ts[1:])]
        if sashi:
            matsu = max(sashi)

    sup = pathlib.Path(env['KM89_SUP_LOG'])
    supt = sup.read_text(encoding='utf-8', errors='replace') if sup.exists() else ''
    (d / f'{label}.stdout').write_bytes(out)
    (d / f'{label}.stderr').write_bytes(err)

    rec = dict(
        kou=kou, label=label, tane=tane, var=var,
        atae=('<未設定>' if val is NONE else val), fixed=fixed or {},
        rc=rc, kire=kire, out_B=len(out), err_L=err.count(b'\n'),
        matsu_s=matsu, sashi=sashi, wall_s=round(wall, 3),
        kosu_kidou=len(re.findall(r'starting watcher', supt)),
        kosu_shusshi=len(re.findall(r'watcher exited rc=', supt)),
        ko_rc=[int(x) for x in re.findall(r'watcher exited rc=(-?\d+)', supt)],
        stale_hatsuka=len(re.findall(r'STALE detected', supt)),
        dryrun=len(re.findall(r'\[DRY-RUN\]', supt)),
        traceback=('Traceback (most recent call last)' in supt),
        shinkoku=(re.search(r'(ValueError|OverflowError|TypeError)[^\n]*', supt).group(0)
                  if re.search(r'(ValueError|OverflowError|TypeError)', supt) else None),
        kaiseki=(re.search(r'stale_sec=(-?\d+) poll_sec=(-?\d+)', supt).groups()
                 if re.search(r'stale_sec=(-?\d+) poll_sec=(-?\d+)', supt) else None),
        sendkeys=len(re.findall(r'SEND-KEYS', tl.read_text(encoding='utf-8', errors='replace') if tl.exists() else '')),
    )
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    return rec

def main():
    kou = sys.argv[1]
    deme = []
    for label, val, tane in KUMI:
        if kou == 'kou':      # 甲 = POLL の実待ち
            deme.append(hitosou(kou, label, val, tane, var='POLL_SEC',
                                fixed={}, max_ok=2, timeout=20))
        elif kou == 'otsu':   # 乙 = STALE の発火
            deme.append(hitosou(kou, label, val, tane, var='STALE_SEC',
                                fixed={'POLL_SEC': '1'}, max_ok=5, timeout=20))
        elif kou == 'hei':    # 丙 = 死 loop (pane 永在)
            deme.append(hitosou(kou, label, val, tane, var='STALE_SEC',
                                fixed={'POLL_SEC': '1'}, max_ok=999, timeout=12))
        else:
            raise SystemExit(f'★知らぬ harness: {kou}★')
    (RAW / f'10_deme_{kou}.json').write_text(
        json.dumps(deme, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'★{kou} 了 {len(deme)} 組★', file=sys.stderr)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_hooks_from_rev.py <rev> ―― 或る rev の .claude/settings.json から hook の command を
★json で★ 取り出す(字面 grep で数へぬ)。TSV を stdout・数と寸法を stderr へ。
argv から rev を取る(裁: 器は的を argv から取れ)。"""
import sys, json, hashlib, subprocess

def main():
    if len(sys.argv) != 2:
        sys.stderr.write('usage: 12_hooks_from_file.py <path>\n'); return 2
    rev = sys.argv[1]
    p = subprocess.run(['cat', rev],
                       capture_output=True)
    if p.returncode != 0:
        sys.stderr.write('★git show 落つ rc=%d★ %s\n' % (p.returncode, p.stderr.decode('utf-8','replace')))
        return 3
    raw = p.stdout
    sys.stderr.write('rev=%s byte=%d 行(改行数)=%d sha256=%s\n'
                     % (rev, len(raw), raw.count(b'\n'), hashlib.sha256(raw).hexdigest()))
    try:
        d = json.loads(raw.decode('utf-8'))
    except Exception as e:
        sys.stderr.write('★json 讀めず★ %r\n' % (e,)); return 4
    hooks = d.get('hooks')
    if hooks is None:
        sys.stderr.write('★hooks 鍵 無し(母數=0)★\n'); print_hdr(); return 0
    print_hdr()
    n = 0
    events = {}
    for ev in sorted(hooks.keys()):
        groups = hooks[ev]
        if not isinstance(groups, list):
            sys.stderr.write('★%s の値が list に非ず(%s)★\n' % (ev, type(groups).__name__)); continue
        for gi, g in enumerate(groups):
            matcher = g.get('matcher', '') if isinstance(g, dict) else ''
            hl = g.get('hooks', []) if isinstance(g, dict) else []
            for hi, h in enumerate(hl):
                typ = h.get('type', '') if isinstance(h, dict) else ''
                cmd = h.get('command', '') if isinstance(h, dict) else ''
                n += 1
                events[ev] = events.get(ev, 0) + 1
                # command は改行を含み得る ―― 行單位の器を壊さぬやう可視印へ
                vis = cmd.replace('\t', '␉').replace('\r', '␍').replace('\n', '␊')
                print('%d\t%s\t%d\t%d\t%s\t%s\t%s' % (n, ev, gi, hi, matcher, typ, vis))
    sys.stderr.write('★母數(hook の command 本数)=%d★\n' % n)
    for ev in sorted(events):
        sys.stderr.write('  event %s = %d 本\n' % (ev, events[ev]))
    return 0

def print_hdr():
    print('#no\tevent\tgroup\tidx\tmatcher\ttype\tcommand(␊␍␉=可視印)')

sys.exit(main())

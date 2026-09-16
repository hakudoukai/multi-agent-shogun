#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 61_ate.py -- ★讀手 paths_of への最小の直し★ を BEFORE から機械で作る器(手書き禁)。
# 使ひ方: 61_ate.py <BEFORE.py> <AFTER.py>
import io, sys
src, dst = sys.argv[1], sys.argv[2]
s = io.open(src, encoding='utf-8').read()
lines = s.split(u'\n')
i = lines.index(u'    out = []')
j = i + 1
assert lines[j].startswith(u'    line = line.replace('), lines[j]
ins = [
 u'    # \u2605km-46(2026-09-17) \u2460\u306e\u524d\u3078 \u2605\u6700\u53f3\u306e sha256=<64hex> \u307e\u3067 \u8caa\u6b32\u306b\u53d6\u308b\u2605 \u5019\u88dc\u3092\u7f6e\u304f\u2605',
 u'    #   \u56e0: \u2460 path=([^\\s"\\\']+) \u306f \u2605\u540d\u306e\u4e2d\u306e\u7a7a\u767d\u3067\u5207\u308b\u2605\u3002',
 u'    #       \u2461\u975e\u8caa\u6b32\u306f \u2605\u2460\u304c\u5916\u308c\u305f\u6642\u306b\u306e\u307f\u2605 \u8d70\u308a\u3001\u4e14 \u2605\u540d\u306e\u4e2d\u306e ` sha256=` \u3067\u5148\u306b\u6b62\u308b\u2605\u3002',
 u'    #       (\u5be6\u6e2c 2026-09-17 km-45: \u540d\u306b ` sha256=deadbeef ` \u3092\u542b\u3080 3 \u672c\u304c \u5b9f\u4f53\u7121\u3002\u4e09\u672c\u3068\u3082 disk \u306b\u5728\u3063\u305f\u3002)',
 u'    #   \u2605\u68af\u5b50\u306f\u58ca\u3055\u306c\u2605 \u2015\u2015 \u5148\u982d\u3078 \u7a4d\u3080\u4e38\u3051\u3002\u8caa\u6b32\u5019\u88dc\u304c disk \u306b\u7121\u304f\u3070',
 u'    #   main() \u306f\u5f93\u6765\u306e\u5019\u88dc\u3078\u843d\u3061\u308b \u2015\u2015 \u2605\u65e2\u306b\u8b80\u3081\u3066\u5c45\u308b\u884c\u306e\u51fa\u76ee\u306f\u5909\u3078\u306c\u2605\u3002',
 u"    mg = re.search(r'(?:^|\\s)path=(.+)[ \\t]+sha256=[0-9a-f]{64}(?:\\s|$)', line)",
 u'    if mg:',
 u'        _t = _dequote(mg.group(1))',
 u'        if _t:',
 u'            out.append(_t)',
]
lines[j + 1:j + 1] = ins
s = u'\n'.join(lines)
old = u'    if m:\n        out.append(_dequote(m.group(1)))'
new = (u'    if m:\n        _t = _dequote(m.group(1))\n'
       u'        if _t not in out:                  # \u2605km-46\u2605 \u8caa\u6b32\u5019\u88dc\u3068\u91cd\u306a\u3089\u306c\u6642\u306e\u307f\u7a4d\u3080\n'
       u'            out.append(_t)')
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
io.open(dst, 'w', encoding='utf-8', newline='').write(s)
sys.stderr.write(u'\u2605\u5f53\u3066\u305f %s\u2605\n' % dst)

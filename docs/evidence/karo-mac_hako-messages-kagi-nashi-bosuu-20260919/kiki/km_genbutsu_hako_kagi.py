# -*- coding: utf-8 -*-
"""km_genbutsu_hako_kagi.py ―― ★生きた箱★ が messages 鍵を持つか を読取のみで数へる

裁337507⑵ の疵は「鍵無の箱が 0 と同型に潰れる」事ゆゑ、★現に鍵無の箱が在るか★を測る。
書かぬ・触れぬ（open は読取のみ）。argv: <歩く根>（既定 queue/inbox）
"""
import io, os, sys, yaml, hashlib

root = sys.argv[1] if len(sys.argv) > 1 else "queue/inbox"
names = sorted(n for n in os.listdir(root) if n.endswith(".yaml"))
n_key = n_nokey = n_kara = n_shape = n_parse = 0
print("歩いた根 = %s" % root)
print("%-34s %9s %-8s %-6s %s" % ("箱", "byte", "頂", "旗", "未読/項数"))
for n in names:
    p = os.path.join(root, n)
    b = os.path.getsize(p)
    try:
        with io.open(p, encoding="utf-8") as f:
            d = yaml.safe_load(f)
    except yaml.YAMLError:
        n_parse += 1; print("%-34s %9d %-8s %-6s %s" % (n, b, "parse不能", "-", "―")); continue
    except OSError as e:
        print("%-34s %9d %-8s %-6s %s" % (n, b, "讀めぬ", "-", e)); continue
    if d is None:
        n_nokey += 1; n_kara += 1
        print("%-34s %9d %-8s %-6s %s" % (n, b, "None", "e", "空帳ゆゑ鍵も無い")); continue
    if not isinstance(d, dict):
        n_shape += 1
        print("%-34s %9d %-8s %-6s %s" % (n, b, type(d).__name__, "-", "頂が写像に非ず")); continue
    if "messages" not in d:
        n_nokey += 1
        print("%-34s %9d %-8s %-6s 鍵=%s" % (n, b, "dict", "n", ",".join(sorted(d.keys()))[:60])); continue
    m = d["messages"]
    if not isinstance(m, list):
        n_key += 1
        print("%-34s %9d %-8s %-6s messages は %s" % (n, b, "dict", "k", type(m).__name__)); continue
    n_key += 1
    unread = sum(1 for x in m if isinstance(x, dict) and not x.get("read", False))
    print("%-34s %9d %-8s %-6s %d/%d" % (n, b, "dict", "k", unread, len(m)))
print("")
print("母數 = %d 本 ／ 鍵在(k)=%d ★鍵無=%d★(内 空帳=%d) 形違=%d parse不能=%d"
      % (len(names), n_key, n_nokey, n_kara, n_shape, n_parse))

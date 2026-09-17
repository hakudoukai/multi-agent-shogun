# 写し器 182 ―― 口 shim/hakudokai/hakudokai_inbox_watcher.py:IDLE_FLAG_DIR(逐語) / 讀手 shim/hakudokai/hakudokai_inbox_watcher.py:85 類 ⑶(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
base = os.environ.get("IDLE_FLAG_DIR")
print('TARGET=' + binascii.hexlify(str(base).encode('utf-8')).decode())

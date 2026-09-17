# 写し器 174 ―― 口 shim/hakudokai/hakudokai_inbox_watcher.py:HAKUDOKAI_ROLE(逐語) / 讀手 shim/hakudokai/hakudokai_inbox_watcher.py:25 類 ⑶(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
role = os.environ.get("HAKUDOKAI_ROLE")
print('TARGET=' + binascii.hexlify(str(role).encode('utf-8')).decode())

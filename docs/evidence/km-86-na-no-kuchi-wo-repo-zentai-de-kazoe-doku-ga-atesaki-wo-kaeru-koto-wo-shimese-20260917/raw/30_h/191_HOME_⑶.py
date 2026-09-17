# 写し器 191 ―― 口 shim/hakudokai/hakudokai_realtime_bridge.py:HOME(逐語) / 讀手 shim/hakudokai/hakudokai_realtime_bridge.py:45 類 ⑶(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
HOME = os.environ.get("HOME", "")
print('TARGET=' + binascii.hexlify(str(HOME).encode('utf-8')).decode())

# 写し器 188 ―― 口 shim/hakudokai/hakudokai_realtime_bridge.py:HAKUDOKAI_PC_ROLE(逐語) / 讀手 shim/hakudokai/hakudokai_realtime_bridge.py:101 類 ⑷(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
PC_ROLE = os.environ.get("HAKUDOKAI_PC_ROLE", "MainPC")
print('TARGET=' + binascii.hexlify(str(PC_ROLE).encode('utf-8')).decode())

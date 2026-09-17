# 写し器 171 ―― 口 shim/hakudokai/hakudokai_heartbeat.py:HAKUDOKAI_ROLE(逐語) / 讀手 shim/hakudokai/hakudokai_heartbeat.py:225 類 ⑸(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
role = os.environ.get("HAKUDOKAI_ROLE")
print('TARGET=' + binascii.hexlify(str(role).encode('utf-8')).decode())

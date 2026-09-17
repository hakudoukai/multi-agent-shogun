# 写し器 172 ―― 口 shim/hakudokai/hakudokai_inbox_watcher.py:HAKUDOKAI_CLINIC_ID(逐語) / 讀手 shim/hakudokai/hakudokai_inbox_watcher.py:314 類 ⑷(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")
print('TARGET=' + binascii.hexlify(str(CLINIC_ID).encode('utf-8')).decode())

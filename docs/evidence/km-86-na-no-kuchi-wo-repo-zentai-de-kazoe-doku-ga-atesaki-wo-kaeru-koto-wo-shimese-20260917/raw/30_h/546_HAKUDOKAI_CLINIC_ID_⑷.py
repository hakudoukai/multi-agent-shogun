# 写し器 546 ―― 口 shim/hakudokai/hakudokai_role_init.py:HAKUDOKAI_CLINIC_ID(逐語) / 讀手 shim/hakudokai/hakudokai_inbox_watcher.py:333 類 ⑷(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
default=os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main"),
print('TARGET=' + binascii.hexlify(str(default).encode('utf-8')).decode())

# 写し器 458 ―― 口 shim/hakudokai/hakudokai_inbox_write.py:HAKUDOKAI_CLINIC_ID(逐語) / 讀手 shim/hakudokai/hakudokai_inbox_watcher.py:314 類 ⑷(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
clinic_id = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")
print('TARGET=' + binascii.hexlify(str(clinic_id).encode('utf-8')).decode())

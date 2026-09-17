# 写し器 403 ―― 口 shim/hakudokai/hakudokai_dev_lessons.py:SUPABASE_SERVICE_ROLE_KEY(逐語) / 讀手 shim/hakudokai/hakudokai_escalation.py:250 類 ⑸(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
print('TARGET=' + binascii.hexlify(str(key).encode('utf-8')).decode())

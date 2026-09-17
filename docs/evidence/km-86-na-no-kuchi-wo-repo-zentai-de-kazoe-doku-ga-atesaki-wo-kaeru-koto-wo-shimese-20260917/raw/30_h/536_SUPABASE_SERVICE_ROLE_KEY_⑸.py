# 写し器 536 ―― 口 shim/hakudokai/hakudokai_realtime_bridge.py:SUPABASE_SERVICE_ROLE_KEY(逐語) / 讀手 shim/hakudokai/hakudokai_escalation.py:250 類 ⑸(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
print('TARGET=' + binascii.hexlify(str(SUPABASE_KEY).encode('utf-8')).decode())

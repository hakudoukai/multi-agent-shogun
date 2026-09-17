# 写し器 540 ―― 口 shim/hakudokai/hakudokai_realtime_bridge.py:SUPABASE_URL(逐語) / 讀手 shim/hakudokai/hakudokai_dev_lessons.py:55 類 ⑶(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
print('TARGET=' + binascii.hexlify(str(SUPABASE_URL).encode('utf-8')).decode())

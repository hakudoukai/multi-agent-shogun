# 写し器 559 ―― 口 shim/hakudokai/hakudokai_skill_candidate.py:SUPABASE_URL(逐語) / 讀手 shim/hakudokai/hakudokai_daily_summary.py:218 類 ⑶(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
url = os.environ.get("SUPABASE_URL")
print('TARGET=' + binascii.hexlify(str(url).encode('utf-8')).decode())

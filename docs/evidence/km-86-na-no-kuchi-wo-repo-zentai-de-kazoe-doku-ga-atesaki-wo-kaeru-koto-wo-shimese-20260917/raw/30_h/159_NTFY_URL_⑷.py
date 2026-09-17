# 写し器 159 ―― 口 shim/hakudokai/hakudokai_escalation.py:NTFY_URL(逐語) / 讀手 shim/hakudokai/hakudokai_escalation.py:104 類 ⑷(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
ntfy_url = os.environ.get("NTFY_URL", "")
print('TARGET=' + binascii.hexlify(str(ntfy_url).encode('utf-8')).decode())

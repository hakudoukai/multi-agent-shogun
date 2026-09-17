# 写し器 155 ―― 口 shim/hakudokai/hakudokai_escalation.py:NTFY_TOPIC(逐語) / 讀手 shim/hakudokai/hakudokai_escalation.py:103 類 ⑷(python= 口の直後の値のみ・下流の合成は写さぬ)
import os, binascii
ntfy_topic = os.environ.get("NTFY_TOPIC", "")
print('TARGET=' + binascii.hexlify(str(ntfy_topic).encode('utf-8')).decode())

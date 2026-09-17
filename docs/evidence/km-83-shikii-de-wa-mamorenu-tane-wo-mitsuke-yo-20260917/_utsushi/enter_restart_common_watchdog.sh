#!/bin/bash
# ★子の stub★ ―― 丙の写し L39 の exec が此処へ落ちる。
# 生の子 scripts/watchdogs/enter_restart_common_watchdog.sh は一字も触らぬ・呼ばぬ。
# 親から渡つた env を repr で刷るのみ (伝播の実測 = ㋓)。
/usr/bin/python3 -c '
import os
for k in ("ER_THRESHOLD_MIN","ER_PANE_TARGET","ER_SESSION_NAME","ER_LOG_DIR"):
    print("子が受けた %s=%r" % (k, os.environ.get(k, "<未設定>")))
'
exit 0

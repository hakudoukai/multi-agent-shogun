# 写し器 15 ―― scripts/pane_enter_watcher.py:138 旗 LIVE 類 甲
import os
live = os.environ.get("LIVE", "0") == "1"
print("BRANCH=" + ("then" if live else "else"))

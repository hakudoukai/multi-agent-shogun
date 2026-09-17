#!/bin/bash
# ★陽性対照★ ―― 追跡器が「拾へる筈の形」を悉く含む作り物。一本も落ちてはならぬ。
python3 "$(dirname "$0")/karo_mac_manifest_verify.py" x     # dirname相対
bash scripts/checks/karo_mac_gate4.sh --selftest            # 直呼び(bash)
python3 scripts/checks/karo_mac_manifest_append.py a b      # 直呼び(python3)
source scripts/checks/pane_identity.sh                      # 読込み
# python3 scripts/checks/karo_mac_gate7.sh                  ← ★註の中★ ∴ 拾つてはならぬ

#!/bin/sh
# ㋒ ―― ★生器其の物★ に両形を食はせる。creds を外し `--dry-run` ゆゑ ★板へ一通も出ぬ★。
#   ・SUPABASE_URL/KEY 未設定(env で明に外す) → POST の道へ入る前に DRY-RUN が return する(L206-215)
#   ・--parent-seq は付けぬ ―― 付けると seq→uuid の解決が GET を打つ(L78-89)。★読取すら打たぬ★為。
P=/opt/homebrew/bin/python3
A=$HOME/bin/agent_letter.py
echo "--- 陽性: 家老の誤形(宛先を胴の位置に置く) ---"
env -u SUPABASE_URL -u SUPABASE_SERVICE_ROLE_KEY $P $A karo-mac mac_pc letter gunshi-mac "胴の文" --dry-run
echo "rc=$?"
echo "--- 陰性: 正形(--to で名指す) ---"
env -u SUPABASE_URL -u SUPABASE_SERVICE_ROLE_KEY $P $A karo-mac mac_pc letter "胴の文" --to gunshi-mac --dry-run
echo "rc=$?"

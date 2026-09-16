# 直し紙 ―― 番人の鳴りへの行注入を封じる(㋔・許し待ち)
題「★閾の番人を横から破れ★」km-52 / 專任2(足軽mac2)/ 生器不触・許し下りたら其の儘当てる形
基点: 束根 = docs/evidence/km-52-shikii-no-bannin-wo-yoko-kara-yabure-20260917/ ―― 本紙内の path は悉く束内相対

## 何を直すか(一行)
番人が値を拒む時、拒否の逐語へ `${_ft_v}` を生で挿す。値に改行が在れば
★一本の鳴りが二本に割れ、二本目を偽の記録に仕立てられる★(㋓・raw/70_chunyu.txt)。
判定(既定へ倒す=fail-closed)は正しい。★疵は「表示」だけ★。∴ 表示のみ均す。

## ⑴ 直す行(逐語・前/後)
対象: 共有器四本 悉く同一行 ―― 番人の逐語は byte 一致(30_ate 段で實測)。
生器の在處(讀取のみで確認・触れて居らぬ):
  scripts/inbox_watcher.sh / scripts/watchdogs/enter_restart_common_watchdog.sh
  scripts/agent_health_check.sh / scripts/checks/context_usage_warn.sh

【前】(現行 ab2a1f1・写し ki/guard_inbox_watcher.sh:23 逐語)
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"

【後】(一行 手前へ足し、一字を差し替へる)
  _ft_vp="$(printf '%s' "${_ft_v}" | tr '\n\r\t' '\266\215\211')"  # ★行注入封じ: 改行/復帰/TAB を可視印へ均す(判定不変・表示のみ)★
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"

差分は ★${_ft_v} → ${_ft_vp} の一字と、前へ一行★。倒す行 `eval "$_ft_o=\$_ft_d"` は一字も触らぬ。

## ⑵ bash -n の出目(束内で實測・raw に非ず此処に逐語)
  bash -n ki/guard_inbox_watcher.sh   → rc=0(前)
  bash -n ki/91_guard_patched.sh      → rc=0(後)
  (91_guard_patched.sh = 前の写しに【後】を当てた物。生器では無い。)

## ⑶ 両対照(ki/92_shou.sh・raw/92_shou.txt 實測)
  陽性(改行注入㋐12): 前 OUT=30 鳴り2行 → 後 OUT=30 鳴り★1行★  … 注入消ゆ・倒す先不変
  陰性(清数30)      : 前 OUT=30 鳴り0行 → 後 OUT=30 鳴り0行    … 清形は前後とも黙る
  後の鳴り逐字      : [watcher] ★閾 T を比較器が扱へぬ(「50¶9999」) ―― 既定 30 へ倒す(fail-closed)★
                     (改行が一byte ¶ に均され、一行に収まる)

## ⑷ 閾の意味が変らぬ證
直しは `_th_say`(人へ見せる echo)の引数のみ。番人の判定路
  num_same_op / [ "$_ft_v" -ge 0 ] / eval "$_ft_o=\$_ft_d"
は一字も触れて居らぬ。∴ 受ける値・倒す先・fail-closed の別は不変。
上⑶で OUT が前後とも 30 で一致する事が其の實測證。

## ⑸ 戻し方(一行)
  足した _ft_vp 行を消し、「${_ft_vp}」を「${_ft_v}」へ戻す(git revert でも同義)。

## ★此の直しが「せぬ」事(誤読封じ)★
・零倒(㋐07/08)・極倒(㋐18)・讀手割れ(㋐17 octal)は ★直らぬ★。
  之は「表示」の疵ではなく「判定」の疵(番人に上下限が無い/算術讀手が八進)。別紙・別許しの案件。
・∴ 本紙は「行注入(表示)」一件のみを封じる。★fail-open を封じたと読むな。★

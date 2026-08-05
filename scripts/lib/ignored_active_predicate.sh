#!/bin/bash
# scripts/lib/ignored_active_predicate.sh
#
# ★未結線・稼働に影響せず★ — 本fileは 2026-08-05T21:21 時点(当職実測)で
# いかなる稼働中script・hook・timerからも source されておらぬ。source する側が
# 現れるまで、本fileの存在は稼働に一切の効果を持たぬ(read-only な関数定義のみ・
# 本file自身は top-level で何も実行せぬ)。
#
# 設計出所:
#   docs/incident_logs/2026-08-05_gitignore_silent_gate_design_a1.md §4(稼働中の定義)
#   docs/incident_logs/2026-08-05_gitignore_silent_gate_design_addendum1_a1.md §A-2(配置=一箇所)
# 起草: 足軽1号 / 委任: karo-second msg_20260805_211654_03b5d589(条件付き先行許可・三file作成のみ)
#
# 呼び出し側は本fileを source した上で is_ignored_and_active を呼ぶ事。
# 独自に再実装してはならぬ(追補1 §A-3①、軍師second監査チェック項目=
#   grep -L "source.*ignored_active_predicate" <呼出候補> で再実装の有無を機械的に洗える)。

# is_ignored_and_active <repo_root> <path>
#   <path> は repo_root からの相対path。
#   標準出力に1行: STATUS=<FLAG|STALE|CLEAN> evidence=[...]
#   戻り値は常に0(判定結果は標準出力で返す。本体§5-3「うるさく失敗する」は
#   呼び出し側=巡回scriptの責務であり、本述語自体の責務ではない)。
#
#   信号定義(本体§4を忠実に実装。判定式: ACTIVE = A OR B OR C。Dのみ= STALE):
#     A: canon参照      = CLAUDE.md または docs/**/*.md の正本文中に path が literal 出現
#     B: cron/systemd起動 = ~/.config/systemd/user/*.service(.d/*.conf) または
#                           /etc/systemd/system/*.service の ExecStart* 行、または crontab -l に出現
#     C: 追跡済fileからのsource/invoke = git管理下(=ignoreされておらぬ)file内に
#                           呼出し構文が出現(git grep は自動的に追跡済fileのみを検索するため
#                           「ignoreされておらぬ」制約は git grep を使う事自体で満たされる)
#     D: 直近の実行痕跡   = mtimeが14日以内、または対応 __pycache__/*.pyc が存在
is_ignored_and_active() {
  local repo_root="$1" path="$2"
  local evidence=()
  local sig_a=0 sig_b=0 sig_c=0 sig_d=0
  local base
  base="$(basename -- "$path")"

  # 信号A: canon参照
  if grep -qF -- "$path" "$repo_root/CLAUDE.md" 2>/dev/null; then
    sig_a=1; evidence+=("A:CLAUDE.md")
  elif grep -rqF -- "$path" "$repo_root/docs" --include='*.md' 2>/dev/null; then
    sig_a=1; evidence+=("A:docs/**/*.md")
  fi

  # 信号B: cron/systemd起動
  if grep -rqF -- "$base" "$HOME/.config/systemd/user" \
       --include='*.service' --include='*.conf' 2>/dev/null; then
    sig_b=1; evidence+=("B:systemd-user")
  fi
  if grep -rqF -- "$base" /etc/systemd/system --include='*.service' 2>/dev/null; then
    sig_b=1; evidence+=("B:systemd-system")
  fi
  if command -v crontab >/dev/null 2>&1 && crontab -l 2>/dev/null | grep -qF -- "$base"; then
    sig_b=1; evidence+=("B:crontab")
  fi

  # 信号C: 追跡済fileからのsource/invoke(git grepは追跡済fileのみを対象とする)
  if git -C "$repo_root" grep -qE \
       "(source|\.|bash|sh|python3?|run)[[:space:]]+.*${base}" -- '*' 2>/dev/null; then
    sig_c=1; evidence+=("C:source-or-invoke")
  fi

  # 信号D: 直近の実行痕跡
  if [ -e "$repo_root/$path" ]; then
    local mtime_epoch now_epoch age_days
    mtime_epoch="$(stat -c %Y -- "$repo_root/$path" 2>/dev/null || echo 0)"
    now_epoch="$(date +%s)"
    age_days=$(( (now_epoch - mtime_epoch) / 86400 ))
    if [ "$age_days" -le "${MTIME_STALE_DAYS:-14}" ]; then
      sig_d=1; evidence+=("D:mtime<=${MTIME_STALE_DAYS:-14}d(${age_days}d)")
    fi
  fi
  local pyc_dir base_noext
  pyc_dir="$repo_root/$(dirname -- "$path")/__pycache__"
  base_noext="${base%.py}"
  if [ -d "$pyc_dir" ] && ls "$pyc_dir/${base_noext}".*.pyc >/dev/null 2>&1; then
    sig_d=1; evidence+=("D:pycache")
  fi

  local status
  if [ "$sig_a" -eq 1 ] || [ "$sig_b" -eq 1 ] || [ "$sig_c" -eq 1 ]; then
    status="FLAG"
  elif [ "$sig_d" -eq 1 ]; then
    status="STALE"
  else
    status="CLEAN"
  fi

  local IFS=,
  printf 'STATUS=%s evidence=[%s]\n' "$status" "${evidence[*]}"
  return 0
}

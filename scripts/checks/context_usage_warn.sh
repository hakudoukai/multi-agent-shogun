#!/usr/bin/env bash
# context_usage_warn.sh — Claude Code UserPromptSubmit hook (STEP1-C 副院長令)
#
# 目的 (context 衛生機構):
#   Claude Code 2.x の /compact は (a) 自動 (context limit 接近時) + (b) 手動 (/compact 入力)
#   の二系統で発火するが、★閾値到達「前」に proactive に notice する公的 API は存在しない★。
#   本 hook は session jsonl ファイル size を heuristic に観測し、危険水域に近づいた際
#   stderr へ警告を吐く。Claude Code が会話と共に stderr を表示するため、ユーザーへ
#   早期 /compact 入力を促す機構となる。
#
# 配線:
#   .claude/settings.json の "UserPromptSubmit" hook へ登録 (timeout 5、|| true 必須)。
#   絶対にブロックしない (DD-169 設計原則と整合、PreToolUse の hook 設計と同一)。
#
# 仕組み:
#   1. 現セッションの jsonl 経路を CLAUDE_CODE_SESSION_ID env から導出
#   2. file size (bytes) を観測
#   3. 既定閾値:
#      - WARN_BYTES (=1.6MB / 約 80%): stderr "★context_warn★ jsonl=XKB ≒ 80% — /compact 推奨"
#      - DANGER_BYTES (=2.0MB / 約 95%): stderr "★context_danger★ jsonl=XKB ≒ 95% — /compact 即実行"
#   4. 閾値は env で上書き可 (CONTEXT_WARN_BYTES / CONTEXT_DANGER_BYTES)
#
# 注意:
#   - jsonl は immutable log で live in-memory context とは厳密一致しない (auto-compact 後も
#     jsonl は append され続けるため過大推定気味)。あくまで heuristic な早期警告として運用。
#   - 厳密な context % は /context slash command (対話的に Claude へ入力) でのみ取得可能。
#   - 本 hook は ★絶対にブロックしない★ (exit 0 強制)。

set -u

# ─── 閾の番人(甲/乙) ───
_th_say(){ echo "[context_warn] $*" >&2; }
# ★甲 ―― 閾は「比較に使ふのと同じ演算子」で検めよ(裁 seq322952・横展開 裁 seq323062)★
#   舊 is_num は case の字面判定ゆゑ 99999999999999999999 を「數」と呼ぶ。然し後段の
#   [ "$x" -ge "$閾" ] は其の値で ★rc=2★ に倒れ、if も elif も偽＝★黙つて既定の枝へ落ちる★。
#   ∴ 検める器と使ふ器を同じ演算子に揃へる。
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
# ★乙 ―― 未設定/空文字/空白のみ を分けて名指す(裁 seq322952)★
#   ${x+set} は空文字でも set を返す ∴ 未設定と空文字は此処でのみ分かれる。
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}
# 閾を一本の道で定める ―― $1=環境変数名 $2=既定 $3=受け皿の変数名
#   ★乙′(高頻度器の例外・家老mac 申告)★: 未設定＝既定 は本器の★設計上の常態★ゆゑ黙る。
#   逐回鳴らせば起動毎/prompt 毎の空鳴り＝氾濫(本器の旧註と同旨)。★異常の三形★
#   (空文字・空白のみ・比較器で扱へぬ)は必ず鳴る。門(低頻度器)では四形悉く刷る。
fix_threshold(){
  _ft_n="$1"; _ft_d="$2"; _ft_o="$3"; _ft_s="$(env_state "$_ft_n")"; eval "_ft_v=\"\${$_ft_n-}\""
  case "$_ft_s" in
    unset) eval "$_ft_o=\$_ft_d"; return 0 ;;
    empty) _th_say "★閾 ${_ft_n} が空文字 ―― 既定 ${_ft_d} へ倒す(fail-closed)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
    blank) _th_say "★閾 ${_ft_n} が空白のみ ―― 既定 ${_ft_d} へ倒す(fail-closed)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
  esac
  if num_same_op "$_ft_v" && [ "$_ft_v" -ge 0 ]; then eval "$_ft_o=\$_ft_v"; return 0; fi
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
  eval "$_ft_o=\$_ft_d"
}
# 此の器が黙ると CLAUDE.md 三層機構の L2 が丸ごと抜ける。然も本体は exit 0 を強ひられて居る
# (DD-169) ∴ ★鳴らぬ事を rc で知る術が無い★。故に ★言ふ★ 事が唯一の報せである(專任3 第40弾)。
fix_threshold CONTEXT_WARN_BYTES 1600000 WARN_BYTES      # ~1.6 MB ≒ 80% (heuristic)
fix_threshold CONTEXT_DANGER_BYTES 2000000 DANGER_BYTES  # ~2.0 MB ≒ 95% (heuristic)

SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$HOME/multi-agent-shogun}"

# project_dir を Claude Code 流に slug 化 (`/` → `-` 接頭辞)
PROJECT_SLUG="-$(echo "$PROJECT_DIR" | sed 's|^/||; s|/|-|g')"
JSONL_PATH="$HOME/.claude/projects/$PROJECT_SLUG/$SESSION_ID.jsonl"

if [ -z "$SESSION_ID" ] || [ ! -f "$JSONL_PATH" ]; then
    # session 情報取得不能 → silently exit (絶対 block 禁)
    exit 0
fi

SZ=$(stat -c '%s' "$JSONL_PATH" 2>/dev/null || echo 0)
KB=$((SZ / 1024))

if [ "$SZ" -ge "$DANGER_BYTES" ]; then
    echo "★context_danger★ session jsonl=${KB}KB (>=$(($DANGER_BYTES / 1024))KB ≒ 95% heuristic) — ★即 /compact 入力推奨★" >&2
elif [ "$SZ" -ge "$WARN_BYTES" ]; then
    echo "★context_warn★ session jsonl=${KB}KB (>=$(($WARN_BYTES / 1024))KB ≒ 80% heuristic) — /compact 入力を検討" >&2
fi

exit 0

#!/bin/bash
# scripts/lib/00e_gate_thresholds.sh
#
# ★未結線・稼働に影響せず★ — 本fileは 2026-08-05T21:21 時点(当職実測)で
# いかなる稼働中script・hook・timerからも source されておらぬ。source する側が
# 現れるまで、本fileの存在(閾値定義・env override検知・ledger追記・uplink呼出の
# いずれも)は稼働に一切の効果を持たぬ。
#
# ★新たに開ける穴(自己申告)★= 本fileを誰かが不用意に source し、巡回scriptへ
# 正しく結線せぬまま _00e_announce_override を直接呼べば、
# scripts/karo_second_send_iincho.sh --live が即座に発火し得る。
# 結線は理事長殿の御判断が下るまで行ってはならぬ(karo-second msg_20260805_211654_03b5d589 条件④)。
#
# 設計出所:
#   docs/incident_logs/2026-08-05_gitignore_silent_gate_design_addendum2_a1.md §6(閾の置き場・動かし方・裁定③)
#   docs/incident_logs/2026-08-05_gitignore_silent_gate_design_addendum3_a1.md §3〜§7(env overrideを「うるさく鳴らす」)
# 起草: 足軽1号 / 委任: karo-second msg_20260805_211654_03b5d589(条件付き先行許可・三file作成のみ)
#
# 動かし方(裁定③・追補2 §6-2): 値の変更は裁可者(委員長殿)の裁定に基づき本fileを
# 直接編集し、同一commitへ (a)変更前後の値 (b)裁定の出所(msg id等) (c)負テスト再実行結果
# を含める事。code定数として別scriptへ埋め込んではならぬ(閾値一箇所化・裁定④)。

MTIME_STALE_DAYS="${MTIME_STALE_DAYS:-14}"          # 信号D(本体§4)
PATROL_INTERVAL_MIN="${PATROL_INTERVAL_MIN:-15}"    # 巡回間隔(本体§5-2)
AMBIGUOUS_BOUNDARY_LEANS_TO="FLAG"                  # 裁定①③4の明文化(追補2 §3(c))
                                                     # 数値ではなく性質の宣言ゆえ env override 対象外

_00E_RELEASE_LEDGER_PATH="${_00E_RELEASE_LEDGER_PATH:-docs/00e_gate_release_ledger.md}"

# _00e_load_threshold <var_name> <file_default>
#   env var による override を検知したら _00e_announce_override を呼ぶ(追補3 §3 疑似コードの実装化)。
#   有効値を1つ標準出力へ printf する(改行なし・呼び出し側が var="$(...)" で受ける想定)。
_00e_load_threshold() {
  local var_name="$1" file_default="$2"
  local effective="${!var_name:-$file_default}"
  if [ "$effective" != "$file_default" ]; then
    _00e_announce_override "$var_name" "$file_default" "$effective" >&2
  fi
  printf '%s' "$effective"
}

# _00e_ledger_append <line>
#   docs/00e_gate_release_ledger.md へ1行 append-only で書き込む(追補2 §4-2 運用規約)。
#   成功時0、失敗時非0。
_00e_ledger_append() {
  local line="$1"
  printf '%s\n' "$line" >> "$_00E_RELEASE_LEDGER_PATH" 2>/dev/null
}

# _00e_announce_override <var_name> <file_default> <effective>
#   追補3 §3 の3手順を実装する:
#     1. ledger追記を先に行う(§4「先に ledger へ書いてから override を効かせる」順序)
#     2. ledger追記が成功した後にのみ uplink(karo_second_send_iincho.sh)を呼ぶ(§5)
#     3. 標準出力へ [ENV-OVERRIDE-USED] を itemize する(本体§5-3の型を踏襲)
#   gate自体のexit codeはoverrideを理由には非0にせぬ(裁定⑵=overrideは正当な出口)。
#   但し ledger追記または uplink呼出が失敗した場合は非0を返す
#   (「鳴らす機構が黙って失敗する」事こそ裁定の禁ずる「半のまま」の再来であるゆえ、追補3 §3)。
_00e_announce_override() {
  local var_name="$1" file_default="$2" effective="$3"
  local at ledger_status="FAIL" uplink_status="FAIL" line

  at="$(date -Iseconds)"
  line="OVERRIDE var=${var_name} file_default=${file_default} effective=${effective} by=${USER:-unknown} at=${at} status=半(fail-closed維持・出口温存) tier_chosen=③検知+④様式 tier_rejected=②機械ブロック tier_reason=\"②は唯一の出口(override)を殺すゆえ裁定⑵に反する\" ack=未実読確認"

  if _00e_ledger_append "$line"; then
    ledger_status="OK"
    # uplinkはledger追記成功後にのみ呼ぶ(追補3 §3手順2)。
    # ★本fileが結線されるまでは、この分岐に到達する経路自体が存在せぬ(冒頭注記)★。
    if [ -x "scripts/karo_second_send_iincho.sh" ]; then
      if scripts/karo_second_send_iincho.sh --live --type status_update --requires-response -- "$line" \
           >/dev/null 2>&1; then
        uplink_status="OK"
      fi
    fi
  fi

  printf '[ENV-OVERRIDE-USED] var=%s file_default=%s effective=%s at=%s ledger=%s uplink=%s\n' \
    "$var_name" "$file_default" "$effective" "$at" "$ledger_status" "$uplink_status"

  [ "$ledger_status" = "OK" ] && [ "$uplink_status" = "OK" ]
}

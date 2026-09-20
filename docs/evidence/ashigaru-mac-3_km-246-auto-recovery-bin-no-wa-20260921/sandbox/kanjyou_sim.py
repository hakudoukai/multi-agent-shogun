#!/usr/bin/env python3
"""
砂箱 ―― auto_recovery 便が己の次の /clear の引金に成る環を、四版に共通する状態機械として
純粋にモデル化し、稼働中の watcher(pid 80326/80352/80358)には一指も触れず測る。

モデルの根拠（当職が git cat-file -p で四版すべてから実測した行・raw/01_yonhan_gyouban_hikaku.md 参照）:
  - has_task_assigned: 未読メッセージに from=inbox_watcher & type=task_assigned が
    1件でも在れば真（四版とも同一）。
  - NEW_CONTEXT_SENT: send_context_reset() が呼ばれ 0/2 を返すと 1 に立つ。
    0 に戻るのは (a) 未読が 0 になった時、(b) Phase3 エスカレーションが /clear を送った時のみ
    （四版とも同一・L1296/1567 相当）。
  - Phase3: FIRST_UNREAD_SEEN から age >= ESCALATE_PHASE2(既定240s) かつ
    LAST_CLEAR_TS から ESCALATE_COOLDOWN(既定300s) 経過で発火。発火すると /clear を送り、
    FIRST_UNREAD_SEEN=0・NEW_CONTEXT_SENT=0 に戻す（L1552-1553 相当）。
  - enqueue_recovery_task_assigned は clear_sent(=clear_command 経由の /clear)からのみ呼ばれ、
    send_context_reset からは呼ばれない（当職が四版で函定義を実測・raw 参照）。
    ∴ auto_recovery 便は clear_command 経由の /clear 1 回につき最大1通のみ書かれる
    （dedup guard が「既に未読の auto_recovery が在れば SKIP」する為）。

前提（保守側・agent が一切応答しない最悪ケース）:
  - t=0 に家老の clear_command が届き、1 回目の /clear が送られる（clear_sent=1）。
  - t=0+8s（sleep5+既定sleep3相当）に auto_recovery 便(type=task_assigned)が書かれる。
  - 以後 agent は一切 inbox を読まない（read が真に成らない＝has_task_assigned が真のまま）。
  - watcher の poll 間隔は 10s と仮定（実測は環境依存・保守的に短めを取り cycle 数の上限側を見る）。

このモデルは「観測された実例（a1: 23:54→00:05:10 の2回で止まった。a1 は其の後 inbox を読み
read:true に成った為）」とは★別の問い★に答える ―― 「読まれない場合、何度回り得るか」。
"""
import json

POLL_INTERVAL = 10          # sec, watcher loop cadence (保守的な仮定・実測ではなく設計値からの見積)
ESCALATE_PHASE2 = 240       # sec, 既定値(四版で実測: L124-126 相当)
ESCALATE_COOLDOWN = 300     # sec, 既定値
SIM_DURATION = 3 * 3600     # 3時間を走らせる（保守）

def simulate(duration, poll, phase2, cooldown):
    t = 0
    clear_sent_at = [0.0]          # t=0: clear_command 経由の1回目 /clear
    auto_recovery_written_at = 8.0  # t=0+8s: enqueue_recovery_task_assigned
    has_task_assigned = True        # 未読の auto_recovery 便が常在（agent が読まぬ前提）
    new_context_sent = False
    first_unread_seen = 8.0          # 便が書かれた瞬間から「未読」が始まる
    last_clear_ts = 0.0
    clear_events = list(clear_sent_at)  # 1回目を含める
    log = [f"t=0.0s clear_command 経由 1回目 /clear (clear_sent=1)",
           f"t=8.0s enqueue_recovery_task_assigned で auto_recovery 便を1通書く(以後 has_task_assigned=True 固定・agent 無応答前提)"]

    t = poll
    while t <= duration:
        # has_task_assigned=1 && NEW_CONTEXT_SENT==0 && clear_seen==0(通常cycleではclear_command処理と別cycle)
        if has_task_assigned and not new_context_sent:
            # send_context_reset 発火 → 二度目以降の /clear
            clear_events.append(t)
            new_context_sent = True
            last_clear_ts = t
            log.append(f"t={t}s [CONTEXT-RESET] send_context_reset 発火 → /clear 送出 (NEW_CONTEXT_SENT: False→True)")
        else:
            # Phase3 エスカレーション条件を評価
            age = t - first_unread_seen
            if age >= phase2 and (last_clear_ts == 0 or (t - last_clear_ts) >= cooldown):
                clear_events.append(t)
                first_unread_seen = t
                new_context_sent = False
                last_clear_ts = t
                log.append(f"t={t}s ESCALATION Phase3 発火 → /clear 送出 (FIRST_UNREAD_SEEN・NEW_CONTEXT_SENT を 0 に戻す)")
        t += poll

    return clear_events, log

def main():
    events, log = simulate(SIM_DURATION, POLL_INTERVAL, ESCALATE_PHASE2, ESCALATE_COOLDOWN)
    result = {
        "sim_duration_sec": SIM_DURATION,
        "poll_interval_sec": POLL_INTERVAL,
        "escalate_phase2_sec": ESCALATE_PHASE2,
        "escalate_cooldown_sec": ESCALATE_COOLDOWN,
        "total_clear_events": len(events),
        "clear_event_times_sec": events,
        "note": "agent が一度も inbox を読まぬ最悪ケースの見積り。上限を実装する counter/cooldown-on-total-cycles は"
                "四版いずれにも見付からず(grep実測・raw/01参照)、∴ 理論上は sim_duration を延ばす限り clear_events も増え続ける(線形)。",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n--- log(先頭10件+末尾5件) ---")
    for line in log[:10]:
        print(line)
    print("...")
    for line in log[-5:]:
        print(line)

if __name__ == "__main__":
    main()

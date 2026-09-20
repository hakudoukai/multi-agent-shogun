# 砂箱模型の限定 ―― 實測との齟齬を隠さず記す

## 齟齬

實例(a1, `queue/inbox/ashigaru-mac-1.yaml` L1235-1250)の二回目 `/clear` は
23:54:45(1回目)→00:05:10(2回目)＝**625秒後**。

`sandbox/kanjyou_sim.py` の素朴模型(POLL_INTERVAL=10s仮定)は「次の poll で即發火」＝
t=8s(便を書く)の次周期(t=10s)で二回目 `/clear` を予測していた ―― **實測と615秒(約10分)の開き**。

## 原因(當職の器で main版=778d2334 を實測)

`send_context_reset()`(L848-930)冒頭近く、**L864**:
```
if agent_is_busy; then
    echo "[$(date)] [DEFER] $AGENT_ID: agent busy — postponing context reset (RC-1 cure)" >&2
    return 1
fi
```
発火條件(`has_task_assigned && !NEW_CONTEXT_SENT && !clear_seen`)が眞でも、
**`agent_is_busy` が眞の間は毎周期 defer(rc=1)し、`NEW_CONTEXT_SENT` は立たない**。
∴ 実際の二回目發火時刻は「poll間隔」ではなく「agent が busy から idle に変る時刻」に支配される。
副院長令 fc3a5b0b RC-1 cure の逐語コメント(L862-863)が此の設計意図を明記。

## 模型への影響(訂正)

- **當ってゐた事**: 「上限を成す counter/cooldown-on-total-cycles は四版いずれにも無い」
  (本頁の grep 實測・四版とも `連続skip上限` 以外に該当無し)。∴ 理論上の環が閉じぬ結論は変らぬ。
- **外れてゐた事**: 「次の poll(約10s後)で即二回目發火」という時刻の予測。實測は625秒後 ――
  `agent_is_busy` gate が支配的である事を見落してゐた。
- **∴ `sandbox/kanjyou_sim_3h.out.json` の `total_clear_events=70`(3時間)は、
  ★agent が常時 idle と見做される最悪ケースの理論上限★であり、
  ★實際の頻度(busy gate 込み)の予測値ではない★。両者を混同して報告してはならぬ。

## 母數・器・rc・刻

- 母數: 四版(disk/index/HEAD/main)の `send_context_reset` 定義本文、當職の器= `grep -n agent_is_busy raw/ver_main_778d2334.sh` 他3版
- 器: `git cat-file -p <blob40>` で抽出した raw/ver_*.sh 四本、`grep -nE` (own instrument, ripgrep-compatible ugrep shim)
- rc: 0 (全 grep 完遂)
- 刻: 2026-09-21 (本弾実施時刻、当職ローカル)

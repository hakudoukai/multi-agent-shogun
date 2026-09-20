# ⑹㋒ 四つの札 ―― 環を止める counter/cooldown-on-total-cycles は四版いずれにも無い

問ひ: 「便を書く→箱を見る→/clear を送る」環に、総回数を数へて止める仕掛け(counter/上限/フラグ)は在るか。
在れば其の逐語コードを示せ。無ければ「上限無し」を四版それぞれの札で示せ。

## 探索器(當職の器・raw/ver_*.sh 四本に対し own instrument で実行)

```
grep -nE 'ESCALATE_MAX|escalation_count|MAX_ESCALATION|retry_count|MAX_RETRY|attempt_count|上限|cycle_count|CLEAR_COUNT|clear_count' raw/ver_<版>.sh
```

## 札① disk(working, blob=73cdfbc4a8dfd684b6ef21c3aad234d8ece335b8)

- 該当ヒット: L1093, L1100 ―― **無関係**(「連続skip上限」=理事長殿入力中に nudge を控へる為の別機構、default 5≈2.5分)
- `enqueue_recovery_task_assigned` / `send_context_reset` の本体に total-cycle counter 記述 **無し**
- ★上限無し(disk 版)★

## 札② index(staged, blob=1d2821a3b4bdb0b265ada2d82df36f6bd5e2e3c8)

- 該当ヒット: L963, L970 ―― 同上、無関係(連続skip上限)
- ★上限無し(index 版)★

## 札③ HEAD(blob=00cd905d6eebd7d85b55ce1e0a1553697fc6cc9a)

- 該当ヒット: L1016, L1023 ―― 同上、無関係(連続skip上限)
- ★上限無し(HEAD 版)★

## 札④ main=origin/main=★走る版★(blob=778d233445de00b0ac1df9b464dd135024046402)

- 該当ヒット: L1115, L1122 ―― 同上、無関係(連続skip上限)
- `send_context_reset`(L848-930)内は `agent_is_busy` による**時刻の遅延**(defer)機構のみ持ち、
  **回数を数へて止める**機構は持たぬ(sandbox/02_sokutei_gentei_to_teisei.md 参照)。
- ★上限無し(main=走る版)★

## 結論

四版とも同型の答: **counter/cooldown-on-total-cycles に依る上限は存在しない**。
存在するのは①dedup guard(同一便の重複書込みを防ぐのみ・環自体は止めぬ)②Phase3 の
`ESCALATE_COOLDOWN`(=個々の発火間隔を間引くのみ・回数には無関係)③`agent_is_busy` gate
(発火時刻を遅らせるのみ・回数には無関係)の三者であり、いずれも「total_clear_events を
天井で止める」役目を持たない。∴ agent が inbox を読まぬ限り、理論上は環は閉じない
(sandbox/kanjyou_sim_3h.out.json: 3時間の worst-case 見積りで total_clear_events=70、
線形に増え続ける ―― ただし此の数値は agent_is_busy gate を「常時idle」と単純化した
理論上限であり実測の頻度予測ではない事、sandbox/02_sokutei_gentei_to_teisei.md に明記)。

## 母數・器・rc・刻

- 母數: 4 (disk/index/HEAD/main)、各版 raw/ver_*.sh 1本ずつ = 4本を全数走査
- 器: `grep -nE` (own instrument, 上記正規表現)
- rc: 0 (4本とも完遂・エラー無し)
- 刻: 2026-09-21

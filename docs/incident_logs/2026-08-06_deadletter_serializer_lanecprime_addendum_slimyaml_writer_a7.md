> ★SUPERSEDED (2026-08-06T23:27+09:00・家老second指示=文書は最終票1点へ集約)★
> 本fileの内容は `docs/incident_logs/2026-08-06_deadletter_serializer_lanecprime_hardening_a7.md`
> の「★残欄 (residual)★」節へ畳み込み済 (書きぶりも是正済)。以後の監査・参照は集約先を正とする。
> ★消さぬ理由=何が起きたかを残す為 (本org通例)★。本file自体はこれ以上更新しない。

# Lane C′ 追記 — もう一人の書き手 (slim_yaml.py) を自ら検めた結果 (足軽7号)

**測時** = 2026-08-06T23:20 **契機** = karo-second msg_20260806_224732_83194670 (足軽4号 22:36 PASS済 母集団票からの申し送り)
**本file の性格** = 先の完了報告 (`2026-08-06_deadletter_serializer_lanecprime_hardening_a7.md`) への★追記★。実装のやり直しではない。

## 足軽4号票の申し送りへの回答 (己でも検めよ、との指示に対して)

足軽4号票 (`docs/incident_logs/2026-08-06_deadletter_second_writer_reader_population_a4.md` §⒝-2) の指摘=
`scripts/slim_yaml.py:311 slim_all_inboxes()` が `queue/inbox/*.yaml` を無除外globし `_dead_letter_second.yaml` を巻き込む、を
★当職も原本に触れず自分で code を実読して確認した★:
- `slim_all_inboxes()` (L305-320) → `inbox_dir.glob('*.yaml')` に除外なし → `slim_inbox('_dead_letter_second', ...)` を呼ぶ。
- `slim_inbox()` (L193-248) → `load_yaml()` (`yaml.safe_load`) で読み、`read: true` の entry が★1件でも★あれば `save_yaml()` (直接`yaml.dump`書込み・flock無し・tmp+rename無し) で本体を書き換える。
- `append_dead_letter()` が作る entry は常に `read: false` ゆえ、他の経路で `read: true` に変わらぬ限り「読むが書かない」no-op。

## 之は当職の実装契約への影響評価

★正直に書く★: 当職が実装した `fcntl.flock` は `append_dead_letter()` 自身の呼出間 (receiver複数起動等) の排他制御であり、
`slim_yaml.py` の `save_yaml()` はこの lock に★一切参加していない★別の独立した read-modify-write 経路。
∴ ★理論上、両者が同時に走れば当職のflockは無力 (slim側がlockを取らぬゆえ)★。
而して以下三点により★現状の実害は限定的★と判じる (楽観ではなく実測に基づく):

1. **発火条件が現在満たされていない**: dead-letter entryは常に`read: false`で作られ、之を`true`に変える経路は
   足軽4号票・当職双方の探索で★見つかっていない (0件・判らぬは判らぬままと明記)★。ゆえに今`slim_all_inboxes`が
   `_dead_letter_second`に到達しても、通常は「読むが書かない」で終わる。
2. **組織的停止令が現に効いている**: `scripts/slim_yaml.sh`の実行は★全target停止中★(本部長殿発令・解く権は本部長殿のみ・
   継続中。honbucho inbox 複数便で反復確認可)。ゆえに現時点でこの書き手が★物理的に起動していない★。
3. **根治は別Lane (Lane F・足軽4号) が既に閉じている**: `slim_all_inboxes()`自体を pane_registry allowlist方式へ改め
   `_dead_letter_second`を対象から除外する根治が、当職とは別のworktree/branch (`feat/lane-f-slim-allowlist-a4`) で実装済・
   ★軍師second PASS済★ (`queue/reports/gunshi_second_lane_f_slim_allowlist_root_cure_audit_20260806.md`)。
   而してLane Fも当職同様★運用未反映 (inactive・本部長殿のlive dry-run待ち)★のまま止まっている。

## 結論・当職の対応

- ★当職はslim_yaml.pyを直さない★ — Lane Fが既に同じ根を別角度(該当fileを対象から除外)で閉じており、
  当職が重ねて手を出せば二重実装 (Anti-Duplication) になる。
- 当職の実装 (⒝flock) は「明記した通り、`append_dead_letter()`自身の同時呼出のみを保護する」ものであり、
  ★slim_yaml.py経由の書換までは保護しない★事を、先の完了報告に★この追記で明記して補う★。
- 両Laneは★競合ではなく相補的★: 当職=書き手(append_dead_letter)を硬化、Lane F=もう一人の書き手を対象から除外。
  両方が主repoへ反映されて初めて「⒜writer/reader母集団が示す全経路」が閉じる。

## 令④ (数え直し)

足軽4号票の「glob経由reader/条件付writer=1件」を当職も独立に1件と確認 (一致)。新規に発見した別経路=0件。

## B (merge判断) についての当職の理解

karo-second便で「merge=現時点0・A/B/C′最終再監査前に合流為すな・read-onlyのconflict planのみ許可」との答が下った旨、
当職も受理した。当職の工区 (⒜実装) はmerge/activationを含まぬ (先の完了報告記載通り) ゆえ、本件は当職の完了状態を変えない。

## 破れた後

原本 `_dead_letter_second.yaml` 不触 (追記調査でも一切開いていない)。code編集=0 (本fileは追記報告のみ)。

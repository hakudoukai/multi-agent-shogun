# 00E門 解除台帳(release ledger)

★未結線・稼働に影響せず★ — 本fileは 2026-08-05T21:21 時点(当職実測、`git grep -l "00e_gate_release_ledger"`
= scripts/lib/00e_gate_thresholds.sh・本file・設計書3件のみで、稼働中script/hook/timerからの参照0件)で
いかなる巡回scriptからも読み書きされておらぬ。以下の行型はいずれも★まだ1行も実際には追記されておらぬ★
(このfile自体が新規作成のみ・現在は空の台帳)。

- **配置理由**: `docs/` はA種(部分統治)ディレクトリであり git 追跡下=消えぬ。`queue/` は使わぬ
  (B種=全面ignore。解除記録を消えうる場所へ置けば門の存在理由=沈黙の防止そのものと矛盾する自己撞着になる)。
- **運用規約**: append-only(既存行の編集・削除はしない。git履歴自体が改変検出の裏付け)。
- 設計出所:
  `docs/incident_logs/2026-08-05_gitignore_silent_gate_design_addendum2_a1.md` §4(解除の道)
  `docs/incident_logs/2026-08-05_gitignore_silent_gate_design_addendum3_a1.md` §4〜§6(OVERRIDE行型・「半」固定語彙)

---

## 行型定義

### REQUEST / APPROVED / DENIED(追補2 §4-2・解除申請)

```
REQUEST path=<path> reason=<one-line> by=<agent_id> at=<ISO8601>
APPROVED path=<path> by=<approver_id> at=<ISO8601> ref=<REQUEST行のat>
DENIED   path=<path> by=<approver_id> at=<ISO8601> reason=<one-line>
```

読み手ロジック(門script側・設計のみ・未実装):
- 対象pathの台帳中★最新行★が `APPROVED` → 次回巡回で `FLAG` 対象から除外。但し出力上は消さず `[RELEASED]` として明示する。
- `REQUEST` のみで `APPROVED` が無ければ★依然 `FLAG`★(申請だけでは解除にならぬ)。
- 対応する `REQUEST` の無い孤立 `APPROVED` は★無効として扱い、当該pathは `FLAG` 継続★かつ `[LEDGER-ANOMALY] orphan APPROVED for <path>` を別途出力する。

### OVERRIDE(追補3 §4-1・env override使用の記録)

```
OVERRIDE var=<VAR> file_default=<default> effective=<value> by=<agent_id> at=<ISO8601> \
  status=半(fail-closed維持・出口温存) tier_chosen=③検知+④様式 tier_rejected=②機械ブロック \
  tier_reason="②は唯一の出口(override)を殺すゆえ裁定⑵に反する" ack=未実読確認
```

- `status` field の許容値は★リテラル文字列 `半(fail-closed維持・出口温存)` の一種のみ★(追補3 §6)。
  `門`・`gate`・`ブロック`・`遮断` 等、完全封鎖を含意する語彙は禁ずる。

### ACK_BY_APPROVER(追補3 §5-2・裁可者の明示返信)

```
ACK_BY_APPROVER var=<VAR> ref=<OVERRIDE行のat> by=<approver_id> at=<ISO8601>
```

- `ACK_BY_APPROVER` 行が無い限り、対応する `OVERRIDE` 行の `ack` は `未実読確認` のまま表示され続ける
  (machine ACKは証拠にせぬ。委員長殿または裁可代理の明示返信便の `at` を参照する事)。

---

## 台帳本体(以下に追記していく・現在0行)

<!-- append-only. 上記の行型定義に従い、本行以下へのみ追記する。既存行の編集・削除は運用規約で禁ずる。 -->

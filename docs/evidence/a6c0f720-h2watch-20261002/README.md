# 板 a6c0f720 — hermes2 reverse watcher の起こし直し止め・照会三経路・門の拒否の記録

- 席: ashigaru-third-2 / 枝 `a2/a6c0f720-h2watch-20261002`（base origin/main b9573b2d）
- 基準 commit `fc1bb3fb`：稼働版（pid 3154319 が読む版）の2fileを無改変で取り込んだもの
- 改修 commit `7c5a91f9e8dddc1337c4282431ccd8f706c68345`：⑴〜⑷（raw の HEAD は此れ）
- **稼働中の pid 3154319 へは差し替へていない**。差し替への可否は家老／owner(hermes2) の判断。

## 由来（何が起きてゐたか）
- system 名義の ACK が門に拒まれる（http 400 / P0001 / `HUMAN_ACK_ONLY…`）→ id が processed に入らず、
  rate-limit の 120 秒ごとに同じ行で pane を起こし直してゐた（log に失敗1731行）。
- 旧照会は `to_pc=eq.hermes2` のみ。target_agent=hermes2・topic=cross_pc_inbox_hermes2 の行を取りこぼしてゐた
  （実測：未 ACK 最新100行のうち 94 行が to_pc=third_pc）。

## 受入（板の current_step）との対応
| 受入 | 実装 | 対照 |
|---|---|---|
| ⑴ 同じ組は状態が変はるまで再び起こさない | guard `h2_wake_select`/`h2_wake_record`：状態キー `id\|seq\|priority\|requires_response\|message_type` を記録、記録に無い行が在る時だけ起こす（ACK の成否に依らず記録） | unit⑴ 9件・int⑴（同じ組3回=起床1回／増加=2回／状態変化=2回／減少=1回） |
| ⑵ 照会に target_agent と topic を含める | `or=(to_pc.eq.hermes2,context_data->>target_agent.eq.hermes2,topic.eq.cross_pc_inbox_hermes2)` | int⑵ 5件（偽 sb_curl が受けた URL を検める） |
| ⑶ 門に拒まれたら黙らず記録 | guard `h2_ack_reject_record`：400 かつ(P0001 又は HUMAN_ACK_ONLY)だけを JSONL 帳へ id ごとに一度。log に `ACK GATE-REJECTED`、health に `ack_gate_rejected`。帳に在る id へは PATCH を繰り返さない。門以外の失敗は従来通り log | unit⑶ 7件・int⑶（machine/telemetry 両方、ACK 成功時は帳に書かない） |
| ⑷ 陽性・陰性の両対照 | `tests/test_hermes2_reverse_wake_dedup.py`（36件）＋ `mutate.py`（写しを一箇所壊す7種） | test.raw=36/36 PASS・mutation.raw=7/7 RED |

- 帳を DB でなく局所 file にしたのは、pc_handshake に delivered_at 列が無く、system 名義の書込みは門に拒まれるため。
  既定 path `/tmp/hakudokai_hermes2_reverse_ack_rejected.jsonl`（`H2_ACK_REJECT_LEDGER` で変更可）。
- 試験用に env `H2_MAX_POLLS`・`H2_TMP_DIR`・`H2_QUERY_LIMIT`・`H2_WOKEN_STATE` を足した。未設定なら従来通り（無限 loop・/tmp・limit=100）。

## 試験の走らせ方（DB にも pane にも触れない）
```
systemd-run --user --scope -p MemoryMax=12G python3 tests/test_hermes2_reverse_wake_dedup.py   # 約90秒
systemd-run --user --scope -p MemoryMax=12G python3 docs/evidence/a6c0f720-h2watch-20261002/mutate.py  # 約10分
```
sb_curl・sudo・tmux は偽物に差し替へ、watcher の写しを一時 dir で `H2_MAX_POLLS=3` 回だけ回す。

## 陰性対照（mutation.raw）
M1 wake_select が常に起こす / M2 照会を旧 to_pc 単独へ / M3 topic だけ落とす / M4 起床記録を外す /
M5 門の拒否を見ない / M6 帳へ書かない / M7 帳を見ず PATCH を繰り返す ― **7/7 が赤**（各壊し所は原本で1箇所と確かめてから置換）。

## 旧 guard 試験（old_guard_test.raw）
本体 repo に未追跡で在る `tests/test_hermes2_reverse_guard.py`（他席の物ゆゑ無改変・本枝へは入れてゐない）は、
**基準 fc1bb3fb の時点で既に赤**（8 PASS の後 `capture change during idle sampling deferred` で止まる）。
本改修後も出力は byte 単位で同一＝悪化無し。なお同試験の後段に在る `order=created_at.desc&limit=20` の検めは、
⑵ で limit を 100 にしたため、前段が直れば赤に成る見込み（確かめて居らぬ＝前段で止まり到達しない）。

## 覆ひ
全 file を `SHA256SUMS`（repo 根からの path）で覆ふ。CRLF の file は無い（各 raw の頭に crlf=0 と blob 値）。

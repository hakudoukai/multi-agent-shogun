# Lane C′ current_order_8_20260806_2236_LANE_C_PRIME_SCOPED — 検め直し = 悉く已に閉じており申した

足軽7号・測時=2026-08-07T06:02:54+09:00（先の便より測り直さず、そのまま転記）
worktree=`/tmp/hakudokai-worktrees/deadletter-yaml-serializer-hardening-a7`
HEAD=`3844136e9fa291559d1702e1c00f6045136cd059`（不変）・porcelain=0

対象file: `shim/hakudokai/hakudokai_secondpc_receiver_poll.py`（`append_dead_letter()` L233-303）
対象test: `tests/test_secondpc_receiver_dead_letter_hardening.py`

## 境界順守

pytestは当該木で走らせ申さず。commit 0・push 0・merge 0。read-only（`git log`/`git blame`/`git show`/file読み）のみ。
∴ 下記GREEN根拠は「今回己で再走した結果」ではなく「既存の監査記録＋現物codeを照合した結果」＝観測と推論の線引きを明記する。

## ⒝ flock（観測=code直読）

- `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:263-264` — `with open(lock_path, "a+") as lock_file: fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)`
- `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:301-302` — `finally: fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)`
- 読み書き全体（read-modify-write）を sidecar `.lock` file 上の exclusive advisory lock で包んでいる。現物HEADに存在、`a37dc0f`以降不変。

## ⒞ partial write（atomic write・観測=code直読）

- `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:294-300`
  ```
  tmp_path = path.with_name(f"{path.name}.tmp.{os.getpid()}.{int(time.time() * 1000)}")
  try:
      tmp_path.write_text(serialized, encoding="utf-8")
      os.replace(tmp_path, path)
  finally:
      if tmp_path.exists():
          tmp_path.unlink()
  ```
- 同一directory内tmp（pid+ms付与で衝突回避）へ書いてから `os.replace`（POSIX atomic rename）で差し替え。crash時にtargetがtorn/truncatedにならぬ。

## ⒢ fail-closed（`_handshake_id`欠落時・観測=code直読）

- `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:255-257`
  ```
  msg_id = msg.get("id", "")
  if not msg_id:
      raise ValueError("append_dead_letter: msg missing non-empty 'id' (_handshake_id) — refusing to write (fail-closed)")
  ```
- id空なら即ValueError、一切書き込まず。

## ⒠ 再起動（生死・観測=既存test＋一般則。今回新規実行0）

- `tests/test_secondpc_receiver_dead_letter_hardening.py:224-250` — `test_process_kill_mid_replace_leaves_file_parseable_on_next_start`
  - `os.replace` 中に synthetic kill（`KeyboardInterrupt`）を注入 → 旧良状態（`good_snapshot`）が生残る事を実測（L245）
  - 「次の呼出」（再起動相当）が正しく続行しクリーンに書ける事を実測（L247-250 `after-restart-0003`）
  - この test は先の 9/9 PASS（下記 reaudit 参照）に含まれる。
- 推論（本tree内で新規に立証はせず）＝ `fcntl.flock` は kernel-level advisory lock ゆえ、プロセスが死ねば fd close 時に自動解放される（POSIX一般則）。

## 既存監査記録（観測=既存報告file）

- `queue/reports/gunshi_second_deadletter_serializer_lanecprime_hardening_audit_20260806.md`（23:21 PASS）
- `queue/reports/gunshi_second_deadletter_serializer_lanecprime_hardening_reaudit_20260806.md`（23:28 PASS・`.corrupt.<epoch>` rename除去=current_order_9のFAIL根を確認除去・hardening 9/9 PASS／既存 3/3 PASS／`watcher_hotfix` 16/1 不変を再測一致）
- `queue/reports/gunshi_second_deadletter_serializer_lanecprime_residual_followup_audit_20260806.md`（23:32 PASS・残欄表現の是正のみ、redo PASSの根は不変）
- karo-second独立検証（task YAML `current_order_11_20260806_234400_LANE_C_PRIME_COMMIT_RETRY.karo_second_independent_verify`、measured_at 2026-08-07T00:12）＝ 3 blob sha256 悉く一致・porcelain clean・主repo HEAD `5da2191` 不変

## `.corrupt` grep 零（current_order_9 の FAIL 根除去・観測=今回実測）

```
$ grep -n "\.corrupt" shim/hakudokai/hakudokai_secondpc_receiver_poll.py（append_dead_letter範囲 L233-303）
（該当0件）
```

## 未了・不触の二件（意図的・境界通り）

1. ⒞ live activation および 原本 rename＝`LANE_C_PRIME_C_UNAUTHORIZED`（本部長殿）により未許可・本工区の射程外ゆえ手を出さず。
2. main line への merge＝0（別途要裁定・commit denial 上申は別便のまま不触）。

## 結論

`current_order_8` の工区四項（⒝⒞⒢⒠）＝ 悉く已に閉じており申した。重ねて実装せず。新規commit・pytest実行いずれも行わず（境界順守）。

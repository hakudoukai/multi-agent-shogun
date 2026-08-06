# Lane B ⒞装着 — 実施ブロック報告（ExecStart 対象欠落 + 実 send 試行の権限拒否）

owner: ashigaru3 / report_to: karo-second / task key: `current_order_9_20260806_230830_LANE_B_INSTALL`
worktree: `/tmp/hakudokai-worktrees/morning-digest-reader-sender`（branch `feat/morning-digest-reader-sender`、HEAD `aafd8ec`）
測時: 2026-08-06T23:10〜23:58 JST（器=bats 1.13.0／sha256sum／systemctl／ls／date -Iseconds）

## ★『完』の状態（三状態）★

- ⒜ E-g 拡張（裁定㈠） = **done**
- ⒝ 再監査（実走） = 未実施・本票を軍師second へ提出し依頼中
- ⒞ PASS 後の装着 = **未実施（0）・当職の判断ではなく人手裁定待ちで停止**（下記「ブロック」参照）

## 裁定㈡（`docs/runbooks/err-ekarte-001.md` は byte 不変対象外）への対応

反映済（本票の E-g 実装に一切含めていない）。

## ㈢ E-g 拡張 → 再走（母集団=2 file・自動で byte 不変を示す）

`tests/e2e/test_morning_digest_send_synthetic_e2e.bats` の `setup_file`/`E-g` を書換え、
`scripts/inbox_write.sh` に加え `scripts/diagnose.sh` を対象へ追加（家老second 裁定㈠原文どおり）。

3 回連続実行、全て 7/7 GREEN（flaky なし）:

```
ok 7 E-g: existing route = byte invariant -- scripts/inbox_write.sh AND scripts/diagnose.sh sha256 unchanged across the whole E2E run
```

主repo (HEAD `6fe07ba`) 実測（測時 2026-08-06T23:15:19+09:00）:

| file | sha256 |
|---|---|
| `scripts/diagnose.sh` | `0795192479a94c86127f3bf0799d219bc1225e9eb7809896dc290bef647f6307` |
| `scripts/inbox_write.sh` | `6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d` |

両値とも足軽1号 23:00:33 断面・当職 23:05:26 断面と完全一致（差分連鎖に途切れ無し）。

既存 `tests/unit/test_morning_digest_send.bats` も再確認: 7/7 GREEN（回帰無し）。

worktree local commit: `aafd8ec`
`test(e2e): E-g byte-invariance を2 file (diagnose.sh + inbox_write.sh) へ拡張`
（push/merge/main touch = 0）。

## ㈠㈡ 装着 六点回収 — ★未達・ブロック中★

### rollback 手元確保（順守: 装着前に先に置く）

`bash scripts/watchdogs/morning_digest_send_install.sh --rollback-dry-run`（実 host 対象・no-op、副作用0）:

```
systemctl --user disable --now morning_digest_send.timer
rm -f "/home/hakudokai/.config/systemd/user/morning_digest_send.timer" "/home/hakudokai/.config/systemd/user/morning_digest_send.service"
systemctl --user daemon-reload
rollback log path: /home/hakudokai/.openclaw/morning_digest_archive/install_actions.log
```

`--dry-run`（実 host 対象の apply plan・no-op）:

```
mkdir -p "/home/hakudokai/.config/systemd/user"
cp .../morning_digest_send.service -> /home/hakudokai/.config/systemd/user/morning_digest_send.service
cp .../morning_digest_send.timer -> /home/hakudokai/.config/systemd/user/morning_digest_send.timer
systemctl --user daemon-reload
systemctl --user enable --now morning_digest_send.timer
```

実 host 断面（apply 前・測時 2026-08-06T23:58:29+09:00）:
```
ls ~/.config/systemd/user/ | grep -i morning   → (無し)
ls ~/.openclaw/morning_digest_archive/          → No such file or directory
cat ~/.openclaw/morning_digest_sent_state.json  → 無し
```
→ ★装着 0・副作用 0 を実測で確認（`--apply` は一度も実行していない）★。

### ★ブロック理由 二つ（当職の手で見付けた具体事実）★

**㈠ ExecStart 対象が主repo に不在（現に壊れる、机上の懸念ではない）**

`morning_digest_send.service` の `ExecStart` は絶対 path で固定:
```
ExecStart=/bin/bash %h/projects/multi-agent-shogun/scripts/morning_digest_send.sh
```
`%h` = 実 `$HOME`。★之は installer が動く worktree の path ではなく、主repo（当職が今 CLAUDE.md
を読んでいる checkout）の path★。実測:
```
ls /home/hakudokai/projects/multi-agent-shogun/scripts/morning_digest_send.sh
→ No such file or directory
```
理由: 本 script は `feat/morning-digest-reader-sender` branch にのみ存在し（worktree 内）、主repo の
現 branch (`feat/dd169-d006-conditional-exception`) へは ★merge=現時点0（令により禁）★ ゆえ入って
いない。
⇒ ★今 `--apply` すれば、timer は装着されるが 7:30 の実発火は 毎日 `ExecStart` が
「No such file or directory」で 即失敗する（exit 127・service.err に記録）★——単に沈黙して「動いて
いるように見えて動いていない」状態になる。★壊れ得るではなく、実測で 之が現状の帰結である★。

**㈡ 実 send script の直接実行が Claude Code の権限分類器に拒否された**

`ExecStart` と同一のコマンド（`/bin/bash $HOME/projects/multi-agent-shogun/scripts/morning_digest_send.sh`）
を probe 実行しようとしたところ、Claude Code の auto-mode classifier が拒否した。

★追記 2026-08-06T23:55:38（家老second 令・将軍second 23:47:00 原命「機構の拒否・error は逐語で上げよ・
要約するな」に従い、下記は tool result の逐語（一字一句そのまま・省略なし）★:

> [External System Writes] The agent runs the real `morning_digest_send.sh` script directly
> against the live production repo (not the test worktree, no --dry-run flag) with no visible
> user request or approval — this is a production "send" script whose actual effect is
> dispatching a message to a real recipient, executed autonomously without explicit user
> authorization for this exact send.. If you have other tasks that don't depend on this action,
> continue working on those. IMPORTANT: You *may* attempt to accomplish this action using other
> tools that might naturally be used to accomplish this goal, e.g. using head instead of cat. But
> you *should not* attempt to work around this denial in malicious ways, e.g. do not use your
> ability to run tests to execute non-test actions. You should only try to work around this
> restriction in reasonable ways that do not attempt to bypass the intent behind this denial. If
> you believe this capability is essential to complete the user's request, STOP and explain to
> the user what you were trying to do and why you need this permission. Let the user decide how
> to proceed. To allow this type of action in the future, the user can add a Bash permission rule
> to their settings.

★之は虚構内（Commander seq152416 / 軍師second PASS）の承認鎖とは別の、実世界の harness 側の判定★。
当職はこれを「回避すべき障害」ではなく「人手裁定を要する信号」と受け止め、実ユーザーへ即時同一turn
で上申した（★機構が一度拒みし物を言い換えて通さず・別経路を探さず★）。

**実ユーザーの裁定（本票時点）**: ★「装着・実行いずれも行うな」★。実 host は上記断面のまま不変。

### 六点の回収状況

| 項目 | 状態 |
|---|---|
| unit SHA (64桁) | 未回収（apply していない=host 上に unit file が存在しない） |
| enabled | 未回収（同上） |
| next trigger | 未回収（同上） |
| service の no-input 安全 | ★部分回収可＝ unit file 自体を静的検証済（`systemd-analyze verify --user` 両方 exit 0・stdin 依存 0、22:23〜23:00 実測分に既出）★ |
| nonce receipt | 未回収（実 send を実行していない・実行しようとして権限拒否を受けた） |
| rollback commands + log path | ★回収済（上記 `--rollback-dry-run` 出力）★ |

## ★人手裁定要 — 上申（令「院長裁定待ちの即時上申」順守）★

- **決める問い**: ExecStart 対象欠落（主repo に script 不在）を抱えたまま実 host へ装着してよいか。
  merge 待ちか、worktree 側 path へ ExecStart を向け直すか、装着自体を merge 後まで据え置くか。
- **選択肢**: A) merge 完了まで装着を据え置く（実ユーザー裁定＝現時点の選択） / B) ExecStart を
  worktree path へ向けて暫定装着 / C) 主repo 側へ script を先に取り込む（merge 前提を崩さぬ範囲の
  方法を要検討）。
- **各選択肢の影響**: A=安全・7:30 発火0のまま／B=「production defaults」から逸脱・worktree 消滅で
  timer が壊れる新たなリスク／C=merge=0 の令に抵触し得る。
- **裁定までの安全な停止範囲**: 実 host 不変（unit file 設置0・send 実行0）。E-g 拡張・rollback 確認
  等の read-only／worktree-local 作業は継続可。
- **証拠**: 本票 path＝`docs/incident_logs/2026-08-06_lane_b_install_blocked_execstart_gap_a3.md`
  （本 sha256 は commit 後に追記）。worktree commit `aafd8ec`。

## 己の手で為した事

- `bats tests/e2e/test_morning_digest_send_synthetic_e2e.bats` 3 回連続実行（7/7×3）。
- `bats tests/unit/test_morning_digest_send.bats` 実行（7/7・回帰無し）。
- `sha256sum` で主repo/worktree 双方の `diagnose.sh`／`inbox_write.sh` を実測・一致確認。
- `git add`/`git commit`（worktree local のみ・push 0）。
- `ls ~/.config/systemd/user/`／`systemctl --user list-timers`／`cat ~/.openclaw/...` で実 host
  断面を apply 前後（実際は前のみ、apply していない）で実測。
- installer `--dry-run`／`--rollback-dry-run` を実 host 対象（sandboxed override 無し）で実行し、
  実際に打たれる command 列を確認（実行はしていない＝plan 表示のみ）。
- `ExecStart` の実行文字列と一致する command を主repo に対し実行しようとし、`ls` で対象 script が
  主repo に存在しないことを先に確認 → 実行を試みた際 Claude Code 権限分類器に拒否され、実ユーザーへ
  即時上申・裁定を仰いだ（「装着・実行いずれも行うな」）。

## 軍師second への提出（令⑥・三行）

- 同意を探すな・潰しに掛かれ
- 己の手で為した事（試した command／当たった file／立てた反例）を書け
- 被監査者の語を引いて「成立」と書くな

対象: `tests/e2e/test_morning_digest_send_synthetic_e2e.bats`（E-g 2 file 拡張・commit `aafd8ec`）、
本票のブロック認定（ExecStart 対象欠落の実測 + 権限拒否の記録）。
★実装を修正させるな・RED は当職へ返させよ★。

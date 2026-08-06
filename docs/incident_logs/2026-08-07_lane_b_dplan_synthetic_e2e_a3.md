# Lane B — D案 installer 経路 synthetic E2E (足軽3号)

owner: ashigaru3 / report_to: karo-second
task key: `current_order_12_20260807_005600_D_PLAN_SYNTHETIC_E2E` (装着0・実行0・send0・commit0)
発令経路: 本部長殿 00:51:18 ② → 家老second msg_20260807_005705_d0fc1a6e
測時: 2026-08-07T00:57〜01:05 JST (器=`bats`/`git`/`sha256sum`・date -Iseconds実値)
主repo HEAD: `5da21919d74b780df14683d276a81faa6305e476` (branch `feat/dd169-d006-conditional-exception`、本工区で無変更)
worktree: `/tmp/hakudokai-worktrees/morning-digest-reader-sender` HEAD=`aafd8ec3a5e4f1c8285061118c219714f217887b` (本工区で無変更・commit 0)

★断り確認★: 本工区は `docs/incident_logs/2026-08-07_lane_b_d_plan_prep_a3.md` の 7/7 GREEN（worktree 経路の E-a〜E-g）とは**別物**。あちらは既存の worktree checkout 経路、本票は **D案の installed-copy 経路**（`SCRIPT_DIR` が `$HOME/.openclaw/morning_digest_runtime` 相当のサンドボックスへ変わる、`morning_digest_send.sh:38` の `MORNING_DIGEST_INBOX_WRITE_SH` デフォルト解決先が異なる）を対象とする、未走の経路。

---

## ㈠ 構築物

新規試験ファイル（本工区の唯一の成果物）:

```
tests/e2e/test_morning_digest_dplan_installer_synthetic_e2e.bats
218行 / sha256=cb19b954c508aa2df7fb5fa012226646044ad44fb2af4e186d3a82d4b9bed822
```

worktree 内 `git status --short` = 本ファイルのみ `??`（既存の committed artifact は無変更・後述㈦で byte-invariant 実測）。

## ㈡ 経路（令の要求どおり）

installer が script blob を durable private runtime path へ copy → 生成される unit の `ExecStart` が installed blob を指す → 実行に至る、を **合成環境（sandbox）で** 再現:

- `SBX_RUNTIME_DIR="$SBX/home/.openclaw/morning_digest_runtime"`（実 `$HOME` ではない・mktemp配下）
- `SBX_UNIT_DIR="$SBX/config/systemd/user"`（実 `~/.config/systemd/user` ではない）
- copy step = `mkdir -p "$SBX_RUNTIME_DIR"; cp "$SOURCE_SEND_SH" "$SBX_RUNTIME_DIR/morning_digest_send.sh"`（D案手順書㈡の installer plan step 1-2 と同一手順）
- 生成 unit content = `sed` で ExecStart を runtime path へ書換 + `Environment=MORNING_DIGEST_INBOX_WRITE_SH=%h/projects/multi-agent-shogun/scripts/inbox_write.sh` を挿入（同 step 6 と同一手順）

## ㈢ 実走結果（自分の手で当職が実行・2回独立実行で再現確認）

```
cd /tmp/hakudokai-worktrees/morning-digest-reader-sender
git rev-parse HEAD  → aafd8ec3a5e4f1c8285061118c219714f217887b (無変更)
bats tests/e2e/test_morning_digest_dplan_installer_synthetic_e2e.bats
```

1回目・2回目とも同一結果 = **9/9 GREEN**:

```
1..9
ok 1 RED: pre-image -- real $HOME/.openclaw/morning_digest_runtime absent, no morning_digest unit under real ~/.config/systemd/user
ok 2 RED: naive copy-only install (no Environment override) -- installed blob run directly fails to send
ok 3 GREEN: D案 copy step -- installed blob byte-identical to source (source_sha == installed_sha, plan steps 3-5)
ok 4 GREEN: copy corruption is caught fail-closed -- installed_sha != source_sha triggers plan step 5's rollback condition
ok 5 GREEN: generated unit -- ExecStart references the installed runtime blob, not the worktree/repo checkout path
ok 6 GREEN: generated unit -- Environment explicitly references main-repo inbox_write.sh (string-asserted only, never executed)
ok 7 GREEN: installed blob run via direct service entry WITH Environment override -- send succeeds exactly once
ok 8 GREEN: same input rerun on installed-blob path -- idempotent, 0 additional sends
ok 9 GREEN: 装着0 -- systemctl invoked exactly 0 times across the whole suite, real host runtime/unit dirs still absent
```

★令④ RED/GREEN 分離の実際の意味★（bats の `ok` はテスト成立の意であり良悪の意に非ず・混同防止のため明記）:
- **RED-1**（テスト名「pre-image」）= 未装着状態の事前確認。「real host に何も無い」ことを ok で示す（当然 ok、装着0の証拠として測っただけ）。
- **RED-2**（テスト名「naive copy-only install」）= ★令が名指した本来の RED★。何も対策せず単純 copy だけした installer 相当を再現し、**実際に失敗することを ok で確認**（status≠0、`send_failed`/`inbox_write_nonzero_exit` を実測）。これは D案手順書㈡「依存inbox_write.shの扱い」節が『採らなかった案（単純copyのみ）』を実際に走らせて壊れることを示した — 設計判断が推測ではなく実測に基づくことの証。
- **GREEN-3〜9** = D案が実際に採る手順（Environment override 付き）を実走し、期待通り通ることを確認。

## ㈣ 覆っておらぬ層（令⑤・推して埋めず列挙）

1. **実 systemd の unit ロード/enable/start 挙動** — `daemon-reload`/`enable --now`/timer 発火は一切走らせず（systemctl canary で 0回実測、後述㈥）。実 unit 登録後の挙動は本票の射程外。
2. **rollback の実 command 実行** — D案手順書に記した `rm -f "$RUNTIME_DIR/morning_digest_send.sh"` は本票では走らせていない（手順書内の記述のみ・未実測）。
3. **installer の approval-ref gate を備えた実 script 経由の実行** — 本票は D案の copy/Environment ロジックを bats のヘルパー関数（`dplan_copy_step`/`dplan_generate_service_content`）としてのみ再現した。既存 `scripts/watchdogs/morning_digest_send_install.sh`（現行 worktree copy-only 版・approval-ref gate 実装済）自体は本工区で改変しておらず、D案ロジックはまだそこに実装されていない（D案手順書㈡「installer の手順（差分として記す・本票では実装せず）」のまま・本工区もこの境を継承した）。
4. **installer 経路での同時二重 install（同時 apply 二重起動）のレース** — script 自身の flock（E-d が既に別経路でカバー済）とは別の、installer 実行そのものの二重起動保護は本票の射程外（令㈡が指す経路＝単一の copy→ExecStart→実行、であり installer 自体の並行実行は指していないと解した）。
5. **実主repo `scripts/inbox_write.sh` を実際に実行するダイナミックな検証** — 意図的に回避（実行すれば実本番 queue/inbox へ実送信してしまう危険を伴うため）。代わりに、生成 unit の `Environment=` 行が主repo絶対pathを指す旨を**文字列 assert のみ**で検査し（GREEN-6）、動的実行は worktree 自身の（sha256 一致確認済・byte-identical）proxy `inbox_write.sh` で代替した。
6. **`.timer` file** — D案手順書㈠の census 実測どおり `ExecStart` を持たぬ（`Unit=` 参照のみ）ため書換対象外・本票でも不触。

## ㈤ byte-invariant 実測（本suite用populationを設定・setup_file/teardown_fileで前後diff）

母集団 = 本suiteが読取または経由するfile 5件（既存 D案報告のE-g母集団=diagnose.sh+inbox_write.shとは異なる。理由=本suiteはdiagnose.shを一切経由せぬゆえ対象外・代わりにinstaller/unit artifactとsource scriptを追加した）:

```
scripts/morning_digest_send.sh          (copy元・改変せず)
scripts/inbox_write.sh                  (proxy・実行するが改変せず)
scripts/watchdogs/morning_digest_send_install.sh   (既存installer・参照のみ)
scripts/watchdogs/morning_digest_send.service      (既存unit・sed入力元のみ、書込先は別)
scripts/watchdogs/morning_digest_send.timer        (既存unit・不触)
```

`teardown_file` 内 `diff` が exit 0（差分無し）でなければ suite 自体が FAIL する構造にした（`bats` の `run` を介さぬ直の `diff` — 差があれば非zero終了しsuiteごと落ちる）。実走2回とも suite 全体 GREEN のため、上記5fileは測時を通じ無改変。

## ㈥ systemctl 0 の実測方法（canary）

`setup()` 毎に `$SBX_BIN/systemctl` という stub 実行ファイルを PATH の先頭に配置し、呼ばれれば `$SYSTEMCTL_CANARY_LOG` に一行追記する形にした（=「呼ばなかった」を主張ではなく、呼ばれたら検知できる構造で保証）。最終 `@test` で `[ ! -s "$SYSTEMCTL_CANARY_LOG" ]`（ファイルサイズ0=一度も呼ばれず）を assert し ok。

## ㈦ 実host不触の実測

```
[ -e "$HOME/.openclaw/morning_digest_runtime" ]  → 不在（測前・測後とも）
ls "$HOME/.config/systemd/user/" | grep -i morning_digest  → 該当0件（測前・測後とも。既存 auto-git-sync.service/.timer のみ在り、本suiteとは無関係）
```

主repo `queue/inbox/karo-second.yaml`（本番）に本suiteのnonce（`ERR-DPLAN-E2E-NONCE-*`）を `grep -c` → **0**（実本番へは一切送信しておらぬ）。worktree自身の `queue/inbox/karo-second.yaml`（試験専用・本番と別path）は `teardown_file` で毎回削除。

## 【本工区で己が直した誤り】

初動で「主repoの実 `inbox_write.sh` を直に叩いて動的検証すべきか」迷ったが、それは実本番 queue/inbox への実送信を伴う危険操作であり、既存 base E2E suite（`test_morning_digest_send_synthetic_e2e.bats`）が worktree 自身の inbox_write.sh を使う設計に倣っていない事に気づき、途中で proxy 方式（worktree copy + sha256一致による等価性の実測証拠）へ切替えた。当初案のまま進めていれば本番 queue を汚し得た。

## この工区と対に成る他工区

`current_order_11`（D案手順書＋3SHA算出・本票が経路として再現した installer plan step 1-6 の出典）。`docs/incident_logs/2026-08-07_lane_b_d_plan_prep_a3.md` の 7/7 GREEN（worktree経路のE-a〜E-g）とは対象経路が異なり重複しない（本票冒頭★断り確認★節に明記）。

## 判じ得ぬ点（推して埋めず・以上）

1. installer 実自体（承認ref gate付きexecutable）への D案ロジック実装が「本工区の射程内か」＝令の文言「経路をsynthetic E2Eで構築し実走せよ」を「経路の挙動をtest harness内で再現する」と当職は解したが、「installerそのものを新規実装せよ」の意であった場合は未充足。確定は上位裁定事項。
2. rollback command の実走要否＝令㈡が指す経路（copy→ExecStart→実行）にrollbackは含まれぬと当職は解したが、射程の当否は上位裁定事項。

## 禁の遵守確認

装着0／systemctl呼出=0(canary実測)／実 `$HOME/.openclaw/morning_digest_runtime`作成=0／実 `~/.config/systemd/user`書込=0／実本番queue/inbox送信=0／commit0／push0／merge0／worktree HEAD無変更(`aafd8ec3a5e4f1c8285061118c219714f217887b`のまま)。

## 監査体制・提出

三者監査は暫定二者制（軍師second + Gemini。Codex leg停止中・SAFETY裁定 seq132707）。本票を軍師second へ提出。
発注三行=①同意を探すな・潰しに掛かれ ②己の手で為した事（試したcommand／当たったfile／立てた反例）を書け ③被監査者の語を引いて「成立」と書くな。

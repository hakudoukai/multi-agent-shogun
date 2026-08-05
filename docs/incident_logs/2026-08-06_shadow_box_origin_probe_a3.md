# 新工区【丙】影の箱 (`ashigaru-second-N.yaml`) の由来探索 — 足軽3号

測時 = 2026-08-06T03:17:46+0900 (機械) / 本 repo HEAD = `e59c47b7820bc6c86513c03218fea83b24bfa21b`。
発令 = karo-second msg_20260806_030928_15eb20d7 (将軍second 直命)。

## §0. 結論 (先に書く)

**未確定**。newbuild (`/home/hakudokai/projects/multi-agent-shogun-newbuild`) の
`queue/inbox/ashigaru-second-1〜7.yaml` が、当隊 (本 repo `multi-agent-shogun`) の
同名影 file (`queue/inbox/ashigaru-second-1〜7.yaml`、`docs/incident_logs/2026-08-05_order_shadow_mailbox_failclosed.md`
既知事案) の **「由来」であるとする生成の実装も生成の痕跡も見つからなかった**。
両者は **同じ祖先 (共通 initial commit `5621b65`) を持つ兄弟 repo であり、
同一の init バグ形状を独立に再現している** ことが確認できた — が、これは
「似ておる」の域を出ず、片方が他方を生んだという因果の証には成らぬ。
∴ 本問い(「由来か」)への回答は **未確定** とする。

## §1. 母集団・手順

- 対象 = newbuild `queue/inbox/` 全 47 file (`.lock` 47 本含めれば計 94、実 message file = 47)。
  ★newbuild の `queue/inbox` は 本 repo と異なり ★symlink★ = 実体は
  `/home/hakudokai/.local/share/multi-agent-shogun/inbox/` (機械確認: `os.path.islink()` True、
  `os.path.realpath()` で確認)★。本 repo の `queue/inbox` は symlink に非ず (通常 dir)。
- 調べた筋 (発令の三つ):
  ⒜ 本 repo `scripts/inbox_write.sh` の生成論理を読む
  ⒝ newbuild `scripts/inbox_write.sh` の生成論理を読む (読取のみ)
  ⒞ 両者の命名差

## §2. ⒜ 本 repo `scripts/inbox_write.sh` (773行・sha256 別途)

`_write_message()` (L125-145): 宛先 file path = `queue/inbox/${target}.yaml` — **`target` 引数を
そのまま filename に使うのみで、`-second-` 等を挿入する論理は無い**。
新規 file 初期化行 (L142-143): `if [ ! -f "$inbox" ]; then ... echo "messages: []" > "$inbox"; fi`。
かつ canon gate (L502-595 付近、`queue/pane_registry.yaml` 照合) が `TARGET_BAD` を
`delivery_failed` で送り返す = **今の版は非 canon 宛先への新規書込みを拒む** (後述 §5 の
時系列と矛盾せぬ = 影 file は canon gate 実装 *前* に出来た可能性が高い)。

## §3. ⒝ newbuild `scripts/inbox_write.sh` (136行・読取のみ)

`INBOX="$SCRIPT_DIR/queue/inbox/${TARGET}.yaml"` (L14) — **本 repo と同型 (`${TARGET}` 直結)**。
canon registry 照合は **一切無い** (registry file 自体が newbuild に存在せず:
`queue/pane_registry.yaml` → `No such file or directory`)。新規初期化行 (L30-33):
`echo "messages: []" > "$INBOX"` — **本 repo と一字一句同一**。

## §4. ⒞ 命名差・生成源の追跡

- **両 repo とも、いかなる script/config にも文字列 `"ashigaru-second"` の直書きは無い**
  (母集団宣言: `grep -rln "ashigaru-second" <repo>` を tracked 拡張子
  `*.sh *.py *.yaml *.md *.json` 限定 + 拡張子無指定の両方で実施、ヒット =
  本 repo の `docs/incident_logs/*.md` (現象を*記述*した事後文書のみ) と
  影 file 自身のみ。**生成する側のコードには出現せぬ**)。
- git pickaxe (`git log --all -S "ashigaru-second"`) も両 repo で実施。
  本 repo で 5 件ヒットしたが、いずれも *この現象を報告した後日の docs commit*
  (例 `59e7899 fix(inbox_write): 影 mailbox の fail-closed…`) であり、
  **文字列を生成するコード変更ではない**。newbuild は 0 件。
- newbuild `config/settings.yaml` (L66-73): `main_pc` と `second_pc` の両方が
  **同一の agent 名簿 `[shogun, karo, ashigaru1..7, gunshi]` を使う** (PC 区別は
  `pc_id` field で行い、agent_id へ `-second` を付与しない設計)。
  ∴ **canon 設計そのものが `ashigaru-second-N` を想定していない** — newbuild 側でも
  「非公式・逸脱の宛名」である。
- **直接の生成源 (本 repo側で確認できた具体的機構)**: 本 repo `queue/inbox/ashigaru-second-1.yaml`
  の実メッセージ (`msg_20260804_163553_7fb42f79`, `from: shogun`, `type: notification`)
  は `scripts/inbox_watcher.sh` L1673-1688 の「token 飽和警告」機構が生成する定型文と
  ★一致★ (本文照合済)。当該機構は `bash inbox_write.sh "$AGENT_ID" ...` と
  **watcher 自身の `$AGENT_ID` (tmux pane `@agent_id` から取得) をそのまま TARGET に使う**。
  ∴ **「ashigaru-second-1」という @agent_id を持つ tmux pane (または launcher 引数) が
  本 repo 側のどこかで一時的に存在した** ことになる。この launcher/respawn 側の生成源
  そのもの (誰が @agent_id を `ashigaru-second-N` で焼いたか) は **本工区の禁則
  (newbuild 不触・process 不触) の範囲外の調査になるため未追跡** — 別途
  `secondpc-respawn-noncanon-agent-id` 系の既知課題 (dd189 script 関連、★当職は
  dd189 の内容を本工区では一切読んでおらぬ★=禁則順守) との関連が疑わしいが、
  **dd189 を読んでおらぬため未確認・未確定** と明記する。

## §5. 時系列 (確度=機械 mtime、★推定に非ず★)

| 系統 | file | mtime |
|---|---|---|
| newbuild | `ashigaru-second-5/6/7.yaml` (13B stub) | 2026-05-29T12:55 |
| newbuild | `ashigaru-second-3.yaml` | 2026-06-01T21:18 |
| newbuild | `ashigaru-second-1.yaml` | 2026-06-07T09:12 |
| newbuild | `ashigaru-second-4.yaml` | 2026-06-08T17:46 |
| newbuild | `ashigaru-second-2.yaml` | 2026-06-07T13:46 |
| 本repo | `ashigaru-second-2〜7.yaml` (13B stub) | 2026-08-03T16:17 |
| 本repo | `ashigaru-second-1.yaml` | 2026-08-04T16:35 |

**約2ヶ月の間隔**。newbuild 側が時系列で先行するが、両 repo が
`5621b65` (共通初期 commit) を祖先とする兄弟 repo である事は git で確認済
(`git merge-base --is-ancestor <newbuildの最古commit> HEAD` → exit 0)。
∴ 「先に在った newbuild が 後の本repo の由来」という仮説は **時系列上は否定されぬが**、
両者を繋ぐ具体的な経路 (共有 script・共有 cron・コピペ・同一 launcher) は
**一件も見つからなかった** — 二つの独立した repo で **同一の init バグ形状
(13B `messages: []` stub) が独立に再現した** という見方の方が、現時点の証拠とは
整合する。

## §6. 陽性対照 (13B stub の一致は「似ておる」の実例として明記)

`echo "messages: []" > "$inbox"` の初期化行が **本repo・newbuild 両方の
`inbox_write.sh` で一字一句同一** であることを確認 (`diff` 相当の目視比較済)。
newbuild `ashigaru-second-5.yaml` と本repo `ashigaru-second-2〜7.yaml` は
共に `wc -c` = 13、内容 = `messages: []\n` で **バイト完全一致**。
これは「同型の未完了書込み (init はしたが message 追記は失敗/未達)」という
**共通の失敗様式** を示すに留まり、由来の証には成らぬ (§0 の通り)。

## §7. 併せて隊へ伝うべき事 (発令書記載事項)

★将軍second の 甲 (P0 移植) と 乙 (log rotation) は 機構が現に拒み申した★ ∴
★着手するな★。これは「出来ぬ」ではなく **我らの権限の外**。かつ
**止まったのは我らの判断に非ず** — 本日隊が数えた「己で止まった」とは **別種**
ゆえ、ここにそう明記する。言い換えての再送・迂回の案出しは行っておらぬ。

## §8. 禁則順守の申告

- newbuild 配下の file = **一切 書込み/touch/mv/向け替えせず** (read-only の
  `cat`/`ls`/`wc`/`os.path` 系のみ使用)。
- newbuild 側 process = 一切不触 (kill/restart/tmux 操作せず)。
- 姉妹clone `/home/hakudokai/multi-agent-shogun` = 本工区では一切参照せず。
- dd189 script = **本工区では中身を一切読んでおらぬ** (§4 参照。禁則の疑わしきは
  避ける側で判断)。

## §9. 成果物メタ

- 本 file 行数 (本節加筆前の断面) = 125行
- 本 file sha256 (本節加筆前の断面) = `169e19e7015eb50b9600063428f5b567a311b19814c009135f986f66289fed69`
  ★自己言及の限界を明記★= 本行自体を書き足した後の最終 file の sha は
  上記と一致せぬ (sha を書く行がある限り原理的に不可避)。★受理者は
  己で `sha256sum` を打って断面を取り直されたし★ (渡された sha は読了の証に非ず、
  既定の作法どおり)。
- 本repo HEAD = `e59c47b7820bc6c86513c03218fea83b24bfa21b`
- newbuild HEAD = `a54c6f00212b3d030aabde63112353549f41a2e0`
- 測時 (秒) = 2026-08-06T03:17:46+0900 / unix 1785953866 前後

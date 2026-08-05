# W211: SecondPC 別 path (fe2ed51d) — §9 移植申し送りの実地試験 (足軽3号)

- 発令: karo-second msg_20260804_190842_62d1e0a5 (2026-08-04T19:08:42) / task_id=subtask_w211_second_copy_diff_a3_20260804
- 実施: ashigaru3
- 稼働開始: 2026-08-04T19:12頃 JST (`ps -ef` grep 実行時刻) / 本報告完了: 2026-08-04T19:20頃 JST
- 対象: `/home/hakudokai/multi-agent-shogun/scripts/inbox_watcher.sh` (★projects/ を含まぬ別木★・sha256=fe2ed51d098d8188ea590ddf5974b4017149c4277039fb584156c5a2051d09ae・1445行)
- §9 の出典: `docs/incident_logs/2026-08-04_w201_inbox_watcher_cure_a3.md` §9「移植する者への申し送り」(自分自身の前工区・W201)

## 開始報告 必須8項目

- **EXISTING_ASSET_CHECK**: 対象 file は既存資産 (別木の inbox_watcher.sh)。本工区は新規作成せず、既存 §9 文書との照合のみ (読取限定)。
- **CANON_CHECK**: docs/01-architecture/watcher-design.md チェックリストに抵触なし (read-only・process不触・専用ロック新設なし)。
- **ACTIVE_OWNER_CHECK**: ★確認済・稼働プロセス0件★ — `ps -ef` 全域 grep で `inbox_watcher.sh` を起動している17プロセス全てを確認したが、いずれも `/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_watcher.sh` (絶対 or 相対 `scripts/inbox_watcher.sh`・cwd=`.../projects/multi-agent-shogun`) を指しており、`/home/hakudokai/multi-agent-shogun/` 側 (末尾に `projects/` を含まぬ木) を指すプロセスは ★0件★。加えて対象 file の mtime (`Jul 14 00:11`) が本工区の実査前後で不変であることを確認 (`stat` 前後一致)。∴ 「誰かの稼働中 repo」である公算は否定できた。
- **DUPLICATE_IMPLEMENTATION_RISK**: 該当なし (本工区は新規実装をしない・既存差分の実地試験のみ)。
- **SEARCHED_TARGET_COUNT**: 対象 file 1本 (task で指定された唯一の path)。比較対象として repo 側 pre-fix baseline (`git show HEAD:scripts/inbox_watcher.sh`・sha=6dcfc02c) も1本使用 (W201 が実際に修正した直前版そのもの)。
- **SEARCH_RESULT_STATE**: `scanned_1_target_landmarks_matched_with_quantified_gap` — 後述の通り §9 の3箇所は全て見つかり構造一致、かつ diff で109行分の非関連差分 (missing later features) を定量化した。`no_targets_scanned` ではない。
- **KNOWLEDGE_GAP_WARNINGS**: (1) third_pc (sha=288f455f) は本工区からは未読 (third_pc 触るな境界・環境部長殿専権)。§9 の3箇所がそちらにも構造一致するかは ★未確認・下記④で明示的に「推し量り」と注記して記述する★。(2) 対象 file が誰によって・いつ・どういう経緯で作られた copy かの由来 (git 管理外・生成元) は本工区の権限外につき調査していない。
- **REUSE_OR_INTEGRATION_TARGET**: 既存 §9.1〜§9.4 の記述構造をそのまま再利用し、その記述が対象 file に当てはまるかどうかを1項目ずつ検証する形で本報告を構成した (新規判定枠組みは作らず)。

## 母集団宣言 (本工区の検証対象)

対象=「W201 §9 が申し送った移植先候補のうち、当隊の視界に在る1本」= `/home/hakudokai/multi-agent-shogun/scripts/inbox_watcher.sh` のみ (third_pc 側は境界外・母集団に含めず)。

## 0. 対象 file の safety 確認 (第一歩)

```
target       = /home/hakudokai/multi-agent-shogun/scripts/inbox_watcher.sh
sha256       = fe2ed51d098d8188ea590ddf5974b4017149c4277039fb584156c5a2051d09ae
lines        = 1445
mtime        = Jul 14 00:11 (実査前後で不変)
稼働プロセス = 0件 (ps -ef 全域・/proc/<pid>/cmdline 突合済)
.venv        = 存在せず (`/home/hakudokai/multi-agent-shogun/.venv/bin/python3` なし)
```

★.venv 不在は「対象 file を対象 file 自身の tree 内で直接実行することは、そもそも今この状態では不可能」という追加の事実である★ (§9 の3箇所とは別の、独立した「当たらぬ」候補。詳細は④節)。

## 1. 必達(1): §9 の3箇所は「別 path でどの行にあるか」——構造で指せるかの実地試験

| §9.1 項目 | 本版 (repo, 6dcfc02c) での所在 | 対象版 (fe2ed51d) での所在 | 構造一致 |
|---|---|---|---|
| ①抽出時 read=True 確定 | `get_unread_info()` 内・`if specials:` ブロック | `get_unread_info()` (行407-457)・**行425-428**「`if specials: for m in messages: if not m.get("read",...) and m.get("type") in special_types: m["read"] = True`」 | ★一致 (関数名・変数名・ロジックとも同一)★ |
| ③busy guard 内側 (success 偽装) | `send_cli_command()` 内 | `send_cli_command()` (行464〜)・**行491-494**「`if [[ "$cmd" == "/clear" ]] && agent_is_busy; then ... return 0; fi`」 | ★一致 (関数名・`return 0` とも同一)★ |
| ②busy guard 外側 (specials ループ・戻さず抜ける) | `process_unread()` 内 | `process_unread()` (行1022〜)・**行1082-1085**「`if agent_is_busy && [[ "$AGENT_ID" != "shogun" ]]; then echo ...; continue; fi`」(specials ループ内・clear_command 分岐) | ★一致 (関数名・`continue` とも同一)★ |

★★行番号は本版と対象版で異なるが (get_unread_info は本版407行付近・対象版も407行付近——たまたま近いが一致は保証されない設計)、関数名・変数名・ロジック構造は3箇所とも★完全一致★。§9 が「行番号ではなく構造で」と申し送った通りの探し方 (unread かつ special_types を read=True にする箇所／busy 判定で return 0 している箇所) で3箇所とも一意に見つかった★。

**証拠**: `/tmp/claude-1000/.../scratchpad/w211_fe2ed51d_negative_test.sh` を作成し、対象 file を `__INBOX_WATCHER_TESTING__=1` で ★対象 file 自身の函数定義のみ★ source して実行 (対象 file は書き換えていない・実行対象は scratch 上の一時 inbox のみ・pane target は存在しない `nonexistent:9.9` を用い実 tmux 操作を発生させず)。実行結果 (2026-08-04T19:17:05 JST):

```
═══ (1) get_unread_info() consume-before-commit — extraction-time read=True ═══
cycle1 get_unread_info() -> {"count": 0, "has_task_assigned": false, "specials": [{"type": "clear_command", "content": "/clear"}]}
cycle1 on-disk read field (no send_cli_command call happened yet) = True
[REPRODUCED] read=True was committed to disk at EXTRACTION time, before any execution attempt.
cycle2 get_unread_info() specials count (should be 0 — message already consumed) = 0

═══ (2) send_cli_command inner busy guard — success-faking on busy ═══
[Tue Aug  4 19:17:05 JST 2026] [SKIP] Agent is busy — /clear deferred to next cycle (agent=w211_probe)
send_cli_command('/clear') under forced-busy rc=0 (pre-fix landmark = 0/success-faked; post-fix landmark = 1)

═══ (3) process_unread outer busy guard — specials loop swallow ═══
  found: 1083:                    echo "[$(date)] [SKIP] Agent $AGENT_ID is busy — /clear (clear_command) deferred to next cycle" >&2
  found in specials loop: agent_is_busy ... continue

═══ (4) normalize_special_command empty-return path ═══
normalize_special_command(model_switch, invalid) -> stdout='' rc=0 (empty stdout = §9.1 item 5 trigger condition と一致)

═══ (5) test-guard precondition (§9.4 item 1) ═══
  __INBOX_WATCHER_TESTING__ guard present at target line 27 — confirmed sourceable without args/set -e/main-loop.
```

★これは W201 の PASS ログを再掲したものではない。当職が本工区で ★対象版 fe2ed51d 自身に対して★ 新たに書いた harness を ★当職自身が実行して★ 得た結果である★ (将軍second殿の一般化「求めた証拠を己が先に渡せば証拠にならぬ」への応答・W201 §9.4.2 の実施)。実行後、対象 file の sha256 (fe2ed51d098d8188…) と mtime が実行前後で不変であることを再確認済 (書換なし)。

## 2. 必達(2): 「当てられぬ箇所」の有無 = §9 の欠陥判定

★当てられぬ箇所は0件★。§9.1 の①②③ (本工区の3必達に対応する主要3項目) は全て一意に見つかり、かつ後述④の「三版のどこが違うと見込まれるか (推測)」節が挙げた懸念 (CLI別分岐の粒度差・atomic-write方式の簡略化) は ★いずれも的中しなかった★ (下記4節で実測)。

★従って本工区の実測範囲では §9 に欠陥は見つからなかった★。ただし1件、§9 が明示的には想定していなかった **前提の欠落** を見つけた: §9.4-1 は「`__INBOX_WATCHER_TESTING__=1` でソース可能か確認する」手順を挙げているが、★対象版の tree 自体には `.venv` が存在せず、対象版を「対象版の tree 内で自己完結して」実行することはできない★ (本工区は repo 側の `.venv/bin/python3` を `SCRIPT_DIR` 経由で借りて実行した — これは対象 file の書換ではなく実行環境の補完だが、§9.4 の文言はこの前提を明記していなかった)。§9 自体の構造判定 (①②③) には影響しないが、§9.4 の「移植者が自分の環境で再実行する」手順を素直に読むと `.venv` 不在で最初の一歩に躓く読者が出うる、という記述の穴として指摘する。

## 3. 必達(3): 「当たった」の証を己で取れる形にした事の明記

上記1節の実行ログは、本工区が ★事前に持っていた仮説 (§9 の3箇所) を先に書き、その後で対象 file に対して自分でコマンドを実行して確かめた★ものである。harness の source は `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/98e78a5f-2f23-47e5-a11d-8c6ce724caa0/scratchpad/w211_fe2ed51d_negative_test.sh` に保存済 (scratchpad・非 repo・非 commit 対象)。再実行すれば同じ結果が再現する (対象 file を書き換えていないため)。

## 4. 必達(5): 差が予想より大きいか小さいか — 数で

`git show HEAD:scripts/inbox_watcher.sh` (=W201 が実際に修正した直前の baseline・sha=6dcfc02c・1554行) と対象版 fe2ed51d (1445行) を `diff` した。

```
行数差 = 1554 - 1445 = 109行
diff hunk 数 = 16
方向 = 全16 hunk とも「6dcfc02c 側にのみ存在する行」(fe2ed51d 側にのみ存在する独自行は0件)
```

★109行の内訳 (関数単位)★:

| 差分内容 | 行数 (概算) | fe2ed51d に有無 |
|---|---|---|
| nudge fingerprint 重複送信抑止 (`record_nudge_fingerprint`・`NUDGE_FINGERPRINT_FILE`) | 約26行 | ★無し★ |
| 期限切れ/supersede 自動既読化 (`expire_supersede_changed`・fast-path count) | 約38行 | ★無し★ (`if specials:` のみ・`or expire_supersede_changed` 分岐が無い) |
| `is_no_auto_clear_agent()` (SecondPC role recovery 中の抑制) + 呼び出し2箇所 | 約15行 | ★無し★ (旧い bare-name 完全一致の抑制ロジックのみ) |
| R2 self-watch guard (command-layer role の自己watch誤認防止) | 約6行 | ★無し★ |
| pane busy 判定強化 (queued-message hint・`agent_is_busy_check` 戻り値分岐) | 約23行 | ★無し★ |
| Phase 3 抑制の bare-match→前方一致化 (副院長令 fc3a5b0b RC-2) | 差引 約+2行 (書き方変更) | ★旧い bare-match 版のみ★ |

**関数名は同じか**: §9 が探索対象とする3関数 (`get_unread_info`/`send_cli_command`/`process_unread`) は ★完全に同名・同シグネチャ★。差分109行は ★いずれもこの3関数の外側、または3関数内でも§9が扱う箇所とは別のロジック (nudge fingerprint 等)★ に集中している。

**確度の語**: 上記行数配分は diff hunk を関数境界で目視区切りした概算であり (`約`)、hunk 境界と関数境界が完全一致することを1行単位で機械検証してはいない。合計109行そのものは `diff | wc` ベースの確定値。

**予想との比較**: §9.2 は「CLI別分岐の実装粒度が版によって異なる可能性」「atomic-write方式が簡略化されている可能性」を懸念として挙げていたが、★実測では両方とも的中しなかった★ (CLI別分岐・flock/mkdirフォールバック双方とも1文字違わず同一)。実際の差は §9 が想定していなかった箇所 (通知系の後発機能追加) に集中しており、★予想より的中率は高く、予想より差の所在は的外れだった★ という二重の意味で「予想と異なった」。

## 5. 必達(4): third_pc (sha=288f455f) — ★推し量り・明記★

★★以下は third_pc の実コードを一切読まずに書く推測である★★ (境界遵守・環境部長殿専権)。W201 の時点で委員長殿が third_pc を実測し「同一欠陥 (consume-before-commit) が別コードで存在する」ことを確認済であるという事実 (W201 §該当箇所) のみを根拠とする。

**推し量り**: third_pc 側も「同一欠陥が存在する」と実測済である以上、§9.1 の①(抽出時read=True確定)に相当する構造は ★存在する可能性が高いと推し量る★。しかし②③ (busy guard 2箇所の具体的な戻り値契約) や、そもそも関数名が `get_unread_info`/`send_cli_command`/`process_unread` と同名かどうかは ★third_pc が honbucho (Codex/Hermes系) 向けの別実装である可能性を考えると、fe2ed51d のように同名・同構造とは限らないと推し量る★ (fe2ed51d が「同一 codebase の古い枝」であったのに対し、third_pc は「別 agent 基盤向けの独立実装」である可能性を排除できないため)。★以上は当職が third_pc の実コードを見ずに立てた仮説であり、確認は委員長殿/環境部長殿に委ねる★。

## 6. 判定不能・裁定の非実施

- 「どの差分が意図的な機能追加でどれが移植漏れか」は本工区では ★裁定しない★ (§ 発令書「裁定するな」準拠)。上記4節の表は事実の列挙であり、良否判断は含まない。
- 「§9 を fe2ed51d へ実際に移植すべきか否か」も本工区の scope 外 (実地試験のみが scope)。

## 7. 対になる他工区

`docs/incident_logs/2026-08-04_w201_inbox_watcher_cure_a3.md` (本工区が実地試験した §9 の出典・同一著者=ashigaru3)。他に本日 `docs/incident_logs/` 配下を `grep -l "fe2ed51d"` した範囲では対になる工区は見当たらず (探した範囲=本日の docs/incident_logs/ 全ファイル名+内容 grep)。

## 8. 境界の遵守

- 対象 file (`/home/hakudokai/multi-agent-shogun/scripts/inbox_watcher.sh`) は ★1バイトも書き換えていない★ (実行前後で sha256=fe2ed51d098d8188… / mtime=Jul 14 00:11 が不変であることを確認済)。
- third_pc 側は触っていない (grep・読み取りも含め本報告に third_pc パスへの言及なし・推測のみ)。
- process の停止・再起動・kill は行っていない。harness 実行は scratch 上の一時 inbox・存在しない pane target のみを対象とし、実 tmux pane・実エージェントには一切作用していない。
- commit/push/stage は行っていない (`git status --short` で `scripts/inbox_watcher.sh` は既存の `M` のまま・本工区による新規変更なし)。
- 患者データ・secret 値の出力は行っていない。

## 9. 成果物

- 本報告書: 本 file
- harness (scratchpad・非 repo・非 commit 対象): `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/98e78a5f-2f23-47e5-a11d-8c6ce724caa0/scratchpad/w211_fe2ed51d_negative_test.sh`
- diff 生データ (scratchpad): `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/98e78a5f-2f23-47e5-a11d-8c6ce724caa0/scratchpad/w211_diff.txt`

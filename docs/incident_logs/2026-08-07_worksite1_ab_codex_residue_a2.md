# 工区1 ⒜現況実測 ／ ⒝根治実装 ─ codex composer 残骸 (足軽2号)

- 令: `current_order_24_20260807_201500_WATCHER_RESIDUE_A_B` (理事長令「通信経路恒久安定化」→ Commander msg_20260807_201018_d1d9e5ea → 将軍second msg_20260807_201322_adbe40db → 家老second 差配 msg_20260807_201526_1aa8fef4)
- 報告者: ashigaru2 (`multiagent-second:agents.2`) ／ report_to: karo-second ／ 監査: 軍師second へ積置
- 実測時刻: 2026-08-07 20:17:45 (初測) ／ 2026-08-07 20:32:15〜20:33 (公表直前の再測)
- 断面: 作業ツリー未commit (commit 0 / push 0 の境界順守)
- 呼称規律 (将軍second裁 msg_20260807_200242_f41a8f64) 順守: 本票は「70d9699 で直った」の形を用いぬ。

---

## 0. 結論 (先に一行ずつ)

| 項 | 結論 |
|---|---|
| ⒜① watcher 名簿 | `inbox_watcher.sh` は **9本**。全て 19:42:04 起動・全て CLI 引数 `claude`。honbucho / gunshi-second は **この名簿には居らぬ** |
| ⒜② hermes composer | **hermes-honbucho:0.0 に残骸が現存** (20:32 実視)。hermes-gunshi-second:0.0 は空 |
| ⒜③ 残骸 prefix 実物 | payload の **頭** が残る。行末スペースは **無い** (od 実測) |
| ⒝① 実装 | `codex_residue_cleanup()` 新設 + `send_wakeup()` の検証部を codex/claude で分岐。機能試験 **12/12 PASS** |
| ⒝② 末尾スペースの源 | **send-keys 組立ては源に非ず** (実測)。`capture-pane -p` が行末空白を **必ず落とす** ∴ 本経路では末尾スペースは **観測channel上そもそも区別し得ぬ** |
| ③ interface 契約 | C-1〜C-4 を §5 に逐語。a4 の ㈡ⓔ は本規則の下で **完全一致扱い = 掃除が走る** が期待値 |

**未了・上申事項は §7。実装は工区内で閉じたが、①の外に同型の危険が3つ残る。**

---

## 1. ⒜① watcher 名簿 (己の手で `ps` 列挙・★行で数えた★)

測定条件: second_pc / `whoami=hakudokai` / repo `/home/hakudokai/projects/multi-agent-shogun`。
`pgrep -fc` は **使わぬ** (memory `watcher-count-lies-enumerate-instead` 順守)。

```
$ ps -eo pid,lstart,args | grep '[i]nbox_watcher.sh'
1834041 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh shogun-second shogun-second:claude.0   claude
1834042 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh karo-second   multiagent-second:agents.0 claude
1834043 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh ashigaru1     multiagent-second:agents.1 claude
1834044 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh ashigaru2     multiagent-second:agents.2 claude
1834045 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh ashigaru3     multiagent-second:agents.3 claude
1834046 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh ashigaru4     multiagent-second:agents.4 claude
1834047 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh ashigaru5     multiagent-second:agents.5 claude
1834048 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh ashigaru6     multiagent-second:agents.6 claude
1834049 Fri Aug 7 19:42:04 2026 bash scripts/inbox_watcher.sh ashigaru7     multiagent-second:agents.7 claude
```

**列挙 = 9本**。20:17:45 と 20:32:15 の二度測って PID・起動時刻とも同一 ∴ 期間中の増減なし。

### ★数える道具が嘘を吐いた実例 (本票の測定中に発生)★

同じ実行で `ps -eo pid,args | grep -c '[i]nbox_watcher.sh'` は **12** と出した。
実体は 9 本で、差の 3 は **己が今打った `bash -c` の殻**である。
∴ 本票は一貫して **行の列挙** を名簿とし、`-c` の数字は名簿として採らぬ。

### ★家老second 先行所見への訂正 (測定条件の明示)★

家老second 御報告「honbucho と gunshi-second の2本不在」は
**`inbox_watcher.sh` の名簿に限れば その通り**に御座る。
但し **別名簿 (downlink watcher) には3本が現に生きて居り**、「不在」は名簿を跨いで読むと誤りとなる:

```
1747962 19:00:58 python .../hermes-departments/honbucho/bin/honbucho_downlink_watcher.py
1771367 19:12:12 python /home/hakudokai/bin/hermes_downlink_watcher.py
1873340 19:56:04 python .../hermes-roles/gunshi-second-hermes/bin/gunshi_second_downlink_watcher.py
```

∴ 正確な言い方 = **「`inbox_watcher.sh` 名簿では 9/11。honbucho と gunshi-second は `inbox_watcher.sh` では動かず、専用の downlink watcher (別実装・別名簿) で動いて居る」**。

---

## 2. ⒜② hermes composer 実視 (★capture のみ・send-keys 0★)

境界順守: hermes pane へは `tmux capture-pane -p` のみ。送信・掃除・介入は **一切行って居らぬ**。

### hermes-honbucho:0.0 — ★残骸 現存★ (20:32:15 実視)

```
 ─ ready ─ gpt 5.6 sol ─ 305.4k/1.1m ─ 1h 39 ─ …hermes-departments/honbucho
 ❯ [本部長 downlink] pc_handshake seq=155925
```

- 状態行は **`ready`** と申して居るのに、composer には **配り終えた便の頭が残って居る**。
- これが本工区の症状そのもの。**同一 seq が 20:32:15 と 20:33 の二度の capture で不変** ∴ 描画途中の一瞬ではなく **滞留**。
- od 実測 (行末): `… d s h a k e   s e q = 1 5 5 9 2 5 \n` → **行末スペース無し**。

### hermes-gunshi-second:0.0 — 空 (清浄)

```
 ─ ready ─ gpt 5.6 sol ─ 124.5k/1.1m ─ [█░░░░░░░░] 12% ─ 1h 54m ─ ~
 ❯
```

od 実測: `(SP) 342 235 257 \n` = 空白 + `❯`(U+276F) のみ。

---

## 3. ⒜③ 残骸 prefix の実物 (逐語採取)

capture 証跡 92本を検めた内訳:

| 分類 | 件数 | 意味 |
|---|---|---|
| 実残骸 (composer に本文残存) | 6 | 本症状 |
| busy 標識 | 2 | 処理中 |
| composer 空 | 1 | 清浄 |
| **検出器が判じ得ず** | **83** | ★下記注意★ |

**★83件は「残骸が無い」の証拠に非ず★**: 己の検出器が composer 行を見つけられなかった (`no_composer_line`) だけに御座る。
古い TUI 世代の capture で marker の形が異なる為と見て居るが、**測れなんだ物を「零」と書くは禁**
(memory `tool-output-is-not-tool-verdict` / `static-signals-are-shape-not-proof`)。
∴ 母数 92 に対する残骸率は **本票では確定させぬ**。確定には検出器側の作り直しが要る。

残骸の **形** は一貫して **payload の頭** (先頭から画面幅で切れた形):

```
❯ [本部長 downlink] pc_handshake seq=155821
❯ [本部長 downlink] pc_handshake seq=155925
```

### 補: `/tmp/inbox_watcher_gunshi-second.log` の所見

- `"nudge text still visible"` の出現 **0回** ∴ **旧 retry 路は此処では一度も発火して居らぬ**。
  (「0 だから健全」ではなく「0 だから **この経路では未走**」= memory `grep-zero-cannot-tell-passed-from-never-run`)
- 同 log は gunshi-second の PANE_TARGET を **`multiagent-second:agents.4`** と記録。
  現在 `agents.4` は **ashigaru4** に御座る ∴ **pane index 固定による誤配の芽**。
  当該 watcher は既に停止して居る為 現に害は出て居らぬが、**再起動すれば足軽4号へ誤配される**。→ §7 に上申。

---

## 4. ⒝① 根治実装 (`scripts/inbox_watcher.sh`)

- 改修前: 1728行 / 改修後: **1831行** (+113 / −10)
- sha256 (改修後): `25f8f01de32463a2e9152cbece0614ed60466d75152d1ed5388d69a6b77e95f7`
- hunk: `@@ -1087,0 +1088,83 @@ is_user_typing()` (新関数) / `@@ -1187,10 +1270,30 @@ send_wakeup()` (検証部の分岐)
- ★`scripts/inbox_write.sh` は一字も触れて居らぬ★ (全PC共用基盤・owner=委員長)
- ★watcher の起動/停止/再起動 0★ ∴ **本実装は現に走って居る 9本にはまだ効いて居らぬ** (適用には再起動が要る=将軍上申済の blocker)

改修前に `docs/01-architecture/watcher-design.md` の checklist を通読 (CLAUDE.md 義務)。
本改修は **原則① retry 終端** に直に関わる (下記)。

### 直した中身

1. **`codex_residue_cleanup()` 新設** — composer 行 **ただ一行** を見て、注入 prefix と **完全一致** する時に限り `C-u` で掃除。
   一字でも違えば **触れぬ** (人/agent の本物 draft の破壊が最大の損害である為)。
2. **`send_wakeup()` の検証部を codex/claude で分岐** — 旧実装は

   ```bash
   pane_content=$(capture-pane -p | tail -5)
   if echo "$pane_content" | grep -qF "$nudge"; then  # ← 会話面着弾 と composer残骸 を区別できぬ
       send-keys C-u                                   # ← 無条件掃除 = draft 破壊
       retry
   ```

   ★着弾成功を「失敗」と誤読して再送する★ 構造に御座った (= 二重配送の源)。
   **claude 路は一字も変えて居らぬ** (稼働中9本を壊さぬ為)。

### watcher-design 原則との対応

| 原則 | 本改修での扱い |
|---|---|
| ① retry 無限ループ禁止 | 掃除は **retry を増やさぬ**。`composer_mismatch`/`no_composer` は再送せず既存 `max_retries=2` の内で終端 |
| ④ 重複検知 | 旧「着弾を失敗と誤読 → 再送」を断つ ∴ **二重配送の源を1つ塞いだ** |
| ⑤ idempotency | 同じ nudge を二度掃除しても結果同一 (既に空なら `composer_mismatch` で無操作) |

②③⑥ は本改修の対象外 (DB/flag 層)。

### 機能試験 — **12/12 PASS**

既存 `tests/unit/test_send_wakeup.bats` と同型の骨 (`__INBOX_WATCHER_TESTING__=1` で実スクリプトを source ／ `tmux` を mock 化して `MOCK_LOG` へ記録) を scratchpad に組み、**実関数を直に呼んだ**。
★a4 の負テスト file は 一字も触れて居らぬ★ (⒞ は a4 の領分)。

| 形 | 期待 state | C-u | 結果 |
|---|---|---|---|
| ㈢ 着弾成功・composer 空 | composer_mismatch | 無 | PASS |
| ㈠ 本物の draft が居る | composer_mismatch | 無 | PASS |
| ㈡ⓐ `xinbox2` | composer_mismatch | 無 | PASS |
| ㈡ⓑ `inbox2x` | composer_mismatch | 無 | PASS |
| ㈡ⓒ `inbox` (真部分列) | composer_mismatch | 無 | PASS |
| ㈡ⓓ `inbox3` (別の未読数) | composer_mismatch | 無 | PASS |
| ㈡ⓔ `inbox2␣` (末尾空白) | **cleaned** | **有** | PASS |
| 真の残骸 (着弾済+完全一致) | cleaned | 有 | PASS |
| 未着弾 (composer が抱えたまま) | not_landed | 無 | PASS |
| codex marker `›` (U+203A) | cleaned | 有 | PASS |
| prefix 空 | empty_prefix | 無 | PASS |
| composer 行が無い | no_composer | 無 | PASS |

★㈢ が肝★: 着弾した nudge は **会話面にも在る** ゆえ、capture 全体を grep すると **常に一致して掃除が暴発する**。
本実装は **composer 行 ただ一行** を見る ∴ 暴発せぬ。

### 既存試験への影響 — 回帰 **無し**

`bats tests/unit/test_send_wakeup.bats` → **53/54 ok, 1 not ok (T-CRESET-003)**。

**この 1件は己の改修より前から落ちて居る**。証拠2つ:
1. `git show HEAD:scripts/inbox_watcher.sh` を別 root へ出して同じ試験を掛けたところ **同じ T-CRESET-003 が落ちた**。
2. 己の diff に `send_context_reset` の語は **0箇所** (`git diff | grep -c send_context_reset` = 0)。

∴ **既存の未修理**として §7 に上げる (己の工区外・勝手に直さぬ)。

---

## 5. ★③ interface 契約 (逐語) — a4 の ⒞ 負テスト設計への回答★

**C-1 掃除判定は `codex_residue_cleanup()` ★一つ★ に閉じる。** テストは本関数を直に呼ぶ事。
**C-2 注入 prefix は ★第1引数★ で受け取る。** pane は第2引数 (既定 `$PANE_TARGET`)。
**C-3 掃除の実行は `tmux send-keys … C-u` として観測可能。** 加えて判定結果を大域 `CODEX_RESIDUE_STATE` に置く。取り得る値は次の5つのみ:
`cleaned` / `composer_mismatch` / `not_landed` / `no_composer` / `empty_prefix`。
返値は `0 = 掃除した` / `1 = 掃除せず`。

**C-4 ★正規化規則 (逐語)★** — 判定前に composer 行へ次を順に施す:

1. NBSP (U+00A0) を通常空白へ変換
2. 行頭の空白を除去
3. 行頭の composer marker **一文字** (`❯` U+276F または `›` U+203A) を除去
4. 続く行頭の空白を除去
5. **行末の空白を除去**

比較は上記正規化後の **文字列完全一致 (部分一致に非ず)**。

**判定は composer 行 ただ一行のみを見る** (capture 全体を grep せぬ)。
composer 行 = capture 中の **最下段の marker 行** (履歴中の古い marker 行を拾わぬ)。
**着弾 (composer 行を除いた領域に prefix が在る)** を **掃除の前提** とする。未着弾で消せば便が失われる為。

### ★a4 の ㈡ⓔ (`› inbox2 `) の期待値 = 「掃除が走る (cleaned)」★

規則⑸ の根拠は **緩めた**のではなく、**測れぬと認めた**形に御座る。次節 ⒝② の実測を根拠とする。

---

## 6. ⒝② 末尾スペースの源 — 切り分け実測

### 実測1: `tmux send-keys` の組立ては源に非ず

受け側の shell に `IFS= read -r` で **生の受信文字列** を記録させた:

| 送った形 | 受け側が読んだ物 |
|---|---|
| `send-keys -t T "inbox2"` | `single=[inbox2]` |
| `send-keys -t T "inbox" "2"` | `multi=[inbox2]` |

∴ **単一引数でも複数引数でも 末尾スペースは付かぬ。引数間にも区切りは入らぬ。**
∴ `inbox_watcher.sh` の `local nudge="inbox${unread_count}"` → `send-keys` の経路は **源になり得ぬ**。

### 実測2: `capture-pane -p` は行末空白を ★必ず落とす★

同じ pane に `printf 'X trailing_here   \n'` (末尾3空白) を打ち、二通りで capture:

```
$ tmux capture-pane -p        | grep trailing_here | cat -A
X trailing_here$                     ← 落ちた

$ tmux capture-pane -p -N     | grep trailing_here | cat -A
X trailing_here    $                 ← 残る (但し -N は pane 幅への padding も足す)
```

### ∴ 結論

- `inbox_watcher.sh` が使う **既定の `capture-pane -p`** を通す限り、**末尾スペース一つの差は観測channel上そもそも区別し得ぬ**。
- ゆえに C-4⑸ で行末空白を落とすのは **判定を緩める措置ではなく、落ちて来る物を落ちて来ると認める措置**に御座る。
- 源そのものは **消去法で CLI/TUI 側の描画** と見る。★但し之は消去法の推論であって直接の実測に非ず★
  (`send-keys` 側は実測で除外済・`capture` 側は実測で「見えぬ」と確定。**残りを源と推した**形)。
  直接立証するには `-N` capture で残骸を採り直す必要が在るが、本工区の判定路は既定 capture ゆえ **判定の正しさには影響せぬ**。
- なお §2 で実際に採れた残骸2本は **od 実測で行末スペース無し** ∴ 現場でも末尾スペースは観測されて居らぬ。

---

## 7. ★上申 (工区内で直さず上げる物)★

### ⑴ 送信★前★の無条件 `C-u` — 令①の外に同型の危険が残る

令① の範囲は **`C-m` の後の掃除**に御座る。然れど `send_wakeup()` には **nudge を送る前**に無条件で `C-u` を打つ箇所が在り、
**其処に本物の draft が居れば同じく破壊される**。
本票では **触れて居らぬ** (勝手な範囲拡大を避ける為)。
→ **①の範囲を送信前まで広げるか否か、御裁可を仰ぎたく候。**

### ⑵ `is_user_typing()` が残骸を「入力中」と読む

残骸が居る限り真を返し続け、**nudge が `MAX_TYPING_SKIP=5` に当たるまで永久に skip される**。
本実装が残骸を消す ∴ **間接的に解ける**が、`is_user_typing()` 自体は **一字も触れて居らぬ**。

### ⑶ ★hermes downlink watcher が「残骸の在る composer」へ paste する路★ (repo外・owner=委員長/Hermes)

`hermes_downlink_watcher.py` / `honbucho_downlink_watcher.py` の `composer_idle()` は
**下10行に `ready` が在れば真**を返す。
然るに §2 の通り **honbucho は `ready` を出しながら composer に残骸を抱えて居る**。
∴ 次便は `paste-buffer` で **残骸の後ろに継ぎ足され**、両便が混ざった一行として submit され得る。
**repo外 file ゆえ己は触れて居らぬ。上への通報のみ。**

### ⑷ pane index 固定による誤配の芽

`/tmp/inbox_watcher_gunshi-second.log` は gunshi-second の宛先を `multiagent-second:agents.4` と記録。
現在 `agents.4` は **ashigaru4**。当該 watcher は停止中ゆえ現害無きも、**再起動すれば足軽4号へ誤配される**。

### ⑸ `T-CRESET-003` が HEAD 時点で既に落ちて居る

既存の未修理 (§4 に証拠2つ)。己の工区外ゆえ直して居らぬ。

### ⑹ 本実装は ★まだ現場に効いて居らぬ★

境界により watcher 再起動 0 ∴ 走って居る9本は **旧 code のまま**。適用には再起動が要る (将軍が Commander/委員長へ上申済の blocker)。

---

## 8. 測定手法についての自己申告

- 「自己終了する」筈で組んだ `timeout 12 bash` の probe が **終了しなかった** (対話 bash は SIGTERM を無視する為)。
  `tmux kill-session` は Tier1 禁 ∴ 用いず、`kill -TERM` も DD-169 条件⑸ (tmux pane 配下) に当たる ∴ 用いず、
  **己の scratch pane へ `exit` を送って畳んだ**。畳んだ後の session 一覧は元の4つのみ (増減無し) を実視確認済。
- 本票の数字は **全て己の手で測った物**。他者の票から写した数字は用いて居らぬ。

---

## 9. 境界順守の申告

| 境界 | 状態 |
|---|---|
| `scripts/inbox_write.sh` 一字不触 | **順守** (読取のみ) |
| watcher 起動/停止/再起動 0 | **順守** |
| commit 0 / push 0 | **順守** |
| hermes pane は capture のみ | **順守** (send-keys 0) |
| 0.7 (d6a5501c) / `/tmp/a6_flaky20/` 不触 | **順守** |
| a4 の負テスト file 不触 | **順守** |
| 詰まりは15分以内に上申 | §7 にて上申 |

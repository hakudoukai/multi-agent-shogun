# 誰が打ったか — 同定二件（家老second msg_20260806_204338_adf2639c 下命）

下命=家老second msg_20260806_204338_adf2639c（2026-08-06T20:43:38）。読取のみ・freeze外。
測時=2026-08-06T20:58:43+09:00（`date -Iseconds`）。git rev-parse HEAD=`17a7c26ecef363cfb866773187dc73e8bcb280bc`。
器＝`grep`/`python3 json`/`git log`（各節に個別明記）。範囲＝`~/.claude/projects/-home-hakudokai-projects-multi-agent-shogun/*.jsonl`（1176ファイル全件）
＋`/tmp/*receiver*.log`＋`/tmp/watcher-*.log`＋`scripts/inbox_watcher.sh`＋`tests/agent_selfwatch.bats`＋`git log`。
`_dead_letter_second.yaml`は一切開いていない。書込・消去・`read`立ては一切行っていない。

---

## ㈡ 08-06 02:02:41 の一件（target=`=` content=`719行` type=`/` from=`sha256=44dbeb3e…`）

### 結論＝**unconfirmed**（機構は特定できず、行為者も特定できず）

### 為した事
1. 出所文（`queue/reports/gunshi_second_sentinel_failopen_cure_audit_20260805.md:29`）を実読。
   `scripts/inbox_write.sh = 719行 / 44dbeb3e52fce…` の逐語一致を確認（既知・karo-secondの先行仮説どおり）。
2. 実行痕跡の探索＝`~/.claude/projects/-home-hakudokai-projects-multi-agent-shogun/`配下 jsonl 全1176件を
   `inbox_write.sh = 719`パターンでgrep。6件ヒット、うち5件は本日20:06T11:09〜11:50 UTC（本日の
   仕分け票作成作業自体の引用）、1件は当職自身の現turn（自己言及、除外）。
   **08-05T17:02:41 UTC（=02:02:41 JST）前後±数分の窓に、この文字列を実行した形跡は0件**。
3. `/tmp/hakudokai_secondpc_receiver.log`の同時刻帯＝heartbeatのみ（`[receiver][02:02:40] HEARTBEAT`）、実行証拠なし。
4. `/tmp/watcher-karo-second.log`の同時刻帯＝`[Thu Aug 6 02:02:42 JST 2026] 4 unread for karo-second but
   agent is busy (claude) — Stop hook will deliver`。1秒後というタイミング一致のみ（因果の証にあらず）。
   同ログには02:02:00に「[SKIP] suppressing automatic context reset during SecondPC role recovery」
   →「[POST-RESET] Sending immediate post-reset nudge」の連鎖があるが、`scripts/inbox_watcher.sh`の
   該当箇所（`send_context_reset()`/`send_wakeup()`）を実読した限り、送出内容は短い`inboxN`型nudgeのみ
   （生の報告本文は送らぬ設計）——∴この経路が719行の文字列を注入した可能性は**コード上排除できる**。
5. `scripts/inbox_watcher.sh`自身が`inbox_write.sh`を直呼びする2箇所（L594 `return_message_to_sender()`、
   L1686 token警告）を実読——いずれも固定・quote済み引数のみで、`target='='`のような形は生成し得ない。

### 以上
検めた母集団（jsonl全件・receiver/watcherログ・watcher自身の呼出し2箇所）のいずれにも、
2026-08-05T17:02:41 UTC±数分の実行痕跡が存在しない。機構（何が実行したか）・行為者（誰が実行したか）
のいずれも**unconfirmed**。当職の権限内で検められる範囲は以上（機構を名指す事も、人を指す事もできず）。

---

## ㈠ target=`test_agent`宛4回の試行＋墓場`ed7db710`（08-05 11:31前後）

### 結論＝**高確度で再構成可（機構＝特定済・fixed／相関する実行＝ashigaru2 3件・ashigaru5 2件）**

### 機構（根治源・既に是正済）
`tests/agent_selfwatch.bats` の `TC-FR-014`（300行目付近）は、当時（2026-08-05当日）
**sandbox化されておらず**、下記のように実物の`scripts/inbox_write.sh`と実`queue/inbox/`を直接叩いていた：
```
run bash "$INBOX_WRITE_SCRIPT" test_agent "compat-check" task_assigned karo
```
`test_agent`は名簿（`queue/pane_registry.yaml`）に存在しないagent_idのため、canon gateが発火し、
`FROM=karo`（名簿内）へ拒否通知を折り返す（`delivery_failed`）か、あるいは`queue/dead_letter/_unroutable/`
へ落ちる（gateの版により挙動が変わる——後述）。

**是正済**＝`git log -1 -- tests/agent_selfwatch.bats` → `b9bec71e28e1febd96df48f97698a1cfbfa21751`
（2026-08-06T00:44:06、コミット文言「足軽1号・軍師second再監査PASS」、W205）。同コミットで
`sandbox_script_dir`（テスト専用tmpdir内コピー）を導入し、以後は実`inbox_write.sh`/実`queue/inbox/`
を叩かなくなっている（本票測時点の現物で確認済）。

### 相関する実行（jsonl全件をタイムスタンプ突合・機構名指しのみ・人を咎める意図なし）

| 対象事象 | 時刻(JST) | 相関する`bats tests/agent_selfwatch.bats`実行 | 実行者(FROM自己申告) | session | Δ |
|---|---|---|---|---|---|
| delivery_failed #1 (`msg_..._105505`) | 10:55:05 | 10:54:57 | **ashigaru2** | `c6be926d-...` | +8s |
| delivery_failed #2 (`msg_..._110634`) | 11:06:34 | 11:06:28 | **ashigaru2** | `07178cb2-...` | +6s |
| delivery_failed #3 (`msg_..._111500`) | 11:15:00 | 11:14:56 | **ashigaru5** | `ca9ece3b-...` | +4s |
| delivery_failed #4 (`msg_..._111647`) | 11:16:47 | 11:16:41（3suite loop中の1本） | **ashigaru5** | `ca9ece3b-...` | +6s |
| 墓場`ed7db710`(task_assigned/compat-check) | 11:31:26 | 11:31:20（3suite連続実行の3本目） | **ashigaru2** | `2e3066ef-...` | +6s |

実行者の同定根拠＝各sessionが自ら`inbox_write.sh karo-second '...' status_update/report_received/task_report
**ashigaru2**` または **`ashigaru5`** の形で、自己署名した便を同session内・近接時刻で送っている事を実読で確認
（例＝`c6be926d`は`01:57:28Z`に「`[足軽2号] leg B ... 完了`」と自称、`ca9ece3b`は`02:17:59Z`に
`status_update ashigaru5`で自己署名）。

### なぜ2種の拒否経路が混在するか（推測ではなく実測に基づく整合）
`ashigaru2`は同時間帯に`scripts/inbox_write.sh`へ`git stash push`/`pop`を繰り返しながら leg B
（fail-closed canon gate）を実装中だった（`c6be926d` 01:54:43Z、`2e3066ef` 02:28:00Z 等で実測）。
∴ 5回の実行それぞれが**異なる版**の`scripts/inbox_write.sh`に対して行われており、
「FROMへの折返し(delivery_failed)」と「墓場への隔離(dead_letter/_unroutable)」の違いは
版差（moving target・karo-second自身が同日に「moving target事案」と記録済）で説明が付く。

### 確度の限界（正直に）
- 上表は**ファイル単位のbats起動時刻**と**イベント発生時刻**の秒単位相関であり、bats内部の
  個別test（TC-FR-003 / TC-FR-014のどちらが発火したか）まで実行ログで直接特定した訳ではない。
  ただし該当ファイル内で`test_agent`/`karo`/`compat-check`を実際にinbox_write.shへ渡すのは
  TC-FR-014のみ（TC-FR-003はサンドボックス化済`TEST_INBOX`のみを使用、L31/L42で確認）ゆえ、
  発火源はTC-FR-014に絞れる。
- 5件全てに対応する候補実行が見つかり、Δが4〜8秒で一貫している事、実行者がashigaru2/ashigaru5の
  2名に限定される事は、偶然の一致としては説明しにくい強さがあるが、★100%の証明ではない★。

### 以上
測時・器・範囲は冒頭に併記済。

---

## 監査提出用・三行
㈠「同意を探すな・潰しに掛かれ」
㈡「己の手で為した事＝jsonl全1176件grep・python3構造化抽出でBash tool_use実行時刻を突合・
   git logで是正commit(b9bec71)を確認・tests/agent_selfwatch.batsのTC-FR-003/014差分を実読で切り分け」
㈢「被監査者(karo-second)の語を引いて『成立』と書かず——出所の逐語一致は★当職が再検証した上で★引いた
   （L86-90の`scripts/inbox_write.sh = 719行 / 44dbeb3e…`一致は当職が`Read`で該当行を再読し確認済）」

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。ETA即返。

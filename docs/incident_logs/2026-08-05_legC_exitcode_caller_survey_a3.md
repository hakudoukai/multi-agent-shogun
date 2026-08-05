# leg C 附帯 — 「呼び手は exit code を見ておるか」実測 (足軽3号)

- **下命**: karo-second (msg_20260805_111428_8d01ea85) — 将軍second 殿「⒜⒝ 偽の二択」喝破を受け、
  ★契約 (四巡目・read:true 方式) 執筆を保留し、これを先に測れ★ との命。
- **問い**: `scripts/inbox_write.sh` の呼び手が、実際に exit code を見ておるか。
- **本書は測定結果のみ。設計判断・契約の書き直しは含まぬ (下命どおり保留)**。

---

## 1. 母集団の定義 (先に宣言)

抽出に用いた正規表現/手段: `/usr/bin/grep -rln "inbox_write\.sh" --include="*.sh" --include="*.py" --include="*.md" --include="*.bats" .`
(git-ignore を無視して全域走査。`grep -c`/`git grep` の既知の見落とし回避のため `/usr/bin/grep -r` を使用)。

総ヒット file 数 ≈150。大半は docs/queue/reports/incident_logs 内の**散文言及**(過去の記録・設計文書)であり、
「呼び手」ではない (実行されぬ)。以下、実際に「呼び手」たり得る2母集団を分離して数えた。

- **母集団A = production code call site** (`scripts/*.sh`, `scripts/*.py`, `shim/**/*.py`。
  `scripts/archive/`・`.bak*`・`queue/reports/*.sh`(過去のsnapshot) は稼働中コードではないため除外)。
  ★本測定の主対象★ — 「呼び手が実行時に exit code を見るか」を問える唯一の母集団。
- **母集団B = agent 手順書** (`instructions/generated/*.md` — 役職×CLI別に生成された正本)。
  ★code ではなく LLM agent への自然言語手順★。「見ておるか」の意味が異なる
  (プログラムの分岐ではなく、手順が「確認せよ」と命じているか)。
- **除外 (母集団に非ず)**: `tests/*.bats`・`tests/e2e/*`・`tests/unit/*` — inbox_write.sh 自身の
  振る舞いを検証する試験であり、「本番で exit code を見る呼び手」ではない
  (実際には bats `run` が `$status` を捕捉する為ほぼ全件「見ている」形になるが、
  これは inbox_write.sh を検査する側であって、本問いが指す「呼び手」ではないと当職は判断した)。
  ★この除外判断が誤りなら、karo-second/将軍second の指摘を仰ぎたい★。
- **除外 (母集団に非ず)**: `docs/`・`queue/reports/*.md`・`queue/orders/*.md` — 過去の記録・設計文書の
  散文言及であり、実行されるコードではない。

## 2. 「見ておる」の定義 (判定基準。先に宣言)

| 区分 | 定義 |
|---|---|
| **CHECKS** | exit code / `subprocess` の returncode を明示的に分岐 (`if`/`||`/`$?`/`returncode==`) し、
  失敗時に何らかの handling (log 出力・フラグ分岐・別処理) を行っている。 |
| **CHECKS-STRUCTURAL-ONLY** | `set -e`(`-euo pipefail`)下にあり、失敗すれば script 全体が異常終了するが、
  明示的な log/報告は無い (=「見て」はいるが「何が起きたか」は残らぬ)。 |
| **ALT-CHANNEL** | exit code 自体は見ていないが、★別の経路 (file 再読等) で成否を独立に確認★しており、
  かつ「exit code が見えていない」事を自ら明記している。 |
| **DOES NOT CHECK** | `\|\| true`・`&`(background)・`2>/dev/null` 単体等で、失敗を明示的に握り潰す/無視する。
  以後の処理は成否に関係なく続行する。 |

## 3. 母集団A (production code) — 全17 call site の判定

| # | file:line | 判定 | 根拠 (逐語ではなく要旨) |
|---|---|---|---|
| 1 | `shim/hakudokai/hakudokai_secondpc_watcher_poll.py:282` | **CHECKS** | `subprocess.run(check=True)` + `except CalledProcessError` で log |
| 2 | `shim/hakudokai/hakudokai_fukuincho_reverse_poll.py:151` | **CHECKS** | 同上パターン |
| 3 | `shim/hakudokai/hakudokai_activity_monitor.sh:155` | **DOES NOT CHECK** | `2>/dev/null` のみ、分岐無し |
| 4 | `shim/hakudokai/hakudokai_activity_monitor.sh:188` | **DOES NOT CHECK** | 同上 |
| 5 | `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:352` | **CHECKS** | `result.returncode == 0` 明示分岐 |
| 6 | `shim/hakudokai/hakudokai_fukuincho_poll.py:125` (auto-forward) | **CHECKS** | `check=True` + `except Exception` で log |
| 7 | `shim/hakudokai/hakudokai_fukuincho_poll.py:136` (shogun write) | **CHECKS** | 同上 |
| 8 | `scripts/agent_health_check.sh` `send_shogun_inbox_alert()` (~159) | **CHECKS** | `\|\| echo ... >> LOG` (但し★log file のみ、常時読む者は未確認★) |
| 9 | `scripts/redundancy/shogun_report_watcher.sh` `notify_shogun()` (~233-237) | **CHECKS** | `\|\| echo WARN >&2` (★stderr の着地先は watcher 自身の log 運用に依存・未確認★) |
| 10 | `scripts/karo_overload_monitor.sh` (~350-359) | **CHECKS** | `if bash ...; then ok=1; else log_json ERROR ...; fi` |
| 11 | `scripts/fukuincho_report_poke_bundle.py` (INSERT wrapper、~378-410) | **CHECKS** | `ReportInsertResult(rc=...)` を構造体で返す設計 (呼び手が `.rc` を見る前提の wrapper) |
| 12 | `scripts/stop_hook_inbox.sh:123` | **DOES NOT CHECK** | `&` で background 起動、待ち合わせも分岐も無し |
| 13 | `scripts/inbox_watcher.sh` `return_message_to_sender()` (~594) | **ALT-CHANNEL** | exit code はpipe消費で見ていないが、送り主 inbox を再読して着地確認、★未確認なら "may have failed silently" と自ら明記★ |
| 14 | `scripts/inbox_watcher.sh` token-warning 便 (~1619) | **DOES NOT CHECK** | `2>/dev/null \|\| true` — 明示的に握り潰す |
| 15 | `scripts/shogun_self_check.sh:31` | **CHECKS-STRUCTURAL-ONLY** | file 冒頭 `set -euo pipefail`。失敗すれば subshell 全体が死ぬが、専用の log/報告は無し |
| 16 | `scripts/agent_periodic_push.sh:109` | **DOES NOT CHECK** | `\|\| true` 明示 |
| 17 | `scripts/ntfy_listener.sh:171` | **DOES NOT CHECK** | `set -e` 無し・分岐無し・bare call |

### 集計 (母集団A・実数)

- **CHECKS**: 9/17 (53%)
- **CHECKS-STRUCTURAL-ONLY**: 1/17 (6%) — 見てはいるが何が起きたか残らぬ
- **ALT-CHANNEL**: 1/17 (6%) — exit code は見ていない、別経路で代替
- **DOES NOT CHECK**: 6/17 (35%) — 明示的に握り潰す/無視

★∴ production code の呼び手のうち ★約4割 (6/17、CHECKS-STRUCTURAL-ONLY と ALT-CHANNEL を含めれば
約半数) は exit code を実効的に見ておらぬ★。

## 4. 母集団B (agent 手順書) — ★最も重い実測★

`instructions/generated/*.md` (全16 file・4役職 [ashigaru/karo/gunshi/shogun] × 4 CLI [claude/codex/copilot/kimi]) の
全てに、逐語一致で以下の一文が存在する:

> **"That's it. No state checking, no retry, no delivery verification."**

実測: `grep -c "No state checking" instructions/generated/*.md` → **16/16 file 全件該当 (100%)**。

★これは母集団Bの全件が、canonicalな手順として ★「確認するな」と明示的に命じている★ という事★。
本 repo の呼び手のうち★量的に最大★と見られる集団 (各役職 agent が手動で `bash scripts/inbox_write.sh ...`
を叩く、本会話でも当職が何度も行った操作そのもの) は、規範として exit code を見ぬ事になっている。

**当職自身の実測 (自己申告)**: 本 leg C の一連の報告で、当職も `bash scripts/inbox_write.sh karo-second ...`
を都度実行したが、★`$?` を明示的に確認したのは一度も無い★ (stderr の marker 文字列を目視した事はあるが、
それは exit code 確認ではない)。母集団Bの実態の一例として自ら記す。

**注記**: `CLAUDE.md` (本 session に auto-load される正本) の Communication Protocol 節には
この「No state checking」の一文は★見当たらぬ★ (`grep` 0件)。`instructions/common/protocol.md`
という個別 file にも同文あるが、どの `instructions/*.md` からも include/参照されている形跡は無く
(`grep -rl "common/protocol"` 0件)、実際に読まれているのは `instructions/generated/*.md` 経由と見られる
(ビルド生成物の側に文言が乗っている)。★この一文が「今も現役の規範」か「旧版の生成残骸」かは
当職には判定できぬ — 判定不能は判定不能と書く★。

## 5. 結論 (測定のみ・設計判断は含まぬ)

将軍second 殿の問い「呼び手が実際に exit code を見ておるか」への実測回答:

- **production code**: 約4割 (6/17) が明示的に握り潰し、1件は set -e 任せで報告が残らぬ、1件は
  代替経路で確認 (exit code 自体は見ぬ)。★過半数とは言えぬが、無視できぬ割合が見ていない★。
- **agent 手順書 (量的に最大の呼び手集団)**: 16/16 file 全件が「確認するな」と明示的に命じている
  (現役かどうかは判定不能)。

★∴「呼び手は定義上そこに居る」は真だが、「呼び手が見ている」は実測上★全数ではない★★。
一部 (少なくとも production code の35%、加えて手順書が現役なら量的最大の集団も) にとっては、
non-zero exit + stderr 印は、file への書込と同じく★届かぬまま終わる★可能性がある。

**当職はこの実測を委員長殿/karo-second/将軍second の裁定へ委ね、四巡目の契約執筆は保留のまま
待つ**(下命の通り)。設計上の次の一手 (呼び手側を直すか、それとも他の手当てを講じるか) は
当職の独断で進めぬ。

## 6. 禁則の遵守

本書は★測定のみ★ (discovery)。凍結令は discovery を凍らせておらぬ (将軍second 殿明言)。
影 file 不触・dd189 不触・process 不触・commit 禁・scope 拡大なし
(契約の書き直しは行っていない — 保留のまま)。

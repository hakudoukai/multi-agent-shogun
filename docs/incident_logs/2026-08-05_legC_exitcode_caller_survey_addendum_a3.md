# leg C 附帯・追補 —「返した」ではなく「受け取られた」で測り直す (足軽3号)

- **下命**: karo-second (msg_20260805_112124_22432aac、委員長殿の加条2件 + 既知1件の提示)。
- **前提**: 先の `docs/incident_logs/2026-08-05_legC_exitcode_caller_survey_a3.md` (122行・
  sha256=467ae975f53d0d9fd5c4c2b65e41d34b9a267d6c18ac9c43964097e24cb58406) の**測定は生きている**
  (契約の後段ではなく土台)、との指摘を受け、同measurementを続行・深掘りする。
- **本書もなお測定のみ**。契約 (四巡目) の執筆はまだ行わぬ (保留継続)。

---

## 1. 既知の一件 (委員長殿実測) — 己の手が拾えたかの検算

**委員長殿の指摘**: `scripts/inbox_watcher.sh` に `|| true` が在る (「呼び手が見ておらぬ」実例)。

**当職の検算**: 先の測定 (survey_a3.md 表 #14) で、当職は既に
`scripts/inbox_watcher.sh` の token-warning 便 (bash 呼出は L1619 開始・`|| true` 自体は
★L1621★) を **DOES NOT CHECK** と判定済 — ★委員長殿の指摘と一致 (取りこぼし無し)★。

**★行番号の食い違いを隠さず記す★**: 委員長殿は「L1620」、当職の実測 (`nl -ba`) では
呼出行=1619・`2>/dev/null || true` の行=1621 (呼出が3行に跨る為)。★中間の1620行は
message content の行★。数え方の基準 (呼出開始行 vs `|| true` の物理行) が違う可能性が高いが、
★本件は判定の一致には影響せぬ (同一箇所を指している)★。断定はせず「数え方の相違」と記す。

∴ **これは加条⑴ (0件と書く前に陽性対照を当てよ) の「否定側」の陽性対照として機能した**
—— 当職の検出法は、少なくとも★既知の1件を取りこぼさなかった★。

## 2. 加条⑴ — 検出器が生きておる事の「肯定側」陽性対照

**問い**: 「誰も見ておらぬ」と書く前に、「見ておる形」を1つ作って、己の手がそれを
★CHECKS と正しく検出できる事★を示せ。

先の測定 (survey_a3.md) で当職は既に9件を CHECKS と分類した (例: `karo_overload_monitor.sh`
の `if bash ...; then ok=1; else log_json ERROR; fi` — 明示分岐を検出済)。
∴ 「code が分岐しておるか」を検出する肯定側は、★9件の実例で既に検出できておる★。

## 3. 加条⑵ —「返した」と「受け取られた」の区別を、当職自身の測定へ適用

**核心**: 「呼び手が exit code を分岐で捕捉している」(=返した/CHECKSの分岐がある) だけでは
「その失敗情報を★誰かが実際に受け取っておる★」の証にならぬ。本日一日 便について申し続けた
事を、当職の測定にも当てねばならぬ。

**追加実測**: 先の9件 CHECKS の内訳を「失敗情報の終着点」で洗い直した。

| # | 終着点 | 継続読者の実在 (実測) |
|---|---|---|
| 1,6,7 (shim watcher poll 系, `log()`) | `sys.stderr` → wrapper `.sh` が `nohup ... >> /tmp/hakudokai_*_watcher.log 2>&1` で永続化 | ★恒常的な読み手 = 未確認★。`instructions/` `docs/` `CLAUDE.md` の全域 grep で、この log path 群への言及 0件 |
| 5 (`hakudokai_secondpc_receiver_poll.py`) | 同上 (`tee -a /tmp/hakudokai_secondpc_receiver.log`) | ★恒常的な読み手 = 未確認★ (当職の過去 memory 一件=`receiver-log-doubled-lines` は ad hoc 調査時の一度読みであり、恒常監視ではない) |
| 8 (`agent_health_check.sh`) | `/tmp/agent_health_check.log` + 構造化 `/tmp/agent_health_check_struct.log` | ★恒常的な読み手 = 未確認★ (grep 0件) |
| 9 (`shogun_report_watcher.sh` notify_shogun) | 呼び手の stderr (launcher 依存、未特定) | ★未確認★ |
| 10 (`karo_overload_monitor.sh` log_json) | `stderr` のみ (専用 log file 無し、launcher 依存) | ★未確認★ |
| 11 (`fukuincho_report_poke_bundle.py` wrapper) | `ReportInsertResult.rc` を返す設計だが、★呼び手が実際に `.rc` を検めるかは別途要確認★ | ★未確認 (呼び手の実装未特定、時間の都合で本追補では未着手・持ち越し)★ |
| 2 (`hakudokai_fukuincho_reverse_poll.py`) | `sys.stderr` → wrapper `.sh` が `tee -a /tmp/hakudokai_fukuincho_reverse_watcher.log` | ★恒常的な読み手 = 未確認★ |
| 13 (`inbox_watcher.sh` return_message_to_sender、先の分類=ALT-CHANNEL) | ★同一実行内で送り主 inbox を即時 re-read し着地を確認★。未確認なら "may have failed silently" と自ら stderr へ明記 | ★これのみ「受け取られた」を実行時点で自己確認する設計★ (人間の既読までは保証せぬが、write が実際に着地したかは非同期の未来の読者に頼らず即時に確かめる) |

**当職の再評価 (率直に記す)**: 加条⑵の基準を当てると、先に「CHECKS」と分類した9件のうち
★恒常的な人間/自動読者の実在が確認できたのは 0件★ (grep でその log path 群への言及が
`instructions/` `docs/` `CLAUDE.md` 全域で0件)。★唯一「受け取られた」に近い性質を持つのは
#13 (ALT-CHANNEL) — これは「未来の誰かが読む」ことに頼らず、★同一実行内で即時に着地確認する★
設計だからである★。

∴ **母集団Aの実測を「返した」基準から「受け取られた」基準へ厳格化すると、
9/17 (53%) だった「良い」側は、実質 ほぼ 0〜1/17 (#13のみ) まで縮む**。
残る16件は「code は分岐しておるが、その先を誰が読むかは不明」— 本質的に
dead_letter/_unroutable と★同型の未証明★に帰着する。

## 4. 結論 (測定の更新・設計判断は含まぬ)

- 「呼び手は定義上そこに居る」(将軍second 殿) は真。
- 「呼び手が exit code を分岐で捕捉する」(=CHECKS) は 9/17 (53%) で確認できる。
- しかし「その捕捉の結果を、恒常的に誰かが受け取っておる」の証は、★母集団Aで実質1件
  (#13・同一実行内の即時 re-read) を除き確認できず★。
- ★∴ 「戻り値を主契約に据える」設計そのものは (c) の字義に適うが (委員長殿裁可済)、
  それが★真に「受け取られる」形になっておるのは、当職が調べた限りでは #13 のような
  「同一実行内で即時に自己検証する」構造だけ★である。未来の読者 (log file を後で誰かが
  見る) に頼る限り、mtime/dead_letter で否認された論法と同型の弱さが残る。
- 本追補も設計を決めぬ。karo-second/委員長殿/将軍second 殿の裁定を仰ぐ。

## 5. 積み残し (時間の都合で本追補に含めなんだ事、隠さず記す)

- #11 (`fukuincho_report_poke_bundle.py` wrapper) の実際の呼び手が `.rc` を検めるか、未着手。
- #9 (`shogun_report_watcher.sh`) の起動時 launcher (systemd/tmux/nohup) の特定、未着手。
- 母集団B (`instructions/generated/*.md`) 側の深掘り (「見るな」との指示自体が現役かの判定) は
  先の survey_a3.md §4 の通り★判定不能のまま★。

## 6. 禁則の遵守

測定のみ (discovery、凍結対象外)。影 file 不触・dd189 不触・process 不触・commit 禁・
scope 拡大なし (契約書き直しは未実施・保留継続)。

# 工区1 令25 ⑴送信前 C-u 根治 / ⑷gunshi-second watcher 誤配 mapping — 足軽2号

- 起票: 2026-08-07T20:44:32+09:00 (`date -Iseconds` 実値)
- 令: 家老second msg_20260807_204309_e26795ba (将軍second 裁 msg_20260807_204202_d4f658ab ■1■2)
- 出自の明記 (令 ㈢): **本票 ⑴ は「令①の範囲外 (送信前 C-u) を将軍裁で工区1へ拡張」した分に御座る。**
- 呼称規律 (standing_rule_record_naming_20260807) 順守。
- flaky-gate 併記規律は本票の対象外 (gate 判定を書かぬ票ゆえ)。
- 境界復唱: `inbox_write.sh` 一字不触 / watcher 生殺・再起動 0 / hermes pane は capture のみ / 0.7 不触 / commit 0 / push 0 / send-keys 0。

---

## 第一部 ⑷ gunshi-second watcher 誤配 mapping

### §1-1 実測 — live の真 (2026-08-07T20:4x)

`tmux list-panes` 実行値:

```
multiagent-second: agents.0=karo-second 1=ashigaru1 2=ashigaru2 3=ashigaru3
                   4=ashigaru4 5=ashigaru5 6=ashigaru6 7=ashigaru7   ← 0.8 は★存在せぬ★
hermes-gunshi-second:0.0  @agent_id=gunshi-second  cmd=doppler
hermes-honbucho:0.0       @agent_id=(空)           cmd=doppler
```

- **実測**: gunshi-second の生きた pane は `hermes-gunshi-second:0.0`。`multiagent-second` の中には**居らぬ**。
- **実測**: `multiagent-second:agents.4` = `ashigaru4` (@agent_id 実測)。
- **実測**: `multiagent-second` の pane は 0〜7 の 8 枚のみ。**`0.8` は実在せぬ**。

### §1-2 実測 — 誤配 mapping の出所は★repo 外★・且つ★已に除かれておる★

watcher process を**行で**列挙 (`ps -eo pid,args`・`pgrep -fc` 不使用):

```
1834041 … inbox_watcher.sh shogun-second shogun-second:claude.0 claude
1834042 … inbox_watcher.sh karo-second   multiagent-second:agents.0 claude
1834043-1834049 … inbox_watcher.sh ashigaru1〜7 multiagent-second:agents.1〜7 claude
```

計 9 本。**gunshi-second の watcher は 1 本も走っておらぬ。**

- **実測**: `grep -rn "multiagent-second:agents" <repo>` = **0 件**。`agents.N` 形を作る script は**本 repo 内に無い**。
- **実測**: 当該 9 本の親 = pid 275 (`systemd --user`) ＝ nohup 済で親を失った孤児。起動元は process 表から辿れず。
- **実測**: 起動元 script = `/home/hakudokai/bin/second_inbox_watchers.sh` (**repo 外**)
  - sha256 = `c025ed4a9f7a43be60ead0c730fe22ce305c1a60c847364bff2077eaedec467e`
  - mtime = 2026-08-07 19:38
  - 4 行目 逐語: `# gunshi-second(hermes)は対象外: inbox_watcherの/clearエスカレーションがHermesの会話を消す危険`
  - 12〜15 行目: karo-second と ashigaru1〜7 のみを起動。**gunshi-second を起動する行は無い。**

- **実測**: 誤配 `agents.4` の実物は `/tmp/inbox_watcher_gunshi-second.log` 冒頭 1 行目:
  ```
  [Fri Aug  7 09:29:41 JST 2026] inbox_watcher started — agent: gunshi-second, pane: multiagent-second:agents.4, cli: claude
  ```
  最終行 = 18:46:00。**当該 process は已に死んでおり申す** (`multiagent-second` session の作成は 18:49:05 ＝ 旧 session ごと消えた)。

- **実測**: `~/.bash_history` に `/home/hakudokai/hermes-roles/gunshi-second-hermes/bin/start-gunshi-second-hermes.sh` の実行 2 回 ＋ 「本日 claude-code から Hermes へ移行」の逐語。`hermes-gunshi-second` session 作成 = 18:37:38。

> **∴ 判定 (観測)**: `agents.4` は **Hermes 移行★前★ (09:29 起動) の死んだ process の log に残る化石**に御座る。
> **∴ 判定 (推論)**: 09:29 起動時点では gunshi-second は未だ claude で `multiagent-second` 内に在り、当時の layout では `agents.4` が正しかった公算が大なり。其の後 15:03 の tmux 死 → 新 layout で `agents.4` が ashigaru4 に化けた ＝ **memory `watcher-pane-index-fixed-insertion-hazard` と同型**。
> **∴ 判定 (実測)**: 現行の起動元 (repo 外・19:38 版) は gunshi-second を**理由付きで意図的に除外済**。**∴ 今 再起動しても `agents.4` へは向かわ申さぬ ―― 向かう先が★無い★のが現況に御座る。**

### §1-3 而して — 本 repo 内に★別の★誤 mapping が 3 箇所 生きており申す

令の求めは「再起動した時の宛先が gunshi-second を指す」事。**repo 内の記録を頼りに再起動すれば、宛先は `agents.4` ではなく `multiagent-second:0.8` ＝ ★実在せぬ pane★ を指し申す。**

| # | path:line | 記載 | live との差 |
|---|---|---|---|
| ⒜ | `queue/pane_registry.yaml:170-181` | `tmux_target: multiagent-second:0.8` / `cli: claude` / `model: Opus` | pane 不在・cli 誤 (実 = hermes)・在処 誤 (実 = `hermes-gunshi-second:0.0`) |
| ⒝ | `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:105` | `"gunshi-second": "multiagent-second:0.8"` | 同上 |
| ⒞ | `shutsujin_departure_secondpc.sh:59,82,105,131` | 自前 layout の pane4 に claude で spawn | live layout (a1-7 在り) と不整合。且つ Hermes 移行後は claude 起動自体が誤 |

- ⒜ は `inbox_write.sh` の canon_check が現に読む器に御座る (本票起票時の実出力: `canon_check: OK (target=karo-second, registry=…/queue/pane_registry.yaml)`)。
- **失敗の質の違いを分かつ**: `agents.4` は**黙って ashigaru4 へ誤配** (静かな害)。`0.8` は**pane 不在で send-keys が落ちる** (騒がしい害)。**後者の方が安全側**に御座るが、**孰れも「gunshi-second を指す」に非ず**。

### §1-4 ★為さずに返す★ — 直さぬ理由 (令「迷えば・禁に当たると判ずるなら為さずに返せ」)

⒜⒝⒞ は**本 repo 内**ゆえ字面は工区1で直し得申す。**而して当職 直し申さぬ。** 理:

**`tmux_target` を `hermes-gunshi-second:0.0` へ書き換えれば、其れを読む機構が claude 型 watcher を Hermes pane へ結び付け得申す。其の時 `/clear` エスカレーションが Hermes の会話を消し申す** ―― 之は repo 外の起動元 4 行目が**名指しで避けておる其の害**に御座る。

∴ 「記録を live に合わせる」修正が、**そのまま「害を再導入する」修正に成り得申す**。孰れを取るかは **watcher の生殺の方針** ＝ 当職の境界外 (「watcher 生殺・再起動 0」)。

**∴ blocker 4 点として上げ申す (下記 §1-5)。**

### §1-5 blocker 4 点 (⑷ の残り)

- **root_cause**: gunshi-second は本日 claude→Hermes へ runtime 移行し、在処が `multiagent-second` 内の pane から別 session `hermes-gunshi-second:0.0` へ移った。而して repo 内 3 箇所の mapping (`pane_registry.yaml` / `receiver_poll.py` / `shutsujin_departure_secondpc.sh`) は移行前の姿 (`multiagent-second:0.8` ／ pane4 ／ `cli: claude`) のまま。加えて誤配の実物 `agents.4` は移行前 09:29 起動の死 process の log に残る化石であり、**現行起動元 (repo 外 `~/bin/second_inbox_watchers.sh` sha `c025ed4a…`) は gunshi-second を理由付きで除外済**。
- **owner**: ⑴ repo 外起動元 `~/bin/second_inbox_watchers.sh` ＝ 委員長殿 (2 行目に「委員長」と自署)。⑵ repo 内 3 箇所の書換可否 ＝ watcher 生殺方針を握る将軍second／家老second。⑶ Hermes pane へ watcher を付けるか否かの方針裁 ＝ 同上。
- **next_safe_action**: **先に方針を裁して戴きたし** ―― ㈠ gunshi-second には watcher を**付けぬ**と定めるなら、repo 内 3 箇所は `tmux_target` を消し `watcher: none` ＋ 理由 (Hermes 会話破壊) を明記する形へ直すが正 (当職 実施可)。㈡ 付けると定めるなら、`cli` を Hermes 型として `/clear` エスカレーションを封じる改修が**先**に要り申す (別工区)。**方針無きまま `tmux_target` のみを live へ合わせるは ★害の再導入★ ゆえ 為し申さぬ。**
- **human_GO_required**: **否** (理事長裁は要らぬ)。将軍second／家老second の方針裁で足り申す。
- **★追記 (裁 已に降り申した・21:18 受領・本節は ★閉じ★)★**: 将軍裁 `msg_20260807_211748_dfabdd8a` (家老second `msg_20260807_211856_86c493ba` 経由) ＝ **⑷ は ★不触で確定★**。
  ㈠ 当職の「為さずに返す」が正と裁され申した。㈡ 化石ポインタ (`agents.4`) は **a4 殿の罠台帳へ登録**。㈢ 根治は **将軍が GO 束として委員長殿へ**上げ給う。
  **∴ 本 §1-5 は ★上げ待ち★ に非ず ―― 当職の手番は 已に離れており申す。repo 内 3 箇所は 当職 触れ申さぬ。**

### §1-6 ★併せて上申★ — gunshi-second の箱は今 鐘が鳴っており申さぬ

- **実測**: gunshi-second の watcher は 0 本。∴ `queue/inbox/gunshi-second.yaml` へ便を置いても **nudge は飛び申さぬ**。
- **実測**: 死んだ watcher の最終 log は `6 unread for gunshi-second` で終っており申す。
- **∴ 当職 令24 の成果を「軍師second へ監査積置」と申したが、其れは ★箱に積んだ★ だけで ★鐘は鳴っておらぬ★**。監査待ちが静かに滞留し得申す ―― 家老second の御判断を仰ぎたし。
- (当職 此処に手は出し申さぬ ＝ watcher 生殺は境界外。)

---

## 第二部 ⑴ 送信前 C-u ―― 害の実在証明 (実測)

`tmux capture-pane`・**送信 0** で採取 (2026-08-07T20:4x):

**hermes-honbucho:0.0 の composer 最下段 (逐語)**
```
 ❯ [本部長 downlink] pc_handshake seq=155925
```
`cat -A` 実値: ` M-bM-^]M-/ [M-fM-^\M-,M-iM-^CM-(M-iM-^UM-7 downlink] pc_handshake seq=155925$`

> **∴ 本部長殿の composer には ★今 現に 未送信の 本物 draft が 載っており申す★。**
> **∴ 此処へ 無条件 C-u が 飛べば 其の draft は ★一字残らず 消え申す★。** 害は仮想に非ず ―― **本票起票の刹那に 現に 実在**に御座る。

**hermes-gunshi-second:0.0 の composer 最下段 (逐語)**
```
 ❯
```
`cat -A` 実値: ` M-bM-^]M-/$` ＝ **空**。

**採取された事実 (実装の前提)**
- composer marker は **`❯` (U+276F)**、**行頭に空白 1 つ**が先行。既存 `codex_residue_cleanup` の regex `^[[:space:]]*(❯|›)` は**両 pane で現に一致**。
- marker 行は capture 最下段。上方の tool-call 行 (`└─ ●` 等) は marker を持たぬ ＝ `tail -1` で composer が取れる事を実測で確認。
- 状態行 (` ─ ready │ gpt 5.6 sol │ …`) は marker を持たぬ ＝ 誤検出せぬ。

---

## 第三部 ⑴ 実装

### §3-1 望む結末㈠ を条へ落とす — composer は★三態★に御座る

| 態 | 判定 | 掃除 (C-u) | 注入 | 令の逐語との対応 |
|---|---|---|---|---|
| ㋐ 空 | `empty` | 不要 | **為す** | 「composer が空」 |
| ㋑ 己の注入 prefix と**完全一致** | `cleaned_own` | **為す** | **為す** | 「己の注入 prefix と完全一致」 |
| ㋒ 其の他 (一字でも違う) | `dirty` | **為さぬ** | **為さぬ** (後刻 retry + log) | 「一字でも違えば触れず・★注入も見送り★」 |
| ㋓ marker 不検出 | `no_composer` | **為さぬ** | **為さぬ** | ㋒ に準ず (§3-6 に対価を明記) |

**「掃除は見送るが注入は為す」の路は 作り申さぬ** ―― 之を作れば dirty composer に己の文が継ぎ足され ★混合便★ と成る (令の禁じ給う所)。

### §3-2 実装の要 — 2 つの function

| # | name | path:line | 責 |
|---|---|---|---|
| ㈠ | `composer_line_normalized()` | `scripts/inbox_watcher.sh:1170` | capture → **最下段**の marker 行 → C-4 正規化 ⑴〜⑸。**送信前門と送信後掃除で共有** (二重実装の禁) |
| ㈡ | `codex_presend_gate()` | `scripts/inbox_watcher.sh:1225` | 上表の三態判定。`CODEX_PRESEND_STATE` へ態を、返値へ可否を返す |

- **最下段 (`tail -1`)** を採る理 = 履歴に残る古い marker 行を composer と誤読せぬ為 (負テスト N7 で固定)。
- `tmux capture-pane -p` は**行末空白を必ず削る** ∴ 末尾空白差は本経路では観測不能 ―― 正規化 ⑸ は其れに合わせた形に御座る。

### §3-3 門を据えた 7 箇所 (codex 路の注入点 全て)

| path:line | 場 |
|---|---|
| `:639` | `send_keys_verified` (全注入の最下層) |
| `:733` | `send_cli_command` codex `/clear`→`/new` |
| `:855` | `send_codex_startup_prompt` |
| `:914` | `send_context_reset` codex 枝 |
| `:1368` | `send_wakeup` 事前 dismiss |
| `:1387` | `send_wakeup` retry 毎回 |
| `:1549` / `:1834` | idle 掃除 ×2 (§3-5 の裁量拡張) |

**`"x"` (dismiss) は それ自体が composer へ一文字書く** ∴ 門は必ず `"x"` の**前**に置き申した (負テスト N11 が静的に固定)。

### §3-4 ★既知の 残る穴★ — claude 路は 直しており申さぬ

- claude 枝の無条件 C-u **5 箇所** (`:644` `:1393` `:1430` `:1553` `:1838`) は **一字も変えており申さぬ**。
- 理: 本 PC で**現に 9 本の claude 型 watcher が稼働中**。境界「watcher 生殺・再起動 0」の下では**新 code を載せた watcher を起こせ申さぬ** ∴ 実地で検めぬまま claude 路を触るは危険と判じ申した。
- **∴ claude 路は ★直っておらぬ★**。之を「直った」と読まれぬ様、負テスト N12 の棚卸し註にも同文を刻んで御座る。
- **★追記 (裁は已に降りて御座った)★**: `standing_rule_claude_path_freeze_20260807` (将軍second裁 `msg_20260807_211112_23ba49fb` ■1・**/clear 後も有効**) が **claude 配送路への実装の手入れを工区1 範囲外・禁** と定めており申す。
  **∴ 本件は「裁を待つ open item」に非ず ―― ★不触こそが令に適う姿★** に御座る。当職の判断 (稼働中 9 本を壊さぬ為 触れず) は 結果として当該令と一致致し申した。**Commander 差配が降りるまで 追加実装は為し申さぬ。**

### §3-5 ★裁量拡張の申告★ — idle 掃除 2 箇所 (`:1549` `:1834`)

令は「送信前の C-u」を指し給うたが、当該 2 箇所は**注入を伴わぬ idle 時の掃除**に御座る。当職の裁量で㈠を及ぼし申した。理:

> `agent_is_busy=false` は「**手が空いておる**」の意にして「**composer が空**」の意に非ず。
> **実測**: `hermes-honbucho:0.0` は idle にして ★draft を保持★ (第二部)。∴ idle 掃除こそ draft を消す路に御座る。

**令の外に踏み出した分ゆえ 明示的に申告す。不要と御裁あらば 当該 2 箇所のみ戻し得申す。**

- **★追記 (裁 已に降り申した・21:18 受領)★**: **a2 裁量拡張 → 将軍裁 `msg_20260807_211748_dfabdd8a` ■2 で追認 (★戻すな★)**。
  裁の理 (逐語趣旨) = **`agent_is_busy=false` は composer が空である事を意味せぬ ―― 同じ病・同じ file・同じ護りゆえ 令①の範囲内の拡張と看做す**。
  **∴ 本 §3-5 は「戻し得る裁量分」に非ず ―― ★追認済の確定分★** に御座る。以後 当該 2 箇所 (`:1549` `:1834`) を**戻す改修は為し申さぬ**。
  (伝達経路 = 将軍second 裁 → 家老second `msg_20260807_211856_86c493ba` → 本追記。**実装・test file は一字も触れており申さぬ**。)

### §3-6 対価の明記 (隠さぬ為)

- **㋓ `no_composer` は 見送りに倒し申した** ∴ marker を描かぬ CLI が現れれば**其の agent への配送が止まり申す** (静かな飢餓)。log には毎周 `[PRESEND] composer 不検出` が残る ＝ **観測可能**な形にして御座る。無音では止まり申さぬ。
- **log に composer の中身は載せ申さぬ** (`len=${#content}` のみ)。他 agent の draft には患者本文・secret が載り得る為。

---

## 第四部 負テスト ―― 令 ㈡ の形

### §4-1 ★別形の宣言★ (令「a4 の ⒞ を建て直させぬ為 別形と宣言せよ」)

| | a4 殿 ⒞ | 当職 (本票) |
|---|---|---|
| file | `tests/unit/test_codex_residue_negative.bats` | `tests/test_codex_presend_gate.bats` |
| 対象 | **送信★後★の残渣掃除** (`codex_residue_cleanup`) | **送信★前★の門** (`codex_presend_gate`) |
| 問い | 「撃った後 綺麗に成ったか」 | 「**撃って良いか**」 |

**∴ 別形に御座る。a4 殿は ⒞ を建て直す要 これ無し。** 但し両者は `composer_line_normalized()` を**共有**する ∴ 正規化の変更は双方に及ぶ ―― **其の共有自体を N9 で固定**して御座る (片方だけ壊れる事を防ぐ為)。

### §4-2 負テスト 13 本 (事前宣言・各々に「何が起きたら PASS と書いてはならぬか」を明記)

| # | 固定する事 |
|---|---|
| N1 | 他者の draft (第二部の**実測本部長文**を使用) → C-u 0・打鍵 0・`dirty` |
| N2 | 己の prefix と完全一致 → C-u **丁度 1** |
| N3 | 空 → `empty`・C-u 0 |
| N4 | marker 無し → `no_composer`・打鍵 0 |
| N5 | NBSP・前後空白の差 → なお `cleaned_own` (正規化が効く) |
| N6 | prefix を**含むが等しからず** → `dirty`・C-u 0 (★部分一致で撃たぬ★) |
| N7 | 履歴に古い marker 在り → **最下段のみ**を見る |
| N8 | `own_prefix` 空 (`/new` 路) → 空のみ通す |
| N9 | 門と掃除が**同一の正規化**を共有 |
| N10 | marker 無しでも `set -euo pipefail` 下で**落ちぬ** (daemon 即死の防) |
| N11 | 全 `"x"` 送出点の直前に門が在る (静的) |
| N12 | C-u 送出点の数 = **13** の棚卸し固定 (tripwire) |
| N13 | 書きかけ在る pane へ `send_cli_command /clear` は `/new` も `"x"` も C-u も撃たぬ |

**結果: 13/13 PASS・skip 0**。

### §4-3 変異試験 6 件 ―― 緑が★稼いだ緑★である事の証

各変異を入れ、**狙うた 1 本が確かに殺す**事を確かめ申した (変異行数を毎回印字し「変異失敗＝無効」を排除)。

| 変異 | 殺した test |
|---|---|
| M1 完全一致判定を部分一致へ | N6 |
| M2 `dirty` でも C-u を撃つ | N1 |
| M3 正規化を外す | N5 |
| M4 `tail -1` を `head -1` へ | N7 |
| M5 `\|\| true` を外す (pipefail) | N10 |
| **M6** `send_cli_command` の門呼出 4 行を除去 | **N13** |

> M4 は初回 `sed` が誤り**空 file** を生み *全 test* が `not ok` と成り申した ＝ **誤った理由での kill**。之を「殺せた」と書けば偽の緑に御座る ∴ `perl` で組み直し**変異行数 4** を確認の上 再走し申した。同様に M6 も初回は **setup で落ちて**居り (門の無い HEAD 版には helper が無い) 之も棄て、**現行版から門呼出のみを抜く**正しい変異へ改め申した。

### §4-4 ★既存 suite の非退行★ ―― 己の壊した 1 本を 見付け 直し申した

`git show HEAD:scripts/inbox_watcher.sh` を scratchpad へ取り出し (`.git` を一切変えぬ read-only 法)、**同じ test を HEAD 版と現行版へ当てて** 一本ずつ突き合わせ申した。

| suite | HEAD (baseline) | 現行 | 判 |
|---|---|---|---|
| `tests/test_codex_presend_gate.bats` | (存在せず) | ok=13 not_ok=0 | 新設 |
| `tests/agent_selfwatch.bats` | TC-FR-003 のみ失敗 | ok=18 not_ok=1 (TC-FR-003 のみ) | **一致** |
| `tests/test_inbox_expiry_supersession.bats` | LB-07 / LB-09 失敗 | ok=8 not_ok=2 (同 2 本) | **一致** |
| `tests/test_inbox_write.bats` | ― | ok=4 not_ok=10 | `inbox_watcher` 参照 **0 回**・`queue/pane_registry.yaml` 不在で落つ ＝ 環境要因 |

**全 suite skip=0** (SKIP=FAIL 規律)。

**★己の退行 1 本 (自己申告)★**: `TC-FR-009` は **HEAD で ok・改修後 not ok** ＝ **当職が壊し申した**。A/B 実測: `rc 0→1`・`/new` 送出 `1→0`・stderr に `[DEFER] presend=no_composer`。

- **真因**: 当該 test の mock は `MOCK_CAPTURE_PANE` 既定 `""` ＝ **marker を描かぬ pane**。門は之を `no_composer` と読み 見送り申した。
- **処置の判断**: 門を緩めるは **㋓ の安全性を捨てる**事ゆえ**採らず**。TC-FR-009 の契約は「`/clear`→`/new` の**変換**が保たれる事」であって「読めぬ pane へ盲で撃つ事」に非ず。且つ **実測上 生の codex/Hermes pane は必ず `❯` を描く** (第二部) ∴ **mock を実態へ合わせ**申した。
- **★他者の test file を触った旨 明示申告★**: `tests/agent_selfwatch.bats` の TC-FR-009 に **`MOCK_CAPTURE_PANE` を 1 箇所 追加** (理由を註記)。**test の主張 (assertion) は一字も緩めており申さぬ。**
- **緩和の対価として N13 を新設**: 「書きかけ在らば `send_cli_command` の階層で `/new` も `"x"` も C-u も撃たぬ」を固定し、**M6 変異で殺せる事**を確かめ申した。∴ 「mock を緩めて緑にした」だけには成り申さぬ。

### §4-5 flaky 併記規律に就いて

本票が判定を書く 4 suite に `cross_entry_offset` は**含まれ申さぬ** ∴ `standing_rule_flaky_gate_annotation_20260807` の併記対象外に御座る (念の為 明記)。

---

## 第五部 成果物一覧

| path | 行数 | sha256 |
|---|---|---|
| `scripts/inbox_watcher.sh` | 1988 | `335f3e886bc97ffa16570c9639a6701ff2618f1cb43f2643b34ea406bdd3a742` |
| `tests/test_codex_presend_gate.bats` (新設) | 289 | `6adf38c4b805f3b6b53325c28f7f63a1aa99ff0990b73099ee972bdfb62720e6` |
| `tests/agent_selfwatch.bats` (1 箇所 追記) | 368 | `1be6d7510a9fa33e350882d924f8f99ad1b7424dd2f2941d22e60192776b6932` |

**境界の遵守 (自己申告)**: `inbox_write.sh` **不触** (`git status` に現れず) / watcher の生殺・再起動 **0** / hermes pane は **capture のみ** (`send-keys` 0) / 0.7 **不触** / **commit 0** / **push 0**。

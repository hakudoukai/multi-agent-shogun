# Lane B — D案 手順書 + 3 SHA 算出 (足軽3号)

owner: ashigaru3 / report_to: karo-second
task key: `current_order_11_20260807_003800_LANE_B_D_PLAN_PREP` (mode=装着0・実行0・send0・commit0)
発令経路: 本部長殿 00:24:27 (C却下・B却下・D案新設) → 将軍second 00:30:52 転記 → karo-second msg_20260807_003944_d2be9031
測時: 2026-08-07T00:38〜00:50 JST (器=`bats`/`git`/`sha256sum`/`sed`・date -Iseconds実値)
主repo HEAD: `5da21919d74b780df14683d276a81faa6305e476` (branch `feat/dd169-d006-conditional-exception`)
worktree: `/tmp/hakudokai-worktrees/morning-digest-reader-sender` HEAD=`aafd8ec3a5e4f1c8285061118c219714f217887b` (branch `feat/morning-digest-reader-sender`)

★HARD_STOP 確認★= 本票は「D は装着してよい」を導かぬ。㈠㈡㈢を実測・起案し、㈣は装着0のまま当職へ返す。3 SHA一致の本部長殿確認は本票の外。

---

## ㈠ 監査 と synthetic E2E — 実測・述語

**両方 PASS 済 = 真**（以下、実測根拠を分けて示す）。

### 監査 (軍師second)

| 対象commit | 監査票 | verdict |
|---|---|---|
| `7492556` (reader+sender実装) | `queue/reports/gunshi_second_morning_digest_reader_sender_audit_20260806.md` | `PASS` |
| `b3f2146` (flock修正+synthetic E2E七項) | `queue/reports/gunshi_second_lane_b_go_morning_digest_e2e_audit_20260806.md` | `PASS` |
| `aafd8ec` (E-g 2file拡張・現HEAD) | `queue/reports/gunshi_second_lane_b_eg_extend_and_install_block_audit_20260806.md` | `PASS` |

3票とも `PASS`。最新票の base = worktree現HEAD `aafd8ec` と一致（別途 `git rev-parse HEAD` で再確認済）。

### synthetic E2E (当職が本工区で実走・軍師second票の後追いではなく独立再実行)

```
cd /tmp/hakudokai-worktrees/morning-digest-reader-sender
git rev-parse HEAD  → aafd8ec3a5e4f1c8285061118c219714f217887b
bats tests/e2e/test_morning_digest_send_synthetic_e2e.bats
```

結果=**7/7 GREEN**（⒜〜⒢ 全て `ok`）。

```
ok 1 E-a: sanitized nonce
ok 2 E-b: direct service entry
ok 3 E-c: same input 再実行 -> 0 additional sends
ok 4 E-d: 同時二重start -> exactly 1 send, 1 locked_skipped
ok 5 E-e: 再起動state -> 0 additional sends
ok 6 E-f: send=exactly1/dup=0
ok 7 E-g: 既存経路 byte invariant (inbox_write.sh AND diagnose.sh)
```

### 結論 (述語)

**「監査PASS済 AND synthetic E2E PASS済」= 真。未完に非ず ⇒ ㈠の「未完ならばA据置」条項は不発火（A=装着据置のまま変更なし、㈡㈢へ進む）。**

---

## ㈡ D案 手順書

### 現状の欠陥（前提・current_order_10 census 再引用）

主repo checkout に `scripts/morning_digest_send.sh` は**実在せぬ**（`ls scripts/morning_digest_send.sh` → `No such file or directory`、本票測時に再実測）。
既存 `.service` の `ExecStart=/bin/bash %h/projects/multi-agent-shogun/scripts/morning_digest_send.sh` は主repo基準で**dangling**（current_order_10 census closure と同一の型）。
B(worktree依存)は却下済・C(主repo先行merge)は却下済 ⇒ 第三の置き場所が要る。

### D案の要点

installer が **監査済commitの script blob** を **durable private runtime path**（/tmp 依存 0・worktree 依存 0・repo merge 0）へ copy し、
**インストール時に生成する `.service` の `ExecStart`** をその runtime path へ向ける。unit file 自体（`.service`/`.timer`）は現行installerと同じく `~/.config/systemd/user/` へ設置する（systemd の制約でここ以外に置けぬ・変更不要）。

### 置き場所

```
durable runtime dir  = $HOME/.openclaw/morning_digest_runtime/
installed script     = $HOME/.openclaw/morning_digest_runtime/morning_digest_send.sh
```

理由=既存 `MORNING_DIGEST_STATE_FILE`/`MORNING_DIGEST_ARCHIVE_DIR` が既に `$HOME/.openclaw/` 配下を「/tmp ではない永続」の置き場として使っておる（script冒頭コメント「NOT /tmp — must survive whatever wiped the digest」と同じ理）。新規の慣習を増やさず既存の慣習に合わせた。

### 依存 `inbox_write.sh` の扱い（★設計判断・要留意★）

`morning_digest_send.sh` は既定で `MORNING_DIGEST_INBOX_WRITE_SH="${MORNING_DIGEST_INBOX_WRITE_SH:-$SCRIPT_DIR/inbox_write.sh}"`（`SCRIPT_DIR`=自身の置き場所）を用いる。
単純 copy のみだと `SCRIPT_DIR` が runtime dir に変わり、そこに `inbox_write.sh` が無く**壊れる**か、あるいは `inbox_write.sh` も runtime dir へ copy して**二重実装**を生む（Anti-Duplication 抵触・かつ E-g の「既存経路 byte invariant」監視対象が増える）。
**採る案**=copy はせず、生成する `.service` の `[Service]` へ `Environment=MORNING_DIGEST_INBOX_WRITE_SH=%h/projects/multi-agent-shogun/scripts/inbox_write.sh` を明示追加し、主repoの**既存・byte-invariant** `inbox_write.sh` をそのまま参照させる（新規copy 0・既存経路そのまま）。
`scripts/inbox_write.sh` は主repo checkout に現に実在し（測時 `-rwxrwxr-x ... 38703 bytes`）、本feature branchの新規物ではない（`git log -1` = `60c1c8b` 2026-08-06、本工区の変更対象外）ため、この参照は「主repo merge 0」の境を破らぬ（読むだけで書かぬ・merge=copyの意ではない）。

### installer の手順（現行 `morning_digest_send_install.sh` からの差分として記す・★本票では実装せず★）

```
--apply --approval-ref=<ref> 受理後（既存の approval-ref gate 構造は維持）:
  1. mkdir -p "$RUNTIME_DIR"                          # $HOME/.openclaw/morning_digest_runtime
  2. cp "$SCRIPT_DIR/morning_digest_send.sh" "$RUNTIME_DIR/morning_digest_send.sh"
  3. installed_sha=$(sha256sum "$RUNTIME_DIR/morning_digest_send.sh" | cut -d' ' -f1)
  4. source_sha=$(sha256sum "$SCRIPT_DIR/morning_digest_send.sh" | cut -d' ' -f1)
  5. [[ "$installed_sha" == "$source_sha" ]] || { rollback; exit 1; }   # fail-closed on mismatch
  6. sed で .service の ExecStart / ExecStartPre / Environment を上記③本文の通り書き換えた版を生成
     → $UNIT_DIR/morning_digest_send.service へ書く（.timer は無変更・既存installer通りcopy）
  7. systemctl --user daemon-reload && enable --now
  8. log_action へ source_sha / installed_sha / unit_service_sha / approval_ref を全て記録
```

`.timer` は `ExecStart` を持たず（census a3 既測=`Unit=`参照のみ）、書き換え対象外。

### rollback

既存 installer の `--rollback --approval-ref=<ref>` 構造を維持しつつ、`rm -f "$UNIT_DIR/..."` に加え `rm -f "$RUNTIME_DIR/morning_digest_send.sh"` を追加する必要がある（現行installerには無い・runtime dir自体は残しても害は無いが空ファイルは掃除すべき）。

---

## ㈢ 3 SHA — 実際に算出（予定値・装着はせず）

| 区分 | 対象 | sha256 |
|---|---|---|
| source | `scripts/morning_digest_send.sh` @ worktree HEAD `aafd8ec` (`git show HEAD:...`) | `4dc46677276e78aecdf8ba100d3ffba61addaba08573eb93fd18c781e4275800` |
| audited | 同file @ 軍師second PASS base `b3f2146`（GO E2E票の base commit） | `4dc46677276e78aecdf8ba100d3ffba61addaba08573eb93fd18c781e4275800` |
| installed (予定値・未実施) | 上記を `$HOME/.openclaw/morning_digest_runtime/morning_digest_send.sh` へ `cp` した場合に生じる値。scratchpad で `cp` を再現し実測（host非破壊）: `/tmp/claude-1000/.../scratchpad/predicted_installed_morning_digest_send.sh` | `4dc46677276e78aecdf8ba100d3ffba61addaba08573eb93fd18c781e4275800` |

**3 SHA 一致（予定）＝ 真**。根拠=`git diff b3f2146 aafd8ec -- scripts/morning_digest_send.sh` が空（両commit間でこの1fileは無改変）、かつ `cp` はbyte単位の複製ゆえ source と installed は理論上・実測上ともに同一になる（scratchpad上の再現copyで実証、host上の実copyではない）。

参考=生成される `.service`（ExecStart書換版）を scratchpad上で構築し実測=`1ef384b9564019236396f3b0bdfad6724ecf12d430f68b3713defcd20cda1f52`（★これは "3 SHA" の対象外★=令が指すのはExecStart対象scriptのSHAのみと当職は解す。unit file側のSHAは参考として併記するに留める・射程の当否は上位裁定事項）。

---

## ㈣ 装着— 0（実施せず）

本工区中、以下は悉く実行せず（測時通じて0）:`systemctl --user enable/start/daemon-reload` / `~/.config/systemd/user/` への書込 / `$HOME/.openclaw/morning_digest_runtime/` の実作成 / `--apply` フラグでの installer 起動 / commit / push / merge。
scratchpadでの `cp`・`sed` 再現は host の `$HOME/.openclaw/` にも `~/.config/systemd/user/` にも一切触れておらぬ（対象は本セッション専用 scratchpad のみ）。

---

## 【本工区で己が直した誤り】

初動で「installed SHA は installer 走行後にしか出せぬ」と思い込みかけたが、㈣の装着0境と㈢の「実際に算出」令が両立せぬと気づき、scratchpad上でinstaller相当の`cp`/`sed`操作を**host非破壊で再現**する形へ切替えた。装着はしていないが、値は推測ではなく実際にcommandを走らせて得た値である。

## この工区と対に成る他工区

`current_order_9`（blocked_execstart_gap_awaiting_ruling・E-g拡張裁定の元票）と `current_order_10`（dangling ExecStart census・本票が「主repoに現物が無い」を再確認した際の先行証拠）。本票はこの2件の続きに位置し、D案はcurrent_order_10が数え上げた4件のdangling ExecStartのうち、Lane B自身の1件（`morning_digest_send.service`は census対象外だったが同型の欠陥＝主repo側に実行対象が無い）を塞ぐ設計である。

## 判じ得ぬ点（推して埋めず・以上）

1. `MORNING_DIGEST_INBOX_WRITE_SH` を主repo絶対pathで参照させる設計が「repo merge 0 / worktree依存 0」の境をどこまで満たすと上が判ずるか＝当職の裁定権外（読むだけで書かぬ、という当職の解釈を示したのみ）。
2. unit file (`.service`) 自体のSHA一致を「3 SHA」の対象に含めるべきか＝令の文言は「installed blob SHA を ExecStart に据える」とあり script blobを指すと当職は解したが、確定は上位裁定事項。

## 禁の遵守確認

装着0／systemctl enable・start・daemon-reload=0／実send=0／B(worktreeへExecStart)=為さず／C(主repo先行merge)=為さず／commit=0／push=0／merge=0。scratchpad上のcp/sed再現はhostの実runtime path・実unit dirいずれにも触れておらぬ（別pathへの実測のみ）。

## 監査体制・提出

三者監査は暫定二者制（軍師second + Gemini。Codex leg停止中・SAFETY裁定 seq132707）。本票を軍師second へ提出。
発注三行=①同意を探すな・潰しに掛かれ ②己の手で為した事（試したcommand／当たったfile／立てた反例）を書け ③被監査者の語を引いて「成立」と書くな。

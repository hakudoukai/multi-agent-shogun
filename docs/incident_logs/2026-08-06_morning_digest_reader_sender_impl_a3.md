# Lane B — morning_digest reader+sender 実装報告（足軽3号）

- 下命: 家老second msg_20260806_212616_6dba5f68（実装GO）＋ 追令 msg_20260806_212919_44054098（RED gate仕様＋交絡告知）
- 出所: 本部長殿 21:19:27／21:23:26／21:24 便 → Commander 裁定 `seq152276` → 将軍second 追加境四つ → 家老second 転記
- 測時（本票起筆）= 2026-08-06T21:43:31+09:00（`date -Iseconds` 実行結果）

## 回収（必須5項目）

| 項目 | 値 |
|---|---|
| owner | ashigaru3 |
| branch | `feat/morning-digest-reader-sender` |
| base | `4061f26128a3c824061f941b746c1bfdff2b76fd` |
| worktree | `/tmp/hakudokai-worktrees/morning-digest-reader-sender`（`git worktree add` にて隔離作成、`/tmp` 配下） |
| commit | `7492556ae5f6df274a181f826e991790f6cbf125`（short=`7492556a`）— **local commit のみ、push/deploy/DB/本番＝悉く0** |

## artifact path + SHA256（コミット後・worktree内）

```
7f04349de1c3be0a938b35a76e582a5624e4ee8031c4a5a019301b3c65be246e  scripts/morning_digest_send.sh
7a9d401e91585b09e407c4b6b2e45676e4b68e1fcfea640d4bdd605d25d80461  scripts/watchdogs/morning_digest_send.service
e5e46a0cb12a56e418d8a3cd67aedd6040ac62275a90fdcb335938cd352dcd80  scripts/watchdogs/morning_digest_send.timer
09ca1a007af6e32d741793fb222fce754943e2d01e21f34d73f40cee9a78144f  scripts/watchdogs/morning_digest_send_install.sh
d623baeeb62f5a5e0f7218e252ad297022524455ae1b89c479beed81cdc29f32  tests/unit/test_morning_digest_send.bats
```

（測時=2026-08-06T21:43:19+09:00・器=`sha256sum`・範囲=本コミットで追加した5 file 全件）

## RED の実走（旧base・script不在の状態で実行）

手順＝新規作成した `scripts/morning_digest_send.sh` を一時退避し、base 4061f26 相当（script 不在）の状態を worktree 内で再現、`bats tests/unit/test_morning_digest_send.bats` を実行。

```
1..7
not ok 1 T-001: N件保留中のdigest -> 出口を叩けば exactly 1 send・内容はsanitized
not ok 2 T-002: digest file 不在 -> 0 send
not ok 3 T-003: digest 空配列 -> 0 send
not ok 4 T-004: 送信直後の再実行 -> 追加送信 0 (live digest が truncate 済)
not ok 5 T-005: 再起動想定 (digestが消える) -> 追加送信 0
not ok 6 T-006: 同一batchが再出現 (truncate競合を想定した防御) -> 追加送信 0
not ok 7 T-007: 未知key (未sanitize混入) -> fail-closed で送信 0
```

7件悉く `exit 127`（"Command not found" — `scripts/morning_digest_send.sh` が実在しない為の**実行**失敗、静的推論ではなく `run` 経由の実行結果）。★これが「出口 0 件」の実行RED★（足軽1号 実測 `70caeee` の裏付け・単なる import ERROR や件数 PASS ではなく、bats が実際に script 呼出を試みて失敗した記録）。

## GREEN の実走（script 復元後・本commit の状態で実行）

```
1..7
ok 1 T-001: N件保留中のdigest -> 出口を叩けば exactly 1 send・内容はsanitized
ok 2 T-002: digest file 不在 -> 0 send
ok 3 T-003: digest 空配列 -> 0 send
ok 4 T-004: 送信直後の再実行 -> 追加送信 0 (live digest が truncate 済)
ok 5 T-005: 再起動想定 (digestが消える) -> 追加送信 0
ok 6 T-006: 同一batchが再出現 (truncate競合を想定した防御) -> 追加送信 0
ok 7 T-007: 未知key (未sanitize混入) -> fail-closed で送信 0
```

7/7 GREEN（再実行1回、再現性確認済・flaky無し）。実行後、実系 `/tmp/morning_digest.json` および `$HOME/.openclaw/morning_digest_sent_state.json`／`$HOME/.openclaw/morning_digest_archive/` の**いずれも作成されていないことを実測確認**（テストは全件 `TEST_PROJECT_ROOT` 隔離下の env override で実行・実系を1バイトも書いていない）。

## 実装の要旨

- `scripts/morning_digest_send.sh`＝新規追加。`scripts/diagnose.sh` の `MORNING_DIGEST="/tmp/morning_digest.json"` と★同一 path★ を読む（既存の書込側 `diagnose.sh` は1行も変更していない＝byte不変）。
- 送信は既存の `scripts/inbox_write.sh` を**そのまま呼ぶだけ**（此方も1行も変更していない）。宛先は `MORNING_DIGEST_RECIPIENT`（既定値 `karo-second`）で環境変数上書き可 — ★令に受信者の明記は無かった為、当職の判断で既定値を設定した設計選択である旨、明記する★。
- sanitize gate＝`diagnose.sh` の `check_night_mode()` が実際に書く4 key（`error_code`/`severity`/`deferred_at`/`epoch`）のみを許可する allowlist を実装。想定外 key が1つでも混入すれば **fail-closed（送信0・exit非0）**——患者本文・実path・token等の混入を、値を見ずにkey名だけで検出し止める。
- 冪等性＝(1) 送信成功後に live digest を `[]` へ truncate（同セッション内の直後再実行を防ぐ）+ (2) `$HOME/.openclaw/`（★`/tmp` ではない★永続 path）に送信済batchの content-hash を記録（truncateが競合/失敗した場合の二重防御）。★再起動想定★=`/tmp` 側 digest を削除しても永続 state 側は残る、という前提でテスト（T-005）。
- cron/systemd 装着＝実施していない（境㈠）。`scripts/watchdogs/morning_digest_send.{service,timer}` は artifact として追加のみ・`systemd-analyze verify --user` でsyntax確認済（morning_digest関連のerror/invalid行=0件）・installer (`morning_digest_send_install.sh`) は `--dry-run` のみ実行し `--apply` は明示 REFUSE する作り（実測=`--apply` 実行 exit=1、`REFUSED` 文言確認）。`systemctl --user list-timers --all` にて `morning_digest` 関連 timer が実在しないことを実測確認。

## ★交絡（将軍second 実測・家老second 追令より転記）★ — 未修正のまま報告

貴殿（家老second）指示の通り、以下2箇所は**本工区の対象外**であり、当職は一切手を加えていない：

1. **入口**＝`$HOME/.openclaw/night_mode` — 実在せず（`ls` → No such file、本票測時点で再確認済）。この flag を立てる code は repo 内に0件（足軽1号 実測 `70caeee` 継承）。
2. **器**＝`/tmp/morning_digest.json` — 実在せず（一度も書かれていない、本票測時点で再確認済）。

∴ **本コミットで直したのは「出口」のみ**。入口・器が現状のまま（人手で `touch ~/.openclaw/night_mode` されない限り）、本番で `morning_digest_send.sh` が実際に送るデータは今後も発生しない。★これは「直った」の限界であり、隠さず報告する★——上位（家老second → 将軍second）への上申は貴殿に委ねる。

## 己の手で為した事（証跡コマンド）

```
git worktree add /tmp/hakudokai-worktrees/morning-digest-reader-sender -b feat/morning-digest-reader-sender 4061f26
mv scripts/morning_digest_send.sh /tmp/...hidden_for_red_test   # RED 実走準備
bats tests/unit/test_morning_digest_send.bats                    # RED: 7 failed (exit 127)
mv /tmp/...hidden_for_red_test scripts/morning_digest_send.sh    # 復元
chmod +x scripts/morning_digest_send.sh scripts/watchdogs/morning_digest_send_install.sh
bats tests/unit/test_morning_digest_send.bats                    # GREEN: 7 passed
bats tests/unit/test_morning_digest_send.bats                    # 再現性確認 (2回目も 7 passed)
git check-ignore -v scripts/morning_digest_send.sh                # whitelist漏れ検出 → .gitignore に1行追加
systemd-analyze verify --user scripts/watchdogs/morning_digest_send.{service,timer}
bash scripts/watchdogs/morning_digest_send_install.sh --dry-run
bash scripts/watchdogs/morning_digest_send_install.sh --apply     # REFUSED 確認
ls /home/hakudokai/.config/systemd/user/morning_digest_send.*     # 実在せず確認
systemctl --user list-timers --all | grep -i morning              # ヒット0件確認
git add .gitignore scripts/morning_digest_send.sh scripts/watchdogs/morning_digest_send.{service,timer,_install.sh 相当} tests/unit/test_morning_digest_send.bats
git commit ...
sha256sum <5 files>
ls /tmp/resimg-* (list のみ・非改変)
```

以上（読めぬfileは無かった・CLAUDE.md 未改変・`/tmp/resimg-*` 未改変・push/deploy/DB 未実施）。

## 発注三行（軍師second 提出時 必須）

1. 同意を探すな・潰しに掛かれ。
2. 返信に己の手で為した事（試した command／当たった file／立てた反例）を書け。
3. 被監査者（当職）の語を引いて「成立」と書くな——引くなら己が引き直したと明記せよ。

## 監査体制

暫定二者制（軍師second + Gemini）。Codex leg 停止中（2026-07-21事案）。「二者PASS」を「三者PASS」と書かない。

report_to: karo-second

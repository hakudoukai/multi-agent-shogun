# 追補1 — §4-4 差分のみ (足軽2号)

**対象**: `docs/incident_logs/2026-08-06_p0_ishoku_heredoc_fix_plan_a2.md`
**軍師second PASS済版**: 220行 / sha256=`96ef9d2c76037f1d7fcba26c7c258695a848f76b3779fb967874a26cce27fe6a`
**現物 (未監査)**: 225行 / sha256=`6e226ae400840d087578722432d801587318e478a1a82a5eb64f1fca5ddaea30`
**測時**: 2026-08-06T03:29:00+0900 (`date -Is`)
**下命**: karo-second msg_20260806_032704_b32b61f1「軍師second へ追補分のみを差し出し再監査を請え」

## ① 差分の所在

§4「⒟ 原子的差替え・検証手順」の手順4「systemd 側の断面 (差替え前)」の1ブロックのみ。他の全節 (§0〜§3、§5〜§8) は★無変更★。

## ② 差分の中身 (逐語 diff)

PASS 済 220行版では、当職の初稿が「timer 三本」を enter_restart 系のみに絞って読み「1組 (2 unit) のみで母集団不明・第四値」と★未確認のまま★報告していた (旧4行)。

家老second が実測 (`systemctl --user list-timers --all`・03:22断面) の上で「三本」の内訳を示された (msg_20260806_032320_02bc98db)。これを受け、当該箇所を実測結果の転記へ差し替えた (新9行)。

```diff
-4. **systemd 側の断面 (差替え前)** — ★実測の上、「三本」ではなく現況を正確に記す★:
-   - 当ホスト (second_pc) で `systemctl --user list-timers --all` を実測した結果、`enter_restart` 系で active/enabled なのは **`enter_restart_shogun_second.timer` + `enter_restart_shogun_second.service` の1組のみ** であった (`~/.config/systemd/user/enter_restart_shogun_second.{service,timer}` は共に newbuild への symlink)。
-   - `systemctl --user is-active enter_restart_shogun_second.timer` / `.service`、`systemctl --user show enter_restart_shogun_second.timer -p ActiveState,SubState,LastTriggerUSec,NextElapseUSecRealtime` を差替え前後で取得し diff する。
-   - **★命令書「timer 三本」との食い違い★**: 当ホストで実測できたのは 1組 (2 unit) のみであり、「三本」に対応する母集団を当ホストからは確認できなかった。他PC (main_pc/third_pc) に存在する enter_restart 系 timer (`enter_restart_shogun_main.timer` / `enter_restart_shogun_third.timer` / `enter_restart_commander.timer` 等、当repo の `scripts/watchdogs/` には4種の名が存在することは確認済) が「三本」の実体である可能性はあるが、★他PCへの確認は本工区の禁 (newbuild/姉妹clone 読取限定・他PC SSH は別工区の範囲) の外にあり、当職からは断定できぬ★。∴ この点は★第四値 (未確認)★として家老second/軍師second へ差し戻し、実際に差替えを行う側が対象PC上で「その時点で active な enter_restart 系 timer 全数」を実測してから母集団を確定することを求める。
+4. **systemd 側の断面 (差替え前)** — ★実測の上、「三本」を確定した現況を記す★:
+   - 当職の初稿では `enter_restart` 系のみに母集団を絞り「1組 (2 unit) のみ」と報告したが、これは★母集団が狭すぎた★誤りであった (家老second msg_20260806_032320_02bc98db にて指摘・是認)。
+   - **★確定 (家老second が `systemctl --user list-timers --all` で再実測・03:22 断面)★**: 「timer 三本」は enter_restart 系の3本ではなく、★当ホストで active かつ enabled な★別 family★ の timer 3本★ を指す:
+     ① `auto-git-sync.timer` (次回 03:24:27 / 前回 03:19:27)
+     ② `enter_restart_shogun_second.timer` (次回 03:25:07 / 前回 03:20:07)
+     ③ `shogun_auto_claim.timer` (次回 03:25:07 / 前回 03:20:07)
+   - 上記3本は本 script (`enter_restart_common_watchdog.sh`) の差替えと★直接には無関係な family も含む★ (`auto-git-sync`/`shogun_auto_claim` は本 script を呼ばない別 watchdog)。∴ 差替え前後で確認すべきは「3本とも enabled/active のまま不変であること」— 本script差替えが他 timer を巻き込んで壊さないことの★横断的な健全性証跡★として3本を見る、という趣旨であったと解する。
+   - 検証コマンド: `systemctl --user list-timers --all` を差替え前後で取得し、上記3 unit の `enabled`/`active`/`waiting` 列が不変であることを diff で確認する。加えて本 script に直接紐づく `enter_restart_shogun_second.timer` / `.service` は `systemctl --user show ... -p ActiveState,SubState,LastTriggerUSec,NextElapseUSecRealtime` まで取得する。
+   - **本節の経緯 (記録として残す)**: 当職は初稿で「三本」の内訳を仮定せず★第四値 (未確認)★として家老second/軍師second へ差し戻した。家老second はこれを実測で応え「三本は現に在るが、命令文が★どの三本か★を挙げていなかった当職の書き方の落度」と自認した。★数を渡す時は構成要素を列挙せよ★という条が本件から立った (家老second 03:23便)。当職の対応 (仮定で埋めず差し戻した点) は家老second より「是」と評された。
```

**行数の精算 (確度の札)**: 旧ブロック4行 → 新ブロック9行、★-4/+9★。file 全体では 220行→225行 (★net +5行★・家老second の「差は5行」はこの net 値と一致)。

## ③ 新判断を足したか否か

★足していない★。追加された内容は全て以下いずれかの転記・整理:
- 家老second msg_20260806_032320_02bc98db の実測結果 (①②③の timer 名・次回/前回発火時刻) の逐語転記
- 当職自身が §4-4 に既に記していた「母集団不明」という立場の経緯としての保存 (削除せず残す形)

★当職独自の新規判断・新規主張は追加していない★。§0〜§3・§5〜§8 (heredoc 書換案・負テスト・陽性対照・原子差替え手順本体・二重実装確認・己が直した誤り・対工区・監査提出) は完全に無変更のまま。

---

**提出**: 軍師second へ本追補のみ提出。①②の sha 対比 + ②の逐語diff + ③の回答、が揃った状態。

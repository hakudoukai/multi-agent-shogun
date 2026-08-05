# 「素通り六名」⒜⒝ 分類の独立検め (足軽4号・2026-08-05)

下命: 家老second msg_20260805_140235_04d39267 (14:02:35)。
「registry canon 名のうち ★この PC で読む者が居らぬ★ を全数列挙し、⒜招いたが来ておらぬ／⒝他PCで生きておる、に分けよ。
当職は shogun/karo/gunshi=⒝・takenaka/honda/sanada=⒜ と判じ申した — 根拠は note欄のみ ∴ 弱う御座る ∴ 覆されたし」。

## §0 検めた範囲 (疑義の広さ と 検めの広さ は 別)

★検めた★: 本 PC (SecondPC=当職の稼働機) の `queue/pane_registry.yaml` 全文・`queue/inbox/*.yaml` の実在/内容/mtime・
`tmux list-sessions`/`tmux list-panes`(本 PC の tmux server のみ)・`ps -eo` (本 PC の process table のみ)・
`scripts/inbox_write.sh` の delivery_failed 経路 (読むのみ)。
★検めておらぬ★: MainPC 側の tmux/process/filesystem 実物 (SSH は足軽権限外・本工区の縛りにも明記)。
∴ 「他PCで生きておるか否か」の★直接証明は本 PC からは不可能★——これは制約であって手抜きではない。以下は全て
「本 PC から見える artifact」を根拠とする★間接証拠★のみ。

## §1 母集団の独立再導出 (手で数えず re-derive)

`grep -oP '^\s*agent_id:\s*\K\S+' queue/pane_registry.yaml | sort -u` で registry 全 canon agent_id を数えた。

- **総数 = 17**(実測)。★足軽3号 (a3) の 10:5x 実測時点では 16 — 差は honbucho 追加 (当職が 2026-08-05T12:4x に registry へ追加登録) による母集団の自然増であり、a3 の数え漏れではない★。
- 本 PC の tmux pane + inbox_watcher process の両方が実在する canon id (実測・列挙): `karo-second, shogun-second, gunshi-second, honbucho, ashigaru1, ashigaru2, ashigaru3, ashigaru4, ashigaru5, ashigaru6, ashigaru7` = **11**。
- 残り **17 − 11 = 6** = `shogun, karo, gunshi, takenaka, honda, sanada`。

★これは下命文の「六名」と一致した — 当職が独立に再導出した数であり、下命文の六の丸写しではない★。
(注: `ashigaru1/2/3` は MainPC 側にも registry entry を持つが、`router local-first` 解決ゆえ本 PC からは
同名の SecondPC pane が reader として実在する。∴ 「本 PC で読む者が居らぬ」には該当せぬ — 除外は妥当。)

## §2 陽性対照 (零を述べる前に、方法が「在る」を検出できるか示す)

| ファイル | mtime | size | 便数(実測) | tmux pane | watcher process |
|---|---|---|---|---|---|
| `karo-second.yaml` | 本日 14:08:14 | 153,866B | 50 | multiagent-second:0.0 (実在) | pid 1990805 (実在) |
| `ashigaru1.yaml` | 本日 14:06:01 | 94,252B | 45 | multiagent-second:0.1 (実在) | pid 3181670 (実在) |

★∴ 本手法は「在る」を正しく拾える (零バイアスに非ず)★。以下の六名は、この陽性対照と対比して読むこと。

## §3 六名 個別実測 (file 実在・size・mtime・便数・内容の性質)

| 名 | file | size | mtime(最終書込) | 便数 | 内容の性質 |
|---|---|---|---|---|---|
| `shogun` | 実在 | 328B | 2026-07-02 13:52 | **0** | ★file 冒頭に自己申告あり★=「Archived generic legacy shogun inbox. reason: current SecondPC shogun route uses queue/inbox/shogun-second.yaml.」 |
| `gunshi` | 実在 | 335B | 2026-07-02 14:14 | **0** | 同型の自己申告=「reason: SecondPC currently has no gunshi pane and current route is role-specific.」(★file自身が「SecondPC に gunshi pane は無い」と明記★) |
| `karo` | 実在 | 47,316B→本日43件目まで成長 | 本日 11:16:47 | **43**(実測=python yaml.safe_load) | ★39件は 2026-05-07T19:04〜2026-07-01T21:25 に集中(ashigaru5/6/7・maeda・second_pc・shogun からの旧世代便)。以後 5週間 空白。★残り4件は本日 10:55〜11:16 の `delivery_failed`(from=inbox_write, content="宛先不明: test_agent")★=何者かが `inbox_write.sh test_agent ... karo` で無効宛先へ送った際の★突き返しが karo 自身へ返っただけ★(karo が読んだ証ではない)。 |
| `takenaka` | 実在 | 13B | 2026-05-09 11:35 | **0** | `messages: []`。rotation注記なし=★そもそも一度も便が来なんだ(退避すべき中身が無い)★。registry status=「持ち場準備中」と整合。 |
| `honda` | ★不在★ | — | — | — | `queue/inbox/honda.yaml` は本 PC に★一度も作られておらぬ★。registry status=「通常運用」だが note=「pane配置は理事長殿確認待ち」——★status欄とnote欄が矛盾しており申す★。 |
| `sanada` | ★不在★ | — | — | — | 同上、file 皆無。`queue/` 全体を `/usr/bin/grep -r` (git-ignore 無視の実 grep) で当てた唯一の hit は★他 agent の会話文中での言及★(例: `ashigaru3.yaml:627` 他)であり、★sanada 宛/発の inbox 実体ではない★。 |

## §4 他工区との突合 (対に成る他工区・二重実装ではなく検証として引用)

★足軽3号 (a3) が同日 10:49:54 (`queue/inbox/ashigaru3.yaml:622-630`) に★ほぼ同一の母集団突合を先に実施済み★=
「16名中5名が実質配送不能=空箱(shogun/gunshi/takenaka)・箱file不在(honda/sanada)」「karo=39通あるが最終書込07-08」。

★当職の実測 (karo=43通) と a3 の実測 (karo=39通) の差=4 は、当職が観測した本日 10:55〜11:16 の
delivery_failed 4件と★数が一致する★(43−39=4)。★∴ 二つの独立測定(10:5x と 14:0x)が同じ増分で辻褄が合い、
双方の実測の信頼性を相互に補強した★(a3 の数字を当職が実測で追試・一致)。

## §5 判定 — 家老second の ⒜⒝ 二分を ★覆す★

★当職の判定=下命の二分そのまま(shogun/karo/gunshi=⒝ / takenaka/honda/sanada=⒜)は★本 PC の実物証拠と合致せぬ★。

理由: 本 PC から見える限り、`shogun`・`gunshi`・`karo`・`takenaka` の四者は★同じ実測パターン★(便0または旧世代のみ・
5週間以上の空白・本 PC に reader 皆無)を共有しており、★karo を shogun/gunshi と切り離す根拠が本 PC には無い★。
むしろ `karo.yaml` は `shogun.yaml`/`gunshi.yaml` と★同じ「役割分岐前の旧世代共有宛先」の性質★を持ちながら、
★rotation ヘッダのみ付いておらぬ(付け忘れの疑い、当職はここを修正せぬ=読むのみの縛り)★。

∴ 本 PC 単独の証拠では、六名は ⒜/⒝ の二値ではなく★三層★に分かれる:

1. **file 皆無 (最弱)**: `honda, sanada` — 一度も inbox provisioning が無い。registry status「通常運用」と最も強く矛盾。
2. **file 実在・便ゼロ/旧世代のみ・rotation 済または実質旧世代 (中間)**: `shogun, gunshi, karo, takenaka` — 本 PC からは
   「生きておる」の直接証拠なし。ただし karo のみ★過去に実在した実便(旧世代)の量が多い(39通)★——「一度も来なんだ」takenaka とは量的に異なる。
3. **他PCでの現況そのもの (⒝の確認)**: ★本 PC からは検証不能 (§0 の縛り)★。

★∴「shogun/karo/gunshi=⒝」は★確定できぬ(第四値のまま残す)★——karo-second の note根拠と★同じ弱さの推定に本職の推定を積み増すのは
「二値に倒す」ことになり本日の様式⑤に反する。★正しい返答は「本 PC の証拠は ⒝ を支持も否定もせぬ。MainPC 側の実物確認 (tmux/process) が無ければ確定不可」★。
一方 `takenaka` を「他三名と別枠」とした下命の直感は★本 PC の証拠では裏付けられぬ★(shogun/gunshi/karo と同じ「空箱または旧世代」枠)。

## §6 己が本工区中に直した誤り (必須欄・空欄不可)

1. 当初、`karo.yaml` の本日 mtime 更新を見て「cross-PC bridge の shadow write (未達便が local yaml に落ちる既知欠陥)」を
   疑い申した。★実際に4件の中身を読んで訂正★=これは shadow write ではなく、無効宛先 `test_agent` への送信試行が
   `inbox_write.sh` の delivery_failed 経路で FROM (`karo`) へ突き返されただけの★自己反射便★であった。
2. 六名を「karo-second 発案の note のみで裏付けようとする」姿勢を一度取りかけたが、①正本の `pane_registry.yaml` 全文
   ②file header の自己申告文 ③a3 の独立実測、の★三点照合に切替えた★。

## §7 未検めの残り (射程外・隠さず明記)

- MainPC 側の tmux/process 実物確認 — SSH 越境禁・足軽権限外。
- `honda`/`sanada` が queue/inbox 以外の経路 (例: hermes 系ディレクトリ) で別途稼働している可能性 — `find queue -iname "*honda*" -o -iname "*sanada*"` は空だったが、`queue/` 外(例 `hermes-departments/`)までは本工区の縛り (registry/inbox_write.sh/墓場 file 読取限定) を超えるため未探索。
- `karo.yaml` に rotation ヘッダが付いておらぬ点の是正可否 — 判断・修正とも本工区の縛り外 (read-only)。

---
**報告**: 家老second。ETA 即返し下命ゆえ即時提出。

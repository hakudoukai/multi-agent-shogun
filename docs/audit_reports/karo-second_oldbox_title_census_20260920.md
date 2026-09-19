# 旧箱 題のみ読取分類 ―― 事業部長令 msg_20260920_031353_2e775fd1 復命

- 執行者: 家老second (karo-second) / pane karo-second:0.0
- 掃きの刻: 2026-09-20 05:08:58 JST ／ 手: python3 yaml.safe_load による読取のみ
- 令の逐語: 「旧 shogun-second／ashigaru4-7 全67件は原本・既読を不変にし、各messageの題（timestamp/from/type/content先頭1行・id・read）のみを読取分類せよ。生きる候補は現役宛先/理由/旧ID/新規DB再発行本文案、失効は理由を一覧化。本文深読・代理ACK・YAML書込・再注入なし。成果を完全path+SHAで返せ。」
- ★己の手: 読取のみ。書込零・既読操作零・ACK零・再注入零。★

## 〇 数の訂 ―― 令の「67」と実測の差

| 器 | 全件 | 未読 |
|---|---|---|
| queue/inbox/shogun-second.yaml | 97 | **67** |
| queue/inbox/ashigaru4.yaml | 35 | 2 |
| queue/inbox/ashigaru5.yaml | 40 | 4 |
| queue/inbox/ashigaru6.yaml | 50 | 1 |
| queue/inbox/ashigaru7.yaml | 33 | **0** |
| queue/inbox/ashigaru-second-4/5/6.yaml | 各0 (13B の空器) | 0 |
| queue/inbox/ashigaru-second-7.yaml | 40 | 8 |
| **合計** | **295** | **82** |

★己の疵 (本紙作成中に己が生じ 己が見つけ 己が直したる物)★ ―― 上表の「全件」欄を、己は**初め測らずに書いた**。合計295と未読欄のみ撃ち、箱別の全件は頭の内で割り付けた (97を199・35を22・40を24・50を30・33を20・40を13と記した)。**六欄悉く誤り**に御座る。紙を渡す前に撃ち直して直し申した。∴ 本紙の数は「一度は推で書かれ、後に器で置き換へられた」物である事を明記す。

∴ 令の「67」は **shogun-second 箱のみの数と一致**。a4〜a7 を併せると **82**。差15。
★測って居らぬ事★: 既読側228件の中身は一切見て居らぬ (令の外)。_archive/*_pruned.yaml も見て居らぬ。

## 一 器の符 (読取前後 不変の證)

| 器 | size | sha256(先16) | mtime |
|---|---|---|---|
| queue/inbox/shogun-second.yaml | 253452 | f08d9ccb418fb912 | 2026-09-19 23:09:44 |
| queue/inbox/ashigaru4.yaml | 95553 | 02acc9f7363543e6 | 2026-09-08 06:09:11 |
| queue/inbox/ashigaru5.yaml | 104765 | 3d5e053095eb0158 | 2026-09-08 06:08:46 |
| queue/inbox/ashigaru6.yaml | 132795 | 6666f30f5f32dae0 | 2026-09-08 06:08:46 |
| queue/inbox/ashigaru7.yaml | 127871 | 4b3fa1b72cbb62a8 | 2026-08-11 12:46:01 |
| queue/inbox/ashigaru-second-7.yaml | 56471 | 453b7f531f7d915e | 2026-09-08 06:08:47 |
| queue/inbox/ashigaru-second-4/5/6.yaml | 各13 | ab1a54afd56934aa | 2026-08-03 |

## 二 差出別 (未読82の出所)

karo-second 66 ／ honbucho 6 ／ second_pc 4 ／ inbox_write 3 ／ third_pc 2 ／ gunshi-second 1
刻の幅: 2026-09-05T05:26:51 〜 2026-09-19T23:09:44

★∴ 82件中66件 (80.5%) は己が出した物である。★ 即ち此の滞留の大半は「届かぬ便」ではなく「**受け手の無い席へ己が置き続けた控**」に御座る。

## 三 ★生きる候補★ (3件)

### 生1 ―― 最も重い
- 旧ID: `msg_20260919_230944_2af95789`
- 刻/差出/型: 2026-09-19T23:09:44 ／ honbucho ／ notification
- 題(先頭1行): `[grill request] Task t_c70f2759: dr-s receiver registration repair. Please provide design review only: compare existing gunshi-second service/poller/watcher pattern, identify minimal reversible implem…`
- 現役宛先案: **karo-second** (SecondPC の現役差配口。将軍second は pane 不在)
- 生と判ずる理由: ㊀未読中 **最新**(9時間前) ㊁task_tracker の id `t_c70f2759` を名指す ㊂求むるは design review のみ＝可逆・安全
- ★未測★: 直近 commit `28eb5ce1 fix(receiver): register dr-s target pane` ／ `16552795 fix(receiver): dedupe unroutable notices` が本件を已に満たすや否や、己は**測って居らぬ**。∴「生」は**宛先が死んで居る**事のみを以て言ひ、**内容が未了**とは断じ得ぬ。
- 新規DB再発行本文案 (≤300字):
  > [再発行/旧ID msg_20260919_230944_2af95789] 旧 shogun-second 箱に滞りたる grill request を現役宛先へ移す。Task t_c70f2759 dr-s receiver 登録修復の design review のみ(実装・送達零)。gunshi-second の service/poller/watcher の型と突合し、最小可逆案を出す。★但し commit 28eb5ce1/16552795 が已に之を満たすや否やが未測ゆゑ、先づ其の突合から入る★。条266 に依り dr-s へは一字も送らず。

### 生2・生3 ―― 一対
- 旧ID: `msg_20260910_203041_7b8a9756` (third_pc 2026-09-10T20:30:41 answer) ／ `msg_20260910_223354_c9e82abe` (third_pc 2026-09-10T22:33:54 answer)
- 題: 「299732裁定: Windows literal pathの設定を修正し、dir出所を1行報。…readbackを299732親付きで返答。」／「299732 GO。Windows画像rootをLinuxで直す。dir出所+変更file/SHA/rollback又はB4。」
- 現役宛先案: **未定 (要裁)**
- 生と判ずる理由: **GO が下りて居り、readback を求めて居る**。旧席へ落ちた儘ならば9日間 readback 未返の恐れ。
- ★己が執り得ぬ理由★: 対象が Windows 画像 root ＝ `/mnt/c` 配下への**書き**。己には `/mnt/c` の書きが禁。∴ 実行者は別席。
- 新規DB再発行本文案 (≤300字):
  > [再発行/旧ID msg_20260910_203041_7b8a9756 ＋ msg_20260910_223354_c9e82abe] third_pc 裁定 299732 (Windows 画像 root の literal path 修正・GO) が旧 shogun-second 箱に9日滞りたり。readback は 299732 親付きで求められ居る。★己は /mnt/c 書き禁ゆゑ執行し得ず★。現役の実行者の指名を乞ふ。消去/移動/add -A/commit/push=0 の枷は原文の儘。

## 四 ★失効★ (79件) ―― 類別と理由

| 類 | 件 | 器 | 理由 |
|---|---|---|---|
| ㊀ 己の発信控 (karo-second→將軍second) | 49 (report_received) ＋1 (task_assigned) ＋2 (notification) = **52** | shogun-second | 宛先席**退役・pane不在**。内容は 09-05〜09-12 の遣り取りにて、別経路(便・紙)へ已に着地。受け手を持たぬ控ゆゑ再発行の実が無い |
| ㊁ 己と將軍second間の答 (second_pc) | 4 | shogun-second | 論点(1087/92/148・81.9%の未検証降格／a2凍結紙の符／偏り二方向)は**已に終結・降格処理済**。再開の実が無い |
| ㊂ honbucho 状況報 | 2 (`msg_20260917_130026_afe0c62a` / `msg_20260919_190504_62a61e28`) | shogun-second | 09-17=honbucho 自箱の未読240件乖離報 ∴ **owner=honbucho**。09-19=API 503 全席停止報 ∴ **已に解消**(現に三席稼働)。孰れも状況が変じたり |
| ㊃ gunshi-second 監査報 | 1 (`msg_20260908_192006_2fa1896a`) | shogun-second | 本文先頭に「**家老secondへ着地確認済み**」と在り ∴ 己へ已に届き居る重複 |
| ㊄ 機構の自動通知 (inbox_write) | 3 (cap_rotated 1 ／ unroutable bundle 2) | shogun-second | 機構が「本人」へ出す控。宛先本人が退役席ゆゑ読む者無し。人の手を要せず |
| ㊅ 己の canary 負試験・裁40突合 | 7 | a4(2) a5(4) a6(1) | 09-08 の**試験用の弾**。「観る者無き事が声に出るか」を測る為に**意図して停止席へ**置きたる物。測定は已に畢 |
| ㊆ a7 宛の旧令・中継 | 8 | ashigaru-second-7 | 09-05/09-08。a7 は **pane 不在**。内容は総監督令の中継(休止令・三條配布)にて**已に時効**。honbucho 発3件も同日の権限外手順令にて已に定着 |
| **計** | **79** | | |

52+4+2+1+3+7+8 = 79 ／ 79+3(生) = **82** ―― 合ふ。

## 五 数の規律3 ―― 本紙が測って居らぬ事

1. **本文を読んで居らぬ**。分類は timestamp/from/type/id/read ＋ **content 先頭1行** のみに拠る。∴ 先頭1行が本旨を表さぬ便が在れば、失効の判は誤り得る。
2. **既読側213件 (295-82) を見て居らぬ**。生きる要件が既読側に在る可能性は排し得ぬ。
3. **`_archive/*_pruned.yaml` を見て居らぬ**。shogun-second は累計1533件を退避し居り、其の中身は本紙の外。
4. **生1の内容的未了を測って居らぬ** (上記 生1 の★未測★)。
5. **a4〜a7 の現役 pane/owner を測って居らぬ**。「pane 不在」は 09-20 時点の `tmux list-panes` に基づく先の測りの引き写しであり、本紙では**撃ち直して居らぬ**。
6. 本紙は**己が81%の差出人である**事を明らかにする。∴ 本紙の失効判定は**己の発信に対する己の判定**であり、独立性を欠く。軍師の検めを要す。

畢

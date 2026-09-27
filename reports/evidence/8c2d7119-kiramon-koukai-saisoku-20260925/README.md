# 板 8c2d7119（恐竜物語B5）MFT キラモンアドベンチャー 公開情報 再測 ―― 專任3

- 席: ashigaru-mac-3 ／ 下命: queue/goals/ashigaru-mac-3.yaml（2026-09-25 14:24 gakushu-bucho 発・受領時 sha256 `82069ea1354e31579999e4adf810b74ad7a0fe27afb75e65c3c406b6663a0d1b`）
- 取得刻: 2026-09-25T14:29〜14:31 +0900（raw/ の mtime）・紙作成 2026-09-25T14:32 +0900
- 縛り（goal 逐語）: 「自席worktreeの読取・紙作成のみ。依存B2/B4はblockedのため待ち、アプリ改修なし。外部login/有料API/患者情報使用なし。公開情報で届かなければ未測定と記す。」
- 前の紙: `queue/reports/ashigaru-mac-1_KM_8c2d7119_kiramon_20260910.md`（專任1・sha256 `d714a24dbd00f05c2c6ae04b29b4a598500962df0ef81d2f2cdae04d56788086`）。4軸・判定四値・勝ち条件・当方数値は★此の紙を引き継ぐ★（書き直さぬ）。

## 結論（先に）

**4軸とも依然「比べ得ず」。** 本段で新たに届いたのは★静止画と公開メタ情報のみ★であり、4軸はいずれも★時間（秒・遷移・動き）★を要するゆゑ、静止画からは決まらぬ。
⑶操作迷い にだけ★質的な手掛かり★（画面上のタップ誘導の有無・起動→訓練の画面段数の下限）が増えたが、★タップ数・ボタン寸法の実測ではない★。
**「超える」判定は、前の紙と同じく K1（理事長 login で academy 動画視聴）／K2（実機で App Store 版を起動）を待つ。** 本紙は受入ではない（理事長受入は別 gate）。

## ① 出所一覧（全て公開・login なし・無料）

| # | URL | http | bytes | 保存先 |
|---|---|---|---|---|
| S1 | https://pr-contents.doctorbook.jp/mft_kiramon_adventure （LP） | 200 | 46705 | raw_excerpt/https___pr_contents_doctorbook_jp_mft_kiramon_adventure.excerpt.txt |
| S2 | https://academy.doctorbook.jp/movies/1009325 （板指定の参照動画） | 200 | 54494 | raw_excerpt/https___academy_doctorbook_jp_movies_1009325.excerpt.txt |
| S3 | https://academy.doctorbook.jp/movies/1009771 （★新出★） | 200 | 53381 | raw_excerpt/https___academy_doctorbook_jp_movies_1009771.excerpt.txt |
| S4 | https://itunes.apple.com/lookup?id=6760813931&country=jp | 200 | 8153 | raw_excerpt/https___itunes_apple_com_lookup_id_6760813931_country_jp.excerpt.txt |
| S5 | https://play.google.com/store/apps/details?id=jp.doctorbook.mft&hl=ja | 200 | 1200963 | raw_excerpt/https___play_google_com_store_apps_details_id_jp_doctorbook_.excerpt.txt |
| S6 | App Store 画面写真 iPhone×4（1242x2688）・iPad×4（2048x2731）、URL は S4 の screenshotUrls | 200×8 | 表 raw/04 | raw/as_iphone1-4.png・raw/as_ipad1-4.png |
| S7 | PR TIMES https://prtimes.jp/main/html/rd/p/000000039.000040613.html 掲載画像×4 | 200×4 | 表 raw/02 | raw/prtimes_img1-4.png |
| S8 | LP の og:image 他（storage.googleapis.com/production-os-assets/assets/…） | 200×2 | 表 raw/05 | raw/lp_*.png |

- curl の http/bytes/rc の生記録: raw/01・02・04・05（手で写さず curl -w の出力そのもの）。
- ★原寸 PNG 14枚（計 約46MB）は commit しない★。其の sha256 は `90_sha256_all_before_commit.txt` に在る（commit 前に全 38 file を算じた）。閲覧用の縮小版（sips・長辺1400）を view/*.jpg として commit する。原寸は各 URL から再取得でき、sha で同一性を検められる。
- ★raw HTML 5本（S1〜S5）は commit しない★（監督裁定 391565/391605・Commander 391700: 1MB 超の object と他社の公開鍵を含むため）。各本は URL・取得時刻・原本 sha256 の3欄だけの抜粋を raw_excerpt/ に置く。原本 sha256 は `90_sha256_all_before_commit.txt` の同名行と一致する。表の byte 数は原本の値。

## ② 前の紙（09-10）からの差分

1. **S3 academy 1009771 が新出。** 題「【MFT新時代】楽しく続く×メニュー自動作成の最強アプリ登場！」・36:08・公開 2026-06-27。説明文に「操作イメージ」を見せる旨あり。★但し再生は login 要★（逐語「この動画の再生にはログインが必要です。」・raw 内 1件）。∴ 観測不可。
2. **S2 academy 1009325 は不変**（10:35・2025-12-26・login 要＝同じ逐語 1件）。
3. **S4 App Store 版の現況**: version 1.0.2・currentVersionReleaseDate 2026-08-21T21:47:02Z（注記＝兄弟アカウント機能）・初版 releaseDate 2026-04-30・fileSizeBytes 218080256・userRatingCount 0・iOS 16.0 以上。★プレビュー動画は無い★（screenshotUrls のみ）。
4. **S6 App Store 画面写真 8枚を初めて実視した**（前の紙は ld+json の読取まで）。
5. **S5 Play の `jp.doctorbook.mft` は★キラモンではない★** ―― 同じ Doctorbook の別 MFT アプリ「PaTaKa（パタカ）」。名の一致で同物と取るな。Play にキラモンの掲載は見当たらぬ（App Store のみ）。
6. **S7 PR TIMES 画像 4枚を実視した。** 2枚目が「アプリを使ったトレーニングの流れ」4段図（下記③）。
7. LP の本文は依然空（studio.design の SPA・本文 JSON は storage.googleapis.com/studio-publish で 403）。og:description と og:image のみ読める。

## ③ 静止画から★見えた事★（数ではない・観測の記述）

- **起動画面**（S6 iphone1・S8 og:image）: ロゴ・リスの相棒・歯科医の人物・「はじめる」ボタン・「ためしてみる」リンク。
- **今日のメニュー**（S6 iphone2・S7 img4）: 項目の縦並び（例 MBリップシールトレーナー もくひょう10秒／MB呼吸ステップ 10回／左右に 30回 等）・合計所要時間表示・赤い「タップしよう！」札・下端に「トレーニングをはじめる」。
- **訓練画面**（S6 iphone3・S7 img4）: もどる／メニュー・手本動画（▶）と「タップしておねえさんからおしえてもらおう！」の誘導・「あと 30 回！」と進捗棒 0%・指導の「ポイント」文。
- **報酬**（S7 img2 の③）: 「クリアしてコインやカードをゲット！」・「キラモンコレクション」のカード一覧（未取得は灰）。★獲得の瞬間の演出（動き・秒）は写って居らぬ★。
- **継続**（S7 img2 の④）: 「今日はあと3回！」と 1/2/3 の段・「トレーニングする」ボタン。PR TIMES 本文の「1日3回…コイン…ガチャ…カード収集・進化」と整合。
- **記録**（S6 iphone4）: カレンダーと達成率・下タブ ホーム／ガチャ／きろく／カード／保護者の方。
- **医院側**（S7 img3）: PC の管理画面（カレンダー状）。★子の体験の4軸には入れぬ★。
- ★「1話」に当たる物語画面は 14枚の何処にも無い★（PR TIMES 本文の「毎日1話ずつ進むストーリー展開」は文のみで、画面は未見）。

## ④ 4軸 比較表（判定四値＝勝ち／負け／比べ得ず／当方未測・勝ち条件は前の紙 §2）

| 軸 | 当方（前の紙 §3 の既存値） | キラモン（本段で届いた物） | 判定 | 決まらぬ理由 |
|---|---|---|---|---|
| ⑴ 動き | 動き 6 cell 未測 | 静止画のみ。動画は login 要（S2・S3）・App Store にプレビュー動画無し | **比べ得ず**（当方も未測） | 動きは時間の量。静止画は0フレームの証拠 |
| ⑵ 間 | 物語 1 行 11.4s（式）・機械下限 2.1s/話 | 1話の画面そのものが未見 | **比べ得ず** | 間は秒。秒の出所が公開物に無い |
| ⑶ 操作迷い | 起動→話の開始 tap 2・最小辺 44px | 誘導表示あり（「タップしよう！」札・「タップしておねえさんから…」）。起動→訓練は★少なくとも★ はじめる→メニュー→トレーニングをはじめる の画面段（段数の下限であり tap 数の実測ではない） | **比べ得ず**（質的手掛かりのみ） | tap 数・迷い時間・ボタン寸法は実機で測らねば出ぬ。画像上の寸法は端末 pt に換算できず推定に留まる |
| ⑷ 読込 | ブラウザ読込 781〜887ms | 版 1.0.2・218080256 bytes（配布容量）のみ | **比べ得ず** | 容量は読込時間ではない。起動秒は実機でしか出ぬ |

## ⑤ 観測限界（何が★言へぬ★か）

- 本紙の画像は★販促用の静止画★であり、S6 は file 名から simulator 撮影（2026-04-16）と読める（実機の挙動の証拠ではない）。S7 img4 の端末時刻 15:03 と 15:04 は★別の撮影の刻★で、画面間の所要秒としては使へぬ。
- App Store の現行 1.0.2 と、画面写真の撮影時（4月・初版前）とは版が違ひ得る。
- 「タップ誘導が在る」は★迷ひが少ない★の証ではない（誘導が要る設計とも読める）。⑶の勝ち負けは付けぬ。
- 本段で★捜して見当たらなかった★物: YouTube・Instagram・TikTok の公式アカウント／Play のキラモン掲載。★無いの証明ではない★（検索で見当たらぬ、の意）。「キラモン」の語は別の game（キラキラモンスターズ）の略称にも使はれ、検索が混ざる。
- livedoor 側の PR TIMES 転載画像頁は 404（S7 は prtimes.jp 本体から取得）。

## ⑥ 未測定点（誰が何をすれば閉じるか）

| id | 閉じる手 | 必要な物 | 閉じる軸 |
|---|---|---|---|
| K1 | academy 1009325（板指定）・1009771（新出・36:08・操作イメージ）を login して視る | 理事長または院の academy account（★足軽は外部 login 禁★） | ⑴⑵⑶（録画上の秒・遷移） |
| K2 | App Store 版 1.0.2 を実機へ入れ、起動→1話→報酬を同操作で録る | iPhone/iPad 実機・Apple ID（無料 app） | ⑴〜⑷ 全軸（録画の frame で秒を出す） |
| T* | 当方の未測 6 cell 等は前の紙 §5 の T1〜T7 のまま | 依存 B2/B4（blocked） | 当方側 |

## ⑦ 本段で★やらなかった★事

アプリ改修なし・外部 login なし・有料 API なし・患者情報なし・DB 書込なし・push なし。自席 worktree `ashigaru-mac-3/8c2d7119-kiramon-koukai-saisoku-20260925`（base origin/main `b9573b2d376e9a0a372234b696a733677feb7919`）への commit のみ。

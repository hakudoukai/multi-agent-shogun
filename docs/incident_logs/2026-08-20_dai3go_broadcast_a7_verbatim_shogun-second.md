# 委員長令 第3号 周知 ―― a7 へ逐語配布し 7/7 完了

- **as_of: 2026-08-20T08:32:47+09:00**／起案 shogun-second (pid 389804・2.1.236)／second_pc
- 上位令（委員長 seq200545）: 「第3号周知を★足軽1-7★へ本文そのままcopyされたい」
- 上位令（Commander Ruling14 / seq200527）: 「Use **post_and_ring** for necessary Hermes-role traffic; preserve aliases」

## 一 結果

| 宛 | 配布 | 逐語一致 |
|---|---|---|
| ashigaru1〜6 | 既済（前段） | 6/6 一致 |
| **ashigaru-second-7 (a7・Hermes)** | **本件で完了** | **一致** |

- 新便: `msg_20260820_083241_fc86cfd8` ／ from=shogun-second ／ ts=2026-08-20T08:32:41 ／ type=notification
- 本文 **1,396 字**・**sha256(16)=`e557de8d2a589039`** ―― 正本（当職の箱 `msg_20260819_225359_662e102f`）の本文と **桁一致**。
  ★末尾改行の欠落に因る指紋ずれが無い事を、配布前に `endswith_newline=False` で確かめた上で送った★。
- a7 の箱: 総 9 → **10 件**・未読 1（＝本便）。

## 二 鳴らし（ring）―― 当職の手からの pane 入力は 0

- a7 は repo 正典 `scripts/inbox_watcher.sh` の走行 9 本（shogun-second / karo-second / ashigaru1〜6 / honbucho）に**含まれぬ**。
- a7 専用の Hermes watcher が**現に生きて居る**: `/home/hakudokai/hermes-roles/ashigaru-second-7-hermes/bin/ashigaru_second_7_hermes_watcher.py`（PID 1220779・5 秒ループ）。
  - **同一性の門**: pane 実測 `pane_id=%26|pid=1156226|dead=0|cmd=doppler|agent=ashigaru-second-7` ＝ 期待値と**逐語一致**。
  - **繁忙の門**: composer 非空・`esc to interrupt` 等が有れば `delivery_deferred` として送らぬ。
  - **`/clear` を送る枝は無い**（`grep -i clear|escalat|kill` ＝ **0 hit**）⇒ Hermes の会話を消す危険は本経路に無い。
- 配布後の state: `{"unread":1,"status":"submitted","updated_at":1787182364.747}` ＝ **2026-08-20T08:32:44 に鳴らしを投函済**。
- ★当職は `tmux send-keys` を一度も打って居らぬ（0）★。鳴らしは機構が為した。

## 三 post_and_ring について（★UNMEASURED / 当 PC に不在★）

- Commander Ruling14 が名指す `post_and_ring` は、**当 PC に実体が無い**:
  `find /home/hakudokai -maxdepth 4 -name 'post_and_ring*'` ＝ **0 件**。
  唯一の言及は `/home/hakudokai/bin/agent_letter.py` の註（「委員長は本日 post_and_ring.py に同じ門を付けたが本器には付けていなかった」）＝ **他 PC（委員長側）の器**と読める。
- ★代替の器を新造せず・迂回の送信路も作らず★、a7 の**既設 canon 経路**（canon 箱 ＋ a7 専用 Hermes watcher）で為した。
  之が Ruling14 の要（Hermes へ直接手を突っ込まぬ・alias を保つ）を満たすか否かの**最終判断は Commander に属す** ⇒ 本紙にて報告する。

## 四 併せて判った事（帳の訂）

- 本部長殿は **2026-08-19T23:16:12** に a7 へ第3号を配信済であったが、其れは **174 字の要旨**（本文中に逐語で「**本文は含みません**」と明記）＝ **sha256(16)=`3022306b1ec5b7e0`** であり、
  委員長 seq200545 の求める「**本文そのままcopy**」ではない。★故に本件の逐語配布は重複ではない★。
- 一方、a7 は其の要旨便を **既読**（read=true）にして居る ⇒ **a7 の経路は現に生きて居る**（配送不達では無かった）。

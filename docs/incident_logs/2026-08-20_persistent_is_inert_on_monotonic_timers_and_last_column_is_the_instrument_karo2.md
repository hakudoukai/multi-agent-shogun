# ★己の訂 三度目★ ―― 「`Persistent=true` ゆゑ永続に撃つ」は ★支への誤り★（主張は猶正しい）／併せて ★事象受入を一発で測る物差し★ を得たり（家老second）

- **as_of: 2026-08-20T09:47 JST**（実測は **2026-08-20T09:46:14〜09:46:23 JST**）
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 契機: 本部長殿 `msg_20260820_094215_bf94044a`（2026-08-20T09:42:15 JST・nonce `HB-20260820-0941-KARO`）― 当職の二度目の訂を **artifact ＋ timer 実測にて確認**、「両 guard 定常 30min・最大 accuracy 2min ⇒ **32 分は通常一巡を観測する bound**」「boot は早める方向」「事象受入の真因 ＝ **一度の緑は永続の緑に非ず**」と収斂。
- **収斂したるゆゑ、当職は ★己の支へを検め直し★、三つ目の誤りを見出し申した**（★正しき結論に安堵して支へを検めぬは危ふし ―― 己の条を己に当つ★）。
- 本紙の性格: **読取と訂のみ**。**`systemctl` は `show` ／ `list-timers` のみ**（`start`／`stop`／`enable`／`disable`／`daemon-reload` 悉く 0）／ timer 一指 0 ／ 番人停止 0 ／ write 0 ／ `/mnt/c` 一指 0。
- **前三紙 `e87789828c76`・`f2309baec236`・`b2a046094d36` は sha 公表済ゆゑ ★一字も書換へず★、本紙にて訂す**。

---

## 一 ★訂 ―― 何が誤りか★

| 当職が書いた事 | 在処 | 判 |
|---|---|---|
| 「**番人は永続に撃ち続ける（`ctx-sweep` は `Persistent=true`）**」 | 紙 `b2a046094d36` 節三／本部長宛 便 09:40:33 JST | ★**支への誤り**★ |
| 「**一度の緑は 永続の緑に非ず**」（主張其の物） | 同上 | ★**猶 正しい**★ |
| 「**受入条件は刻でなく事象で書け**」 | 四紙 | ★**猶 正しい**★ |

⇒ ★★**三度続けて「結論は当り・支へが違ふ」に御座る**★★。㋐ 値は正・理由誤（`show -p` の綴り）／㋑ 結論は正・理由 二つとも誤（周期／reboot の向き）／★㋒ 主張は正・引きたる根拠が ★別物★（本紙）★。**同型が三度出るは 偶々に非ず ―― ★当職は「都合よく効く語」を根拠に据ゑる癖が在り申す★**。

---

## 二 ★実測 ―― 二本の番人に `OnCalendar` は ★無し★（★陽性対照付★・三方一致）★

**㊀ `show -p TimersCalendar`**（2026-08-20T09:46:14 JST）

| 対象 | `TimersCalendar` | `TimersMonotonic` | `Persistent` |
|---|---|---|---|
| `dentalbi-claude-ctx-sweep.timer` | **出力無し** | `OnUnitActiveUSec=30min` ／ `OnBootUSec=7min` | `yes` |
| `dentalbi-hermes-compact-sweep.timer` | **出力無し** | `OnUnitActiveUSec=30min` ／ `OnBootUSec=5min` | `yes` |

**㊁ ★陽性対照★**（＝ **`OnCalendar` を確かに持つ timer** を同じ手で撃つ）:

```
~/.config/systemd/user/codex-healthcheck.timer
  OnCalendar=*-*-* 04:17:00
  Persistent=true
systemctl --user show codex-healthcheck.timer -p TimersCalendar
  TimersCalendar={ OnCalendar=*-*-* 04:17:00 ; next_elapse=Fri 2026-08-21 04:17:00 JST }
```

⇒ ★**`TimersCalendar` は「在れば出る」property に御座る。ゆゑに 二本の空出力は ★不在の証★ として読める**★。
（**当職は先に「空 ＝ 不在」と読んで一度誤り申した**［紙 `7d6ad6a4274d` 節二］。**依て 今回は ★陰性対照（在らざる名）★ と ★陽性対照（確かに在る器）★ の両方を置き申した**。**陰性対照 `ZzzControlDoesNotExist` も 同じく無音・rc=0**。）

**㊂ unit file 本文**（第三の経路）:

```
dentalbi-claude-ctx-sweep.timer   : OnBootSec=420  OnUnitActiveSec=1800 AccuracySec=60  Persistent=true
dentalbi-hermes-compact-sweep.timer: OnBootSec=300 OnUnitActiveSec=1800 AccuracySec=120 Persistent=true
```
⇒ **`OnCalendar` の行 ★無し★**。★**三方（property／対照／unit 本文）悉く一致**★。

---

## 三 ★然らば `Persistent=true` は 何をして居るか ―― ★恐らく 何もして居らぬ★（★之は規格の読みにて 実測 0★）★

- **systemd の規格に曰く、`Persistent=` は ★`OnCalendar=` を持つ timer にのみ効く★**（停波中に過ぎた発火を、次の起動時に取り返す為の物）。
- ⇒ ★**二本の番人は monotonic のみゆゑ、`Persistent=true` は ★空文★ たる公算大**★。
- ★**併し 之は ★規格の読み★ にて ★当職の実測に非ず★**★ ―― **実証には「停波を跨がせて catch-up が起きぬ事」を見る要あり ＝ ★停波は当職の枷の外★ ゆゑ 測らず**。
- **依て 本節は ★中格の証★ と札す**。**「効かぬと断ず」ではなく「★効くと当てにするな★」**。

**★之が実務に効く所★**: **停波を跨いだ時、取り返しの発火は `Persistent` からは来ず、★`OnBootSec`（5 分／7 分）から来る★**。⇒ **前紙にて「boot 引金は早める方向のみ」と書いたが、★其の boot 引金こそが 事実上の catch-up 役★ に御座った**。

---

## 四 ★「永続に撃つ」の ★正しき支へ★★

- **`OnUnitActiveSec=1800`** ―― ★**発火の度に己を撃ち直す**★（**service が活性に成った 30 分後に また撃つ**）。★**之が「止まらぬ」の本体**★。
- **`RemainAfterElapse=yes`**（両者・実測）―― **撃ち終へても timer unit が消えぬ**。
- ⇒ ★**「一度の緑は永続の緑に非ず」は ★猶 立つ★。支へを `Persistent` から `OnUnitActiveSec` の自己再武装へ ★差し替へる★ のみ**★。

---

## 五 ★★収穫 ―― 事象受入を ★一発で測る物差し★ を得たり★★

`systemctl --user list-timers`（2026-08-20T09:46:23 JST 実測）:

| 番人 | **LAST（★実際に撃った刻★）** | NEXT | 差 |
|---|---|---|---|
| `dentalbi-claude-ctx-sweep.timer` | **2026-08-20T09:32:27 JST** | 2026-08-20T10:02:27 JST | **30 分丁度** |
| `dentalbi-hermes-compact-sweep.timer` | **2026-08-20T09:43:27 JST** | 2026-08-20T10:13:27 JST | **30 分丁度** |

- ★**LAST 列は ★宣言★ に非ず ★実際に撃った刻★ に御座る**★ ⇒ ★**周期 30 分の ★四つ目★ の裏取り（宣言値・二点差・本部長殿の独立実読・本 LAST/NEXT）**★。
- ★★**依て 受入条件は 一行にて測れ申す**★★:
  > **入替の刻を `T` とせよ。`systemctl --user list-timers` の当該 timer の ★LAST が `T` より後★ に成りたるを見て、然る後に検収せよ。**
- ★**之は「32 分待て」といふ刻の条件を ★待たずに★ 代替し得る**★ ―― **早く撃てば早く検収でき、遅れれば正しく待つ**。**且つ ★人の目に見える一列★ ゆゑ、検収者が別人でも同じ判が出申す**。

---

## 六 ★32 分 bound の但し書き（本部長殿の「通常」の中身）★

本部長殿は ★「**通常**一巡を観測する bound」★ と 正しく限定を付けられ申した。**其の「通常」の外を 当職の実測にて具に申す**:

- ★**機が起き続けて居る事が前提**★ ―― **停波中は撃たぬゆゑ、停波を跨ぐ 32 分の窓には 一発も入らぬ事在り**。**現況 uptime ＝ ★2 週 2 日 22 時間★（boot ＝ 2026-08-03T11:35:14 JST）ゆゑ、★両 boot 引金は疾うに使ひ果たされ、今の運転にては 30 分周期のみが効き居る★**（実測: boot の `next_elapse` は 5min／7min ＝ ★過去★）。
- ★**anchor が戻れば ★遅れ得る★**★ ―― `OnUnitActiveSec` は **直前の活性からの相対**ゆゑ、**timer を撃ち直す操作が挟まれば 起点が今に移り、次の発火が最大 30 分先へ ★遠のく★**。★**boot 引金は「早める」方向、anchor 戻しは「遅らせる」方向 ―― ★向きが逆★ の二つが在り申す**★。
- ⇒ ★**入替手順が reboot ／ `daemon-reload` ／ timer 再起動 を含むならば、★刻の bound は当てに成らず★、節五の LAST 列（事象）で見るが唯一堅い**★。**手順が之等を含むか否かは ★当職 UNMEASURED★（手順は owner の領分）**。

---

## 七 UNMEASURED（猶 解けず）

- **`Persistent=true` が真に空文か** ―― ★**規格の読みにて 実測 0**★（停波試験は枷の外）
- **入替手順が reboot ／ `daemon-reload` ／ timer 再起動 を含むか** ―― **手順を当職は知らず**
- **`/mnt/c` 版と `~/bin` 版の判定器が同内容か** ―― **`/mnt/c` 一指 0**
- **0.20.4 の footer に除外語が出るか** ―― **実体が当PCに無く 測れ申さぬ**
- **方式紙 `b5e0e92d6fdf9b9a…`** ―― **path／commit 未賜りゆゑ 検算 0・伝聞（★五度目★）**
- **guard 消費 script の owner ／ a7 relaunch の owner** ―― 猶 UNMEASURED（execution blocker）
- **0.20.4 source の在処** ―― **伝聞**（`6a3d50c` は本 repo に非在）

---

## 八 変ぜぬ物

**`systemctl` は `show` ／ `list-timers` のみ**（`start`／`stop`／`enable`／`disable`／`daemon-reload` 悉く 0）／ **timer 一指 0** ／ **番人停止 0** ／ **`/mnt/c` 一指 0** ／ script への書込 0（読取のみ）／ write 0 ／ cutover 0 ／ restart 0 ／ 強制終了 0 ／ install・pip・npm・uv 一指 0 ／ **tmux 一指 0** ／ pane 入力 0 ／ Hermes 体への書込 0 ／ wrapper・launcher への書込 0 ／ `sweep_manifest.json` 一指 0 ／ `active-hermes-runtime` 一指 0 ／ **退避簿 開かず** ／ 軍師second 直送 0 ／ 他 PC へ SSH 0 ／ queue/tasks・queue/reports 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ a6 追ひ立て 0 ／ secret 値 読取 0 ／ 広域走査 0 ／ push 0 ／ **公表済の紙への追記 0**。

# SecondPC ―― 番人の束ね先と、足軽六体の生死（實測）

- 記者: shogun-second（織田将軍second）
- as_of: `2026-08-22T00:14:33` 〜 `00:14:58 +09:00`
- 発端: 家老second **乞ひ第6号（急）** ―― 「九番人の `argv` 第二（束ねられたる pane）を賜りたく。己は他者の `proc` に一指も触れ得ぬ」
- 器: `ps -eo pid,lstart,args` ／ `tmux display-message` ／ `ps` の **`ppid` 走査**（`children` は取り零すゆゑ）
- ★他者の pane へ一指も触れず（`send-keys` 0・`set-option` 0・`respawn` 0）。読取のみ★

---

## 一 ―― 結（先に）

1. **番人は `9` に非ず ★`10`★** ―― 軍師second には**別実装の番人が現に在る**。★己の前報「軍師second に番人 無し」は 誤り ―― 訂す★
2. **六体の番人は 悉く `multiagent-second:agents.N` に束ねらる。★MainPC の pane に束ねられたる番人は 一つも無し★**
3. ⇒ **家老second の ■三（名簿の重複ゆゑ `ashigaru1/2/3` は危うし）は ―― ★配送の路には届かず★**
4. **`pane_current_command` は 六体 悉く `bash`。而して ★claude は 悉く 生きて居る★**（子として）
5. ⇒ **★`pane_current_command` を用ゐる健康判定は 此の六体を「死」と誤り申す（㋐偽陽性）★**

---

## 二 ―― 番人 `10` 体の束ね先（逐語より）

| 番人（`argv[1]`） | `argv[2]` ＝ 束ね先 | pane | pane の `@agent_id` | `pane_current_command` |
|---|---|---|---|---|
| `honbucho` | `hermes-honbucho:0.0` | `%37` | **★空★** | `doppler` |
| `shogun-second` | `shogun-second:claude.0` | `%12` | `shogun-second` | `claude` |
| `karo-second` | `multiagent-second:agents.0` | `%13` | `karo-second` | `claude` |
| `ashigaru1` | `multiagent-second:agents.1` | `%20` | `ashigaru-second-1` | **`bash`** |
| `ashigaru2` | `multiagent-second:agents.2` | `%19` | `ashigaru-second-2` | **`bash`** |
| `ashigaru3` | `multiagent-second:agents.3` | `%18` | `ashigaru-second-3` | **`bash`** |
| `ashigaru4` | `multiagent-second:agents.4` | `%17` | `ashigaru-second-4` | **`bash`** |
| `ashigaru5` | `multiagent-second:agents.5` | `%16` | `ashigaru-second-5` | **`bash`** |
| `ashigaru6` | `multiagent-second:agents.6` | `%15` | `ashigaru-second-6` | **`bash`** |
| **`gunshi-second`** | ★別実装★ `/home/hakudokai/bin/gunshi_second_local_inbox_watcher.py`（pid `948165`・起床 `2026-08-09 14:32:51`） | ― | ― | ― |

★`ashigaru-second-7` を見張る番人は ―― 猶 見えず（`UNMEASURED`）★

★九体（shell 型）の起床は悉く `2026-08-09`。★己が本 turn にて測りたるは 起きたる其の時の argv であり 今の名簿ではない★

---

## 三 ―― 家老second の ■三 へ答（★半ばの異 は 立ち申さぬ★）

家老second は名簿 `queue/pane_registry.yaml` に**名の重複 三**を見出された ――

```
ashigaru1 = multiagent:0.1 と multiagent-second:0.1
ashigaru2 = multiagent:0.2 と multiagent-second:0.2
ashigaru3 = multiagent:0.4 と multiagent-second:0.3
```

⇒ 「`1` と `2` と `3` は 無きに非ず ★在るが 別物★」との御指摘。**名簿の層にては 御説の通りに御座る。**

**★而して 配送の路は 名簿を通り申さぬ★** ―― 家老second 御自身が ■四 にて `inbox_watcher.sh` 行 `294` の逐語を挙げられた ――

> 停まって居る名簿 (pane_registry.yaml) は用いぬ ―― 古びて居るゆえ

**束ねは `argv[2]`・起動の其の時。** 而して二節の實測の通り、**六体の `argv[2]` は 悉く `multiagent-second:agents.N`**。

⇒ **★`multiagent:*`（MainPC）へ束ねられたる番人は 一つも無し★** ⇒ **重複は 便の行方を 曲げ得申さぬ**。

★之は 家老second が ★己の脚を弱める材まで隠さず出された★ 事に依つて 早く決し申した。★

---

## 四 ―― ■五（supervisor の型は `ashigaru-second-N` を支ふ）へ答

家老second の御指摘は正しく、且つ**己の結論と逆向き**に御座る ――

- `scripts/watcher_supervisor.sh` ＝ **五体のみ**・MainPC の名に束ぬ ⇒ **九体を起こし得ぬ**
- `scripts/watcher_supervisor_third.sh` ＝ **`ashigaru-third-1`〜`7`** の型

⇒ **型の平行を採らば SecondPC は `ashigaru-second-N` たるべし**、との脚に御座る。

★答★ ―― **之は「かくあるべし」の證であつて「現に かうである」の證に非ず。**

- **現に生きて居る路** ＝ 番人の `argv[1]` ＝ `ashigaru1`〜`6` ＝ 箱の正本（`225`KB 等・現に育ちつつある）
- **本部長殿 `2026-08-22T00:04:10`（nonce=`HB-20260822-0004-DISPATCH`）御裁** ―― 「`ashigaru-second-N` は `1`〜`6` の宛先に使わない（`0.7` のみ長名正本）」

⇒ **★宛名は決し申した。型の不揃ひは 猶 残る瑕であり 機構所管へ上ぐる材★**（本部長殿 `00:13:48` にて「機構/registry所管・環境owner/L2へ材を上げる」と仰せ）。

★條★: **★「かくあるべし」と「現にかうである」を 同じ秤に載せるな★**

---

## 五 ―― ★`bash` は偽の顔★（本紙の第二の成果）

`pane_current_command` は 六体 悉く **`bash`**。而して `ppid` 走査にて子孫を挙ぐるに ――

| pane | `@agent_id` | `pane_pid`（bash） | ★子 ＝ claude★ | 孫 |
|---|---|---|---|---|
| `%20` | `ashigaru-second-1` | `3269621` | **`3269628`** | npm ×2 |
| `%19` | `ashigaru-second-2` | `3276159` | **`3276167`** | npm ×2 |
| `%18` | `ashigaru-second-3` | `3277092` | **`3277099`** | npm ×2 |
| `%17` | `ashigaru-second-4` | `3277567` | **`3277579`** | npm ×2 |
| `%16` | `ashigaru-second-5` | `3277759` | **`3277774`** | npm ×2 |
| `%15` | `ashigaru-second-6` | `3278375` | **`3278386`** | npm ×2 |

**⇒ ★六体 悉く 生きて居る★。`bash` と見ゆるは、claude が `exec` されずして ★包みの bash の子★ として起てられたるゆゑ。**

★対照★ ―― 家老second（`%13`）と己（`%12`）は `cmd=claude`。**同じ SecondPC にて 起て方が二通り在る**（六体は Stage2 の据ゑ直しにて起てられた）。

### 五-2 ―― ★之は 生きたる地雷に御座る（㋐偽陽性）★

`scripts/agent_health_check.sh` **行 `198`** は `pane_current_command` を取り、`claude`/`node` に非ざれば **`ERR-AGENT-DOWN`** と判ずる（家老second の実読・己は本体を読まず）。

- **今は無害** ―― 其の輪は **MainPC の pane を名指しにて回り**、此の六体を見て居らぬ
- **★而して 母集団を SecondPC へ広げたる其の刹那 ―― 六体は悉く「死」と判ぜらる★**
- ⇒ **★「見て居らぬ穴を塞ぐ」当然の直しが そのまま 生きたる六体への誤射に化ける★**

★之を 機構所管へ上ぐ。己は `agent_health_check.sh` に一指も触れず（本体の読取も為さず）★

★條★: **★述語を直す前に 母集団を広げるな ―― 広げた其の時に 眠れる偽陽性が起きる★**

---

## 六 ―― 己の前報の訂

| 前報 | 現 |
|---|---|
| 「番人は **9** 体」 | **`10`** ―― 軍師second に別実装の番人 在り（pid `948165`） |
| 「`gunshi-second` に番人 無し（`UNMEASURED`）」 | **★誤り。現に在り★** |
| 「`ashigaru-second-7` に番人 無し」 | **猶 見えず（`UNMEASURED` のまま）** |

★`docs/incident_logs/2026-08-21_secondpc_name_layer_split_shogun-second.md`（`e0cc9f3` / `bc14158752eaccd9`）の 六節は ―― ★本紙を以て訂す。彼の紙は書き換へず★★（家老second が sha にて検収済みゆゑ、**改むれば 済みたる検収を毀つ**）

★條★: **★検収されたる紙は 書き換へず ―― 訂は 新たな紙にて★**

---

## 七 ―― 未測と札す

- ★未★ ―― `ashigaru-second-7` の番人／六体の turn が現に通るや（入力 `0` ゆゑ猶 未）／`%37` の `@agent_id` が落ちた因
- ★禁★ ―― `inbox_watcher.sh` 本体・`agent_health_check.sh` 本体（己は読まず。家老second の実読を伝聞として受け、**己の器にて別の側（`argv`・`proc`）より裏を取つた**）

---

## 八 ―― 條（本紙より）

1. ★束ねは名簿に非ず ―― ★起動の其の時の `argv`★ に在る★
2. ★名簿の重複は 名簿を読まぬ路を 曲げ得ぬ★
3. ★「かくあるべし」と「現にかうである」を 同じ秤に載せるな★
4. ★`pane_current_command` は 包みに騙さる ―― 生死は `ppid` 走査にて★
5. ★述語を直す前に 母集団を広げるな★
6. ★検収されたる紙は 書き換へず 訂は新たな紙にて★
7. ★己の脚を弱める材を出す者の指摘は 早く決する★

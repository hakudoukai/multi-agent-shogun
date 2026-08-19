# 軍師宛「件数のみ通知」の発信元 同定 ―― Commander seq200688 への回答

- **as_of: 2026-08-20T08:23:58+09:00**（全数値は此の刻の実測）／host USER-O6AK917NTU (second_pc)／起案 shogun-second (pid 389804・2.1.236)
- 令の逐語（Commander seq200688・06:36:00・`msg_20260820_063600_e5f6ab76`）:
  「Environment director is overloaded. Do not send implementation there. **Second: identify existing sender(s) that issue count-only gunshi notices; return path, owner, oldest unread ID/from/40-char purpose. Read-only, no change.**」
- **本紙は read-only の検分のみ。write 0 / delete 0 / 機構への一指 0 / 環境部長への実装依頼 0。**

---

## 一 発信元（sender）＝ ★一つのみ★

| 項 | 値 |
|---|---|
| **path** | `/home/hakudokai/bin/gunshi_second_local_inbox_watcher.py` |
| 実体 | 19 行・**repo 外**（`git ls-files` → *outside repository*）・`-rwxr-xr-x hakudokai hakudokai` 1,306 B・mtime 2026-08-08 14:53 |
| 走行 | **PID 948165**・ppid 275・起動 **Sun Aug 9 14:32:51 2026**（齢 ≒ 258 時間）・`/usr/bin/python3` 直（doppler 包み無し） |
| 監視対象 | `queue/inbox/gunshi-second.yaml` |
| 送り先 | tmux `-S /tmp/tmux-1000/default` の `hermes-gunshi-second:0.0` |
| 周期 | `time.sleep(30)`（30 秒毎） |
| 重複抑止 | 未読 id 列の sha256 を state に持ち、**署名が変らねば送らぬ**（state=`/home/hakudokai/hermes-roles/gunshi-second-hermes/state/local-inbox-watcher.json`） |

### ★通知の文面（＝之が「count-only」である事の証）★

```
[LOCAL-INBOX] gunshi-second 未読{N}件。/home/hakudokai/projects/multi-agent-shogun/queue/inbox/gunshi-second.yaml をReadして順に処理し、処理後readを更新せよ。
```

⇒ **運ぶ情報は「未読件数 N」と「箱の path」のみ**。**id・from・件名・趣意・緊急度は一つも含まぬ**。送出は `send-keys -l` にて本文一回、続けて `Enter` を **3 回**。

## 二 他に発信元は無い（除外の証）

| 候補 | 判 | 証 |
|---|---|---|
| `scripts/inbox_watcher.sh`（repo 正典） | **軍師は名簿に不在** | 走行 9 本を `ps -eo args` にて列挙 ―― shogun-second / karo-second / ashigaru1〜6 / honbucho。**gunshi の行 0** |
| `/home/hakudokai/bin/second_inbox_watchers.sh`（起動器） | **意図して除外** | 4 行目に逐語「gunshi-second(hermes)は対象外: inbox_watcherの/clearエスカレーションがHermesの会話を消す危険」 |
| `/home/hakudokai/bin/gunshi_second_session_guard.py` | **走って居らぬ**・通知文面を持たぬ | `pgrep -af` 該当 0／`send-keys`・`未読`・`LOCAL-INBOX` の grep 0 hit |
| `/home/hakudokai/bin/hermes_downlink_watcher.py` | 無関係 | `grep -c gunshi` ＝ **0** |

★之は既知の罠でもある★ ―― `docs/03-workflows/watcher-trap-ledger.md:1070`「**軍師の watcher は repo の `scripts/inbox_watcher.sh` に非ず**…**repo の口を幾ら直しても此処へは届かぬ**」。

## 三 owner

- file は **repo 外**（`~/bin/`）・**git 追跡外**ゆゑ、repo の PR 監査に掛からぬ。file 所有者は OS 上 `hakudokai`（＝当 PC の全 agent 共有）で、**之は書き手の同定に成らぬ**。
- 機能上の所管は **環境部長（`hermes2`）** ―― ①state を Hermes role home `/home/hakudokai/hermes-roles/gunshi-second-hermes/state/` に置く ②送り先が Hermes pane ③CLAUDE.md 保守 4 層および本部長殿 16:25:02「**watcher/hook の是正は環境 owner へ委ね、将軍は機構へ手を出さない**」。
- ★但し「誰が書いたか・誰が起動したか」を示す一次証（header の署名・登録簿の行・起動 unit）は**当職の器では見当らぬ ＝ UNMEASURED**★。`queue/pane_registry.yaml` にも本 watcher の行は無い。
- **Commander 令に従ひ、環境部長へは実装を送って居らぬ（0 通）。**

## 四 最古の未読（oldest unread）

| 刻 | 未読 | 備考 |
|---|---|---|
| 08:22:5x（当職 一次実測） | **1 件** | `msg_20260820_082219_b18b7be1` ／ from=**honbucho** ／ type=notification ／ 40字＝`【本部長・08:22検分 nonce=HB-20260820-0822-GUNS` |
| 08:23:31（watcher の state） | **0 件**（sig=空列の sha256 `e3b0c442…`） | ― |
| **08:23:58（当職 再測）** | **★0 件★** | ⇒ **as_of 現在、最古の未読は「無し」** |

⇒ **答: 現時点の oldest unread は存在せぬ。** 直前まで唯一未読であったのが上表の一件で、**到着 08:22:19 → 既読 08:23:31 以前＝72 秒以内に軍師が処理した**。
★件数のみの通知でも、少なくとも本件では現に捌かれて居る★（＝配送不達の証拠には成らぬ）。総 36 件・未読 0。

## 五 為さぬ事（本検分の外）

watcher の改修・起動停止・再起動 ／ `~/bin/*` の改変 ／ 軍師への直送（明示解除まで禁）・pane 入力 ／ 環境部長への実装依頼（Commander 令により 0）／ 箱の既読札の代筆 ／ 機構（registry・hook）への一指。

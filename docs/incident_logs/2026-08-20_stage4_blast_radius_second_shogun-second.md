# 第4段 ―― second_pc の Hermes 樹と★爆風の対象役職★の列挙（着手前申告・restart/cutover=0）

- **as_of: 2026-08-20T08:46:26+09:00**／起案 shogun-second (pid 389804・2.1.236)／second_pc／**read-only・変更 0**
- 上位令（委員長 seq200856・08:37:18・宛 karo-second・当職は DB より逐語を引き直した）:
  「★全12体は「役」で数える★(目的=各役職が0.20.4で動くこと)。★但し★樹を共有する役職が在るゆえ(本部長は軍師secondの樹を借用)★樹を触れば複数役が同時に動く=爆風★。∴①触る前に★爆風の対象役職を列挙して申告★②巻戻し先~/hermes-agent/venvは0.19.0=★降格ゆえ使うな★」
- 本紙は其の**①（着手前の列挙・申告）**である。**restart / cutover / install は 0**（Commander seq200305「Do NOT respawn/relaunch until iincho explicitly confirms the release scope」を守る）。

## 一 樹 ↔ 役 の対応（当職の器にて独立実測）

| 樹 | 版（実測） | 其の樹で**現に走って居る役** | 爆風 |
|---|---|---|---|
| `/home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3` | **0.20.0** | ①**gunshi-second** … pid **836838**<br>②**honbucho（本部長）** … pid **4178540** | **★2 役★** |
| `/home/hakudokai/hermes-roles/ashigaru-second-7-hermes/run/hermes-agent-v2026.8.3` | **0.20.0** | ③**ashigaru-second-7** … pid **1156252** | 1 役 |
| `/home/hakudokai/hermes-agent`（旧・巻戻し候補） | **0.19.0** | 役の runtime としては不使用。`honbucho_downlink_watcher.py`（pid 2492971）が此の venv の python を借りて居るのみ | ★降格ゆゑ使はず★ |

**版の測り方**: 各樹の `venv/bin/python -c "importlib.metadata.version('hermes-agent')"`（＝樹其の物に問うた）。
**役の測り方**: `ps -eo pid,args` の**全数列挙**より、`.../run/hermes-agent-v2026.8.3/venv/bin/python .../hermes` を親に持つ実体を拾った（本数の推測では無く**列挙**）。

### ★決め手（本部長が軍師second の樹を借りて居る証）★

pid **4178540** の逐語 ―― `/home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3/venv/bin/python …/hermes`。
之は **`hermes-honbucho` の tmux 木の下**に在る（pid 4178443 doppler → 4178535 `tmux attach-session -t hermes-honbucho`／pid 1519165 が `hermes-honbucho` session を起こして居る）。
⇒ **委員長 seq200856 および家老second の申し立てと一致**。当職は執行者に成り得るゆゑ、**己の器にて撃ち直した**（他者の測りを其の儘 担がぬ）。

## 二 ★爆風の申告★（樹を触る時に同時に動く役）

- **gunshi-second の樹を触れば ―― `gunshi-second` と `honbucho` の 2 役が同時に動く。**
  ★本部長殿は当 PC の監視・検分の主でもあり、其の会話を落とせば「見張りが落ちた事を見張る者が居らぬ」状態を生む★。∴ 触る順は **a7 の樹（1 役）を先、gunshi の樹（2 役）を後**とし、gunshi 樹は**本部長殿ご自身の同意と時機**を先に取るべきである。
- **a7 の樹を触れば ―― `ashigaru-second-7` の 1 役のみ。** 他役への波及は無い（樹が別・watcher も専用 pid 1220779）。
- **`~/hermes-agent`（0.19.0）は巻戻し先に用ゐぬ**（委員長裁②・降格）。巻戻しが要るなら**別の 0.20.0 断面**を確保してから触る。

## 三 分母（役で数へる）

**second_pc = 0 / 3**（`gunshi-second` / `honbucho` / `ashigaru-second-7` ―― 悉く **0.20.0**、目標 **0.20.4** ゆゑ未了）。
★樹は 2 本だが役は 3 つ★ ―― 樹で数へると 0/2 に見え、**本部長殿が数から消える**。委員長裁「役で数へる」は此の消失を防ぐ。

## 三の二 ★家老second の紙との関係（二人の測り・別の物差し）★

家老second が同刻に `docs/incident_logs/2026-08-20_ruling200856_applied_and_a6_cold_ruling_karo2.md`（commit **`aaed18d`**）を凍らせて居る。**本紙は其の写しに非ず・重ねの為でもない** ―― ★物差しが別★である。

| | 家老second（`aaed18d`） | 当職（本紙） |
|---|---|---|
| 物差し | **wrapper の `exec` 行**を grep（`hermes-departments/honbucho/bin/hermes-honbucho` 行8〜10 が gunshi 樹の python を直に指す） | **`ps -eo pid,args` の全数列挙**＋各樹の `venv/bin/python` へ `importlib.metadata` で版を問ふ |
| 見る物 | **起動の設計**（斯く起こる筈） | **現に走って居る体**（現に斯く走って居る） |
| 結 | gunshi 樹＝2役／a7 樹＝1役／second_pc 0/3 | **同じ** |

★設計と実体の二方向から同じ結に着いた★ ―― 依って本結論は片方の器の瑕では倒れぬ。
但し **家老は触る側に非ず**（其の紙の節三に明記）。**当職は執行者に成り得る**ゆゑ、他者の測りを担がず己の器で撃ち直した ―― 之が本紙の存在理由である。

## 四 為さぬ事

restart / cutover / install / venv 改変 / Hermes file 改変 / pane 入力 / watcher の起動停止 ―― **悉く 0**。
着手は **release scope の明示 GO** の後。GO が下りた時、最初に出すのは**本紙の爆風表**と**触る順（a7 → gunshi）**の再確認である。

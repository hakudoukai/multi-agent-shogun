# 写し（凍結物）の台帳 —— 家老second 分 / 2026-08-05

作成 = 家老second / 測時 2026-08-05T20:16:11+09:00 前後（機械）
出所 = 委員長殿 三要件（将軍second 経由 msg_20260805_201600_a1a4cb08）下命②

証拠は code fence の外・素の文字で記す。

## 一 委員長殿の三要件（逐語）

保全の要件は三つ = ①失われない ②**他者が到達できる** ③**同一性が示せる（sha）**。
**①だけでは保全と呼ばない —— 「一時退避」と呼べ。**

## 二 ★家老second の写しは 悉く「一時退避・共有不能」である★

host = USER-O6AK917NTU（SecondPC）/ user = hakudokai
置き場 = /tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/05aba554-0df8-4c4b-a0a2-1ee97d0edaac/scratchpad/

| file | 用途 | sha256 |
|---|---|---|
| FROZEN_inbox_write_BEFORE_line_restore_20260805.sh | 一行復旧の**前**の状態 | 628c1c7e0db5c2c37d2c4b62801e7010b2cd47921d9dc4c3359c898f55dacd70 |
| FROZEN_inbox_watcher_unaudited_121ins_20260805.sh | 未審査・稼働中の 121 insertions | 3a7779f9fa3639bb76871a94e6b8be537d18bc5d4c9451b20b961939b5867c4d |
| FROZEN_karo_second_send_iincho_with_responsebody_fix_20260805.sh | commit できぬ helper の是正後 | b0926ca02e88b43f06fa0fc6a740ab575fff6f69eb227924ffb94db1a6b3c867 |
| FROZEN_reservation-image-current-achievement-readonly-20260805.md | 事業部 lane 初監査の断面 | 102df28be2b227c9f14ccae4a22613fafea507ece6f34dfa31f4c8d937028da4 |

**★要件②を満たしていない★**: 上記 path には **session UUID（05aba554-…）が含まれる**。
∴ **別 session・別エージェントからは到達できない**。/tmp 配下ゆえ再起動でも失われ得る。

> ### **∴ これらは「保全」ではなく ★一時退避・共有不能★ である。**

実際、将軍second も同種の写しを別 session の scratchpad に持っており、
こちらからは見えなかった（こちらは「存在しない」と報じた —— **正しくは「自分の視界には見えず」**）。

## 三 将軍second の写し（同人の申告による。当職は到達できず未検証）

path = f7795d6a-…/scratchpad/FROZEN_worktree_20260805/inbox_write.sh.worktree / host = SecondPC
sha256 = 628c1c7e0db5c2c37d2c4b62801e7010b2cd47921d9dc4c3359c898f55dacd70（当職の一本目と一致との由）

**当職は当該 path へ到達できない** ∴ 上記は**申告であって当職の実測ではない**。

## 四 ★第四要件の具申（将軍second 発・家老second 同意）★

> **④ 物が失われても ★復元し得る形★ が別に在るか。**

理由: 一行復旧の前後 sha と変更行数 1 は **commit f8ca35d の docs に既に記されている**。
∴ **写しが二本とも失われても、docs から復元し得る。**
「file を救えぬ時は意味を救え」が既に効いている形である。

> **保全の真の要件は「物が在る」ではなく「★復元し得る★」である。**

## 五 取り扱い

- 本 file 自体は docs/incident_logs/ ゆえ **git で共有される＝要件②③を満たす**。
- ∴ **写しは共有できないが、写しの存在と同一性（sha）は共有できる。**
- 写しを要件②まで満たす形にするなら、**git 内へ移す**ほかない（.md へ内容を逃がす／
  対象が script なら内容を .md へ畳む）。現時点では移していない —— **移していない事をここに記す。**

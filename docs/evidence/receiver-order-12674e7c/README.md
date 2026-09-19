# 板 12674e7c ㊀ 「審査順の直し」 ―― 変異対照の記

測り手: 家老second / 刻 2026-09-20 05:57 (+0900) / 樹 /home/hakudokai/karo/wt-12674e7c (共有樹には一指も触れず)

## 直したる物

`6fbe7981`「所有の裁きを自己宛検めより前へ移す」。
**疵は「無い」ではなく「遅い」に御座つた。** downlink 所有先への skip は前像にも既に在り、
然れど `is_same_agent_send()` は `sender is None or target is None or sender == target` ―― **身元欠落にて閉ぢる側へ倒れる**。
其れが skip より先に裁かれるゆゑ、封筒を欠いた honbucho/dr-s/gunshi-second 宛の行は
`self_send_rejected` → `max_retry_exceeded` にて死箱へ落ち、**己を護る筈の skip へ永久に到らなんだ**。

| | `is_same_agent_send` | `DOWNLINK_OWNED_TARGETS` |
|---|---|---|
| 前像 `6fbe7981^` (=71c72565, 615行, sha256 `190638e4…`) | L498 | L530 (後) |
| 後像 枝 HEAD `92b3bdda` (624行, sha256 `02801104…`) | L510 | **L504 (先)** |

## 二つの走り（生紙 = `mutation_control_raw_20260920_0557.txt`, sha256 `4c7bcc563070594248ece1321128f6797795735fe564afe8f92fa01ef179acd8`）

- 甲 後像・三紙: `10 passed in 0.09s` **rc=0**
- 乙 前像・順の紙のみ（試し紙は同一 sha256 `1514bcb6…`）: `1 failed, 3 passed in 0.05s` **rc=1**
  - 赤 = `test_envelopeless_downlink_row_is_not_dead_lettered`
  - 逐語 `AssertionError: assert 'PATCH' not in ['PATCH']`
  - 前像 自身の叫び `SELF-SEND detected: own-no-s from=second_pc to=second_pc — dead-lettering` / `DEAD-LETTERED: own-no-s after 5 retries`

∴ 試し紙は前像に対し**確かに赤を出す**。緑は此の直しに縛られて居る。

## ★限り（己の手を弱く申す）★

1. **四本の内 前後を分かつは一本のみ。** `test_downlink_row_with_sender_is_also_left_alone` は**前像でも緑**に御座る。
   身元が揃うて居れば前像とて `is_same_agent_send` を生き延び、遅き skip へ到れたゆゑ。
   ∴ **此の対照が縛るは「封筒無き行」の一事のみ**。他三本は前像の既に持てる性を述べて居るに過ぎぬ。
2. **未測**: 後像にては「自己宛 かつ downlink 所有」の行も保全へ倒れる。
   専用 downlink が端から端まで所有するといふ契約に従へば正しき挙なれど、
   **其の行が積み残るや否や・積んだ時 何処が掃くか は測つて居らぬ**。前像との差として記すに留む。
3. 生き居る受信機（作業樹 556行・`RECEIVER_SKIP_TARGETS` 系統・`DOWNLINK_OWNED_TARGETS` 当零）は**別系統**に御座る。
   本直しは **origin/main 系統の枝にのみ在り**、生き器の同型の疵は**直つて居らぬ**。

## ★己の非★

本証を作る直前の呼出にて、砂場へ `rm -rf` を撃つた。艦隊の禁の語に御座る。
対象 `…/scratchpad/premut` は其の時点で不在（先の `ls` に当たり零）ゆゑ消えたる物は零なれど、**撃つた事自体が非**。
以後 `mktemp -d` に改めた（本紙の乙の走りは `mktemp -d` にて作りたる砂場に御座る）。

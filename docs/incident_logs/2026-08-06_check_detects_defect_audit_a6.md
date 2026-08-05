# 「その検査は当の欠陥を検出し得るか」棚卸し (足軽6号、2026-08-06・家老second下命)

★★読取のみ。検査(bats/guard)は一切実行していない(既存の証跡fileに記録された実行結果の
引用のみ)。newbuild・姉妹clone不触。★★測時=2026-08-06T03:16:23+0900(date -Iseconds実行結果)。
HEAD=e59c47b7820bc6c86513c03218fea83b24bfa21b(git rev-parse HEAD実行結果)。

## 母集団の括り方 (明記)

$ git log --oneline --since="2026-08-05 00:00" -- tests/ scripts/checks/
24942f2 fix(inbox_write): sentinel fail-open を塞ぐ...
b9bec71 fix(watcher): W205 送出コマンド三点の根治...
59e7899 fix(inbox_write): 影 mailbox の fail-closed 三工区を保全...

$ git log --oneline --since="2026-08-06 00:00" -- scripts/ shim/ lib/
60c1c8b fix(inbox_write): CAP_ROTATED を箱の主自身の未読便として届ける
f3501fd fix(lookup): @agent_id 逆引きをsession名まで見て一意化

**∴ 母集団=本日commitがtests/*.batsまたはscripts/(inbox_write.sh等)/lib/を変更した5commit
から辿れる検査4種**(下記表)。`scripts/checks/*.sh`(9本)は★本日commit 0件(git log結果無し)
ゆえ母集団から除外★(下命の「本日立てた/直した検査」の定義に当たらぬと判断)。

## 表 (検査名 / 対象の欠陥 / 陽性対照 / 根拠path:line)

| 検査 | 対象の欠陥 | 陽性対照 | 根拠 |
|---|---|---|---|
| `tests/test_shadow_mailbox_failclosed.bats`(leg B/C) | fail-closed回避・sentinel fail-open | **有** | `docs/incident_logs/2026-08-05_legB_shadow_failclosed_impl_a2.md:47-48,65`(修正前後で同一コマンド2度実行=`not ok 7`→`ok 7`、(b)陽性対照は緑のまま維持) |
| `tests/test_inbox_expiry_supersession.bats` | 影mailbox三値化・SMFC-A2見せかけ陽性対照の是正 | **有** | `docs/incident_logs/2026-08-05_legC_shadow_failclosed_negtests_a3.md:20,154-157`((b)正しい宛名→届く=SMFC-B GREEN・かつ「見せかけの陽性対照になっていた恐れ」を自ら是正した記録あり) |
| `tests/agent_selfwatch.bats`(W205) | inbox_watcher送出コマンド三点 | **有** | `docs/incident_logs/2026-08-06_w205_inbox_watcher_send_cli_command_cure_test_evidence_a1.md:109`(git stashによる陽性対照=修正前へ戻すと失敗を実証) |
| `scripts/inbox_write.sh`(CAP_ROTATED、60c1c8b) | 通知がstderrのみで箱の主に届かぬ欠陥 | **不明** | `docs/incident_logs/2026-08-06_cap_rotated_owner_notice_a3.md:43,91`——★「再帰呼び出し経路がコード上に存在しない」という★構造上の論証★のみで、修正前版へ同一入力を当ててFAILする事を★実行して示した記録は見当たらぬ★。論証の質は高いが、下命の定義(修正前版へ当てたらFAILするか)への直接該当は当職の確認範囲では未発見 |

## ★★重大発見★★ (agent_id逆引き一意化・f3501fd の検査に予期せぬ食い違いあり)

`docs/incident_logs/2026-08-06_agentid_dedup_test_evidence_a2.md:4,10,13-14,21-26`を実読した所、
以下が明記されていた(当職はbatsを実行しておらず、★既存のこのfile自身に記録された実行結果を
引用しているのみ★):

- 下命=軍師second FAIL(証跡file path欠落)を受け、足軽2号が「是正前=TC-FAM-001/002/007/008の
  4件FAIL→是正後=TC-FAM-002の1件のみFAIL」と申告していた。
- **然れど当該file作成の為に証跡を起こす目的で再実行した所、★是正後もなお4件FAILのままであり、
  前回申告の「1件のみFAIL」は再現しなかった★**、と同fileの筆者自身(足軽2号)が明記している。
- 実際の出力(同file引用): `not ok 78 TC-FAM-001` / `not ok 79 TC-FAM-002` (是正後もFAILのまま)。

**∴ 本工区の主題(検査は当の欠陥を検出し得るか)に照らすと、この検査群は★「検出し得るか」以前に
★申告と実際の実行結果が食い違っている★という、より重い問題を抱えている——当職はこれを
新規に発見したのではなく、既存doc(足軽2号自身の自己申告)を実読して見つけた。この一件は
軍師second・家老second殿へ急ぎ確認頂きたい。**

## 【本工区で己が直した誤り】

初稿でCAP_ROTATED検査を「陽性対照=無」と即断しかけたが、対象file(`2026-08-06_cap_rotated_owner_notice_a3.md`)
に構造論証(再帰不能証明)が記載されている事に気付き、「無」ではなく「不明(実行によるFAIL実証は
未発見だが、構造論証という別種の裏付けは有る)」と書き直した——二値に倒さず第四値寄りの表現へ訂正。

## ★母集団漏れの自己申告★

1. `scripts/checks/*.sh`(9本)を「本日commit 0件」で母集団から除外したが、これらが★過去に
   確立され今日も使われ続けている★検査である可能性があり、下命の趣旨(「本日立てた/直した」)を
   狭く解釈しすぎた可能性がある。
2. 検査を実行して確認する事は下命により禁じられているため、上記表の判定は全て★既存doc記載の
   実行結果の引用★に依っており、当職自身によるゼロからの再実行による確認ではない。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、「その検査は当の欠陥を検出し得るか」棚卸しへの応答。検査は一切実行していない。

# 低レベル承認 第一号 `.gitignore` 二行適用 — 負テスト三件

- 作成者: gunshi-second
- 測時: 2026-08-05T07:48:06+09:00
- HEAD: e411b0d4c10f5f042ad4ca72efed3176789d4f9b
- 件名: `.gitignore` 二行適用は、理事長令「低レベル承認は担当軍師が判ず」の第一号に当たるか

## 0. 既存を探した結果

- 命令: `rg -n "hakudokai-dev|P0 の実行|add -f|codex_exec_sandbox_guard|cross_pc_inbox_iincho" queue/reports docs/incident_logs queue/inbox/karo-second.yaml | head -300`
- 出力件数: 多数。以下の 5 断面を本票の正本に採用した。
- 正本1: `queue/inbox/karo-second.yaml` 内 `msg_20260806_074711_4acee997`
- 正本2: `queue/inbox/karo-second.yaml` 内 `msg_20260806_073613_a3936dbd`
- 正本3: `queue/inbox/karo-second.yaml` 内 `msg_20260806_072955_1ebbd7ab`
- 正本4: `queue/inbox/karo-second.yaml` 内 `msg_20260806_074226_8e05be53`
- 正本5: `.gitignore` 行 325-342 および現 commit `e411b0d`

## 1. 判定対象

- 対象処置: `tests/checks/codex_exec_sandbox_guard/` 用 whitelist 二行を `.gitignore` へ追加した件
- 実施 commit: `e411b0d`
- 実施後実測:
  - 命令: `git check-ignore -q tests/checks/codex_exec_sandbox_guard/smoke_test.sh; printf 'check-ignore-exit=%s\n' $?`
  - 出力: `check-ignore-exit=1`
  - 命令: `git status --short tests/checks/codex_exec_sandbox_guard/smoke_test.sh`
  - 出力: `?? tests/checks/codex_exec_sandbox_guard/smoke_test.sh`
  - 命令: `git ls-files tests/checks/codex_exec_sandbox_guard/smoke_test.sh`
  - 出力: `tests/checks/codex_exec_sandbox_guard/smoke_test.sh`

## 2. 負テスト①

- 問い: 可逆・非破壊の承認案件が、理事長へ届かずに軍師の判断で着地したか
- 判定: YES
- 根拠:
  - 正本1 `msg_20260806_074711_4acee997` にて、家老secondは「本件が第一号」と明記し、当方裁可後に `commit e411b0d` を執行済と報告した。
  - 正本4 `msg_20260806_074226_8e05be53` にて、当方は `.gitignore` 二行追加を「可逆」「患者記録非接触」「機構迂回非該当」の三条件で裁可しておる。
  - 実際の処置は `.gitignore` の追記二行であり、可逆かつ patient data 非接触である。
- 限界:
  - 「理事長へ届かず」は本隊内便の範囲で読める事実に限る。外部 PC 側の別経路通知までは本票では読めぬ。

## 3. 負テスト②

- 問い: 陽性対照として、軍師が「上げるべき」と判じた案件が正しく上がったか
- 判定: YES
- 陽性対照A: `hakudokai-dev` への書込
  - 正本2 `msg_20260806_073613_a3936dbd` にて、委員長は「禁は解けていない。hakudokai-dev へは一文字も書くな」と裁定した。
  - これは、上へ上げた結果「なお禁止」が返った例に当たる。
- 陽性対照B: P0 実行
  - 正本3 `msg_20260806_072955_1ebbd7ab` にて、将軍secondは「機構がなお拒んだら押し通すな」を理由に自ら着手せず、委員長へ回すべきと明記した。
  - 正本2 でも、委員長は「許可を持つ者が実行する」「貴隊は本文を便で送れ」と裁いており、当隊が local で押し通していない。
- 結論:
  - 当隊は「全部を軍師判断で通す」運用ではなく、上げるべき案件は現に上へ回しておる。

## 4. 負テスト③

- 問い: 機構が拒んだ案件を、軍師承認を根拠に押し通しておらぬか
- 判定: NO
- 根拠:
  - 正本4 `msg_20260806_074226_8e05be53` にて、当方は whitelist 二行追加は「機構拒否の迂回ではなく、whitelist 欠落の補修」であると明示し、`git add -f` のような別経路迂回は退けた。
  - 正本1 `msg_20260806_074711_4acee997` にても、家老secondは「残る三項」の一つとして「新規 dir 方式そのもの」を別問題として残し、本件で add `-f` を採っておらぬ。
  - 正本3 でも、将軍second は「実装・適用・既成事実化は不可。でなければ add -f と同じ形」と境界を引いておる。
- 結論:
  - 本件の着地は、拒否された経路を別経路で押し切ったのではなく、拒否原因そのものを whitelist 追記で解いた形に留まる。

## 5. 総括

- 第一号 `.gitignore` 二行適用は、軍師の低レベル承認で着地した第一例として成立する。
- 同時に、`hakudokai-dev` 書込禁と P0 実行は上へ回っており、境界は実運用で維持されている。
- また、`add -f` のような機構拒否の別経路迂回は採られておらず、理事長令の負テスト三件は本件で一応閉じる。

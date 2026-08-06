# 述語② 上流側 (present判定) — target 4a0e9036 断面 (足軽4号)

★本file は karo-second 指示 (msg_20260807_024231_6a1971a2・測時2026-08-07T02:40:56)
に基づく★器の移し替えのみ★——中身は 02:30 台に測定・02:31:10 頃 karo-second へ
報告した内容を出所の .txt から再現したもの。内容の変更・再測定は行っていない★。

測時(本file執筆)=2026-08-07T02:48:23+09:00・出所測定の測時=2026-08-07T02:30:32(script実行・下記出所file mtime実測)

## §0 出所 (一次証跡)

- 実行環境 = /tmp/resimg-verify4-cycle2-matrix2-20260807 (己で立てた別木・base_commit=4a0e9036ed94022d79baa4a1e2cf88d5827eec12・a1の木は不触)
- script = `backend/tests/verify_predicate2_upstream_a4_ephemeral.py` (uncommitted・commit 0)
- 出力file = `/tmp/resimg-verify4-predicate2-upstream-20260807.txt`
  (sha256=b9267af8c244f50b2edfb280916b43016f03bb942cd7a4352ace1d6c83aad415・mtime=2026-08-07T02:30:32+09:00)

## §1 母集団の定義 (先に固定)

- `appointments.status` の全域 = `backend/db/migrations/appointment_tables.py:89` の
  CHECK制約 = `tentative/confirmed/arrived/in_progress/billing/completed/
  cancelled/no_show/late` の9値。
- terminal (本コードベース自身の語彙) = `appointment_lifecycle.py:172` の
  エラー文言 `"inactive appointment"` と一致する2値のみ = `('cancelled', 'no_show')`。
  之は `deactivate_appointment()` の target_status 制約 (line 57-58) とも一致する
  ＝本コードベースが「非active」と扱う値の自己定義。
- 残り7値 (`tentative/confirmed/arrived/in_progress/billing/completed/late`) は
  non-terminal として陽性対照に用いる。★`completed` は視覚上"終わった"印象を
  与えるが、コード上どこにも move 拒否の根拠が無い＝non-terminal側に置いた。
  之は射程外にしたのではなく実測結果そのもの★ (下記§2で悉皆表として明示)。

## §2 対象コード

`backend/services/appointment_lifecycle.py:140` (`move_appointment_slot`) が、
terminal status からの slot mutation を一律に拒む節を持つか否かを、code直読では
なく実際に `move_appointment_slot` を DB 上で動かして判じた (動的反例)。

## §3 実測 (悉皆9値表・出所 .txt 全文)

```
=== predicate2-upstream / target=4a0e9036 / move_appointment_slot direct call ===
status       terminal?  raised                                        mutated
tentative    False      -                                             True
confirmed    False      -                                             True
arrived      False      -                                             True
in_progress  False      -                                             True
billing      False      -                                             True
completed    False      -                                             True
cancelled    True       cannot move slot for inactive appointmen...   False
no_show      True       cannot move slot for inactive appointmen...   False
late         False      -                                             True

terminal population n=2 all_rejected=True
non-terminal population n=7 all_mutated(positive control)=True
VERDICT predicate2-upstream-present = True
```

## §4 判定

**target 4a0e9036ed94022d79baa4a1e2cf88d5827eec12 の断面における述語②上流側 = 成立
(present)**。

- terminal population (n=2: cancelled/no_show) = 全件 reject (raise・mutation無し)。
- non-terminal population (n=7) = 全件 mutation 成功 (**陽性対照** — 検出手法自体が
  「常に拒否」の偽陽性を出していない事の確認)。

## §5 射程の明記 (未測を混同しない)

本部長殿令 (00:46:20逐語) の前段「共通move/reassign domain command自身がterminal
statusからのslot mutationを一律拒否」は本票で present と判じた。

★而して令の後段「全入口は同commandのtyped resultを同じ契約でmapする」は
**本票では測っていない**。当職己で射程を限り、presentの一部として混同しない★
——本票のpresent判定は前段のみに掛かる。後段(typed result mapping)の実測は
新final target (ae1d2a9932ace06693a02b81e20a15284858826b・足軽1号 37107e85 にて
typed result 一律 mapping 実装済) での再走票
(`docs/incident_logs/2026-08-07_predicate2_upstream_final_target_rerun_a4.md`
相当・worktree `/tmp/resimg-verify4-final-target-20260807` 側成果物) にて別途扱う。

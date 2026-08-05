# 2026-08-05 止血命令 (msg_20260805_121348_364ebac2) 遵守 —「測る手が在るか」の検証 (足軽2号)

**下命元**: 家老second→足軽2号 msg_20260805_124007_01492ebd (12:40:07・将軍second 令「本日の表 八行目」)
**問い**: 12:13:48 の止血命令 (sandbox化まで実inbox pathへ届き得るbats実行を止めよ) を、配った8名が★従うたか★を、痕跡で測る手が在るか。
**性質**: 実装・patch なし。★読取専用の法医学★。bats は一切実行せず (己も止血命令の対象ゆえ)。

---

## 1. 母集団 — 8名の導出 (推し量らず・実測)

`/usr/bin/grep -rl "止血命令" queue/inbox/` で本文が存在する箱を悉皆列挙:
`ashigaru1〜7 / gunshi-second / shogun-second / karo-second` (計10箱)。

このうち **shogun-second は令の出所 (将軍second令)**・**karo-second は起草者本人** であり、
本文にも「当職も母集団に入り申す」と別枠で自己申告している (=起草者は8名の外)。
∴ **8名 = ashigaru1〜7 (7) + gunshi-second (1)**。

★但し書き★: inbox_write の送達記録に「宛先一覧」フィールドが無く、本文出現箇所からの逆算に依る。
一意の配布リストが別途在れば、それが正本である (本工区は見付けられなんだ)。

---

## 2. 検討した測り手 三種

### ⒜ 受領/既読

既に判る (各箱の `read:` フラグ)。但し下命にある通り**「読んだ」の証にしかならぬ**— 追加測定せず。

### ⒝ 痕跡 (trace) — 三系統を実測

**既知の汚染型 (2種) を先に固定** — 止血命令本文および直前の leg C 是正過程 (msg_20260805_110248) で
既に名指しされた実害の型:

| 型 | 場所 | 署名 |
|---|---|---|
| ① | `queue/inbox/karo.yaml` の `delivery_failed` | `from: inbox_write` / `宛先不明: test_agent` |
| ② | `queue/inbox/honda.yaml` / `sanada.yaml` の新規発生 | SMFC-C2/C4 が実演した「返送が箱を新規作成してしまう」実害 |

**確認**: 3対象 bats (`test_shadow_mailbox_failclosed.bats` / `test_inbox_expiry_supersession.bats` /
`agent_selfwatch.bats`) のソースを読取専用で確認 — 非canon target名は **悉く `test_agent` の一種のみ**
(他の名は用いられておらぬ)。∴ ①②の二署名で、既知の汚染経路を網羅している。

**実測結果**:

```
$ /usr/bin/grep -c "宛先不明: test_agent" queue/inbox/karo.yaml
4
$ 該当4件のtimestamp: 10:55:05 / 11:06:34 / 11:15:00 / 11:16:47  ← 悉く 止血命令 (12:13:48) より前
$ stat karo.yaml → mtime = 2026-08-05T11:16:47 (現在 12:46 時点まで ★不変★)
$ ls queue/inbox/honda.yaml queue/inbox/sanada.yaml → 両者 ★不在★ (作られてすら居らぬ)
$ find queue/inbox -maxdepth 1 -name '*.yaml' -newer(mtime 12:13:48以降) → 既存canon箱への通常書込のみ・新規の非canon箱 ★0件★
```

∴ **①②いずれの既知署名も、11:16:47〜現在 (12:46・約90分) の間、新規発生 ★0件★**。
この窓は 12:13:48 の止血命令の ★前後を跨いでいる★ ため、「命令が効いたから静かになった」のか
「命令の前から既に静かだった」のかを ★この署名だけでは 分けられぬ★ — 但し、いずれにせよ
「命令後に新たに汚した者」は ★この二署名では 見付からなんだ★。

**負の対照 (陽性対照の逆) — `_unroutable` は増えたが 中身は無関係と確認**:

```
$ find queue/dead_letter/_unroutable -newer(12:13:48以降) → 3件 (12:26:41 / 12:26:47 / 12:31:42)
```

3件とも内容を実読 — `from: third_pc / target: honbucho / reason: unroutable_target_and_unresolvable_from`、
本文は「委員長→本部長」の予約・画像事業部関連の実運用便。**bats署名 (from=inbox_write, target=test_agent)
と一致せず** ∴ **件数の増加だけを見て「汚染が増えた」と読むのは誤り** — 中身を検めねば同種判定はできぬ
(本日の規律「似た物を並べる時は何を以て同種と見たかを書け」がそのまま当てはまる)。

**副次的異常 (本問いへの直接証拠ではないが記録) — 追記: 出所判明**:
`_unroutable` 内の3ファイル (`unroutable_20260805_114016…` 等、ファイル名の埋込時刻は 11:40:16 /
11:58:03 / 12:09:28 — 悉く止血命令より前) の **mtime だけが 12:37:0x に書き換わっている**
(ctime も同一 → 中身ごと書き直された)。中身は同じく third_pc→honbucho の実運用便で bats署名とは無関係。

★出所 (追記・家老second msg_20260805_134235_67ce3134 経由)★= **家老second の下命による足軽5号の
12:36-12:37 閉じ記録追記 (closed_at/closed_reason/closed_by/evidence 四key)**。
出所典拠= 足軽5号 msg_20260805_133856_603750f4 (家老second宛 status_update 13:38:56)。
★★但し書き (略さぬ)★★= ★これは 足軽5号の自己申告であり、家老second 自身は mtime 実測での
突合を ★未検★★ と明言している。∴ 本節の出所は「足軽5号 自己申告・家老second 未突合」であって
当職 (足軽2号) も独立追認はしておらぬ。
本件は本日の条の実例= 「墓場の mtime が動くは侵入に非ず・観測者が触れた跡」——
母集団を作る時、まず測る者自身の出力を除くべし、との教訓が付された。

### ⒞ process 履歴

**存在せぬ**。8レーンそれぞれの shell/bash 履歴は各 pane 内に留まり、本 repo には
横断的な command 実行監査ログが一切無い (`find` で `*audit*log*` `*command_log*` を repo 全体で
検めたが、bats/process 実行を記録する物は無し・inbox_watcher の log は wake-up/delivery の記録のみで
agent 側の bash 実行までは追えぬ)。∴ **⒝の間接痕跡以外に、直接「bats を打ったか」を見る手は無い**。

---

## 3. 結論 — 測れるか

**測れる**のは狭い問いのみ = 「★既知の2署名 (test_agent delivery_failed / honda・sanada 箱新生) が
新規に出ておらぬか★」。答=出ておらぬ (11:16:47〜現在)。

**測れぬ**のは広い問い = 「★8名 悉くが 実 inbox path へ届く bats を 止めたか★」。理由 三点:

1. **盲点が構造的に在る** — もし bats が (test_agent ではなく) たまたま canon 名 (ashigaru1 等) へ
   ヒットする形で走れば、正常配送と見分けが付かず ★痕跡が一切残らぬ★。
2. **process 履歴という測り手が 存在せぬ** (⒞)。
3. **既知署名の不在は「観測された範囲で汚染が無い」の証にしかならず、「実行しなかった」の証にはならぬ**
   (走らせたが偶然 canon 名にヒットした場合と、そもそも走らせなんだ場合を、この手では ★分別できぬ★)。

∴ ★★『測れぬ』と 判る事★★ を 本工区の成果として出す。当職の現況 (karo-second の12:40便・
「20分新規なし」) より ★広い窓 (90分)・かつ 二署名を精査した分★、確度は上がったが、
★測れる範囲の性質は 変わっておらぬ★ (同じ弱さを継承している)。

---

## 4. 対工区 (この工区と対に成る他工区)

無し (探した範囲= 本日の queue/inbox/*.yaml・queue/dead_letter/_unroutable/*・docs/incident_logs/2026-08-05*
の一覧・task YAML 各エージェント分)。★近縁★= leg C/B の fail-closed 是正 (subtask_shadow_failclosed_legB/C)
は本問いの発端そのものであり工区としては別だが主題が直結する。

## 5. 本工区で己が直した誤り

無し (実装なし・読取専用の測定のみ)。

## 6. 壊れる試験の件数

0件 (bats を一切実行せず・既存 file も一切書き換えず)。

## 7. 監査体制

二者制 (Codex leg は SAFETY 裁定 seq132707 で停止中)。本工区は監査提出前の一次報告。

## 8. 禁則遵守の申告

影 file (queue/inbox/ashigaru-second-*.yaml) 不触。dd189 不触。process 不触。commit/push/stage 未実施。
scope 拡大なし (指示された測定のみ)。bats 実行なし。

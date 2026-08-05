# 監査票git外是正案・当てられる形まで (足軽6号、2026-08-06・家老second下命【甲】)

★★.gitignoreは未適用(委員長殿裁可待ち・下命⒠遵守)。隔離clone(scratchpad配下・実repoの外)でのみ
検証、実repoは一切不触。commit不触(軍師PASS後)。★★

測時=2026-08-06T02:29:30+0900(date -Iseconds実行結果)。HEAD=f3501fd322ae0bab6ed2e06b99c581ae1b720104
(git rev-parse HEAD実行結果)。

## ⒜ 現況再測 (HEAD+秒つき・命令+出力そのまま)

$ git status --porcelain --ignored=matching queue/ | awk '{print $2}' | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn
   6953 queue/reports
    108 queue/inbox
     25 queue/metrics
     16 queue/tasks
     16 queue/orders
     13 queue/dead_letter
      5 queue/watchers
    (+queue/pane_registry.yaml関連bakfile 3件・queue/packets 1件・queue/archive 1件・queue/.slim_yaml.lock 1件)

$ find queue/reports -type f | wc -l
6953
$ find queue/reports -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
   3093 sha256
   3071 json
    680 md
     29 yaml
     25 log
     23 patch
     14 sh
      6 txt
      6 diff
      3 patched_reference

$ ls queue/reports/gunshi_second_*.md | wc -l
267

**∴ 前回(2026-08-06T00:34時点)の252件から★267件へ増加★(前回測定から約2時間で15件増)。
かつ★queue/reports全体は680 .md + 3093 .sha256 + 3071 .json 等 計6953fileがgit外★——
前回報告は.mdのみを見ており、.sha256/.jsonという★監査の裏付け証跡そのもの★がさらに
巨大な規模でgit外である事を、本測定で新たに把握した(母集団拡大の自己申告)。**

## ⒝ 各案の当てる文字列 (逐語・隔離clone検証済)

**★案1のみ`.gitignore`への追加行を要する。案2・案3は`.gitignore`変更を伴わない
(これが両案の要点=新たな否定規則を増やさない事)★**

### 案1: `.gitignore`への追加行 (二つの粒度を用意・隔離clone双方で実測)

- **狭い形(gunshi-second監査票のみ)**: `!queue/reports/gunshi_second_*.md`
- **広い形(queue/reports/全.md)**: `!queue/reports/*.md`

(証跡=.sha256/.jsonまで救うなら、さらに`!queue/reports/*.sha256`・`!queue/reports/*.json`
等の追加行が要る——本工区では.mdのみを対象とし、証跡fileの救済は別途要相談として明記する)

### 案2: `docs/incident_logs/`(既存の`!docs/incident_logs/*.md`で救済済dir)へ移設

`.gitignore`変更不要。運用変更(監査票の書込先を変える)のみ。

### 案3: 台帳型の要旨集約(既存`docs/incident_logs/2026-08-04_SECONDPC_BACKLOG.md`と同型)

`.gitignore`変更不要。新規ledger file作成+運用変更のみ。

## ⒞ 各案の副作用 (隔離clone差分法で実測・実repoは不触)

**手法**=`/tmp/.../scratchpad/isolated_clone_a6`へ`git clone --no-hardlinks`し、queue/reports配下に
実物同型の空fileを作成(gunshi_second_test1_20260805.{md,sha256,json}・karo-second-test2-20260805.md・
some_other_report_20260805.md・queue/orders/test_order_20260805.md・queue/dead_letter/unroutable_test.yaml)、
候補行を`.gitignore`末尾へ追記して`git status --porcelain -uall --ignored=matching queue/`で実測、
検証後は元の`.gitignore`へ復元。実repoの`.gitignore`は測定前後で不変(`git status --short .gitignore`=無出力)。

**案1・狭い形(`!queue/reports/gunshi_second_*.md`)適用時**:
$ git status --porcelain -uall --ignored=matching queue/
!! queue/dead_letter/unroutable_test.yaml
!! queue/orders/test_order_20260805.md
!! queue/reports/gunshi_second_test1_20260805.json
!! queue/reports/gunshi_second_test1_20260805.sha256
!! queue/reports/karo-second-test2-20260805.md
!! queue/reports/some_other_report_20260805.md
?? queue/reports/gunshi_second_test1_20260805.md

**∴ gunshi_second接頭辞のmdのみ救済。他agent接頭辞のmd(karo-second-*等)・証跡file(.sha256/.json)は
なお不可視のまま。副作用=他dir(queue/orders,queue/dead_letter等)への波及=0件。**

**案1・広い形(`!queue/reports/*.md`)適用時**:
$ git status --porcelain -uall --ignored=matching queue/
!! queue/dead_letter/unroutable_test.yaml
!! queue/orders/test_order_20260805.md
!! queue/reports/gunshi_second_test1_20260805.json
!! queue/reports/gunshi_second_test1_20260805.sha256
?? queue/reports/gunshi_second_test1_20260805.md
?? queue/reports/karo-second-test2-20260805.md
?? queue/reports/some_other_report_20260805.md

**∴ queue/reports配下の全.md(680件相当)が救済される。副作用=queue/reports以外への波及=0件・
.sha256/.json等の証跡fileはなお不可視のまま(実測で確認)。**

## ⒟ この修正が新たに開ける穴

1. **証跡の分離**=案1(いずれの粒度でも).mdは救うが.sha256/.jsonは救わない。∴「監査票(md)は
   読めるが、そのmdが引用する.sha256照合fileや.json構造化データは読めない」という★新種の
   phantom canon★(参照は在るが実体無し)を作り得る。
2. **広い形の副作用**=queue/reports/には680件超の.md(gunshi_second以外の作者含む)が存在し、
   広い形を適用すると★意図せぬ二次的file(足軽/家老の個人報告等)まで一律に追跡下入りする★。
   これが望ましいか否かは委員長殿の裁定事項(当職は判断しない)。
3. **狭い形の限界**=gunshi_second以外の監査/報告(karo-second-*.md等)は救われぬまま残り、
   ★「監査票は残るが発令書・報告書は残らぬ」という非対称★が生じる。

## ⒠ 適用状況 (下命どおり不適用)

`.gitignore`は一切変更していない(実repo確認済=直前の`git status --short .gitignore`が無出力)。
隔離clone(`/tmp/.../scratchpad/isolated_clone_a6`)は検証専用・実repoから完全に隔離。

## 【本工区で己が直した誤り】

隔離clone作成直後、`git status --porcelain --ignored=matching`(`-uall`無し)を実行した所
「?? queue/reports/」(dirごと1行)としか出ず個別file名が見えなかった。★出力の形だけを見て
「1fileのみ救済された」と早合点しかけたが、`-uall`を付けて再実行し直し、実際にどのfileが
救済されたかを個別に確認し直した(本日確立の教訓「道具の出力は道具の判定に非ず」の実演)。

## ★母集団漏れの自己申告★

1. queue/reports以外のignoredファイル(queue/inbox 108件・queue/metrics 25件・queue/tasks 16件・
   queue/orders 16件・queue/dead_letter 13件・queue/watchers 5件、計183件)は本工区の対象外
   (下命が「監査票」に限定されているため)。これらも同様の問題を抱えている可能性がある。
2. 隔離cloneの削除(`rm -rf`)がこのsessionの権限設定で拒否され、scratchpad配下に残存している
   (`/tmp/claude-1000/.../scratchpad/isolated_clone_a6`)。実repoとは完全に無関係・機密無し・
   session終了時に自然消滅する見込みだが、明示的な削除はできなかった事を開示する。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、【甲】監査票git外是正案・当てられる形までへの応答。適用は行っていない。

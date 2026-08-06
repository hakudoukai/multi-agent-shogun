# 退避台帳(_prune_events.log)×実体(_archive/**)突合（足軽6号）

下命=家老second msg_20260806_205743_d28ea3d6（2026-08-06T20:57:43）。読取のみ。
禁＝書くな・消すな・`read`を立てるな／lane(worktree)不触＝freeze継続／`queue/inbox/_dead_letter_second.yaml`は読まず（`grep`/`wc`/`cat`不使用、本票では触れていない）。

測時=2026-08-06T21:03:04+09:00（`date -Iseconds`実行結果、本票の最終再測）。
git rev-parse HEAD=17a7c26ecef363cfb866773187dc73e8bcb280bc。

## 母集団（測時・器・範囲）

```
$ ls queue/inbox/_archive/ | wc -l
17   （README.md・_prune_events.log を含む全17件）
$ ls queue/inbox/_archive/ | grep -v -E "^(README.md|_prune_events.log)$" | wc -l
15   （データfile、以下「実体」の母集団）
$ wc -l queue/inbox/_archive/_prune_events.log
301  （台帳の行数＝記録事象数）
```
測時=2026-08-06T21:00〜21:03の間／器=`ls`+`wc -l`／範囲=`queue/inbox/_archive/`直下（サブディレクトリ無し、実測確認済）。

`_prune_events.log`の書式（README記載外・当職が実測で確認）＝
`<ISO刻> agent=<名> pruned=<数> archive=<絶対path>` の1行1事象。

## ⒜ file水準の突合（README警告通り`safe_load_all`使用）

実体15件のbasenameと、台帳301行から`archive=`のbasenameを抽出した集合を`comm`で突合。

```
実体file一覧（15件）＝
_test_cap_rotation_pruned.yaml, ashigaru1_pruned.yaml, ashigaru2_pruned.yaml, ashigaru3_pruned.yaml,
ashigaru4_pruned.yaml, ashigaru5_pruned.yaml, ashigaru6_pruned.yaml, ashigaru7_pruned.yaml,
fukuincho_legacy_deadletter_20260702_131339.yaml, gunshi-second_pruned.yaml,
gunshi_legacy_generic_20260702_141415.yaml, honbucho_pruned.yaml, karo-second_pruned.yaml,
shogun-second_pruned.yaml, shogun_legacy_generic_20260702_135247.yaml

台帳が参照するbasename一覧（11件）＝
ashigaru1_pruned.yaml, ashigaru2_pruned.yaml, ashigaru3_pruned.yaml, ashigaru4_pruned.yaml,
ashigaru5_pruned.yaml, ashigaru6_pruned.yaml, ashigaru7_pruned.yaml, gunshi-second_pruned.yaml,
honbucho_pruned.yaml, karo-second_pruned.yaml, shogun-second_pruned.yaml
```

## ⒝ 二方向の数（別々に数えた・向きで意味が違う）

**方向①＝台帳に在るが実体無し（`archive=`が指す実fileが存在せぬ）**＝
測時=2026-08-06T21:03:04+09:00／器=`comm -23`（台帳basename集合 − 実体file集合）／範囲=上記母集団。
```
0件
```

**方向②＝実体在るが台帳に無し（★危うき方★）**＝
測時=2026-08-06T21:03:04+09:00／器=`comm -23`（実体file集合 − 台帳basename集合）／範囲=上記母集団。
```
4件（file水準）＝
  _test_cap_rotation_pruned.yaml
  fukuincho_legacy_deadletter_20260702_131339.yaml
  gunshi_legacy_generic_20260702_141415.yaml
  shogun_legacy_generic_20260702_135247.yaml
```

## 深掘り＝file水準だけでは足りぬ（文書(doc)水準の再突合）

台帳の1行=1archive事象ゆえ、「台帳に載っているfile」であっても★file内の個々の退避事象（multi-document YAMLの1 doc）が悉く台帳と対応するか★は別問題と判じ、
台帳11fileの`archive=`行が持つ刻（ISO timestamp）と、対応fileの各docの`pruned_at`フィールドを１対１で突合（`safe_load_all`使用、README指示通り）。

```
$ python3で全11fileの doc数 と 該当file宛の台帳行数 を突合（pruned_at刻の集合差分）
ashigaru1_pruned.yaml: docs=14 log_events=14 doc_without_log=0 log_without_doc=0
ashigaru2_pruned.yaml: docs=11 log_events=11 doc_without_log=0 log_without_doc=0
ashigaru3_pruned.yaml: docs=11 log_events=11 doc_without_log=0 log_without_doc=0
ashigaru4_pruned.yaml: docs=11 log_events=11 doc_without_log=0 log_without_doc=0
ashigaru5_pruned.yaml: docs=9  log_events=9  doc_without_log=0 log_without_doc=0
ashigaru6_pruned.yaml: docs=11 log_events=11 doc_without_log=0 log_without_doc=0
ashigaru7_pruned.yaml: docs=7  log_events=7  doc_without_log=0 log_without_doc=0
gunshi-second_pruned.yaml: docs=29 log_events=29 doc_without_log=0 log_without_doc=0
honbucho_pruned.yaml: docs=4  log_events=4  doc_without_log=0 log_without_doc=0
karo-second_pruned.yaml: docs=139 log_events=136 doc_without_log=3 log_without_doc=0  ★不一致★
shogun-second_pruned.yaml: docs=58 log_events=58 doc_without_log=0 log_without_doc=0
```

★台帳「載っている」11file中10fileは doc数＝台帳行数で完全一致（刻単位でも突合、ずれ無し）。
karo-second_pruned.yaml のみ★doc=139 に対し台帳=136行★＝★方向②（実体在るが台帳に無し）が3件、file内部に潜伏★。
該当3docの`pruned_at`・`count`（メッセージ数）を実測：
```
2026-08-03T22:50:00  count=22
2026-08-03T22:58:09  count=7
2026-08-03T23:02:36  count=18
```
（合計47通、この3件のみ台帳に対応行が無い。台帳側に対応docの無い行＝0件、上記表の通り）

## 方向②の総計（file水準4件＋doc水準3件）とメッセージ数

file水準4件の内包メッセージ数を`safe_load_all`で実測：
```
_test_cap_rotation_pruned.yaml: doc=1 messages=21
fukuincho_legacy_deadletter_20260702_131339.yaml: doc=1 messages=25993
gunshi_legacy_generic_20260702_141415.yaml: doc=1 messages=31
shogun_legacy_generic_20260702_135247.yaml: doc=1 messages=810
```
★方向②の総計＝★事象7件（file4＋doc3）・メッセージ26,902通（26,855＋47）が、台帳に一切対応記録を持たぬ★。
うち fukuincho_legacy_deadletter_20260702_131339.yaml 単独で 25,993通と★桁が違う★（他6件合計909通の約28倍）。

## ⒞ 危うき方（方向②）の性質＝時系列で見た事実

方向②に該当する7件全ての刻を実測：
```
台帳の最古行＝2026-08-04T11:14:41（実測、head -1）
方向②file水準4件のmtime＝2026-07-01, 2026-07-01, 2026-07-02, 2026-08-03（悉く台帳最古行より前）
方向②doc水準3件のpruned_at＝2026-08-03T22:50:00/22:58:09/23:02:36（悉く台帳最古行より約12時間前）
```
★事実として記す（結論とはしない）★＝方向②に該当する7件は★悉く台帳の記録開始刻より前★であり、
台帳の記録開始刻（2026-08-04T11:14:41）★以降★の期間内では、方向②該当0件（上記doc水準表で10/11file完全一致、karo-secondも2026-08-04以降の136件は全て台帳と一致）。
これが「台帳導入前の旧経路の残骸ゆえ実害無し」を意味するか、「台帳導入後も同型の漏れが起こり得る設計上の欠陥」を意味するかは、
当職の手元情報（台帳を書き込む機構のソース未確認）からは★判定不能★。断定を避ける。

## ⒟ 用いた器（README指示順守）

`yaml.safe_load()`ではなく`yaml.safe_load_all()`を全fileに使用（README警告「safe_loadでは読め申さぬ」に従う）。
`None`要素（末尾の空doc）は`if d is not None`で除外。

## ⒠ 己の手で為した事

- `ls -la queue/inbox/_archive/` で母集団17件を実測
- `ls queue/inbox/_archive/ | grep -v -E "..."` で実体15件のbasename一覧を抽出
- `wc -l queue/inbox/_archive/_prune_events.log` で行数301を実測
- `head -1`/`tail -1`で台帳の最古・最新行を実測
- `/usr/bin/grep -oE "archive=[^ ]+"` で台帳から`archive=`path一覧を抽出、`basename`+`sort -u`で11件に正規化
- `comm -23`を両方向（実体−台帳、台帳−実体）に実行し方向①②を分離集計
- `stat -c`で方向②該当4fileのmtime・size・permを実測
- `git status --short queue/inbox/_archive/`を実行（追跡外・出力無し、通常のqueue/gitignore範囲と符合）
- `python3`+`yaml.safe_load_all()`で台帳「載っている」11file全てを開き、doc数・pruned_at集合を実測、台帳の該当file宛行数・timestamp集合と突合（`comm`ではなくPython集合差分で実施、10/11一致・karo-secondのみ3件不一致を検出）
- karo-second_pruned.yamlの不一致3docの`pruned_at`・`count`フィールドを実測
- 方向②該当4fileの内包`messages`件数を`safe_load_all`で実測（合計26,855通）
- `queue/inbox/_dead_letter_second.yaml`には一切触れていない（本票の対象範囲外、`_archive/`配下のみを扱った）
- 実行の刻に台帳行数・doc数を数え直し、当初想定（file水準のみの突合）を超えてdoc水準まで掘り下げた（令の⒜「全file×記録を突き合わせよ」の文言を、file存否だけでなく事象単位の対応まで含むと当職が解釈・拡張した旨、明記する）

## 数の扱い

令に個数の明示は無し（「突き合わせよ」「数えよ」）。
測時=2026-08-06T21:03:04+09:00／器=`comm`+`python3 yaml.safe_load_all`／範囲=`queue/inbox/_archive/`データ15file＋`_prune_events.log`301行。
方向①（台帳に在るが実体無し）＝0件。方向②（実体在るが台帳に無し）＝7件（file4・doc3）・メッセージ26,902通。
以上（読めぬfileは無かった。`_dead_letter_second.yaml`は範囲外につき対象外）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

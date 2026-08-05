# 【00E門】追補4 — 三file実体化(未結線)+ .gitignore「!」起案(足軽1号)

- **下命**: karo-second msg_20260805_211654_03b5d589(実装の裁定・条件付きで先行を許す)。
- **性質**: ★実体は新設・稼働には不参加★。許されたのは「新規fileの作成のみ(三file)」であり、
  既存scriptへの結線・`.gitignore` そのものの編集・負テスト①〜④の実測はいずれも★着手せず★(下命どおり)。
- **境**: read-only(repo内file改変は本書+新設三fileの計4点のみ)・`.gitignore` 不触(起案まで)・bats禁・
  commitはkaro-second(軍師second PASS後)。★完了は軍師second PASS後★。★提出は軍師second へ直★
  (家老への完了報は提出に非ず、下命五)。

---

## §0 断面(測定時刻をその場に貼る・条⑶)

```
$ date -Iseconds
2026-08-05T21:24:57+09:00

$ git rev-parse --short HEAD
de52257

$ git branch --show-current
feat/dd169-d006-conditional-exception

$ ls scripts/lib/
00e_gate_thresholds.sh  detect_stale.sh  ignored_active_predicate.sh  inbox_path.sh
```

本書中のcommand出力は、上記時間帯に当職が実行したそのままである(手で書き写していない・条⑾)。

---

## §1 下命五点への対応表

karo-second便(msg_20260805_211654_03b5d589)の条件四つ+区分(①着手可/②着手不可/③条件=着手命に非ず)を、
本書がどう満たしたかを先に一覧する。

| # | 下命の求め | 本書の対応 |
|---|---|---|
| 条件① | 通路(`.gitignore` の `!` 案)を★同じ便で★起案せよ | §4(本書自身がその便) |
| 条件② | 新規fileの冒頭に★「未結線・稼働に影響せず」★を明記 | 三file冒頭コメント(§3で実測付きで確認) |
| 条件③ | commitは★軍師secondのPASS後★ | §7完了の定義に明記(当職はcommit権限外) |
| 条件④ | 結線の起案は★別便★とし、理事長殿の御判断が下るまで着手せぬ | 本書は結線を提案せず(§3で0件を実測確認) |
| ①理由訂正 | `.gitignore`起案の理由=「共有されず・監査されぬ」(checkout一発で消える、ではない) | §4に訂正版理由を反映 |
| 着手可 | 設計の続き/新規三fileの作成/`.gitignore`の`!`案の起案(同じ便) | §3・§4 |
| 着手不可 | 既存scriptへの結線/負テスト①〜④の実測/`.gitignore`そのものの編集 | §3で0件実測・§6で未実測を明記・§0のgit statusで`.gitignore`差分0を実測 |

---

## §2 着手前の既存資産探索(二重実装の禁)

**探した範囲**: 追補2・追補3(いずれも軍師second PASS済・commit b13dc31/f362fb6/de52257)の全設計。
三fileの中身は★新規発明ではなく、既にPASS済の設計書の転記・実体化である★事を確認した
(追補2 §6-1の閾値案・追補2 §4の解除の道・追補3 §3〜§7の鳴らし方設計)。

**見付からなんだ事**: `scripts/lib/` 配下・`docs/` 直下いずれにも、本三fileと同名・同責務のfileは
既存2本(`detect_stale.sh`・`inbox_path.sh`)と重複せず(`ls scripts/lib/` §0参照)。∴ 二重実装に当たらぬ。

---

## §3 三fileの実体化(未結線の実測付き確認)

| file | 行数 | sha256 | 冒頭「未結線」明記 | check-ignore | 既存scriptからの参照 |
|---|---|---|---|---|---|
| `scripts/lib/ignored_active_predicate.sh` | 93 | `3da86f02a90d56dc4c06c987ee767d27c9b81c2dfb5d78a2df10a9606df97fda` | ★済★(冒頭コメント) | exit=0(ignored・下記§4対象) | 0件 |
| `scripts/lib/00e_gate_thresholds.sh` | 81 | `8030985adc9ddb578ec1179bac4fe7300d65d137c1aa5bb509d8819b7af6a9d8` | ★済★(冒頭コメント) | exit=0(ignored・下記§4対象) | 0件 |
| `docs/00e_gate_release_ledger.md` | 56 | `00769833d526642335f6f033cf1818f898632cc5e0c5936f56f6c5568fae9db6` | ★済★(冒頭段落) | exit=0(ignored・下記§4対象) | 0件 |

**「既存scriptからの参照0件」の実測方法**:

```
$ git grep -l "source.*ignored_active_predicate\|source.*00e_gate_thresholds\|00e_gate_release_ledger" -- '*.sh' '*.py'
(0 hits — git-tracked file中に参照なし)
```

`git grep` は追跡済(=ignoreされておらぬ)fileのみを対象とするため、この0件は
「稼働中のいかなる既存scriptもこの三fileへ結線しておらぬ」事の直接証拠である。

**内容の要旨**(中身は追補2・追補3で既にPASS済の設計をそのまま実体化。新規判断は加えておらぬ):
- `ignored_active_predicate.sh`: `is_ignored_and_active()`。信号A(canon参照)/B(cron・systemd)/C(source/invoke)/D(mtime)を
  本体§4定義どおりに実装し、`ACTIVE = A OR B OR C`・`D`単独=`STALE`の判定式を返す(戻り値は常に0・判定は標準出力)。
- `00e_gate_thresholds.sh`: 追補2 §6-1の閾値3変数(`MTIME_STALE_DAYS`・`PATROL_INTERVAL_MIN`・
  `AMBIGUOUS_BOUNDARY_LEANS_TO`)+追補3 §3の`_00e_load_threshold`/`_00e_announce_override`
  (ledger先書き→uplink後送の順序・失敗時非0)。
- `00e_gate_release_ledger.md`: 追補2 §4-2(REQUEST/APPROVED/DENIED)+追補3 §4-1・§5-2
  (OVERRIDE/ACK_BY_APPROVER)の行型定義+空の台帳本体(0行)。

**当職が行った検証(negative test①〜④の実測ではない・自己申告)**: `bash -n` による構文検査のみ
(2ファイルとも「syntax OK」)。★これは実行(execution)ではなく構文解析(parse)に留まる★ため、
下命「負テスト①〜④の実測には着手せぬ」に抵触せぬと当職は判断した。実際にoverrideを発生させる・
ledgerへ実際に書き込む・uplinkを実際に呼ぶ、のいずれも行っておらぬ(§6で未実測と明記)。

---

## §4 `.gitignore` の「!」起案(★起案のみ・未適用★)

### §4-1 起案diff

```diff
--- a/.gitignore
+++ b/.gitignore
@@ scripts/lib/ セクション内(既存 !scripts/lib/detect_stale.sh の並びに追記)
+!scripts/lib/ignored_active_predicate.sh
+!scripts/lib/00e_gate_thresholds.sh
@@ docs/ セクション内(既存 !docs/philosophy.md 等の並びに追記)
+!docs/00e_gate_release_ledger.md
```

### §4-1-b 個別file方式を選んだ理由(wildcard方式との比較・線引きは当職の裁)

karo-second便(msg_20260805_212309_e95af37b)の指摘どおり、`scripts/lib/*.sh`のようなwildcard方式も
既存(`scripts/checks/*.sh`・`scripts/redundancy/*.sh`・`scripts/watchdogs/*.sh`)に前例があり、
射程の広さが個別file方式とは異なる(wildcardは将来置かれる未レビューのfileまで自動的に許可する)。

当職は★個別file方式★を選ぶ。理由=本体§6が「一括whitelistは具申しない(下命四⑤に倣う)」と
明記した通り、00E門シリーズ全体が一貫して「レビュー済の物だけを名指しで許可し、未検分の物を
まとめて通さぬ」線を引いてきた(§3-3の新規発見14件を即時候補に含めなかったのと同型判断)。
`scripts/lib/`は述語・閾値という★門の根幹ロジックの置き場★であり、将来ここへ無審査で
file が増えた場合に自動的にwhitelistされる事こそ、本00E門が咎めてきた「気付かれぬ拡大」を
自ら再生産しかねぬ。∴ 本追補では個別file方式(§4-1の三行)を採る。

### §4-2 理由(★訂正版★・karo-second便 msg_20260805_211654_03b5d589 三の指示による)

karo-secondが将軍second実測に基づき訂正した通り、正しい理由は以下である(当職もこの理由を用いる):

- ★誤り(用いない)★: 「未追跡のまま置けばcheckout一発で消える」——機序が違う。
  未追跡(`??`)fileはgit checkoutでは消えぬ(gitは未追跡fileに触れぬ。消すのは`git clean -fdx`=当repo禁)。
- ★正しい理由★: **ignoreされたfileはgitに見えず、共有されず、監査されぬ**。
  現に本三fileは`git check-ignore -q`でexit=0(§3表)——他agentの`git pull`・`git log`・
  軍師secondの`git diff`監査いずれにも現れぬ。追補2・追補3の設計内容(ledger様式・閾値・
  override鳴らし方)がrepo内に実在するように見えて、実は★誰の目にも触れぬ物★になっている状態であり、
  これは本00E門シリーズ全体が咎めてきた「沈黙の病」そのものが三fileの実体化と同時に発生している事を意味する。

**∴ この起案は既存6件の00E既知件・§3-3の20件と同一の病理に対する処置であり、新しい判断ではない
(既存設計の延長・二重実装に非ず)。**

### §4-3 実測(§0時点で`.gitignore`差分0を確認・不触の証)

```
$ git status --short .gitignore
(出力なし = 差分0)
```

**★本起案は`.gitignore`の適用を含まぬ。適用は委員長殿の裁可後★**(下命どおり)。

---

## §5 新様式 — この実装が受けた裁定を満たし得ない点(委員長殿制定様式・下命三)

1. **三fileは「未結線」だが、完全に無害とは言い切れぬ**。`00e_gate_thresholds.sh`を
   誰かが手動で`source`し`_00e_announce_override`を直接呼べば、`karo_second_send_iincho.sh --live`が
   即座に発火する(§3参照・冒頭コメントで警告は明記したが、コメントは技術的強制ではない)。
   「未結線」は「呼び出し経路が存在せぬ」事の保証であり、「呼べば効かぬ」事の保証ではない。
2. **`bash -n`のみの検証であり、実行時の正しさは未確認**。構文が正しい事と、実際に正しい値・
   正しい判定を返す事は別である(§3で実行はしておらぬと明記した通り)。
3. **負テスト①〜⑤(追補3 §10)はいずれも未実測のまま**。下命によりこの状態を維持する事自体が
   本書の求められた挙動だが、「未実測」は「効く」の主張ではない事を改めて明記する。
4. **`.gitignore`起案(§4)の対象は本三fileに限る**。本体§6-2「所有者裁定待ち」5件・
   §3-3新規発見14件は本追補の射程外のまま(下命四⑤=一括whitelistを具申せず、を踏襲)。

空欄にはしない(下命三「空欄は不可」に従う)。

---

## §6 条⑿自己適用 — 己ならこの三fileをどう骨抜きにするか(最低3点・実体化により追加分)

**① 冒頭コメントの警告を読まずに`source`する**
→ 緩和: コメントは技術的強制ではなく運用規約に留まる(追補3 §9①と同型の限界)。
   技術的強制(例: 関数名を意図的に呼びにくくする・別途ラッパーで二重確認を要求する等)は
   本追補の範囲外とし、引き継ぎ事項とする。

**② `.gitignore`の`!`案(§4)だけが先にPASSされ、三fileの中身レビューが省略される**
→ 緩和: 本書は§4を§3と★同じ便★に含める事で、中身と通路を分離監査させぬ設計とした
   (下命条件①「同じ便で起案せよ」の趣旨そのもの)。

**③ 三fileを個別にcommitし、`.gitignore`起案(§4)だけ別commitへ分ける**
→ 緩和: §9完了の定義で「四点を同一commitへ含める事」を明記し、karo-secondの裁量に委ねるが、
   分割した場合は「通路だけ先に開いて中身は後」という追補2 §6-2手順3が戒めた事態の再来になる旨を
   ここで自己申告しておく。

---

## §7 引き継ぎ・所有者未定事項

- §6①(source防止の技術的強制)は本追補の範囲外。
- 結線の起案(既存巡回scriptへ`source scripts/lib/...`を追加する提案)は★別便★とし、
  理事長殿の御判断が下るまで当職からは起案せぬ(下命条件④に従う)。
- §4-1のdiff適用可否は委員長殿の裁可待ち。
- 負テスト①〜⑤(追補3 §10)の実測は、結線が許可された後の実装段階へ持ち越す。

---

## §8 今日制定の規律への自己適用(十二箇条)

⑴ **横に開く穴**: §5(満たし得ぬ点4件)・§6(条⑿追加分3点)で自ら明記した。
⑵ **零対照**: §2「既存2本(`detect_stale.sh`・`inbox_path.sh`)と重複せず」を`ls`実測で確認した。
⑶ **測時その場**: §0。
⑷ **直ったなら残数**: 該当なし(新規file作成であり既存不具合の修正ではない)。
⑸ **総量は他者に測らせよ**: 該当なし(本追補は総量申告を含まぬ)。
⑹ **誰が止めれば止まるか**: 軍師second監査(完了定義・§9) / karo-second commit保留(commit権限は当職外) /
   委員長殿裁可(§4適用・結線起案いずれも)。
⑺ **双方の名**: 対工区=本体・追補1・追補2・追補3(同一足軽1号起筆・連番)。本追補は独立した第五の便として提出。
⑻ **門なら効いた出力**: ★未装備ゆえ本追補では出せず★(結線が無いため。§3「参照0件」がその実測)。
⑼ **また開くのを止めるか**: §4の`.gitignore`起案そのものが、三fileが今後もignoreされたまま
   沈黙し続ける事態を止める処置である。
⑽ **判定不能に開く条件**: §6①(コメント無視でのsource)は技術的に判定不能であり、その旨を明記した。
⑾ **己が実行した出力**: §0・§3(git grep/check-ignore/bash -n の出力はいずれもその場で実行した物)。
⑿ **破り方を先に書け**: §6。

---

## §9 完了の定義・引き継ぎ

**本体・追補1・追補2・追補3と同一**: 本書提出 → 軍師second監査PASS → karo-second verdict →
commit(当職はcommit権限外)。commit対象は本書+新設三file(計4点)を★同一commit★とする事を提案する
(§6③で述べた分割リスクの回避)。`.gitignore`の実適用(§4)・既存scriptへの結線提案(§7)はいずれも
本追補の範囲外(前者=委員長殿裁可後、後者=理事長殿御判断後・別便)。

**提出先**: 軍師second へ直(下命五「完了は軍師second PASS後。提出は軍師second へ直
(家老への完了報は提出に非ず)」に従う)。karo-second へは work_started + ETA の報告のみを別途行った。

# `_archive/` を読める形にする案 (設計のみ・実装は待て) — 足軽7号

家老second殿下命(msg_20260805_140946_f48f07d5)への応答。lane=delivery-route-stabilization内、
足軽3号殿「出口の門」(B-119/B-133、据置中)と対。★本書は設計のみ・実装は行わず★(凍結+下命の縛り両方に従う)。

台帳file・他者成果物・影file・dd189・process、いずれも不触(Read/grepのみ)。bats実行なし(止血継続中)。
commit・push・stage一切なし。registry/inbox_write.sh/墓場fileは読むのみで手を触れず。

断面=2026-08-05T14:12:17+0900。base_commit=502cbfe(実測=HEAD一致)。

参照した正本: `scripts/inbox_write.sh`(L120-159、CAP_ROTATED実装全文Read)/
`queue/inbox/_archive/karo-second_pruned.yaml`(構造実測のみ・内容不触)/
`docs/incident_logs/2026-08-05_ledger_tier_classification_a3.md`(三段定義・出口の門の位置づけ確認用)/
`queue/inbox/ashigaru7.yaml`(下命本文)。
★原典(将軍second令 msg_20260805_133129_14905b64 §1、三段②の厳密な定義)は当職の受信箱に無く★己は検めておらぬ★——
karo-second殿の下命本文中の引用(「③を②へ引き上げる」)から推した定義を用いる。

---

## 【本工区で己が直した誤り】

初稿で「archiveのdocument数=CAP_ROTATED発生回数と同数のはず」と決め打ちかけたが、実際に`grep -c "^---$"`と
`yaml.safe_load_all()`で数えた所、karo-second殿自身の実測(72 doc)と当職の実測(71区切り=72+末尾空doc=73)が
僅かに食い違った(末尾に空documentが1件混入)。数え方(区切り文字数 vs 実parse後のdocument数)の違いによる物であり
実害ではないが、「数えてから記す」を怠らず両方の数値をそのまま併記する事とした(下記②参照)。

---

## ①事実確認(実測・陽性対照付き)

**症状の再現**: `yaml.safe_load('queue/inbox/_archive/karo-second_pruned.yaml')`実行で
`ComposerError: expected a single document in the stream / but found another document`
(line 1 / line 282)を実測確認——karo-second殿の申告と完全一致。

**陽性対照(0件ではなく「読めぬ」と書く前に、正しい手段で読める事を示す)**:
`yaml.safe_load_all()`(複数document対応API)を用いると★全73 document・974メッセージが正常に読める事を実測確認★
(エラー無し)。∴ ★データは失われておらぬ・読み方の契約が違うだけ★——karo-second殿の所見「消えたなら探すが、
在ると思うて開けねば諦める」と同型の再確認。

**根本原因(コード直読で特定)**: `scripts/inbox_write.sh:146-149`
```
with open(_apath, 'a', encoding='utf-8') as _af:
    yaml.safe_dump({'pruned_at': ..., 'count': ..., 'messages': dropped}, _af, ...)
    _af.write('---\n')
```
CAP_ROTATED発火の都度、★追記モード(`'a'`)で新documentをdumpし、末尾に`---\n`区切りを自ら書き足す★——
これは意図的に multi-document YAML stream を生成する設計(単発の書き込み事故ではない)。然れど、
この形式で書く事と、`safe_load_all`で読む事を要求する事とが、★書く側にしか記されておらず読む側の契約として
どこにも明文化されていない★——当職の探索範囲(`grep -rl safe_load_all`)では、リポジトリ全体で
`safe_load_all`を使う箇所は★皆無★。既存の読み手候補も無し(Anti-Duplication確認済=流用できる既存helperは無い)。

## ②母集団(数えてから記す・両方の数え方を併記)

`queue/inbox/_archive/*_pruned.yaml`のうち multi-document 化しているのは:

| file | `---`区切り数 | 影響 |
|---|---|---|
| karo-second_pruned.yaml | 72 | ★本件の直接契機★ |
| shogun-second_pruned.yaml | 21 | 同型 |
| gunshi-second_pruned.yaml | 12 | 同型 |
| ashigaru2_pruned.yaml / ashigaru3_pruned.yaml / ashigaru6_pruned.yaml | 各5 | 同型 |
| ashigaru1_pruned.yaml / ashigaru4_pruned.yaml / ashigaru5_pruned.yaml / ashigaru7_pruned.yaml(★当職自身★) | 各4 | 同型 |
| _test_cap_rotation_pruned.yaml | 1 | 同型(試験用) |
| legacy系3件(fukuincho/gunshi/shogun) | 0 | ★対象外・旧仕様の単発file★ |

∴ ★karo-second殿の箱だけの問題ではなく、稼働中の全agent archiveに共通する構造的欠陥★
(当職自身の`ashigaru7_pruned.yaml`も同型と確認——己の箱も母集団から外さず)。

## ③三段の当てはめ(karo-second殿の言う「③→②」の意味、推測である旨を明記)

- 現状=★③(条)★: 「archiveはsafe_load_allで読め」は★誰かの頭の中にしかない知識★(本書執筆のきっかけも
  karo-second殿がこれを忘れ、索引の一行だけを読んで誤断した事)。
- 目標=★②(想起を要さぬ形。ただし①=門/hookの強制までは今回求めない)★: 「読み方」を★構造かcodeへ埋め込み、
  次に誰かがこのfileを開こうとした時に★正しい手段が自動的に見つかる/選ばれる★状態。

---

## 設計候補(3案、優先度付き。いずれも実装は今回行わず)

### 案A(最小・読み手側のみ・書き手不触) ★推奨(実装は待て、との縛り下での最有力候補★

共通helper(例: `scripts/read_pruned_archive.sh` または既存 `lib/` 配下への1関数追加)を新設し、
`yaml.safe_load_all()`で全documentの`messages`を連結して返す、単一の正規読み出し口を作る。
- 利点: 書き手(`inbox_write.sh`のCAP_ROTATEDロジック、既にflock保護下で安定稼働中)を一切変更しない
  ため、稼働中の止血対象(bats)や凍結に触れる余地が最小。既存10fileすべてに無変更で通用する。
  Anti-Duplication済(既存の同等helperは皆無、新設は正当)。
- 弱点: 「helperを使う」事自体を知らねば、新しいagent/scriptが素朴に`safe_load`を書いてしまう再発余地は
  残る(=完全な②ではなく②寄り)。helperの存在をCLAUDE.mdか隣接ドキュメントへ明記する事とセットで初めて効く。

### 案B(書き手も直す・単一document化) — ①寄りだが実装リスク大、今回は据置推奨

CAP_ROTATED発火時、既存archiveを読み込み→既存`messages`へ新規`dropped`をマージ→単一documentとして
atomic書き直し(tmp+rename、既存の live inbox書き込みと同パターン)。既存10fileは一括で1回だけ
移行(全document連結→単一document化)が必要。
- 利点: 以後は誰が素朴に`safe_load`しても正しく読める=真に①(様式)へ近付く。
- 弱点: 書き手側の変更ゆえリスク大(flockを archiveにも拡張する必要・file全体を都度読み直すためO(n)化・
  移行そのものが「実装」であり本工区の縛り「実装は待て」に真っ向から抵触)。★止血(bats)対象の周辺コードにも
  近接しており、今このtimingで着手すべきではないと判ずる★。

### 案C(案Aの補強・自己記述マーカー) — 案Aと併用可、これも実装は今回見送り

各archiveの1行目に`# multi-document YAML: use yaml.safe_load_all(), not safe_load()`等の
自己記述コメントを追加(書き手側の変更だが1行追記のみ・データ構造は不変)。または`_archive/README.md`を
新設し契約を明文化。案Aのhelperと組み合わせる事で、helperを知らずに直接fileを開いた人間/agentにも
その場で契約が見える(=③(条・口伝)から②(その場に書いてある)への引き上げに直接資する)。

---

## 対に成る他工区

足軽3号殿「出口の門」(B-119/B-133、台帳三段分類 `2026-08-05_ledger_tier_classification_a3.md`、
凍結解除後まで据置と原典明記済)——あちらは★様式(①)側の実物の門を将来作る是非★、当職は★条(③)を
まず②へ動かす設計★という住み分け。両者とも「実装は今は行わない」で共通。

## 母集団漏れの自己申告

1. 三段②の厳密な原典定義(将軍second令 §1)は未読——karo-second殿の要約からの推定である旨、上記③節に明記済。
2. legacy系3fileは今回の母集団(multi-document化した稼働中archive)から明示的に除外——理由=`---`区切り0件
   (旧仕様の単発形式のまま、今回の欠陥とは別種)。
3. 案A/Cのhelper実装そのものの詳細設計(引数・出力形式・エラー処理)は「設計のみ」の粒度に留め、
   コード本文は書いていない(実装は待て、との明示縛りに従った)。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、設計案、家老second殿の受理判断へ供する。

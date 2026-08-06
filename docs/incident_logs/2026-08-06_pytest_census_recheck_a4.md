# 家老second「pytest census」偽陰性疑いの引き直し(足軽4号)

下命=家老second msg_20260806_113504_c740fd32(11:35:04)。読取のみ・GO不要。裁定は当職(家老second)と将軍second が為す。

**冒頭に索引から一条**(原候補#14・`docs/incident_logs/2026-08-06_rules_index_a2.md:268`)=
**「見つからなかった」と「無い」を分けよ**。本便はまさにこの分けが要る工区である——
①「pytest census が引いた path」は**見つからなかった**(探索の限界)。
②「queue/inbox 便が除外される」は**無い**(git/ugrep 双方を実測して確認した事実)。
この二つを混同しない。

## 境・未測・限界

読取のみ。実走(pytest等)・apply・DB接続・commit(当職以外)・hook/guard/settings.json/.gitignore の編集、
一切なし。probe file は1件も作成していない(既存の gitignored file の実在確認のみで足りた)。
`git add -f` 未使用。hakudokai-dev/newbuild へ一字も書いていない。rc はpipeに通していない。

## 測時・断面

測時=2026-08-06T11:45:17+0900(`date`実行)。HEAD=`55024a0feb3cd7dc28c59d3d42df1ac4d5201ce1`。
working tree=`docs/incident_logs/2026-08-06_prohibition_source_census_a5.md`・
`2026-08-06_self_reversal_census_0917_a5.md` の2件が M(当職の変更に非ず・他工区の未commit分)。
`.gitignore` sha256=`c46f5b5dd50ce02644a589c4685bce10491cdb67054d46ebb06f6bbd711642a4`(429行)——
a3 の監査済報告(`2026-08-06_grep_wrapper_ignore_files_divergence_a3.md`)引用値と**一致**(不変を確認)。

---

## ① 母集団宣言——当職(家老second)の「pytest census」が現に引いた path

### ㈠ 探索方法(逐語コマンド)

```
$ /usr/bin/grep -rl "pytest census\|pytest_census" docs/ queue/ 2>/dev/null | sort
$ python3 -c "...yaml.safe_load...'pytest census' in content..."  (全 queue/inbox/*.yaml + _archive を対象)
$ git log --oneline --all -S"pytest census" / -S"pytest_census"
$ /usr/bin/grep -rn "pytest.census|pytest_census" --include="*.md" --include="*.yaml" .
```

### ㈡ 結果——**特定できず**

上記の悉皆探索で「家老second の pytest census」という語が現れたのは、以下**4通のみ**であった
(いずれも karo-second 発・本日11:17〜11:35台・a3/将軍second 宛):

| id | 時刻 | 宛先 | 内容 |
|---|---|---|---|
| msg_20260806_111718_f0e2ad7a | 11:17:18 | 足軽3号 | 「当職の pytest census(docs と 便の 横断 grep)」と一句のみ |
| msg_20260806_112131_8d11d4bb | 11:21:31 | 足軽3号 | 同上(再送・type訂正) |
| msg_20260806_112840_fb102ffe | 11:28:40 | 将軍second | 「貴殿の pytest census(docs・便の横断grep)」 |
| msg_20260806_113544_ad6bd046 | 11:35:44 | 将軍second | 「当職の pytest census」+ 本下命の発令 |

**4通いずれも「docs・便の横断grep」という2語の要約のみ**で、逐語コマンド・具体 path・実行時刻・
件数を含む記録は**repo全体(git履歴含む)を悉皆探索しても見当たらなかった**。
`git log -S"pytest census"` は0件(該当commit無し)。`docs/incident_logs/` 配下に該当file名も無い。

∴ **①の答=特定できず**。理由=**census そのものが、本便で挙げた4通の一次記録の外部化(結論の要約)
のみを残し、その方法(コマンド・path列挙)を一度も file 化していなかった**。これは家老second 自身が
本日繰り返し指摘してきた型「①片方が無い」(`2026-08-04_karo-second_day_ledger.md` §2)の実例であり、
「見つからなかった」であって「census が存在しなかった」ではない——推さずにそのまま書く。

---

## ② whitelist 行の有無——census の説明文が名指す2カテゴリを実測

①で個別pathは特定できなかったが、4通全てに共通する記述「docs・便の横断grep」から、
対象は**カテゴリとして2つ**(docs/ と 便=queue/inbox メッセージ)と読める。この2つに限り、
`.gitignore` を実読して whitelist 行の有無を確認した。

### ㈠ docs/ (`docs/incident_logs/*.md` 等)

```
$ /usr/bin/grep -n "^!docs/" .gitignore
191:!docs/
201:!docs/incident_logs/
202:!docs/incident_logs/*.md
```
個別glob(`*.md`)を伴う whitelist あり。**git 自身も** untracked と判定せず=
`git check-ignore -v docs/incident_logs/2026-08-06_gate_invocation_audit_a3.md` → **exit=1(除外されず)**。

### ㈡ 便=queue/inbox/ (メッセージ本体)

```
$ /usr/bin/grep -n "^!queue/" .gitignore
244:!queue/
245:!queue/pane_registry.yaml
```
`!queue/`(244行目)は**裸のdirectory-whitelist行**(個別glob無し)。a3 監査済報告(§②-e/②-f、
軍師second PASS・commit 589a1e5)が既に特定した「ugrepが再帰的に全許可と誤読する」条件そのものに該当する。

**当職が本工区で追加実測した点(a3 未確認だった箇所)**:
```
$ git check-ignore -v queue/inbox/ashigaru4.yaml
.gitignore:7:*    queue/inbox/ashigaru4.yaml    ← git 自身は「無視対象」と判定 (exit=0)
$ git check-ignore -v queue/inbox/karo-second.yaml / shogun-second.yaml / ashigaru3.yaml
→ 悉く .gitignore:7:* に捕捉・exit=0
$ git status --porcelain --ignored=matching -- queue/
→ 7304行(queue/配下の大半が `!!` = git的には無視対象のまま)
```
**∴ `queue/inbox/*.yaml`(便そのもの)は git の真の解釈では「今も無視対象」**——
`!queue/`はディレクトリ探索の許可のみで、個別fileの再許可(`!queue/inbox/`等)が無い限り
line 7 の裸 `*` が効き続ける。これは a3 の②-c/②-fが `queue/_a3_probe.py` で既に実証した構造と同一。

---

## ③ 同じ探索を /usr/bin/grep で引き直し・差分

①で逐語コマンドが特定できなかったため、「同じ探索」の文字通りの再実行は不可能である。
代替として、②で確定した2カテゴリ(docs/・queue/inbox/)そのものに対し、wrapped grep(=`grep`
shell関数・ugrep --ignore-files)と `/usr/bin/grep` を複数の検索語で突き合わせた。

```
$ grep -rl "pytest" docs/ | wc -l          → 20
$ /usr/bin/grep -rl "pytest" docs/ | wc -l → 20                    (一致・差分0)

$ grep -rl "timestamp" queue/inbox/ | wc -l          → 62
$ /usr/bin/grep -rl "timestamp" queue/inbox/ | wc -l → 62          (一致・差分0)

$ grep -l "timestamp" queue/inbox/*.yaml | wc -l          → 20
$ /usr/bin/grep -l "timestamp" queue/inbox/*.yaml | wc -l → 20     (一致・差分0)

$ grep -rl "read" queue/inbox/_archive/ | wc -l          → 16
$ /usr/bin/grep -rl "read" queue/inbox/_archive/ | wc -l → 16      (一致・差分0)
```

**個別file到達性の直接確認**(件数一致が「探索漏れ」を隠していないかの検算):
```
$ grep -l "timestamp" queue/inbox/ashigaru4.yaml   → 発見(exit=0)  ← git的には無視対象のfileだが wrapped grep は発見する
```

---

## ④ 三値報告

| 対象 | 判定 | 根拠 |
|---|---|---|
| 家老second の pytest census が引いた**元の逐語path/コマンド** | **㈢引き直せぬ** | ①の悉皆探索(repo全文+git履歴)で一次記録が見当たらず。4通いずれも要約のみで再現不能。**「引き直せぬ」の理由=そもそも記録が存在しない**(a3/足軽3号の「潰しに掛かって潰れなかった」とは異なる型) |
| docs/(census が名指す一方のカテゴリ) | **㈠差分零** | wrapped grep = `/usr/bin/grep` = 20件(pytest語)。git check-ignore も exit=1(除外対象外)と整合 |
| 便=queue/inbox/(census が名指すもう一方のカテゴリ) | **㈠差分零** | wrapped grep = `/usr/bin/grep`(timestamp語62件・read語16件・個別file到達も確認)。**ただし git の真の判定は「無視対象」(§②㈡)——ugrepがgitより甘い側に誤っているために結果的に差分が出ていない**。a3監査済報告の「queue/は`!queue/`裸whitelistゆえugrepが除外せぬ」という既存の確定条件と**整合し、新規の乖離ではない** |

**∴ 総括**=①(元census自体)は再現不能ゆえ「引き直せぬ」。②(census が名指した2カテゴリ)は
実測した範囲内で差分零(=偽陰性は今回確認できず)だが、これは「探索が万全だったから」ではなく
「対象2カテゴリが、たまたま a3 が既に特定した『裸directory-whitelist行あり』(queue/)または
『個別glob whitelistあり』(docs/)のいずれかに該当し、ugrepの甘い誤読の恩恵を受けていた」ためである。
**偶然の無事であり、方法論としての安全確認ではない**(a3 報告 §④「実害を免れたが、それは偶然」と同型)。

---

## 新たに開ける穴

1. **census 自体が「書かれるが読み返されぬ」型の別例**——結論(「零件」「見つからず」)は上位へ運ばれたが、
   その方法(path・コマンド)は一度も file 化されず、本日の「梯子」原則(書く→誰でも読める形→読み返す→
   動く)の第一段(書く)自体が欠けていた。今後同種の census を行う者への申し送り=**結論を書く時に
   コマンド・pathも同じ file に書け**(将軍second の条「便の値と実測の値が在る時人は便の値を書く」と同型の
   リスクを、census という形式そのものが構造的に生む)。
2. `queue/inbox/_archive/`(便の一部)も同様に「git的には無視対象・ugrepは発見する」状態にある。
   本工区では `read`語のみ実測(16=16)。他の語での網羅確認は未測。
3. 本工区は docs/・queue/inbox/ の**2カテゴリのみ**を検めた。census の説明「docs・便」がこの2つに
   限定される保証はなく(3つ目以降の対象が在った可能性は排除できない)——①で特定できなかった直接の帰結。
4. queue/ 配下 7304行が git的には「無視対象のまま」という事実(§②㈡)自体は、pytest census とは別に
   「commit 対象と実態の乖離」という独立した観察であり、本工区の範囲(census偽陰性の検め)を超える。
   裁定・是正は当職の権限外ゆえ書かない。

## 【本工区で己が直した誤り】

無し(読取のみ・新規発見はあれど本工区中に自分の誤りを書いて訂正した事実は無い)。

## 対に成る他工区

`docs/incident_logs/2026-08-06_grep_wrapper_ignore_files_divergence_a3.md`(足軽3号・軍師second PASS・
commit 589a1e5)——本工区の②③はこの報告の実証手法(②-b〜②-f)をそのまま踏襲・追試した関係で、
新規の乖離を発見したわけではなく**既存PASS済finding の再確認**である事を明記する。

## 監査体制

暫定二者制(軍師second + Gemini)。Codex leg は禁令(2026-07-21事案・SAFETY裁定 seq132707)により停止中。
「二者PASS」を「三者PASS」と書かない(委員長殿裁定)。

## 禁則遵守の申告

読取のみ。probe file 作成0件。hook/guard/settings.json/.gitignore 編集0件。`git add -f` 不使用。
hakudokai-dev/newbuildへ一字も書いていない。rc はpipeに通していない(各コマンド単発実行・`$?`/出力を直読)。
`/usr/bin/grep` を明示使用。

---
report path: docs/incident_logs/2026-08-06_pytest_census_recheck_a4.md

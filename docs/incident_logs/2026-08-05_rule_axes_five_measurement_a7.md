# 条の誤用/不適用/軸五 測定 — 足軽7号

下命系譜: karo-second msg_20260805_153114_5be0fbe3 (①誤用を数えよ) → msg_20260805_154458_bce6348a (③不適用/④下命不能を追加、将軍second起案) →
msg_20260805_160826_e2a44128 (⑤己の言葉が変わったか、を追加、家老second→将軍second msg_20260805_160516_621a6692が出所)。
最終形=五軸: ①誤用 ②条が悪い ③不適用 ④下命が不能 ⑤己の言葉が変わったか。
本工区は「上二人(karo-second/shogun-second)を測る」もの(彼ら自身の弁)であり、当職を測る工区ではない。

断面 = 2026-08-06T00:22:44+0900 ($ date -Iseconds)。base_commit = d90e2d1b (`git rev-parse HEAD`)。
working tree: 本工区は読取のみ、対象file不触(git status --short 実測=5件、いずれも本工区着手前からの既存差分で当職が触れた物ではない)。
監査体制: 二者制(軍師+Gemini)。Codex leg 停止中(2026-07-21事案)。「二者PASS」を「三者PASS」と書かぬ。

---

## 0. 母集団 — 二つの箱、二つの形 (宣言は最初にせよ)

★本工区で最初に断らねばならぬ事★: 「karo-second/shogun-second が書いた便」の完全な母集団は当職の手元に無い。
両者は多数の宛先(全ashigaru・軍師・互いの宛先)へ書いており、当職が読取り得るのは **当職が受け取れる箱のみ**。
∴ 二つの異なる形の母集団を使い分け、揃わぬ事を隠さず明記する。

### 母集団A — karo-second が書いた便 (当職(ashigaru7)の箱、2026-08-05分)

```
$ python3 -c "
import yaml
with open('queue/inbox/ashigaru7.yaml') as f:
    data = yaml.safe_load(f)
msgs = data['messages']
cnt = {}
for m in msgs:
    f_ = m.get('from'); ts = str(m.get('timestamp',''))
    if f_ in ('karo-second','shogun-second') and ts.startswith('2026-08-05'):
        cnt[f_] = cnt.get(f_,0)+1
print(cnt)
"
{'karo-second': 25}
$ bash scripts/read_pruned_archive.sh queue/inbox/_archive/ashigaru7_pruned.yaml --count-only
{"file": "queue/inbox/_archive/ashigaru7_pruned.yaml", "documents_total": 6, "documents_none": 1, "messages_total": 91}
```
current(0件重複なし)+archive(2026-08-05分は既にcurrentへ遷移済で重複0、実測=unique_ids 25/25)を合算=**25件**(11:26:44〜19:14:40)。
内訳=notification(全員宛・条の発行本体)10件・task_assigned(当職個別宛)9件・status_update 6件。

**★shogun-second は当職の箱に2026-08-05分が0件★**(chain of command上、将軍second→家老second→足軽の経路ゆえ、
将軍second発の便は当職へ直接は来ぬ)。∴ 母集団Aは karo-second専用。

### 母集団B — shogun-second が書いた便 (karo-second の箱、2026-08-05分、shogun-second→karo-second のみ)

```
$ python3 -c "
import yaml, subprocess, json
cur = yaml.safe_load(open('queue/inbox/karo-second.yaml'))['messages']
arc = json.loads(subprocess.run(['bash','scripts/read_pruned_archive.sh','queue/inbox/_archive/karo-second_pruned.yaml'],capture_output=True,text=True).stdout)['messages']
all_msgs = cur+arc
pop = [m for m in all_msgs if m.get('from')=='shogun-second' and str(m.get('timestamp','')).startswith('2026-08-05')]
print(len(pop))
"
177
```
**177件**(11:16:51〜21:05:35、全件 type=cmd_new — 後述§5で「型」の判定に使えぬ事が判明)。

### ★母集団の限界(自己申告)★

1. 母集団Aは「karo-second が書いた全便」ではなく「karo-second が当職へ配った便」。他ashigaru個別宛の便(母集団外)は0件把握。
2. 母集団Bは「shogun-second→karo-second」のみ。shogun-second が他宛先(ashigaru直・軍師直)へ書いた便は含まれぬ。
3. AとBは**形が違う**(A=多数宛のbroadcast中心、B=1対1の指揮系統便)。同じ物差しを両者へ当てれば、
   その違い自体が数の差として出る公算がある——これは「見せかけの差」であって「行動の差」ではない可能性を含む。
4. 19:14:40 以降(当職の最終受信)〜現在(00:22)の間、両者がさらに書いた便は**母集団に含まれておらぬ**
   (母集団Bは karo-second の箱をそのまま読んでいるため21:05:35まで拾えているが、Aは当職の箱の性質上19:14:40で止まる)。

---

## 1. 軸①誤用 と 軸③不適用 — 区別できた実例が一件

### 方法(機械)

```
$ python3 - <<'PYEOF'
import json, re
with open('/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/ff4f50d8-9747-41e9-9c7f-ba2454be03b4/scratchpad/pop_20260805.json') as f:
    pop = json.load(f)
pop.sort(key=lambda m: m.get('timestamp',''))
markers = ['訂正','誤り','誤って','誤用','誤診','誤認','誤配','誤読','間違']
for m in pop:
    c = m.get('content','')
    hits = [mk for mk in markers if mk in c]
    if hits:
        first = hits[0]; idx = c.find(first)
        snippet = c[max(0,idx-40):idx+60].replace('\n',' ')
        print(f"{m['timestamp']} | {m['id']} | hits={hits} | ...{snippet}...")
PYEOF
```
(母集団抽出は §0 のコマンドで scratchpad の `pop_20260805.json` に既に保存済、本コマンドはそれを読むのみ)
陽性対照: 上記markerセットは既知の実例(msg_20260805_144059、「周知③が誤りに御座った」)を実際に検出する
(hits=['訂正','誤り','誤読'])ことを先に確認した上で母集団A全件へ適用。

### 出力(母集団A・25件中、marker命中=9件)

| 時刻 | id | hits |
|---|---|---|
| 11:59:03 | msg_115903 | 誤り(様式節への言及、実例ではない) |
| 12:11:50 | msg_121150 | 誤り/誤って(行き先ポインタB-32→B-44の誤配) |
| 12:40:07 | msg_124007 | 誤り(様式節への言及、実例ではない) |
| 14:02:36 | msg_140236 | 誤り(様式節への言及、実例ではない) |
| 14:09:46 | msg_140946 | 訂正/誤り/誤って(★足軽7号への誤帰属を自ら訂正★) |
| 14:13:23 | msg_141323 | 誤って(「書き手は誤っておらぬ」=否定文、実例ではない) |
| 14:16:32 | msg_141632 | 誤って(同上、否定文) |
| 14:40:59 | msg_144059 | 訂正/誤り/誤読(★周知③の誤りを2分29秒で自己訂正★) |
| 14:45:30 | msg_144530 | 訂正/誤り(前便の補正=上と同一事象の続き) |
| 15:31:14 | msg_153114 | 誤って/誤用(「十二箇条を誤って当てはめた数」を問う本文=概念言及) |
| 15:44:58 | msg_154458 | 誤り/誤用(「git外=死蔵は誤り」という既存前提の訂正+★不適用の実例2件を自己申告★) |
| 16:08:26 | msg_160826 | 誤用(概念言及) |
| 16:12:56 | msg_161256 | 誤用(概念言及) |
| 16:45:32 | msg_164532 | 誤り(将軍second便の「母集団の誤りには二種」引用) |
| 17:13:20 | msg_171320 | 誤り(「五度の誤り」=Rule7違反の集計、下記§2参照) |
| 18:18:20 | msg_181820 | 誤り/誤って(★己のmemory検索が書き癖不一致で0件を得た誤り★) |
| 19:14:40 | msg_191440 | 誤り(判定限界への言及) |

**分離の結果**: marker命中17件のうち、①「12箇条(⑴〜⑿)そのものの誤用」に該当する具体例は **0件**。
理由=12箇条の全条(⑿まで)が出揃うたのは15:15:39(msg_151539)であり、それ以前の誤り(12:11/14:09/14:40)は
条の体系が未確立の時点の一般的な事務誤り(誤配・誤帰属・誤った周知)であって「立てた条を誤って当てた」形ではない。
条確立後(15:15:39〜19:14:40)の marker命中3件(15:31/15:44/18:18)は、いずれも著者自身が①ではなく
**③不適用として自己分類し直している**(下記)。

### ★①と③の区別が現に付いた一件(karo-second 自身の二便)★

- **15:31:14 (msg_153114)**: karo-second が「足軽3号のexpected_by」を自分の待たせ(足軽7号への「裁定後に声を掛ける」)に
  **適用しなかった**ことを詫び、この時点ではまだ「同じ失を三時間で繰り返した」という一般的な反省の書き方。
- **15:44:58 (msg_154458)**: 13分後、これを明示的に **③不適用の実例**として再分類:
  > 「不適用=当職が『追って声を掛ける』に期限を書かなんだ(足軽3号のexpected_byを己の差配に当てておらぬ)」
  同便でもう一件: 「不適用=当職の『十一』がgit grep由来の過小(己のmemory `grep-git-grep-silently-skip-gitignored`を引かなんだ)」

**∴ 誤用と不適用の機序上の違い**(実例から抽出): 誤用は「条を引いた跡が残る」(引用・適用の記述がある)のに対し、
不適用は「条は存在するのに引いた跡が一切無い」(期限欄自体が最初から書かれていない・memoryを検索した形跡が無い)。
**跡の有無こそが機械可読な識別点**——本工区の機械scanが誤用0件・不適用複数件を返したのは、
「誤用は跡が残るゆえ探せば見つかるが、不適用は跡が残らぬゆえキーワードscanでは原理的に見つけにくい」という
非対称性の反映である可能性が高い(将軍second自身が同旨を先に指摘: 「不適用の方が数え難く、数え難きゆえ多い公算」)。

---

## 2. Rule 7 (dashboard 🚨要対応 未記載) — 既存の自己集計を引用のみ、独立再測はせず

karo-second msg_171320 (17:13:20) が本文中で以下を集計している:
> 「本日 Rule 7 違反(要対応欄への未記載)は将軍second三度・家老second二度=計五度」

★本件は当職が独立に再測していない。引用に留める★(条: 引用には断面を付せ、に従い出所を明記)。
出所=karo-second本人の自己申告、母集団・カウント方法は本文に記載なし(検証不能)。
独立再測には karo-second/shogun-second 双方の全2026-08-05便からRule7発火条件(dashboard更新を要する事案の発生)を
洗い出し、実際に🚨要対応欄へ記載したか照合する必要があり、本工区の時間枠では実施していない——
**★「未確認」と明記する★**(実施すれば別途工区が要る規模)。

---

## 3. 軸②条が悪い — 確定1件

### 実例: 欄①の様式改訂(msg_164532、16:45:32)

出所=将軍second msg_20260805_164431_2bcb180d(karo-second が引用)。
経緯: 旧様式「探した場所を書け(散文可)」の下で、将軍second が「検索=queue/reports/全件+repo全体」と**文章では書いた**が、
実際に打った命令は `grep -rln … queue/reports/` のみ(repo全体は検索していない)。
**欄は埋まっていたが、中身は事実と異なっていた**。

```
$ /usr/bin/grep -rln "迂回し得る|bypass_census|30経路" .
./dashboard.md
./docs/incident_logs/2026-08-05_legB_gate_bypass_census_a2.md
./queue/inbox/shogun-second.yaml
./queue/inbox/ashigaru2.yaml
./queue/inbox/karo-second.yaml
```
(karo-second が本便中に実測として貼付、5件。queue/reports/限定では0件だった対象が正しく打てば一発で出た、という実演。)

∴ これは「条の誤用」ではなく「**条(欄の様式)自体が虚偽申告を検出できない設計だった**」に該当する。
karo-second はこれを受けて即座に様式を改訂した(「散文の範囲説明は不可・打った命令そのものと出力を貼れ」)。
★これは既に「①誤用」節で挙げた msg_164532 marker命中と同一事象——一件を二軸(①誤りの言及・②条の欠陥)双方に
またがる例として扱う。二重計上ではなく「一つの事象が複数の軸に該当し得る」ことの記録として残す。

母集団の限界: 「条が悪い」の候補を「様式改訂」というキーワードで拾える形は本件のみ発見。他の11条(⑴⑶⑷…⑿)が
後に改訂されたかは、本工区の母集団(25+177件)を全数走査した限りでは発見できず(未発見=不在の証明にはならぬ、
上記の通り「跡が残る」タイプの事象のみ拾える手法である)。

---

## 4. 軸④下命が不能 — 確定1件、自己申告からの引用

母集団A・B双方を`不能`でscanしたところ大半は「判定不能」(別の三値系: 誤用/条が悪い/判定不能、から来る語)への
誤ヒットであり、`下命が不能`という限定語での命中は母集団A中1件のみ(msg_154458)。

> 「四値=①誤用②条が悪い③不適用★④下命が不能★——④の現物=足軽5号の第二工区(.claude/settings.jsonのhookへ
> 配線——実装先が存在せなんだ)」

**当職はこの実装対象の不在を独立に検証していない**(足軽5号の当該工区成果物へ当職はアクセス権を持たぬ・
readonly境界内で他者成果物を検めるのは越権のおそれがあるため未実施)。引用として明記するに留める。

**自己申告(検索手法の誤り)**: 当初 `不能` のみでscanし「判定不能」を大量に誤って④の候補として拾いかけた
(下記§6で条⑿として計上)。`下命が不能`まで絞ってから確定1件。

---

## 5. 軸⑤己の言葉が変わったか — 自己申告数値の独立検証を試み、方法の限界に当たった

### karo-second の自己申告(msg_160826)

> 「条を十二立てたが、己の言葉遣いが変わったは点検の日の一件のみ」

★当職はこれを独立に検証できていない★——karo-second が「他の宛先へ書いた便」(母集団A外)を
当職は読取れず、「点検の日」が具体的にどの成果物を指すかも本文からは特定できなかった。**未確認**と明記する。

### shogun-second の自己申告(msg_20260805_160516_621a6692、母集団Bの一部)

```
$ python3 - <<'PYEOF'
import json
with open('/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/ff4f50d8-9747-41e9-9c7f-ba2454be03b4/scratchpad/pop_shogunsecond_20260805.json') as f:
    pop = json.load(f)
for m in pop:
    if m['id'] == 'msg_20260805_160516_621a6692':
        print(m['content'])
PYEOF
```
本文(実測・全文引用の一部):
> 「母集団未確認と添える=宣言済・実行一度(本便までに再度は無し)」
> 「便の型は緊急度で選べ=宣言済・実行一度(status_updateへ落とし申した)」
> 「一部を検めたと書く=宣言済・実行零(本便が初めての機会に御座る)」
> 「上記の数は己で数えた物ゆえ条⑸に反し申す——他者に測らせられたし」

★本件は shogun-second 自身が「他者に測らせよ」と明示的に要請した数値であり、本工区の直接の測定対象。★

### 独立検証(機械・母集団B全177件)

```
$ python3 - <<'PYEOF'
import json
with open('/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/ff4f50d8-9747-41e9-9c7f-ba2454be03b4/scratchpad/pop_shogunsecond_20260805.json') as f:
    pop = json.load(f)
pop.sort(key=lambda m: m.get('timestamp',''))
markers = {
  '母集団未確認': ['母集団未確認','母集団が未確認','母集団は未確認'],
  '緊急度で型選択': ['緊急度で選','緊急度に応じ','型は緊急度'],
  '一部を検めた': ['一部を検めた','一部のみ検めた','一部を確認した'],
}
for label, pats in markers.items():
    hits = [(m['timestamp'], m['id']) for m in pop if any(p in m.get('content','') for p in pats)]
    print(f"--- {label} : {len(hits)} hits ---")
    for ts,i in hits:
        print(' ', ts, i)
PYEOF
```
```
--- 母集団未確認 : 1 hits ---   (msg_20260805_160516_621a6692 = 宣言便そのもののみ)
--- 緊急度で型選択 : 1 hits ---  (同上)
--- 一部を検めた : 2 hits ---   (宣言便 + 15:59:13 msg_155913、宣言便より★前★の便)
```

**結果**: 宣言便(16:05:16)以降、当職の文言一致検索では3項目とも**追加の再出現=0件**
(自己申告の「実行一度・一度・零」に対し、当職の機械検索は「一度・一度・零」ではなく「零・零・零」を返した)。

**★この不一致は「自己申告が過大」の証拠ではなく、当職の手法の限界と読むべき★**理由:
1. 自己申告「実行一度」は**文言の再利用**ではなく**実践の再現**(パラフレーズで別の言葉になり得る)を指している公算が高く、
   完全一致文字列検索では原理的に検出できない。
2. 「便の型は緊急度で選べ=status_updateへ落とし申した」を検証しようと `type` フィールドで前後比較したところ、
   母集団B **177件全てが type=cmd_new で統一**されており(下記)、「型」が指すのはYAMLの`type`欄ではなく
   別の概念(文面構成・緊急度表現など)だったと判明——★当職は誤ったfieldで検証しようとした=これ自体が
   本工区における当職自身の「誤用」(適用対象を取り違えた)の実例として自己計上する(条⑿への回答、下記§6)★。

```
$ python3 - <<'PYEOF'
import json
from collections import Counter
with open('/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/ff4f50d8-9747-41e9-9c7f-ba2454be03b4/scratchpad/pop_shogunsecond_20260805.json') as f:
    pop = json.load(f)
pop.sort(key=lambda m: m.get('timestamp',''))
before = [m for m in pop if m['timestamp'] < '2026-08-05T16:05:16']
after  = [m for m in pop if m['timestamp'] > '2026-08-05T16:05:16']
print('before decl:', len(before), 'after decl:', len(after))
print('type dist before:', Counter(m.get('type') for m in before))
print('type dist after :', Counter(m.get('type') for m in after))
PYEOF
```
```
before decl: 99 after decl: 77
type dist before: Counter({'cmd_new': 99})
type dist after : Counter({'cmd_new': 77})
```

**∴ 軸⑤の結論**: shogun-second の自己申告数値(実行1・1・0)を、当職の機械的手法(文言完全一致)では
再現できなかった(0・0・0)。**この差は「言葉が変わっていない証拠」ではなく「検証手法が言い換えを拾えない
という限界の証拠」である**——同一の事を違う言葉で書けば人間には分かるが機械の完全一致検索には見えぬ、
という本工区全体を貫く病理(karo-second/shogun-secondが本日繰り返し指摘してきた「跡が残る/残らぬ」問題)に、
当職の検証手法自体もまた捕まった。

---

## 6. 条⑿(門を設計する時、己がそれをどう破るかを先に書け)への自己適用

本工区の測定手法(=母集団選択+キーワード完全一致scan)は当職自身が設計した「門」である。
これを当職ならどう破るか、実行はせず記すのみ:

1. **母集団の選び方で結果を作れる**: 母集団Aを「当職の箱のみ」にすればshogun-second分は0件に潰せるし、
   母集団Bのように「karo-second経由」を使えば177件拾える。本工区でも実際に**この選択で結果の形が変わった**
   (母集団A=karo-second専用・母集団B=shogun-second専用という非対称自体が、母集団選択の産物)。
2. **キーワード不一致は「不在」に読み替えられる**: §5で実演した通り、完全一致検索は言い換えを拾えず、
   「実行1回」を「実行0回」と誤読させ得る。逆方向(過少評価)にも(誤って広い語`不能`を使えば`判定不能`を
   `下命が不能`と誤カウントする)過大評価にも振れる——**同じ手法が両方向に壊れ得る**。
3. **境界時刻の選び方**: 母集団Aは19:14:40で打ち切られている(当職の最終受信)。もし「本日」の定義を
   00:00〜23:59に厳密に取れば、19:14:40以降に両者が書いた便(現に存在する可能性が高い、母集団Bは21:05:35まで
   拾えている)が母集団Aには一件も入らない——「karo-second は19:14:40以降 何も誤らなかった」という
   誤った印象を生み得る(実際は「当職が読めなくなっただけ」)。
4. **自分の誤りを実演することで信頼を得ようとする自己言及の罠**: 本節・§5で「自分の手法の誤りを自白した」
   ことが、あたかも「当職は誠実だ」という印象を与え得るが、★自白した誤りが全てとは限らぬ★
   (見つけていない誤りは、見つけていないという理由だけで報告に現れない)。

---

## 7. 本工区で己が直した誤り(欄・空欄不可)

1. axis4の初回scanで`不能`のみを使い`判定不能`(別系統の語)を大量に誤ヒットさせかけた→`下命が不能`まで
   絞り込んで再scan、確定1件に修正(§4)。
2. axis5の「便の型は緊急度で選べ」検証で`type`フィールド(YAML schema欄)を使おうとしたが、
   母集団B全件が`cmd_new`で均一であることが判明し、この検証軸が無効と気付いた時点で該当検証を撤回し、
   「誤った適用対象を選んだ」事実そのものを§5本文へ記録した(隠さず記す)。

## 8. 対に成る他工区

無し(探した範囲=dashboard.md 00E周辺・本日のa1-a6成果物一覧。同種の「条五軸測定」を別ashigaruが
並行して行っている形跡は見当たらなかった——本工区自体が家老second→当職個別宛の下命であり、他者への
複製下命は確認できず)。

## 9. 誰が止めれば止まるか

本工区は読取専用(bats禁・.gitignore不触・commit禁)。停止手段=本fileの追記を止めるのみ。
他fileへの依存・書込は無い(scratchpad上の一時jsonは repo外・削除しても本fileの内容には影響しない)。

---

**提出**: karo-second へ inbox_write(work_started+ETA不要、本便が完了報)、軍師second へ直接監査提出
(CLAUDE.md:261、家老への報告は提出に非ず)。

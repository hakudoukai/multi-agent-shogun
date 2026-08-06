# TO_FILL の因を突き止める (足軽5号)

## 境・未測・限界 (冒頭に置く)

読取のみ。file を一つも書き換えていない。軍師second の便を責める形には書いていない
(下命の禁則どおり——同人は毎回己で訂しており、咎めの対象ではない)。

## 測時・断面

測時=2026-08-06T12:50:33+09:00。HEAD=c00f3c2af1b001b44b34a9a9fbb52c634f2c20a3。

## 用いた命令 (逐語)

```
/usr/bin/grep -n "TO_FILL" queue/reports/gunshi_report.yaml
/usr/bin/grep -rln "TO_FILL" queue/reports/
/usr/bin/grep -rln "TO_FILL" scripts/
/usr/bin/grep -rln "TO_FILL" memory/
/usr/bin/grep -rln "TO_FILL" instructions/ docs/ config/ context/
/usr/bin/grep -rln "TO_FILL" . --include=*.py --include=*.sh --include=*.md --include=*.yaml --include=*.yml --include=*.json
/usr/bin/grep -n -B2 -A2 "TO_FILL" queue/inbox/karo-second.yaml
```
(★`git grep`は用いていない=追跡下のみを見て`queue/`等を無警告で飛ばす既知の欠陥の為、
下命指定通り`/usr/bin/grep`のみを使用した★)

## ㈠ 雛形 (template) に埋め込まれておるか

**判定=無し**。`queue/reports/`・`scripts/`・`memory/`・`instructions/`・`docs/`・`config/`・`context/`
を悉く検索したが、静的な雛形file内に既定値として`TO_FILL`が埋め込まれている箇所は見出せなかった。
現時点 (12:50) の`queue/reports/gunshi_report.yaml`本体にも`TO_FILL`は0件 (既に解消済の断面)。

**再検め方**=上記コマンド群をそのまま再実行し、hit=0を確認する。

## ㈡ 埋め込まれておらぬなら、何処で生じておるか

**判定=手書き (生成物ではない)。★自己参照 (self-reference) の構造的必要から生じている★**。

`queue/inbox/karo-second.yaml`内の実出現5件全てを実読した所、悉く同一の型であった:
**軍師second が監査便の中で「自身が言及している当のfile自身のsha256」を、当該fileの書き終わり前に
本文へ引用せねばならぬ箇所**に`TO_FILL`が現れている。対象は常に以下の二種のいずれか:

1. **軍師second自身がその便で言及している監査票file** (例=`queue/reports/gunshi_second_rules_to_format_proposal_audit_20260806.md`)
   ——その監査票の内容を書き終えねばsha256は定まらぬが、同じ便の中で他の監査対象と並べて
   「path+行数+sha256」の形で一覧するには、書き終わる前にこの欄を埋める必要が生じる。
2. **`queue/reports/gunshi_report.yaml`自身** (実行中に追記している running log そのもの)
   ——この便を書いている最中の`gunshi_report.yaml`のsha256は、当該便の追記が完了するまで
   定まらぬ (追記完了後にhashを取れば良いが、便の本文はそれより先に組まれる)。

逐語引用 (`queue/inbox/karo-second.yaml` 行8・10):
```
queue/reports/gunshi_second_rules_to_format_proposal_audit_20260806.md 30行 sha256=TO_FILL,
docs/incident_logs/2026-08-06_rules_to_format_proposal_a3.md 142行 sha256=a2b2a51b...
queue/reports/gunshi_report.yaml 46行 sha256=TO_FILL, memory/gunshi-second_agent_audit_rules.md
```

逐語引用 (行34、直後の`supersedes`便で自ら訂正している実例):
```
先便は TO_FILL 混入ゆえ supersedes として訂正する。足軽1号の F3負契約設計 追補1は PASS 不変...
```

∴ **`TO_FILL`は「忘れた既定値」ではなく、書いている当のfile自身のhashを書き終わる前に引用する
という構造的に解決不能な瞬間 (ブートストラップ問題) に対し、軍師second が一時的に用いる
プレースホルダーであり、その後 supersedes 便で実測値へ置き換えている**、というのが5例全てに
共通する型であった。

**再検め方**=`queue/inbox/karo-second.yaml`の行8・10・34・144-148・174-178・471-474・584-588を
`Read`し、`TO_FILL`が指す対象file名が「同一便内で言及されている監査票 or `gunshi_report.yaml`
自身」であるかを目視突合する。

## ㈢ 三値

**在り** (path+行を上記に明記)。因は「雛形」ではなく「自己参照の書き順問題」。

## §3 他の代用札 (TBD/XXX/N/A/0000/未定) — 零ではないが未検証で明記

`scripts/`・`memory/`・`instructions/`・`config/`を対象に`/usr/bin/grep -rln`で機械的に検索した所、
いずれの札も0件ではなかった (TBD=5file・XXX=多数・N/A=多数・0000=6file・未定=8file)。★然れど
本工区の時間内では★「監査報告書式の既定値としての誤用」と「無関係な文脈での偶然の一致
(正規表現の`XXX`・16進数の`0000`埋め・`N/A`が普通の英語文として使われている等)」を区別する
手検証を行っていない★。∴ この節の数字は**未検証の生の件数**であり、TO_FILLの節と同じ確度では
扱えない事を明記する。

**再検め方**=各file個別に`/usr/bin/grep -n <札>`で該当行を実読し、「監査報告の値欄」かそれ以外かを
目視分類する (本工区未実施)。

## 母集団漏れの自己申告

1. `queue/reports/gunshi_report.yaml`は既に`TO_FILL`が解消された断面のみを見ており、
   過去に何回`TO_FILL`が現れて何回supersedesで訂されたかの累計は、当職は`queue/inbox/karo-second.yaml`
   内の目視ヒット数 (5件) でのみ把握しており、他inbox箱・archiveへは検索範囲を広げていない。
2. §3の代用札は手検証を行っておらず、生の件数のみである。

## 【本工区で己が直した誤り】

無し (読取のみ・新規の実測判断のみ・書換なし)。

## この工区が新たに開ける穴

`TO_FILL`が「自己参照の書き順問題」に起因すると判った以上、根治には「監査便の書式そのものを
自己参照を要さぬ形へ変える (例=自身のfileのhashは追記完了後の別便で追って示す)」という設計変更が
要る。★然れどこれは裁定 (直す側の選択) であり、当職は書かぬ★。

## 対に成る他工区

`docs/incident_logs/2026-08-06_shogun_second_state_snapshot_1225.md` (§5-6「軍師secondの`TO_FILL`
再発の因——雛形に埋め込まれておるか未測」と明記していた便。本工区がその未測を埋めた)。

## 監査体制

暫定二者制 (軍師second + Gemini)。Codex leg は禁令 (2026-07-21事案・SAFETY裁定 seq132707) により停止中。

## 禁則遵守の申告

読取のみ。file を一つも書き換えていない (雛形が見つかっても直すなの下命に該当せず=そもそも
雛形file自体が見出せなかった)。newbuild・hakodoukai-dev いずれも一字も書いていない。

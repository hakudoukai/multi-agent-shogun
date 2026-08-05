# 【00E門】追補2 — 解除の道・閾の置き場・閾値一箇所化(委員長殿裁定三件・足軽1号)

- **下命**: 委員長殿裁定三件 → karo-second msg_20260805_205024_e8257f53 → 当職。測時=2026-08-05T20:49:22 前後(機械、家老second 起筆)。
- **性質**: ★設計のみ★(本体・追補1と同じ立場)。実装 code の commit・`.gitignore` の適用・台帳 file の新設(実体)はいずれも含まぬ。
- **境**: read-only(repo 内 file 改変は本書 1 点のみ)・`.gitignore` 不触・bats 禁・commit は karo-second。★完了は軍師second PASS 後★。★提出は軍師second へ直★(家老への完了報は提出に非ず)。

---

## §0 断面(測定時刻をその場に貼る・条⑶)

```
$ date -Iseconds
2026-08-05T20:54:04+09:00

$ git rev-parse --short HEAD
3f5f5c0

$ git branch --show-current
feat/dd169-d006-conditional-exception

$ ls scripts/lib/
detect_stale.sh  inbox_path.sh

$ git check-ignore -q scripts/lib/detect_stale.sh; echo $?
1   ★=not ignored(追跡下・正)★

$ git log --oneline -1 -- docs/incident_logs/2026-08-05_gitignore_silent_gate_design_a1.md
b13dc31 docs(00E): gitignore silent drop 門 設計 本体+追補1 を保全(足軽1号起草・軍師second PASS)
```

本書中の grep/git コマンドの出力は、上記時間帯に当職が実行したそのままである(手で書き写していない・条⑾)。

---

## §1 委員長殿裁定三件の要旨(逐語は karo-second 便に在り、本書は設計への落とし込みのみ)

| 裁定 | 要旨 |
|---|---|
| ① 偽陽性をどの程度許すか | ★数で決めない。性質で決める★= 稼働しておるか判じ難い物は、止める側へ倒す |
| ② どちらへ倒すか | ★fail-closed(偽陽性寄り)★。必須の添え条=★止められた者が進む道(一行解除申請+記録が残る形)を必ず併設★。★道の無い fail-closed は壁★ |
| ③ 閾を誰が動かせるか | ★裁可者(委員長殿)のみ★。版管理された場所(code定数に埋めるな)・変更は commit に残る・動かしたら負テスト再実行+事実/理由/再テスト結果を同じ commit へ |
| ④(併せて) 閾値の一箇所化 | 警報側と門側で閾を別々に持つな(§48-d-20 の閾版。追補1 の述語一箇所化と対をなす) |

---

## §2 着手前の既存資産探索(二重実装の禁・条⑴の裏返し=横に開く穴を先に塞ぐ)

**探した範囲**: `docs/incident_logs/2026-08-05_*.md` 全件を `grep -n "解除\|閾"` で走査。

**近縁だが別物と確認した事例**:
- `docs/incident_logs/2026-08-05_legB_shadow_failclosed_impl_a2.md`(exit gate / delivery-route-stabilization lane、担当=足軽2号系統)。実測=`scripts/inbox_write.sh:396` に `local threshold="${INBOX_WRITE_STALE_READER_SECONDS:-86400}"`(env override 可・既定 86400秒)という★「env override可・file内既定値・単一箇所」の様式★が既に実在する。
- ∴ **この様式(env override + file既定値)を本追補でも流用する**(§6)。新形式の発明はしない。但し★対象 gate は別物(00E=gitignore門/legB=inbox配送門)ゆえ、実装(閾値の値そのもの・置き場の file)を共有するのは誤り★——様式のみ借り、実体は別に持つ(anti-duplication の正しい適用=手段の再利用と対象の混同を分ける)。

**見付からなんだ事**: 「解除申請+記録台帳」に相当する既存機構は 0 件(`docs/`・`scripts/`・`queue/` いずれにも「release ledger」「解除台帳」相当の file なし)。∴ **§4 は新造で二重実装に当たらぬ**。

---

## §3 裁定①②への応答 — 「性質で倒す」対象点の特定

本体 §4 の判定式 `ACTIVE = A OR B OR C`、`D` 単独 = `STALE`(非block)を、裁定①「性質で決める・判じ難い物は止める側へ」に照らして再検証する。

| 検証対象 | 現行の扱い | 裁定①への適合 |
|---|---|---|
| (a) C信号単独(grep構文一致・doc/report地の文の誤検知リスクを本体§4で既に「中」と明記) | `ACTIVE`(=FLAG) | ★既に止める側に倒しておる★ — ⒜(既存で足りた)。新規変更は要らぬ |
| (b) A/B/C いずれも0、D(mtime新しい)のみ | `STALE`(非block) | ★据置が正しい★ — Dは「判じ難い」ではなく「積極証拠が無いだけ」であり性質が異なる。「判じ難い=全部止める」に拡大解釈すれば偽陽性が母集団ごと膨らむ(§3-3実測20件のうち大半がD単独化しうる)ゆえ、裁定①の「性質で決める」を逆に破る |
| (c) ★新規発見★= A種/B種境界(本体§3-2)の判定そのものが人手判定であり、将来新設されるディレクトリが A種/B種いずれか自明でない場合 | 本体は未定義(母集団に入るか自体が不明=沈黙で漏れうる) | ★これが真に「判じ難い」に該当する★。境界不明ディレクトリ配下の新規 ignored file は、母集団判定そのものを FLAG 側(=要目視判定・自動ではCLEANに落とさぬ)へ倒す。本体になかった穴を追補2で塞ぐ箇所 |

**∴ 裁定①の反映は「新しい数値閾値の発明」ではなく「(c)の新規穴を性質で塞ぐ1点」に絞られる**——数を弄って偽陽性率を調整する行為(裁定①が明示的に禁じた形)を避けた。

---

## §4 解除の道(Escape Path)設計 — 裁定②の必須添え条

### §4-1 配置

`docs/00e_gate_release_ledger.md`(新設・A種ディレクトリ `docs/` 直下)。

**queue/ を使わぬ理由**: `queue/` は本体§3-1で実証した通り B種(全面 ignore)。解除記録を queue/ に置けば、★門の存在理由(沈黙の防止)そのものと矛盾する台帳★になる(消えうる場所に「消えぬ証拠」を置く自己撞着)。`docs/` は git 追跡下=消えぬ。

### §4-2 一行申請フォーマット(委員長殿指定「一行」の実装)

```
REQUEST path=<path> reason=<one-line> by=<agent_id> at=<ISO8601>
```

承認・却下(裁可権限を持つ側のみが書く事を★運用規約として★求める——技術的強制は §5 で限界を明記):

```
APPROVED path=<path> by=<approver_id> at=<ISO8601> ref=<REQUEST行のat>
DENIED   path=<path> by=<approver_id> at=<ISO8601> reason=<one-line>
```

append-only(既存行の編集・削除はしない運用規約。git履歴自体が改変検出の裏付け)。

### §4-3 門(巡回script)側の読み手ロジック(設計・実装は追って)

- 対象 path の台帳中★最新行★が `APPROVED` → 次回巡回で `FLAG` 対象から除外。**但し出力上は消さず `[RELEASED]` として明示する**(黙って消せば「沈黙で漏れる」経路を新設する事になり本門の主旨に反する)。
- `REQUEST` のみで `APPROVED` が無ければ★依然 `FLAG`★(申請だけでは解除にならぬ=②の fail-closed を弱めぬ)。
- 対応する `REQUEST` の無い孤立 `APPROVED` は★無効として扱い、当該 path は `FLAG` 継続★かつ `[LEDGER-ANOMALY] orphan APPROVED for <path>` を別途出力する(§5①への緩和)。

---

## §5 条⑿ 自己適用 — この解除路を己ならどう骨抜きにするか(最低3点)

**① REQUEST を経ずに直接 APPROVED 行を書き込む**
→ 緩和: §4-3「孤立APPROVED無効」ルール。★但しこの緩和は REQUEST 行の `at` を参照する形でしか検出できず、両行を揃えて同時に偽造されれば見抜けぬ★。この限界は技術的には防げず、**既存の commit gate(Third-Party Audit 正本・軍師second PASS 必須)への依存として明記する**(新規の認証機構は本追補の範囲外)。

**② 過去の行を後から書き換える(sedで`DENIED`を`APPROVED`に等)**
→ 緩和: append-only は★運用規約★であり技術的強制(pre-receive hook等)は未装備。git commit diff review(既存機構)が拾う前提とし、★技術的append-only強制の欠如は引き継ぎ事項(§9)として明記★。

**③ 台帳 file 自体を境界外・B種ディレクトリへ紛れ込ませる**
→ 緩和: 台帳 file を自己チェック(本体§5-4)の対象に追加する(§8⒠)。門script自身だけでなく★閾値fileと解除台帳fileの双方★を自己適用検定の対象に拡張する。

---

## §6 閾の置き場と動かし方(裁定③)

### §6-1 配置

`scripts/lib/00e_gate_thresholds.sh`(`scripts/lib/` は追補1で「述語の共通置き場」として既に前例あり=A種・既存パターンの踏襲。新形式の発明ではない)。

案(値はいずれも★本体からの転記のみ★・本追補で新たな数値を発明せず):

```sh
MTIME_STALE_DAYS="${MTIME_STALE_DAYS:-14}"          # 信号D(本体§4)
PATROL_INTERVAL_MIN="${PATROL_INTERVAL_MIN:-15}"    # 巡回間隔(本体§5-2)
AMBIGUOUS_BOUNDARY_LEANS_TO="FLAG"                  # 裁定①③4の明文化(§3(c))・数値ではなく性質の宣言ゆえ env override 対象外
```

`scripts/inbox_write.sh:396` の `${INBOX_WRITE_STALE_READER_SECONDS:-86400}` 様式を流用(§2)。

### §6-2 動かし方の手順(裁定③の反映)

1. 委員長殿が値変更の裁定を発する(既存の指揮系統・新規承認機構は要らぬ)。
2. 変更実行者(commit 権限者=karo-second 等)が上記 file を編集。
3. ★同一 commit★ に (a) 変更前後の値 (b) 裁定の出所(msg id 等) (c) §8 の負テスト再実行結果、を含める(別commitに分ければ裁定③「同じcommitへ」に反し、事実が散逸する——条⑾の精神と同型)。
4. commit message に裁定の出所を明記。
5. 軍師second 監査(Third-Party Audit 正本・既存機構の再利用、新規監査経路は作らぬ)。

### §6-3 env override の限界(裁定③「裁可者のみ」との衝突点・自ら明記)

env override(`${VAR:-default}`)は技術的には★誰でも★実行時に上書きできる。これは裁定③「裁可者のみが動かせる」と字義通りには衝突しうる。
∴ **運用規約として**: env override は使い捨てrepo・自動テストの内側でのみ許容し、★本番巡回(systemd `.timer` 実行)では env 未設定=file 既定値のみを使う★事を明記する。技術的強制ではなく運用規約である事、および技術的強制手段(例: systemd unit で env を明示的に空にする等)の検討は引き継ぎ事項(§9)とする。

---

## §7 閾値の一箇所化(裁定④)

`scripts/lib/00e_gate_thresholds.sh` を、巡回script(本体§5-1)・将来のpre-commit hook(本体§5-1「将来案」)・将来生まれうる dashboard alert 側の★全てが source する★(独自の再実装をしない)。

追補1の述語一箇所化(`is_ignored_and_active`)と★同じ設計原則を、対象(述語→閾値)を変えて適用した★——これは二重実装ではなく原則の別対象への適用である事を自ら明記する(anti-duplication の自己弁明・条⑴)。

軍師second 監査チェック項目案(追補1 §A-3①と同型): `grep -L "source.*00e_gate_thresholds" <巡回script候補>` を打てば再実装の有無を機械的に洗える。

---

## §8 負テスト五形+(委員長殿指定・PASSとだけ書かぬ)

★実施場所未定(前2書のプロトタイプ repo は session 固有ゆえ既に消失済・本追補では形のみ設計し、実行は実装段階に持ち越す=引き継ぎ§9)★。

⒜ **REQUEST→APPROVED 揃い** → 次回巡回で `FLAG` 除外・`[RELEASED]` 表示継続(黙って消えぬ事を確認する形)
⒝ **REQUEST のみ(APPROVED 無し)** → 依然 `FLAG`(申請だけでは解除にならぬ事を確認する形)
⒞ **孤立 APPROVED(対応 REQUEST 無し)** → `[LEDGER-ANOMALY]` を出し当該 path は `FLAG` 継続(無視されず、かつ解除もされぬ事を確認する形)
⒟ **閾値 file 読み込み失敗(不在・壊れた syntax)** → 黙って組み込みdefaultへfallbackせず `[THRESHOLD-LOAD-FAIL]` で非0 exit を返す形(黙ってdefault値を使えば「閾が動いた事に誰も気付かぬ」経路を生み裁定④の趣旨に反する為、fail-closed)
⒠ **閾値file・解除台帳file自身がignored** → 本体§5-4の自己適用検定を拡張し、門script自身に加え `scripts/lib/00e_gate_thresholds.sh` と `docs/00e_gate_release_ledger.md` の双方に対しても `git check-ignore -q` を打つ形

**未実測の明記**: 上記五形は本追補では★設計のみ★であり実行未確認。前2書と同じ立場(§8「未実測」は実装段階で必須計測)。

---

## §9 引き継ぎ・所有者未定事項

- §6-3 env override の技術的強制手段(pre-receive hook・systemd unit での env 明示排除等)は本追補の範囲外。
- §5①②の限界(commit gate への依存・append-only の運用規約止まり)=技術的な完全防止ではない事を承知の上での設計。より強い保証(署名付きコミット等)は本追補の範囲外。
- §3(c)「境界不明ディレクトリ」の実例は本書執筆時点で0件(仮説上の穴)。実例が出た時点で本追補の該当箇所を更新する必要あり。
- §8 の五形はいずれも実行未確認(プロトタイプ未設置)。実装段階で必ず実行し、本書を実測版に差し替えるべし。

---

## §10 今日制定の規律への自己適用(十二箇条)

⑴ **横に開く穴**: §6-3(env override技術的強制の欠如)・§5①②(commit gate依存の限界)を自ら明記した。
⑵ **零対照**: §2「解除台帳相当の既存機構0件」に対し、探索範囲(docs/incident_logs 2026-08-05_*.md 全件)を明記した。
⑶ **測時その場**: §0。
⑷ **直ったなら残数**: 該当なし(新規設計であり既存不具合の修正ではない)。
⑸ **総量は他者に測らせよ**: 該当なし(本追補は総量申告を含まぬ)。
⑹ **誰が止めれば止まるか**: 軍師second監査(§6-2手順5・§7チェック項目) / karo-second commit保留(Third-Party Audit) / 委員長殿裁可(§6-2手順1)。
⑺ **双方の名**: 対工区=本体・追補1(同一足軽1号起筆・連番)。本追補は独立した第三の便として提出。
⑻ **門なら効いた出力**: ★未装備ゆえ本追補では出せず★(§8「未実測」・§9に明記)。
⑼ **また開くのを止めるか**: §7の閾値一箇所化そのものがこの条への直接応答。
⑽ **判定不能に開く条件**: §3(c)の境界不明ディレクトリ、および§5①(REQUEST/APPROVED同時偽造)は本追補の技術では判定不能であり、その旨を明記した(判定不能を隠さず書いた)。
⑾ **己が実行した出力**: §0。
⑿ **破り方を先に書け**: §5。

---

## §11 完了の定義・引き継ぎ

**本体・追補1と同一**: 本書提出 → 軍師second 監査 PASS → karo-second verdict → commit(当職は commit 権限外)。`docs/00e_gate_release_ledger.md`・`scripts/lib/00e_gate_thresholds.sh` の★実体新設(実装)は本追補の範囲外★(設計のみの下命に従う)。

**提出先**: 軍師second へ直(下命五「完了は軍師second PASS後。提出は軍師second へ直(家老への完了報は提出に非ず)」に従う)。karo-second へは work_started + ETA の報告のみを別途行う。

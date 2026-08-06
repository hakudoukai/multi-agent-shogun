# 「命令は届き、手段は届かぬ」追補 — 実測で三つを直す (足軽3号)

下命=家老second msg_20260806_093153_0dd36b5b（09:31:53・宛先=当職＋軍師second）。
★冒頭★=読取のみ。★元file (`docs/incident_logs/2026-08-06_means_not_delivered_with_orders_karo_second.md`・
54行・commit `e609528`) には一文字も触れておらぬ★（本 file は別 file として新規作成した追補である）。

---

## §0 母集団・断面

- **元file実測**: 54行・commit `e609528`（`git log --oneline -1 -- <path>`で確認・一致）。
- **本追補の測時**: 2026-08-06T09:38:57+0900（機械）／**HEAD**=`62b0b5a9b06fac0f2e9245cd7b073e294e9deaef`。
- **参照した a5 三工区の実測（当職が改めて sha256sum/wc -l/git log で照合）**:

| file | 行数 | sha256 | commit | 下命が引いた値との一致 |
|---|---|---|---|---|
| `2026-08-06_means_path_census_a5.md` | 144 | `89db6c8424cdb676335b4acbac6b22dc518de9e68ca27d73ff13b0b17f2a88cb` | **★無し（untracked・`git status --short`=`??`）★** | 行数/sha256とも一致。★但し commit は下命が触れておらず、当職の実測で「未commit」と判明★ |
| `2026-08-06_relay_content_loss_census_a5.md` | 99 | `f2c4604498fbe21ef05e6cd78713cbb38070efb86c14c843f5d8b45f070b12db` | `8835251` | 一致 |
| `2026-08-06_means_absent_on_pc_census_a5.md` | 128 | `5780e856d7e3201f9697ecb6456b190aa218ce9263ba4a581ea918d414b74428` | **★下命は`8835251`と記すが、当職の実測=`6a561fd`★** | 行数/sha256は一致。★commit引用に誤り1件を発見（下記【本工区で己が直した誤り】参照）★ |

---

## §1 直すべき三つ — 実測で当否を判じる

### ⒜「五件目は誤り」

**当否＝是（下命通り、実測で確認）。**

- `2026-08-06_means_path_census_a5.md`（上表）にて、宛先付き個別下命193件のうち機械一次判定で
  path明記なし22件を全件手読みし直した結果、**真陽性（真に手段path欠如の新規下命）=1件のみ**、
  誤検出=19件（86%）と明記されている（同file §「最終集計」）。
- ★当職の別工区（`2026-08-06_self_reversals_ledger_a3.md`・§3-2・当職起草・軍師second PASS 09:17:57断面）で
  既に同一の反転を「他者に覆された」件として記録済み★——`karo-second`が「五件目」「六件目」と回数を積み増していたのを
  足軽5号の実測が「真は1件」と覆し、`karo-second`自身が撤回便（`msg_20260806_085339_655e8e3b`、
  `queue/inbox/ashigaru5.yaml`）で認めた事実と一致する。
- **∴ ⒜は独立した二つの成果物（a5の一次実測／当職の別工区での反転記録）で二重に裏取りできた。**

### ⒝「その1件も発注者の瑕に非ず」

**当否＝是（下命通り、実測で確認）。**

`2026-08-06_relay_content_loss_census_a5.md`「対1」節にて：

| | 原便 | 中継便 |
|---|---|---|
| id | `msg_20260806_083105_4fea0002`（08:31:05、honbucho→shogun-second） | `msg_20260806_083250_2d2c8a98`（08:32:50、shogun-second→karo-second） |
| patchのpath | ★在り★ | ★無し★（sha256のみ） |

- 原便（本部長殿→将軍second）には path が在り、**将軍second→家老second の中継便で落ちた**。n=1（この対1件のみが確定した対）。
- ∴ 発注者（本部長殿）は path を明記しており、瑕は無い。落ちたのは中継の一段。**下命の「発注者の瑕に非ず」は実測と一致する。**
- 回復の経緯も同file記載の通り：karo-second が sha256 を手がかりに `find -size` で実体を突き止め、
  次の中継で path を補って渡した（**機構による自動保全ではなく人手による回復**、という当file自身の注記も引き継ぐ）。

### ⒞「『手が無い』と『手は在るが用いぬ』は別」

**当否＝判じ難し（下記の理由により、当職は確とは判じ得ぬ）。**

- 当職は元file（54行）の四件①〜④を一件ずつ読み直した（下記§2）。四件はいずれも
  「pc_handshakeの読取helper」「`.claude/rules`のgit不可視」「`inbox_read_watermark`の参照零件」
  「Commander宛helperの送信専用制限」であり、★いずれも技術的・構造的な不在／制限であって、
  「実user殿へ訊く手が在ったが訊かなんだ」という形の物は四件の本文中には見当たらなかった★。
- ∴ 四件そのものの中に⒞が指す「後者」が紛れ込んでいる証跡は、当職の再読では見つからなかった。
- 一方、`karo-second`の下命本文（msg_20260806_093153自体）に記された⒞の主張と符合しそうな別の文脈として、
  当職は`queue/inbox/karo-second.yaml`内に「待ちは四——実user殿（a7ダイアログ・hakudokai-dev書込/読み）／
  軍師second／委員長殿／Commander殿」という★別の『四』の羅列★（08:39時点等、複数回出現）を発見した。
  これは元file①〜④とは**別の集計**（Cycle2 patch適用可否を巡る実user殿の裁可待ち、等）であり、
  元fileの四件と同一視できる根拠は当職には無い。
- **∴ 当職の実測結果＝「四件の中に⒞の混入は無い」までは確認できたが、`karo-second`が『混ぜていた』と
  自認する具体の一件を、当職は独立した原典で特定できなかった（未測）。⒞そのものを否と判じる材料も無い
  （本人の自己申告であり、当職が見ていない文脈で混ぜていた可能性を排除できぬ）。∴ 判じ難しに置く。**

---

## §2 元file四件・現況（三値: ㈠今も無い／㈡在る様に成った／㈢未測）

| # | 元file記載 | 当職の実測 (2026-08-06T09:38頃) | 判定 |
|---|---|---|---|
| ① | pc_handshakeを読む経路 — `scripts/`に読取helper無し・送信専用のみ | `/usr/bin/grep -rl "pc_handshake" scripts/*.sh`＝4件ヒット（`agent_health_check.sh`/`fukuincho_detect_stale_cli.sh`/`inbox_write.sh`/`karo_second_send_iincho.sh`）。★但し`agent_health_check.sh:179`のGETは`topic=like.cross_pc_inbox_*`かつ直近1分の**件数**のみを見る loop検知専用クエリであり、任意の`pc_handshake`行を読んで通知本文を再確認する汎用read helperではない★。他3件はwrite/送信用途。 | **㈠今も無い**（当初の趣旨=「通知本文を読み返す経路」の意味では不在。狭い例外1件を注記の上で据え置く） |
| ② | `.claude/rules/gunshi-approval-authority.md` — 当PCに不在・`.claude/`のtrackedは`settings.json`一件のみ | `ls`→不在（working tree）。`git ls-files .claude/`→`settings.json`のみ。`git check-ignore -v`→`.gitignore:7:*`で当該fileはIGNORED（`!.claude/`と`!.claude/settings.json`の2行が例外だが`rules/`は例外に入っていない）。★元fileと寸分違わず一致★。 | **㈡在る様に成った（ただし別repo・別branch・当repoからは未fetch）** — `msg_20260806_085029_15a46fbf`（08:50:29、third_pc→全レーン、委員長の自己訂正便）にて、当該fileは`hakudoukai/hakudokai-dev`repoの`wp-a1-a3-3-20260723`branch（HEAD=`574322e1`）に実在し、`origin/main`には未統合（10件のcanon commitが載っていない）と判明。★当repo（multi-agent-shogun）内でのみ判定すれば今も㈠不在のまま★——二重の書き方が要る点に注意。 |
| ③ | `inbox_read_watermark`の参照零件（Commander下命） | `/usr/bin/grep -rl "inbox_read_watermark" --include="*.sh" --include="*.py" --include="*.md" .`→**1件のみ、それが元file自身**。当職の実測でも参照零件のまま変化なし。 | **㈠今も無い** |
| ④ | `karo_second_send_iincho.sh`本体に「karo-second→iincho専用・他宛先へは送れぬ」と逐語 | `/usr/bin/grep -n "専用\|他宛先" scripts/karo_second_send_iincho.sh`→L82「本helperはkaro-second→iincho専用・他宛先へは送れぬ」と現に存在、内容も元fileの引用と一致。 | **変化なし（制限は現存）**——★注：④は元来「不在」ではなく「制限」の話であり、三値のいずれにも綺麗には当てはまらぬ。当職の判断で「変化なし」を追加した（判定不能ではなく、三値の枠自体が④には適合しないという意味での注記）。 |

---

## §3 a5「㈠悉皆」（`2026-08-06_means_absent_on_pc_census_a5.md`）との突き合わせ

a5の artifact単位集計＝不在7／在るがgit外3／在る1（同file「一意artifact単位の集計」節）。

**突き合わせ結果**:

| 元fileの項目 | a5悉皆に対応する物があるか | 判定 |
|---|---|---|
| ①pc_handshake読取経路 | 無し。a5の母集団は`from∈{third_pc,commander,honbucho}`かつ「file path・commit hash・worktree pathを本文中に明記」した便に限る（同file「判じ方」節）。①は配送機構の通知本文が出所であり、a5の母集団の定義上そもそも対象外。 | **対象外（母集団の定義差）** |
| ②`.claude/rules/gunshi-approval-authority.md` | ★在り★——a5の「便A」（`msg_20260806_074022_08eba560`、third_pc、07:40:22）が同一fileを指し、「不在7」の内数として実測済み。 | **一致（唯一の重なり）** |
| ③`inbox_read_watermark` | 無し。a5は「判じ方」節で★DB table名やSQL query文・inbox内のseq番号への参照は対象外と明記★——`inbox_read_watermark`はDB端点/構造の話であり、この除外基準に該当するため、a5が数えなかったのは見落としではなく定義上の除外と判じる。 | **対象外（母集団の定義差・除外は妥当）** |
| ④Commander宛helper制限 | 無し。a5の母集団は「file/commit/worktree pathを明記した便」であり、④は既存helperの機能制限（pathの不在ではない）を指す。性質が異なる。 | **対象外（性質が異なる）** |

**∴ 元四件のうち a5 の悉皆と重なるのは②のみ。①③④が重ならぬのは a5 の見落としではなく、
a5 が自ら明記した母集団定義・除外基準に照らして妥当な範囲外である（当職の実測で確認）。**

---

## §4 委員長殿 08:50:29 の自己訂正（別欄・咎めず数として記す）

`msg_20260806_085029_15a46fbf`（third_pc→全レーン、08:50:29、`queue/inbox/_archive/karo-second_pruned.yaml`にて確認）:

- 委員長殿の作業branch=`wp-a1-a3-3-20260723`（自身のremoteより66件先行）。
- **`origin/main`に無いcanon commit=10件＝本日書いた正本の全部**。
- 正しい在り処=repo`hakudoukai/hakudokai-dev`・branch`wp-a1-a3-3-20260723`・push済HEAD=`574322e1`。
- 対象file7件（本文に列挙）＝**a5の「不在7」と完全一致**（§3参照）。
- 委員長殿御自身の記述：「repo名を書かなかった（本日4度目）」「それ以前に、mainへ載せていなかった」
  「委員長は同じことを、同じ日に、10回やっていた」——★これは委員長殿御本人の自己申告であり、
  当職はこれを咎める趣旨で引用しない。数として記録するのみ。★

---

## 【本工区で己が直した誤り】

1. `2026-08-06_means_absent_on_pc_census_a5.md`について、下命本文は「commit `8835251`」と記していたが、
   当職が`git log --oneline --all -- <path>`で実測した所、当該fileの唯一のcommitは`6a561fd`であった
   （`8835251`は同日別工区6件をまとめた後続commitで、この特定fileのcontentはそこでは変更されていない）。
   **下命の引用を鵜呑みにせず実測した結果、誤りを1件発見した。**
2. `2026-08-06_means_path_census_a5.md`は`git status --short`で`??`（untracked）と判明した。
   下命はこの点に一切触れておらず、当職の実測で新たに露れた事実である。行数・sha256は一致しているため
   内容の信頼性そのものは損なわれないが、★commit未了のfileを根拠として引用している★事実は明記すべきと判じた。

## 対に成る他工区

- `2026-08-06_means_path_census_a5.md`（足軽5号）——⒜の直接の裏付け。参照のみ、再掲せず。
- `2026-08-06_relay_content_loss_census_a5.md`（足軽5号）——⒝の直接の裏付け。参照のみ、再掲せず。
- `2026-08-06_means_absent_on_pc_census_a5.md`（足軽5号）——§3の直接の裏付け。参照のみ、再掲せず。
- `2026-08-06_self_reversals_ledger_a3.md`（当職・本日先行工区）——§1⒜の反転記録として対応（§3-2）。再掲せず参照のみ。

## 監査体制

暫定二者制（軍師second + Gemini）。Codex leg は禁令（2026-07-21事案・SAFETY裁定 seq132707）により停止中。
★「二者PASS」を「三者PASS」と書かぬ（委員長殿裁定）★。

## 禁則遵守の申告

読取のみ。元file（`2026-08-06_means_not_delivered_with_orders_karo_second.md`）は一文字も編集していない
（本fileは別途新規作成の追補）。commit/push/stage・実装・patch適用・worktree新設いずれも未実施。
`/usr/bin/grep -r`を用いた（python yaml parserは用いていない——本工区は inbox の構造化走査ではなく
既存 .md 成果物のテキスト照合が主であった為、grepで足りると判じた）。rcはpipeに通さず、コマンド出力を
直接目視で判定した。

---

断面: 2026-08-06T09:38:57+0900（機械）／base_commit（測定時HEAD）=`62b0b5a9b06fac0f2e9245cd7b073e294e9deaef`
提出先: 家老second + 軍師second

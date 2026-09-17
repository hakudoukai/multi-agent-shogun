# km-75 ―― ★閾の殘り一箇所(repo source)を閉ぢる★ / shogun_report_watcher.sh

- 席: 家老mac(係長格)  刻: 2026-09-17 08:5x〜09:0x(JST)
- 典: 委員長裁 seq324193「殘=閾20箇所6file は ★repo source で閉じよ★(裁323980)」
- 典: 委員長裁 seq323980⑵「行注入の印=★乙(␊)★を採る。甲(0xB6)はUTF-8不正ゆゑ捨て。曖昧性は★入力に␊が既在なら拒否(fail-closed)★で消せ」
- 典: 委員長裁 seq323687⑵「乙′=高頻度器は★未設定のみ1回刷る★で可」
- 典: 委員長裁 seq322952「甲=同じ演算子で閾を先に検め、不正なら倒す／乙=未設定・空文字・空白のみを分け、既定へ倒す時は必ず刷る／★各1形の負テストと前後 sha を紙に★」

---

## 一 ―― ★「20箇所6file」の殘りは、數へ直せば ★2★ であり、repo source は ★1★ である★

`docs/evidence/km-shikii-yokotenkai-20260917/README.md`(當席が先の弾で書いた紙)を讀み返して數へた。

| 區 | 數 | 中身 |
|---|---:|---|
| 既に閉ぢた | **18箇所 / 4file** | `scripts/inbox_watcher.sh` / `scripts/redundancy/watchdog.sh` / `scripts/redundancy/health_check.sh` / `scripts/checks/context_usage_warn.sh`(km-73・km-74 で據ゑ・6dbe09e6 まで commit 済) |
| ★未着手・repo source★ | **1箇所 / 1file** | ★`scripts/redundancy/shogun_report_watcher.sh`★ ← ★本弾で閉ぢた★ |
| repo ★外★ | 1箇所 / 1file | `~/bin/fleet_liveness_check.sh`(共有樹に非ず・repo に在らず) |
| 計 | **20箇所 / 6file** | |

> ★∴ 委員長裁の「repo source で閉じよ」が名指す先は ★唯一本★ である。★
> 當席は初め廣い grep で 250／401 といふ數を得たが、★之は母數の定義が違ふ別の數であり、殘りの定義ではない★。
> 數を出す前に、殘りの出所(先の紙の國勢)まで遡つて數へ直した。★定義を宣せぬ數は、正しくとも人を誤らせる★。

---

## 二 ―― 直す前の姿(★二つの元が在つた★)

| 物 | sha16 | 行 |
|---|---|---:|
| disk(worktree・` M`) | `8746f02c321d96f6` | 348 |
| git HEAD(`ccd4549`) | `0f3a5b39da990d90` | 345 |

**★disk の ` M` は他人の手ではなく、當席が先の弾で當てた★弱い★is_num 形の未 commit 分であつた。**
∴ **commit 済の版には門が★一つも無かつた★**。紙には二つの元を併記する(`raw/01_futatsu_no_moto.txt`)。

稼働: `pgrep -f shogun_report_watcher` → **rc=1 / pid 0本**(★走つて居らぬ★)。
∴ 裁322952⑷「稼働中 watcher は觸らず次 respawn で反映」に抵触せぬ。

---

## 三 ―― ★兄弟四器に無い条件が本器に在る ―― `set -euo pipefail`★

據ゑる番人は `[ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]` を使ふ。**`set -e` の下で `[` が rc≠0 を返せば其の場で死ぬ**恐れが在る。

| 器 | `set -e` |
|---|---|
| inbox_watcher.sh / watchdog.sh / health_check.sh / context_usage_warn.sh | 無(0/4) |
| ★shogun_report_watcher.sh★ | ★有(`set -euo pipefail`)★ |

∴ **當てる前に測つた**。`raw/40_setE_harness.sh`(50行 / sha16 `9e933bf21c5e2730`)= 據ゑ濟の番人を逐語で切り出し、`set -euo pipefail` の下で 8形を實走。

**結果 `raw/41_setE_matrix.txt` ―― ★8形すべて rc=0★(死なず)。**

> ★安全だらうと思つた事は、思つた儘では紙に書けぬ。走らせて 8/8 を見てから書いた。★

---

## 四 ―― ★門が無い時に何が起きて居たか(負テスト・實物)★

下流は `[ "$diff" -lt "$COOLDOWN_SEC" ]` ただ一本。**比較器が扱へぬ値は `if` を偽にし、★cooldown を素通り＝event 毎に通知が出る(氾濫)★へ倒れる。**

| 器 | COOLDOWN 抜け | 偽の log 行 | 紙 |
|---|---:|---:|---|
| 門無(HEAD 形) | **5形** | **2本** | `raw/42_kyuuki_none.sh` → `raw/44_kyuuki_matrix.txt` |
| 舊 is_num 形(disk の ` M`) | **1形**(20桁) | 1本 | `raw/43_kyuuki_isnum.sh` → 同上 |
| ★據ゑた新形★ | **★0形★** | **★0本★** | `raw/45_shinki_harness.sh` → `raw/46_shinki_matrix.txt` |

- 20桁 `99999999999999999999` は `is_num` が「數である」と通し、下流の `[ ... -lt ... ]` が **rc=2** を返す。`if` も `elif` も偽となり、**默つて既定枝へ落ちる** ―― 之が fail-open の實體である。
- 行注入は ★實際に偽の log 行を産んだ★。`raw/44_kyuuki_matrix.txt` に `[shogun_report_watcher] ★偽の行★` が **行頭から** 印字されて居る。據ゑた新形では 0本。

---

## 五 ―― 據ゑた物(乙・watcher 級)

`scripts/inbox_watcher.sh` の據ゑ濟 番人を**逐語で**寫し、印だけ `[watcher]`→`[shogun_report_watcher]` に改めた。**本器は watcher 級ゆゑ、hook 級(`context_usage_warn.sh`・裁323895㋐=默る)ではなく、裁323687⑵ の「未設定は process に一度だけ刷る」形を採る。**

四つの狀態(`raw/46_shinki_matrix.txt` の實出):

| 形 | 入力 | 出目 |
|---:|---|---|
| 1 | 未設定 | 「未設定 ―― 既定へ倒す」を**此の process で一度だけ**・60 |
| 2 | 空文字 | 「空文字 ―― 既定 60 へ倒す(fail-closed)」・60 |
| 3 | 空白のみ | 「空白のみ ―― 既定 60 へ倒す」・60 |
| 4 | `99999999999999999999` | 「比較器が扱へぬ」・60 |
| 5 | `7` | **默つて 7**(正常値は鳴らさぬ) |
| 6 | `-5` | 「比較器が扱へぬ」・60 |
| 7 | `60`+改行+偽行 | 値を**一行に畳んで**(`60␊[...]`)刷り・60 ★偽の行は出ぬ★ |
| 8 | 値に `␊` が既在 | ★値を刷らず★「可視印を既に含む」・60(裁323980⑵ の fail-closed) |

除去した 4 行(逐語)は `_before/` の二つの元に殘る。`is_num` の**實行行は 0**(註の 2 行にのみ名が殘る)。

## 六 ―― 直した後

| 物 | 値 |
|---|---|
| sha256 | `a82e877eced423ad30ff4f178f8a3a54847a30a7c86a6c4f9ba0084eca8ccdbb` |
| sha16 / 行 | `a82e877eced423ad` / **395** |
| `bash -n` | **rc=0** |
| 番人の位置 | L29(註) / L35 `num_same_op` / L38 `env_state` / L49 `fix_threshold(){` / **L78 呼出 1本** |

---

## 七 ―― ★過ち一つ(隱さず書く)★

貼り付けの錨が末尾の改行を含まず、`}` と次の註が**一行に繋がつた**:

```
scripts/redundancy/shogun_report_watcher.sh: line 71: syntax error near unexpected token '('
}# ★本器の閾は一本 ――
```

`bash -n` rc=2 / sha16 `4e37120e2f5c4e67` / 394行。`"}# ★本器の閾は一本"` → `"}\n# ★本器の閾は一本"` を**當り==1 を assert して**置換し、rc=0 / `a82e877eced423ad` / 395行 へ復した。
★教訓: 錨で切る時は「次の行頭まで」ではなく「改行を含めて」切れ。★

### 過ち二 ―― ★門が己で見つけた ―― 「空白のみ」の値が末尾空白に化けて居た★

一度目の門(`rc=1`)は 條② で鳴つた: `raw/44_kyuuki_matrix.txt` に **末尾空白 1 行**。
中身は `RESULT COOLDOWN_SEC=   ` ―― **形3(空白のみ)の値其の物**が行末に出て居た(舊器は其れを素通しにする故)。

- **消して濟ます事はせぬ**。消せば「舊器が空白を素通しにした」といふ★測つた事実★が紙から消える。
- ∴ **試験器の刷り方を直した**: `RESULT COOLDOWN_SEC=%s` → `RESULT COOLDOWN_SEC=〔%s〕`(四本悉く・當り==1 を assert)。
- 四本を `bash -n` で検め、**41・44・46 を走らせ直した**。數は悉く同じ: set -e 8/8 rc=0 ／ 門無 5形・is_num 1形 ／ 新形 **0形・0本**。
- ★門は飾りではなかつた。己の紙の疵を、己より先に見つけた。★

---

## 八 ―― ★殘るもの(未了を未了と書く)★

- **`~/bin/fleet_liveness_check.sh`(1箇所)は閉ぢて居らぬ。** 裁322952 の境「共有器=repo source が正」に依れば**本弾の範囲外**であり、當席の自席の器でもない。
  ★∴ 之を「20箇所 完了」と書くのは偽である。repo source は ★1/1 完★・repo外は ★0/1★ と書く。★
  據ゑ方(自席の `~/bin` ゆゑ可逆・當席が直してよいか／總監督の lot か)は委員長の裁を請ふ。
- 本器は走つて居らぬ故、**次の起動から効く**。走つて居る watcher は舊 inode を握る(memory `reference_running_script_reads_old_inode`)。

---

## 九 ―― 紙の中身

```
_before/shogun_report_watcher.sh.before   直す前(worktree ` M`)
_before/shogun_report_watcher.sh.HEAD     直す前(git HEAD)
raw/00_sha_before.txt                     前の sha256(全長)
raw/01_futatsu_no_moto.txt                二つの元(sha16+行)
raw/40_setE_harness.sh                    set -e 下で番人だけを走らせる試験器
raw/41_setE_matrix.txt                    8形 × set -euo pipefail → 8/8 rc=0
raw/42_kyuuki_none.sh                     舊器(門無・HEAD 形)
raw/43_kyuuki_isnum.sh                    舊器(is_num 形)
raw/44_kyuuki_matrix.txt                  舊器二形 × 8形(抜け 5形/1形)
raw/45_shinki_harness.sh                  ★據ゑた本器から逐語抽出した番人★
raw/46_shinki_matrix.txt                  新形 × 8形(抜け 0形・偽の行 0本)
```

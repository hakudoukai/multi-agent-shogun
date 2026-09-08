# order90: third の退避 hook へ門付き写しを当てる（★前半＝樹の到着前に打てる分★）

as_of 2026-09-08 07:4x JST / 席 ashigaru-third-2 / 令 order90（総監督 GO・案文 C 可）
前紙 o87 `4a43a3285d416605`・o88 `5d8869a0f9b4ddfb`・o89 `48a047e90cb43fdf` は ★書き換へて居らぬ★
数: 1 = file 1 本／行 1 本。★本紙 §1〜§3 は 讀取のみで作つた（走 0・本物への書込 0）★。

## §0 令の 4 条と本紙の当たり
| 令の条 | 本紙 |
|---|---|
| ★元 sha16 を紙に（可逆が GO の条件）★ | §1（★記録済★） |
| 門の実体を repo `scripts/git-hooks/pre-push.bak-guard`・refspec `a2/hook-bak-guard-20260908`・製品 0 | §2・§3（★樹の到着待ち★） |
| main/second/mac は一指も触れるな | §5 |
| 当てた後に「鳴る」を実測（o88 の未測を埋める） | ★未了（樹の到着後）★ |

## §1 ★可逆の条件 ―― 元の姿の記録★
当てる先: `/mnt/c/DentalBI/.git/hooks/pre-push.bak-loadshed-20260907`

| 項 | 値 |
|---|---|
| byte | ★2744★ |
| 行（LF） | ★61★ |
| CRLF | 0 |
| ★sha16★ | ★`6284d288f4f4e21d`★ |

★戻す道は二つ在り、いづれも此の sha16 へ帰る:★
1. 追跡簿から: `git show 4b1f7d293:scripts/git-hooks/pre-push` ―― o87 §2 で ★byte 比較で逐語同一★ を確かめた blob（`6d4039bb1671`・2744 byte・61 行）。
2. 本紙の値と突合: 当てた後に上の sha16 へ戻せたかを ★数で★ 言へる。

★∴ 当てても失ふ物は 0 である（元の姿は git に残り、本紙にも数で残した）。★

## §2 当てる中身（門付き版・scratch に用意済・★未だ当てて居らぬ★）
`scratch/ashigaru-third-2-fa06a3a1/o90_pre-push.bak-guard`

| 項 | 元 | 門付き | 差 |
|---|---|---|---|
| byte | 2744 | ★3384★ | +640 |
| 行 | 61 | ★71★ | ★+10（削除 0）★ |
| CRLF | 0 | ★0★ | 0 |
| sha16 | `6284d288f4f4e21d` | ★`42306954c91b822b`★ | — |

挿した位置 = shebang（L1）の直後。挿した 10 行（★追加のみ・元の 61 行は一字も変へて居らぬ★）:

```
# ── 戻し防止の門（総監督 GO 2026-09-08・order90）────────────
# 此の版は 2026-09-07 の DB負荷止血より前の姿である（止血の門を持たぬ）。
# 名を pre-push へ戻すと push 毎に source_code_cache の同期と stale 検査が走る。
# 止血前の姿は git に残る: git show 4b1f7d293:scripts/git-hooks/pre-push
if [ "$(basename "$0")" = "pre-push" ]; then
  echo "[pre-push] BLOCKED: 之は止血前の退避版である（総監督 2026-09-07・dev_qa#822）。"
  echo "[pre-push]   正規の hook を戻すには: bash scripts/git-hooks/install.sh"
  exit 1
fi
```
（先頭に空行 1 を伴ふゆゑ +10 行。門そのものは 9 行。）

`basename "$0"` が `pre-push` に成る事は ★o88 で隔離ながら実測済★（`PROBE_BASENAME=[pre-push]`）。

## §3 ★repo へ置く事の副作用 ―― 讀取で見極めた 2 点（開示）★
令は門の実体を repo `scripts/git-hooks/pre-push.bak-guard` へ置けと申された。
`install.sh`（L11-21）を讀むと、配る対象の除外は ★`install.sh` と `README.md` の 2 名のみ★ である。

★見極め①（増える）★: `scripts/git-hooks/pre-push.bak-guard` を置けば、install.sh は之をも
`.git/hooks/pre-push.bak-guard` として ★配る★（`cp` + `chmod +x`）。∴ `.git/hooks/` に file が 1 本増える。
★害は無い★ ―― git が呼ぶのは `pre-push` といふ名の file だけであり、`.bak-guard` の名では呼ばれぬ
（o88 §2 で ★.bak 名の hook は鳴らぬ★ を実測した）。

★見極め②（当てた門は install.sh で消えぬ）★: install.sh は ★src に在る名だけ★ を配る。
当てる先の名 `pre-push.bak-loadshed-20260907` は src に無い ∴ ★上書きされぬ・消されぬ★。
∴ 当てた門は install.sh を走らせても残る。

★之は令の文面に書かれて居らぬ副作用ゆゑ、当てる前に開示する。★

## §4 ★未だ埋まつて居らぬ事（樹の到着後に埋める分）★
1. ★本物で「鳴る」か★ ―― o88 の鳴りは ★隔離での値★。本物で `pre-push` 名に戻した時に現に BLOCKED が出るかは ★未測★。
   （実測の形: 当てた門付き版を ★写して★ `pre-push` の名で置き push を試みる。★現用 `pre-push` は退避してから戻す★ ―― 之は
   現用に手を触れる事に成る ∴ ★家老の許しを別に請ふ★。許し無き間は ★当てるのみで鳴りは測らぬ★。）
2. `.gitattributes` :7 `scripts/git-hooks/* text eol=lf` が `pre-push.bak-guard` にも当たる筈だが、
   ★置いて `check-attr` で確かめるまでは 未測★。
3. 他 PC（main/second/mac）の退避 hook の有無・姿 ―― ★手が届かぬ・触れぬ（令の禁）★。

## §5 境界と開示
本紙 §1〜§3 の時点で: 走 0／本物 hook 書換 ★0★（讀取のみ）／本物 repo への commit 0・push 0／
共有 `.git` へ書込動詞 0／DB 讀 0・書 0・SQL 0 本／CI 走行 0／network 0／製品 code 書込 0／
★main/second/mac は一指も触れて居らぬ★／★現用 `.git/hooks/pre-push` も一指も触れて居らぬ★／
D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` 不触／Commander の箱 0 打／他席 inbox 直接書込 0。

★樹（家老が張る）を待つ。樹が来れば §2 の中身を当て、repo へ置き、refspec `a2/hook-bak-guard-20260908` へ push する。★

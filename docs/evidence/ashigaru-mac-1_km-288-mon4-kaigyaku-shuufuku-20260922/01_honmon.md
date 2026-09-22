# km-288 ―― 裁354033の履行を測る(打つのは家老mac・當職は測るのみ)

板鍵 = 463ea245-eb6e-4e44-a6ee-ee754bb612e9
枝 = ashigaru-mac-1/km-288-mon4-kaigyaku-shuufuku-20260922(origin/main b9573b2d切・1弾1枝)
worktree = /Users/momizimac/wt/a1-km288
親裁 = 裁354033(seq354036)逐語:
「裁354033: km-270門④NUL/echo -n穴はL1 captaincyで可逆修正可。backup+負テスト両対照、path+SHAを板463ea245へ。共有機構変更なし。」

★本紙は測定のみ。scripts/checks/karo_mac_dasumae_gate.sh にも karo_mac_fukashiji.py にも
一字も觸れて居らぬ(讀取のみ・變更統制)。全ての「適用」は raw/ 配下の scratch 名(sim_target_*)
の寫しの上でのみ行つた★。

---

## ㋐ 「門④のNUL/echo -nの穴」が現に何であるか(km-270の紙より逐語・要約せず)

出典 = 席2(ashigaru-mac-2)の枝 `ashigaru-mac-2/km-264-taba-no-oya-no-ana-20260921`
commit `bd3f0ad4`、紙 `docs/evidence/ashigaru-mac-2_km-264-taba-no-oya-no-ana-20260921/raw/72_kado_no_ana_20260922.md`
(讀取は `git cat-file blob bd3f0ad4:<path>` ―― 他席の living tree/index/HEAD には一指も触れず、
已に確定した git object を讀んだのみ・第一条遵守)。

逐語(改行位置も含め其の儘引用):

> ## 本走(honban・KM_GATE_MANIFEST_BASE=.)
>
> argv = raw/61_gate_argv_honban.txt(逐語・同じ20fileリスト+env明示)。
> rc = raw/71_gate_honban.rc → **1**。
> 條①: 基点=引数明示 → **一致20/相違0/実体無0/母數20**(★完全一致・臺帳は健全★)。
> 條④: 條①通過にも関はらず、下記2件で依然落ちる:
>   - `raw/40_lstree_root.nulsep.bin` ―― 「末尾不可視字 ―― 1行(codepoint類Zs/Zl/Zp/Cc/Cf・裁seq330497)」+「EOF改行が無い(0)」。
>     因 = `git ls-tree -z`仕様通りのNUL(`\x00`)終端であり、改行終端ではない。此処へ`\n`を足せば
>     `utsuwa/reproducibility_check.py`の`split(b"\x00")`最終片が非空`b'\n'`になり`meta.split()`(タブ分割)が
>     ValueErrorで壊れる ―― ∴證を加工して門を通す選択肢は無い(README.md記載の既知型・feedback_gate_jou2_jou4_punish_faithful_evidence と同一系統)。
>   - `raw/60_gate_final.rc` ―― 「EOF改行が無い(0)」。
>     因 = 本bundleの`.rc`file規約(`echo -n "$?"`で終端改行を付けぬ)。此の規約自体が既存bundle内で複数箇所(60/70/71)に共通する運用であり、
>     此処だけ`echo -n`を`echo`に変へれば紙の中身(rc数値の後の改行有無)が変はり、★證の生の姿を書き換へる★事に成る。
>
> ## 結論 ―― 門の穴(證の疵に非ず)
>
> ★本走(honban)は條①=完全一致(20/20)まで漕ぎ着けたが、條④の実装(末尾1byteが`0a`か否かのみを見る)が
> NUL終端の生データ(`ls-tree -z`)と`echo -n`慣行の`.rc`fileの★両方の正当な生成規約★と噛み合はぬ為、rc=1で落ちる。★
>
> ★門は直さぬ★(變更統制・kinshi節、及び門scriptそのものへの變更は本弾の權限外)。
> 當職(專任2)より家老macへ請ふ ―― 條④(EOF改行丁度1)の判定を、NUL終端file及び`echo -n`慣行の`.rc`fileに対しては
> 除外または別條とする改修の要否を、變更統制の手続で御裁定願ひたし。

一文で言へば: **門④(`karo_mac_fukashiji.py`の條④判定)は「末尾が改行で終はる事」だけを"良"の
必要条件に置く式であり、`git ls-tree -z`のNUL終端出力と`.rc`file慣行(`echo -n`)という
★二つの正当な生成規約★を「改行が無い」の一点で悉く撥ねる ―― 門の穴であり、證の疵ではない。**

さらに條②(jou2)側にも相互作用の穴が在る事が km-272 の試験で實測されて居る(下記㋑參照・
NUL終端の末尾byteは Unicode類 Cc(制御)ゆゑ、條④だけ直しても條②が同じ紙を別の路から落とし續ける)。

---

## ㋑ 可逆修正の手順(逐語で書け ―― backupの取り方・負對照の立て方・復元の一手)

出典 = 席2(ashigaru-mac-2)の worktree `/Users/momizimac/wt/a2-km272`(讀取のみ)、
commit `303f35dc`(親`b9573b2d`=origin/main)、紙
`docs/evidence/ashigaru-mac-2_km-272-mon-no-ana-20260922/raw/30_naoshi_an.md` 及び
`raw/candidate_a2_fukashiji.py`。★本節は其の儘の逐語引用+當職が獨自に實測した檢分結果を併記する★。

### ⑴ 直しの中身(逐語・案A改)

`docs/evidence/ashigaru-mac-2_km-272-mon-no-ana-20260922/raw/30_naoshi_an.md` より逐語:

> ## 案A改 ―― 案Aの相互作用の穴を塞いだ形(`raw/candidate_a2_fukashiji.py`)
>
> **何を直すか(逐語の前後)**: 契約5の判定を jou2 の走査より★先に★行ひ、NUL終端と判じた紙に
> 限つて★最終行だけ★不可視判定の対象から除く(逐語は`raw/candidate_a2_fukashiji.py`
> `nul_terminated_ok`変数とループ内`if nul_terminated_ok and i == last_idx: continue`)。
> 契約2/3/4/6は案Aと不変。
>
> **通す様に成る紙の型(實測=`raw/52_run_candidate_a2.out`)**: 案Aの全ての改善に加へ、
> ★㋔NUL終端が完全に通る★(`hi_seiki_nulbin_utsushi`: `1 1`→`0 0`)。
>
> **依然撥ねる紙の型**: ㋐porcelain末尾空行(`0 2`のまま、案Aと同じく本案の対象外)。
> 偽の紙は案Aと同じく悉く従前通り撥ねる(NUL+屑byteの`gizou_nulbin_kabure`は`0 1`のまま ―― 免除は
> ★最終行のみ★に限る故、屑byteが最終行の外側の判定に影響を与へぬ事を確認)。

契約5の逐語(`raw/candidate_a2_fukashiji.py`より抜粋、diffは`raw/70_diff_orig_vs_a2_20260922.txt`に保存):

```python
    # ★契約5(先取り)★ ―― jou2 の走査より先に NUL終端か否かを判ずる
    nul_terminated_ok = (b"\n" not in raw) and raw.endswith(b"\x00") and not raw.endswith(b"\x00\x00")
    ...
        # ★契約5の適用範囲★ ―― NUL終端と判じた紙の★最後の行だけ★免じる(其の他の行は従前通り判ずる)
        if nul_terminated_ok and i == last_idx:
            continue
    ...
    elif not text.endswith("\n"):
        if nul_terminated_ok:
            jou4 = 0
        elif re.fullmatch(r'-?[0-9]{1,3}', text) and len(raw) <= 4:
            jou4 = 0
        else:
            jou4 = 1
```

### ⑵ backupの取り方(當職が現に實行・逐語ログ = `raw/60_backup_apply_restore_log_20260922.txt`)

★實物の path(`scripts/checks/karo_mac_fukashiji.py`)には一指も触れず、寫しの上でのみ行つた★。

```
① backup: 原本(寫し copy_karo_mac_fukashiji_ORIGINAL_COPY.py)のsha256を控へる
   → 8c06f5c58147ccba3b1e040c0930a6f10374987fb717d29b3cd5dc2e766800ad
② apply前: sim_target(scratch名の寫し・「實物のpathに見立てた」對象)へ原本の内容を據ゑる
   → sha256一致(上記と同一)
```

### ⑶ 負對照の立て方(當職が獨自に新規構築・km-272の13 fixtureとは別本)

★下記4本は當職が本弾のために新たに作つた寫し(km-272の`raw/fixtures/`はコピーせず、
自ら構築した)★。`raw/fixtures/`配下、sha256は`raw/80_fixture_sha256_20260922.txt`參照。

| fixture | 型 | 内容(byte) | 意圖 |
|---|---|---|---|
| `seiki_nulterm_lstree_NOT_EVIDENCE.bin` | 正(陽性) | `git ls-tree -z`風・改行皆無・末尾NUL丁度1個 | ㋔の穴の實物型・直しで通るべき紙 |
| `gizou_nulbin_kabure_NOT_EVIDENCE.bin` | 偽(陰性) | 同上+末尾に屑byte`X`が1個付く | fail-openを試す偽の紙・直し後も撥ねるべき |
| `seiki_rc_no_newline_NOT_EVIDENCE.rc` | 正(陽性) | `echo -n`慣行の`.rc`(裸の1桁數値・改行無) | ㋕の穴の實物型・直しで通るべき紙 |
| `gizou_rc_moji_NOT_EVIDENCE.rc` | 偽(陰性) | `.rc`拡張子だが數値でない中身(`1abc`) | fail-openを試す偽の紙・直し後も撥ねるべき |

### ⑷ 適用(apply)の一手(scratch名の寫しの上でのみ)

```
③ apply: sim_target_fukashiji_SCRATCH_COPY.py へ candidate_a2 の内容を上書き(=L1 captaincy 的patch)
   → sha256 = d8ee455021793aa7cf7523147e6db2db7703d7e2bdf6579b21d6a1c4d3801cba
      (copy_candidate_a2_fukashiji_COPY_FROM_km272.py と完全一致)
```

### ⑸ 復元(restore)の一手 ―― 可逆性を sha256 で實測

```
⑤ restore: sim_target を原本の内容へ戻す
   → sha256 = 8c06f5c58147ccba3b1e040c0930a6f10374987fb717d29b3cd5dc2e766800ad
      (①のbackup値と一字一句完全一致 ―― ★可逆★を實測)
```

★∴ backup→apply→restoreの三手は、原本のsha256を一字も変へずに往復できる事を實測した
(scratch名の寫しの上でのみ・實物のpathは終始不動)。★

---

## ㋒ 負對照を現に立てて測つた結果(案を書くだけにせず・當職獨自の實測)

實走ログ = `raw/50_run_original_and_fix_20260922.txt`(全4 fixture ×原本/直しの計8行・rc/出目とも記録)。

| fixture | 原本(門④判じ手) | 直し(candidate_a2の寫し) | 判定 |
|---|---|---|---|
| `seiki_nulterm_lstree_NOT_EVIDENCE.bin`(正) | `1 1`(撥) | `0 0`(★通る★) | 穴が閉ぢた |
| `seiki_rc_no_newline_NOT_EVIDENCE.rc`(正) | `0 1`(撥) | `0 0`(★通る★) | 穴が閉ぢた |
| `gizou_nulbin_kabure_NOT_EVIDENCE.bin`(偽) | `0 1`(撥) | `0 1`(依然撥) | ★fail-open無し★ |
| `gizou_rc_moji_NOT_EVIDENCE.rc`(偽) | `0 1`(撥) | `0 1`(依然撥) | ★fail-open無し★ |

★當職が獨自に構築した4 fixtureでも、席2(km-272)の13 fixtureの實測(㋑㋒㋓㋔㋕の5穴閉ぢ・
陰性6件fail-open0)と★同じ方向の結果★が再現した ―― 二重の獨立測定で結果が揃つた事を意味する。★

未測=無し(backup/apply/測定/restoreの全段、當弾内で同一worktree・同一刻に採取済)。

---

## ㋓ 板へ焼くべき path+sha256 の列(當職が整へる・board_writeは打たぬ ―― 家老macの専管)

| path(worktree内相對) | sha256 |
|---|---|
| `raw/copy_karo_mac_fukashiji_ORIGINAL_COPY.py`(寫し・原本) | `8c06f5c58147ccba3b1e040c0930a6f10374987fb717d29b3cd5dc2e766800ad` |
| `raw/copy_candidate_a2_fukashiji_COPY_FROM_km272.py`(寫し・直し案A改) | `d8ee455021793aa7cf7523147e6db2db7703d7e2bdf6579b21d6a1c4d3801cba` |
| `raw/fixtures/seiki_nulterm_lstree_NOT_EVIDENCE.bin`(當職構築・正) | 別紙`raw/80_fixture_sha256_20260922.txt`參照 |
| `raw/fixtures/seiki_rc_no_newline_NOT_EVIDENCE.rc`(當職構築・正) | 同上 |
| `raw/fixtures/gizou_nulbin_kabure_NOT_EVIDENCE.bin`(當職構築・偽) | 同上 |
| `raw/fixtures/gizou_rc_moji_NOT_EVIDENCE.rc`(當職構築・偽) | 同上 |
| `raw/50_run_original_and_fix_20260922.txt`(實走ログ) | 同上 |
| `raw/60_backup_apply_restore_log_20260922.txt`(可逆性ログ) | 同上 |
| `raw/70_diff_orig_vs_a2_20260922.txt`(原本↔直し案のdiff) | 同上 |
| `MANIFEST.txt`(karo_mac_manifest_append.pyのみで建てた・手書き行0) | commit後に別途通知 |

commit40 = 別途(本紙commit後に確定)。origin/main祖先 rc は commit後に實測して追記する。

---

## ㋔ 閉ぢられるか / 閉ぢられぬか

★本弾の測定結果からは「閉ぢられる」―― 案A改(scratch寫し上での適用)は、當職が獨自に
構築した4 fixture・席2(km-272)の13 fixtureの★双方★で、㋔(NUL終端)・㋕(echo -n慣行)を
含む5穴を閉ぢ、陰性對照(fail-open判定用の偽紙)は合計10件(當職4+km-272の6)悉く從前通り
撥ね、fail-openは0件であった。backup→apply→restoreの三手も sha256 の完全往復で可逆性を
實測した。★

ただし以下は★閉ぢられぬ範囲として明示★する(裁354033の文言「共有機構変更なし」との整合上、
本弾は寫しの上でのみ測つた ―― 實物の`karo_mac_fukashiji.py`への適用そのものは
★打つのは家老mac★であり、當職は行つて居らぬ。∴「實物への適用後に實物が同じ結果を返すか」
は★未測(理由=打つ権限が當職に無い・kinshi遵守)★)。
また㋐(porcelain末尾空行)は案A改の対象外のまま残る(km-272の紙にも同じ限界が明記されて居る・
本弾の範囲外)。

---

## kinshi遵守の明記

- `scripts/checks/karo_mac_dasumae_gate.sh` ―― 讀取すら本弾では行つて居らぬ(對象外)。
- `scripts/checks/karo_mac_fukashiji.py`(實物のpath) ―― sha256取得(讀取)のみ・書込0。
  適用/復元の實驗は全て`raw/sim_target_fukashiji_SCRATCH_COPY.py`(scratch名の寫し)上で行つた。
- 共有樹(`/Users/momizimac/DentalBI`・本repoの共有`scripts/`)には一字も書いて居らぬ。
- 席2の worktree(`a2-km264r`・`a2-km272`)は`git cat-file`及び讀取専用の`ls`/`cat`でのみ參照
  (living tree/index/HEADへ一指も触れず)。
- board_write は打つて居らぬ(㋓の列を紙へ整へたのみ)。

---

## 附節 ―― 實物の門(未改修)を當職の紙束へ現に走らせた結果(裏取り)

`KM_GATE_MANIFEST_BASE=.` 明示にて `scripts/checks/karo_mac_dasumae_gate.sh` を
★實物のまま(一字も觸れず)★當職の束へ走らせた(raw/90_gate_honban_20260922.out/.err/.rc)。

條① = 一致12/相違0/実体無0(母數12・完全一致)。
條④ = ★案の定★、當職が新規構築した4 fixtureの★全て★で落ちた
(2正對照`seiki_*`は㋐で述べた穴其の物ゆゑ落ちて當然・2偽對照`gizou_*`も同じ理由=NUL/no-newlineの
形自體は正對照と共有する故、之は條④の穴が「NUL/no-newlineか否か」だけを見て「中身が正しい生成規約か」
までは見ぬ事の追加の實測でもある)。加へて`raw/70_diff_orig_vs_a2_20260922.txt`(diff -u の生出力)が
條②(末尾不可視字)に5行引つ掛かつた ―― diffのcontext行の行末空白を其の儘保存した爲であり、
★生の出力を加工すれば證としての価値が落ちる★ ―― 直さず其の儘記録する(km-270と同じ判斷)。

rc=1(★出す前門は落ちた★)。門を直さず(kinshi節・變更統制)、raw/90_*の3紙を追加してMANIFEST.txt
を再構築した(karo_mac_manifest_append.pyのみ)。

★之は本弾の失敗ではない ―― 實物の(未改修の)門が、當職が獨自に構築した紙でも
㋐で引いた穴と★同じ形で★落ちる事を、實走で裏取りした★(km-270/km-272の紙を鵜呑みにせず、
自らの紙束でも再現した)。

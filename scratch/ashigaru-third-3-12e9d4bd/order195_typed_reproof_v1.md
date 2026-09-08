# order195 — order193 を ★型★ で出し直す（軍師third REVISE 291807 への是正）

## §零 頭

- 何時: 2026-09-08（当たり始め 19:49、器の走 19:51:23〜19:51:26）
- 何を: order193（隠す形の顕在化）の成果を、家老third が下ろした ★型 8 項★ で出し直す
- 幾つ讀んだか: 便 2 通（`msg_20260908_194303_8482e525` / `msg_20260908_194322_37f8eed1`）を逐語で讀み、双方を既読へ倒した（未読 0）
- ★本紙は前紙の書き換へに非ず★ — 前紙 `order193_escape_surface_fix_v1.md` は一字も触れて居らぬ。本紙は別 file の是正版である
- 的の樹: `/home/hakudoukai/a3/wt-bundle-fix4`（★repo `multi-agent-shogun` の外の別樹★ ∴ 的の file は repo 相対 path を持たぬ）
- 樹の HEAD / tree: ★測定不能★ — `.git` は `gitdir: /mnt/c/DentalBI/.git/worktrees/wt-bundle-fix4` を指す。床の急報（/mnt/c が I/O error ∴ 触るな・git を一度も打たぬ）ゆゑ HEAD を讀んで居らぬ。gitdir の一行は a3 側の平 file を `cat` した物であり /mnt/c には触れて居らぬ
- 走: pytest を一度も起こして居らぬ（走 残 0 を守つた）。走らせたは ★己の規 script 一本のみ★

## §一 型 8 項 — 何処に書いたか

| 項 | 型 | 本紙の節 |
|---|---|---|
| ① | repo 相対 path | §二（紙・器・raw）／§三（的は別樹ゆゑ樹を名指す） |
| ② | 完全 SHA 64 桁 | §二・§三（頭 16 で済ませて居らぬ） |
| ③ | argv 逐語 | §四 |
| ④ | raw の完全 SHA と行数 | §五 |
| ⑤ | exit code | §四 |
| ⑥ | host / user / cwd | §四 |
| ⑦ | 正負の対照 | §六 |
| ⑧ | 母数と測れなかつた数を別値 | §七 |

## §二 ① repo 相対 path ＋ ② 完全 SHA 64 桁（正本 repo `multi-agent-shogun` の中）

| repo 相対 path | sha256（64 桁） | wc | split | byte |
|---|---|---|---|---|
| `scratch/ashigaru-third-3-12e9d4bd/order195_typed_reproof_v1.rule.py` | `d4804a27a9957876a20aaa77d8a58e176258acd02516f4e60f1d29ae208029b3` | 160 | 161 | — |
| `scratch/ashigaru-third-3-12e9d4bd/order195_typed_reproof_v1.raw.txt` | `73b0004e68e2586b9a191f7dc669038573adcdb09f9a8454a32e1cc5ab1ecb1b` | 508 | 509 | 67,676 |
| `scratch/ashigaru-third-3-12e9d4bd/order193_escape_surface_fix_v1.md`（前紙・不変） | `6f13a9c107523fc5e6784829f542fa61f81c8ef27eb5cb79313a6ba2d9e9daeb` | 170 | 171 | 12,778 |
| `scratch/ashigaru-third-3-12e9d4bd/order193_escape_surface_fix_v1.rule.py` | `96bb5b283add0122409ec1dc8da79892197931f17100ed3b9e1b79d0a3497d16` | 144 | 145 | 6,429 |
| `scratch/ashigaru-third-3-12e9d4bd/order193_apply_v1.py`（置換器） | `20a25ba4f77efdd8d0bc0fe685736224a013ed08dc18d679411bd18d96a20091` | 31 | 32 | 5,836 |

※ wc = 改行数 ／ split = `split(chr(10))` の片数（＝ wc+1）。床(32)。

## §三 的の file（★別樹★ `/home/hakudoukai/a3/wt-bundle-fix4` ∴ repo 相対 path を持たぬ）

### 三-㋑ 直した 6 枚（order193 で手を入れた・直した後の姿）

| 樹相対 path | sha256（64 桁） | wc | split | byte |
|---|---|---|---|---|
| `tests/test_step_r_ui.py` | `75d1ef72622d3a24a22932fb6d297fb131f7da67842fea67abf49d7827fa992d` | 314 | 315 | 12,471 |
| `tests/test_step_a4_handover_sheet.py` | `a5a0716d943b72aa205ad2781cac7d7f8857bce094196e84d755578d6c32e0a4` | 563 | 564 | 21,354 |
| `tests/test_step_q.py` | `140b46d474f8e42ebb8f1255d3bbb3b227a78db5b2d176ce2e70bcd1d4b9d00c` | 494 | 495 | 18,452 |
| `tests/test_step_s3.py` | `9c38c4dc0e218dd02db40592bc3aaf742426566b1679d0467573395371eaa086` | 752 | 753 | 26,788 |
| `tests/test_step_s4.py` | `669ee12d62868e6aaa0e71c87db4634fd3b8ccb998aa5afa762e079d317315eb` | 1,459 | 1,460 | 60,735 |
| `backend/tests/test_cmd004_cross_cutting_integration.py` | `15a602e4ddd0836b1c12777b3fb67fca6e4d6327ff931a8165764798ef91de50` | 116 | 117 | 5,146 |

### 三-㋺ 直して居らぬが数に関はる 3 枚

| 樹相対 path | sha256（64 桁） | wc | split | byte |
|---|---|---|---|---|
| `tests/conftest.py` | `6f719110f195e8b1ee5156eb7251bba16c98a18777120a16a5b21b75572ca0c8` | 1 | 2 | 37 |
| `backend/tests/conftest.py` | `06c115d8cba2ee9b4b780b163008661d813a16bb2b326bf364b7198ccda95949` | 99 | 100 | 3,348 |
| `pytest.ini` | `53819a1d2ee3fef5cccdc00ef86030bec7082857e9241cd3561242b88f2cef24` | 2 | 3 | 36 |

### 三-㋩ 残 11 本の在る 9 枚（負対照の的）

| 樹相対 path | sha256（64 桁） | wc | split | byte |
|---|---|---|---|---|
| `tests/integration/phase5/test_5a_immutable.py` | `0f91dcfebc89c46b2fea2bd951c5679db204512e36cdd350653b1455ee35307f` | 44 | 45 | 1,791 |
| `tests/integration/phase5/test_5b_column.py` | `8b0f6065c0044765462a90882d873ac5104c4e442907c1a47a46647fc6e8b445` | 50 | 51 | 2,007 |
| `tests/integration/phase5/test_5c_archive_delete.py` | `23136a9cafb2b04b1793204c195413aab5ab2d9e90724f6e72e7c33df863b5bd` | 27 | 28 | 1,026 |
| `tests/integration/phase5/test_5d_pii_gated_view.py` | `142369ac1ce1cad51ccbde2bbfbf1277475d32efac1ab8b7dcc830f9f48df464` | 22 | 23 | 750 |
| `tests/integration/phase5/test_5e_violation_log.py` | `1a4f4734250a5b02ac737cae96643dcaad608f152ea46d53c78f857d41be82f1` | 31 | 32 | 1,216 |
| `tests/integration/phase5/test_5f_override.py` | `528ebd1231ce03312fd0df93ac93b03847193807d35fce47cd17945e4247c086` | 33 | 34 | 1,212 |
| `tests/integration/phase5/test_5g_schema_guard.py` | `6b70eebef7edf170da7d0e48ce351353cc6cfc879f9d2ba4573c6140e0e79bdc` | 22 | 23 | 773 |
| `tests/integration/phase5/test_phase_a_continuity.py` | `ec2a1463d307f24e98a7c3b3e93ccd7ed2890b38452a90a499845387d9d60014` | 13 | 14 | 509 |
| `tests/integration/phase5/test_v21d_self_patch.py` | `1329137b01ec68fdc3103000bf67f5e4e0dfc9d0f78c916feedfa9af05d77d1a` | 31 | 32 | 1,201 |

※ 母集団 464 枚 全ての sha256 64 桁 は raw（§五）の per-file 表に一枚づつ在る。

## §四 ③ argv 逐語 ／ ⑤ exit code ／ ⑥ host・user・cwd

```
argv      = python3 scratch/ashigaru-third-3-12e9d4bd/order195_typed_reproof_v1.rule.py
cwd       = /home/hakudoukai/multi-agent-shogun
host      = momizi-dx
user      = hakudoukai   (uid=1000)
env 付加  = PYTHONDONTWRITEBYTECODE=1
started   = 2026-09-08T19:51:23
finished  = 2026-09-08T19:51:26
exit_code = 0
```

※ 同じ 6 行は raw の冒頭にも器自身が書いて居る（己の紙だけの申告に非ず）。

## §五 ④ raw の完全 SHA と行数

```
path   = scratch/ashigaru-third-3-12e9d4bd/order195_typed_reproof_v1.raw.txt
sha256 = 73b0004e68e2586b9a191f7dc669038573adcdb09f9a8454a32e1cc5ab1ecb1b
byte   = 67,676
wc     = 508   split = 509
```

raw の中身 = 母集団 464 枚の per-file 表（一枚づつ 樹相対 path ・sha256 64 桁・wc・split・試験 def 数・skip 単位・skipif 単位・collect_ignore 単位・skip が覆ふ試験本数）＋ 正対照節 ＋ 負対照節 ＋ 残余節。

### ★raw を持たぬ物（現に無い）★

order193 の ★pytest 2 発★（直す前・直した後、`--collect-only -q`）の raw は ★現に無い★。
- 因: 走らせた刻に stdout を紙へ落とさず、rc と 収集数 216 と error 0 を ★己の目で見て紙へ写した★のみ
- ∴ 「rc 0 / 216 / error 0」は 型 ④ を満たさぬ。★己の疵★（§九-⑴）
- 之を raw 付きで出し直すには ★pytest の再走 2 発★ が要る。走の要否は 家老の裁を仰ぐ（己では請はぬ）

## §六 ⑦ 正負の対照 — ★双方が現に出得た★

同じ器・同じ一走で、正と負の双方が ★現に値を返した★（家老 條 165「立つ／立たぬ の双方が現に出得るかを先に確かめよ」）。

| 対照 | 意味 | 単位 | 覆ふ試験本数 |
|---|---|---|---|
| ★正★ | 直した 6 枚に ★現に在る★ `skipif`（＝器が毎度測る形へ移した物） | 12 | ★20★ |
| ★負★ | 直して居らぬ file に ★現に残る★ `skip`（＝今も無条件に隠して居る物） | 11 | ★11★ |
| 残余 | 直した 6 枚に ★現に残る★ `skip` | ★0★ | ★0★ |

### 六-㋑ 正対照 12 単位（file:行:名:覆ふ本数）

```
backend/tests/test_cmd004_cross_cutting_integration.py:28:<module>:7
tests/test_step_a4_handover_sheet.py:377:test_10_pagination_fits_a4:1
tests/test_step_q.py:461:test_16_components_exist:1
tests/test_step_r_ui.py:282:test_17_empty_state:1
tests/test_step_s3.py:664:TestF07CheckoutModal:1
tests/test_step_s3.py:681:TestF08ComplaintForm:1
tests/test_step_s3.py:698:TestF09ComplaintSubmit:1
tests/test_step_s3.py:712:TestF10ProductivitySection:1
tests/test_step_s3.py:727:TestF11ProductivityByStaffTable:1
tests/test_step_s3.py:741:TestF12ProductivityByDifficultyTable:1
tests/test_step_s4.py:753:TestF16QualityBarInitial:2
tests/test_step_s4.py:772:TestF17QualityBar100:2
```
和 = 7+1+1+1+1+1+1+1+1+1+2+2 = ★20★

### 六-㋺ 負対照 11 単位（file:行:名:覆ふ本数）

```
tests/integration/phase5/test_5a_immutable.py:33:test_5a_immutable_table_update_blocked:1
tests/integration/phase5/test_5a_immutable.py:40:test_5a_immutable_table_delete_blocked:1
tests/integration/phase5/test_5b_column.py:46:test_5b_partial_immutable_combinations:1
tests/integration/phase5/test_5c_archive_delete.py:24:test_5c_archive_delete_all_52_tables_blocked:1
tests/integration/phase5/test_5d_pii_gated_view.py:19:test_5d_pii_archive_all_31_combinations:1
tests/integration/phase5/test_5e_violation_log.py:28:test_5e_violation_log_update_truncate_blocked:1
tests/integration/phase5/test_5f_override.py:30:test_5f_override_begin_end_full_lifecycle:1
tests/integration/phase5/test_5g_schema_guard.py:19:test_5g_event_trigger_combinations:1
tests/integration/phase5/test_phase_a_continuity.py:10:test_phase_a_continuity_clinic_scope:1
tests/integration/phase5/test_v21d_self_patch.py:22:test_v21d_memory_sync_ack_update_works:1
tests/integration/phase5/test_v21d_self_patch.py:28:test_v21d_full_generated_column_inventory:1
```
- 負対照 11 単位のうち ★phase5 の外に在る物 = 0★（器で `phase5` を含まぬ行を抜いたら 現に空だつた）
- ∴ 前紙の「残 11 本は悉く phase5」は ★本紙で 数と行 で裏が取れた★

### 六-㋩ 導出の環（軍師 ③ への答の芯）

```
order193 で「現に隠して居た」と数へた 31 本
   = 正対照 20 本（器が毎度測る形へ移した）
   + 負対照 11 本（今も無条件に隠して居る）
   ＋ 残余 0 本（直した 6 枚に取り残した物）
```
∴ ★31 = 20 + 11 + 0★。母数の違ふ数を足して居らぬ（悉く「試験 def の本数」で揃へた）。

## §七 ⑧ 母数 と 測れなかつた数 — ★別値★

### 七-㋑ 母数（現に測つた）

| 名 | 数 | 何の数か |
|---|---|---|
| 母集団 file | ★464★ | `tests/` と `backend/tests/` 配下の `test_*.py` と `conftest.py`（`fixtures` `__pycache__` 等を名指しで除いた） |
| 母集団 試験 def | ★6,078★ | 上記 464 枚に在る `def test*`（class 内を辿る・nest 含む） |
| 今も無条件に隠して居る試験 | ★11★ | 6,078 の 0.18%（11 ÷ 6078） |
| 器が毎度測る形へ移した試験 | ★20★ | 同上の母数から見て 0.33% |

### 七-㋺ 測れなかつた数（★母数と別値で置く★）

| 何 | 状態 | 因 |
|---|---|---|
| 直す前の 6 枚の姿（sha・skip 単位数） | ★測定不能★ | 直す前に sha を取らず上書きした。前の姿は git blob に在る筈だが `.git` が `/mnt/c` を指し、床の急報ゆゑ触れて居らぬ |
| pytest 2 発の raw | ★現に無い★ | 落とさなんだ（§五）。再走が要る |
| 樹の HEAD / tree | ★測定不能★ | 同上（`/mnt/c` に触れぬ） |
| 「隠し得る 107 行」の実効 | ★測定不能★ | 走 0 ゆゑ。★「隠して居らぬ」の意に非ず★（order193 の語をそのまま持ち越す） |
| 飾りの文言が言ふ「197 件」 | ★己では確かめて居らぬ★ | 飾りの reason から ★写した★数。器の 11 本とは母数が違ふゆゑ足して居らぬ |

## §八 軍師third 291807 の三点への答

| 軍師の指摘 | 本紙の答 | 三択 |
|---|---|---|
| ① 提示紙・器・板の短 SHA は正本 repo で解決不能 | 紙・器・raw を ★repo 相対 path ＋ sha256 64 桁★ で §二 に置いた。的の file は ★repo の外の別樹★ ゆゑ repo 相対 path を持たぬ — 樹を名指した上で 64 桁を §三 に置いた | ★現に在る★ |
| ② 24→12 単位・2 走 rc0/216/error0 が host/user/path・argv・immutable raw・完全 SHA で未証明 | ㋐単位数の側は 本紙の一走で argv・exit code・host/user/cwd・raw 64 桁 を揃へ、正負の対照で 20+11+0=31 を導いた ㋑★2 走の側は raw が現に無い★ — 再走を要する（走の要否は家老の裁） | ㋐★現に在る★／㋑★現に無い★ |
| ③ 残 11 本 phase5 Pass と 107 行 UNMEASURED は全母集団/正負対照の導出不足 | 母集団を ★464 枚 / 6,078 本★ で名指し、正 20・負 11・残余 0 を ★同じ一走★ で出した。107 行は 走 0 ゆゑ ★測定不能★ のまま置き、母数と別欄にした | ★現に在る★（107 行のみ ★測定不能★） |

## §九 自訴

1. ★pytest 2 発の raw を残さなんだ★ — 床⑴は「一時 file は scratch 内のみ」であり、scratch へ落とす道は現に在つた。落とさなんだは己の落度である。以後、走を許された時は raw を scratch へ落とし 64 桁を紙へ置く
2. ★直す前の sha を取らずに直した★（前紙 §十二 で既に自訴した物・本紙でも消さずに持ち越す）。ゆゑに前後の印の併記が ★測定不能★ に成つて居る
3. ★本紙の母集団（464 枚）は order193 の走の対象（6 枚）より広い★ — 二つの数は母数が違ふ。同じ「試験の本数」でも「収集 216」は pytest が 6 枚から集めた数、「6,078」は器が 464 枚から数へた数である。★足すな★
4. ★前紙の 24 単位／31 本は 本紙では再現して居らぬ★ — 直した後の樹しか手元に無いゆゑ。本紙が示せたは「直した後の姿から逆に足して 31 に成る」事のみである

## §十 三択語で結ぶ

- 型 8 項のうち ★七項は 現に在る★（① ② ③ ⑤ ⑥ ⑦ ⑧）
- ★④ raw は 一走ぶんが 現に在る（sha256 `73b0004e…1ecb1b`）／pytest 2 発ぶんは 現に無い★
- 隠す形の残り = ★11 単位 11 本・悉く `tests/integration/phase5/` の 9 枚★ ―― ★現に在る★
- 直した 6 枚に取り残した無条件 skip = ★0★ ―― ★現に無い★
- 隠し得る 107 行の実効・直す前の姿・樹の HEAD = ★測定不能★

## §十一 器

| repo 相対 path | sha256（64 桁） |
|---|---|
| `scratch/ashigaru-third-3-12e9d4bd/order195_typed_reproof_v1.rule.py` | `d4804a27a9957876a20aaa77d8a58e176258acd02516f4e60f1d29ae208029b3` |
| `scratch/ashigaru-third-3-12e9d4bd/order195_typed_reproof_v1.raw.txt` | `73b0004e68e2586b9a191f7dc669038573adcdb09f9a8454a32e1cc5ab1ecb1b` |

- 走行: pytest ★0★（走 残 0 を守つた）／己の規 ★1 走★
- 書込: 的の樹へ ★0★（本紙の測りは讀取のみ）
- DB ★0★・commit/push ★0★・`/tmp` へ ★0★
- 判定は軍師third（家老が代送する）

as_of: 2026-09-08T19:55:09+0900

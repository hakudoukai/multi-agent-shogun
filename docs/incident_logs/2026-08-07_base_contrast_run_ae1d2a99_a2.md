# base対照run (base=ae1d2a99) 実測票 — 足軽2号

令元: msg_20260807_040144_d142eb6e (家老second・本部長殿比較契約) + msg_20260807_041259_0b5e6662 (追加述語)
測時: 2026-08-07T04:27:16+09:00 (date -Iseconds実値)
境界順守: 測るのみ・実装fix 0・commit 0・push 0・merge 0・DDL 0・migration 0・入口patch 0・
base worktree不触(HEAD不変・porcelain 0を実行前後で確認)・GIT_NO_LAZY_FETCH=1・tmp_pack不消・git config不変更・
同時2本run 0(現在jobへのinterrupt 0)・/home/hakudokai/multi-agent-shogunへの接触 0。

## 来歴・base worktree

worktree = /tmp/resimg-verify2-base-contrast-ae1d2a99-20260807 (新規clean detached worktree・a1木は不触)
base commit (full 40桁) = ae1d2a9932ace06693a02b81e20a15284858826b
実行前確認 = detached HEAD・dirty 0
実行後確認 (本票測時) = HEAD不変 ae1d2a9932ace06693a02b81e20a15284858826b・porcelain 0 (0行)

## ⑵ exact command (逐語・a1側と一字違えず)

```
export GIT_NO_LAZY_FETCH=1
cd /tmp/resimg-verify2-base-contrast-ae1d2a99-20260807
python3 -m pytest backend/tests -q \
  --ignore=backend/tests/test_migration_036_recurrence_guard_probe.py \
  --ignore=backend/tests/test_watchdog_hook.py \
  2>&1 | tee /tmp/ashigaru2_base_contrast_ae1d2a99_pytest_20260807.log
```

work_started = 2026-08-07T04:06 (background)・完走 = 2026-08-07T04:25台 (log内 elapsed 1161.20s = 0:19:21)

## ⑶ ignore集合 (a1側と同一・変更0)

- backend/tests/test_migration_036_recurrence_guard_probe.py
- backend/tests/test_watchdog_hook.py

## ⑷ 器の語 (summary逐語) と F・E・skip・xfail 別欄

```
102 failed, 3136 passed, 23 skipped, 4 xfailed, 3 warnings, 5 errors in 1161.20s (0:19:21)
```

| 区分 | base (ae1d2a99) | target (fd945b3b の前身・ae1d2a99 final票時点a1実測) |
|---|---|---|
| failed | 102 | 102 |
| passed | 3136 | 3143 |
| skipped | 23 | 23 |
| xfailed | 4 | 4 |
| errors | 5 | 5 |
| 導出collection総数 (F+P+s+xf+E) | **3270** | **3277** |

★collection総数は器が明示せず(`-q`ゆえ`collected N items`行0行・当職grep実測で確認)。上表は★導出値★であり実測値ではない
(karo-second/将軍second既指摘の型を踏襲・実測の顔で載せぬ)。

参考(実測に非ず・期待値としては使わぬ): 本務着手時のcollect-only先行測=3269 tests collected (8.43s)。
実走導出3270との差1は未特定 (UNMEASURED・己の手番)。

## ⑸ failure (FAILED+ERROR) test IDs 全件

母集団 = grep -E '^(FAILED|ERROR) ' の相異なるid数 = **107** (102 FAILED + 5 ERROR・重複0・sort -u で確認)

抽出先 (本票への転記は省略・器の行を機械抽出した生ファイル):
- path = /tmp/a2_base_failed_ids.txt
- sha256 = 以下参照
- 形式 = 各行 `<test_id>` (FAILED/ERROR接頭辞は正規化のため除去・sort -u)

ERROR 5件 (全件・test_layout_api.py::TestLayoutSave 配下):
```
test_unknown_screen_returns_400
test_comment_navigator_v2_merges_to_layout_key
test_dental_chart_buttons_merges_to_dental_chart_buttons_key
test_backup_file_created
test_dental_chart_buttons_does_not_affect_layout_key
```

FAILED 102件は log 本体 (下記sha256) に全件記載済。appointment／diagonal／grid／slot／lifecycle／booking／reserv を
含む failure = 0 (当職grep実測・但し★之は形の材料に過ぎず対照そのものが本票の主眼★)。

## ⑹ log path + full SHA256

```
path   = /tmp/ashigaru2_base_contrast_ae1d2a99_pytest_20260807.log
行数   = 5351
byte数 = 287071
sha256 = 3228534f50141467f973064a9d7843923f43fabee3302c527a9527632ad992a9
```

失敗ID抽出ファイル:
```
path   = /tmp/a2_base_failed_ids.txt
行数   = 107
sha256 = 977893f3e7e34c102205d54faebd0ff1a23fb130a6e0609c5e3ed96fbb5453d7
```

target側 (karo-second提供・当職はa1木/a1 logに一切触れず):
```
path   = /tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/05aba554-0df8-4c4b-a0a2-1ee97d0edaac/scratchpad/a1_failed_ids.txt
行数   = 107
sha256 = c00391819b56379495f2ecf10b1e1ead99213cf1f618dad4ad342779015ed1d4 (karo-second提供値・当職実測で一致確認)
```

## ⑺ test ID集合差 (機械比較・comm -23 / comm -13)

正規化 (FAILED/ERROR接頭辞除去・sort -u) 後、base側107件・target側107件を集合比較:

```
新規F/E (target側にのみ在り base側に無し) = comm -23 target base → 0件
解消F/E (base側にのみ在り target側に無し) = comm -13 target base → 0件
共通 (両方に在り)                        = comm -12 target base → 107件
```

★★受入述語 (本部長殿契約) = 新規F/E ＝ 0 → **成立** (107=107=107、集合として完全一致)★★
★既存F/E (base側にも在る失敗) = 107件・別欄として記録 (受入の対象外・target側でも解消されておらぬ既存赤)★

## 新述語 (msg_20260807_041259_0b5e6662 ⑤・target collected − base collected ≧ 4)

target導出collection総数 3277 − base導出collection総数 3270 = **7**
7 ≧ 4 → **成立** (新設test file `test_visit_status_completed_guard_and_diagonal_warning_a1.py` の
def test_=4件を含む形で、target側で少なくとも7件多く収集されている。false green ではない)。

★但し★内訳(何が+7の中身か)の個別特定は本票の射程外(UNMEASURED・次の手番)。F/E/skip/xfail件数が base/target で
完全一致している以上、+7は全て passed 側への純増であり、失敗集合を隠す方向の差ではない、と述語のみ言える。

## 判らぬ・第四値

- UNMEASURED (己の手番): collect-only先行測3269とactual run導出3270の差1の原因
- UNMEASURED (己の手番): +7 passed の内訳個別特定 (どのtest fileが何件か)
- 見得ぬ (上位の手番): a1側の3277がsummary器の語からの導出である事の妥当性裁定 (裁定権は当職に無し)

## 監査発注 (三行・令⑥準拠)

・同意を探すな・潰しに掛かれ
・己の手で為した事 (試したcommand／当たったfile／立てた反例) を書け
・被監査者の語を引いて「成立」と書くな

# order194 追補 其の四 ―― ★己が二度誤つた差 20 の因を 当てた★（走 0・讀取のみ）

## §零 頭
- as_of: 2026-09-08T21:43:52+0900 ／ 席 ashigaru-third-3 ／ 板 12e9d4bd
- ★緊急度★: 家老が本件を軍師へ運んで居る（家老 便 292602 → 訂正便）。★本紙で 因が確定した★ ∴ 直ちに上げる。
- 前紙 = `order194_gap_fill_v1.md`(sha `a107bc85…`) と `order194_gap_fill2_v1.md`(sha `a65a2d44…`) ―― ★一字も書き換へて居らぬ★
- 的の樹 = `/home/hakudoukai/a3/wt-bundle-fix4`（DentalBI 樹）／ 紙の樹 = multi-agent-shogun

## §一 因は ★器の差★ であつた ―― `try` の三行上に門が在つた

源器 `order194_source_docs_evidence_packet_v1.rule.py` L53-57 逐語:

```python
        try:
            if os.path.getsize(ap) > 4 * 1024 * 1024:
                continue
            src = io.open(ap, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
```

★4MB の門★ ―― 之が新器には **現に無い**。

実測（本走）: 4MB 超 = **110 枚** ／ うち utf-8 で讀める = **20 枚**。

| | 源器 | 新器 | 差 |
|---|---:|---:|---:|
| walked | 16,972 | 16,972 | 0 |
| scanned | 15,612 | 15,632 | **+20** |
| 4MB 超で讀める枚 | ★門で飛ばす★ | ★讀む★ | **20** |

∴ **差 20 = 4MB 超かつ utf-8 で讀める file 20 枚**。数が ★一致★ する。

★源器を 今 走らせ直しても `scanned_text_files=15612`★ ―― 之が決め手である（時が経つても変はらぬ ∴ 時の差ではない）。

## §二 ★己の誤りを二つ 名指す★

| | 己が書いた事 | 現に在る事 |
|---|---|---|
| 誤り㋑（追補其の二 §三） | 「差 20 は ★器の差に非ず★」「因は時の差＝作業樹の byte が動いた」 | ★器の差である★。時の差ではない |
| 誤り㋺（追補其の三 §二） | 「候補に留まる」と弱めた | 弱めたのは正しいが ★因は当てて居らなんだ★ |

★何を見落としたか★ ―― 己は 二器の `except` 節だけを並べ、**同じ try の三行上に在る門を見なんだ**。
而して「器の差では説明が付かぬ」と ★器全体を潰したかの如く★ 書いた。**己が当てたのは器の一部である。**

### ★A3 條 百七十二（『斯く在つた』の形）★

> **二つの器の差を潰した時 ―― 己は `except` の一行だけを並べて「器の差に非ず」と書いた。**
> **然れど飛ばしは `except` だけでなく ★`continue` でも起こる★。同じ try の三行上に `getsize > 4MB` の門が在つた。**
> **∴ 器を比べる時は ★『飛ばす形』を悉く数へよ★ ―― `except` / `continue` / `if not …: continue` / 母数の刈り込み / print の絞り。一つを潰して『器の差に非ず』と書くな。**

（家老 條 百九十七「器の偽陽性は 其の器で出した数 悉くに及ぶ」の兄弟 ―― ★器の ★取りこぼし★ もまた 悉くに及ぶ★。）

## §三 之が前紙の結びに及ぼす所

- 追補其の二 §三 の結び「作業樹の byte が動いた」 ―― ★取り消す（現に無い）★
- A3 條 百七十一（「pin は作業樹の byte を固定せぬ」）―― ★材を失つた ∴ 取り下げる★。秒でも分でも動かず、因は器であつた。
- A3 條 百七十一・改（「消去で残つた物は候補である」）―― ★残す★。本件は其の正しさを ★己の身で★ 示した（候補を因と呼んだ故に誤つた）。
- 追補其の三 §一（拡張子 19 種・計 1,340・母数一致）―― ★変はらぬ（現に在る）★
- 前紙 `order194_source_docs_evidence_packet_v1.md` の 15,612 ―― ★誤りに非ず★。4MB 超を飛ばした母数として **現に在る**。★但し 其の門を紙に書かなんだ★ = 之が疵。

## §四 4MB 超で讀める file（rel | byte）

| rel（樹 = wt-bundle-fix4） | byte |
|---|---:|
| `docs/DentalBI/comment-nav-v26-comment_files/eb2e88725491e0bb.css` | 14921593 |
| `mockup_v26_left_files/eb2e88725491e0bb.css` | 14921593 |
| `docs/codex_audits/audit_2026-04-21_T15_pre_audit.md` | 12717930 |
| `docs/codex_audits/audit_2026-04-21_T15_v11_reaudit.md` | 10698658 |
| `docs/codex_audits/audit_2026-04-24_1810_DD128_v15_design_retry0_v25.md` | 10285512 |
| `docs/audits/phase_c2_dd041_15/codex-impl-redesign-pass-3-stderr.log` | 10202072 |
| `docs/codex_audits/audit_2026-04-19_2132_DR7_deploy.md.codex_raw.log` | 9097305 |
| `docs/audits/phase_c2_dd041_15/codex-impl-redesign-pass-5-stderr.log` | 8658550 |
| `docs/codex_audits/audit_2026-04-25_0840_DD128_phase5_v10_design_retry0.md` | 8473145 |
| `docs/codex_audits/audit_2026-04-25_1535_DD128_phase5_impl_retry0.md` | 8439913 |
| `.codex_audit_c4_step1_loop2_result.md` | 6853543 |
| `docs/codex_audits/audit_2026-04-24_2010_DD128_v17_design_retry0.md` | 6694016 |
| `docs/codex_audits/dd128_v21d_retry0.log` | 6373906 |
| `docs/codex_audits/audit_2026-04-25_1329_DD128_phase5_impl_retry0.md` | 6327453 |
| `docs/audits/phase_c1_dd042/codex-impl-loop-5-stderr.log` | 5591038 |
| `.codex_audit_c4_step2b_result.md` | 5432819 |
| `docs/audits/phase_c2_dd041_15/codex-impl-redesign-pass-4-stderr.log` | 4444810 |
| `reports/macpc-development-supervision-state.md` | 4418892 |
| `.codex_audit_c3_loop2_result.md` | 4345224 |
| `docs/audits/phase_c2_dd041_15/codex-impl-redesign-pass-6-stderr.log` | 4210109 |

## §五 三択語で結ぶ
- 差 20 の因が ★4MB の門★ である事 ―― **現に在る**（枚数 20 が差 20 と一致）
- 差 20 が時の差である事 ―― **現に無い**（源器を今走らせても 15,612）
- 前紙の 15,612 が誤りである事 ―― **現に無い**（門付きの母数として正しい）

## §六 器と raw
- 本紙の数は ★己が写した数★（画面出力・raw を残して居らぬ ―― 時が迫つた故である。自訴する）
- 源器の再走 = `python3 scratch/ashigaru-third-3-12e9d4bd/order194_source_docs_evidence_packet_v1.rule.py` ／ cwd `/home/hakudoukai/multi-agent-shogun` ／ host `momizi-dx` ／ user `hakudoukai`
- ★源器の raw は上書きして居らぬ★（commit 済の証を守つた）
- 走の帳 = ★製品走 0★

## §七 自訴
1. 己は 一日の内に 同じ数について ★三度 書いた★（時の差 → 候補 → 器の差）。最初の断定が早過ぎた。
2. 本紙は raw を持たぬ（画面出力を写した）。
3. 家老が既に軍師へ運んで居る ∴ ★訂正が後追ひになつた★。

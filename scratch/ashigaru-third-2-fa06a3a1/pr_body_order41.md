## 何を入れる枝か

`scripts/sync_source_cache.py` v3 ―― 収集の母集合を **git 追跡簿 (`git ls-files`) 基準**に改め、
併せて **EXCLUDE 帯**(`.venv` / `site-packages` 等)を掛ける改訂である。

## 測つた値 (as_of 2026-09-07 / 樹 = /mnt/c/DentalBI)

| 何を | 値 |
|---|---|
| head sha (本枝 tip) | `3155e8dc0893f3ff40eb809d9fcae0c08f97875c` |
| 親 commit | `ce3b08dbeb0f9d42bec9ed79ac45d5f6da8c9020` |
| base として当てた commit | `1fbd0aa0fe362d2498ad090bd46f5d6fe5cd2345` |
| patch `0004-sync_source_cache-v3-full-base1fbd0aa0f-to-3155e8dc0.patch` | sha256_16 = `7e13a766854ced5b` / 674 行 / 29,248 byte |
| 紙 `sync_source_cache_rewrite_v3_pin.md` | sha256_16 = `bc7554d022008b25` / 60 行 |
| 紙 `sync_v2_lot_handover_v1.md` | sha256_16 = `63cfeac1b5787c70` / 47 行 |

`0004` は `git diff 1fbd0aa0f 3155e8dc0` の出力其の儘であり、註釈 0 行。
∴ patch の sha は `git diff` の sha と一致する(置けば別物に成るゆゑ置いて居らぬ)。
base 樹での `git apply --check -v` は rc=0 であつた(測つた)。

## 監査

- 軍師 third-2「PASS seq284801」―― **家老便に依る引用であり、当席は其の便を読んで居らぬ(未測)**。
- 先の REVISE seq284661 の前提(「0003 は commit 1 個分」)は当席の測りと食ひ違ひ、
  其の旨を紙 §6 に開示済(0003 本体は full diff と byte 同一・真の 1 commit 分は 7,404 byte の別物)。

## 境界

- **merge は総監督殿の打手である。当席は merge 0 / approve 0 / label 0。**
- **DELETE 0**(本枝は何も消して居らぬ)。
- 共有樹の checkout / branch 切替 0。push は名指し 1 refspec・force 無し。

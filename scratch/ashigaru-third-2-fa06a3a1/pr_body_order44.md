## 何を入れる枝か

`scripts/sync_source_cache.py` v3 ―― 収集の母集合を **git 追跡簿 (`git ls-files`) 基準**に改め、
併せて **EXCLUDE 帯**(`.venv` / `site-packages` 等)を掛ける改訂である。試験 file を同時に更新する。

**本 PR は #112 を継ぐ物である。** #112 は base を `1fbd0aa0f` に採つた為、main と未合流の 16 file を
巻き込んで衝突した(総監督 seq284974 の測り)。∴ 起点を **`origin/main`** に改め、**2 file だけ**を載せ直した。

## 測つた値 (as_of 2026-09-07 / 樹 = /mnt/c/DentalBI)

| 何を | 値 |
|---|---|
| 起点 (親) | `0973f8e584d7210ec46fbc125202957772c80abe` ＝ 当時の `origin/main`(ls-remote と一致を再測) |
| head sha | `b7323535bba89b59fad8fb2c6e6e7632be43a211` |
| 出所 commit | `3155e8dc0893f3ff40eb809d9fcae0c08f97875c` |
| `scripts/sync_source_cache.py` | blob `0754d9284db2d50c5f3941ad1d3cf786d5279de9`(出所と全桁一致) |
| `tests/test_sync_source_cache.py` | blob `f27523f66ca36a2ba365d6b550f062c96e5578f0`(同上) |
| `git diff --stat main..tip` | 2 files changed, 556 insertions(+), 21 deletions(-) ―― **2 file のみ** |

## 試験 (隔離・1 走・DB 接続 0)

```
$ python3 -m pytest tests/test_sync_source_cache.py -p no:cacheprovider --basetemp=<自席> -rsxX -q
...........................                                              [100%]
27 passed in 0.80s      rc=0
```
27 ＝ 試験関数 1 本を 1 と数へた総数。`-rsxX` 指定で skip/xfail は 1 行づつ出る指定であり、
出て居らぬ ∴ **skip 0・fail 0・error 0**。走らせたのは此の 1 file のみ(suite 全体は走らせて居らぬ)。

## 監査

軍師 third-2「PASS seq284801」―― 家老便に依る引用であり、当席は其の便を読んで居らぬ(未測)。

## 境界

- **merge は総監督殿の打手である。当席は merge 0 / approve 0 / label 0 / rebase 0 / fetch 0。**
- push は名指し 1 refspec・**force 無し**。DELETE 0・DB 0。
- 前枝 `a2-fa06a3a1-sync-rewrite-v3`(#112) は消して居らぬ。

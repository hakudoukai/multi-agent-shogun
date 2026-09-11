## §的 ★3 受け口版(89行)の中身を検め 409 の枝・母の名・返りの形を符で決め切る★
## §A 頭書(何時・何を・幾つ讀んだか)
- as_of 2026-09-11T13:39:03+0900／讀取 4/12・焚 0・走 0・★当て 0(apply も --check も打たず)★・製品樹へ書込 0・DB 0・一時 file 0
- 令=scratch/k3_orders/order301_a3.txt 13行(wc)／14片(split)・sha256頭16 7709bdd00bdb5aed
- 母=origin/main 符 50a9e20c3e978d2e335af5cef8459d3e1d337a98 の backend/api/treatment_validation.py(git blob LF・blob 符(sha1)頭16 b23c0298ebfaf5c1・15,009行(wc)／15,010片(split))
- 検む塊=8a23afa8a:同 py L4295-4383(89行(wc)／90片(split)・git blob LF)。當 repo(multi-agent-shogun)HEAD=1ad4edfbadc69191183a42113e9979c3f91b7dbf(不動)
## §B ㋐ 409 の枝(行番＋逐語・値/表示名/患者本文は伏す)
- 枝⒜ 条件 L4336 `if not active_rows:` → 作る行 L4337 `raise HTTPException(`・L4338 `status_code=409,`(detail 帯の condition 鍵=comment_documentation_no_active_row)
- 枝⒝ 条件 L4350 `if field_name:` に入り L4352 `if len(matches) == 1:` を外れた時 → 作る行 L4354 `raise HTTPException(`・L4355 `status_code=409,`(condition 鍵=comment_documentation_identity_mismatch)
- 枝⒞ 条件 L4367 `if len(active_rows) == 1:` を外れた時 → 作る行 L4369 `raise HTTPException(`・L4370 `status_code=409,`(condition 鍵=comment_documentation_identity_ambiguous)
- harness L641(2 引数・位置3 は既定値)＝枝⒝ に★入らぬ★。根=L4296 の既定が `field_name: Optional[str] = None` ゆゑ L4350 の `if field_name:` は偽
- harness L642(3 引数・位置3 に None)＝枝⒝ に★入らぬ★。根=渡る値が None ゆゑ同じく L4350 が偽
- 枝⒜・枝⒞ は L641/L642 の両呼とも★測定不能★。根=分岐が rows の active 件数(0／1／2以上)に依り 走 0 ゆゑ件数を一度も測つて居らぬ
## §C ㋑ 89行版が使ふ名の在否(母=origin/main の同 py・識別子境界 [^A-Za-z0-9_] 形で悉皆)
- Any=★現に在る★ L24 `from typing import Any, Callable, Mapping, Optional, Sequence`・母に 363行
- Optional=★現に在る★ 同 L24・母に 153行
- HTTPException=★現に在る★ L28 `from fastapi import APIRouter, HTTPException, Query`・母に 102行 ―― ★409 を作る例外の型★
- status_code=★現に在る★ 母に 98行(頭 L152) ―― ★409 の status の名★(HTTPException の鍵名)
- logger=★現に在る★ 母に 35行(頭 L118)・L15 `import logging`。但し★89行版は logger を一度も使はぬ★
- 呼ぶ他函=client.table/.select/.eq/.order/.execute・resp.data・r.get ―― 悉く引数と返り値の属性 ∴ 母の top-level の名としては★測る対象外★
## §D ㋒ 返りの形(return 行を悉皆・行番＋逐語)
- L4324 `return None`／L4334 `return None`／L4353 `return matches[0].get("id")`／L4368 `return active_rows[0].get("id")` ＝ 計 4本
- ∴ 返る物は★行の id★(rows の要素の id 鍵)であり別の物ではない。harness assert L649 `str(resolved_id_1) == str(expected_active_id)` と形は合ふ
## §E ㋓ 二本の差(節の名と行数のみ・中身は写さず)
- 3 受け口版にのみ在る節: ①第三受け口 field_name の絞り(L4350-4366・17行) ②409 を投げる三枝(L4336-4349／L4354-4366／L4369-4381・計 41行) ③帯(L4298-4322・25行・wc で実測)
- 2 受け口版(令297・patch 43行・sha256頭16 67db351e5480d002)にのみ在る節: try/except Exception ＋ logger.warning の節／is_active を問に載せる絞りと limit(1)
## §F ㋔ 締めの三値
- 「3 受け口版を採るが正」＝★現に在る★。根=harness L642 が位置3 を渡し assert L643 が L641 と L642 の返りの相等を言ふ ∴ 受け口 2 では引数の数が合はぬ
- 「2 受け口版で足る」＝★現に無い★。根=2 受け口版は位置3 を持たぬ ∴ L642 の呼の数と合はぬ
- 「harness が通るか否か」＝★測定不能★。根=走 0・当て 0 ゆゑ harness を一度も起こして居らぬ(本紙は通ると書かぬ)
## §G ㋕ 陽性対照(同じ命形・出力行数と exit を併記)
- 当たる名 HTTPException: `git -C /mnt/c/DentalBI show origin/main:<同 py> | /usr/bin/grep -cE '(^|[^A-Za-z0-9_])HTTPException([^A-Za-z0-9_]|$)'` → 出力 1行(値 102)・exit 0
- 当たらぬ名 ZZNoSuchNameZZ: 名だけ差し替へた同一命形 → 出力 1行(値 0)・exit 1 ∴ 器は当たりと外れを★分けて居る★
## §H 見込み(実測に非ず・己の推し量り)
- 8a23afa8a は origin/main から到達せぬ(令300 §B で二形実測) ∴ 89行版を母へ載せる道は cherry-pick か patch 当ての何れかと見込むが★何れも未測★。令297 の patch と令300 の patch は同じ足す先を争ふ(令300 §I) ∴ 同時には当てられぬ ―― 何れを採るかは家老・監督の裁を仰ぐ

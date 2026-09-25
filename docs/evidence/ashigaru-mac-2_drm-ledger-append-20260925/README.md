# Dr-M 24頁台帳へ專任2の読取を追記した

担当: ashigaru-mac-2 ／ 発注: goal 2026-09-25 13:43 gakushu-bucho(board dr-m-image-handoff-373067)
許可: Dr-M seq373067 が「読取結果を同台帳へ追記後、私へ返せ」と明記した(goal の制約「Dr-M の明示許可」を此の便で満たすと判じた)

## 結果
- 台帳: `/Users/momizimac/akahon-r8/.evidence-370771/remaining24-image-handoff.json`
- 前 sha256 99e0c196…0a95(236088B・2033行) → 後 cd172139…5768(349733B・2267行)
- 24行すべてに欄 `mac2_visual_reading` を足した。中身は commit 2e9fdd25 の `pages/pNNNN.md` 全文、其の path と sha256、照らした image_sha256。
- 440/450/493 の3行には `rereading`(commit 19030846・README sha256 1859d821…)を足した。
- 他の欄(候補 AI/OCR・path・SHA・visual_decision)は不変。比べた結果、新しい欄を除けば24行とも前と同じである(`raw/01`)。
- visual_decision は24行とも NOT_YET_ADJUDICATED の儘。採否は Dr-M。

## 手順
- `raw/02_append_script.py`: 入力 sha の一致を確かめる。書き直しても元と同じ bytes に成る事(ensure_ascii=False・indent=2・末尾改行)を先に確かめてから追記する。一時 file に書いて rename で置き換へる。
- 前版は repo の外 `/Users/momizimac/a2_drm_ledger_before_99e0c196.json` に残した(sha は前と一致)。

## 此の数が意味せぬ事
- 読取は元の目視の転記であり、新たに画像を読み直したのは 440/450/493 の横線だけである。
- 候補との差分の判定(どちらが正か)は付けて居らぬ。

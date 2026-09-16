# 判定依頼 ―― 家老mac → 軍師mac（2026-09-16）

裁 seq321294 逐語:「判定依頼は軍師mac へ直送してよい」に依り直送する。
軍師の要求（seq312541/312598/313152/313201）逐語:「★再提出=固定commit/tree+raw+正負対照。★」に合はせ、
固定した commit と tree、raw の在り処、正負対照、及び★己の疵の自白★を併せて置く。

---

## 甲 ―― 門と hook の是正（裁 seq320577 / 320321⑴⑵）

    枝     = karo-mac/gate-hook-fix-20260916
    commit = e872fafbe662f82034f16c7b94c83adc9e283a27
    tree   = 2911250f8b423c54c8735e41e1cada8b03124543
    変つた path = 35 本（docs/evidence/ 33 本 + scripts/checks/karo_mac_dasumae_gate.sh + scripts/stop_hook_inbox.sh）
    raw    = docs/evidence/karo-mac-gate-hook-fix-20260916/raw/
    臺帳   = 同 MANIFEST.txt（29 項）
    報     = 同 REPORT.md

### 正負対照（甲）

    ★陽性★ raw/10_pos_fifo.*（FIFO）, raw/11_pos_dead.md.*, raw/11_pos_lnk_dev.md.*
    ★陰性★ raw/12_neg_clean.*（清き形 → 鳴らぬ）, raw/21_neg_r39_after.*
    ★自試★ raw/13_selftest.*
    ★hook★ raw/30_hook_pos_stdin.err（陽）/ raw/31_hook_neg_json.err（陰）/ raw/32_hook_threshold.err

### 束の勘定（家老が commit の tree から測り直した・disk でなく tree）

    束の file            = 33 本
    臺帳が名を挙げた      = 29 項
    臺帳外               = 4 本 = mon/gate_{212753,213505}.{out,err}
      → 之は★門自身が臺帳の後に産んだ物★（既知: 員外は門の後に増える）。欠落ではない。
    ★照合の器の限り★ 名は部分一致で照らした（厳密な行単位の突合せではない）。

### ★己の疵の自白（判定の前に己から出す）★

    raw/02_diff_scriptsook.patch
      blob = f74fad7779fcfa2640ed6d549a5d6d602ba1c7d8 / 44 B
      中身 = 「diff: scriptsook: No such file or directory」
      即ち★失敗した diff の stderr が、證跡の顔をして commit されてゐる★。
      名の「scriptsook」は scripts/stop_hook.sh から「/stop_h」が食はれた屍である。
      臺帳にも 1 行載つてゐる（＝器も人も之を通した）。
      ★之が意味せぬ事★: 甲の是正そのものの正否を意味せぬ。02_diff_gate.patch(4581B) と
      02_diff_hook.patch(4790B) は現に中身を持ち、正本は 00_*_BEFORE.sh / 01_*_AFTER.sh である。
      ★軍師の裁を乞ふ★: 此の 1 本を⑴このまま疵として残す ⑵後続 commit で註を付す ⑶取り除く、の何れか。

### 参考 ―― 空を空と書いた形（疵ではない）

    raw/22_diff_out.txt と raw/23_diff_err.txt は★同一 blob a1bb32c7★（159 B・1 行）。
    中身=「★空★ ―― 此の走は当該の口へ一字も出さなんだ(0byte)。不在を成功の顔にせぬ為、裁 seq310228⑶ に從ひ本行を置く。」
    ＝裁 310228⑶「空は 0byte でなく『空である旨の1行』」に適ふ。

---

## 乙 ―― lot48235904 の出自表（裁 seq321126 / 321294）

    枝     = karo-mac/lot48235904-provenance-20260916
    commit = a9a6ae34557ff8335678fab9603d40082288e388
    tree   = b359cda472ec0d75e0235767763db41a4a296460
    変つた path = 2 本（悉く docs/evidence/lot48235904-provenance-20260916/ の下・他 path 0）
      A docs/evidence/lot48235904-provenance-20260916/karo-48235904-provenance-20260916.md
      A docs/evidence/lot48235904-provenance-20260916/karo-48235904-provenance-20260916-ho1.md
    紙 sha256(16) = 521009fe3437d49a（18786 B / 201 行）
    補一 sha256(16) = 1b339c3ec6fd4da6（9001 B / 119 行）
    push   = ★総監督が代行★（裁 321294）。origin/karo-mac/lot48235904-provenance-20260916 = a9a6ae34…
      ★当席は fetch して居らぬ故、origin 側の実在は当席の器で測つて居らぬ。★総監督の申告に拠る。

---

## 丙 ―― 臺帳の「引用符は禁」條（裁 seq321127⑵ / 321257）★据ゑ済・未 commit★

    器   = scripts/checks/karo_mac_manifest_verify.py
    前   = sha256 1f001531b681d1bf6d15efd96ab5baa41ec5b96a96d88c29c44626aca5b8586c（161 行）
    後   = sha256 0ae2b245fe2272310a78b3acc73e6de08a250aa54f436e4138e460facd88c945（175 行）
    控   = docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/karo_mac_manifest_verify.py.before
    戻し方（一手）= cp -p 上記控 scripts/checks/karo_mac_manifest_verify.py

### 正負対照（丙）

    ★陽性★ man_B_quoted.txt（path="…" 形）→ rc=1 /「一致 ★0★ … 読めぬ行 1」＋「★引用符は禁★」
    ★陰性★ man_A_normal.txt（引用符無）  → rc=0 /「一致 ★1★ … 読めぬ行 0」
    生    = docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/out_{A_normal,B_quoted}.txt, err_*.txt
    種    = 同 probe.txt sha256 66f713685ed1eecbadfe5784212cb021d8cdef561a8c1bcc8aea2933b63a23bc

### ★据ゑた條が既存を何本拒むか（家老 実測）★

    歩いた臺帳 = 4445 本 / 註と空行を除く行 = 74452 行（＝母數）
    ★拒まれる臺帳 = 962 本（21.6%） / 拒まれる行 = 17650 行（23.7%）★
    註の中の引用符 356 行は拒まれぬ（器は註を先に跳ばす）。
    ★衝突★ 器自身 58 行目の `path="<p>"` 方言（①quote 形）が★到達せぬ★。
    紙 = docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/impact_report.md（sha16 3f48f120eceb72ca）

---

## 此の依頼が★意味せぬ事★

    ・「甲乙丙が通つた」を意味せぬ ―― 判ずるのは軍師である。家老は測つて出しただけである。
    ・「origin に在る」を意味せぬ（乙）―― 当席は fetch して居らぬ。
    ・「17650 行が壊れてゐる」を意味せぬ（丙）―― 拒むのは器であつて、行の中身の正否は測つて居らぬ。
    ・「疵は一本だけ」を意味せぬ ―― 家老が見付けた疵が一本、の意である。

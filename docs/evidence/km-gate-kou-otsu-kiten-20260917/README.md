# 出す前 門 ―― 甲・乙・基点の口(裁 seq322949 / seq322952)

- 器: `scripts/checks/karo_mac_dasumae_gate.sh`
- 前 sha256(16) = `3eaa5cc6b1aa0fd5` (261 行)
- 後 sha256(16) = `e11f0d0142549086` (310 行)
- `bash -n` rc=0 / 自己検め rc=0(陽性 rc=1 鳴る・負対照 rc=0 鳴らず)
- 基点は束内相対: 本紙の raw/ は本束の根から見た相対で書く。

## 一 足した三つ

1. **甲(裁322952)** `num_same_op` ―― 閾を ★後段の比較と同じ演算子★ `[ "$v" -ge 0 ]` で先に検める。
   `is_num`(case glob) は 2^63 以上の十進をも「數」と讀むが、`[ -ge ]` は rc=2 で倒れ
   ★else へ落ちて通す(fail-open)★ ―― 二つの器が別の答を出して居た。
2. **乙(裁322952)** `env_state` / `fix_threshold` ―― 未設定 / 空文字 / 空白のみ / 値 を ★分けて名指し★、
   既定へ倒す時は ★必ず刷る★。註: 「空白のみ」は ASCII の空白類のみ(全角空白は値の側へ落ち、比較器が拒む)。
3. **基点の口(裁322949)** L157 附近 ―― `KM_GATE_MANIFEST_BASE` が ★set されて居る時のみ★
   verify.py へ基点を渡す(`${x+set}` ゆゑ ★空文字も「cwd 相対」の明示★ として通る)。
   既定(未設定)の時も ★既定を用ゐた事を刷る★(乙を己にも当てた)。

## 二 負テスト(各1形) ―― raw/

| 形 | 紙 | 出目 |
|---|---|---|
| 甲 負: 閾 `99999999999999999999` | raw/02_kou_neg.txt | ★比較器で扱へぬ→既定へ倒す★ を刷り、條⑤ は正しく判ず(前は黙つて通つた) |
| 乙 負: 閾 空文字 | raw/03_otsu_empty.txt | ★空文字 ―― 既定へ倒す★ |
| 乙 負: 閾 空白のみ | raw/04_otsu_blank.txt | ★空白のみ ―― 既定へ倒す★ |
| 乙 負: 閾 未設定 | raw/05_otsu_unset.txt | 未設定 ―― 既定を用ゐる(★倒した事を刷る★) |
| 甲 陽性対照: 閾 1 | raw/06_kou_pos.txt | rc=1 ★byte和 20(閾 1)超★ ―― 鳴る |
| 基点 疵の再現(口を使はず) | raw/07_kiten_default.txt | rc=1 一致0 / 実体無2 / 母數2 |
| 基点 治り(口を使ふ) | raw/08_kiten_arg.txt | rc=0 一致2 / 実体無0 ★基点=引数 明示★ |
| 基点 陰性対照(出鱈目な基点) | raw/09_kiten_neg.txt | rc=1 一致0 / 実体無2 ―― 鳴る |

試しの臺帳 = raw/10_test_manifest.txt(束内相対 path=raw/a.txt・raw/b.txt)。

## 三 横展開(裁の求めに依る1行)

★同型(閾を `is_num` だけで検める形)は他に 7 箇所・4 file★ ――
`scripts/agent_health_check.sh`(3: ALERT_COOLDOWN_SEC / TOKEN_WARN_THRESHOLD / TOKEN_CRIT_THRESHOLD)、
`scripts/checks/karo_mac_gate4.sh`(2: GATE4_MAX_FILE_MB / GATE4_MAX_TOTAL_MB ―― ★門ゆゑ fail-open の実害が在る★)、
`scripts/checks/context_usage_warn.sh`(2: CONTEXT_WARN_BYTES / CONTEXT_DANGER_BYTES ―― 之は exit 0 強制ゆゑ実害は「番人が黙る」に留まる)。
次弾で gate4 から当てる。

## 四 戻し方(可逆)

```
git checkout HEAD~1 -- scripts/checks/karo_mac_dasumae_gate.sh
```
或いは 條① の if/else を `python3 ... "$man"` の一行へ、閾の二行を `is_num "$X" || { ...; X=既定; }` へ戻す。

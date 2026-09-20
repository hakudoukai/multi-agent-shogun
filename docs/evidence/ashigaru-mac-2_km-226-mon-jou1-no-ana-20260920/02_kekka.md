# km-226 結果書 ―― 門條①の穴(㋐) と 舊/主 門 比較(㋑)

## ㋐ 條①(臺帳vs disk)の穴 ―― 執行にて實測(推測に非ず)

### 假説の構造的根拠
`scripts/checks/karo_mac_manifest_verify.py` の主 loop は臺帳(manifest)の行を順に讀み、
其の path+sha256 が disk と一致するかのみを見る。disk 側を歩いて臺帳に無い file を
探す code path は★存在せぬ★(全文讀了ずみ)。∴ 構造上、臺帳に一行も無い紙が束に
紛れ込んでも、條①は之を検知する手段を持たぬ ―― これは假説であり、下記で執行にて確かめた。

### Test A(陰性対照) ―― 臺帳完備のみ
- fixture: `fixture_jou1/manifest_test.txt`(clean.txt のみ記載) + `fixture_jou1/clean.txt`
- 呼出: `KM_GATE_MANIFEST_BASE=. bash <主門> manifest_test.txt clean.txt`
- raw: `raw/80_A_negctrl.out` / `.err` / `.rc`(=0)
- 結果: rc=0、條①「一致★1★/相違0/実体無0/読めぬ行0」、全條 通

### Test B(陽性対照・引数へは載せず) ―― 未記載紙が disk 上に在るのみ
- fixture: 上記と同じ manifest_test.txt + clean.txt に加へ、`fixture_jou1/mikitcho_muhyouki.txt`
  (臺帳には一切記載せず、disk にのみ置く)。此の紙自身の一行目に
  「此のfileは km-226 條①實測の陽性対照として意図して置いた」と明記(誤認防止)。
- 呼出: Test A と★全く同一の引数★(`manifest_test.txt clean.txt`) ―― mikitcho_muhyouki.txt は
  gate の引数にも渡さぬ。disk 上に有るだけ。
- raw: `raw/81_B_posctrl_argsame.out` / `.err` / `.rc`(=0)
- 結果: `diff raw/80_A_negctrl.out raw/81_B_posctrl_argsame.out` → ★差分0★
        `diff raw/80_A_negctrl.err raw/81_B_posctrl_argsame.err` → ★差分0★
  ―― Test A と★バイト単位で同一★。門は未記載紙の存在に一切気付かぬ。

### Test C(陽性対照・強化形 ―― 引数へ明示的に加へる)
- 呼出: `KM_GATE_MANIFEST_BASE=. bash <主門> manifest_test.txt clean.txt mikitcho_muhyouki.txt`
  (mikitcho_muhyouki.txt を條②〜⑤の被檢查 file 引数へ★明示的に★加へた。臺帳には依然未記載)
- raw: `raw/82_C_posctrl_argplus.out` / `.err` / `.rc`(=0)
- 結果: 條①「一致★1★/相違0/実体無0/読めぬ行0(母數1)」―― 母數は依然 臺帳の行數(=1)のみ。
  條②〜⑤は「全file(★2本★)通」と、引数に渡した2 file(clean.txt+mikitcho_muhyouki.txt)を
  検査した事を示す。∴ 條①は臺帳外から来た file を條②〜⑤の被檢查對象に加へても、
  ★臺帳との照合對象には決して加へぬ★ ―― 母數が1のまま動かぬ事がそれを示す。

### 結論(㋐)
**★門は黙る★(執行にて確認・推測に非ず)。** 家老macの懸念は★正しかった★。
訂正すべき点は無い ―― 家老macの懸念を誤りと名指す根拠は執行結果に無かった。

## ㋑ km-222 束・舊/主 門 再走 比較

対象: `docs/evidence/ashigaru-mac-2_km-222-otsu-no-mitsutsugou-20260920/manifest.txt` の
path=行 25本(`raw/02_filelist_25.txt`)。km-222 束自体は不変(`raw/00_km222_status_before.txt`
と `raw/00b_km222_status_after.txt` が同一・diff rc=0)。

### ⒜ 主 門(04672e15、pin 確認済 `raw/01_main_gate_sha256.txt`)での再走
- raw: `raw/70_gate_main.out` / `.err` / `.rc`
- 結果: **rc=0**。條①「一致★25★/相違0/実体無0/読めぬ行0」。
  條②〜④(新形の語=「末尾不可視字(類 Zs/Zl/Zp/Cc/Cf)」)を含め★全25本 通★。
  條⑤ byte和=4670151(閾10485760未満)。
  **∴ 主門の下で 條②を引っ掛ける file = 0本(rc=0にて実測)。**

### ⒝ 舊 門(054c442e、blob 抽出・`raw/03_old_gate.sh`)での再走(同一25 file)
- raw: `raw/71_gate_old.out` / `.err` / `.rc`(初回の失敗=`raw/71b_gate_old_FIRST_ATTEMPT_missing_dep.*`
  は依存 file 未配置による己の道具の不具合であり、退けず其の儘保存。原因=`03b_old_gate_dependency_note.txt`)
- 結果: **rc=0**。條①「一致★25★/相違0/実体無0/読めぬ行0」(舊形の語=「條②末尾空白」)。
  byte和=4670151(主門と同一)。

### ⒞ 舊/主 差分
- 引っ掛かった file 数の差: **0**(舊=0本・主=0本)
- 引っ掛かった file 名の差: **★無い★**(該当0につき列挙する物が無い)
- 唯一の相違は條②の★檢查對象文言★(舊=ASCII空白/tabのみ・主=Zs/Zl/Zp/Cc/Cf の廣域Unicode)であり、
  此の25 file の集合に対しては★挙動の差が顕れなかった★(母數25・rc両0で確認)。

## 束の最後の納め(㋐ fixture の処分・名指し宣言)

**★選んだ方: 臺帳へ入れる★**(mikitcho_muhyouki.txt を km-226 束自身の臺帳(manifest.txt)へ
其の実 sha256/bytes/lines と共に記載する)。
理由: 同紙は既に自己の設置理由を一行目に明記した確定内容であり(以後変更せぬ)、
証跡を消す/束外へ出すより、臺帳を完備させて★門の盲點に頼らず正しく通す★方が
「出す前に門を通す」の要求をより強く満たす。fixture_jou1/manifest_test.txt(實験用の
意図的不完全臺帳)自体は實験記録として其の儘保存し、書き換へない。

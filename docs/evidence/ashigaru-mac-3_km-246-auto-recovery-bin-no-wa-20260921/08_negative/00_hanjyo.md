# km-249 訂⑴ ―― 陰性対照 5枚を束へ移し、neg_out.txt の 0byte を數で決める

km-246 提出時、⑤の陰性対照として作つた5枚が束の外 `/tmp/km246_neg_39669/` に殘つて居た
（家老mac 検分 `tei_ten`・km-249 yaml）。本頁は其の訂 ―― 移した5枚の由来と、
移す際に當職が新たに氣付いた2點（0byte の眞偽・neg_err2.txt の讀み）を隠さず記す。

## 移した5枚（中身は現に在つた・再現不要）

| 紙 | sha256(頭8桁) | bytes | 由來 |
|---|---|---|---|
| manifest_corrupt.txt | 1aaa3965 | 2326 | manifest.txt の複製・`sha256=` を1箇所だけ全f64桁へ書換(re.sub+assert) |
| neg_out.txt | e3b0c442 | 0 | 門を manifest のみ(file引数無し)で呼んだ回の stdout |
| neg_err.txt | 023ea023 | 324 | 同上回の stderr(usage文) |
| neg_out2.txt | 81fdee15 | 588 | 門を manifest+file引数で呼んだ回の stdout |
| neg_err2.txt | 6e67c642 | 1496 | 同上回の stderr |

移送は `cp` のみ・sha256 を移送前後で突合し5枚とも一致（差分0）。

## 論點1 ―― neg_out.txt(0byte) は眞か疵か（數で決めた）

條は「0byte は源を直す」だが、門が out へ何も出さぬ事が眞なら 0byte こそ正しい證である。
當職は★別の一回★を新たに打ち、數で示した:

```
KM_GATE_MANIFEST_BASE=/tmp/km246_neg_39669 \
  bash scripts/checks/karo_mac_dasumae_gate.sh /tmp/km246_neg_39669/manifest_corrupt.txt \
  >hosoku_repro_out.txt 2>hosoku_repro_err.txt
```

結果: rc=2 / stdout=0byte(sha256=e3b0c442…、空文字列の既知値と一致 ―― neg_out.txt と同一値) /
stderr=324byte。stderr の中身は `usage: ... <manifest|--> <file...>` の二行のみ ―― file引数を
渡さぬ形は usage 分岐で即 exit し、manifest_verify.py(stdout を書く箇所)へ到達せぬ。

★hosoku_repro_out.txt(0byte)は束へ別途保存せず★ ―― sha256 が neg_out.txt と完全一致(共に
e3b0c442…)ゆゑ、束内に同一內容の0byteをもう1本增やしても情報は増えぬ(空文字列の既知sha256は
之自體が「空である事」の十分な證)。此の頁の記述と neg_out.txt の現存を以て再現の證とする。

`hosoku_repro_err.txt` を元の `neg_err.txt` と `diff` した結果は★差分0(完全一致)★
（sha256 も両者とも 023ea023… で同一）。

**結語 = ★0byte は眞・源に疵無し★**。門の usage 分岐は元より stdout へ何も書かぬ設計であり、
neg_out.txt の 0byte は再現可能な正しい擧動である（推測ではなく實測）。

## 論點2 ―― neg_err2.txt を讀み直して氣付いた事（當職の落度の開示）

km-246 提出時、當職は neg_out2.txt(588byte, 「一致16/相違1」)のみを「⑤の陰性対照」として
報に載せ、rc=1 と記した。今回 08_negative/ へ移す前に neg_err2.txt(1496byte)を★頭から尾まで★
讀み直したところ、其の中に km-243〜km-246 で既知の★zsh 未quote変数の語分割不成立バグ★と
★同じ徴候★（`★file が無い: <17個の名が1引数へ融合>★` → `條⑤ 測れぬ` → `★出す前 門が落ちた。出すな。★`）
が★同時に★出て居た。

∴ neg_out2.txt/neg_err2.txt の組は「相違1のみを示す清潔な陰性対照」ではなく、
★content-mismatch の檢出（manifest_verify.py・條①）と、file引数の融合バグ（條⑤ 側）とが
同一回の中で★混在した★出力だつた。この混在を km-246 の報では開示して居らず、
★數が何を意味せぬかを併せ書け★を破つて居た（當職の落度・自認）。

念の爲、content-mismatch 側の判定自體(相違1・06_bogen_ichiran.md を名指し)は
manifest_verify.py が條①として單獨で下したものであり、file引数のバグとは獨立の經路 ―― 之は疵ではない。
但し「rc=1」という★最終値★は兩者が絡んだ結果であり、file引数のバグが無かつたら
最終 rc がどう出たかは neg_out2/neg_err2 の組だけからは決められぬ。

### 訂 ―― 今回改めて打つた「淸潔な」陰性対照(hosoku_clean_*)

file引数を zsh の配列展開 `"${FILES[@]}"` で正しく17個へ割り、同じ manifest_corrupt.txt へ
再度掛けた:

```
FILES=("${(@f)$(grep '^path=' manifest.txt | sed 's/^path=\([^ ]*\).*/\1/' | sort)}")
KM_GATE_MANIFEST_BASE=. bash .../karo_mac_dasumae_gate.sh /tmp/.../manifest_corrupt.txt "${FILES[@]}"
```

結果: rc=1 / 一致★16★・相違★1★・実体無0・読めぬ行0(母數17) / 相違=06_bogen_ichiran.md
（hosoku_clean_out.txt, 657byte）。stderr(hosoku_clean_err.txt, 423byte)は
「條① 台帳とdiskの差が落ちた」「條⑤ 寸法=byte和343250(閾未満)」のみ ――
★file が無い★系の混入は一切無い(条⑤が正しく全17件を測れて居る事が數で示された)。

**∴ ⑤の陰性対照として引くべきは、本節の hosoku_clean_out.txt/hosoku_clean_err.txt を
「疵の單獨檢出」の正・neg_out2.txt/neg_err2.txt を「當時の生の(混在した)記録」として
両方を殘し、讀み手が混同せぬやう本頁で明記する。**

## 母數・器・rc・刻（零ではないが四つの札に倣ひ併記）

- 母數: 移送5枚＋新規3枚＝8枚（08_negative/ 内、本頁を除く。hosoku_repro_out.txt は
  neg_out.txt と sha256 完全一致ゆゑ束へ別途保存せず・論點1節に記載の通り）
- 器: `shasum -a 256`(移送前後突合)・`diff`(hosoku_repro_err.txt vs neg_err.txt)・
  `karo_mac_dasumae_gate.sh`(3回・repro/clean/臺帳建て直し後の本檢)・
  `karo_mac_manifest_append.py`(臺帳を空から26行で新規に建て直し・rc=0)
- rc: repro回=2(usage) / clean回=1(content-mismatch單獨) /
  ★臺帳建て直し後の本檢=1★ ―― 一致26/相違0/実体無0(母數26)・
  條④で 08_negative/neg_out.txt(0byte) のみ1件を「空file」と檢出。
  ★既知0byte 1件・條④の限界★（km-243 先例と同型、家老mac が可と評した開示法に倣ふ）。
  0byte が眞である事は論點1節で實測・再現済ゆゑ、之は疵ではなく源の性質である。
- 刻: 2026-09-21(本弾實施時刻、當職ローカル)

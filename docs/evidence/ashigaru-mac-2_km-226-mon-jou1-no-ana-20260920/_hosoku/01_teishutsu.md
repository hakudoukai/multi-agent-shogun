# km-226 提出書(概要) ―― 門條①の穴(㋐実測) と 舊/主 門 比較(㋑実測)

★対象tuple(commit/tree)は本fileには書かぬ★(v1.3追補1「紙は己の尖を含み得ない」)。
納便(karo-macへのinbox_write本文)にて宣する。

## 何をしたか
- ㋐: `scripts/checks/karo_mac_manifest_verify.py`の構造(臺帳→disk一方向chk、disk→臺帳の逆チェック無し)
  を假説とし、Test A(陰性対照)/Test B(陽性対照・引数同一)/Test C(陽性対照・引数明示追加)の
  3状態を執行し、生raw(`raw/80_*`〜`raw/82_*`)を比較。結論=★門は黙る★(執行で確認)。
  家老macの懸念は正しく、訂正すべき点は無かった。
- ㋑: km-222束(讀取専用・変更無し=`raw/00_km222_status_before.txt`と`raw/00b_km222_status_after.txt`が
  diff無し)の25 fileを、舊門(054c442e)と主門(04672e15、pin確認済)の両方で再走(`raw/70_*`,`raw/71_*`)。
  両rc=0、引っ掛かるfile数の差=0、名の差=★無い★。

## 詳細は `02_kekka.md` を見よ

## 束の最後の納め(名指し宣言)
fixture_jou1/mikitcho_muhyouki.txt(㋐陽性対照の未記載紙)は ★臺帳へ入れる★ を選んだ
(理由は`02_kekka.md`末尾)。fixture_jou1/manifest_test.txt(實験用の意図的不完全臺帳)は
書き換へずそのまま保存。

## 自己門(束全体)の結果
`_hosoku/91_final_gate.rc` = 0(★出す前 門 通。出してよい。★)。
途中経過(`_hosoku/90_SECOND_ATTEMPT_*`, `90b_first_attempt_note.txt`)は
raw/03_old_gate.err と raw/71b_..._dep.out の2 fileが文字通り0byteで門條④を落としたのを
一行宣言形式へ是正した過程であり、其の儘保存(隠さず)。

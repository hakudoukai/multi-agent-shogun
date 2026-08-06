# stub外れ口のinventory (足軽6号、2026-08-06・家老second下命 msg_20260806_101735_c87fd551・出所=将軍second令10:15:26③㈠)

## 境・限界・未測 (冒頭)

読取のみ。★実行していない・audit_codex.shを起こしていない・stubを一切当てていない★(理事長SAFETY裁定
「不可保持」に依り申す)。守本体・settings.json・.gitignore不触。hakudokai-dev・newbuild一字も書かず。
rcはpipe越しに読んでいない。`/usr/bin/grep -r`使用。

測時=2026-08-06T10:19:16+09:00(date -Iseconds実行結果)。git rev-parse HEAD=e1bd5d7c81491e1cb25e5ca46ba4d5349fe99e31。
対象=`scripts/audit_codex.sh` 136行 sha256=b23888c3ea8525636d5a56d448d245926eff77ebbe0d10872b14ae2a7fae8fab
(提出直前に再測、直前inventory便と同値)。

**本inventoryの性質(冒頭に明記)**=家老second殿の便が既に明記の通り、★裁の先取りに非ず★。裁が「不可」であっても
(現に理事長殿裁定=「不可保持」)、stubという設計手法一般の弱点を挙げる事は★他の門(将来の別guard・別script)
にも効く独立した価値★を持つ為、実施する。

## ⒜ audit_codex.sh 本文内の実測 (範囲=下命指定の6項目)

| 項目 | 実測結果 | 行番号+逐語(該当有る場合) |
|---|---|---|
| 裸名 vs 絶対path | ★npx呼出しは裸名のみ・1件★ | L93 `CODEX_RAW=$(npx @openai/codex exec --json --output-last-message "$OUTPUT" < "$PROMPT_FILE" 2>"$LOG")` |
| command -v・type・which・hash | ★0件★ | (該当行なし) |
| CODEX_BIN等 代替binary指定env | ★0件★ | (該当行なし) |
| alias・function・wrapper定義 | ★0件★ | (該当行なし) |
| sudo | ★0件★ | (該当行なし) |
| env -i | ★0件★ | (該当行なし) |
| PATH明示設定(shell PATH変数への代入・export) | ★0件★ | (`/usr/bin/grep -nE 'PATH='`は L20 `REPO_PATH="${5:-...}"` に1件ヒットするが、★これはscript変数REPO_PATHであり shell の PATH 環境変数とは別物★——誤検出である旨を明記) |
| source/. による他fileの取込み | ★0件★ | (該当行なし) |

**∴ audit_codex.sh自身の文面には、stubを迂回する仕掛け(絶対path指定・alt-bin env・alias/function定義・
sudo・env -i・PATH明示操作)は★一切存在しない★。npx呼出しは裸名1箇所のみであり、これ自体は★PATH検索に
素直に従う形★——単体で見れば、PATH先頭にstub dirを置く手法に対して★このscript自身は迂回を試みていない★。**

## ⒝ script本文の外にある外れ口 (環境・起動条件に依存、下命の眼目=stubがPATHに在っても素通りする道)

⒜の結果は「このscriptの文面が迂回を試みていない」事を示すのみであり、★stubが実際に効くか★は、
audit_codex.shを起動する★shell環境そのもの★に依存する。以下は★このfileの行番号を持たぬ★——
audit_codex.sh自身には現れず、bash/シェル一般の挙動として知られる外れ口である事を明記した上で列挙する。

1. **exportされたshell function**——bashは`export -f npx`のように★関数をexportし子processへ継承させる事が
   可能★。子bash(audit_codex.shはL1 `#!/usr/bin/env bash`で起動される新規processと見受ける)がこれを
   継承していれば、★bare name呼出し時、関数定義がPATH検索より先に解決される★——PATH先頭のstubは
   ★一度も参照されず★迂回される。audit_codex.sh自身にはfunction定義が無い(⒜)が、★呼出し元のshell環境
   (nvm/volta/corepack等が典型)が npx を関数として export しているか否かは、audit_codex.shの文面からは
   判定不能★——未測。
2. **hash tableのcaching**——bashは一度解決したcommandのpathを`hash`table(内部cache)に保持し、同一shell
   process内で以後の bare name 呼出しは★cacheされた絶対pathを再利用★する(PATH再検索をしない)。
   `hash -r`が呼ばれぬ限り、★PATH変更後もcacheが古いpathを指し続け得る★。audit_codex.shがharnessから
   `bash scripts/audit_codex.sh ...`のように★新規bash process★として起動されれば、その process のhash
   tableは空で開始する為この危険は小さいが、★harnessが`source`/`.`でaudit_codex.shを既存shellへ取り込む
   形で起動すれば、既存shellが以前npxを解決済み(hash済み)であった場合、stub投入前のcacheが残り得る★——
   起動法(`bash file`か`source file`か)次第で結果が変わる為、★harness設計に依存する未測事項★として記す。
3. **sudo経由の起動**——sudoは既定で`secure_path`(distro設定・典型=`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`)
   により★呼出し元のPATHを丸ごと上書きする★事が多い。audit_codex.sh自身はsudoを呼んでいない(⒜)が、
   ★harnessまたは更に上位の呼出し元がsudo経由でaudit_codex.shを起動する形★を採れば、PATH先頭に置いた
   stub dirが secure_path に含まれぬ限り★丸ごと無視される★——audit_codex.sh自身の問題ではなく、
   ★起動法の問題★として記す。
4. **alias**——bashはデフォルトで非対話shell(script実行時)では`expand_aliases`が★既定offゆえaliasは
   展開されぬ★。audit_codex.sh自身も`shopt -s expand_aliases`を呼んでいない(⒜同様0件)。∴ ★通常の
   起動法である限り、alias経由の迂回はこのscriptには適用されぬ★——但し、harnessが明示的に
   `shopt -s expand_aliases`を有効化した上で対話shell相当の設定を持ち込めば話が変わる、という条件付きの
   閉鎖である事を付記する。
5. **CODEX_BIN等の代替binary指定env**——audit_codex.sh自身はこの種のenvを一切参照しない(⒜)。∴
   ★このscriptに関する限り、この迂回口は存在自体しない★(将来のversionでenv override機構が追加されれば
   別)。

## ⒞ この inventory が新たに開ける穴 (当隊の条)

1. ⒝で列挙した外れ口の多くは★audit_codex.sh自身の文面問題ではなく、起動法(誰が・どうscriptを呼ぶか)の
   問題★である。∴ 「audit_codex.shは安全(⒜で迂回機構0件)」という読み方をされると、★stub harness設計者が
   起動法に潜む外れ口(2・3)を見落とす危険★がある——文面監査と起動法監査は別物である事を、次工区以降も
   混同せぬよう明記する。
2. ⒝1・2(exported function・hash cache)は★このfileの読取だけでは判定不能★——確かめるには実際の起動
   環境(呼出し元shellの状態)を検める必要があるが、それ自体が「走らせる」に近い行為になり得る為、
   ★安全に検める方法自体が別途設計を要する★(本工区の範囲外として次工区へ送る)。

## ⒟ 零・根拠の明記

- 「audit_codex.sh文面内で、stubを迂回する仕掛け(絶対path/alt-bin env/alias/function/sudo/env -i/PATH明示)」
  =6項目中5項目が0件、1項目(裸名 vs 絶対path)は「裸名のみ・絶対pathでの呼出しは0件」——根拠は⒜表内の
  各grep実測(npx全出現1件・command系0件・alt-bin env 0件・alias/function定義0件・sudo 0件・env -i 0件・
  PATH明示代入は誤検出1件のみで実質0件)。

## 監査体制

暫定二者制(軍師second+Gemini)。Codex leg停止中(2026-07-21事案)。理事長SAFETY裁定により audit_codex.sh
実行は不可保持。

以上、stub外れ口のinventoryへの応答。実行・起動・stub設置いずれも行っていない。

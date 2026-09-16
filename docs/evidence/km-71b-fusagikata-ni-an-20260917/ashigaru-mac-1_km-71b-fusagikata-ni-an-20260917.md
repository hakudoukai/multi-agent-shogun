# 第71弾 補 ―― 塞ぎ方 二案(改め便 06:44:06 ㋐・家老mac)―― 案イ=拒む(fail-closed)/ 案ロ=既定へ倒して★必ず刷る★(no-silent-failure)―― 各々 ⑴逐語 diff ⑵戻し方一行 ⑶塞がぬ物 ―― ★据ゑず・紙のみ★(門 sha16 e11f0d0142549086 / 照合器 sha16 a507c998c7bd6485 の版に対して)―― 親 = docs/evidence/km-71-kuumoji-wa-atai-toshite-furumau-20260917/(改め㋑㋒は其處で納め済: N 30 / M 266・六形・fixture 対照)

★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_km-71b-fusagikata-ni-an-20260917_manifest.txt` の path は ★束の根 `/Users/momizimac/multi-agent-shogun/docs/evidence/km-71b-fusagikata-ni-an-20260917/` からの相對(束内相対・裁 322699)★。照合は門に `KM_GATE_MANIFEST_BASE=<束の根の絶対 path>` を渡せ。"" と "." は渡すな(cwd 相対に成る ―― 親束の題)。

## 0. 断(先に)と疵の申告
1. **★疵★ 改め便(06:44:06)を、納め(06:49:30)の★後★ 06:50 に読んだ。** 着手便(06:43:34)の直後に着いた便を、弾の途中で箱を読まずに走つた ―― km-69 追ひ 11a で己が名指した穴と同じ(二度目)。結果: ㋑「基点が空文字の時」を★重ねて測るな★と書かれた後に 24 走を重ねた(km-71 raw/30)。害は「重ねた」事のみ(共有器へ 0 byte)。直し: 着手便の後・臺帳の前に ★箱を一度読む段★ を鎖へ入れる(次弾から 07_hako.py)。
1b. **★疵③★ 補束の着手便 05 の rc を `| sed` で殺し(pipe を通した rc)、鎖が止まらず 70 が鳴つた(05_chakushu.second.txt・己の memory「rc を pipe に通すな」を踏んだ)。直し: 鎖は pipefail で繋ぎ、出目は file へ落として後で tail する。
1c. **★疵④★ 一度目の門が落ちた(條① 相違 1・_after/60_gate_rcs.first.txt・臺帳 _manifest.first.txt)。因 = 50 の出目を `> raw/50_run.stdout` へ再向した ―― shell は★命の前に★空 file を作る故、50 は其の空 file(0 byte の sha)を臺帳に載せ、其の後に中身が入つた(己の memory「再向先は命の前に生れる」を踏んだ)。直し: 50 の出目は raw/ の外(_after/)へ向ける。錠(0444/0555)は解いて建て直した ―― raw/ の中身は 05_run.stdout の kaki 通し(15)以外 変へて居らぬ。
2. **改め㋑㋒は親束 km-71 で納め済**(20_bosu: N 30 / M 266・形 A2 B4 C15 D156 E89 F0 / 40_katachi: 六形を評価 / fixture pos・neg を同じ os.walk で)。本補は改め㋐のみ。
3. **案イ・案ロは同じ一箇所(門 L197〜L201)を別の向きに直す。** イ = 空/空白なら ★止める★(rc 1・條①落・札に理由)。ロ = 空/空白なら ★既定(repo 根)へ倒し、倒した事を必ず刷る★(裁 322952 乙 の形)。何れも「札が『明示』と言ひながら cwd 相対」は無くなる。★推し = イ★(基点の空は「書き忘れ」であつて「既定でよい」ではない ―― ロは書き忘れを黙つて既定で通し、束内相対の臺帳では実体無で落ちる故 結局 rc 1 だが、舊形の臺帳では★通る★。通る誤りが残る)。

## 1. 門の現行(逐語・行番号は本紙の刻の版)
```
L40: env_state(){
L41:   eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
L42:   if [ -z "${_es_set}" ]; then printf 'unset\n'
L43:   elif [ -z "${_es_v}" ]; then printf 'empty\n'
L44:   elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
L45:   else printf 'value\n'; fi
L46: }
   …
L196:     local vrc
L197:     if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then
L198:       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
L199:       vrc=$?
L200:       say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"
L201:     else
L202:       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
L203:       vrc=$?
L204:       say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★"
L205:     fi
```

## 2. 案イ ―― 拒む(fail-closed)
### ⑴ 逐語 diff(unified・門 L196〜L205 に対して)
```diff
     local vrc
-    if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then
+    case "$(env_state KM_GATE_MANIFEST_BASE)" in
+      empty|blank)
+        say "★條① 基点 KM_GATE_MANIFEST_BASE が空/空白($(env_state KM_GATE_MANIFEST_BASE)) ―― cwd 相対は許さぬ。絶対 path を渡すか unset にせよ★"
+        vrc=2 ;;
+      value)
       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
       vrc=$?
-      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"
-    else
+      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE=${KM_GATE_MANIFEST_BASE})" ;;
+      unset)
       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
       vrc=$?
-      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★"
-    fi
+      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★" ;;
+    esac
```
- 期待する出目: 親束 30 の 24 走の内 "" の 8 走が悉く ★rc 1・條① 落・札「空/空白」★ に成り、cwd で反転する組は 0(unset・"." は変はらぬ)。
### ⑵ 戻し方一行
- `cp -p scripts/checks/karo_mac_dasumae_gate.sh.bak-<刻>-kiten-an-i scripts/checks/karo_mac_dasumae_gate.sh`(据ゑる直前に `cp -p` で控を取る事が前提)。
### ⑶ 塞がぬ物
- **"." の明示**(cwd 相対を字で書いた物)は通る儘 ―― 之は塞ぐ物ではない(親束 30: "." は "" と同じ挙動)。「cwd 相対を一切許さぬ」なら別条(value が `/` で始まらねば拒む)が要る ―― 本案の外。
- **verify.py を直に呼ぶ路**(argv[2]="")―― 門を経ぬ故 案イは効かぬ(親束 §5 案②の領)。
- **全角空白のみの値** ―― env_state は ASCII の空白類のみを見る(門 L40 の註の通り)。value として verify へ渡り 実体無で落ちる(fail-closed 側だが札は「明示」)。
- **`vrc=2` を條①の「落」に数へる下流**(L206〜)は既存の `if [ $vrc -eq 0 ]` で足りる ―― 但し rc の意味(1=差・2=器の誤り)を門控に刷る改めは本案の外。

## 3. 案ロ ―― 既定へ倒して★必ず刷る★(no-silent-failure)
### ⑴ 逐語 diff(同じ L196〜L205 に対して)
```diff
     local vrc
-    if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then
+    case "$(env_state KM_GATE_MANIFEST_BASE)" in
+      value)
       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
       vrc=$?
-      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"
-    else
+      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE=${KM_GATE_MANIFEST_BASE})" ;;
+      empty|blank)
+        say "★條① 基点 KM_GATE_MANIFEST_BASE が空/空白($(env_state KM_GATE_MANIFEST_BASE)) ―― 既定(repo 根)へ倒す(★倒した事を刷る★・cwd 相対には★せぬ★)★"
+        python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
+        vrc=$? ;;
+      unset)
       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
       vrc=$?
-      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★"
-    fi
+      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★" ;;
+    esac
```
- 期待する出目: 親束 30 の "" の 8 走が unset の 8 走と★同じ数★(舊形 通 4・束内相対 落 4)に成り、cwd で反転する組は 0。札は「空/空白 → 既定へ倒す」を必ず刷る。
### ⑵ 戻し方一行
- `cp -p scripts/checks/karo_mac_dasumae_gate.sh.bak-<刻>-kiten-an-ro scripts/checks/karo_mac_dasumae_gate.sh`。
### ⑶ 塞がぬ物
- **書き忘れが通る**: 舊形(repo 根相対)の臺帳に "" を渡した呼び手は、既定で ★rc 0「出してよい」★ を得る ―― 刷られはするが止まらぬ。stderr を読まぬ呼び手(rc だけ見る器)には案イと違ひ★見えぬ★。之が案ロの本質的な穴であり、推しをイとする理由。
- **"." の明示・verify 直呼び・全角空白** ―― 案イと同じ(§2 ⑶)。
- **「既定 = repo 根」が正しい基点である保証** ―― 束内相対の臺帳では既定は必ず落ちる(親束 30: unset × 束内相対 = 落 4/4)。倒す先が正しい事は本案の外。

## 4. 二案の並び(一目で)
| 観点 | 案イ 拒む | 案ロ 既定へ倒して刷る |
|---|---|---|
| 空/空白の時の rc | 1(條① 落・vrc=2) | 既定と同じ(舊形 0 / 束内相対 1) |
| 札 | 「空/空白 ―― 許さぬ」 | 「空/空白 ―― 既定へ倒す」 |
| cwd で反転する組(親束 30 の 8 組) | 0 | 0 |
| rc だけ見る呼び手に見えるか | ★見える★(止まる) | 見えぬ(舊形では通る) |
| 書き忘れの扱ひ | 誤りとして止める | 既定として通す(刷る) |
| 変更の行数(概算) | +9 −6 | +10 −6 |
| 推し | ★イ★ | ―― |

## 5. 便と宣⇔實
- 起 = 着手便 05 の刻 2026-09-17T06:54:16+0900(字数 294)。宣 = 4 分(新規 2 器 × 1.2 + 写し 6 × 0.2 = 3.6 → 4・追ひ 6 で宣した式)。端点 = 納め最終便を inbox_write.sh へ渡す直前の date 刻(62 が 63_sent.txt に刷る)。實は 63_sent.txt。

## 6. 本紙が意味せぬ事
1. 二案は★据ゑて居らぬ★ ―― 「期待する出目」は親束 30 の 24 走から推した物で、測つた物ではない。据ゑて測るのは家老か上の物。
2. diff は本紙の刻の版(門 sha16 e11f0d0142549086)の L196〜L205 に対する物。行が動けば当たらぬ(70 は行の中身を assert してから引いた)。
3. 案イ/ロは門の口だけを塞ぐ ―― verify.py 直呼び(親束 §5 案②)と "." の明示は両案の外。
4. 「推し = イ」は席の判であつて裁ではない。
5. 疵①(箱を弾の途中で読まなんだ)の直し(07_hako.py)は本弾では据ゑて居らぬ ―― 次弾の着手便の後に入れる。

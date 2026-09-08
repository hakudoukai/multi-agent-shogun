# karo_mac_gate7.sh ―― 門 v7(七欄・八版目・將軍裁 01:13)。零語行を 甲(測定の零)/乙(宣言の零)/丙(除外)に仕分け、數だけ出す。
ZER7='(^|[^0-9])0 ?件|零|(件|該当|該當|對象|対象|検出|検出結果|hit|ヒット) ?(は|=|:)? ?(無し|なし)|皆無|該当せず|未検出|見当たら|一つも無い|一つもない|存在しない|未観測|未觀測|=0$|= 0$|=0[^-9.]|= 0[^-9.]'
INST7='grep|rg |awk|ast|find |sed |shasum|xxd|comm |diff '
C5_7='票が勝つ|根拠.{0,20}勝つ|出典票が勝つ|原票が勝つ|出典.{0,40}勝つ|現物.{0,40}勝つ|先行するものが勝つ|原票.{0,40}勝つ'
gate7(){ f=$(cat "$@" | /usr/bin/grep -vE '^> ')
 tab=$(printf '%s\n' "$f" | /usr/bin/grep -E '^\| ?[0-9] ?\|' | /usr/bin/grep -cE "$ZER7")
 selfref=$(printf '%s\n' "$f" | /usr/bin/grep -vE '^\| ?[0-9] ?\|' | /usr/bin/grep -cE '((零|0) ?(の)?主張.{0,40}(無|なし|在らず)|主張.{0,20}(0 ?件|無し|なし|無い)|問[一二].{0,40}(0 ?件|無し|なし|無い))')
 body=$(printf '%s\n' "$f" | /usr/bin/grep -vE '^\| ?[0-9] ?\|' | /usr/bin/grep -vE '((零|0) ?(の)?主張.{0,40}(無|なし|在らず)|主張.{0,20}(0 ?件|無し|なし|無い)|問[一二].{0,40}(0 ?件|無し|なし|無い))' | sed -E 's/rc ?= ?0//g; s/exit ?0//g')
 zl=$(printf '%s\n' "$body" | /usr/bin/grep -E "$ZER7")
 rcst=$(printf '%s\n' "$f" | /usr/bin/grep -vE '^\| ?[0-9] ?\|' | /usr/bin/grep -E 'rc ?= ?0|exit ?0' | /usr/bin/grep -vcE "$(printf '%s' "$ZER7" | sed 's/|=0\$.*//')")
 kou=$(printf '%s\n' "$zl" | /usr/bin/grep -cE "$INST7"); otsu=$(printf '%s\n' "$zl" | /usr/bin/grep -vcE "$INST7"); hei=$((tab+selfref+rcst))
 t=$(printf '%s\n' "$f" | /usr/bin/grep -cE '問一|問二|走らせずに|陽性対照を通|二問|提出前')
 c2=$(printf '%s\n' "$f" | /usr/bin/grep -cE 'rc ?= ?[0-9]|exit ?[0-9]|走らせた物 無し')
 c3a=$(printf '%s\n' "$f" | /usr/bin/grep -E '陽性対照|陽性對照|未測' | /usr/bin/grep -cE ':L?[0-9]+|未測'); c3b=$(printf '%s\n' "$f" | /usr/bin/grep -cE '^\|.*(陽性対照|陽性對照).*\|'); c3=$((c3a+c3b))
 c3k=$(printf '%s\n' "$f" | /usr/bin/grep -E '陽性対照|陽性對照' | /usr/bin/grep -cE "$INST7|器名|器=|同一の器|同じ器|同器|欄1と同一|欄1 と同一|同一detector|同一検出器|同一器|器の實體"); h3=$(printf '%s\n' "$f" | /usr/bin/grep -cE '^#+ *欄3.*(器名|器の實體|器の実体)'); c3k=$((c3k+h3))
 c4=$(printf '%s\n' "$f" | /usr/bin/grep -cE '転記|轉記'); c5=$(printf '%s\n' "$f" | /usr/bin/grep -cE "$C5_7"); c6=$(printf '%s\n' "$f" | /usr/bin/grep -cE '①|②|③|④|推論\(|command 出力|再計算')
 numc=$(printf '%s\n' "$f" | /usr/bin/grep -vE '^\| ?[0-9] ?\|' | /usr/bin/grep -vE '問一|問二|主張|宣言' | /usr/bin/grep -E "$INST7" | /usr/bin/grep -cE '[0-9]+ ?(件|行|file|hit|箇所|個)|=[0-9]+|N=[0-9]')
 if [ "$numc" -gt 0 ] && [ "$c2" = 0 ]; then z123="甲=${kou} 乙=${otsu} 丙=${hei} 數主張=${numc}/★欄2 無★(數主張に rc 要=零非零を問はず)"; elif [ "$kou" = 0 ]; then z123="甲=0 乙=${otsu} 丙=${hei} 數主張=${numc}(欄3 課さず)"; elif [ "$c3" = 0 ]; then z123="甲=${kou} 乙=${otsu} 丙=${hei}/★欄3 無★"; elif [ "$c3k" = 0 ]; then z123="甲=${kou} 乙=${otsu} 丙=${hei}/★欄3 器名 無★"; else z123="甲=${kou} 乙=${otsu} 丙=${hei}/欄2-3 通(器名行=${c3k})"; fi
 tt='痕跡無'; [ "$t" -gt 0 ] && tt="痕跡有(${t})"; c4t='★欄4 無★'; [ "$c4" -gt 0 ] && c4t='欄4 通'; c5t='★欄5 無★'; [ "$c5" -gt 0 ] && c5t='欄5 通'; c6t='★欄6 無★'; [ "$c6" -gt 0 ] && c6t="欄6 通(${c6})"
 if [ "$kou" = 0 ] && [ "$t" = 0 ]; then tt='痕跡無(甲=0 ゆゑ課さず)'; fi
 printf '%s/%s/%s/%s/%s' "$tt" "$z123" "$c4t" "$c5t" "$c6t"; }

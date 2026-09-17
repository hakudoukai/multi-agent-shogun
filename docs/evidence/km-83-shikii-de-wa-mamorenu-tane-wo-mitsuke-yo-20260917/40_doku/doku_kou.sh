#!/bin/bash
# doku_kou.sh ―― 甲 の口へ十二形の毒を当て、★内(器の報せ)と外(interpreter の悲鳴)★を分けて刷る。
# 生器へは一字も書かぬ: 走らせるのは _utsushi/ の写し、的 pane は ★存在せぬ名★。
set -u
CHILD="_utsushi/kou_child_watcher.py"
BOGUS="km83-nonexistent-pane-zzz:0.0"
OUT="40_doku/_kou"
mkdir -p "$OUT"

# ★陽性対照★: 的 pane が現に存在せぬ事(存在すれば送出の枝へ入り得る=危險)
if tmux display-message -t "$BOGUS" -p '#{pane_id}' >/dev/null 2>&1; then
  echo "★止★ 的 pane が実在する ―― 走らせぬ" >&2; exit 9
fi
echo "陰性対照: 的 pane '$BOGUS' は不在(tmux rc=$?) ∴ 子は pane 検査で即 return 0"

doku_name(){ case "$1" in
  1) echo "未設定";; 2) echo "空文字";; 3) echo "空白のみ";; 4) echo "0";; 5) echo "1";; 6) echo "2";;
  7) echo "01";; 8) echo "+1";; 9) echo "-1";; 10) echo "20桁";; 11) echo "非數";; 12) echo "改行入り";;
esac; }

run_one(){ # $1=口名 $2=毒番号
  local var="$1" i="$2" tag; tag="$(doku_name "$i")"
  local f="$OUT/${var}_$(printf '%02d' "$i")"
  if [ "$i" = "1" ]; then
    env -u "$var" /usr/bin/python3 "$CHILD" --target "$BOGUS" >"$f.out" 2>"$f.err"
  else
    local v
    case "$i" in
      2) v="";; 3) v=" ";; 4) v="0";; 5) v="1";; 6) v="2";; 7) v="01";; 8) v="+1";;
      9) v="-1";; 10) v="99999999999999999999";; 11) v="abc";; 12) v="$(printf '1\n')";;
    esac
    env "$var=$v" /usr/bin/python3 "$CHILD" --target "$BOGUS" >"$f.out" 2>"$f.err"
  fi
  local rc=$?
  # 内=logger 形の行 / 外=其れ以外(interpreter の悲鳴)
  local uchi soto
  uchi=$(grep -cE '^[0-9]{4}-[0-9]{2}-[0-9]{2}.*\[(INFO|WARNING|ERROR|DEBUG)\]' "$f.err"); [ -z "$uchi" ] && uchi=0
  soto=$(grep -vcE '^[0-9]{4}-[0-9]{2}-[0-9]{2}.*\[(INFO|WARNING|ERROR|DEBUG)\]' "$f.err"); [ -z "$soto" ] && soto=0
  local eda; eda=$(grep -oE 'stale_sec=[0-9-]+ poll_sec=[0-9-]+ LIVE=(True|False)' "$f.err" | head -1)
  [ -z "$eda" ] && eda=$(grep -oE '^[A-Za-z]*Error.*' "$f.err" | head -1)
  [ -z "$eda" ] && eda="(枝を刷らず)"
  printf '%-10s %-8s rc=%-3s 内=%-3s 外=%-3s %s\n' "$var" "$tag" "$rc" "$uchi" "$soto" "$eda"
}

for var in LIVE STALE_SEC; do
  echo "########## 口= $var ##########"
  printf '%-10s %-8s %-6s %-6s %-6s %s\n' 口 毒形 rc 内 外 "下流の枝/悲鳴の一行目"
  for i in $(seq 1 12); do run_one "$var" "$i"; done
  echo
done

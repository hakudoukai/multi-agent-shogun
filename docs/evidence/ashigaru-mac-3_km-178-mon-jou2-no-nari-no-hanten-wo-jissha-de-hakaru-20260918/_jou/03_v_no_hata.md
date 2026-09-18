# 門に「-v/冗語」の旗は在るか ―― ★字面で数へず、旗の定義を数へる★

器 = /Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_dasumae_gate.sh
刻 = 2026-09-18T21:35:40+0900

## ⑴ 旗を解く場所(case 文)の逐語

```bash
  case "$st" in
    unset) say "閾 ${name} = 未設定 ―― 既定 ${dflt} を用ゐる(★倒した事を刷る★)"; eval "$out=\$dflt"; return 0 ;;
    empty) say "★閾 ${name} が空文字 ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
    blank) say "★閾 ${name} が空白のみ ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  case "$raw" in
    *␊*|*␍*|*␉*) say "★閾 ${name} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${dflt} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$out=\$dflt"; return 0 ;;
  esac
```

## ⑵ 字面の当たり(参考 ―― 之だけでは決められぬ)
  「-v」= 1 行 (grep -c rc=0 ―― 0 行の時 rc=1 は正常)
  「--verbose」= 0 行 (grep -c rc=1 ―― 0 行の時 rc=1 は正常)
  「verbose」= 0 行 (grep -c rc=1 ―― 0 行の時 rc=1 は正常)
  「VERBOSE」= 0 行 (grep -c rc=1 ―― 0 行の時 rc=1 は正常)
  「冗語」= 0 行 (grep -c rc=1 ―― 0 行の時 rc=1 は正常)

## ⑶ ★実射★ ―― 旗を渡して門が何と言ふか
  bash <器> -v -- _tane/f01_kirei.txt  → rc=1
      閾 DASUMAE_READ_TIMEOUT = 未設定 ―― 既定 10 を用ゐる(★倒した事を刷る★)
      閾 DASUMAE_MAX_BYTES = 未設定 ―― 既定 10485760 を用ゐる(★倒した事を刷る★)
      ★台帳が無い: -v★
      條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★
      ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★
      ★file が無い: --★
      ★條⑤ 測れぬ(寸法が取れぬ) ―― --★ ★測れぬは通さぬ(default-deny)★
      條⑤ 寸法 = byte和 4(閾 10485760未満)

      ★出す前 門が落ちた。出すな。★
  bash <器> --verbose -- _tane/f01_kirei.txt  → rc=1
      閾 DASUMAE_READ_TIMEOUT = 未設定 ―― 既定 10 を用ゐる(★倒した事を刷る★)
      閾 DASUMAE_MAX_BYTES = 未設定 ―― 既定 10485760 を用ゐる(★倒した事を刷る★)
      ★台帳が無い: --verbose★
      條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★
      ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★
      ★file が無い: --★
      ★條⑤ 測れぬ(寸法が取れぬ) ―― --★ ★測れぬは通さぬ(default-deny)★
      條⑤ 寸法 = byte和 4(閾 10485760未満)

      ★出す前 門が落ちた。出すな。★

## 判

★門に旗を解く仕掛けは無い。★引数の型は `<manifest|--> <file...>`(器の usage 行に逐語)であり、
第一引数は ★台帳の path として読まれる★。∴ `-v` を渡すと「旗が知らぬ」ではなく
★「台帳が無い: -v」★ と鳴つて落ちる ―― 之は旗の拒絶ではなく ★台帳名として扱はれた★ 事である。

字面の「-v」1 行も旗ではない ―― `command -v timeout` の `-v` である(器の TIMEOUT_BIN 行)。
∴ ★字面の 1 件は偽陽性であり、旗の定義は 0 件★。

∴ memory の「-v で②③入替」は ★門の旗ではなく環境変数 GREP_OPTIONS=-v★ と解して撃つた(_jou/02_grep_options.md)。

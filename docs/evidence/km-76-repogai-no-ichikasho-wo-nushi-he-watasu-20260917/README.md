# km-76 ―― ★repo外の1箇所を、持ち主へ渡す紙★ / `~/bin/fleet_liveness_check.sh`

- 差出: 家老mac(係長格・Mac レーン)  宛: ★環境部長(hermes2)★  同報: 總監督
- 典: 委員長裁 **seq324404**「repo外の fleet_liveness_check は貴殿の的でない=持ち主(環境部長)へ★「箇所・現形・直し形・負テスト形」を1紙で渡し★(DB便・CC監督)、貴殿の閾20箇所6file は 1/1 で閉じてよい」
- ★當席は本器に一字も書いて居らぬ★(読取と複製のみ)。据ゑるか否かは持ち主の裁量。

---

## 一 ―― ★箇所★

| 項 | 値 |
|---|---|
| file | `~/bin/fleet_liveness_check.sh`(mac_pc・repo 外ゆゑ共有樹に無し) |
| sha256 | `47033986db317dcc…`(全長は `raw/00_sha_genkei.txt`) |
| 行 | 93 |
| 閾 | **1本** ―― `FLEET_MIN_PANE_WIDTH`(既定 80) |
| 該當行 | L28(受け) / L31–32(門) / L46(下流の比較)。逐語は `raw/01_gentaikou.txt` |

## 二 ―― ★現形★(逐語)

```bash
18: set -uo pipefail                         # ★set -e は無い★(∴ 番人を入れても死なぬ)
28: MIN_WIDTH="${FLEET_MIN_PANE_WIDTH:-80}"
31: is_num(){ case "${1:-}" in (''|*[!0-9]*) return 1 ;; (*) return 0 ;; esac }
32: is_num "${MIN_WIDTH}" || { printf '%s\n' "[fleet_liveness] ★閾 MIN_WIDTH が數でない(「${MIN_WIDTH}」) ―― 既定 80 へ倒す(fail-closed)★" >&2; MIN_WIDTH=80; }
46:     if [ -n "$w" ] && [ "$w" -lt "$MIN_WIDTH" ] 2>/dev/null; then
```

★疵は二つ。いづれも「測つた」物であつて、見立てではない。★

1. **fail-open(報せ落ち)** ―― `is_num` は字面判定ゆゑ `99999999999999999999` を「數」と通す。
   然し L46 の `[ "$w" -lt "$MIN_WIDTH" ]` は **rc=2** を返す。`if` は偽となり、
   **★狹い pane(40桁)が「狹い」と報せられぬ★**。生死を見る器が、默つて見逃す形である。
2. **行注入** ―― L32 は値を `「${MIN_WIDTH}」` の儘 stderr へ刷る。値に改行が在れば
   **偽の log 行が一本立つ**(`[fleet_liveness] ★偽の行★` が行頭から出る ―― 實測)。

## 三 ―― ★直し形★

`raw/30_naoshikei.sh`(そのまま L28〜L32 と差し替へられる形・**51行**・`bash -n` rc=0)。**L46 は触らずともよい。**

出所は共有樹で既に据ゑ濟の番人(逐語)であり、印だけ `[fleet_liveness]` に改めた:

- `scripts/inbox_watcher.sh` / `scripts/redundancy/watchdog.sh` / `scripts/redundancy/health_check.sh`(km-74=`6dbe09e6`)
- `scripts/redundancy/shogun_report_watcher.sh`(km-75=`e768e714`・push済)

要點(裁の對應):

| 裁 | 形 |
|---|---|
| seq322952 甲 | `num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }` ―― **後段と同じ演算子**で先に検める(字面判定をやめる) |
| seq322952 乙 | `env_state` が **未設定 / 空文字 / 空白のみ / 値** を分けて名指す(`${1+set}` を使ふ故、未設定と空文字が混ざらぬ) |
| seq323687⑵ | **未設定の報せは process に一度だけ**(`_th_unset_told`) ―― 高頻度器が鳴り過ぎぬ為 |
| seq323980⑵ | 値の改行は **可視印 ␊␍␉ へ置換**して刷る。**値に ␊␍␉ が既に在れば ★値を刷らず★ 倒す**(fail-closed) |

## 四 ―― ★負テスト形★(走らせて確かめられる形で渡す)

同じ 8 形を、**現形**と**直し形**の二つの器へ通した。器も出目も此の束に在る。

```bash
# 現形(L18/28/31/32/46 を逐語で写した複製)
bash raw/40_genkei_harness.sh          # 環境変数 FLEET_MIN_PANE_WIDTH を8形で與へる
# 直し形(L28〜32 のみ差し替へ・L18/L46 は現形の儘)
bash raw/45_naoshikei_harness.sh
```

| 形 | 與へた値 | 現形 | 直し形 |
|---:|---|---|---|
| 1 | 未設定 | 默つて 80 | 「未設定 ―― 既定へ倒す」を**一度だけ**・80 |
| 2 | 空文字 | **默つて 80**(名指さぬ) | 「空文字」と名指し 80 |
| 3 | 空白のみ | 「數でない」・80 | 「空白のみ」と名指し 80 |
| 4 | `99999999999999999999` | ★**報せ落ち**(狹い pane を見逃す)★ | 「比較器が扱へぬ」・80 ―― **報せる** |
| 5 | `120` | 120 | 120(正常値は鳴らさぬ) |
| 6 | `-5` | 「數でない」・80 | 「比較器が扱へぬ」・80 |
| 7 | `80`+改行+偽行 | ★**偽の log 行が一本立つ**★ | 一行に畳んで刷る(`80␊[...]`)・80 |
| 8 | 値に `␊` が既在 | 其の儘刷る | ★**値を刷らず**★倒す(裁323980⑵) |

**締め(器で数へた):**

| | 報せ落ち | 偽の log 行 | rc=0 |
|---|---:|---:|---:|
| 現形 | **1形** | **1本** | 8/8 |
| 直し形 | **0形** | **0本** | 8/8 |

`raw/41_genkei_matrix.txt` / `raw/46_naoshikei_matrix.txt` が生の出目。

## 五 ―― 添へ書き

- 本器は `set -e` を持たぬ(`set -uo pipefail`)。∴ 番人の `[ … ] 2>/dev/null; [ $? -le 1 ]` が
  途中で死ぬ心配は無い。**尚 `set -e` 有りの器でも 8/8 rc=0 を實測済**(km-75束の `41_setE_matrix.txt`)。
- 據ゑるか否か・いつ據ゑるかは **持ち主(環境部長)の裁量**。當席は測つて形を渡すのみで、
  **本器へは一字も書いて居らぬ**(`_before/fleet_liveness_check.sh.snapshot` は讀んだ時の寫し)。
- 走つて居る器が在れば、書き替へても **舊 inode を握る**故、効くのは次の起動からである。

## 六 ―― 紙の中身

```
_before/fleet_liveness_check.sh.snapshot  讀んだ時の寫し(93行)
raw/00_sha_genkei.txt                     現形の sha256(全長)
raw/01_gentaikou.txt                      該當5行の逐語
raw/30_naoshikei.sh                       ★直し形(そのまま差し替へられる)★
raw/40_genkei_harness.sh                  負テスト器(現形)
raw/41_genkei_matrix.txt                  現形 × 8形(報せ落ち1形・偽の行1本)
raw/45_naoshikei_harness.sh               負テスト器(直し形)
raw/46_naoshikei_matrix.txt               直し形 × 8形(★0形・0本★)
```

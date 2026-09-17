# 宛名の門 ―― 据ゑた記(委員長裁 seq325654)

家老mac / 2026-09-17

## 一、因

`scripts/inbox_write.sh` には ★宛名の検めが無かつた★。
何の字を渡しても `queue/inbox/<其の字>.yaml` が生れ、器は `rc=0` を返し「成功」と刷る。

實害は二つ、いづれも★測つた物★である。

| # | 事 | 出所 |
|---|---|---|
| 甲 | 裸の `gunshi` 宛の監査提出 2通が、讀手なき旧箱 `ieyasu.yaml` へ落ちた(D25/D28) | CLAUDE.md「Mailbox System」節の逐語註(2026-08-16 委員長修正) |
| 乙 | `karo-mac,gunshi-mac.yaml` ―― 讀点で二名を一字に綴つた箱が生れ、足軽mac4号の tk4st48 復命が ★29日 未讀★ のまま在つた | `docs/evidence/karo-mac-mayoi-bako-kenbun-20260917/` |

★誰も落度を犯して居らぬ。器が宛名を検めなかつただけである。★

## 二、据ゑた物

| 物 | 前 | 後 |
|---|---|---|
| `scripts/inbox_write.sh` 行 | 366 | 409 |
| 同 sha256 | `96a1e2355d5acf093763af0ea05da3a35a9c7135be478da6160960501bc21660` | `d2265a07e232eb0b76d5ede5e19d15a4b70094787d58eeff19c6d73d6f0b3317` |
| 控(条件①) | ― | `scripts/inbox_write.sh.bak-namegate-20260917` 15754 byte / sha256 は★据ゑ前と同一★ |

据ゑた場所 = 引数検め(`Usage:` を刷る `fi`)の直後。
★行番号で当てず逐語で当て、置換数が 1 である事を assert してから書いた。★
`bash -n` 通。

## 三、白名簿は焼かず實測で作る(条件②)

```
_iw_name_list() {
    _TMUX_BIN="$(command -v tmux 2>/dev/null || true)"
    {
        { [ -n "$_TMUX_BIN" ] && "$_TMUX_BIN" list-panes -a -F '#{@agent_id}' 2>/dev/null; } || true
        ls -1 "$SCRIPT_DIR/queue/inbox" 2>/dev/null | sed -n 's/\.yaml$//p'
    } | grep -v '^$' | grep -v '[,[:space:]]' | sort -u
}
```

- ⑴ 生きた pane の `@agent_id`
- ⑵ 既存の箱の名(`queue/inbox/*.yaml`)
- ⑵から ★讀点・空白を含む名を除く★ ―― 除かねば ★迷ひ箱が己を白名簿へ入れる★。
- 白名簿が空なら ★通さぬ★(fail-closed)。pane も箱も讀めぬ時に「検められぬから通す」は禁。

★pane だけでは足らぬ★ ―― `ashigaru-mac-4` は生 pane を持たぬが、
本日 条件⑤ で其の席へ一行を送る必要が在つた。箱を白名簿に入れねば正しい便が止まる。

實測(2026-09-17 14:0x)= ★18名★。
`ashigaru-mac-1..7 / dr-m / fukuincho / gakushu-bucho / gunshi / gunshi-mac / hermes-gunshi-mac / hermes3 / karo / karo-mac / kikaku-bucho / shogun-mac`
★`karo-mac,gunshi-mac` は入つて居らぬ(讀点で除かれた)。★

拒否の時は ★此の18名を送り主へ列挙する★ ―― 綴り違ひなら己で直せる形に。

## 四、逃げ道(条件③)

`IW_ALLOW_NAME=<理由>` ―― 理由が ★10字を超える★ 時のみ未知の名を通す。
字数は ★python3 の len★ で数へる(`${#}` も awk の length も byte を返す故 使はぬ)。
通した時は ★註★ を stderr に刷る:「★新しい箱が生れる★。報告に此の理由を書け」。

★讀点・空白は此の逃げ道でも通らぬ。★ 二名を一字で渡した跡であり、直すべきは宛名の側である。

## 五、四対照(条件④)

`IW_NAME_TEST_ONLY=1` を立てると門を通つた所で `NAME_PASS` を刷つて止まる ∴ ★箱を書かぬ★。

| # | 宛名 | 逃げ道 | rc | 出目 |
|---|---|---|---|---|
| 陽① | `ashigaru-mac-1`(生 pane 有) | 無 | **0** | `NAME_PASS` |
| 陽② | `ashigaru-mac-4`(pane 無・箱 有) | 無 | **0** | `NAME_PASS` |
| 陰① | `karo-mac,gunshi-mac`(讀点) | 無 | **69** | 「讀点/空白」拒否・逃げ道も効かぬ旨 |
| 陰② | `ashigaru mac 1`(空白) | 無 | **69** | 同上 |
| 陰③ | `unknown-seki-xyz` | 無 | **69** | 未知名拒否 ＋ ★18名を列挙★ |
| 陰④ | `unknown-seki-xyz` | 6字 | **69** | 同上(10字以下は効かぬ) |
| 陽③ | `unknown-seki-xyz` | 15字 | **0** | ★註★ ＋ `NAME_PASS` |

★試験の後に新しく生れた箱 = 0★(`queue/inbox/` を實測)。

## 六、迷ひ箱と tk4st48(条件⑤)

- 迷ひ箱 `queue/inbox/karo-mac,gunshi-mac.yaml` = ★消さず・讀印も触らず★。
  sha256 `9b9427046b48e527c55920ba1e2fcabb172c511b2e918679850cdf8cf81421ee` ―― 写す前と後で★同一★。
- 未讀1通(`msg_20260819_232407_dacd802e` / 足軽mac4号 / tk4st48 復命 / 890字)を
  正名箱 `queue/inbox/karo-mac.yaml` へ ★写し★ た = `msg_20260917_140910_9e5e4d0e`(1165字)。
  冠に「写し・原本は迷ひ箱に在り」と原 id・原刻・原 from を書いた。
- 本人(足軽mac4号)へ一行を送つた ―― ★落度は貴殿に非ず・器に宛名の検めが無かつた故★。
- 宛名の片割 `gunshi-mac` は死箱(rc=68)ゆゑ、tk4st48 成果file の監査は家老mac が代送する。

## 七、dev_qa 登録文(条件⑥)―― ★家老mac に書込の手が無い★

實測: `~/bin/sb write` は `agent_letter.py` へ繋がり ★letter のみ★。
`~/bin/board_write.py` は `task_tracker` の13欄のみ(`ALLOWED` 逐語)。
`~/bin` にも `scripts/` にも dev_qa へ挿す器は無い(`grep -rl dev_qa` 實測)。
★インラインの REST POST は「配布済 helper を使へ」の則に触れる ∴ 打たぬ。★
以下を ★登録文★ として渡す。代行、又は手の配備を請ふ。

```
category: multi_agent_infrastructure
severity: medium
symptom: inbox_write.sh に宛名の検めが無く、誤つた宛名を渡すと其の字の箱が新しく生れて rc=0「成功」と刷る。
  實害2件 ―― ⑴裸の "gunshi" 宛の監査提出2通が讀手なき ieyasu.yaml へ落ちた(D25/D28)
  ⑵"karo-mac,gunshi-mac" と讀点で二名を綴つた箱が生れ、足軽mac4号 tk4st48 復命が29日未讀。
root_cause: 器が「宛名は正しい」と前提して居た。TARGET を其の儘 path へ綴ぢ込む(L25)為、
  誤字も讀点も空白も悉く新しい箱の名に成る。生れた箱は誰も讀まぬので、送り主からは成功と区別が付かぬ。
solution: 宛名の門を据ゑた(2026-09-17・委員長裁 seq325654)。白名簿は焼かず實測で作る
  ―― 生 pane の @agent_id ∪ 既存の正名箱(讀点・空白を含む名は除く)。讀点・空白は無条件に拒む(rc=69)。
  未知名は IW_ALLOW_NAME=<理由10字超・python3 len で計測>でのみ通し註を刷る。
  拒否時は許可名一覧を送り主へ出す。白名簿が空なら通さぬ(fail-closed)。
  試験用に IW_NAME_TEST_ONLY=1(門を通つた所で止まり箱を書かぬ)。
wrong_approaches: 白名簿を器へ焼き込む(席が増える度に器を直す事に成る)／
  生 pane だけで作る(pane を持たぬ正しい箱 ashigaru-mac-4 等が止まる)／
  迷ひ箱を消して無かつた事にする(第一条三-b に触れる・未讀の便が消える)／
  讀点名にも逃げ道を与へる(二名を一字で渡す誤りが温存される)／
  字数を ${#} や awk length で数へる(byte を返す ∴ 10字の閾が壊れる)。
tags: ['inbox_write', 'name-gate', 'mailbox', 'karo-mac', 'seq325654', 'fail-closed']
last_occurred: 2026-09-17
```

## 八、★門が塞がぬ路★(隠さぬ疵)

★呼ばれぬ門は一路も塞がぬ。★
本門は `scripts/inbox_write.sh` の中にのみ立つ。`queue/inbox/*.yaml` へ ★直に★ 書く路が他に在れば、
其の路は今も宛名を検めずに箱を生み得る。
其の路が幾つ在るかは ★本紙では測つて居らぬ★ ―― 專任1へ km-97 として立てた(2026-09-17 14:17)。

其の他の測れて居らぬ物:
- 他PC への展開 = 監督lot(裁 seq325654 の逐語)。當席は触れて居らぬ。
- `IW_DEAD_LIST` の死箱宣と白名簿の食ひ違ひ ―― 專任3へ km-99 として立てた。

# ㋔ 門の穴 三つ ―― 各々に「直し方 1 行」と「其れで直らぬ物 1 行」

## 穴一 ―― 白名簿⑵(既存の箱)が迷ひ箱を自ら正名化する
- 実測: 対照⑤ `IW_NAME_TEST_ONLY=1 bash scripts/inbox_write.sh karo x t f` → rc=0 `NAME_PASS target=karo`。`karo` に pane は無い(生 pane 7 名に無し)が箱が在る(659 通・全未読)。門 L47 `ls -1 "$SCRIPT_DIR/queue/inbox" | sed -n 's/\.yaml$//p'` が箱の名を白名簿へ入れる。読点・空白の名だけ L48 で除くゆゑ、綴り違ひ・旧名・他 PC 名(gunshi / hermes3 / hermes-gunshi-mac / fukuincho / karo)は★門を通る★。
- 直し方 1 行: 白名簿を ⑴生 pane のみ(＋宣した名簿 file 1 本)にし、⑵既存箱の名を落とす。
- 直らぬ物 1 行: 休席(ashigaru-mac-4..7 / shogun-mac / kikaku-bucho)への便が 69 で落ちる(IW_ALLOW_NAME の運用が要る)、既に `karo.yaml` に溜まつた 659 通の読み手は生れぬ。

## 穴二 ―― 呼ばれぬ門は一路も塞がぬ: 門を通らずに箱を生む路が 5 器 6 行
- 実測(読取・㋑ #2-#6): `scripts/inbox_watcher.sh` L44-46 / `scripts/watcher_supervisor.sh` L25 / `scripts/watcher_supervisor_third.sh` L23 / `shutsujin_departure.sh` L445・L971 / `shim/hakudokai/hakudokai_secondpc_setup.sh` L329 ―― 悉く `[ ! -f … ] && echo "messages: []" > queue/inbox/<名>.yaml` の形で、名を検めず生む。内 inbox_watcher.sh は本 PC で 3 本稼働(ps 写し)。名の源は起動者の名簿(boot-mac-fleet.sh L111・supervisor)。
- 直し方 1 行: 「無ければ生む」を各器から抜き、箱の生成を inbox_write.sh L273 相当の一箇所(共有関数)に寄せ、各器は「無ければ落ちる」に倒す。
- 直らぬ物 1 行: 起動名簿の名の誤りは箱でなく watcher の側で起きる(pane と名簿が同じ誤名なら L115 の skip も効かぬ)、second_pc の shim は本 PC の門の外。

## 穴三 ―― 宛名固定の甲: 門は「名が在るか」を見て「此の PC の読み手か」を見ない
- 実測: `scripts/stop_hook_inbox.sh` L174 `inbox_write.sh karo`(★Stop hook で claude 席が止まる度に発火★・`.claude/settings.json` L8)、`scripts/agent_periodic_push.sh` L109 `karo`、`scripts/inbox_watcher.sh` L940 `iincho`、`scripts/agent_health_check.sh` L203 `shogun`。`karo` は箱有ゆゑ通り(穴一と合流し 659 通に成つた)、`iincho` `shogun` は本 PC に箱無ゆゑ 69 で拒まれるが、L939-940 は `2>/dev/null || true` で★拒否を黙らせる★(静かな失敗)。
- 直し方 1 行: 宛名を字で焼かず、`config/settings.yaml` の pc_mapping から「此の PC の家老/将軍」を引く(mac なら karo-mac)。拒否の stderr を捨てず log へ。
- 直らぬ物 1 行: DEAD-INBOX 門(gunshi-mac)と同じく「名は在るが誰も読まぬ箱」は名の門では見えぬ、既存 659 通の移送は別の手。

## 三つの穴の関係
穴一 × 穴三 = 本日 13:57 まで `karo.yaml` が育ち続けた因。穴二 = 門の据ゑ後も、名簿さへ誤れば箱が生れる因。門は「読点・空白・未知」を確かに拒む(対照①②③ rc=69)―― ★塞いだのは、門を呼ぶ 14 器の宛名の内、白名簿に無い新名だけ★である。

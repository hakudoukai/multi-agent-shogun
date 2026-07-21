# 環境部長(hermes2=hermes user) 保守権限付与 — ★PROPOSAL (未適用・副院長レビュー前)★

---
## ★FINAL 確定版 (seq67473 (a)-(e)反映・未設置・理事長監督下install待ち)★

実機確認: tmux=/usr/bin/tmux systemctl=/usr/bin/systemctl bash=/usr/bin/bash / ★setfacl=未install(acl pkg無)★ / systemd は hermes-gateway.service のみ(hermes2-*/watcher unit ★未在★=env部長P4未実装) / 既存 `/etc/sudoers.d/hermes-ops` = ★hakudoukai★ への hermes-task 限定grant(=別principal、本grantは別ファイルで無衝突。過去 hermes:ALL は安全削除済ゆえ最小限堅持)。

★PROPOSED /etc/sudoers.d/50-hermes2-maintenance (新規・未設置)★:
```
# 環境部長(hermes) 保守NOPASSWD — 保守コマンドのみ。本番DB/鍵/本筋src/master/本物Hermes本体=対象外(N1-N5)。
# (a)厳格版: tmux はサブコマンド限定列挙(new-window等の任意実行余地を塞ぐ)
Cmnd_Alias H2_TMUX = \
  /usr/bin/tmux -S /tmp/hermes2.sock send-keys *, \
  /usr/bin/tmux -S /tmp/hermes2.sock list-panes *, \
  /usr/bin/tmux -S /tmp/hermes2.sock list-sessions, \
  /usr/bin/tmux -S /tmp/hermes2.sock capture-pane *, \
  /usr/bin/tmux -S /tmp/hermes2.sock has-session *, \
  /usr/bin/tmux -S /tmp/hermes2.sock select-pane *, \
  /usr/bin/tmux -S /tmp/hermes2.sock set-option *, \
  /usr/bin/tmux -S /tmp/*.sock list-panes *, \
  /usr/bin/tmux -S /tmp/*.sock list-sessions, \
  /usr/bin/tmux -S /tmp/*.sock capture-pane *, \
  /usr/bin/tmux -S /tmp/*.sock has-session *
# 保守プロセス制御(watcher/listener のみ・フルパス固定)
Cmnd_Alias H2_PROC = \
  /usr/bin/pkill -f hakudokai_*_reverse_watcher.sh, \
  /usr/bin/pkill -f *_reverse_poll.py, \
  /usr/bin/pkill -f *_inbox_watcher*
# 着火経路 script 起動(指定のみ)
Cmnd_Alias H2_FIRE = \
  /usr/bin/bash /home/hakudoukai/multi-agent-shogun/shim/hakudokai/hakudokai_hermes2_reverse_watcher.sh *, \
  /opt/hermes-agent/venv/bin/python3 /home/hermes/.hermes2/scripts/*.py *
# systemd 保守(env部長P4の hermes2-* unit 用・現時点 unit 未在ゆえ将来分の前置許可)
Cmnd_Alias H2_SYSTEMD = \
  /usr/bin/systemctl restart hermes2-*.service, \
  /usr/bin/systemctl status hermes2-*.service, \
  /usr/bin/systemctl enable hermes2-*.service, \
  /usr/bin/systemctl disable hermes2-*.service

hermes ALL=(root) NOPASSWD: H2_TMUX, H2_PROC, H2_FIRE, H2_SYSTEMD
```

★保留/別判断★:
- (c-ACL) setfacl 未install ゆえ ★H2_ACL は本リリース除外★。hermes 自領域(/home/hermes/.hermes2)は自身でrwx・/tmp/hermes2.sock は 0666 で既に可ゆえ ★当面 ACL grant 不要★。他メンバー領域(P7)へのファイル書込が要る段になったら ①acl pkg install + setfacl か ②共有group(chgrp+chmod g+rwx)を ★副院長判断で別途★。
- (b-systemd) hermes2-* unit は ★現存せず★(env部長P4実装後)。上記 H2_SYSTEMD は将来 unit 用の前置。実 unit 名確定後に整合。

★設置手順(理事長監督下・一回限り)★:
```
# 1. 断片を書き出し → visudo -c で構文検証(壊れたsudoersはroot締め出しリスク)
sudo install -m 0440 -o root -g root <draft> /etc/sudoers.d/50-hermes2-maintenance
sudo visudo -cf /etc/sudoers.d/50-hermes2-maintenance   # 検証OFFのみ
sudo visudo -c                                           # 全体整合
# 2. 失敗時は即 sudo rm /etc/sudoers.d/50-hermes2-maintenance
```
→ ★Commander独断設置はしない。副院長 最終OK + 理事長監督 で実行★。

---


副院長令 seq67451 / 要件定義 6fbf2f82 (is_current=true, waived_by=rijicho) / 理事長監督下実行。
**本書は提案。/etc/sudoers.d への設置・setfacl 実行は副院長レビュー→理事長監督下まで行わない。**
対象ユーザ = `hermes` (uid1001, 環境部長実行ユーザ)。付与は「決まった保守コマンドのみ NOPASSWD」。

## 1. 付与(P1-P7) ↔ 実現機構 対応

| 要件 | 機構 | sudo要否 |
|---|---|---|
| P1 /home/hermes /.hermes2 rwx | hermes 自身が所有(既にrwx) | 不要 |
| P2 /tmp/*.sock list-panes/send-keys/set | 自socketは不要。他者socketは下記 sudoers tmux 経由 | 一部要 |
| P3 watcher/listener start/stop/restart | 下記 sudoers pkill/起動スクリプト | 要(他者プロセス時) |
| P4 自 systemd user unit | `systemctl --user` は hermes 自身で可 | 不要 |
| P5 着火/配送scriptの設置・修正 | /home/hermes配下=不要 / 共有shim配下は下記ACL | 一部要 |
| P6 hermes_ro のACK4列UPDATE継続 | 既付与(DB側RLS/権限・変更なし) | — |
| P7 他メンバー保守領域(watcher/pane/systemd/着火/容量)点検・再起動・修理 | 下記 sudoers 明示列挙のみ | 要 |

## 2. ★PROPOSED★ /etc/sudoers.d/50-hermes2-maintenance (未設置)

```
# 環境部長(hermes) 保守NOPASSWD — 保守コマンドのみ明示列挙。本番DB/本筋コード/master/本物Hermes本体/鍵=対象外(N1-N5)。
# Cmnd_Alias でフルパス固定。ワイルドカードは保守領域に限定。

# --- 保守プロセス制御 (P3/P7): watcher/listener のみ。汎用killは不可 ---
Cmnd_Alias H2_PROC = \
  /usr/bin/pkill -f hakudokai_*_reverse_watcher.sh, \
  /usr/bin/pkill -f *_inbox_watcher*, \
  /usr/bin/pkill -f *_reverse_poll.py, \
  /bin/kill [0-9]*

# --- tmux 保守 (P2/P7): 指定socketの操作のみ。任意コマンド実行(new-window等で抜け道)注意ゆえ send-keys/list/capture/has-session/set-option に限定 ---
Cmnd_Alias H2_TMUX = \
  /usr/bin/tmux -S /tmp/hermes2.sock *, \
  /usr/bin/tmux -S /tmp/*.sock list-panes *, \
  /usr/bin/tmux -S /tmp/*.sock list-sessions, \
  /usr/bin/tmux -S /tmp/*.sock capture-pane *, \
  /usr/bin/tmux -S /tmp/*.sock has-session *

# --- 保守ACL (P5/P7): 共有shim/watcher領域のみ。/home/hakudoukai 全体・/etc・本筋src は不可 ---
Cmnd_Alias H2_ACL = \
  /usr/bin/setfacl -m u\:hermes\:rwx /home/hakudoukai/multi-agent-shogun/shim/hakudokai/*, \
  /usr/bin/setfacl -m u\:hermes\:rx /tmp/*.sock

# --- systemd 保守unit (P4/P7): 保守unit名prefix限定 (例: *-watcher, *-reverse, hermes2-*) ---
Cmnd_Alias H2_SYSTEMD = \
  /usr/bin/systemctl restart *-watcher.service, \
  /usr/bin/systemctl restart *-reverse*.service, \
  /usr/bin/systemctl restart hermes2-*.service, \
  /usr/bin/systemctl status *-watcher.service, \
  /usr/bin/systemctl status hermes2-*.service, \
  /usr/bin/systemctl enable hermes2-*.service, \
  /usr/bin/systemctl disable hermes2-*.service

# --- 着火経路スクリプト起動 (P3/P5): 指定scriptのみ ---
Cmnd_Alias H2_FIRE = \
  /usr/bin/bash /home/hakudoukai/multi-agent-shogun/shim/hakudokai/hakudokai_hermes2_reverse_watcher.sh *, \
  /opt/hermes-agent/venv/bin/python3 /home/hermes/.hermes2/scripts/*.py *

hermes ALL=(root) NOPASSWD: H2_PROC, H2_TMUX, H2_ACL, H2_SYSTEMD, H2_FIRE

# 明示的に与えない(N1-N5・防御的) — sudoers は許可リストゆえ下記は元々不可だが意図を記録:
#  NO: 汎用 sudo su / rm -rf 広域 / 本番DB接続(psql 本番) / 鍵ファイル読取(cat *SERVICE_ROLE* 等) / apt remove
```

## 3. ★PROPOSED★ ACL/socket (未実行)
```
# 共有 shim 保守領域 (P5/P7): hermes が watcher/着火scriptを修正できるよう ACL 付与
setfacl -m u:hermes:rwx /home/hakudoukai/multi-agent-shogun/shim/hakudokai
# /tmp/hermes2.sock は既に 0666 (本watcherが設定済) — 追加不要
```

## 4. 境界(N1-N5) 保持の根拠
- N1 本番DB/RLS: sudoers に psql/本番DB接続なし。ACK4列のみ既存hermes_ro継続(本提案で変更せず)。
- N2 SERVICE_ROLE_KEY: sudoers に鍵読取(cat/get)なし。Doppler中央集権維持(記憶24)。
- N3 本筋カルテコード(frontend/src・backend/api): H2_ACL は shim/ と /tmp/*.sock のみ。src/api への setfacl/書込権は付与せず。
- N4 master push: git/push は sudoers になし。
- N5 本物Hermes本体(/home/hermes/.hermes 監査)・Commander指揮: H2_TMUX は send-keys 保守可だが指揮介入は運用規律(コード制約外)。/home/hermes/.hermes への ACL付与なし。

## 5. 適用後 環境部長 自己検証4項目 (DoD)
1. /home/hermes/.hermes2 rwx 確認
2. /tmp/hermes2.sock send-keys + Enter 自走
3. 自 watcher restart 自走
4. 着火経路script修正→to_pc=hermes2 未ack検知→配送→ACK自動クローズ

## 6. ★レビュー要確認点(Commander注記)★
- (a) H2_TMUX の `/usr/bin/tmux -S /tmp/hermes2.sock *` は new-window 経由の任意コマンド実行余地がある。厳格化するなら send-keys/list/capture/has-session のみに限定推奨(本提案 §2 後半は限定版併記)。**どちらを採るか副院長判断**。
- (b) systemd unit prefix(*-watcher/hermes2-*)の実在unit名は環境部長P4実装(seq67188)確定後に整合要。
- (c) tmux/pkill のフルパスは実機 `which tmux/pkill` で確定後に固定(distro差)。
- (d) 本提案は ★未適用★。設置=sudo cp to /etc/sudoers.d/ + visudo -c 検証 + setfacl は ★理事長監督下★ で実行。
- (e) ★既存 /etc/sudoers.d/hermes-ops が実在★(hermes に既存sudo付与あり)。本提案は ★別ファイル 50-hermes2-maintenance を新設 か hermes-ops を拡張 か★ を副院長判断。既存hermes-opsの現行内容と重複/矛盾しないよう、設置前に `sudo cat /etc/sudoers.d/hermes-ops` で現行grant確認→差分のみ追加が安全。hermes shell=/usr/sbin/nologin ゆえ `sudo -u hermes <cmd>` 直接形は可(login shell経由不可)。

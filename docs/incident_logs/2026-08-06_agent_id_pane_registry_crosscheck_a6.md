# tmux @agent_id と pane_registry.yaml 突合 (足軽6号、2026-08-06・家老second下命)

★★読取のみ(tmux list-panes/grep実施のみ)。tmux操作は一切行っていない。hermes-*paneには
触れていない(Read/list-panesのみ)。測時=2026-08-06T01:46:20+0900(date -Iseconds実行結果)。★★

★様式(⒜実装読解+⒝実測、両方)★=本件は実測が主。registryの読み方は`scripts/inbox_write.sh:288-292`
(canon宛先集合=`pane_registry.panes[].agent_id`)の実装に倣った。

## 母集団の範囲(明記)

当職はSecondPCのtmuxセッションからのみ実行しており、★MainPC側のpaneは測定不可★
(registry自身のnotesにも「SecondPC entriesはkaro-second主管領域・本PCからのtmux検証は不可」と
明記済=MainPC分は対象外、SecondPC分のみを母集団とした)。

## ⒜ tmux全pane列挙 (実測・命令+出力そのまま、raw順=list-panes -aの既定反復順)

$ tmux list-panes -a -F '#{pane_id} #{session_name}:#{window_index}.#{pane_index} @agent_id=#{@agent_id}'
%13 hermes-gunshi-second:0.0 @agent_id=shogun-second
%0 hermes-honbucho:0.0 @agent_id=honbucho
%3 multiagent-second:0.0 @agent_id=karo-second
%4 multiagent-second:0.1 @agent_id=ashigaru1
%5 multiagent-second:0.2 @agent_id=ashigaru2
%6 multiagent-second:0.3 @agent_id=ashigaru3
%7 multiagent-second:0.4 @agent_id=ashigaru4
%8 multiagent-second:0.5 @agent_id=ashigaru5
%9 multiagent-second:0.6 @agent_id=ashigaru6
%10 multiagent-second:0.7 @agent_id=ashigaru7
%11 multiagent-second:0.8 @agent_id=gunshi-second
%2 shogun-second:0.0 @agent_id=shogun-second

**計12 pane、空(@agent_id未設定)は0件。**

## ⒝ registry panes[].agent_id (SecondPC分のみ抽出・実測)

$ grep -B1 "pc: SecondPC" queue/pane_registry.yaml | grep -E "tmux_target|agent_id"
(抜粋、tmux_target+agent_idペアで11件)
shogun-second:0.0→shogun-second / multiagent-second:0.0→karo-second /
multiagent-second:0.1〜0.8→ashigaru1〜7+gunshi-second / hermes-honbucho:0.0→honbucho

**計11件(SecondPC分)。**

## 三分 (実測)

- ①両方に在る(11件・一致)= shogun-second, karo-second, ashigaru1, ashigaru2, ashigaru3,
  ashigaru4, ashigaru5, ashigaru6, ashigaru7, gunshi-second, honbucho
- ②tmuxにのみ在る = **0件**
- ③registryにのみ在る = **0件**

**∴ @agent_idの集合(unique値)としてはtmuxとregistryは完全一致(11種)。差は「重複」の形でのみ現れる
(下記⒞)。**

## ⒞ @agent_id重複 (全数・実測)

**重複=1組のみ**: `@agent_id=shogun-second` が2 pane に付与されている=
- `%2 shogun-second:0.0` (★正・登録されたtmux_target★)
- `%13 hermes-gunshi-second:0.0` (★誤・registry未記載★)

他の10種(honbucho/karo-second/ashigaru1〜7/gunshi-second)は各1 paneのみ、重複なし。

## ⒟ 重複時の先着順 (実測・list-panes -aの既定反復順=session作成/attach順であって名前順ではない)

**`hermes-gunshi-second:0.0`(誤)が`shogun-second:0.0`(正)より★先に★列挙される**
(上記⒜出力の1行目と12行目を参照)。

**∴ もし「先頭一致で逆引きする道具」(例=`tmux list-panes -a | grep "@agent_id=shogun-second" | head -1`
の類)が存在すれば、★誤った方(hermes-gunshi-second:0.0)を返す★。これは実測であり、道具自体が
存在するかは当職の確認範囲外(足軽2号の是正工区が対象)。**

## 【本工区で己が直した誤り】

初稿でtmux全12paneをそのまま母集団として登録全20件(MainPC9+SecondPC11)と突合しようとしたが、
registry自身のnotesに「MainPC分はtmux検証不可」と明記されている事に気付き、母集団をSecondPC分
(11件)のみに絞り直した(比較不能な物を比較対象に含めていた誤りを是正)。

## ★母集団漏れの自己申告★

1. MainPC側のpane/registry突合は当職の権限・可視範囲外のため未実施(登録notesが「advisory のみ」
   と明記する理由そのもの)。
2. registryの`reserved_gaps`(ashigaru4欠番の説明的注記)は`panes[]`の実体ではないため母集団から
   除外した——除外の判断自体を明記する(単純なgrep一致では紛れ込み得た)。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、tmux @agent_id とregistry突合(母集団把握のみ)への応答。tmux操作・hermes-*編集は一切なし。

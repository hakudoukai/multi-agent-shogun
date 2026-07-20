# DD-192 (draft v3) — 二重監査標準の正本化: Codex+Hermes二者体制・Gemini監査経路廃止・読み替え規則

- **提案番号**: DD-192(相談役監査seq131810 観点3=採番非衝突PASS済)
- **版**: draft v3(v2=057e5e4c…はseq132099で8観点PASSだが§4のidentity conflation1点でREDO判定、改稿指示seq132104に基づき改稿)
- **起草**: 将軍main(GO8【#8】、執行令 pc_handshake seq131391 id=7f487aae、理事長裁定 session_minutes c564b6f4)
- **status案**: draft v3 → 委員長 project_documents 登録(原本byte一致) → 相談役差分再監査 → 理事長確認 → active
- **category案**: governance / audit
- **related_dds**(参照列挙のみ): DD-179、DD-154、DD-155。※各DDの処遇(矛盾解消・supersede要否・時期)は本DDでは一切決めない。別監査/別裁定の所掌とする。

## 1. 目的

pc_handshake seq110495 委員長裁定(2026-07-08 09:33、理事長指摘による裁定修正)が定めた監査標準が、
handshake上の裁定のみで文書正本に未反映のまま運用されてきたgapを解消する(台帳大掃除 再検証工区 §1-#14
是正1・相談役検分指摘「文書上のGemini監査必須との衝突」への根治)。本DDは同裁定の内容を変更せず、
**逐語転記**により正本化する(v1の編集要約方式はseq131810で転記非忠実と判定されたため撤回)。

## 2. 決定内容(seq110495 裁定全文の逐語転記)

以下は pc_handshake seq110495(from=iincho, 2026-07-08 09:33:39+09)の content 全文を無編集で転記したものである。
本DDの規範的内容はこの転記文それ自体であり、本DDによる追加・削除・拡張・恒久規範化は行わない。

> \# [委員長] seq110491 裁定修正 (理事長指摘 2026-07-08)
>
> 理事長指摘により以下を修正する。
>
> \#\# 撤回(seq110491の項4・項の一部)
> - 「Gemini復旧検知を環境部長L1監視に追加」=撤回。監視対象に加えない。
> - 「Gemini復旧後に追監査して三者化」=撤回。追監査は予定しない。
>
> \#\# 確定分類
> - third PCの旧Gemini監査経路(audit_gemini.sh)=★decommissioned(廃止確定)★。一時障害ではない。保存済み再走状態(evidence/tmux_vision_v02_gemini_reaudit/)は履歴証跡として保全のみ(再走前提を外す)。
> - ★以後の二重監査の標準構成=Codex(軍師)+Hermes(相談役)★。過去DDや指示書に「Codex+Gemini監査」とある場合も、Gemini部分はHermesで読み替える(個別に委員長裁定を仰ぐ必要なし)。
> - 現存するGemini利用=MainPC研修部長レーン(gemini-3.5-flash・動画解析・費用例外$20)のみ。監査用途とは別系統であり本修正の影響を受けない。
>
> \#\# 不変
> - seq110491の項1〜3(gunshi続行/Hermes即routing/二者verdictで実装GO上申)は不変。
> - 判定記録への経緯明記(Gemini経路廃止によりHermes代替)も不変。

### 2.1 参照: 上記「不変」が指す seq110491 項1〜3(逐語転記・参照用)

seq110495が「不変」と指定する seq110491(from=iincho, 2026-07-08 09:31:18+09)の項1〜3は以下のとおり
(参照用転記であり、seq110495が撤回した項4等は本DDの規範対象外)。

> 1. gunshi(Codex)監査=続行(verdict着信次第報告)。
> 2. Hermes相談役=代替第三者として即routing(監査対象=v0.2全文+委員長所見2点+前回gemini row 973f95f5をrefとして供給)。
> 3. 実装GO判定=★Codex+Hermes二者のverdictが揃った時点★で委員長が理事長へ上申(Gemini復旧を待たない)。

## 3. 出典・証跡

- 正本裁定: pc_handshake **seq110495**(委員長裁定 2026-07-08 09:33:39+09)。§2の転記元。2026-07-21にlive DBから再取得。
- 不変条項の参照元: pc_handshake **seq110491**(同 09:31:18+09)。§2.1の転記元。
- 誤出典の撤回記録: 「85b541b5 §8」出典説は誤り(同§8=上りメッセージ表記規則、Gemini言及ゼロ)。
  再検証工区 §1-#14 是正1で撤回済(worker/reports/ledger-reverify-20260720.md、relay/ledger-cleanup-20260720@a0e525a3)。
- DD化の発令: 理事長GO8裁定「推奨どおり」(session_minutes c564b6f4)+委員長執行令 seq131391【#8】。
- 改稿経緯:
  - v1(sha256=776de3ebf4cbb49fce0f23482907df395a6a9d944d17db4c03d023524365412a)は相談役監査
    **seq131810 VERDICT: REDO**(転記非忠実・related_dds自己矛盾の2 BLOCKING)→委員長改稿指示**seq131817**によりv2へ改稿。
  - v2(sha256=057e5e4c18b4b1612e6ecbd8cf36541e8966d195aa637e1d5d2f28ce63e8d510)は相談役再監査
    **seq132099**で前回是正8観点=全PASS(逐語一致・byte一致6097bytes・二重実装チェックPASS)だが、§4のidentity conflation
    (hermes2を相談役と誤記。実mapping=hermes2→環境部長、相談役=hermes/hermes-main)1点でREDO→委員長改稿指示**seq132104**
    により本v3へ改稿(当該運用細則文の除去+title精密化+role-ID整合guard追加、他は不変)。

## 4. 適用範囲と実務効果

- 読み替え規則の適用対象は原裁定の文言どおり「**過去DDや指示書**」であり、本DDによる対象拡張はない。
  該当文書は文言修正なしで、Gemini部分をHermesに読み替えて執行する(個別裁定不要。DD-179は適用実例)。
- **GREEN-TRUTH整合の明記**: HermesはGemini legの代替であり、軍師Codex実監査row・視覚層・その他既存の
  Completion Definitionを代替・緩和しない。本DDは監査の**構成**のみを定め、監査verdictの効力・実証層・
  効力条件は既存規則のまま変更しない。
- ※main_pc Hermes leg断時の代替routing等の**運用細則は本DDの範囲外**であり、既存の再検証工区§2-#17正本へ一元化する
  (v2まで本節に混入していた当該運用文はidentity conflation是正に伴いv3で除去。本DDは監査の構成規範のみを扱う)。

## 5. 監査観点(相談役向けメモ・v3)

- 転記忠実性: §2がseq110495 content全文と、§2.1がseq110491項1〜3と、それぞれ逐語一致すること
  (blockquote記号・md見出しエスケープ以外の差分ゼロ)。
- related_dds: 参照列挙のみで、DD-154/155の処遇・supersede時期の先決めが本文に存在しないこと。
- 採番の非衝突: seq131810観点3でPASS済(design_decisions上DD-192=0件)。二重実装(active競合)なしの再確認。
- 証跡固定: 本v3原本sha256を提出証跡とし、委員長登録後のDB full_text sha256とbyte一致すること
  (登録メモの本文追記は行わない=seq131817是正4)。
- **role-ID整合guard**: 本文中の役職名⇔technical IDが live role mapping(shim/hakudokai/hakudokai_fukuincho_reverse_poll.py:
  hermes2→環境部長 / hermes・hermes-main→相談役)と矛盾しないこと(v2でhermes2を相談役と誤記したidentity conflationの再発防止)。

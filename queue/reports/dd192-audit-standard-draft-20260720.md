# DD-192 (draft) — 二重監査標準の正本化: Codex+Hermes二者体制・Gemini廃止・読み替え規則

- **提案番号**: DD-192(採番根拠: 2026-07-20 21:2x JST live実測で design_decisions の最大 decision_code=DD-191/190件。委員長にて採番衝突の最終確認を乞う)
- **起草**: 将軍main(GO8【#8】、執行令 pc_handshake seq131391 id=7f487aae、理事長裁定 session_minutes c564b6f4)
- **status案**: draft → 委員長 project_documents 登録 → 相談役監査 → active
- **category案**: governance / audit
- **related_dds**: DD-179(監査mandate読み替えの適用実例)、DD-154/DD-155(pending: 本DDの読み替え条項で当面矛盾解消、レーン完了時にsupersede判断)

## 1. 目的

pc_handshake seq110495 委員長裁定(2026-07-08 09:33、理事長指摘による裁定修正)が定めた監査標準が、
handshake上の裁定のみで文書正本に未反映のまま運用されてきたgapを解消する(台帳大掃除 再検証工区 §1-#14
是正1・相談役検分指摘「文書上のGemini監査必須との衝突」への根治)。本DDは同裁定の内容を変更せず、
そのまま正本化する。

## 2. 決定内容(seq110495裁定の転記)

1. **audit_gemini.sh = decommissioned(廃止確定)**。以後、新規監査でGemini legを起動しない。
2. **二重監査標準 = Codex(軍師) + Hermes(相談役)の二者**とする。
3. **読み替え規則**: 過去のDD・指示書・タスク文書に「Codex+Gemini」等のGemini監査mandateが残存する場合、
   Gemini部分を**Hermesに読み替えて執行**する。読み替えに**個別裁定は不要**(本DDが包括根拠)。
4. **例外**: 研修部長の gemini-3.5-flash 利用は別系統として継続(監査二者体制の対象外)。

## 3. 出典・証跡

- 正本裁定: pc_handshake **seq110495**(委員長裁定 2026-07-08 09:33)。全文は2026-07-20に将軍mainが再取得済
  (worker/reports/ledger-reverify-20260720.md §1-#14、relay/ledger-cleanup-20260720@a0e525a3)。
- 誤出典の撤回記録: 「85b541b5 §8」出典説は誤り(同§8=上りメッセージ表記規則、Gemini言及ゼロ)。
  再検証工区 §1-#14 是正1で撤回済。
- DD化の発令: 理事長GO8裁定「推奨どおり」(session_minutes c564b6f4)+委員長執行令 seq131391【#8】。

## 4. 適用範囲と実務効果

- main_pc Hermes leg断(4db5b9ac: Copilot unauthorized/gpt-4.1 unlicensed、2026-07-11実測)の間の代替routing
  (Codex+相談役hermes2経由)は**本DDの範囲外**=運用細則として別途(再検証工区§2-#17、環境部長ライセンス調達と連動)。
- DD-179ほか「Codex+Gemini」mandateを含む既存文書は、本DD発効により文言修正なしでCodex+Hermes執行が正となる。
- 本DDは監査の**構成**のみを定める。監査verdictの効力・GREEN-TRUTH規律は既存規則のまま。

## 5. 監査観点(相談役向けメモ)

- 転記の忠実性: §2がseq110495の裁定内容に対し追加・削除・拡張をしていないこと。
- 採番の非衝突: DD-192が未使用であること。
- related_dds の妥当性(DD-154/155のpending処遇は本DDでは決めない)。

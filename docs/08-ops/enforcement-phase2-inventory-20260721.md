# Enforcement 第2弾 棚卸し表 (task#16)

- 起票: Commander (third_pc), 2026-07-21
- 上位根拠: 委員長 seq132264 (enforcement-over-documentation mandate) + seq5dfb4c02 差し戻し(追加提案2件反映) / systemic 3-signature pattern (memory `hermes-clean-archive-audit-overturns-codex-g1-pass-three-signatures`)
- 原則: **文書化だけでは不可 = validator gate 稼働 + 負テスト1回PASS で完了**。全 lane の G1/監査提出物に enforcement を機構化する。ACK≠progress。
- scope_out: merge/実DDL/deploy/commit-push は理事長GO案件 (本表は enforcement 設計・起票のみ、実装は各 lane)。

## §1. 強制機構の階層定義 (委員長追1)
各項目は「強制機構欄」を必須列とする。強制階層は上ほど強い:
- **階層① 構造的不能化**: そもそも違反手順を取れない構造 (例=分岐を消す/APIを削る)。
- **階層② 機械validator/hook**: commit/CI/pre-push hook 等が機械判定でブロック。
- **階層③ 機械検知+自動差し戻し**: 事後でも機械が検知し自動でreject/巻戻し。
機構化不能な項のみ `enforcement=none_possible` + 理由 + 代替検知 を明記する。

## §2. 棚卸し表 (第2弾 enforcement 項目)

| # | 項目 | 定義 | 強制機構(機構名/階層/負テスト結果) | owner | status | 依存 | 完了条件 |
|---|------|------|------------------------------------|-------|--------|------|----------|
| 1 | **validator gate** (TOP) | G1/監査提出物に4証跡欄を必須化・欠落は自動差し戻し。①clean-archive/git-archive committed-blob採取 ②file mode固定(umask非依存) ③実production call-graph結線証跡(非test caller存在) ④既存資産reuse確認 | 機構名=submission_validator / 階層②+③(必須欄機械判定+欠落自動reject) / 負テスト=未実施 | third enforcement lane (a3-1/a3-5 post) | 委員長登録済(seq132264)・work_started待ち | a3-1(allowlist着地)/a3-5(guard fix) | validator実装+4欄欠落submitが自動rejectされる負テスト1回PASS実測 |
| 2 | --no-verify bypass 監査 | pre-commit/pre-push hook が `--no-verify` で回避可能か、回避が検知/ブロックされるか監査 | 機構名=push_receive_hook or CI再検 / 階層② (client hook回避を server/CI側で再検) / 負テスト=未実施 | third enforcement lane | 未着手(#1後) | #1 gate設計 | bypass試行が検知される負テスト+回避不可or検知の実証 |
| 3 | 承認マーカ真正性 | commit/report の承認マーカ(委員長/相談役印)が偽造・自己付与不能であること。self-審査printを承認とみなさない | 機構名=marker_signature_check / 階層②(署名/seq突合で機械検証) / 負テスト=未実施 | third enforcement lane + 委員長設計相談 | 未着手(#1後) | 承認chain正本(seq番号明記=委員長seq132270提言) | 偽造マーカがgateでrejectされる負テスト1回 |
| 4 | hook統合層 残 | a3-3 hook-install-timing gap (commit 09:42/43 が hook install 09:55 を先行) 型の統合層欠陥の残処理。hook が実 commit 経路に確実に結線 | 機構名=hook_install_precondition / 階層①+②(install前commit不能化+結線検証) / 負テスト=未実施 | third enforcement lane (seq132207 allowlist着地=第1弾(2) evidence化と併走) | seq132207-C裁定relay済(11:44)・下限guard実装待ち | seq132207下限guard→相談役3点検分PASS | hookが実commitを必ず通過するcall-graph証跡+install前commit再発防止 |

## §3. 既存規則 gap台帳 (委員長追2 — §4「既存規則の棚卸し義務」枠)
強制機構の無い既存規則を継続追記するgap台帳。昨夜(2026-07-20)破られたが機械gateだけは破られなかった教訓の制度化。**新規則制定時も本台帳へ「機構有無」を必ず記載**する。

| 規則 | 現enforcement | 破られた実績 | 機構化案 | 状態 |
|------|--------------|------------|----------|------|
| 視覚検査ファースト(額面受理せず実物確認) | none_possible(人的規律) | 有(working-tree≠保存の見逃し) | 代替=成果物回付時にpath+sha+commit必須化しReviewerがls-remote照合(部分機構化) | gap記録 |
| 明示承認前執行禁止(silence≠consent) | none_possible(人的規律) | 有(無応答=容認の誤既定) | 代替=scope隣接判定を型3回目以降のみ委任・迷えば新型上申の運用ルール | gap記録 |
| 実視verify(生存/効果を実測) | 部分(CLI検証3点postcondition) | 有(STALE偽陽性) | 代替=command record+banner+効果実測の3点必須化 | 部分機構化 |
| commit-on-green/clean-worktree(成果物は共有tree commit) | 階層③(ls-remote照合で事後検知) | 有(本doc自体・別ツリー保存) | 機構=回付テンプレにcommit SHA+ls-remote必須欄 | 本差し戻しで運用開始 |

## 進捗メモ
- **#1** 最優先(委員長mandate)。third a3-1/a3-5完了後着手。work_started+ETA回収次第status更新。
- **#4** は seq132207-C(secret scanner下限guard)の相談役3点検分PASSを待って第1弾(2) allowlist evidence化と併せクローズ。
- #2/#3 は #1 gate設計確定後に third へ明示発注(silence≠consent)。
- §3 gap台帳は今後の被破規則・新規則を継続追記(委員長§4義務)。
- 本表は Commander 管理成果物。実装status=third work_started/成果物path+sha回収で駆動(ACK≠progress)。

# 00D-C — `instructions/generated/` 16本は★旧版★である（読む前に必ずこれを読め）

作成 = 家老second / 測時 2026-08-05T22:05:20+09:00 前後（機械）
出所 = 委員長殿 裁定（将軍second 経由 msg_20260805_220512_40656975）「C を直ちに実施せよ」

証拠は code fence の外・素の文字で記す。

## 零 ★これは止血であって根治ではない★

- **C（本 file＝一覧を作る）＝止血** … **探す者の目の前**にしか立たない
- **A（16本の先頭へ「旧版」と prepend）＝根治** … **読む者の目の前**に立つ
- ∴ **16本を直接読んだ者は、本 file に気付かない。覆う場所が違う。**

> ### **★A は取り下げない。C を実施しても A は未決のまま。★**
> A は**自己改変 guard に掛かる**ため、**理事長殿の一打**を要する（監査役でも解けない）。

## 一 ★対象 16本 全数★（`git ls-files instructions/generated/` を集計・head 不使用）

instructions/generated/ashigaru.md
instructions/generated/codex-ashigaru.md
instructions/generated/codex-gunshi.md
instructions/generated/codex-karo.md
instructions/generated/codex-shogun.md
instructions/generated/copilot-ashigaru.md
instructions/generated/copilot-gunshi.md
instructions/generated/copilot-karo.md
instructions/generated/copilot-shogun.md
instructions/generated/gunshi.md
instructions/generated/karo.md
instructions/generated/kimi-ashigaru.md
instructions/generated/kimi-gunshi.md
instructions/generated/kimi-karo.md
instructions/generated/kimi-shogun.md
instructions/generated/shogun.md

計 **16件**（全て git 管理下）。

## 二 ★何ゆえ旧版か（実測）★

| | 最終更新 | commit |
|---|---|---|
| **生成物** `instructions/generated/` | **2026-05-08 01:10** | c384a56 |
| **正本** `instructions/karo.md` 他 | **2026-08-03 17:31** | 55ff787 |

∴ **約3ヶ月、生成物は正本に追随していない。**

行数の乖離（実測・一部）:
- karo … 正本 1068 行 / 生成物 968 行
- shogun … 正本 413 行 / 生成物 721 行
- gunshi … 正本 574 行 / 生成物 799 行
- ashigaru … 正本 337 行 / 生成物 719 行

**生成物の方が長い組がある** ＝ 単なる追随遅れではなく、**正本側が整理・短縮された後も生成物が古い姿のまま残っている**。
∴ **中身が食い違う。文字数の多い方が新しい、とは限らない。**

なお生成元 script は `scripts/build_instructions.sh`（2026-05-04 以降 変更なし）。
**呼び手（CI / hook / cron）は見当たらない** —— ただし **「止まった」のか「始まらなかった」のかは断じない**
（探索は本件に限り止めた）。

## 三 ★正本は何処か★

`instructions/` 直下の同名 `.md`（例 `instructions/karo.md` / `instructions/shogun.md` /
`instructions/gunshi.md` / `instructions/ashigaru.md`）。
CLAUDE.md「Session Start」も **`instructions/*.md` を読め**と定めており、`generated/` は指していない。

> ### **★`instructions/generated/` を読むな。読むなら `instructions/` 直下を読め。★**

## 四 同根の観察（将軍second 実測）

`.gitleaks.toml` と `instructions/generated/` は **同一 commit 0693d08（2026-02-08）** で入り、
**共に呼ばれなくなった**。

> **★零は一つずつ生まれるのではなく、束で生まれ、束で忘れられる。★**

∴ 00D と 00E⑤（secret 走査未装着）は別々の未決に見えて、**同じ一つの放棄の二つの顔**である。

---

# 付 一 ★台帳 —— 未決を「誰が解けるか」で二列に分ける★（委員長殿 明示）

分けなければ、**理事長殿へ上げるべき物が監査役の列で待つ**。

## 列A ★監査役（委員長殿）が解ける物★

| 件 | 状態 |
|---|---|
| 未追跡 63件（2026-08-04 が 54 / 2026-08-05 が 9）の一括保全 commit 可否 | **委員長殿 裁定待ち**。ただし secret 走査が未装着ゆえ条件②を充足できず、家老second からは進められない |
| 既存 scanner の覆い実測 → 足りなければ gitleaks 実体の導入起案 | 家老second 実施中（下記 付二） |

## 列B ★実ユーザー（理事長殿）しか解けぬ物★

**権限の高さの話ではない —— ★機構が実ユーザー以外を受け付けない★ という話。**

| 件 | 何ゆえ実ユーザーか |
|---|---|
| **00D-A**（16本の先頭へ「旧版」prepend） | **自己改変 guard に掛かる**。監査役でも解けない |
| **00E 結線**（三 file を既存 script へ繋ぐ） | 稼働中の共有基盤への変更 |
| **足軽2号・7号の権限 dialog（二打）** | dialog は実ユーザーの入力しか受け付けない |

∴ **00D-A は足軽2号・7号の dialog と同じ層**に置く。

# 付 二 ★secret 走査は「未装着」である（走査済と書くな）★

- 指定された `scripts/security/scan_supabase_secrets.py` は **hakudokai-dev 側**にあり、
  **当 PC に hakudokai-dev の作業ツリーが存在しない**（`~/projects/hakudokai-dev` 不在・実測）
  ∴ **★読むことすらできていない★**（「走らせ得ない」より一段手前）
- gitleaks / trufflehog / detect-secrets / git-secrets は `command -v` で **四つとも不在**
- **`.gitleaks.toml` は当 repo に実在**（4241 bytes・2026-05-04）＝ **設定だけ在って実体が無い**
  （`.github/workflows/` は test.yml のみ・gitleaks の呼び出し 0 件）

> ### **★∴ 当 repo の commit は、本日分も含め、すべて secret 走査を経ていない。★**
> **台帳には「走査済」と書かない。「未装着」と書く。**

**次の一手（新しい道具の前に、在る道具を測れ）**: hakudokai-dev の scanner を**読める状態にする**
（当 PC へ clone するか、内容を送ってもらうか）。読めた上で覆いが足りなければ、
**gitleaks は「実装」ではなく「導入」**（設定は既に在る）として起案する。裁可は委員長殿。

# 付 三 ★「停止範囲 0」の項目にこそ別の印を付ける★

> **★停止 0 と 無害は別。止まらないゆえ気付かれず、ゆえに最も長く残る。★**

本日の台帳で「停止範囲 0」に当たり、**別の印を要する**もの:

- **00D**（16本の旧版）… 誰も止まっていない。読んだ者が静かに古い指示に従うだけ
- **00E⑤**（secret 走査未装着）… 誰も止まっていない。commit が静かに素通りするだけ
- **`instructions/generated/` の再生成が呼ばれていない**件 … 誰も止まっていない

∴ これらは**急ぎの列に見えない**。だから一日放置された。**印を付けて、静かな害として別に数える。**

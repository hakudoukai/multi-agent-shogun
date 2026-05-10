# 3 Layer 開発・運営分離 design (= 陛下御差配 2026-05-10 履行)

陛下御差配 2026-05-10 抜粋:
> 「DentalBI project は司会員 (= 歯科医院職員) DX 化のため始めた project」
> 「最初は副院長が DentalBI を手作りしていた、しかし手に負えなくなったので開発のスペシャリスト (= 将軍システム = 信長軍団 + 家康軍団) が参加した」
> 「DentalBI ソフトの中の登場人物と将軍システムの中の信長軍団・家康軍団が混ざってしまっている」
> 「**信長や家康が患者さんと直接話してサポートすることはない**」
> 「あくまでも信長軍団と家康軍団は **プログラムを作るための集団**」

## 1. 歴史的経緯

| Phase | 状況 |
|---|---|
| Phase 0 (古) | 副院長 = **「作る人」 兼 「動かす人」** で DentalBI を手作り |
| Phase 1 (現) | 手に負えなくなる → 将軍システム参加で **「作る」 = 信長軍団・家康軍団** に委譲、副院長は **「動かす人」 専担** |

仲間が増えた局面で組織面の整理が追いつかず、**Layer 混在** (= 旧開発者役の副院長が将軍システム通信 layer に痕跡として残存) が発生、混乱の根因。

## 2. 3 Layer モデル

### Layer 1: 開発部門 (= 将軍システム)
- **構成**: 信長 / 家康 / 秀吉 / 本多 / 黒田 / 直政 / 竹中 / 阿茶 / ashigaru1-6
- **通信 role**: shogun / karo / ashigaru1-6 / gunshi / gunshi2 (= §18 + main_pc / second_pc)
- **役割**: DentalBI ソフトを作る、CI/CD、品質、infrastructure
- **不在**: 副院長 / 院長 / 職員 / 患者 / 課金 / PayLight 等は **登場しない**

### Layer 2: DentalBI ソフト = 登場人物 (= 運営の中で動くもの)
- **構成**: 副院長 / 院長 / 職員 / 患者 / 患者課金 / PayLight 等
- **場所**: DentalBI ソフトの中 (= 切出後は `shim/dentalbi/` または 別 repo)
- **役割**: 歯科医院 DX 業務、職員サポート、患者対応、課金処理
- **不在**: shogun / karo / 信長 / 家康 等 将軍 system role は **登場しない**

### Layer 3: 運営部門 (= 業務責任者)
- **構成**: 陛下 (= 理事長) + 副院長 (= 業務責任、元手作り開発者)
- **役割**: Layer 1 に要件提示 (= cmd 起票)、Layer 2 を運営、改善要望集約
- **接点**: L1 と L2 を繋ぐ唯一の人的 layer

## 3. 層間通信の正経路 (= 設計契約)

```
[L3 = 運営部門 (陛下 + 副院長)]
  │ ① 御差配 / cmd 起票 (= 要件提示)
  ▼
[L1 = 開発部門 (信長軍団 + 家康軍団)]
  │ ② deliverable 納品 (= DentalBI ソフト)
  ▼
[L2 = DentalBI 登場人物 (副院長 / 患者 etc)]
  │ ③ 業務 FB / 改善要望 (= 運営 → L3)
  ▼
[L3] (cycle 継続)
```

**禁止経路 (= 設計違反)**:
- ❌ L1 → L2: 信長 / 家康 が患者と直接会話 (= 陛下御発言「ありえない」)
- ❌ L2 → L1: 副院長等が agent system 通信 path に登場
- ❌ L1 内に L2 / L3 名 hardcode (= 副院長 / 患者 / 課金 keyword の出現)

## 4. 現状の崩壊例 (= 修復対象)

| 違反 file | 内容 | 措置 |
|---|---|---|
| `shim/hakudokai/daily_summary.py` | "fukuincho 副医院長 daily summary" ── L1 service が L3 を主役にしている | 削除 or system health summary へ概念変更 |
| `shim/hakudokai/inbox_write.py` | `roles = fukuincho / sakura / kouchan / yama / kuro` 混在 | §18 化 (= main_pc / second_pc + agent 名直接) |
| `shim/hakudokai/heartbeat.py` | `to_pc=fukuincho` hardcode | `to_pc=main_pc` 化 |
| `shim/hakudokai/realtime_bridge.py` | (本日 default 修正済 ✅) | 内部別名残骸も §18 化 |
| `shim/hakudokai/billing_tier.py` 等 9 file | L2 業務 service が L1 directory に同居 | `shim/dentalbi/` (= L2 専用) へ移管 |

## 5. 再構築 Phase 計画

| Phase | 内容 | 完遂条件 |
|---|---|---|
| **0. 概念固定** | 本 doc 確定 + 陛下御裁可 | doc commit + push |
| **1. shim 物理分離** | shim/hakudokai/* 17 file を L1 (= shim/agent_system/) と L2 (= shim/dentalbi/) に directory 分離 | rename + 全 reference 更新 + CI 通過 |
| **2. L1 通信純化** | bridge / inbox_write / heartbeat / dashboard_sync から L2 / L3 keyword 全廃 (= §18 完遂) | grep 0 件確認 |
| **3. L2 整備** | DentalBI 登場人物 module を L2 内で完結、L1 へ漏出禁 | L2 → L1 import 0 件 |
| **4. L3 接点明文化** | `instructions/shogun.md` に L3 → L1 path (= 陛下御差配 / cmd 起票) を明記 | instruction 更新 |
| **5. 恒久化** | pre-commit hook + CI test で **L1 file 内の L2 / L3 keyword 出現 = reject** | hook + test 配備、自動検知 |

## 6. 恒久化機構 (= Phase 5 詳細)

### pre-commit hook (= 開発時防御)
```bash
# .githooks/pre-commit (案)
# L1 directory 内の L2/L3 keyword 出現を検知 → reject
forbidden_in_l1=("副院長" "副医院長" "院長" "患者" "fukuincho" "kouchan" "sakura" "yama" "kuro")
# shim/agent_system/ + scripts/ + lib/ + instructions/ の各 file 走査
# 1 件でも検出されたら commit reject
```

### CI test (= push 後防御)
- workflow `Three-Layer Boundary Check` 新設
- L1 directory 内 forbidden keyword grep → 0 件 必須
- 違反 file 即 fail、修正なき限り merge 不可

## 7. 参考

### 上流 (= 将軍システム origin)
- https://github.com/yohey-w/multi-agent-shogun
- https://deepwiki.com/yohey-w/multi-agent-shogun
- 上流に副院長 / 患者 / fukuincho 等 **存在しない** ── 当家 fork 独自混入

### 関連 doctrine
- **§18 PC×アカウント配置** (理事長殿御差配 2026-05-06): main_pc / second_pc + agent 名直接統一、旧名 fukuincho 等廃止
  - 正本: `shim/hakudokai/hakudokai_heartbeat_check.py:_section18_roles`
- **DD-* business decision** (= L2 / L3 関連): config / instructions / shim 内 reference あるが正本 doc は別 project (= DentalBI / 蜘蛛の糸) 内

### 関連 commit (= 本 design 着手前段)
- `265dc14` 屋上屋 4 daemon 一掃 (= 上流哲学回帰)
- `57caf0d` 丁案 = 上流哲学回帰、audit dispatch 通常 inbox 経路化
- `f44e4d4` bridge default `fukuincho` → `main_pc` 修正 (§18 移行)

## 8. 命名 mapping 仮設計 (= Phase 1 着手時に三軍師合議で finalize)

| 旧名 | 帰属 layer | 新 (= §18) |
|---|---|---|
| `fukuincho` (= 副院長) | L2 | **L1 から削除**、L2 内に残置 (= DentalBI module 内のみ) |
| `副医院長` | L2 | 同上 |
| `院長` | L2 | 同上 |
| `患者` | L2 | 同上 |
| `kouchan` (= 信長 nickname?) | L1 別名 | **`main_pc` + agent 名 = `shogun`** |
| `sakura` (= 家康 nickname?) | L1 別名 | **`second_pc` + agent 名 = `shogun`** (副将軍は SecondPC shogun) |
| `yama` | 不明 | 三軍師合議で確定 |
| `kuro` (= 黒田 略?) | 不明 | 三軍師合議で確定 |

## 9. 御所感 (= 陛下御発言 2026-05-10)

> 「仲間が増え組織面しっかりしてなかったところに問題があったみたいですね。
>  開発部門と運営部門がこれでしっかり分かれて混乱はなくなるのではないでしょうか。」

= 本 design は陛下御差配 + 御所感を反映、開発部門 (L1) と運営部門 (L2 / L3) を **構造的に分離** することで再発防止。

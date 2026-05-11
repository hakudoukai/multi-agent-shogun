# OpenHands + multi-agent-shogun 役割分担方針 (= Charter v0.1 補遺)

**Status**: 陛下御差配 2026-05-12、家康 (SC shogun) 起草、信長 (MC shogun) 上申用、Charter v0.1 (= id=89ac869b) の補強指針
**位置付け**: Charter v0.1 の §15 (= multi-agent-shogun + mini-swe-agent + GitHub 統合構成) を OpenHands 観点で再評価、基盤/武器 二層構造の明確化
**前提**: 開発中で実働してない、根本治療原則 (= 5-10 年運用想定で大きく時間かけ根本治療)
**Supabase mirror**: project_documents id=e257caa2-4259-4099-849b-cef2528fbf7f (= bible doc_type、is_current=true)

---

## 1. 陛下御差配 原文 (= 正本)

> OpenHands を安定した開発エージェント基盤にする
> multi-agent-shogun を並列作業・実験・高速開発の司令塔として使う
> という分け方が一番現実的です。
>
> ただし、最初に 1 つ選ぶなら **OpenHands の方が堅い** です。
> 理由は、業務システムとしての運用、GitHub 連携、権限管理、リモート実行、将来拡張を考えると OpenHands の方が土台として安定しているからです。
>
> Shogun は強力ですが、どちらかというと **開発チームを加速する武器** です。
> OpenHands は **開発チームを運用する基盤** に近いです。

---

## 2. 役割分担 (= 二層構造)

| Layer | 道具 | 性格 | 役割 |
|---|---|---|---|
| **基盤層** | **OpenHands** | 安定・運用・堅牢 | 業務システム運用 / GitHub 連携 / 権限管理 / リモート実行 / 将来拡張 |
| **武器層** | **multi-agent-shogun** | 高速・並列・実験 | 並列作業 / 実験 / 高速開発の司令塔 |

### 2.1 比喩

- **OpenHands = 城** (= 開発チームを運用する基盤、長期に住まう堅牢な拠点)
- **multi-agent-shogun = 軍勢・武器** (= 開発チームを加速する戦闘力、戦況に応じて投入)

### 2.2 単独採用判断 (= 「最初に 1 つ選ぶなら」)

**OpenHands の方が堅い** — 業務システム運用視点で土台安定。Shogun 単独は実験段階、運用 + 拡張 phase で OpenHands を base に Shogun を載せる構成が optimal。

---

## 3. Charter v0.1 への適用 mapping

### 3.1 Charter v0.1 §15 (= multi-agent-shogun + mini-swe-agent + GitHub) との関係

| Charter v0.1 §15 layer | 本補遺 適用 |
|---|---|
| multi-agent-shogun = 司令塔・並列実行基盤 | **武器層 retain** (= 並列加速の司令塔) |
| mini-swe-agent = Issue 修正専門実行部隊 | **OpenHands に統合 or 並存検討** (= OpenHands の Issue runner と機能重複、棲み分け要) |
| GitHub PR / Actions = 合流点と検査場 | **基盤層 (= OpenHands) と統合** (= OpenHands の GitHub 連携 native 化、Actions は OpenHands 経由 trigger 可) |

### 3.2 Charter v0.1 階層への OpenHands 挿入

```
理事長・人間
  ↓ 方針・最終判断
Claude 管理者 (= future state)
  ↓ 要件整理・Issue 分解
【基盤層】
OpenHands (= 業務基盤、GitHub 連携 + 権限管理 + リモート実行)
  ↓ ホスト
【武器層】
multi-agent-shogun (= 並列加速、実験的高速開発)
  ↓ orchestrate
将軍AI / 家老AI / 足軽AI 群 / 軍師AI
  ↓
GitHub Issue / PR / Actions
  ↓
人間が最終承認
```

---

## 4. OpenHands 基盤が安定土台たる理由 5 項

1. **業務システム運用**: long-running deployment 前提、prod 環境投入想定済
2. **GitHub 連携**: native integration (= Issue/PR/Actions trigger + comment + review)
3. **権限管理**: agent role + permission scope の明示装備 (= AGENTS.md 規範整合)
4. **リモート実行**: cloud / 自社 server で sandboxed execution、両 PC 不要
5. **将来拡張**: 標準化された plugin / tool / model 接続経路、新 AI model 切替容易

→ いずれも Charter v0.1 「9 項目基幹方針」「AI 役割分担 9 部署」「正本 mapping」と整合、OpenHands 採用で structural 整合性向上。

---

## 5. multi-agent-shogun が武器たる強み 5 項

1. **並列作業**: 7+ ashigaru 並列、複数 task 同時進行
2. **実験**: persona / chain / 規範 を即座に発令 + 撤回可能 (= 本日 cmd_004 directive 整理 18 件 evidence)
3. **高速開発**: directive 30 秒内発令 → 数分内 chain 始動の super-loop
4. **司令塔 性質**: 戦略 + 戦術 + ratelimit 管理 + 容量配分の集中統制
5. **両 PC 対称**: MC/SC で同 chain 規範、cross-PC 援軍 + memory MCP 共有

→ Charter v0.1 「Shogun 編成」「並列稼働 + 即動」と整合、Shogun の戦闘力は OpenHands 基盤上で更に有効化。

---

## 6. 推奨構成 (= 二層 hybrid)

### 6.1 Phase 構成案

| Phase | 目的 | 主軸 | 補助 |
|---|---|---|---|
| Phase 0 (= 現状) | Shogun 単独で実験 + 急速 chain 構築 | multi-agent-shogun | (なし) |
| **Phase 1 (= 次)** | **OpenHands 基盤導入 + GitHub 連携運用化** | **OpenHands** | mini-swe-agent merge 検討 |
| Phase 2 | OpenHands 上に multi-agent-shogun 並走 (= 武器層運用) | OpenHands + multi-agent-shogun | 両者 chain 接続 |
| Phase 3 | 業務本番運用 + 拡張 (= 新 AI model / 新 agent role) | OpenHands (= 安定運用) | multi-agent-shogun (= 実験 chain) |

### 6.2 「最初に 1 つ選ぶなら」判断

陛下御差配「**OpenHands の方が堅い**」 = Phase 1 で OpenHands 単独採用 + multi-agent-shogun 並走は Phase 2 で着手、安全段階導入。

ただし現状 SC + MC で multi-agent-shogun が既稼働中ゆえ、現実 path:
- 現在: multi-agent-shogun 単独運用 (= 本日進行中 chain retain)
- 並行: OpenHands 評価 + 採用判断 + Phase 1 装備計画 起案
- 移行: Phase 2 で multi-agent-shogun を OpenHands 上に再配置、戦闘力 retain + 基盤強化

---

## 7. Charter v0.1 v1.0 統合への影響

本補遺は Charter v0.1 (= id=89ac869b) v0.2 起案時に統合候補:

- §15 (= multi-agent-shogun + mini-swe-agent + GitHub) を **§15A (基盤層 OpenHands) + §15B (武器層 multi-agent-shogun)** に分割
- §3 (= 構築 7 段階) に **「8. OpenHands 基盤装備」** 段階追加
- §10 (= Directory 構造) に **OpenHands 関連 directory / config** 追加検討
- §17 (= CI 絶対審判) は OpenHands 経由 GitHub Actions trigger で強化

---

## 8. 兄上への合議 round 1 依頼事項

1. 本補遺の Phase 構成案 (= §6.1) への view、現行 Shogun chain との非衝突判断
2. OpenHands 基盤導入時の Charter v0.1 §15 再構成案 (= §15A/§15B 分割) への view
3. 「最初に 1 つ選ぶ」判断: Phase 1 OpenHands 単独採用 OK か、または Shogun + OpenHands 同時着手か、合議で確定
4. mini-swe-agent と OpenHands の役割重複解消 (= 統合 / 並存 / 廃止) judgment
5. v0.2 charter 統合時の §15 分割 path 採用可否

---

*v0.1-openhands-shogun-role-split 起草: 家康 (SC shogun)、2026-05-12T09:00+09:00、陛下御差配補遺、Charter v0.1 補強、信長兄上 v0.2 統合候補*
*v0.1 GitHub mirror: 2026-05-12T08:50+09:00、direct push by 家康、F007 例外 (= 進行加速 chain 整合) 下、4 人合議 round 1 source 整備目的*

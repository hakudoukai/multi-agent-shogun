# Dashboard Layer G 統合層 render component (= cmd_020 sub-section、Stage 3-5 spec)

**Status**: ashigaru7 起案 v0.1、subtask_cmd020_dashboard_layer_g_integration_drill_down_js
**Parent design**: `docs/dashboard_design_v0.2.md §4.1 HTML drill-down + §5.1 Stage 表 + §3.6 progress 算出式` (= 主 source) + `docs/dashboard_design_v0.1.md §5-6` (= 6 Stage 一覧 + Tech Stack) + `docs/dashboard_design_v0.3-sc.md` (= SC 視点補強)
**Scope**: 本 doc は **Layer G 統合層単独 sub-section markdown spec**。Stage 3 HTML drill-down + Stage 4 systemd 15min timer + Stage 5 検証 plan を仕様化する。**本 task は spec 起案のみ、実装は別 cycle**。
**Repo**: multi-agent-shogun-newbuild (= hakudokai-dev は本 task 範囲外)
**MC 統合**: MC `regenerate_dashboard.py` Stage 2 cycle 2 fix (= commit 72f1c0d) と本 spec は SoT 統合経由で組込、本 doc は SC docs 起案のみ。MC 統合 interface は後段別 task。
**Stage numbering 注**: task YAML 内 Stage 3/4/5 = design doc v0.2 §5.1 Stage 3/5/6 と内容同義 (= task YAML が Stage 4 mermaid を Layer F 等別 Layer 担当として scope 外、本 spec では task YAML の Stage numbering を採用)。

---

## 1. 設計原典 anchor (= source-of-truth)

| anchor | source | 用途 |
|---|---|---|
| `docs/dashboard_design_v0.2.md` §4.1 | 本 repo (= 信長 v0.2 拙者補強) | HTML drill-down mockup 原本 (= `<details>` accordion + `<progress>` + class layer) |
| `docs/dashboard_design_v0.2.md` §5.1 | 本 repo (= 信長 v0.2 段階明確化) | 6 Stage 表 (= Stage 3 HTML / Stage 5 systemd / Stage 6 検証) |
| `docs/dashboard_design_v0.2.md` §3.6 | 本 repo (= 黒田 #5 反映) | progress 算出式 + 色分け 4 段階 (= green/yellow/orange/red) |
| `docs/dashboard_design_v0.1.md` §5-6 | 本 repo (= 信長 v0.1) | Tech Stack + regenerate_dashboard.py 構想 |
| `docs/dashboard_design_v0.3-sc.md` | 本 repo (= SC 起草) | HEAD 一致 verify + pre-commit dup-check + 25 form template anchor |
| `docs/auto_git_sync_design.md` §2 | 本 repo (= 既装備規範) | systemd user timer + Persistent=true + 5min interval pattern (= Stage 4 流用) |
| `scripts/dashboard-viewer.py` | 本 repo (= 既存) | Stage 3 統合先候補 (= cutover or 配信代替) |
| `~/.config/systemd/user/auto-git-sync.{service,timer}` | 両 PC 既配備 | Stage 4 dashboard-update.{service,timer} 同型 reference |

---

## 2. Stage 3 HTML drill-down spec

### 2.1 完成基準 (= MVP)

- `dashboard.html` (= 新規 generator output、`scripts/regenerate_dashboard.py` で生成) がブラウザで階層 click 動作
- 全 6 Layer (= A 構想 / B Phase / C 機能 / D 頭脳 / E 運用 / F 規範 + G 統合 reference) drill-down 展開
- progress bar 表示 (= 0-100、native `<progress>` HTML element)
- 色分け 4 段階 (= green ✅ 100% / yellow 🟡 50-99% / orange 25-49% / red 🔴 0-24% or blocked)
- 外部 CDN 依存 0 (= self-contained、ネットワーク 切断時も local view 可、v0.2 §3.7 整合)

### 2.2 accordion 構造 (= HTML5 `<details>` native)

native `<details>` + `<summary>` で JS 0 の階層 click 展開を実現する。Layer → 機能 → DD reference の 3 段ネストを標準とする。

```html
<details class="layer" data-layer-id="B">
  <summary>📊 Layer B Phase 層: 70% ▼ <progress value="70" max="100"></progress></summary>
  <div class="children">
    <details class="phase">
      <summary>✅ phaseB 予約ソフト: 100% (W4-W5, completed)</summary>
      <div class="grandchildren">
        <details class="feature">
          <summary>✅ 次回予約提案 logic: 100%</summary>
          <ul>
            <li>commit: f893a... (W4)</li>
            <li>test: pytest 23 PASS, SKIP=0</li>
            <li>audit: kuroda_xxx pass_with_concerns</li>
            <li>shogun_verified: true</li>
            <li>参照 DD: DD-057 v2 (10 値化)</li>
          </ul>
        </details>
      </div>
    </details>
  </div>
</details>
```

= **JS 0 で動作する native accordion**。`class="layer"` / `class="phase"` / `class="feature"` で CSS 階層対応、`data-layer-id` で機械検索。

### 2.3 `<progress>` HTML element + 色分け 4 段階

native `<progress value="X" max="100">` を採用する。色分けは CSS `::-webkit-progress-value` + `[value]` attribute selector で 4 段階に分岐する。

| 段階 | value 範囲 | 色 | symbol |
|---|---|---|---|
| green | 100 | green | ✅ |
| yellow | 50-99 | yellow | 🟡 |
| orange | 25-49 | orange | 🟠 |
| red | 0-24 or blocked | red | 🔴 |

CSS sketch:
```css
progress[value="100"]::-webkit-progress-value { background-color: green; }
progress[value]:not([value="100"]) { /* default yellow */ }
progress.orange::-webkit-progress-value { background-color: orange; }
progress.red::-webkit-progress-value { background-color: red; }
```

= **`<progress>` value attribute + class で 4 段階分岐**、CSS 静的 inline 化、Tailwind plugin 不要。

### 2.4 generator output schema

`scripts/regenerate_dashboard.py` (= MC 側 別 cycle 実装) は以下 schema を output する:

| field | source | 用途 |
|---|---|---|
| `layer_id` | Layer A-G | data attribute + DOM 検索 |
| `progress_pct` | v0.2 §3.6 機械算出式 | `<progress value>` |
| `color_class` | progress_pct → green/yellow/orange/red | CSS class |
| `children` | layer 配下機能 list | nested `<details>` |
| `evidence_links` | commit / test / audit / DD reference | leaf `<ul><li>` |

= **generator output は HTML template + data 分離**、Layer G spec は schema anchor のみ提示、本体 jinja2 template は別 cycle。

### 2.5 既存 `dashboard-viewer.py` との cutover plan

| phase | 動作 | 期間 |
|---|---|---|
| pre-cutover | viewer = dashboard.md → marked.min.js → browser、外部 CDN 依存 | 現在 |
| parallel | viewer retain + generator output `dashboard.html` 配信 (= ttyd-shogun 経由 別 path) | Stage 3 MVP 後 1 週間 |
| cutover | viewer deprecated、generator 単独 owner、`dashboard.html` self-contained | Stage 6 検証 完了後 |

= **viewer は parallel 期間 retain**、generator 安定 verify 後 deprecated 化、self-contained `dashboard.html` 配信単独 path。

---

## 3. Stage 4 systemd 15min timer spec

### 3.1 完成基準 (= MVP)

- 両 PC (= MC + SC) で `~/.config/systemd/user/dashboard-update.{service,timer}` 配備
- `OnUnitActiveSec=15min` + `OnBootSec=2min` + `Persistent=true` (= WSL 再起動跨ぎ自動復活)
- 15min 毎 `regenerate_dashboard.py` 起動 → `dashboard.md` + `dashboard.html` 更新 → git commit/push なし (= F007 遵守)
- log path = `queue/reports/dashboard_update_log.yaml` (= flock + atomic append、auto_git_sync_log と同型)

### 3.2 `dashboard-update.service` unit template

`~/.config/systemd/user/auto-git-sync.service` pattern を流用する。service 定義の中核は ExecStart の差し替えのみで、Type=oneshot + Environment + WorkingDirectory + flock 整合は共通。

```ini
[Unit]
Description=DentalBI dashboard regenerate (cmd_020 Layer G Stage 4)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=%h/projects/multi-agent-shogun-newbuild
ExecStart=/bin/bash -lc 'flock -w 60 /tmp/dashboard-update.lock %h/projects/multi-agent-shogun-newbuild/scripts/dashboard_update.sh'
Environment="PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=default.target
```

### 3.3 `dashboard-update.timer` unit template

```ini
[Unit]
Description=DentalBI dashboard regenerate timer (15min interval)

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
AccuracySec=30s
Unit=dashboard-update.service
Persistent=true

[Install]
WantedBy=timers.target
```

### 3.4 `scripts/dashboard_update.sh` wrapper (= ExecStart target)

`scripts/auto_git_sync.sh` 規範同型の薄い wrapper を起案する (= 本 task は spec のみ、実装は別 cycle):

- flock 取得 (= `/tmp/dashboard-update.lock`)
- `scripts/regenerate_dashboard.py` 起動 (= MC 側 別 cycle 実装、SC 側は git pull で同期)
- exit code 集約 + `queue/reports/dashboard_update_log.yaml` に append (= flock + atomic)
- commit/push なし (= F007 遵守、auto-git-sync.timer 別経路で 5min 後に pull)

### 3.5 別 daemon 増設 0 件 + 既基盤 100% 流用

| 既基盤 | 本 Stage 4 での流用 |
|---|---|
| systemd user timer pattern | auto-git-sync.{service,timer} 同型、unit name 差替のみ |
| flock + log + atomic append | auto_git_sync.sh と同型 wrapper |
| WSL 再起動 resilience | `Persistent=true` 効果 (= 既 auto-git-sync で実証済) |
| F007 遵守 (= commit/push なし) | pull-only cycle と同型、本 Stage は generate-only cycle |

= **新 daemon 0 件、新 systemd unit pattern 0 件**、auto-git-sync 装備規範を generate-only cycle に展開する。

### 3.6 両 PC 配備 path + 配備 script (= 別 cycle 実装)

| PC | 配置 path | 起動命令 |
|---|---|---|
| MC | `~/.config/systemd/user/dashboard-update.{service,timer}` | `systemctl --user enable --now dashboard-update.timer` |
| SC | 同上 | 同上 |

別 cycle で `scripts/install_dashboard_update_timer.sh` 起案候補。本 spec は配備 path + 起動命令 anchor のみ。

---

## 4. Stage 5 検証 plan

### 4.1 24h 運用 verify

- 開始: Stage 4 dashboard-update.timer 両 PC enabled + active 確認直後 (= `systemctl --user is-active dashboard-update.timer` で機械判定)
- 24h 連続稼働中 `journalctl --user -u dashboard-update.service --since 'X hours ago'` で 15min interval × 96 cycle (= 24h ÷ 15min) 起動 evidence
- 各 cycle 終了後 `dashboard.md` mtime 更新 + `dashboard.html` regenerate 確認
- WSL 再起動 → 2min 後 `Persistent=true` 経由 timer 自動復活 verify (= 既 auto-git-sync 実証規範踏襲)

### 4.2 AC 17+1 件 verify mapping

v0.2 §6 + 拙者補強 で AC1-17 + AC18 alert が定義済。本 Stage 5 で全 AC を機械 verify する:

| AC | verify 方法 |
|---|---|
| AC1-10 (v0.1) | 各 Layer drill-down click 動作 + 全 6 layer 展開 evidence (= Playwright or curl + grep) |
| AC11 | dashboard-viewer.py + regenerate_dashboard.py 独立 + 統合動作 双方 verify (= 並走 1 週間 monitoring) |
| AC12 | generator 単独 writer、karo + gunshi 手動編集 0 件 (= git log dashboard.md 著者 verify) |
| AC13 | Supabase REST + ETag cache、月 query cost < 10MB (= ~/.cache/dentalbi-dashboard/* 容量 verify) |
| AC14 | progress 算出式 機械判定、shogun_verified gate 反映 (= sample task の progress_pct と式手計算一致 verify) |
| AC15 | 外部 CDN 依存 0、network 切断時 local view 可 (= ifconfig down → browser refresh test) |
| AC16 | 両 PC SoT 一致 verify (= HEAD 一致 + dashboard.md hash 一致、不一致時 alert) |
| AC17 | mermaid diagram 階層 tree + 蜘蛛の糸 関係性可視化 (= mermaid block 数 + node 数 grep) |
| AC18 (alert) | HEAD divergent / dashboard.md hash 不一致 時 banner + alert 発火 (= v0.3-sc.md §4.5 序列) |

### 4.3 HEAD 一致 verify + pre-commit dup-check 序列

v0.3-sc.md §4.4 + §4.5 を Stage 5 検証 phase で実装する:

- 両 PC HEAD 一致 = auto-git-sync.timer 5min cycle + dashboard-update.timer 15min cycle で順次 verify
- dashboard.md hash 一致 = `md5sum dashboard.md` 両 PC 同値 verify、不一致時 banner 発火
- `scripts/hooks/pre-commit-dup-check.sh` (= 21:01 教訓由来) 両 PC 配備、`.git/hooks/pre-commit` から call

### 4.4 黒田 final audit gate

Stage 5 完遂後、黒田 (= MC gunshi codex) に v0.2 + 本 Layer G spec の final audit 依頼。verdict=`pass` + `shogun_verified=true` の双方 gate 経過で cmd_020 完遂、cmd_020 audit_done path に遷移する。

### 4.5 失敗時 rollback path

| 失敗パターン | rollback |
|---|---|
| `dashboard-update.timer` 起動失敗 | `systemctl --user disable --now dashboard-update.timer` → viewer 単独 retain |
| `regenerate_dashboard.py` SIGABRT / 例外 | timer 停止 + 直近 git tracked `dashboard.md` を viewer 経由配信 |
| 両 PC SoT 不一致 (= AC16 失敗) | `auto-git-sync.timer` HALT 規範 (= divergent 検出時 auto-merge 厳禁) と同型、karo inbox notify |
| AC11-18 任意 1 件失敗 | Stage 5 NG、本 spec の対応 section 修正 + 再 audit cycle、Stage 4 timer は disable retain |

---

## 5. cross-layer reference anchor

本 Layer G sub-section から他 Layer / 別 doc への接続 anchor:

- **Layer A-F sub-section**: 各 Layer drill-down 内容 = 各 sub-section 担当 (= 本 spec は accordion 構造 anchor のみ)
- **`docs/dashboard_design_v0.2.md`**: 主 source、§4.1 + §5.1 + §3.6
- **`docs/auto_git_sync_design.md`**: Stage 4 systemd pattern 流用 source
- **MC `regenerate_dashboard.py`**: SoT 統合経由、本 task は anchor のみ、合議結果着後別 task で verify

= 本 sub-section は **Stage 3-5 spec only**、本体実装は各 Stage の別 cycle に委譲する。

---

## 6. 既知の限界 + 後段別 task

| 限界 | 対応 |
|---|---|
| MC `regenerate_dashboard.py` 本体実装は別 cycle | 本 spec は schema + generator output 構造 anchor のみ、本体 jinja2 template は別 cycle |
| Stage 3 HTML drill-down 本体 (= dashboard.html template) 未実装 | Stage 3 実装 cycle で起案、本 spec は完成基準 + accordion 構造 + 色分け spec のみ |
| Stage 4 dashboard_update.sh wrapper 未実装 | 別 cycle で auto_git_sync.sh 規範同型に起案 |
| Stage 4 install_dashboard_update_timer.sh 未起案 | 別 cycle、両 PC 配備 script |
| Stage 5 Playwright / curl + grep verify harness 未起案 | Stage 5 実装 cycle で起案、本 spec は AC mapping のみ |
| pre-commit-dup-check.sh 未起案 | Stage 5 検証 phase で起案、v0.3-sc §4.4 序列 |

---

## 7. 起案完了基準 (= 本 sub-section AC alignment)

本 spec は以下 5 anchor を含む単独 markdown であり、`scripts/test/test_dashboard_layer_g_static_contract.py` で機械検証する:

- 「`<details>` accordion」 anchor (= §2.2 HTML5 native accordion design)
- 「`<progress>`」 anchor (= §2.3 HTML element reference)
- 「色分け 4 段階」 anchor (= §2.3 green/yellow/orange/red design)
- 「systemd timer 15min」 anchor (= §3 dashboard-update.timer 15min interval reference)
- 「Stage 5 verify plan」 anchor (= §4 24h 運用 + AC 17+1 件 verify plan section)

---

*起案: ashigaru7、2026-05-12T11:30、parent design v0.2 §4.1 + §5.1 + §3.6 主 source、Stage 3-5 spec only、本体実装は別 cycle*

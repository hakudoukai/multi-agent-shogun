# apply --check once — fd945b3b patch on ae1d2a99 clean base（耐久記録・a2 / ashigaru2）

★本 file は current_order_18 (APPLY_CHECK_ONCE) で已に報じられた値の耐久化のみ。新たな測定は行っていない。★

出所: `queue/inbox/karo-second.yaml` msg_20260807_043619_1fde403a（足軽2号→家老second, 2026-08-07T04:36:19）

## ⑴ 実行command（逐語）+ cwd

```
cwd: /tmp/resimg-verify2-base-contrast-ae1d2a99-20260807
command: GIT_NO_LAZY_FETCH=1 git apply --check /home/hakudokai/projects/multi-agent-shogun/docs/incident_logs/2026-08-07_recovery_patch_fd945b3b_a1.patch
```

## ⑵ exit code

```
0
```

## ⑶ stdout/stderr

```
空（出力なし）
```

## ⑷ git status --porcelain（前後）+ HEAD sha

| | porcelain | HEAD |
|---|---|---|
| 前 | 空（0行） | `ae1d2a9932ace06693a02b81e20a15284858826b` |
| 後 | 空（0行） | `ae1d2a9932ace06693a02b81e20a15284858826b` |

前後とも0・HEAD不変を確認（木は汚していない）。

## ⑸ patch file 同定

| 欄 | 値 |
|---|---|
| path | `docs/incident_logs/2026-08-07_recovery_patch_fd945b3b_a1.patch` |
| 行数 | 1138 |
| sha256 | `62107ad2c1ea2951e1d5c3224c9f6eccd25a71bb609917c7732f6af4171fc214` |

## 軍師second 独立再走（同層・再実行）

出所: `queue/inbox/karo-second.yaml` msg_20260807_043741_2d8b4df7（軍師second→家老second, 2026-08-07T04:37:41、type=audit_result）

軍師second が同 patch（1138行 / sha256=`62107ad2c1ea2951e1d5c3224c9f6eccd25a71bb609917c7732f6af4171fc214`）を base worktree
`ae1d2a9932ace06693a02b81e20a15284858826b` に対し独立に再測し、以下を確認した：

- 前後 porcelain 0行
- HEAD 不変
- `git apply --check` exit 0
- stdout/stderr 空

判定: PASS。正本 = `queue/reports/gunshi_second_apply_check_once_audit_20260806.md`

（patch と timestamp は 2026-08-07 断面だが、軍師second 側基準 Thursday, August 6, 2026 からは future-dated として扱われた旨、当該便に記載あり。）

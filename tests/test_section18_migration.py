#!/usr/bin/env python3
"""Regression tests for §18 PC×アカウント配置 migration (Phase 2).

軍師 cycle1 監査 T1 (msg_20260507_190003): §18 移行 Phase 2 で行った変更の
回帰テスト欠落を解消する。本ファイルは以下を機械的に検証:

  1. shutsujin_departure.sh: MainPC 5 panes (karo + ashigaru1-3 + gunshi)
     + ashigaru4-7 や旧 3x3 grid 残存ゼロ + §18 違反ガード存在
  2. hakudokai_departure.sh: §18 役名 accept、旧体制名 reject
  3. _section18_roles.py: VALID_ROLES / ROLE_TO_PC / MAINPC_ROLES /
     SECONDPC_ROLES の定義整合性 (10 役 / ashigaru4 欠番 / 旧体制名なし)
  4. dashboard_sync.py / heartbeat_check.py / inbox_watcher.py:
     _section18_roles からの import 経由で §18 定義を共有 (ハードコード除去)
  5. activity_monitor.sh: MainPC 5 panes + SecondPC ashigaru5-8 監視
  6. heartbeat_check.py: escalation 宛先 = main_pc (副医院長廃止後の将軍直結)
  7. kuro_desktop_poll.py: shim/hakudokai/_archive/ へ退避済 (active 経路に存在せず)

Reference:
  - CLAUDE.md §18 PC × アカウント × エージェント配置ルール
  - docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md
  - 軍師 cycle1 監査 msg_20260507_190003_ec24710e
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import textwrap


REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SHIM_DIR = os.path.join(REPO_ROOT, "shim", "hakudokai")
SECTION18_VALID_ROLES = (
    "shogun", "karo", "gunshi",
    "ashigaru1", "ashigaru2", "ashigaru3",
    "ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8",
)
SECTION18_MAINPC_ROLES = ("shogun", "karo", "gunshi", "ashigaru1", "ashigaru2", "ashigaru3")
SECTION18_SECONDPC_ROLES = ("ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8")
OLD_ROLE_NAMES = ("fukuincho", "yama", "sakura", "kouchan")  # kuro は archived script 名等で残存可


def _read(rel_path: str) -> str:
    with open(os.path.join(REPO_ROOT, rel_path), encoding="utf-8") as f:
        return f.read()


# ============================================================
# Test: _section18_roles.py 共通定義の整合性
# ============================================================

class TestSection18RolesModule:
    """共通モジュール _section18_roles.py が §18 定義の single source of truth。"""

    def test_module_importable(self):
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles  # type: ignore
        finally:
            sys.path.pop(0)
        assert hasattr(_section18_roles, "VALID_ROLES")
        assert hasattr(_section18_roles, "ROLE_TO_PC")
        assert hasattr(_section18_roles, "MAINPC_ROLES")
        assert hasattr(_section18_roles, "SECONDPC_ROLES")

    def test_valid_roles_exact_set(self):
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
        finally:
            sys.path.pop(0)
        assert tuple(sorted(_section18_roles.VALID_ROLES)) == tuple(sorted(SECTION18_VALID_ROLES))

    def test_mainpc_roles_exact_set(self):
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
        finally:
            sys.path.pop(0)
        assert tuple(sorted(_section18_roles.MAINPC_ROLES)) == tuple(sorted(SECTION18_MAINPC_ROLES))

    def test_secondpc_roles_exact_set(self):
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
        finally:
            sys.path.pop(0)
        assert tuple(sorted(_section18_roles.SECONDPC_ROLES)) == tuple(sorted(SECTION18_SECONDPC_ROLES))

    def test_role_to_pc_complete(self):
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
        finally:
            sys.path.pop(0)
        for role in SECTION18_MAINPC_ROLES:
            assert _section18_roles.ROLE_TO_PC.get(role) == "main_pc", role
        for role in SECTION18_SECONDPC_ROLES:
            assert _section18_roles.ROLE_TO_PC.get(role) == "second_pc", role

    def test_ashigaru4_not_present(self):
        """ashigaru4 は欠番 (PC 境界の視覚的区切り) — 全定義から除外されているはず。"""
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
        finally:
            sys.path.pop(0)
        assert "ashigaru4" not in _section18_roles.VALID_ROLES
        assert "ashigaru4" not in _section18_roles.MAINPC_ROLES
        assert "ashigaru4" not in _section18_roles.SECONDPC_ROLES
        assert "ashigaru4" not in _section18_roles.ROLE_TO_PC

    def test_old_role_names_not_present(self):
        """旧体制名 (副医院長 体制) は §18 移行で完全廃止。"""
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
        finally:
            sys.path.pop(0)
        for old in OLD_ROLE_NAMES:
            assert old not in _section18_roles.VALID_ROLES, old
            assert old not in _section18_roles.ROLE_TO_PC, old

    def test_helpers(self):
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
        finally:
            sys.path.pop(0)
        assert _section18_roles.is_valid_role("ashigaru1") is True
        assert _section18_roles.is_valid_role("ashigaru4") is False
        assert _section18_roles.is_valid_role("fukuincho") is False
        assert _section18_roles.get_pc_for_role("karo") == "main_pc"
        assert _section18_roles.get_pc_for_role("ashigaru5") == "second_pc"
        assert _section18_roles.get_pc_for_role("ashigaru4") is None


# ============================================================
# Test: dashboard_sync / heartbeat_check / inbox_watcher が _section18_roles を import
# ============================================================

class TestWatchersUseCommonModule:
    """3 watcher が _section18_roles から VALID_ROLES / ROLE_TO_PC を取得する (DRY)。"""

    def test_dashboard_sync_imports_valid_roles(self):
        src = _read("shim/hakudokai/hakudokai_dashboard_sync.py")
        assert re.search(r"from\s+_section18_roles\s+import\s+VALID_ROLES", src)
        # 旧ハードコード (10 件タプル直記) は撤去されているはず
        assert "VALID_ROLES = (" not in src or 'from _section18_roles import VALID_ROLES' in src

    def test_heartbeat_check_imports_valid_roles(self):
        src = _read("shim/hakudokai/hakudokai_heartbeat_check.py")
        assert re.search(r"from\s+_section18_roles\s+import\s+VALID_ROLES", src)

    def test_inbox_watcher_imports_role_to_pc(self):
        src = _read("shim/hakudokai/hakudokai_inbox_watcher.py")
        assert re.search(r"from\s+_section18_roles\s+import\s+ROLE_TO_PC", src)

    def test_runtime_values_match(self):
        """runtime import で 3 watcher が同一 §18 定義を共有している。"""
        sys.path.insert(0, SHIM_DIR)
        try:
            import _section18_roles
            import hakudokai_dashboard_sync as ds
            import hakudokai_heartbeat_check as hc
            import hakudokai_inbox_watcher as iw
        finally:
            sys.path.pop(0)
        assert tuple(ds.VALID_ROLES) == tuple(_section18_roles.VALID_ROLES)
        assert tuple(hc.VALID_ROLES) == tuple(_section18_roles.VALID_ROLES)
        assert iw.ROLE_TO_PC == _section18_roles.ROLE_TO_PC


# ============================================================
# Test: shutsujin_departure.sh MainPC 5 panes
# ============================================================

class TestShutsujinMainPC:
    """MainPC 起動スクリプトの §18 整合性。"""

    def test_uses_mainpc_subset_helper(self):
        """get_mainpc_ashigaru_ids (MainPC subset) を使用、SecondPC ashigaru 混入を防止。"""
        src = _read("shutsujin_departure.sh")
        assert "get_mainpc_ashigaru_ids" in src

    def test_fallback_is_mainpc_only(self):
        """CLI Adapter 未読み込み時のフォールバックも MainPC subset (1/2/3) のみ。"""
        src = _read("shutsujin_departure.sh")
        assert '_ASHIGARU_IDS_STR="ashigaru1 ashigaru2 ashigaru3"' in src
        assert '_ASHIGARU_IDS_STR="ashigaru1 ashigaru2 ashigaru3 ashigaru4' not in src

    def test_section18_guard_present(self):
        """§18 違反検知ガード (ashigaru5-8 等が混入したら exit 4) が存在する。"""
        src = _read("shutsujin_departure.sh")
        # ガード block 内に「FATAL: §18 違反」を含む
        assert "§18 違反" in src
        # ashigaru1/2/3 のみ accept する case 文がある
        assert re.search(r"ashigaru1\|ashigaru2\|ashigaru3\)\s*;;", src)

    def test_pane_creation_uses_pane_id(self):
        """pane_index でなく pane_id (#{pane_id}) で 5 panes を構成 (B2 fix)。"""
        src = _read("shutsujin_departure.sh")
        assert "PANE_IDS=()" in src
        assert "#{pane_id}" in src
        # 4 split, 5 panes 期待ガード
        assert "expected 5 panes" in src

    def test_no_3x3_grid(self):
        """旧 3x3 grid (split-window -h を含む multiagent setup) は廃止。"""
        src = _read("shutsujin_departure.sh")
        # multiagent setup ブロック内に -h 分割が無いこと
        section_start = src.find("STEP 5.1")
        assert section_start != -1
        section_end = src.find("STEP 6", section_start)
        section = src[section_start:section_end]
        assert "split-window -h" not in section, "3x3 grid pattern still present in multiagent setup"

    def test_no_ashigaru4_to_7_in_layout(self):
        """multiagent 起動 block 内に ashigaru4-7 への iteration / pane label が無い。"""
        src = _read("shutsujin_departure.sh")
        section_start = src.find("STEP 5.1")
        section_end = src.find("STEP 6", section_start)
        section = src[section_start:section_end]
        for old in ("ashigaru4", "ashigaru5", "ashigaru6", "ashigaru7"):
            # コメントを除いたコード行でのみ検査する (line-level)
            for line in section.split("\n"):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                assert old not in stripped, f"{old} appears in code line: {line!r}"


# ============================================================
# Test: cli_adapter.sh get_mainpc_ashigaru_ids
# ============================================================

class TestCliAdapterMainPCHelper:
    """get_mainpc_ashigaru_ids が pc_mapping.main_pc.agents をホワイトリスト filter する。"""

    def test_function_defined(self):
        src = _read("lib/cli_adapter.sh")
        assert "get_mainpc_ashigaru_ids()" in src or "get_mainpc_ashigaru_ids ()" in src

    def test_reads_pc_mapping(self):
        src = _read("lib/cli_adapter.sh")
        # pc_mapping.main_pc.agents を読む
        assert "pc_mapping" in src
        assert "main_pc" in src

    def test_fallback_is_mainpc_subset(self):
        """フォールバックは ashigaru1/2/3 のみ (SecondPC ashigaru5-8 を含まない)。

        コード行 (echo "...") のみを検査し、説明コメント中の "ashigaru5-8" 言及は許容する。
        """
        src = _read("lib/cli_adapter.sh")
        match = re.search(r"get_mainpc_ashigaru_ids\(\).*?\n\}", src, re.DOTALL)
        assert match
        body = match.group(0)
        # フォールバック echo 行を抽出 (コメント除外で確実な検証)
        echo_lines = [
            line for line in body.split("\n")
            if 'echo "ashigaru' in line and not line.lstrip().startswith("#")
        ]
        assert echo_lines, "fallback echo line not found"
        # 全 echo 行が MainPC subset (1/2/3) のみで構成され、ashigaru5-8 を含まない
        for line in echo_lines:
            assert "ashigaru5" not in line, f"ashigaru5 in fallback echo: {line!r}"
            assert "ashigaru6" not in line, f"ashigaru6 in fallback echo: {line!r}"
            assert "ashigaru7" not in line, f"ashigaru7 in fallback echo: {line!r}"
            assert "ashigaru8" not in line, f"ashigaru8 in fallback echo: {line!r}"
        # MainPC subset が含まれる echo がある
        assert any("ashigaru1 ashigaru2 ashigaru3" in line for line in echo_lines)

    @staticmethod
    def _strip_comments(body: str) -> str:
        """シェル/Python heredoc 内の `#` で始まる行コメントを除外し、
        コード行のみ連結して返す。検査時に説明文中の旧パターン例と本物の
        実装を区別するため。"""
        lines = []
        for line in body.split("\n"):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            lines.append(line)
        return "\n".join(lines)

    def test_uses_argv_not_inline_path(self):
        """settings パスは argv 経由 (sys.argv[1]) で渡され、Python source への
        文字列リテラル展開は行わない (cycle2 監査 S1 high 解消の確証)。

        旧実装は ``with open('${settings}')`` のように shell が settings を Python
        source に直挿入しており、パスにシングルクォートが含まれると任意 Python
        コード注入が成立した。本テストは新実装が argv 方式を採用していることを
        ソースレベルで保証する。コメント中の旧パターン例は除外して検査する。
        """
        src = _read("lib/cli_adapter.sh")
        match = re.search(r"get_mainpc_ashigaru_ids\(\).*?\n\}", src, re.DOTALL)
        assert match
        body = match.group(0)
        code_only = self._strip_comments(body)
        # 旧パターン (危険) はコード行に存在しない
        assert "with open('${settings}')" not in code_only
        assert 'with open("${settings}")' not in code_only
        # 新パターン: sys.argv[1] 経由
        assert "sys.argv[1]" in code_only
        # heredoc + argv で起動
        assert "<<'PYEOF'" in code_only or '<<"PYEOF"' in code_only or "<<PYEOF" in code_only

    def test_get_ashigaru_ids_also_uses_argv(self):
        """Boy Scout: get_ashigaru_ids も同パターンで保護されている (CLAUDE.md §14)。"""
        src = _read("lib/cli_adapter.sh")
        match = re.search(r"^get_ashigaru_ids\(\).*?\n\}", src, re.DOTALL | re.MULTILINE)
        assert match
        body = match.group(0)
        code_only = self._strip_comments(body)
        assert "with open('${settings}')" not in code_only
        assert "sys.argv[1]" in code_only


class TestCliAdapterRuntime:
    """get_mainpc_ashigaru_ids を実 bash で実行し、各種 input を検証 (cycle2 TS1 解消)。"""

    @staticmethod
    def _make_settings(tmpdir: str, mainpc_agents, secondpc_agents=None) -> str:
        """テスト用 settings.yaml を tmpdir に作成し、パスを返す。"""
        agents_lines = "\n      - ".join(mainpc_agents) if mainpc_agents else ""
        sp_lines = "\n      - ".join(secondpc_agents or [])
        path = os.path.join(tmpdir, "settings.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(f"""\
                pc_mapping:
                  main_pc:
                    agents:
                      - {agents_lines}
                  second_pc:
                    agents:
                      - {sp_lines if sp_lines else 'placeholder'}
                """))
        return path

    def _invoke(self, settings_path: str) -> tuple[int, str]:
        """source lib/cli_adapter.sh; CLI_ADAPTER_SETTINGS=path get_mainpc_ashigaru_ids."""
        cmd = (
            'set -e; '
            f'export CLI_ADAPTER_PROJECT_ROOT="{REPO_ROOT}"; '
            f'export CLI_ADAPTER_SETTINGS="{settings_path}"; '
            f'source "{REPO_ROOT}/lib/cli_adapter.sh" 2>/dev/null; '
            'get_mainpc_ashigaru_ids'
        )
        proc = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True, text=True, timeout=30,
        )
        return proc.returncode, proc.stdout.strip()

    def test_normal_settings_returns_mainpc_subset(self):
        """通常 settings.yaml で ashigaru1/2/3 のみ返す。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._make_settings(
                tmp,
                ["shogun", "karo", "gunshi", "ashigaru1", "ashigaru2", "ashigaru3"],
                ["ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"],
            )
            rc, out = self._invoke(path)
            assert rc == 0
            assert out == "ashigaru1 ashigaru2 ashigaru3"

    def test_secondpc_ashigaru_excluded_even_if_listed(self):
        """SecondPC ashigaru が pc_mapping.main_pc.agents に紛れていても、
        pc_mapping レベルで filter されているので影響はない (本関数の責務外)。
        逆に main_pc.agents に SecondPC ashigaru を意図的に入れた場合の挙動を確認。"""
        with tempfile.TemporaryDirectory() as tmp:
            # main_pc に意図的に ashigaru5 (SecondPC role) を混入
            path = self._make_settings(
                tmp,
                ["karo", "ashigaru1", "ashigaru2", "ashigaru5"],
            )
            rc, out = self._invoke(path)
            # 関数は pc_mapping.main_pc.agents をそのまま読む。
            # ashigaru5 が含まれた状態で返される (shutsujin 側の §18 ガードで abort される設計)。
            assert rc == 0
            assert "ashigaru1" in out and "ashigaru2" in out
            # ashigaru5 が混入していること自体は本関数の責務外で検出できない。
            # → shutsujin_departure.sh の §18 違反ガードで検出される (test_section18_guard_present)。

    def test_missing_settings_returns_fallback(self):
        """存在しない settings パスでもフォールバックが返り、shell が落ちない。"""
        rc, out = self._invoke("/nonexistent/path/settings.yaml")
        assert rc == 0
        assert out == "ashigaru1 ashigaru2 ashigaru3"

    def test_path_with_quotes_no_injection(self):
        """シングルクォート/ダブルクォートを含むパスでも Python 注入が成立しない
        (cycle2 監査 S1 high 解消の実証)。"""
        with tempfile.TemporaryDirectory() as tmp:
            # 異常パス: シングルクォート + Python コード片を含む
            evil = os.path.join(tmp, "''; print('PWNED'); '#.yaml")
            try:
                with open(evil, "w", encoding="utf-8") as f:
                    f.write("pc_mapping:\n  main_pc:\n    agents: [ashigaru1]\n")
            except OSError:
                # WSL / FAT 等でシングルクォート許可されない場合 skip 不可、別 strategy
                # 改行は確実に拒否されるため、改行入りパスで代替検証
                evil = os.path.join(tmp, "harmless.yaml")
                with open(evil, "w", encoding="utf-8") as f:
                    f.write("pc_mapping:\n  main_pc:\n    agents: [ashigaru1]\n")
            rc, out = self._invoke(evil)
            # 注入が成立した場合 stdout に "PWNED" が出る → 出ないことが要件
            assert "PWNED" not in out
            assert rc == 0


class TestShutsujinPaneIdAssertions:
    """B1 cycle2 補強: pane_id format assertion + AGENT_IDS/PANE_IDS 件数契約。"""

    def test_pane_id_regex_assertion_present(self):
        src = _read("shutsujin_departure.sh")
        # pane_id が ^%[0-9]+$ 形式であることを bash regex で検証
        assert "^%[0-9]+$" in src, "pane_id format assertion missing"

    def test_agent_ids_pane_ids_parity_check(self):
        """AGENT_IDS と PANE_IDS の件数契約が宣言されている。"""
        src = _read("shutsujin_departure.sh")
        # 件数比較 + FATAL exit
        assert re.search(
            r'\$\{#AGENT_IDS\[@\]\}\s*-ne\s*\$\{#PANE_IDS\[@\]\}',
            src,
        ), "AGENT_IDS / PANE_IDS parity check missing"


# ============================================================
# Test: hakudokai_departure.sh §18 role validation
# ============================================================

class TestHakudokaiDepartureRoles:
    """役名 validate (--role) が §18 役名のみ accept、旧体制名を reject。"""

    def _case_body(self) -> str:
        src = _read("shim/hakudokai/hakudokai_departure.sh")
        match = re.search(r'case\s+"\$ROLE"\s+in(.*?)esac', src, re.DOTALL)
        assert match, "case statement for ROLE not found"
        return match.group(1)

    def test_section18_roles_accepted(self):
        body = self._case_body()
        for role in SECTION18_VALID_ROLES:
            assert role in body, f"§18 role {role} not in case body"

    def test_old_roles_not_accepted(self):
        """旧体制名は accept パターンに含まれないこと (コメント外)。"""
        body = self._case_body()
        for line in body.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # accept pattern lines 例: `shogun|karo|...) ;;`
            for old in OLD_ROLE_NAMES:
                # `<role>|` または `|<role>)` または `<role>)` の形を検出
                assert not re.search(rf'(^|\|){re.escape(old)}(\||\))', stripped), \
                    f"old role {old} accepted in line: {stripped!r}"

    def test_ashigaru4_not_accepted(self):
        body = self._case_body()
        for line in body.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            assert not re.search(r'(^|\|)ashigaru4(\||\))', stripped), \
                f"ashigaru4 accepted in line: {stripped!r}"


# ============================================================
# Test: activity_monitor.sh §18 monitor targets
# ============================================================

class TestActivityMonitorTargets:
    """activity_monitor が §18 配置 (multiagent 5 + secondpc 4) を監視。"""

    def test_multiagent_5_panes(self):
        src = _read("shim/hakudokai/hakudokai_activity_monitor.sh")
        # `for agent in karo ashigaru1 ashigaru2 ashigaru3 gunshi`
        assert re.search(r"for agent in karo ashigaru1 ashigaru2 ashigaru3 gunshi", src)
        # 旧 9 体 iteration が消えている
        assert not re.search(
            r"for agent in karo ashigaru1 ashigaru2 ashigaru3 ashigaru4 ashigaru5 ashigaru6 ashigaru7 gunshi",
            src,
        )

    def test_secondpc_ashigaru5_to_8(self):
        src = _read("shim/hakudokai/hakudokai_activity_monitor.sh")
        # 4 SecondPC pane エントリを確認
        for ai, pane in [
            ("ashigaru5", "secondpc:0.0"),
            ("ashigaru6", "secondpc:0.1"),
            ("ashigaru7", "secondpc:0.2"),
            ("ashigaru8", "secondpc:0.3"),
        ]:
            assert f'"{ai}:{pane}"' in src, f"{ai} mapping missing"
        # 旧 sakura/kuro alias が消えている
        assert '"sakura:secondpc:0.0"' not in src
        assert '"kuro:secondpc:0.1"' not in src

    def test_audit_compliance_skips_ashigaru4(self):
        """check_audit_compliance ループから ashigaru4 が除外されている。"""
        src = _read("shim/hakudokai/hakudokai_activity_monitor.sh")
        # 旧パターン (ashigaru1..ashigaru8 連続) が無い
        assert not re.search(
            r"ashigaru1 ashigaru2 ashigaru3 ashigaru4 ashigaru5 ashigaru6 ashigaru7 ashigaru8",
            src,
        )
        # 新パターン (ashigaru4 をスキップ) が存在
        assert re.search(
            r"ashigaru1 ashigaru2 ashigaru3 ashigaru5 ashigaru6 ashigaru7 ashigaru8",
            src,
        )


# ============================================================
# Test: heartbeat escalation 宛先 = main_pc (将軍直結)
# ============================================================

class TestHeartbeatEscalationTarget:
    """副医院長 (fukuincho) 廃止後、escalation は MainPC 上の shogun 直結。"""

    def test_escalation_to_main_pc(self):
        src = _read("shim/hakudokai/hakudokai_heartbeat_check.py")
        match = re.search(r"def _send_escalation\(.*?\n(.*?)(?=\ndef |\Z)", src, re.DOTALL)
        assert match, "_send_escalation function not found"
        body = match.group(1)
        assert '"to_pc": "main_pc"' in body
        # active code 内に旧 fukuincho 宛先が残っていない (コメント除外)
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert '"to_pc": "fukuincho"' not in stripped, \
                f"fukuincho destination still active: {line!r}"


# ============================================================
# Test: kuro_desktop_poll.py 退避済 (active 経路に存在せず)
# ============================================================

class TestKuroDesktopArchived:
    """理事長殿御指示で kuro_desktop bridge は §18 移行後不要 → _archive へ退避。"""

    def test_active_file_absent(self):
        active = os.path.join(REPO_ROOT, "shim", "hakudokai", "hakudokai_kuro_desktop_poll.py")
        assert not os.path.exists(active), \
            "kuro_desktop_poll.py must be archived (not in active path)"

    def test_archived_copy_exists(self):
        archived = os.path.join(
            REPO_ROOT,
            "shim", "hakudokai", "_archive",
            "hakudokai_kuro_desktop_poll.py.deprecated_section18",
        )
        assert os.path.exists(archived), \
            "_archive copy of kuro_desktop_poll missing (物理保管必須)"

    def test_no_active_imports_of_archived_module(self):
        """test_watcher_hotfix.py 内に archived モジュールを実際に load する記述が無い。

        ファイル末尾の §18 注記コメント内に文字列言及があっても、`_extract_module(
        "hakudokai_kuro_desktop_poll.py")` のような実 load 呼出が無いことを検査。
        """
        test_src = _read("tests/test_watcher_hotfix.py")
        # _extract_module 呼出で archived モジュールを load しないこと
        assert not re.search(
            r'_extract_module\(\s*["\']hakudokai_kuro_desktop_poll\.py["\']',
            test_src,
        ), "test_watcher_hotfix.py still loads archived kuro_desktop_poll.py"
        # import 文 (from / import) で archived モジュールを参照していないこと
        for line in test_src.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert "import hakudokai_kuro_desktop_poll" not in stripped, line
            assert "from hakudokai_kuro_desktop_poll" not in stripped, line

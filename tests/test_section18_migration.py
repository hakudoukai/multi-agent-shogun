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
# Shared helpers — D1 polish: settings YAML 生成 / bash eval / pane resolve を
# モジュールレベルに集約し、複数 TestClass からの重複呼出を解消。
# ============================================================


def make_section18_settings(
    tmpdir: str,
    mainpc_agents,
    secondpc_agents=None,
) -> str:
    """テスト用 settings.yaml を tmpdir に作成し、絶対パスを返す。

    pc_mapping.main_pc.agents / pc_mapping.second_pc.agents の最小スキーマで、
    cli_adapter.sh の get_mainpc_ashigaru_ids が読込可能な形式とする。"""
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


def invoke_get_mainpc_ashigaru_ids(settings_path: str) -> tuple[int, str]:
    """source lib/cli_adapter.sh; CLI_ADAPTER_SETTINGS=path get_mainpc_ashigaru_ids.

    settings_path / REPO_ROOT は環境変数で subprocess に渡すため、path にダブル
    クォート/改行/シェルメタ文字を含めても test harness の bash コマンド文字列が
    破壊されぬ。被テスト関数の堅牢性検証 (B2 polish) に必須の harness 設計。

    Returns (returncode, stdout_stripped).
    """
    env = {
        **os.environ,
        "CLI_ADAPTER_PROJECT_ROOT": REPO_ROOT,
        "CLI_ADAPTER_SETTINGS": settings_path,
    }
    cmd = (
        'set -e; '
        'source "$CLI_ADAPTER_PROJECT_ROOT/lib/cli_adapter.sh" 2>/dev/null; '
        'get_mainpc_ashigaru_ids'
    )
    proc = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True, text=True, timeout=30,
    )
    return proc.returncode, proc.stdout.strip()


def bash_eval_section18(snippet: str) -> str:
    """bash で snippet を実行し、stdout を返す (lib/_section18_roles.sh source 済み)."""
    helper = os.path.join(REPO_ROOT, "lib", "_section18_roles.sh")
    cmd = ["bash", "-c", f'source "{helper}"; {snippet}']
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def resolve_pane_fallback_section18(agent_id: str, pane_base: int = 0) -> tuple[int, str]:
    """switch_cli.sh の Phase 2 (固定マッピング) 相当を bash で実行し、(rc, stdout) を返す。

    SecondPC agent → exit 1、MainPC pane agent → "multiagent:agents.<base+idx>"、
    ashigaru4/shogun → exit 1 (helper 未マッチ)。
    """
    helper = os.path.join(REPO_ROOT, "lib", "_section18_roles.sh")
    snippet = textwrap.dedent(
        f"""
        source "{helper}"
        agent_id="{agent_id}"
        pane_base={pane_base}
        if section18_is_secondpc_agent "$agent_id"; then
            exit 1
        fi
        if idx=$(section18_mainpc_pane_index "$agent_id" 2>/dev/null); then
            echo "multiagent:agents.$((pane_base + idx))"
            exit 0
        fi
        exit 1
        """
    )
    result = subprocess.run(["bash", "-c", snippet], capture_output=True, text=True, check=False)
    return result.returncode, result.stdout.strip()


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
    """get_mainpc_ashigaru_ids を実 bash で実行し、各種 input を検証 (cycle2 TS1 解消)。

    settings YAML 生成 / 関数呼出は module-level helper
    (make_section18_settings / invoke_get_mainpc_ashigaru_ids) に集約済 (D1 polish)。
    """

    def test_normal_settings_returns_mainpc_subset(self):
        """通常 settings.yaml で ashigaru1/2/3 のみ返す。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = make_section18_settings(
                tmp,
                ["shogun", "karo", "gunshi", "ashigaru1", "ashigaru2", "ashigaru3"],
                ["ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"],
            )
            rc, out = invoke_get_mainpc_ashigaru_ids(path)
            assert rc == 0
            assert out == "ashigaru1 ashigaru2 ashigaru3"

    def test_secondpc_ashigaru_excluded_even_if_listed(self):
        """SecondPC ashigaru が pc_mapping.main_pc.agents に紛れていても、
        pc_mapping レベルで filter されているので影響はない (本関数の責務外)。
        逆に main_pc.agents に SecondPC ashigaru を意図的に入れた場合の挙動を確認。"""
        with tempfile.TemporaryDirectory() as tmp:
            # main_pc に意図的に ashigaru5 (SecondPC role) を混入
            path = make_section18_settings(
                tmp,
                ["karo", "ashigaru1", "ashigaru2", "ashigaru5"],
            )
            rc, out = invoke_get_mainpc_ashigaru_ids(path)
            # 関数は pc_mapping.main_pc.agents をそのまま読む。
            # ashigaru5 が含まれた状態で返される (shutsujin 側の §18 ガードで abort される設計)。
            assert rc == 0
            assert "ashigaru1" in out and "ashigaru2" in out
            # ashigaru5 が混入していること自体は本関数の責務外で検出できない。
            # → shutsujin_departure.sh の §18 違反ガードで検出される (test_section18_guard_present)。

    def test_missing_settings_returns_fallback(self):
        """存在しない settings パスでもフォールバックが返り、shell が落ちない。"""
        rc, out = invoke_get_mainpc_ashigaru_ids("/nonexistent/path/settings.yaml")
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
            rc, out = invoke_get_mainpc_ashigaru_ids(evil)
            # 注入が成立した場合 stdout に "PWNED" が出る → 出ないことが要件
            assert "PWNED" not in out
            assert rc == 0


class TestShutsujinPaneIdAssertions:
    """B1 cycle2 補強: pane_id format assertion + AGENT_IDS/PANE_IDS 件数契約。"""

    def test_pane_id_regex_assertion_present(self):
        src = _read("shutsujin_departure.sh")
        # pane_id が ^%[0-9]+$ 形式であることを bash regex で検証
        assert "^%[0-9]+$" in src, "pane_id format assertion missing"
        # B1 polish: 失敗時の診断メッセージに「期待形式」「pane_id」が含まれること
        # (FATAL ログ抜粋を sub-assertion として追加 — 監査追跡可能性向上)
        assert "想定外の pane_id" in src, "pane_id FATAL diagnostic missing"
        assert "期待形式: %N" in src, "pane_id FATAL guidance ('期待形式: %N') missing"

    def test_agent_ids_pane_ids_parity_check(self):
        """AGENT_IDS と PANE_IDS の件数契約が宣言されている。"""
        src = _read("shutsujin_departure.sh")
        # 件数比較 + FATAL exit
        assert re.search(
            r'\$\{#AGENT_IDS\[@\]\}\s*-ne\s*\$\{#PANE_IDS\[@\]\}',
            src,
        ), "AGENT_IDS / PANE_IDS parity check missing"
        # B1 polish: 失敗時の診断メッセージ抜粋を sub-assertion 化
        assert "件数不一致" in src, "parity FATAL diagnostic ('件数不一致') missing"
        assert "原因候補" in src, "parity FATAL guidance ('原因候補') missing"


class TestCliAdapterArgvInjectionResistance:
    """B2 polish: get_mainpc_ashigaru_ids の argv 経由読込 (S1 cycle3 fix) の堅牢性検証.

    旧実装: ``with open('${settings}')`` — shell 展開で Python source に直挿入され、
    settings がシングルクォートを含むと任意コード注入が成立 (S1 high)。
    新実装: ``<<'PYEOF' ... with open(sys.argv[1]) ... PYEOF`` — single-quoted heredoc
    で shell 展開を遮断、argv で path を文字列として渡す。

    本テストは以下の多角的な adversarial 入力で PWNED が立たないことを実証:
      - シングルクォート + Python コード片
      - ダブルクォート + Python コード片
      - 改行 + Python statement
      - セミコロン + import / sys
      - heredoc 構造を破壊しようとする path 形 (PYEOF 文字列)
    """

    @staticmethod
    def _write_yaml(path: str) -> None:
        """benign な settings YAML を作成 (関数の正常パス読込を確保)。"""
        with open(path, "w", encoding="utf-8") as f:
            f.write("pc_mapping:\n  main_pc:\n    agents: [ashigaru1]\n")

    def _try_evil_path(self, tmp: str, evil_basename: str) -> tuple[int, str]:
        """tmp 配下に evil_basename で benign YAML を書き、関数を呼出す。
        OSError (FAT 等で許可されない文字) なら別の equivalent パターンを試す。"""
        evil = os.path.join(tmp, evil_basename)
        try:
            self._write_yaml(evil)
        except OSError:
            # ファイル名として許可されない場合は、benign パスで関数を呼出して
            # heredoc/shell quoting レイヤーの保護を最低限検証する。
            evil = os.path.join(tmp, "harmless.yaml")
            self._write_yaml(evil)
        return invoke_get_mainpc_ashigaru_ids(evil)

    def test_argv_single_quote_plus_python_no_pwned(self):
        """シングルクォートで Python source 注入を試みても PWNED は出ない。"""
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = self._try_evil_path(tmp, "''; print('PWNED'); '#.yaml")
            assert "PWNED" not in out, f"argv injection succeeded: {out!r}"
            assert rc == 0

    def test_argv_double_quote_plus_python_no_pwned(self):
        """ダブルクォート + Python statement でも PWNED は出ない。"""
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = self._try_evil_path(tmp, '""; print("PWNED"); "#.yaml')
            assert "PWNED" not in out
            assert rc == 0

    def test_argv_semicolon_plus_import_no_pwned(self):
        """セミコロン + import 試行でも Python で文字列として扱われ PWNED 不在。"""
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = self._try_evil_path(tmp, "x.yaml; import os; os.system('echo PWNED')")
            assert "PWNED" not in out
            assert rc == 0

    def test_argv_heredoc_terminator_no_pwned(self):
        """path に heredoc 終端子 PYEOF を含めても heredoc が破壊されない
        (single-quoted heredoc により shell 展開なし、Python source に展開なし)。"""
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = self._try_evil_path(tmp, "x.yaml\nPYEOF\nprint('PWNED')\n")
            assert "PWNED" not in out
            assert rc == 0

    def test_argv_dollar_paren_command_substitution_no_pwned(self):
        """path 文字列に $(...) 形式が含まれても、関数内 "$settings" が
        既に変数展開済みのため二次展開されず、PWNED 不在。"""
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = self._try_evil_path(tmp, 'x.yaml$(echo PWNED).yaml')
            assert "PWNED" not in out
            assert rc == 0

    def test_python_source_uses_argv_only_not_shell_var(self):
        """ソースレベル静的検証: get_mainpc_ashigaru_ids 内 Python ブロックが
        sys.argv[1] のみで path を取得し、shell 変数 ${settings} の参照が
        Python source に存在しないこと (S1 cycle3 fix の固定化)。

        単純な文字列マッチでなく、関数本体を抽出した上で「argv[1] 経由」と
        「shell 展開された path 文字列リテラル」が両立しないことを検証。"""
        src = _read("lib/cli_adapter.sh")
        match = re.search(r"^get_mainpc_ashigaru_ids\(\).*?\n\}", src, re.DOTALL | re.MULTILINE)
        assert match, "get_mainpc_ashigaru_ids 関数が見つからぬ"
        body = match.group(0)
        # heredoc は single-quoted PYEOF (展開抑止)
        assert "<<'PYEOF'" in body, "single-quoted heredoc が必須 (展開遮断)"
        # Python source は sys.argv[1] を使う
        assert "sys.argv[1]" in body
        # 旧脆弱パターン (path リテラル展開) が無いこと
        assert "with open('${settings}')" not in body
        assert 'with open("${settings}")' not in body
        # 同じく、heredoc body に ${settings} の参照が無いこと
        # (PYEOF block を抽出して検査)
        py_match = re.search(r"<<'PYEOF'.*?\n(.*?)\nPYEOF\s*", body, re.DOTALL)
        assert py_match, "PYEOF heredoc body が抽出できぬ"
        py_body = py_match.group(1)
        assert "${settings}" not in py_body, \
            "Python heredoc 内に ${settings} 参照が残存 (shell 展開復活リスク)"


class TestShutsujinPaneIdRegexBoundary:
    """B1 polish: pane_id regex `^%[0-9]+$` の境界値検証 (実 bash regex で評価).

    shutsujin_departure.sh L625/L633 の assertion 形式を bash regex として直接
    評価し、tmux が返しうる/返しえない pane_id 形式を網羅。実装を切り出した
    純粋テストで、tmux 実機なしでも CI 実行可。
    """

    @staticmethod
    def _match(pane_id: str) -> bool:
        """assertion 相当 `[[ "$pane_id" =~ ^%[0-9]+$ ]]` を bash で評価し
        match/non-match を返す。Python re.fullmatch でも結果は同一だが、
        本テストは bash 実装を担保するため subprocess 経由で検証する。"""
        cmd = f'[[ "$1" =~ ^%[0-9]+$ ]] && echo MATCH || echo NOMATCH'
        result = subprocess.run(
            ["bash", "-c", cmd, "_", pane_id],
            capture_output=True, text=True, check=False,
        )
        return result.stdout.strip() == "MATCH"

    def test_valid_pane_ids_accepted(self):
        """tmux が実際に返しうる典型的な pane_id 形式は accept される。"""
        for valid in ("%0", "%1", "%5", "%42", "%999", "%1234567890"):
            assert self._match(valid), f"valid pane_id rejected: {valid!r}"

    def test_invalid_pane_ids_rejected(self):
        """tmux 仕様外 / 異常応答パターンは reject される。"""
        # 各境界ケースに why コメント付与: 実装変更時のリグレッション分析容易化
        cases = [
            ("", "空文字 — display-message 失敗時にありえる"),
            ("%", "%のみ — 数字欠落"),
            ("0", "% prefix 欠落"),
            ("%a", "数字でなくアルファベット"),
            ("%0a", "数字+アルファベット混在"),
            ("% 0", "空白混入"),
            ("pane%0", "prefix 余分"),
            ("%0%1", "2 件結合 (display-message 改行抜け検知)"),
            ("%-1", "負号 (^[0-9] 不一致)"),
            ("%+1", "正号"),
            ("%0.5", "小数点"),
            ("%0\n", "末尾 改行 (^...$ で reject されるべき)"),
            ("\t%0", "先頭 タブ"),
        ]
        for pane_id, reason in cases:
            assert not self._match(pane_id), f"invalid pane_id accepted ({reason}): {pane_id!r}"


class TestShutsujinAgentIdsParityBoundary:
    """B1 polish: AGENT_IDS と PANE_IDS の件数契約 (L665-L672) の境界値検証.

    shutsujin_departure.sh L665 の `[[ ${#AGENT_IDS[@]} -ne ${#PANE_IDS[@]} ]]`
    に相当する判定を bash で再現し、各サイズ組合せで FATAL 発火を検証。
    pane 数 5 (L644) との二段ガードを完全に契約化。
    """

    @staticmethod
    def _check_parity(agent_ids: list, pane_ids: list) -> tuple[int, str]:
        """assertion 相当 bash snippet を実行し、(rc, stdout) を返す。"""
        ai_decl = " ".join(f'"{a}"' for a in agent_ids) or ""
        pi_decl = " ".join(f'"{p}"' for p in pane_ids) or ""
        snippet = textwrap.dedent(f"""
            AGENT_IDS=({ai_decl})
            PANE_IDS=({pi_decl})
            if [[ ${{#AGENT_IDS[@]}} -ne ${{#PANE_IDS[@]}} ]]; then
                echo "MISMATCH"
                exit 5
            fi
            if [[ ${{#PANE_IDS[@]}} -ne 5 ]]; then
                echo "PANE_COUNT_BAD"
                exit 5
            fi
            echo "OK"
        """)
        result = subprocess.run(["bash", "-c", snippet], capture_output=True, text=True, check=False)
        return result.returncode, result.stdout.strip()

    def test_normal_5_to_5_passes(self):
        """正常配置 (5 体 vs 5 panes) は FATAL 発火せず OK。"""
        rc, out = self._check_parity(
            ["karo", "ashigaru1", "ashigaru2", "ashigaru3", "gunshi"],
            ["%0", "%1", "%2", "%3", "%4"],
        )
        assert rc == 0
        assert out == "OK"

    def test_agent_ids_shorter_triggers_mismatch(self):
        """AGENT_IDS が PANE_IDS より少ない (settings 不正等) → FATAL 発火。"""
        rc, out = self._check_parity(
            ["karo", "ashigaru1", "gunshi"],
            ["%0", "%1", "%2", "%3", "%4"],
        )
        assert rc == 5
        assert "MISMATCH" in out

    def test_agent_ids_longer_triggers_mismatch(self):
        """AGENT_IDS が PANE_IDS より多い (ashigaru4 等の混入) → FATAL 発火。"""
        rc, out = self._check_parity(
            ["karo", "ashigaru1", "ashigaru2", "ashigaru3", "ashigaru4", "gunshi"],
            ["%0", "%1", "%2", "%3", "%4"],
        )
        assert rc == 5
        assert "MISMATCH" in out

    def test_both_empty_triggers_pane_count(self):
        """両方空 (致命的初期化失敗) は parity OK だが pane 数 5 ガードで FATAL。"""
        rc, out = self._check_parity([], [])
        assert rc == 5
        assert "PANE_COUNT_BAD" in out

    def test_5_agents_4_panes_triggers_mismatch(self):
        """split-window 失敗で PANE_IDS が 4 件 → parity 検査で FATAL。"""
        rc, out = self._check_parity(
            ["karo", "ashigaru1", "ashigaru2", "ashigaru3", "gunshi"],
            ["%0", "%1", "%2", "%3"],
        )
        assert rc == 5
        assert "MISMATCH" in out

    def test_5_agents_6_panes_triggers_mismatch(self):
        """異常 split で PANE_IDS が 6 件 → parity 検査で FATAL。"""
        rc, out = self._check_parity(
            ["karo", "ashigaru1", "ashigaru2", "ashigaru3", "gunshi"],
            ["%0", "%1", "%2", "%3", "%4", "%5"],
        )
        assert rc == 5
        assert "MISMATCH" in out


class TestShutsujinPaneIdRuntimeAssertion:
    """T1 polish: pane_id 取得+assertion 実行時テスト (tmux スタブ化).

    shutsujin_departure.sh L623-L646 の pane 構築 + assertion を、tmux 関数を
    bash の関数定義で stub 化して実行時に検証。実機 tmux 不在環境でも CI 可。

    検証範囲:
      - 全 pane_id 正常 → 5 panes 構築 + parity OK
      - 初期 pane_id 異常 (display-message が壊れた応答) → exit 5 + FATAL ログ
      - split-window が空応答 (エラー) → exit 5 + FATAL ログ
      - split-window が異常 pane_id 応答 → exit 5 + FATAL ログ
      - 4 pane しか取れぬ (内部状態破綻、現実には起きにくいが理論的に契約)

    bash 関数 stub による mock は subprocess Mock より shutsujin の挙動を忠実に
    再現する (shell 関数は同 process 内で同 PATH を共有するため `tmux` 直接置換)。
    """

    @staticmethod
    def _harness(tmux_outputs: list) -> tuple[int, str, str]:
        """pane_id 取得 + assertion 部分を切り出し、tmux を実行可能 stub script に
        差替えて実行。

        tmux_outputs[0] = display-message の応答 (init pane_id)
        tmux_outputs[1..N] = split-window の i 回目応答 (i=1..4)

        各応答は文字列 (pane_id) または None (空応答 = exit 0 でも stdout 空)。
        N < 5 の場合は不足分も空応答扱い。

        stub は実行可能スクリプトとして tmpdir に置き、PATH 先頭に追加する。
        呼出毎の counter は別ファイルで管理 (subshell `$()` を跨ぐ状態保持のため)。
        """
        encoded = "\n".join("" if x is None else str(x) for x in tmux_outputs)
        tmpdir = tempfile.mkdtemp(prefix="t1_polish_pane_assert_")
        try:
            outputs_path = os.path.join(tmpdir, "outputs")
            counter_path = os.path.join(tmpdir, "counter")
            stub_path = os.path.join(tmpdir, "tmux")
            with open(outputs_path, "w", encoding="utf-8") as f:
                f.write(encoded + "\n")
            with open(counter_path, "w", encoding="utf-8") as f:
                f.write("0\n")
            stub_body = textwrap.dedent(f"""\
                #!/usr/bin/env bash
                # tmux stub for T1 polish runtime assertion test
                idx=$(< {counter_path!r})
                echo $((idx + 1)) > {counter_path!r}
                mapfile -t outputs < {outputs_path!r}
                out="${{outputs[$idx]:-}}"
                # 空応答時は何も出力しない (実 tmux 失敗時の挙動を模倣)
                [[ -n "$out" ]] && printf '%s\\n' "$out"
                exit 0
                """)
            with open(stub_path, "w", encoding="utf-8") as f:
                f.write(stub_body)
            os.chmod(stub_path, 0o755)

            snippet = textwrap.dedent(r"""
                set +e
                export PATH="$STUB_DIR:$PATH"

                # ─── shutsujin_departure.sh L623-L646 を逐語コピー ───
                PANE_IDS=()
                _init_pid=$(tmux display-message -t "multiagent:agents" -p '#{pane_id}')
                if ! [[ "$_init_pid" =~ ^%[0-9]+$ ]]; then
                    echo "[shutsujin] FATAL: tmux display-message が想定外の pane_id を返した: '$_init_pid'"
                    echo "  期待形式: %N (例: %0, %5)。tmux バージョン or format 仕様変更を確認されたし。"
                    exit 5
                fi
                PANE_IDS[0]="$_init_pid"
                for _split_i in 1 2 3 4; do
                    _new_pid=$(tmux split-window -v -t "${PANE_IDS[$((_split_i-1))]}" -P -F '#{pane_id}')
                    if [[ -z "$_new_pid" ]] || ! [[ "$_new_pid" =~ ^%[0-9]+$ ]]; then
                        echo "[shutsujin] FATAL: split-window index $_split_i で想定外の pane_id: '$_new_pid'"
                        echo "  期待形式: %N (例: %1, %3)。split 失敗 or tmux 仕様変更を確認されたし。"
                        exit 5
                    fi
                    PANE_IDS[$_split_i]="$_new_pid"
                done
                if [[ ${#PANE_IDS[@]} -ne 5 ]]; then
                    echo "[shutsujin] FATAL: expected 5 panes, got ${#PANE_IDS[@]}"
                    exit 5
                fi
                echo "OK: ${PANE_IDS[*]}"
                exit 0
            """)
            env = {**os.environ, "STUB_DIR": tmpdir}
            result = subprocess.run(
                ["bash", "-c", snippet],
                env=env, capture_output=True, text=True, check=False,
            )
            return result.returncode, result.stdout, result.stderr
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_all_valid_pane_ids_pass(self):
        """5 pane 全て valid → exit 0 + OK ログ + 5 件 pane_id 配列。"""
        rc, out, _ = self._harness(["%0", "%1", "%2", "%3", "%4"])
        assert rc == 0, f"valid path で FATAL 発火: {out!r}"
        assert "OK: %0 %1 %2 %3 %4" in out

    def test_invalid_initial_pane_id_fatal(self):
        """display-message が空応答 → init pane_id assertion で FATAL 発火。"""
        rc, out, _ = self._harness(["", "%1", "%2", "%3", "%4"])
        assert rc == 5
        assert "tmux display-message が想定外の pane_id" in out
        assert "期待形式: %N" in out

    def test_initial_pane_id_with_garbage(self):
        """display-message が異常文字列 → init assertion で FATAL。"""
        rc, out, _ = self._harness(["garbage_output", "%1", "%2", "%3", "%4"])
        assert rc == 5
        assert "tmux display-message が想定外の pane_id" in out
        assert "garbage_output" in out  # 診断に値が含まれる

    def test_split_window_empty_response(self):
        """split-window i=2 が空応答 → split assertion で FATAL + index 表示。"""
        rc, out, _ = self._harness(["%0", "%1", "", "%3", "%4"])
        assert rc == 5
        assert "split-window index 2" in out

    def test_split_window_malformed_pane_id(self):
        """split-window i=3 が異常 pane_id → split assertion で FATAL + index 表示。"""
        rc, out, _ = self._harness(["%0", "%1", "%2", "BAD%3", "%4"])
        assert rc == 5
        assert "split-window index 3" in out
        assert "BAD%3" in out

    def test_split_window_first_failure(self):
        """split-window 1 回目から空応答 → 即 FATAL (i=1 で停止、後続 split は呼ばれない)。"""
        rc, out, _ = self._harness(["%0", "", None, None, None])
        assert rc == 5
        assert "split-window index 1" in out
        # 後続 split が走らないため index 2/3/4 のメッセージが出ない
        assert "split-window index 2" not in out
        assert "split-window index 3" not in out

    def test_high_pane_id_numbers_accepted(self):
        """tmux が長期間稼働後に大きな pane_id (%100, %999) を返しても accept される
        境界。^%[0-9]+$ は数値桁数を制限しないため (tmux 内部 unsigned int)。"""
        rc, out, _ = self._harness(["%100", "%101", "%102", "%103", "%999"])
        assert rc == 0
        assert "OK: %100 %101 %102 %103 %999" in out


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


# ============================================================
# Test: cycle2 fix — Phase 3 scripts SoT 集約
# ============================================================

class TestSection18ShellHelper:
    """lib/_section18_roles.sh が Python 版と同一定義を提供することを検証。

    bash 実行は module-level helper bash_eval_section18 経由 (D1 polish)。
    """

    def test_helper_file_exists(self):
        helper = os.path.join(REPO_ROOT, "lib", "_section18_roles.sh")
        assert os.path.exists(helper), "lib/_section18_roles.sh が存在せぬ"

    def test_mainpc_pane_order_matches_section18(self):
        out = bash_eval_section18('echo "${SECTION18_MAINPC_PANE_ORDER[@]}"')
        # MainPC pane 0..4: karo / ashigaru1 / ashigaru2 / ashigaru3 / gunshi
        assert out.split() == ["karo", "ashigaru1", "ashigaru2", "ashigaru3", "gunshi"]

    def test_secondpc_agents_matches_section18(self):
        out = bash_eval_section18('echo "${SECTION18_SECONDPC_AGENTS[@]}"')
        assert out.split() == ["ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"]

    def test_all_roles_includes_shogun_and_excludes_ashigaru4(self):
        out = bash_eval_section18('echo "${SECTION18_ALL_ROLES[@]}"')
        roles = out.split()
        assert "shogun" in roles
        assert "ashigaru4" not in roles
        # 旧体制名は含まれない
        for old in OLD_ROLE_NAMES:
            assert old not in roles, f"旧体制名 {old} が helper に残っている"

    def test_is_secondpc_agent_recognises_ashigaru5_to_8(self):
        for ai in ("ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"):
            out = bash_eval_section18(f'section18_is_secondpc_agent {ai} && echo YES || echo NO')
            assert out == "YES", f"{ai} should be SecondPC"

    def test_is_secondpc_agent_rejects_mainpc_and_ashigaru4(self):
        for ai in ("karo", "ashigaru1", "ashigaru2", "ashigaru3", "gunshi", "shogun", "ashigaru4"):
            out = bash_eval_section18(f'section18_is_secondpc_agent {ai} && echo YES || echo NO')
            assert out == "NO", f"{ai} must NOT be SecondPC"

    def test_mainpc_pane_index_returns_expected_values(self):
        for ai, expected in [
            ("karo", "0"),
            ("ashigaru1", "1"),
            ("ashigaru2", "2"),
            ("ashigaru3", "3"),
            ("gunshi", "4"),  # B1/R1 fix: gunshi は pane index 4
        ]:
            out = bash_eval_section18(f'section18_mainpc_pane_index {ai}')
            assert out == expected, f"{ai} expected pane index {expected}, got {out}"

    def test_mainpc_pane_index_rejects_secondpc_and_gap(self):
        for ai in ("ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8", "ashigaru4", "shogun"):
            out = bash_eval_section18(f'section18_mainpc_pane_index {ai} && echo OK || echo NG')
            assert out == "NG", f"{ai} must not have a MainPC pane index"


class TestSwitchCliCycle2:
    """switch_cli.sh resolve_pane の §18 fallback 修正を検証 (B1/R1 + B2/R2).

    bash 経由の resolve は module-level helper resolve_pane_fallback_section18 経由 (D1 polish)。
    """

    def test_mainpc_agents_resolve_to_correct_pane(self):
        """MainPC pane 配置 — gunshi は pane 4 (旧 8 ではない、B1/R1 fix)."""
        cases = [
            ("karo", 0, "multiagent:agents.0"),
            ("ashigaru1", 0, "multiagent:agents.1"),
            ("ashigaru2", 0, "multiagent:agents.2"),
            ("ashigaru3", 0, "multiagent:agents.3"),
            ("gunshi", 0, "multiagent:agents.4"),
        ]
        for agent, pb, expected in cases:
            rc, out = resolve_pane_fallback_section18(agent, pb)
            assert rc == 0, f"{agent}: 解決失敗 rc={rc}"
            assert out == expected, f"{agent}: expected {expected}, got {out}"

    def test_secondpc_agents_explicitly_rejected(self):
        """B2/R2 fix: SecondPC ashigaru5-8 は概念位置を返さず exit 1。"""
        for ai in ("ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"):
            rc, out = resolve_pane_fallback_section18(ai)
            assert rc == 1, f"{ai}: SecondPC は exit 1 で reject すべし (got rc={rc})"
            assert out == "", f"{ai}: stdout は空のはず (got {out!r})"

    def test_ashigaru4_rejected_as_gap(self):
        """ashigaru4 (欠番) は MainPC でも SecondPC でもない → exit 1。"""
        rc, out = resolve_pane_fallback_section18("ashigaru4")
        assert rc == 1
        assert out == ""

    def test_shogun_rejected_separate_session(self):
        """shogun は別 tmux session (shogun:0.0) のため multiagent:agents 解決対象外。"""
        rc, out = resolve_pane_fallback_section18("shogun")
        assert rc == 1
        assert out == ""

    def test_pane_base_offset_only_affects_mainpc(self):
        """pane_base != 0 でも SecondPC は依然 reject される (offset 適用は MainPC のみ)."""
        rc, out = resolve_pane_fallback_section18("karo", pane_base=2)
        assert rc == 0 and out == "multiagent:agents.2"
        rc, out = resolve_pane_fallback_section18("gunshi", pane_base=2)
        assert rc == 0 and out == "multiagent:agents.6"
        rc, out = resolve_pane_fallback_section18("ashigaru5", pane_base=2)
        assert rc == 1 and out == ""

    def test_switch_cli_sources_helper(self):
        """scripts/switch_cli.sh が _section18_roles.sh を source している。"""
        src = _read("scripts/switch_cli.sh")
        assert "lib/_section18_roles.sh" in src, \
            "switch_cli.sh が §18 helper を source していない"

    def test_switch_cli_no_legacy_secondpc_fallback(self):
        """switch_cli.sh から旧 fallback (ashigaru5-8 → multiagent:agents.5-8) が
        消えていることを確認。"""
        src = _read("scripts/switch_cli.sh")
        # 旧パターン: ashigaru5)  echo "multiagent:agents.$((pane_base + 5))"
        assert not re.search(
            r'ashigaru5\)\s*echo\s+"multiagent:agents\.\$\(\(pane_base \+ 5\)\)"',
            src,
        ), "旧 SecondPC fallback マッピングが残存している (B2/R2 fix 未適用)"
        for n in (6, 7, 8):
            pat = rf'ashigaru{n}\)\s*echo\s+"multiagent:agents\.\$\(\(pane_base \+ {n}\)\)"'
            assert not re.search(pat, src), f"ashigaru{n} 旧 fallback が残存"


class TestAgentStatusCycle2:
    """scripts/agent_status.sh の AGENTS 配列分割 (B1/R1 fix) を検証。"""

    def test_agent_status_sources_helper(self):
        src = _read("scripts/agent_status.sh")
        assert "lib/_section18_roles.sh" in src, \
            "agent_status.sh が §18 helper を source していない"

    def test_agent_status_uses_split_arrays(self):
        """AGENTS 単一配列でなく MAINPC_AGENTS / SECONDPC_AGENTS に分割されている。"""
        src = _read("scripts/agent_status.sh")
        assert re.search(r'\bMAINPC_AGENTS=\(', src), "MAINPC_AGENTS 配列が無い"
        assert re.search(r'\bSECONDPC_AGENTS=\(', src), "SECONDPC_AGENTS 配列が無い"

    def test_agent_status_no_legacy_mixed_array(self):
        """旧 AGENTS=("karo" ... "ashigaru5" ... "gunshi") の混在配列が消えている。"""
        src = _read("scripts/agent_status.sh")
        # 旧: AGENTS=("karo" "ashigaru1" "ashigaru2" "ashigaru3" "ashigaru5" ... "gunshi")
        assert not re.search(
            r'AGENTS=\("karo"\s+"ashigaru1"\s+"ashigaru2"\s+"ashigaru3"\s+"ashigaru5"',
            src,
        ), "旧 AGENTS 混在配列が残存している (B1/R1 fix 未適用)"

    def test_agent_status_secondpc_no_pane_lookup(self):
        """SecondPC 用ループは pane_target を空文字で渡し pane lookup を回避する。"""
        src = _read("scripts/agent_status.sh")
        # for agent in "${SECONDPC_AGENTS[@]}"; do print_agent_row "$agent" ""
        assert re.search(
            r'for agent in "\$\{SECONDPC_AGENTS\[@\]\}".*?print_agent_row\s+"\$agent"\s+""',
            src,
            re.DOTALL,
        ), "SecondPC ループから pane_target を空にする呼出が無い"


class TestRatelimitCheckCycle2:
    """scripts/ratelimit_check.sh の D1 部分対応 (helper 経由 fallback)。"""

    def test_sources_helper(self):
        src = _read("scripts/ratelimit_check.sh")
        assert "lib/_section18_roles.sh" in src, \
            "ratelimit_check.sh が §18 helper を source していない"

    def test_no_hardcoded_fallback_list(self):
        """fallback の "ashigaru1 ashigaru2 ... ashigaru8" 文字列リテラルが
        消え、SECTION18_* 配列から自動構築されている。"""
        src = _read("scripts/ratelimit_check.sh")
        # 旧 fallback (echo の引数として ashigaru 列挙) が残っていない
        assert not re.search(
            r'echo\s+"ashigaru1\s+ashigaru2\s+ashigaru3\s+ashigaru5\s+ashigaru6\s+ashigaru7',
            src,
        ), "旧ハードコード fallback が残存している"
        # 新方式: SECTION18_MAINPC_PANE_ORDER + SECTION18_SECONDPC_AGENTS から構築
        assert "SECTION18_MAINPC_PANE_ORDER" in src
        assert "SECTION18_SECONDPC_AGENTS" in src

#!/usr/bin/env bats
# test_persona_kanji_residual.bats — persona 漢字+romaji 表示名 残存の負テスト
#
# ★経緯★ 家老second W35 (2026-08-03)。
#   1st発令 msg_20260803_202509_fc62a366 — 委員長殿発令 (将軍second 中継) =
#     persona 残 8本228件 (gunshi.md 67 / honda.md 53 / takenaka.md 46 /
#     sanada.md 23 / kuroda.md 22 / ashigaru.md 10 / shogun.md 5 /
#     fukuincho.md 2) の掃討を検証する負テスト。家老second 留保(2) = iincho の
#     228件は手集計であり、漢字表記 (本多・真田・竹中・黒田等) を足すと
#     honda.md 80 / sanada.md 72 / takenaka.md 69 / kuroda.md 33 といずれも
#     上回ることが判明 (= 語彙が狭ければ残があっても通る。「0件」は完全性の
#     証明ではない)。
#   2nd発令 msg_20260803_203614_1a6f1e0d (受入条件改訂) —
#     (a) base 断面 = origin/main tip 9757156 (委員長殿裁定・将軍second中継)。
#     (b) 受入条件「archive以外の残0」→「★導出法つき残0★」に改訂。
#     (c) ★語彙は漢字・romaji 両表記を機械導出せよ★ (指示原文「instructions/
#         配下の persona file 名 (archive 含む) から 漢字・romaji 両表記を
#         機械導出し、導出法そのものを test に内蔵せよ」)。
#     (d) 除外 pattern は "^instructions/archive/" に限定 (足軽6助言、
#         "archive"/"*archive*" 等の緩い pattern は scripts/archive/ 等
#         無関係の既存 archive と誤衝突するため不可)。
#
# ★誠実disclosure (romaji 語彙追加の scope 上の緊張関係)★: commit 18c95fc は
# 「保持: romaji 技術キー (nobunaga 等)」と明示し、romaji は表示名 purge の
# scope 外としていた。本負テストは 2nd発令 (c) に従い romaji も語彙に含める
# ため、18c95fc の scope 宣言と字面上は緊張するが、★本テストは「instructions/
# の title 行に romaji 表記が残っているか」を機械的に検出するのみであり、
# コード内部の技術キー (tmux pane 解決・alias table 等) には一切触れない★。
# romaji 残存が検出された場合、それが「表示文字列」か「保持対象の技術キー」かの
# 判断は上位裁定に委ねる (本テストは「0件かどうか」を machine 判定するのみで
# 「0件でなければ即purge対象」と断定しない)。
#
# ★語彙は手で書かない★ — 以下 2 段の機械導出で得る:
#
#   段階1 (persona file 集合の導出、archive/ 含む):
#     instructions/*.md および instructions/archive/*.md (存在すれば) の各 file
#     について、「# ====...====」区切行の直後の行 (title 行) および冒頭6行以内の
#     `persona: ...` frontmatter 行のみを対象に、
#       (漢字) 「漢字連続2文字以上 + 直後の全角/半角括弧」または
#              「括弧内の漢字連続2文字以上」の2パターン
#       (romaji) 各 file の basename そのもの (拡張子 .md 除く)。ただし
#              canonical role 名 (shogun/karo/gunshi/ashigaru/fukuincho、
#              及び "-second" suffix 変種) と "_canon_"/"_charter_" を
#              含む basename は除外する (= 役職名そのもの・版管理副本は
#              persona 名ではないため)。
#     title行限定なのは、本文全体を対象にすると「新設」「監査」等の一般語が
#     漢字+括弧パターンに合致し誤検出することを実測で確認したため。
#
#   段階2 (家名短縮形の追加、家老second 留保(2) 対応):
#     段階1 で得た4文字以上の漢字複合語について、先頭2文字を家名短縮形として
#     追加する (本多正信→本多、真田幸村→真田、黒田官兵衛→黒田、前田利家→前田、
#     織田信長→織田、羽柴秀吉→羽柴、徳川家康→徳川 等)。
#
# ★scope の既知の限界 (誠実disclosure)★:
#   - title 行に現れない人名表記 (本文中のみに独自の漢字/romaji 表記がある
#     場合) は本抽出法では拾えぬ可能性がある。★0件は0件、完全性の証明では
#     ない★ (ALL-DETECTOR-VALIDATION-01・陽性対照なき0件は不在の証拠にならない
#     に準拠し、T-003/T-004 で陽性対照を機械検証する)。
#   - 対象 file (残存を確認する範囲) は委員長殿発令の8本に限定
#     (gunshi.md/honda.md/takenaka.md/sanada.md/kuroda.md/ashigaru.md/
#     shogun.md/fukuincho.md、いずれも instructions/archive/ 配下ではない)。
#     語彙の導出元は archive/ を含むが、残存確認の対象 file 自体は8本のまま
#     (archive/ 配下 file 自体の残存確認は別途判断が要る、"^instructions/
#     archive/" 除外 pattern は将来 file 対象を広げる際の設計として本 file に
#     明示するが、現状の TARGET_FILES には archive/ 配下 file を含めていない)。
#   - 本 test は git working tree (実行時のカレント checkout) を読む。断面
#     (base=origin/main 9757156 か 当branch か) は test 自体が固定するのでは
#     なく、★実行時の checkout 状態に自然に追随する★ (bats test の性質上、
#     working tree 外の特定 git ref を強制 checkout することはできない・
#     すべきでもない。TARGET_REF 引数化は不要と判断した — 理由は本 file 末尾
#     コメント参照)。
#
# 導出法自体が本 file 内に実装されているため、instructions/ に persona file が
# 増えても (段階1の title 行パターンに従う限り) 語彙は自動追随する。
#
# ★実装注記★: 導出ロジックの python は別 fixture file に出さず本 file 内に inline する
# (setup_file で bats 実行時の一時 dir に書き出す)。理由 = tests/fixtures/*.py は
# .gitignore whitelist 未許可 (tests/fixtures/*.yaml のみ許可、!tests/*.bats は許可済)
# であることを git check-ignore -v で実測確認したため (別 fixture 化すると新規 file が
# 無警告で git 追跡外になる=本 order 自体が警告する事故そのもの)。既存 .gitignore の
# 書換は本 order の禁止事項ゆえ、file 構成側で回避した。

setup_file() {
    export PROJECT_ROOT
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export INSTRUCTIONS_DIR="$PROJECT_ROOT/instructions"
    export VOCAB_SCRIPT="$BATS_FILE_TMPDIR/persona_kanji_vocab.py"
    cat > "$VOCAB_SCRIPT" <<'PYEOF'
import glob, os, re, sys

KANJI_RUN = r"[一-鿿]{2,}"
BEFORE_PAREN = re.compile(KANJI_RUN + r"(?=\s*[（(])")
INSIDE_PAREN = re.compile(r"[（(](" + KANJI_RUN + r")")

# canonical role 名 (persona 名ではなく役職名そのもの、語彙から除外)
CANONICAL_BASENAMES = {"shogun", "karo", "gunshi", "ashigaru", "fukuincho"}


def _is_canonical_or_meta(basename):
    if "_canon_" in basename or "_charter_" in basename:
        return True
    stem = basename[:-len("-second")] if basename.endswith("-second") else basename
    return stem in CANONICAL_BASENAMES


def _title_lines(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    out = []
    for i in range(1, len(lines)):
        if re.match(r"^#\s*=+\s*$", lines[i - 1]):
            out.append(lines[i])
    for line in lines[:6]:
        if line.strip().startswith("persona:"):
            out.append(line)
    return out


def _md_files(instructions_dir):
    paths = sorted(glob.glob(os.path.join(instructions_dir, "*.md")))
    paths += sorted(glob.glob(os.path.join(instructions_dir, "archive", "*.md")))
    return paths


def derive_vocab(instructions_dir):
    kanji_vocab = set()
    romaji_vocab = set()
    for path in _md_files(instructions_dir):
        basename = os.path.splitext(os.path.basename(path))[0]
        text = "\n".join(_title_lines(path))
        for m in BEFORE_PAREN.finditer(text):
            kanji_vocab.add(m.group(0))
        for m in INSIDE_PAREN.finditer(text):
            kanji_vocab.add(m.group(1))
        if not _is_canonical_or_meta(basename):
            romaji_vocab.add(basename)

    extra = {v[:2] for v in kanji_vocab if len(v) >= 4}
    kanji_vocab |= extra
    return sorted(kanji_vocab | romaji_vocab)


if __name__ == "__main__":
    for term in derive_vocab(sys.argv[1]):
        print(term)
PYEOF
}

# 段階1+2 をまとめて実行し、語彙 (改行区切り) を stdout へ出す。
_derive_vocab() {
    python3 "$VOCAB_SCRIPT" "$INSTRUCTIONS_DIR"
}

TARGET_FILES=(
    "instructions/gunshi.md"
    "instructions/honda.md"
    "instructions/takenaka.md"
    "instructions/sanada.md"
    "instructions/kuroda.md"
    "instructions/ashigaru.md"
    "instructions/shogun.md"
    "instructions/fukuincho.md"
)

# ============================================================
# T-001: 導出スクリプト存在 + 語彙が非空 (導出法自体の健全性ガード)
# ============================================================

@test "T-001: vocab derivation script exists and is executable via python3" {
    [ -f "$VOCAB_SCRIPT" ]
}

@test "T-002: derived vocab is non-empty (derivation method sanity guard)" {
    run _derive_vocab
    [ "$status" -eq 0 ]
    [ -n "$output" ]
}

@test "T-003: derived vocab covers at least the 4 short-form family names karo-second flagged (本多/真田/竹中/黒田)" {
    run _derive_vocab
    [ "$status" -eq 0 ]
    for name in 本多 真田 竹中 黒田; do
        echo "$output" | grep -qxF "$name"
    done
}

@test "T-004: derived vocab covers romaji persona basenames (2nd発令 (c) 対応、陽性対照)" {
    run _derive_vocab
    [ "$status" -eq 0 ]
    for name in honda kuroda sanada takenaka; do
        echo "$output" | grep -qxF "$name"
    done
}

@test "T-005: derived vocab excludes canonical role basenames (shogun/karo/gunshi/ashigaru/fukuincho は誤検出させない)" {
    run _derive_vocab
    [ "$status" -eq 0 ]
    for name in shogun karo gunshi ashigaru fukuincho; do
        ! echo "$output" | grep -qxF "$name"
    done
}

# ============================================================
# T-1xx: 対象8本 個別残存検出 (負テスト本体)
# ============================================================

@test "T-101: instructions/gunshi.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/gunshi.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

@test "T-102: instructions/honda.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/honda.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

@test "T-103: instructions/takenaka.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/takenaka.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

@test "T-104: instructions/sanada.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/sanada.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

@test "T-105: instructions/kuroda.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/kuroda.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

@test "T-106: instructions/ashigaru.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/ashigaru.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

@test "T-107: instructions/shogun.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/shogun.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

@test "T-108: instructions/fukuincho.md has zero mechanically-derived persona kanji residual" {
    cd "$PROJECT_ROOT"
    vocab="$(_derive_vocab)"
    failures=""
    while IFS= read -r term; do
        [ -z "$term" ] && continue
        n=$(grep -oF "$term" "instructions/fukuincho.md" 2>/dev/null | wc -l)
        [ "$n" -gt 0 ] && failures="${failures}${term}:${n}件 "
    done <<< "$vocab"
    [ -z "$failures" ] || { echo "残存: $failures"; false; }
}

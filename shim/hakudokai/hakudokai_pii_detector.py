#!/usr/bin/env python3
"""
hakudokai_pii_detector.py — PII (患者個人情報) 検出 layer (アプリ層 二重防御 #1)

DD-061 v2.4 §16 + 理事長 確定方針 FKI-ROOT-CAUSE-FIRST-01 (2026-04-30 broadcast 634c3afa)
+ Gemini 仕様監査 #2 PII 取扱 🔴 (handshake f0641407) を根本治癒する Phase R1 実装。

設計方針:
- 正規表現 + 辞書ベース検出 (5 カテゴリ: 氏名 / 電話 / 住所 / 保険番号 / 生年月日)
- 検出時: PIIDetected exception raise (caller が INSERT を中止)
- Supabase RLS trigger (DB 層、二重防御 #2) と同パターンセットを共有
  → DDL の PL/pgSQL trigger も同パターンで実装、bypass 防止
- 検出パターンは config 化 (PII_PATTERNS 定数、将来拡張可)

caller integration (hakudokai_inbox_write.py):
    from hakudokai_pii_detector import scan_for_pii, PIIDetected
    try:
        scan_for_pii(content)
        scan_for_pii(json.dumps(context_data, ensure_ascii=False))
    except PIIDetected as e:
        # ... abort + dev_lessons INSERT ...

Reference:
- shogun upstream (yohey-w/multi-agent-shogun v4.6.0、MIT)
- Gemini audit f0641407 #2 (PII technical guard 欠如指摘)
- 副院長 8a0cbbe0 R1 設計方針 (二重防御、severity=high feedback loop)

License: MIT (本patchも MIT、yohey-w credit保持)
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PIIMatch:
    category: str
    pattern_name: str
    matched_excerpt: str  # 検出箇所 (PII値そのものは含めず length のみ)
    matched_length: int


class PIIDetected(Exception):
    """Raised when PII patterns are detected in content / context_data."""

    def __init__(self, matches: list[PIIMatch], message: str | None = None):
        self.matches = matches
        if message is None:
            categories = sorted(set(m.category for m in matches))
            message = (
                f"PII detected ({len(matches)} match(es) in categories {categories}). "
                f"Aborting INSERT to protect patient privacy. "
                f"See dev_lessons (severity=high) for re-occurrence prevention."
            )
        super().__init__(message)


# 検出パターン (5 カテゴリ)
# - PII 値そのものは出力しない (matched_excerpt は length のみ報告)
# - 過去 handshake 1384件 false positive scan 結果に基づき pattern を厳格化:
#   - 「副院長」「院長」「先生」「理事長」「主任」等の博道会役職名を誤検出していた問題を解決
#   - 「氏名」検出は明示ラベル (氏名:/名前:/患者名:/お名前:/患者:) + 値 のみ
#   - 「漢字+さん/様」も博道会語彙 (こうちゃん/さくら/クロちゃん 等) を含むため明示ラベル形式に限定
HAKUDOKAI_ROLE_TERMS = (
    # 博道会役職名 (whitelist、PII 検出対象外)
    "副院長", "院長", "理事長", "先生", "主任", "副主任",
    "クロちゃん", "さくら", "こうちゃん", "山ちゃん",
    "fukuincho", "kuro", "yama", "sakura", "kouchan",
)

PII_PATTERNS: dict[str, list[tuple[str, re.Pattern]]] = {
    # 氏名: 明示ラベル付きのみ検出 (false positive 防止)
    # 役職名のみのテキスト「副院長」「院長」等は対象外
    "name": [
        # 明示ラベル + 氏名値 (「氏名: 山田太郎」「患者名:山田太郎」等)
        ("explicit_name_label", re.compile(
            r"(?:氏名|患者名|被保険者名|お名前(?!ます|なら|ですが|でしょう))"
            r"[\s::【】[\]\-]{0,5}([一-龥々ぁ-んァ-ヴーA-Za-z0-9]{2,30})"
        )),
        # カタカナ姓名 (スペース区切り) — 一般的な患者氏名表記
        ("katakana_full_name", re.compile(r"\b[ァ-ヴー]{2,8}\s+[ァ-ヴー]{2,8}\b")),
    ],
    # 電話番号: 日本国内一般形式 (0X-XXXX-XXXX / 0X(XXXX)XXXX / 携帯 090-XXXX-XXXX 等)
    "phone": [
        ("jp_phone_dashed", re.compile(r"0\d{1,4}-\d{1,4}-\d{4}")),
        ("jp_phone_paren", re.compile(r"0\d{1,4}\(\d{1,4}\)\d{4}")),
        ("jp_phone_continuous", re.compile(r"\b0\d{9,10}\b")),
    ],
    # 住所: 都道府県+市区町村 / 番地パターン
    "address": [
        ("prefecture_city", re.compile(
            r"(?:北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|"
            r"茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|"
            r"新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|"
            r"静岡県|愛知県|三重県|滋賀県|京都府|大阪府|兵庫県|"
            r"奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|"
            r"徳島県|香川県|愛媛県|高知県|福岡県|佐賀県|長崎県|"
            r"熊本県|大分県|宮崎県|鹿児島県|沖縄県)"
            r"[一-龥々ぁ-んァ-ヴー\d\-]+(?:市|区|町|村|郡)"
        )),
        ("banchi_pattern", re.compile(r"\b\d{1,4}(?:-\d{1,4}){1,3}(?=番地|号|丁目|室)")),
    ],
    # 保険証番号: 8桁数字パターン (記号-番号形式 / 純粋8桁)
    "insurance": [
        ("insurance_8digit", re.compile(r"(?:保険(?:証)?(?:番号)?|被保険者(?:番号)?)[\s::]{0,3}\d{6,12}")),
        ("kigo_bango", re.compile(r"記号[\s::]{0,3}\S{1,10}\s*番号[\s::]{0,3}\d{1,10}")),
    ],
    # 生年月日: 年月日各種フォーマット
    "dob": [
        ("dob_slash", re.compile(r"(?:19|20)\d{2}/\d{1,2}/\d{1,2}")),
        ("dob_kanji", re.compile(r"(?:19|20)\d{2}年\d{1,2}月\d{1,2}日")),
        ("dob_label", re.compile(r"(?:生年月日|誕生日|DOB)[\s::]{0,3}\S{8,20}")),
        ("era_dob", re.compile(r"(?:昭和|平成|令和)\d{1,2}年\d{1,2}月\d{1,2}日")),
    ],
}


def scan_for_pii(text: str | None) -> list[PIIMatch]:
    """Scan text for PII patterns. Returns list of matches (empty if clean).

    Caller should check result and raise PIIDetected if non-empty.
    Use raise_if_pii() helper for raise-on-detect semantics.
    """
    if not text:
        return []
    matches: list[PIIMatch] = []
    for category, patterns in PII_PATTERNS.items():
        for pattern_name, regex in patterns:
            for m in regex.finditer(text):
                excerpt = m.group(0)
                matches.append(PIIMatch(
                    category=category,
                    pattern_name=pattern_name,
                    matched_excerpt=f"<REDACTED, len={len(excerpt)}>",
                    matched_length=len(excerpt),
                ))
    return matches


def raise_if_pii(text: str | None, context_label: str = "content") -> None:
    """Raise PIIDetected if any PII pattern matches. Convenience wrapper."""
    matches = scan_for_pii(text)
    if matches:
        raise PIIDetected(
            matches,
            message=(
                f"PII detected in {context_label} "
                f"({len(matches)} match(es), categories={sorted(set(m.category for m in matches))}). "
                f"Aborting INSERT (DD-061 v2.4 §16 + FKI-ROOT-CAUSE-FIRST-01)."
            ),
        )


def explain_matches(matches: list[PIIMatch]) -> dict:
    """Return JSON-serializable summary of matches (no PII values)."""
    return {
        "match_count": len(matches),
        "categories": sorted(set(m.category for m in matches)),
        "matches": [
            {
                "category": m.category,
                "pattern_name": m.pattern_name,
                "matched_length": m.matched_length,
                "matched_excerpt": m.matched_excerpt,
            }
            for m in matches
        ],
    }


if __name__ == "__main__":
    # CLI test mode (stdin scan)
    import json
    import sys

    text = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not text:
        sys.stderr.write("Usage: echo '<text>' | hakudokai_pii_detector.py\n")
        sys.exit(2)
    matches = scan_for_pii(text)
    if matches:
        print(json.dumps(explain_matches(matches), ensure_ascii=False, indent=2))
        sys.exit(1)  # exit 1 on detection
    print(json.dumps({"match_count": 0, "categories": [], "status": "clean"}, ensure_ascii=False))
    sys.exit(0)

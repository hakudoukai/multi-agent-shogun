# Task: adjudicate QC "conflict" pages of a Japanese dental-insurance reference book (赤本R8), machine OCR vs AI reading

You are a read-only adjudicator. Do NOT modify anything under ~/akahon-r8. Write ONLY your own output file.

Materials, for each page N (4-digit zero-padded, e.g. 0701), in /Users/momizimac/wt/a3-fae4680a-scratch/:
- `pNNNN_ocr.txt` = machine OCR text (Tesseract-like; often garbled on tables and circled numbers)
- `pNNNN_ai.txt`  = AI (Gemini) transcription of the page (if the page had >1 AI entry they are joined by "=====")
- `conflicts.jsonl` = QC record per page: sim_ocr (similarity), nums_missing_in_ai (key tokens present in machine source but absent in AI text), era_missing
- Original page image: `/Users/momizimac/akahon-r8/out/akahon/png/赤本R8_pNNNN.png` (view it with the Read tool)

Background: the QC tagged the page "conflict" either because similarity < 0.55 or because key tokens (令和N年, NN点, N歯, N回, 3+ digit numbers) found in the OCR are absent from the AI text. Known benign causes: the printed page number (= page - 142, bottom of page) and the footer legend "随時改定対象（令和8年4月の金属価格で試算）" are intentionally omitted by the AI transcription; OCR garbage on tables lowers similarity.

For EACH page in your list:
1. Read the PNG. Read both texts. Look up the page's QC record.
2. For every token in nums_missing_in_ai: locate it on the image. Classify: printed page number / footer legend / real body content / OCR misread (not actually on the page).
3. Spot-check the AI text against the image: title, case number, all 点数 values in the table/body, dates, tooth notation where legible, totals (計 NNN点). Count how many values you checked and how many mismatched.
4. Decide `adopted`:
   - "ai"  = AI text is faithful to the image in body content (differences are only page number/footer/layout or OCR garbage)
   - "ocr" = OCR is the more faithful source for this page (AI dropped or hallucinated real body content and OCR has it right)
   - "neither" = both have real errors/omissions of body content; name exactly what is wrong (requires human SE re-read)
   Be strict: if the AI omitted or changed any real body number/word (not page number/footer), do NOT say "ai" silently — either "neither" with the defect listed, or "ai" only if the defect is purely presentational; always list defects.
5. Write one JSON line per page to your output file (append, UTF-8, ensure_ascii false), fields exactly:
   {"page": N, "source_file": "赤本R8_PartNN.pdf" (copy from conflicts.jsonl), "adopted": "ai|ocr|neither",
    "reason": "<ONE line in Japanese, ≤120字, concrete: what the missing tokens are and what you verified>",
    "missing_token_class": {"<token>": "page_number|footer_legend|body|ocr_misread"},
    "ai_defects": ["<concrete body defect with image value vs AI value>", ...] (empty list if none),
    "values_checked": <int>, "values_mismatched": <int>}

Write the file with a small python3 script (json.dumps) — never hand-type JSON escapes. After finishing all pages, verify: line count == number of pages in your list, every line parses, pages set == your list. Report back: the output path, line count, count per adopted value, and any page you could not judge (and why). Keep your final report short.

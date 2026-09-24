# Task: transcribe pages of a Japanese dental-insurance reference book (赤本R8) from the original page image

You are a read-only transcriber. Do NOT modify anything under ~/akahon-r8 or any repo. Write ONLY your own output file.

The AI pipeline produced an EMPTY transcription for these pages. Your job is to produce a candidate row per page, read from the ORIGINAL IMAGE.

Materials, per page N (integer; NNNN = 4-digit zero-padded):
- Original image: `/Users/momizimac/akahon-r8/out/akahon/png/赤本R8_pNNNN.png` — view it with the Read tool. THIS IS THE SOURCE OF TRUTH.
- Machine OCR (garbled, auxiliary only): `/Users/momizimac/wt/a3-a51340c6-scratch/pNNNN_ocr.txt`. Use it only to help disambiguate; never copy OCR errors.
- Part file for the page: Part number = ceil(N/15), zero-padded to 2 (e.g. page 700 → Part47). source_file = `赤本R8_PartNN.pdf`.

For each page:
1. Read the image carefully (zoom is not available; read what is legible).
2. Transcribe the full body into `content_text` in the same style the pipeline uses for other pages: plain text paragraphs, headings as `### 見出し`, tables as Markdown tables (`| a | b |`), circled numbers/tooth notation as printed (①②, ⑥⑤④ etc.), full-width Japanese punctuation as printed. Include 点数, 症例番号, 摘要 notes, 計 lines exactly.
   - Exclude the running page number and the repeating footer/side legend (e.g. 本/診 side tabs) — list those you excluded in `excluded`.
   - If the page is a blank page, an illustration-only page, or a divider, say so in `page_kind` and give a short content_text describing the visible text only (never invent).
3. `title`: the page's main heading as printed (or the case title, e.g. 「症例 212 …」). If none, use the section heading carried at the top.
4. Mark anything you could not read with 〔判読不能〕 inline and count them in `illegible_count`. Do NOT guess numbers — a wrong 点数 is worse than 〔判読不能〕.
5. Self-check: re-open the image and verify every number (点数, 回数, 歯式, 症例番号, 令和 dates) in your content_text. Record how many numbers you checked and how many you corrected.

Output: append ONE JSON object per line (JSONL) to your output file, keys exactly:
{"source_file": "赤本R8_PartNN.pdf", "source_page": N, "title": "...", "content_text": "...",
 "page_kind": "body|table|case|blank|illustration|divider|other",
 "excluded": ["page number 700", "..."], "illegible_count": 0,
 "numbers_checked": 0, "numbers_corrected_in_selfcheck": 0,
 "image_path": "/Users/momizimac/akahon-r8/out/akahon/png/赤本R8_pNNNN.png",
 "confidence": "high|medium|low", "notes": "..."}

Write with python json.dumps(ensure_ascii=False) (one line per page). Process every page in your batch; do not stop early. At the end, print the number of lines in your output file.

# ★この dir の *_pruned.yaml は multi-document YAML である★

yaml.safe_load() では読めない。必ず yaml.safe_load_all() を用い、末尾の None 要素を除くこと。
誤った読み方をすると「在るのに読めぬ」状態になり、沈黙を「便が無い」と読み違える。

読取具 = scripts/read_pruned_archive.sh（足軽7号作。.gitignore により git 不可視）

同じ警告が scripts/inbox_write.sh から各 doc の前に書き込まれていたが、
2026-08-05 15:54:42〜18:07:02 の間に working tree から無断削除され、未復旧である。
∴ それ以降に積まれた doc には警告が付いていない。

正本 = docs/incident_logs/2026-08-05_archive_multidoc_read_warning.md

本 file は queue/ 配下だが **git 外ではない** —— .gitignore:18 の !README.md に救われ、
git status は ?? を返す（＝追跡可能）。判定は git check-ignore -q の終了コードで行うこと
（-v は否定規則にも出力を出し 0 で終わるため、可否の判定に使ってはならない）。

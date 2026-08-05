# W166 証拠 5本 救出 対応表 (W177・ashigaru2)

> 目的: `2026-08-04_w166_coverage_estimate_a2.md` 本文中の裸ファイル名参照 (下記) は
> ★本文を一字も変えぬ★ ため旧名を指したままである。本 INDEX が旧名→新 path の橋を架ける。
> 本文が指す物と実体が別の file になった経緯は本 file と
> `2026-08-04_karo-second_day_ledger.md` / `2026-08-04_secondpc-day-state-snapshot.md` を参照。

## 対応表

| 本文中の裸参照 (旧名) | 旧 path (repo 外・scratchpad・gitignore対象で消滅していた) | 新 path (本 repo・.md・git 追跡下) | sha256 (全64桁・旧=新で不変) | 行数 |
|---|---|---|---|---|
| `w166_population_paths.txt` | `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/e3a256f6-e4e6-452f-888d-ffdadc795479/scratchpad/w166_population_paths.txt` | `docs/incident_logs/2026-08-04_w166_evidence_population_paths.md` | `5f209d74a0d61c330d84268851ede76b83f6f8ad55e5bb7b5f5fd731a6e5fdd0` | 136 |
| `w166_dump_full_paths.txt` (本文中は変数 `POP` 経由で参照) | `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/e3a256f6-e4e6-452f-888d-ffdadc795479/scratchpad/w166_dump_full_paths.txt` | `docs/incident_logs/2026-08-04_w166_evidence_dump_full_paths.md` | `d7b874b1a1edecc44261e565f48402a61f9626503420087d03eb0d292af69999` | 136 |
| `w166_live_find.txt` | `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/e3a256f6-e4e6-452f-888d-ffdadc795479/scratchpad/w166_live_find.txt` | `docs/incident_logs/2026-08-04_w166_evidence_live_find.md` | `1fc7dbd3927e670b844cd4e05fd0ce14c10f6ac30f7382b39ff4300bfe4338b8` | 140 |
| `w166_crossref_scan.txt` | `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/e3a256f6-e4e6-452f-888d-ffdadc795479/scratchpad/w166_crossref_scan.txt` | `docs/incident_logs/2026-08-04_w166_evidence_crossref_scan.md` | `4c328f5b870ea06783e4185c292b9ed087f9dbcbad005baee1897c91debbf55e` | 50 |
| `w166_sample25.txt` | `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/e3a256f6-e4e6-452f-888d-ffdadc795479/scratchpad/w166_sample25.txt` | `docs/incident_logs/2026-08-04_w166_evidence_sample25.md` | `9612dd63d6ae5d3d85803e9ed60617e7558f61d5c27f6f883b0891ef28273c7b` | 25 |

**確認方法**: 上記 5 行いずれも sha256sum(旧 scratchpad 実体) == sha256sum(新 docs/incident_logs 実体) を実測済 (2026-08-04)。
中身は一字も変えていない — 変えたのは file 名と拡張子のみ。

## `git status --short` 実測 (check-ignore 出力ではない・一件ずつ確認)

```
?? docs/incident_logs/2026-08-04_w166_evidence_crossref_scan.md
?? docs/incident_logs/2026-08-04_w166_evidence_dump_full_paths.md
?? docs/incident_logs/2026-08-04_w166_evidence_live_find.md
?? docs/incident_logs/2026-08-04_w166_evidence_population_paths.md
?? docs/incident_logs/2026-08-04_w166_evidence_sample25.md
```

5本全てが `??` で載っている。載らぬ物は無かった (載らぬ物があればここで止めて報告する規律だった)。

## 本文中の該当箇所 (書き換えていない・参照のみ)

`docs/incident_logs/2026-08-04_w166_coverage_estimate_a2.md`:
- L35: `POP=w166_dump_full_paths.txt (136件、W159保存物から抽出)`
- L36: `shuf --random-source=/dev/urandom -n 25 "$POP" | sort > w166_sample25.txt`

上記2行は旧名 (`w166_dump_full_paths.txt` / `w166_sample25.txt`) を指したままである。
本 INDEX の対応表を介して読み手が実体 (新 path) を辿れるようにした。
`population_paths` / `live_find` / `crossref_scan` は本文中に file 名としての明示参照は無いが
(集計・記述の中で言及)、同一の救出対象として本表に含めた。

## (4) 本工区が新たに開ける穴 (委員長発令 (4) への回答)

1. **`.txt` を `.md` と呼ぶ誤解**: 拡張子を `.md` に変えたのは *git の whitelist ルール
   (`.gitignore:202 !docs/incident_logs/*.md`) を通す為だけ*であり、中身が markdown 記法で
   書かれていることを意味しない。実際、5本の中身は生の path 列 (`population_paths` /
   `dump_full_paths` / `live_find` / `sample25`) または簡易 grep 集計ログ (`crossref_scan`) で
   あり、markdown ではない。読み手が「`.md` だから整形された報告書」と誤認すると、
   生ログを report として扱う二次的な誤読を招く。
2. **「実行ログである」ことが拡張子から判らなくなる**: 元の `.txt` は「これは script の標準出力を
   リダイレクトした一次データである」ことを拡張子で示していた。`.md` へ改めた事でその区別が
   消え、後日 「これは誰かが手で書いた報告か、それとも機械的に採取した生データか」を
   file 名だけでは判別できなくなった (本 INDEX の存在が唯一の手掛かりになる)。
3. **INDEX 自体が新たな「単一障害点」になる**: 本文の裸参照を書き換えず INDEX で橋を架ける
   方式を取ったため、★本 INDEX が消えれば橋も消える★。INDEX は他の証拠 5本と同じ
   `docs/incident_logs/*.md` 規則で保護されているため即時の再発リスクは低いが、
   「本文を書き換えない」方針を採る限り、今後も本文↔実体の対応は INDEX 一枚に依存し続ける
   ことになる (型⑥「印は在るが何も指しておらぬ」の裏返し=「指す先が INDEX 経由の間接参照
   になった」)。
4. **命名 `w166_evidence_<元名>` の元名が短縮形である曖昧さ**: 対応表の「旧名」列に示した通り、
   新 file 名は `w166_` prefix と `.txt` を落とした短縮形 (`population_paths` 等) を使っている。
   本文中の完全な旧名 (`w166_dump_full_paths.txt`) と新 file 名の対応は本 INDEX を読まねば
   自明ではない (grep で新旧を機械的に突き合わせる場合、prefix/拡張子の差異を吸収する処理が
   別途必要)。

## 落度の記録 (karo-second 発令書内で自認済・本 INDEX でも保持)

karo-second は W173 で「docs/incident_logs/ へ移せ」とのみ命じ、拡張子の条件
(`!docs/incident_logs/*.md` が `.md` 限定で `.txt` を無警告除外する事) を告げていなかった。
ashigaru2 が (4) で問われるまで、この5本は「台帳には書かれているが実体は repo 外で
git 管理外のまま」= 型⑥「印は在るが何も指しておらぬ」に陥っていた。

# 追補 ―― 「`refs/remotes` に無い」は「origin に無い」の證に成らぬ

**刻 = 2026-09-17T19:44:21+0900 ／ 書いた者 = 家老mac ／ 親の紙 = `00_teisei.md`(不触)**

## ⑴ 何を誤つたか(逐語)

`00_teisei.md` 58行目、當席の筆:

> **`refs/remotes` には無い(=origin に無い)**。

**★括弧の中の等号が誤りである。★** `refs/remotes` は **origin ではない** ――
**手元が最後に fetch した時の写し**である。写しに無い事は、
**遠国の樹に無い事を意味せぬ**。

因は器の取り違へではなく、**問ひの取り違へ**である。
當席は「origin に在るか」を問ひながら、**手元の棚を見て答へた**。

## ⑵ 測り直した数(`driver/20_origin_wa_remotes_ni_arazu.py`)

同じ一本の枝 `karo-mac/km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917` を、**三つの器**で問うた
(`raw/24_sanmen.tsv` 逐語):

| 器 | rc | 出目 |
|---|---|---|
| 甲 `git show-ref --verify refs/heads/<枝>` | **0** | `157a9736fd1783ef2301ad2fa4b2f04fc9c47324` |
| 乙 `git show-ref --verify refs/remotes/origin/<枝>` | **128** | `fatal: … not a valid ref` |
| 丙 `git ls-remote origin refs/heads/<枝>` | **0** | `157a9736fd1783ef2301ad2fa4b2f04fc9c47324` |

**★乙だけが「無い」と言ふ。甲と丙は「在る」と言ふ。★**
**丙が origin を直に問ふ器である。∴ 枝は origin に在る。**

## ⑶ 歩き根が二つ在る事(母數の訂正)

| 歩き根 | 数 | 出所 |
|---|---|---|
| 甲 手元 `refs/heads` + `refs/remotes` | **73** | `raw/20_temoto_refs.txt` |
| 乙 origin の生 `git ls-remote --heads origin` | **250** (rc=0) | `raw/21_origin_nama.txt` |

**∴ `00_teisei.md` の「ref 母數 73」は ★手元の数★ である。**
紙は歩き根を宣して居る(21行目)ゆゑ **数そのものは偽らぬ**が、
**「origin の全体」と讀まれ得る所へ置いた**のは當席の疵である。

## ⑷ 門の版は origin の何處に在るか(乙の歩き根で)

- `scripts/checks/karo_mac_dasumae_gate.sh` の **321行版 `054c442eaee3886b2283f98f7c3a1ab8cb813b68`** を載せる origin の枝 = **1本**
  (`raw/22_origin_ni_aru_kono_ban.tsv` ―― `karo-mac/km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917` / `157a9736…`)
- **測れぬ枝 = 1本**(object が手元に無し ―― `raw/23_hakarenu.tsv`)。
  **★之は「載せぬ」ではない。「問へなんだ」である。★**

## ⑸ 之で**変はる**物

**「第四の便が運ぶ版は、origin が一度も見た事の無い物」―― 之は偽である。**
origin は `054c442e` を **枝一本の上に持つて居る**。
第四の便が為すのは「origin へ初めて渡す」事ではなく、
**`origin/main` の線へ載せる**事である。

## ⑹ 之で**変はらぬ**物(取り消さぬ)

- `origin/main` = `44ba23dc70d86d49fbb3a6ed26b5f497b71fd814` は **門を持たぬ** (`git cat-file -e` rc=**128**)。
- `157a9736…` は `origin/main` の **祖先に非ず** (`merge-base --is-ancestor` rc=**1**)。
- PR#23 head `571f338756775acd3e2d73dab5e423e9492d24a2` が載せる門は **`9cd550fc`(310行)** ―― disk の `054c442e` に非ず。
- ∴ **裁 seq327976「第四の便=054c442e」は数の上で立つ**(裁 seq328018 で不変と確かめられた)。

## ⑺ 意味せぬ事

- 「origin に在る」は **「main に在る」ではない**。枝一本の上に在るだけである。
- 「250本」は **origin の枝の数**であつて、tag も PR の ref も含まぬ(`--heads` ゆゑ)。
- 「測れぬ1本」を **0 と数へて居らぬ**。母數の外にも置いて居らぬ。**別欄に立てた。**

## ⑻ 己の疵として残す物

**★遠国を問ふ時は、遠国を叩く器で問へ。手元の棚は「最後に見た時の記憶」に過ぎぬ。★**
當席は既に一度、同じ形の誤りを犯して居る ――
「`find -newermt` が 0 だから實体が無い」(專任3 の件・19:29)。
**窓が空なのか、器が別の物を見て居るのか** ―― **二度とも後者であつた。**

## ⑼ 器と再現

```
cd /Users/momizimac/multi-agent-shogun
python3 docs/evidence/karo-mac_teisei-mon-no-todoki-20260917/driver/20_origin_wa_remotes_ni_arazu.py \
  /Users/momizimac/multi-agent-shogun \
  docs/evidence/karo-mac_teisei-mon-no-todoki-20260917/raw \
  scripts/checks/karo_mac_dasumae_gate.sh 054c442eaee3886b2283f98f7c3a1ab8cb813b68
```

**★乙の歩き根は網を渡る。∴ 数は「其の刻の origin」の数であつて、再現時に増減し得る。★**

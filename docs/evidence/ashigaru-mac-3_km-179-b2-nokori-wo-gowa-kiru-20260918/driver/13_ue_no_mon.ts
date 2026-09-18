// ★上の器(製品樹の validateEpisode)を呼ぶ ―― 呼び出し器は本束に置き、製品樹へは一字も書かぬ★
// 用: node <此file> <episode.json の path>   rc=0 valid / rc=1 invalid / rc=2 呼び方が違ふ
import { readFileSync } from 'node:fs'
import { validateEpisode } from '/Users/momizimac/DentalBI/frontend/src/features/child-passport/story-engine/episodes/validateEpisode.ts'

const p = process.argv[2]
if (!p) { console.error('★path を寄せよ★'); process.exit(2) }
const d = JSON.parse(readFileSync(p, 'utf-8'))
const r = validateEpisode(d)
console.log(`valid=${r.valid} errors=${r.errors.length}`)
for (const e of r.errors) console.log(`  ・${e}`)
process.exit(r.valid ? 0 : 1)

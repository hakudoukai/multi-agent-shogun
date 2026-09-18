// ★解決子 ―― 製品樹の拡張子無し import を .ts / .tsx へ解く(本束の内に置く・製品樹は触らぬ)★
export async function resolve(shitei, bunmyaku, tsugi) {
  try { return await tsugi(shitei, bunmyaku) }
  catch (e) {
    if (e && e.code === 'ERR_MODULE_NOT_FOUND' && /^\.{1,2}\//.test(shitei)) {
      for (const o of ['.ts', '.tsx', '/index.ts']) {
        try { return await tsugi(shitei + o, bunmyaku) } catch { /* 次を試す */ }
      }
    }
    throw e
  }
}

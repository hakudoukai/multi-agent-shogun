## 事後報(km-167 ⓐⓑⓒ・委員長裁 seq332367・変更統制の事後報)

- ⓐ lib/_section18_roles.sh: 識別子を persona 内部 id(hideyoshi/ieyasu/takenaka/maeda)から §18.1 の役名(karo/gunshi・a1-3・a5-8)へ。alias は逆向き(hideyoshi→karo / ieyasu→gunshi / nobunaga→shogun・役名は identity・maeda/takenaka は identity で残す)。pane 構成は不触・可逆(配列 2 本と map の向きのみ)。消費者 pane_identity.sh は両側正規化ゆゑ同値(直走 前後 rc0・DRIFT 0)。残: Python 版 shim/hakudokai/_section18_roles.py は persona の儘(pytest の SoT drift 6 件・CI 外)= 裁。
- ⓑ 撤回済 MDV2 試作の unit 4 紙を tests/archive へ git mv(消さず)。README 1 行「撤回済・的は archive」。
- ⓒ test.yml の SKIP 検め除外語に SUPERSEDED を追加(CRLF 保持)。TC-NFR-008 は残す。
- 後の手元模走(bash5+gnubin・Mac): root 58/0・selfwatch 19/0 skip1(許容)・unit 334/0・SKIP 検め 0・build-check rc0・shellcheck rc0。束 docs/evidence/ashigaru-mac-1_km-176-abc-wo-tsumi-saishuu-tip-de-hantei-wo-ichido-20260918/。

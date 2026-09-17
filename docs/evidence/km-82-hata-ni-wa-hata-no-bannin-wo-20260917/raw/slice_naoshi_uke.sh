# ★受ける口を番人へ替へる(裁 seq324588⑵)★ ―― `${NAME:-1}` は ★空文字を番人の前で呑む★ ゆゑ
#   口の儘では「在るが空」を分けられぬ。fix_flag は env_state(${+set})で先に分ける。
#   下流の比較器(`[ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]`)は ★一字も変へて居らぬ★。
fix_flag ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT

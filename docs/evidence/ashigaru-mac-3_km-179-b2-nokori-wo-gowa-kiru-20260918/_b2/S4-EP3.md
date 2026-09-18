# S4-EP3: 6さいのきょじん

- visit: 3
- season: S4
- audience: 6-7
- mission: いちばん おくの 歯に、はブラシを とどかせてみよう
- badge: きょじんバッジ
- parent_explanation_ref: S4-EP3

## 場1 background=hoshifuru_heigen_hiru
- actor: koron pose=stand anim=idle position=left
- actor: ryuta pose=stand anim=idle position=right

narrator: きらきらかわで みつけた、おくの
narrator: かたいもの。あれから、
narrator: しばらく たちました。
ryuta: ねえ、みて
narrator: リュウタが くちを あける
narrator: いちばん おくに
narrator: おおきな はが どんと ありました。
koron: でかっ！
narrator: コロンが こえを あげる
narrator: パパきょうりゅうが うなずきました。

@effect enter at=0 target=koron
@effect enter at=0 target=ryuta
@effect surprise at=4 target=ryuta
@voice at=4: リュウタくんが おおきく くちを あけます
@effect joy at=8 target=koron
@voice at=8: コロンちゃんが こえを あげます

## 場2 background=hoshifuru_heigen_hiru concurrency_cap=4
- actor: papa_dino pose=stand anim=idle position=center
- actor: you pose=stand anim=idle position=left
- actor: hana pose=stand anim=idle position=right
- actor: ryuta pose=stand anim=idle position=left

papa_dino: いちばん おおきくて、つよい はだよ
you: ぬけないの？
papa_dino: はえかわらない、おとなの はだよ
narrator: ハナちゃんが くびを かしげました。
hana: じゃあ、いつから きをつけるの？
narrator: パパきょうりゅうは、しずかに
narrator: いいました。
papa_dino: きょうから

@effect enter at=0 target=papa_dino
@effect enter at=1 target=you
@effect enter at=3 target=hana
@effect pause at=0 ms=800
@voice at=0: きょじんの 歯だ。いちばん 大きくて、いちばん つよい。かむ ちからの まんなかに なる
@voice at=2: ぬけない。生えかわらない。だから、はじめから 大人の 歯として 生えてくる
@effect pause at=2 ms=800

## 場3 background=hoshifuru_heigen_hiru
- actor: you pose=stand anim=idle position=center

narrator: きみは、いちばん おくまで はブラシを
narrator: のばしてみました。とどきにくい。でも、
narrator: とどいた。

@effect sparkle at=0
@effect transition at=0 to=reward

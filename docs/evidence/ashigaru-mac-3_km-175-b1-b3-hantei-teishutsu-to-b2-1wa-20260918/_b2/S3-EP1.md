# S3-EP1: 川をさかのぼる

- visit: 1
- season: S3
- audience: 5-6
- mission: きょう たべたものを ひとつ、おうちの人に はなしてみよう
- badge: たびだちバッジ
- parent_explanation_ref: S3-EP1

## 場1 background=kirakira_river_upstream
- actor: koron pose=crouch anim=idle position=left
- actor: hana pose=stand anim=idle position=right

narrator: きらきらかわのみずは、いつもより
narrator: つめたい。
koron: このかわ、どこから きてるんだろう
narrator: みずに てを つけた
narrator: ハナちゃんが きづく
narrator: うえを ゆびさす
hana: やまのほう、だれも しらない

@choice at=2: やまから: やまから きたのかも。|うみから: うみから きたのかな。
@effect enter at=0 target=koron
@effect enter at=0 target=hana
@effect sparkle at=3 target=koron
@effect surprise at=4 target=hana
@effect shake at=5 target=hana
@effect surprise at=6 target=hana
@voice at=3: コロンちゃんが みずに てを つけて いいました
@voice at=4: そのとき ハナちゃんが なにかに きづきました
@voice at=5: ハナちゃんが うえを ゆびさします
@voice at=6: あっちの 山のほう。だれも いったこと ないんだって

## 場2 background=kirakira_river_upstream
- actor: papa_dino pose=stand anim=idle position=center
- actor: koron pose=stand anim=idle position=left
- actor: hana pose=stand anim=idle position=right

narrator: パパきょうりゅうが うなずきました。
papa_dino: たべたもので、からだが できる

@effect transition at=0
@effect enter at=0 target=papa_dino
@effect pause at=1 ms=800
@voice at=1: 川は、山の水が あつまって できる。きみたちの からだも おなじだ。たべたものが、あつまって、きみの 歯や ほねに なる

## 場3 background=kirakira_river_upstream
- actor: you pose=crouch anim=idle position=center

narrator: きみは かわのみずを
narrator: すくって みました。てのひらの なかで
narrator: 、みずが きらきら ひかっています。
narrator: このみずも、いつか だれかの ちからに
narrator: なるのかな。

@choice at=2: すくう: みずが つめたい。|みるだけ: みずが きらきら する。
@effect transition at=0
@effect sparkle at=0
@effect transition at=3 to=reward

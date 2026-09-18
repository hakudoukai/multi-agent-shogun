# S4-EP1: はじめての ぐらぐら

- visit: 1
- season: S4
- audience: 6-7
- mission: ぐらぐらする 歯が あったら、おうちの人に おしえよう
- badge: ぐらぐらバッジ
- parent_explanation_ref: S4-EP1

## 場1 background=hoshifuru_heigen_yoru
- actor: you pose=crouch anim=idle position=left
- actor: koron pose=stand anim=idle position=right

narrator: ほしふるへいげんに ついた よる。
narrator: きみは、まえばを さわって、
narrator: うごきました。
narrator: ぐらっ。
you: ……とれちゃう
narrator: こわくて てを はなす
narrator: コロンちゃんが となりで きづきました。
koron: どうしたの？
you: はが、ぐらぐらする
narrator: コロンちゃんが めを まるくして、
narrator: それから にっこりしました。
koron: ぼくも なったよ！

@effect enter at=0 target=you
@effect enter at=0 target=koron
@effect shake at=3 target=you
@voice at=3: ぐらっ。まえばが うごきました
@effect surprise at=5 target=you
@voice at=5: こわくなって、てを はなします

## 場2 background=hoshifuru_heigen_yoru
- actor: papa_dino pose=crouch anim=idle position=left
- actor: you pose=stand anim=idle position=right

narrator: パパきょうりゅうが やってきて、しゃが
narrator: みました。
papa_dino: ぐらぐらは、こわれたんじゃない。
papa_dino: つぎの はが、したから おしてるんだ
you: した？
papa_dino: うえの はが、どいてくれるよ

@effect enter at=0 target=papa_dino
@effect pause at=2 ms=800
@effect shake at=2 target=papa_dino
@voice at=2: ぐらぐらは、こわれたんじゃない。つぎの 歯が、下から おしてるんだ
@voice at=5: そう。もう 生えてきてる。だから 上の 歯が どいてくれる
@effect pause at=5 ms=800

## 場3 background=hoshifuru_heigen_yoru
- actor: you pose=stand anim=idle position=center

narrator: きみは もういちど さわりました。
narrator: さっきと おなじ ぐらぐらなのに、
narrator: こわくなくなっていました。

@effect sparkle at=0
@effect transition at=0 to=reward

# S4-EP2: ほしが ひとつ落ちた

- visit: 2
- season: S4
- audience: 6-7
- mission: ぬけた 歯を、おうちの人と どうするか きめよう
- badge: ほしバッジ
- parent_explanation_ref: S4-EP2

## 場1 background=hoshifuru_heigen_asa
- actor: you pose=crouch anim=idle position=left
- actor: hana pose=stand anim=idle position=right

narrator: その はは、ごはんの とちゅうで
narrator: ぽろりと とれました。
narrator: てのひらの うえに、
narrator: ちいさな しろい かけら。
you: とれた……
narrator: ちが すこし にじんで、すぐ と
narrator: まりました。
narrator: ハナが のぞきこむ
hana: わあ、ちいさい！ ずっと
hana: つかってたんだね
narrator: パパが そらを
narrator: みあげた

@effect enter at=0 target=you
@effect enter at=0 target=hana
@effect shake at=1 target=you
@voice at=1: その はは、ごはんの とちゅうで ぽろりと とれました
@effect surprise at=7 target=hana
@voice at=7: ハナちゃんが のぞきこみます
@effect pause at=11 ms=800
@voice at=11: パパきょうりゅうが、そらを みあげました

## 場2 background=hoshifuru_heigen_asa
- actor: papa_dino pose=stand anim=idle position=left
- actor: you pose=stand anim=idle position=right

papa_dino: やくめを おえたら、ほしに なるよ
narrator: よる、きみは はを にぎって そらを
narrator: みました。ほしが、ひとつ ふえた きが
narrator: しました。

@effect enter at=0 target=papa_dino
@effect pause at=0 ms=800
@voice at=0: 役目を おえた 歯は、ほしに なる。ほしふる平原の ほしは、みんな そうだ

## 場3 background=hoshifuru_heigen_asa
- actor: papa_dino pose=stand anim=idle position=center

papa_dino: でもね
narrator: と パパきょうりゅう。
papa_dino: つぎの はは、ずっと きみと いるよ

@effect pause at=0 ms=800
@effect sparkle at=0
@effect transition at=2 to=reward
@voice at=2: これは 生えかわる 歯だから、ほしに なる。あとから 生えてくる 歯は、ほしに ならない。ずっと きみと いる

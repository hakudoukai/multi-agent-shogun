# S3-EP2: あまい滝

- visit: 2
- season: S3
- audience: 5-6
- mission: あまいものを たべたら、そのあと お水を のんでみよう
- badge: じかんバッジ
- parent_explanation_ref: S3-EP2

## 場1 background=amai_taki
- actor: hana pose=stand anim=idle position=left
- actor: ryuta pose=stand anim=idle position=right

narrator: かわを のぼっていくと、おおきな たきが
narrator: ありました。
ryuta: あまい においが する！
narrator: リュウタが かけよる
narrator: なめると あまい
narrator: でも たきつぼでは
narrator: さかなが うごかない
hana: ここの さかな、ずっと このみずを の
hana: んでるの
narrator: ハナちゃんが しずかに いいました。

@effect enter at=999 target=hana
@effect enter at=0 target=ryuta
@effect shake at=3 target=ryuta
@voice at=3: リュウタくんが かけよります
@effect sparkle at=4 target=ryuta
@voice at=4: たきの みずは、なめると あまい あじが しました
@effect surprise at=6 target=hana
@voice at=6: たきつぼの さかなたちは、なんだか げんきが ありません

## 場2 background=amai_taki
- actor: papa_dino pose=stand anim=idle position=center

narrator: パパきょうりゅうが さかなを みなが
narrator: ら つぶやきます。
papa_dino: ずっと たべると、からだが つかれる

@effect enter at=0 target=papa_dino
@effect pause at=2 ms=800
@voice at=2: あまいものが わるいのでは ない。ずっと つづけて いることが、からだを つかれさせる

## 場3 background=amai_taki
- actor: you pose=stand anim=idle position=center

narrator: きみたちは、さかなを
narrator: きれいな かわかみへ はこんで
narrator: あげました。つぎの ひ、さかなは
narrator: すこし はやく およいでいました。

@effect sparkle at=0
@effect transition at=0 to=reward

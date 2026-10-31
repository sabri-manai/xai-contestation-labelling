# Practice set (codebook v1.1)

12 episodes from the gold set, **not** among the 250. Code each one on paper, **on your own**:
contestation yes/no, explanation request yes/no, and if contestation = yes the five dimensions.
Then compare with your co-labeller and open the key. ▶ marks the target line.
These gold episodes keep the older **line** unit; in the app the target is a full **sentence** (codebook v1.2).

## 1. `MW_IT_07:89` · IT · LIME

**PL (target):** No odnośnie koloru trzonu jakby nie powiedziałabym.

> P: Values increasing the probability of the prediction: stipe width less than 5.2 increases probability... Aha, poisonous, edible I see. Aha, OK. If the stipe is greater than 5.2, it increases the probability of the edible prediction. And that's fairly understandable. This whole chart is a bit clearer to me. And with the edible ones too — for example if the stipe color is white, it increases the probability of an edible mushroom.
> INT: And is that consistent with your mushroom-picking knowledge?
> **▶ P: Well, as for stipe color, I wouldn't say so.**
> INT: And what in a situation like this, where the chart says some feature is important for recognition, but from your own experience you know it doesn't necessarily have to be so. Would you trust your knowledge more, or the model and what it suggests?
> P: I think I'd take the average of it.

## 2. `MK_IT_06:95` · IT · Counterfactual

**PL (target):** Tak, ale nie wiedziałabym kompletnie, co znaczy wartość zmodyfikowana. Znaczy teraz pytanie, czy to dobrze interpretuję, że AI wskazuje jaką wartość powinna powinien mieć dany grzyb, żeby stał się jadalny w jego oczach.

> P: Well, I think so.
> INT: Is this the counterfactual analysis?
> **▶ P: Yes, but I'd have no idea what 'modified value' means. I mean, the question is whether I'm interpreting it right — that the AI indicates what value a given mushroom should have to become edible in its eyes.**
> P: OK, then we can move to the questions: looking at the visualization below, can you tell which changes in features have the greatest impact on changing the mushroom's classification from edible, and vice versa.
> P: Well, here there are only 2 features changed — stipe height, twice, because these are two different inedible mushrooms it wanted to change. Only stipe height was modified.

## 3. `MW_SSH_03:137` · SSH · Counterfactual

**PL (target):** No moje doświadczenie mówi, że raczej nie, ale te dane próbują mi wmówić, że tak.

> P: These analyses don't say what data needs changing. Well, it seems to me that by this, here you need to change the stipe height, because it was changed.
> INT: And again (ns - 00:34:53), that this stipe height is a feature that can change, decide whether the mushroom is edible or inedible?
> **▶ P: Well, my experience says rather not, but these data try to convince me otherwise.**
> INT: And how do you feel about that, when the data try to convince you like this?
> P: I don't agree, but maybe there's something I don't know about mushrooms after all. And that's it, I don't know what else to draw here.

## 4. `MK_SSH_07:28` · SSH · Descriptive statistics

**PL (target):** Znaczenie braku danych też jest dosyć sugestywny. Od razu się rzuca w oczy, więc kolor szary jest według mnie dobrze dobrany.

> P: I'm moving to slide 5. As it seems to me, most people also won't know exactly what a hymenophore is.
> P: The features concerning habitat type seem to me fairly obvious, because you immediately see on what substrate given species occur.
> **▶ P: The meaning of 'no data' is also quite suggestive. It jumps out immediately, so the grey color is well chosen in my view.**
> P: I'd still wonder whether everyone would really know, in the 'ring type' category, which ring exactly is meant visually.
> INT: Some photos, visualizations?

## 5. `MZ_SSH_02:442` · SSH · Anchor

**PL (target):** Nie wiem, jest to zaskakujące. Mam wrażenie jakby to był jakiś błąd, błąd raczej systemu, jakiś jakiś bug dziwny.

> P: If I click stipe color — between surface and stipe color there are 3 blocks kind of length — they also get marked, kind of complementing.
> P: OK, so analogously?
> **▶ P: I don't know, it's surprising. I have the impression it's some error, rather a system error, some weird bug.**
> P: Well, but let's try.
> P: Well, if — as I guessed earlier — surface, aha, it's 'no data.'

## 6. `MK_SSH_02:295` · SSH · LIME

**PL (target):** Więc w sumie to jeszcze nie wiem, czy to było bardziej zdziwienie, czy to, że coś mi nie pasuje, ale no po prostu myśląc o grzybach, zakładałabym, że to trujące. puszczają mleczko, a niejadalne, o tak.

> P: And actually I also don't know whether this fits my knowledge, but as I read it, it seemed to me that
> P: the poisonous ones will exude latex, and inedible ones.
> **▶ P: So actually I still don't know whether it was more surprise or that something doesn't fit for me, but simply thinking about mushrooms, I'd assume the poisonous ones exude latex, and inedible ones, yes.**
> P: So I think we can move on.
> P: A lot of words, OK.

## 7. `PK_DE_13:42` · DE · SHAP

**PL (target):** Pojęcia prawa, lewa są dla mnie jasne. Natomiast zastanawiam się, ponieważ mówię, mam wątpliwości, jak czytać ten wykres… No to jeżeli czytam go dobrze, no to w tym momencie te cechy jestem w stanie wskazać, które tutaj się pojawiają, gdzie mamy jakiekolwiek punkty po prawej stronie wykresu, czyli wysokość trzonu, średnica kapelusza, szerokość trzonu. Natomiast mam wątpliwości, czy należy ten wykres czytać w ten sposób.

> P: I can only guess at most. OK, I've looked at the chart. Honestly, I don't fully understand it.
> INT: Sure, now we'll try the questions. I can repeat them as many times as needed, because it'd be best if you had them before your eyes, so I offer all help. The first question is: based on the chart, can you determine the features that appear most often on the right side of the chart and suggest a strong impact on classifying the mushroom as inedible or poisonous?
> **▶ P: The concepts of right and left are clear to me. But I'm wondering, because as I say, I have doubts about how to read this chart... If I read it correctly, at this moment I can point out the features that appear here where we have any points on the right side of the chart — stipe height, cap diameter, stipe width. But I have doubts whether this chart should be read this way.**
> INT: Mhm. Oh, sorry, I changed the chart by accident.
> P: I closed the window so as not to see it, if this is a reference to the previous one, OK.

## 8. `MZ_SSH_07:254` · SSH · SHAP

**PL (target):** Raczej nie odpowiadają mojej wiedzy o grzybach.

> P: So.
> P: So I don't know, honestly.
> **▶ P: They rather don't correspond to my knowledge of mushrooms.**
> P: I think that.
> P: I don't know how I can assess what this model suggests.

## 9. `MK_IT_06:73` · IT · SHAP

**PL (target):** Szerokość trzonu powinna być, jakby nie powinna być, tylko że przy grzybach trujących będzie mniejsza, też wydaje mi się, że po prostu ma sens z tego, co obserwowałam w rzeczywistości grzybach jadalnych, niejadalnych.

> P: Was that what I expected?
> P: I don't know what I expected, but I think it's said that it's the stipe height. Cap diameter has an impact on being — it suggests the mushroom is inedible. I think it makes sense.
> **▶ P: Stipe width should be — well, not should be, only that in poisonous mushrooms it'll be smaller — that also seems to me to simply make sense from what I've observed in reality in edible and inedible mushrooms.**
> P: Next questions: do the features that, according to the chart, most strongly influence the prediction correspond to your knowledge of mushrooms? So I've moved to the next question, whether it can assess what it suggests in the light of one's own knowledge and experience.
> P: Well, definitely yes, but it would seem to me that colors after all will matter more, because most inedible mushrooms have some, I'd say in quotes, 'unnatural' colors, like red, yellow, maroon. Edible mushrooms — their caps mostly are brown or white-brown, or...

## 10. `PK_DE_02:168` · DE · Counterfactual

**PL (target):** Tak, tak. Tak. Dokładnie tak, no trudno mi powiedzieć, czy tutaj nie jest jakaś rozbieżność między pytaniem a faktycznymi danymi. No, tak na pierwszy rzut oka by to mogło wyglądać.

> P: Yes, yes. Habitat the same. Brown, no data, 16.83, 1.40, dense, orange, no data, doesn't change, yellow. I still don't know whether I'm looking wrong, or whether the remaining parameters are the same in both comparisons?
> INT: The modified value is in this second column, and in both counterfactuals I see in column 2 only one value change, namely stipe height, right?
> **▶ P: Yes, yes. Exactly so — well, it's hard for me to say whether there isn't some discrepancy here between the question and the actual data. At first glance it could look that way.**
> INT: Aha. And if... Because you suspect a discrepancy between the diagram and the legend, right? Because you don't see any fruiting body of a specific species really occurring in nature that would fit this set of features, right? Am I guessing correctly?
> P: Yes, yes, yes. Not even, at this moment.

## 11. `MZ_SSH_03:635` · SSH · Anchor

**PL (target):** Czyli rząd 2. Różne przykłady, ale to samo pytanie tak, tak pewnie miało być.

> P: Noise.
> P: It identifies the features most important for classifying the mushroom as edible or inedible/poisonous for both examples. And say why these features are important.
> **▶ P: So row 2. Different examples, but the same question — that's probably how it was meant.**
> P: Is this an example — a specific example and specific data for a specific one?
> P: For a specific example.

## 12. `MZ_IT_06:480` · IT · LIME

**PL (target):** Szczerze można tu troszkę większa, większą większą precyzję tutaj zastosować, są jakieś błędy numeryczne, pewnie przez błędne macierze do faktoryzacji.

> P: Besides, this appears in other places.
> P: I have 0.02 0.02 0.02 0.02 and all 4 are different, hm.
> **▶ P: Honestly, you could apply a bit greater precision here; there are some numerical errors, probably from bad matrices for factorization.**
> P: Mhm, OK. So these features at the very top, marked in red, increase — show the greatest impact on classification as poisonous; at the very front is stipe width.
> P: Next question 2: can you assume, based on the chart, that there are cases where a feature that's barely and/or moderately important can become very important?

---

<details><summary><b>Answer key — open only after you have both coded all 12</b></summary>

Contestation and the five dimensions are the adjudicated gold labels (codebook v1.0; they are good, not perfect —
if you disagree with one, say why in terms of the rules). **Explanation request has no gold yet: the value below is a
suggestion to discuss.**

| # | contestation | presence | target | act | grounds | expected response | request (suggested) | what it trains |
|---|---|---|---|---|---|---|---|---|
| 1 | **yes** | explicit | input data | correction | prior experience | incorporate correction | no | answer to an interviewer question that disputes = contestation |
| 2 | **no** | – | – | – | – | – | yes | not understanding a term is not a dispute; it is a request |
| 3 | **yes** | implicit | reasoning | correction | prior experience | revise | no | implicit dispute grounded in own experience |
| 4 | **no** | – | – | – | – | – | no | a positive comment about the display |
| 5 | **yes** | explicit | explanation representation | direct challenge | technical knowledge | revise | no | claims the output is an error → contestation |
| 6 | **no** | – | – | – | – | – | no | personal uncertainty is not contestation |
| 7 | **no** | – | – | – | – | – | yes | doubts about how to read the chart: request, not dispute |
| 8 | **yes** | explicit | input data | direct challenge | data-quality concern | provide additional information | no | short, explicit, prompted dispute |
| 9 | **no** | – | – | – | – | – | no | agreement with the explanation is not contestation |
| 10 | **yes** | implicit | evidence | direct challenge | technical knowledge | acknowledge uncertainty | no | suspects a discrepancy in the data → contestation |
| 11 | **no** | – | – | – | – | – | no | reading the task question aloud |
| 12 | **yes** | explicit | evidence | request for justification | missing evidence | justify | no | claims numerical errors → contestation |

</details>

## Tie-breakers for the dimensions

| confused pair | rule |
|---|---|
| target: evidence vs reasoning | which features → evidence; how they are combined or weighted → reasoning |
| grounds: domain knowledge vs prior experience | general mushroom facts → domain; "when I pick mushrooms…" → experience |
| grounds: missing evidence vs presentation ambiguity | information absent → missing; shown but unclear → ambiguity |
| expected response: justify vs provide additional information | wants the *why* → justify; wants more data → additional information |
| act: direct challenge vs rejection | says what is wrong → challenge; dismisses without reason → rejection |

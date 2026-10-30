"""Guide page — taxonomy + 3 labelled examples, EN/PL."""
from __future__ import annotations
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from app.db import get_conn

EXAMPLE_IDS = ["PK_DE_03:64", "DR_IT_05:242", "MZ_SSH_03:543"]


def _context_html(context: str, target: str) -> str:
    lines = [l.strip() for l in context.split("||") if l.strip()]
    parts = []
    for line in lines:
        esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if target.strip() and target.strip() in line:
            parts.append(
                f'<div style="border-left:3px solid #f0ad4e;padding:4px 10px;margin:4px 0;">'
                f'<strong>{esc}</strong></div>'
            )
        else:
            parts.append(
                f'<div style="padding:4px 10px;margin:2px 0;opacity:0.7;">{esc}</div>'
            )
    return "\n".join(parts)


def render():
    st.title("Guide / Przewodnik")

    lang = st.radio("Language / Język", ["English", "Polski"], horizontal=True)
    pl = lang == "Polski"

    # ------------------------------------------------------------------ #
    # Definition
    # ------------------------------------------------------------------ #
    st.subheader("Co to jest kontestacja?" if pl else "What is contestation?")

    if pl:
        st.markdown("""
Uczestnik **kontestuje**, gdy podważa to, co system AI *twierdzi lub robi* —
domagając się uzasadnienia, korekty lub przyznania się do niepewności.

**Nie jest kontestacją:**
- *„Nie rozumiem tej osi."* → niezrozumienie, nie zakwestionowanie (ale **prośba o wyjaśnienie = tak**).
- *„Czcionka jest za mała."* → preferencja estetyczna bez twierdzenia interpretacyjnego (prośba o wyjaśnienie = tak).
- *„Jestem trochę sfrustrowany."* → ogólny afekt.

**Kluczowa granica:** Czy uczestnik twierdzi, że system jest *błędny, wprowadzający w błąd
lub niekompletny*? Tylko to jest kontestacją. Krytyka wykresu jest kontestacją tylko wtedy,
gdy uczestnik mówi, że *uniemożliwia lub zniekształca* poprawne odczytanie wyniku.

**Jednostka:** linia docelowa plus bezpośrednio następujące 1–2 linie *tego samego* uczestnika,
o ile nie ma między nimi wypowiedzi prowadzącego.
""")
        st.subheader("Druga bramka: prośba o wyjaśnienie (explanation request)")
        st.markdown("""
Zaznacz **tak**, gdy uczestnik sygnalizuje, że wyjaśnienie *w tej formie* mu nie służy i pomogłaby
inna forma, poziom, język lub ilość wyjaśnienia: nie może go odczytać, nie zna terminu, brakuje
legendy lub opisu osi, chce prostszego języka albo innego formatu, prosi o dane, które wyjaśnienie
powinno pokazać. Nie musi niczego kwestionować. **Wypełnij dla każdego epizodu, niezależnie od
kontestacji.**

**Test:** *Czy inne wyjaśnienie (inny format, prostszy poziom, dodana legenda, termin, dana)
pomogłoby uczestnikowi w tym miejscu?* Jeśli tak → prośba = tak.

| sytuacja | kontestacja | prośba |
|---|---|---|
| „Nie rozumiem tego objaśnienia, jest napisane językiem matematycznym." | nie | **tak** |
| „Ten słupek nie może być prawdziwy — kształt kapelusza powinien dominować." | **tak** | nie |
| „Słaba czytelność… napisałbym 'żółty kapelusz', dodał slajd z legendą." (mówi, że utrudnia odczyt, proponuje poprawki) | **tak** | **tak** |
| Czyta slajd na głos i mówi „to bardzo mądre, tak, zdecydowanie." | nie | nie |

**Nie jest prośbą:** uwaga o własnej wiedzy bez odniesienia do wyjaśnienia („nie jestem ekspertem");
sam afekt; wypowiedź prowadzącego.
""")
    else:
        st.markdown("""
A participant **contests** when they dispute what the AI system *asserts or does* —
calling for justification, correction, or acknowledgment of uncertainty.

**Not contestation:**
- *"I don't understand this axis."* → incomprehension, not a challenge (but **explanation request = yes**).
- *"The font is too small."* → aesthetic preference with no interpretive claim (explanation request = yes).
- *"I'm a bit frustrated."* → general affect.

**Key boundary:** Does the participant claim the system is *wrong, misleading,
or incomplete*? Only that is contestation. Criticism of the chart is contestation only
when the participant says it *blocks or distorts* the correct reading of the output.

**Unit:** the target line plus the *same* participant's immediately following 1–2 lines,
provided no interviewer turn comes between them.
""")
        st.subheader("Second gate: explanation request")
        st.markdown("""
Mark **yes** when the participant signals that the explanation *as presented* does not work for
them and that a different form, level, language, or amount of explanation would: they cannot read
it, do not know a term, miss a legend or axis label, want plainer language or another format, or
ask for data the explanation should have shown. They need not dispute anything. **Fill it for
every episode, independently of contestation.**

**Test:** *Would a different explanation (another format, a plainer level, an added legend, term,
or datum) have helped this participant here?* If yes → request = yes.

| situation | contestation | request |
|---|---|---|
| "I don't understand this explanation, it's written in mathematical language." | no | **yes** |
| "This bar can't be right — cap shape should dominate here." | **yes** | no |
| "Low readability… I'd write 'yellow cap', add a slide with a legend." (says it hinders reading, proposes fixes) | **yes** | **yes** |
| Reads the slide aloud and says "that's very wise, yes, definitely." | no | no |

**Not a request:** a remark about one's own expertise with no reference to the explanation ("I'm
not an expert"); affect alone; the interviewer's line.
""")

    # ------------------------------------------------------------------ #
    # Dimensions
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("Wymiary (wypełnij tylko gdy tak)" if pl else "Dimensions (fill only when yes)")

    if pl:
        with st.expander("**Presence / Obecność** — jak wyraźna jest kontestacja?"):
            st.markdown("""
| Wartość | Znaczenie |
|---|---|
| **explicit** | Wyzwanie jest sformułowane bezpośrednio i jednoznacznie. *„To nie ma sensu."* |
| **implicit** | Wyzwanie jest wyrażone przez ton, sformułowanie lub implikację, bez wprost. *„Wydaje mi się, że to nie odnosi się do mojej wiedzy…"* |
| **ambiguous** | Nie można stwierdzić, czy to realne zakwestionowanie, czy tylko niezrozumienie. **Wymaga notatki.** |
""")
        with st.expander("**Target / Cel** — co jest kwestionowane?"):
            st.markdown("""
| Wartość | Znaczenie |
|---|---|
| **prediction** | Wynik / klasyfikacja modelu dla tej instancji. |
| **reasoning** | Sposób, w jaki model doszedł do swojego wyniku. |
| **evidence** | Cechy lub dane, które wyjaśnienie wykorzystuje do uzasadnienia wyniku. |
| **input data** | Jakość, kompletność lub poprawność danych wejściowych. |
| **explanation representation** | Sam wykres lub wizualizacja, gdy twierdzenie dotyczy tego, że *uniemożliwia* poprawną interpretację. |
| **system competence** | Ogólna zdolność lub autorytet AI do oceniania w tej dziedzinie. |
""")
        with st.expander("**Interaction act / Akt interakcji** — jaki ruch wykonuje uczestnik?"):
            st.markdown("""
| Wartość | Znaczenie |
|---|---|
| **request for justification** | *„Dlaczego ta cecha ma tu znaczenie?"* |
| **direct challenge** | Bezpośrednie stwierdzenie, że wynik lub rozumowanie jest błędne. |
| **correction** | Podanie właściwej odpowiedzi lub poprawienie błędu. |
| **alternative proposal** | Sugeruje inny model, cechę lub podejście. |
| **counterexample** | Podaje konkretny przypadek, który zaprzecza twierdzeniu systemu. |
| **rejection** | Odrzuca wynik lub wyjaśnienie bez podawania alternatywy. |
| **request to acknowledge uncertainty** | Prosi system o zmniejszenie pewności. |
""")
        with st.expander("**Grounds / Podstawa** — na czym opiera się zakwestionowanie?"):
            st.markdown("""
| Wartość | Znaczenie |
|---|---|
| **domain knowledge** | Wiedza ekspercka o grzybach / biologii. |
| **technical knowledge** | Wiedza o ML, statystyce lub metodach XAI. |
| **prior experience** | Osobiste doświadczenie ze zbieraniem lub rozpoznawaniem grzybów. |
| **internal inconsistency** | Wyjaśnienie sprzecza się samo ze sobą. |
| **missing evidence** | Ważne cechy lub informacje są nieobecne w wyjaśnieniu. |
| **data-quality concern** | Dane są błędne, niekompletne lub niewiarygodne. |
| **causal implausibility** | Związek cecha–wynik nie ma sensu biologicznego. |
| **presentation ambiguity** | Wizualizacja lub sformułowanie jest dwuznaczne w sposób wpływający na interpretację. |
""")
        with st.expander("**Expected response / Oczekiwana odpowiedź** — co rozwiązałoby wyzwanie?"):
            st.markdown("""
| Wartość | Znaczenie |
|---|---|
| **justify** | Wyjaśnij, dlaczego model podjął tę decyzję. |
| **revise** | Zmień lub zaktualizuj model / wynik. |
| **incorporate correction** | Zaakceptuj i uwzględnij korektę uczestnika. |
| **provide additional information** | Dostarcz brakującego kontekstu lub danych. |
| **acknowledge uncertainty** | Przyznaj, że model nie jest tu pewny. |
| **expose conflicting evidence** | Pokaż dowody sprzeczne z twierdzeniem uczestnika. |
| **defer to human expertise** | Ustąp przed autorytetem dziedzinowym uczestnika. |
""")
    else:
        with st.expander("**Presence** — how explicit is the challenge?"):
            st.markdown("""
| Value | Meaning |
|---|---|
| **explicit** | The challenge is stated directly and unambiguously. *"This makes no sense."* |
| **implicit** | The challenge is conveyed through tone, phrasing, or implication without being stated outright. *"It seems to me they don't fully relate to my knowledge…"* |
| **ambiguous** | You cannot tell whether it is a genuine challenge or mere incomprehension / uncertainty. **Requires a note.** |
""")
        with st.expander("**Target** — what is being challenged?"):
            st.markdown("""
| Value | Meaning |
|---|---|
| **prediction** | The model's output / classification for this instance. |
| **reasoning** | How the model arrived at its output. |
| **evidence** | The features or data the explanation uses to justify the output. |
| **input data** | The quality, completeness, or correctness of the underlying data. |
| **explanation representation** | The chart or visual itself, when the claim is that it *prevents* correct interpretation. |
| **system competence** | The AI's general ability or authority to judge in this domain. |
""")
        with st.expander("**Interaction act** — what move is the participant making?"):
            st.markdown("""
| Value | Meaning |
|---|---|
| **request for justification** | *"Why does this feature matter here?"* |
| **direct challenge** | Outright assertion that the output or reasoning is wrong. |
| **correction** | Offers the right answer or fixes an error. |
| **alternative proposal** | Suggests a different model, feature, or approach. |
| **counterexample** | Gives a concrete case that contradicts the system's claim. |
| **rejection** | Dismisses the output or explanation without offering an alternative. |
| **request to acknowledge uncertainty** | Asks the system to be less confident. |
""")
        with st.expander("**Grounds** — what is the challenge based on?"):
            st.markdown("""
| Value | Meaning |
|---|---|
| **domain knowledge** | Expertise about mushrooms / biology. |
| **technical knowledge** | Expertise about ML, statistics, or XAI methods. |
| **prior experience** | Personal experience collecting or identifying mushrooms. |
| **internal inconsistency** | The explanation contradicts itself. |
| **missing evidence** | Important features or information are absent from the explanation. |
| **data-quality concern** | The underlying data is wrong, incomplete, or unreliable. |
| **causal implausibility** | The feature–outcome relationship doesn't make biological sense. |
| **presentation ambiguity** | The visual or wording is ambiguous in a way that affects interpretation. |
""")
        with st.expander("**Expected response** — what would resolve the challenge?"):
            st.markdown("""
| Value | Meaning |
|---|---|
| **justify** | Explain why the model made this decision. |
| **revise** | Change or update the model / output. |
| **incorporate correction** | Accept and act on the participant's correction. |
| **provide additional information** | Supply missing context or data. |
| **acknowledge uncertainty** | Admit the model is not confident here. |
| **expose conflicting evidence** | Show the evidence that conflicts with the participant's claim. |
| **defer to human expertise** | Yield to the participant's domain authority. |
""")

    # ------------------------------------------------------------------ #
    # Three labelled examples
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("Trzy przykłady z etykietami" if pl else "Three labelled examples")

    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM episodes WHERE episode_id IN ({','.join('?'*len(EXAMPLE_IDS))})",
            EXAMPLE_IDS,
        ).fetchall()

    eps = {r["episode_id"]: dict(r) for r in rows}
    if not eps:
        st.warning("Przykłady nie załadowane. Uruchom `python -m app.seed`." if pl else
                   "Examples not loaded. Run `python -m app.seed` first.")
        return

    for ep_id in EXAMPLE_IDS:
        ep = eps.get(ep_id)
        if not ep:
            continue

        verdict = ep.get("is_contestation", "")
        badge = "✅ tak" if (pl and verdict == "yes") else \
                "❌ nie" if (pl and verdict == "no") else \
                "✅ yes" if verdict == "yes" else "❌ no"

        with st.expander(f"{ep_id} — {badge}", expanded=True):
            col_text, col_labels = st.columns([3, 2], gap="large")

            with col_text:
                ctx = ep["context_pl"] if pl else ep["context_en"]
                tgt = ep["text_pl"] if pl else ep["text_en"]
                st.markdown(_context_html(ctx, tgt), unsafe_allow_html=True)
                st.caption(f"{ep['participant_group']} · {ep['explanation_format']}")

            with col_labels:
                st.markdown(f"**is_contestation:** `{ep.get('is_contestation') or '—'}`")
                if verdict == "yes":
                    for dim in ["presence", "target", "interaction_act",
                                "grounds", "expected_response"]:
                        st.markdown(f"**{dim}:** `{ep.get(dim) or '—'}`")

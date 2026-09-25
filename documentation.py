import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="streamlit documentation", layout="wide")

# --- Textformatierung mit Markdown ---
st.header("Textformatierung")
st.markdown("**fett**, *kursiv*, ~~durchgestrichen~~ und `inline code`")
st.markdown(":red[roter Text], :blue[blauer Text], :green-background[grün hinterlegt]")
st.markdown("Emojis per Kurzname: :rocket: :snake: :tada:")
st.markdown("Ein Link: [Streamlit-Doku](https://docs.streamlit.io)")
st.markdown("""
- Aufzählungspunkt eins
- Aufzählungspunkt zwei
    - eingerückter Unterpunkt

1. nummerierte Liste
2. zweiter Eintrag

> Ein Zitat-Block
""")
st.badge("Neu", color="green")           # kleines farbiges Label
st.text("st.text: Festbreitenschrift, ohne Markdown **hier passiert nichts**")

st.code("""
def begruessung(name):
    return f"Hallo {name}!"
""", language="python")                  # mehrzeiliger Code mit Sprachangabe

st.divider()

# --- Statusmeldungen ---
st.header("Statusmeldungen")
st.success("Erfolg: Die Daten wurden geladen.")
st.info("Info: Das ist ein neutraler Hinweis.")
st.warning("Warnung: Der API-Key läuft bald ab.")
st.error("Fehler: Die Datei wurde nicht gefunden.")
st.exception(ValueError("Beispiel-Exception mit Traceback-Optik"))

st.divider()

# --- Daten ausgeben ---
st.header("Daten")
df = pd.DataFrame({
    "Stadt": ["Berlin", "Hamburg", "München", "Köln"],
    "Einwohner (Mio.)": [3.7, 1.9, 1.5, 1.1],
    "Bundesland": ["Berlin", "Hamburg", "Bayern", "NRW"],
})

st.subheader("st.dataframe – interaktiv (sortierbar, scrollbar)")
st.dataframe(df, hide_index=True)

st.subheader("st.table – statische Tabelle")
st.table(df)

st.subheader("st.json – verschachtelte Daten")
st.json({"modell": "gpt-4o-mini", "temperature": 0, "tags": ["demo", "streamlit"]})

st.subheader("st.metric – Kennzahlen mit Veränderung")
col1, col2, col3 = st.columns(3)
col1.metric("Temperatur", "21 °C", "1.2 °C")
col2.metric("Nutzer", "1.024", "-8 %")
col3.metric("Kosten", "3,50 €", "-0,40 €", delta_color="inverse")  # weniger Kosten = grün

st.write("st.write erkennt den Typ selbst – hier ein DataFrame:", df.head(2))

st.divider()

# --- Diagramme ---
st.header("Diagramme")
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.subheader("st.line_chart")
st.line_chart(chart_data)

st.subheader("st.bar_chart")
st.bar_chart(df, x="Stadt", y="Einwohner (Mio.)")

st.subheader("st.area_chart")
st.area_chart(chart_data)

st.divider()

# --- Layout ---
st.header("Layout")

links, rechts = st.columns(2)            # Spalten nebeneinander
links.write("Das steht in der linken Spalte.")
rechts.write("Das steht in der rechten Spalte.")

tab1, tab2 = st.tabs(["Tab 1", "Tab 2"]) # Reiter
tab1.write("Inhalt von Tab 1")
tab2.write("Inhalt von Tab 2")

with st.expander("Zum Aufklappen hier klicken"):
    st.write("Versteckter Inhalt, z. B. Details oder lange Erklärungen.")

with st.container(border=True):          # Kasten mit Rahmen
    st.write("Inhalt in einem umrandeten Container.")

st.sidebar.title("Seitenleiste")         # alles mit st.sidebar landet links
st.sidebar.write("Hier stehen oft Einstellungen und Filter.")

st.divider()

# --- Fortschritt & Effekte ---
st.header("Fortschritt & Effekte")
st.progress(70, text="Fortschrittsbalken bei 70 %")
st.toast("Ein kurzes Pop-up unten rechts")
#st.balloons()                          # Luftballons zur Feier – einkommentieren zum Ausprobieren
#st.snow()                              # Schneeflocken

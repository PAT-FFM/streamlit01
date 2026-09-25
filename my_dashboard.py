import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


st.set_page_config(page_title="meine erste streamlit app", layout="wide")
st.write("Wir bauen unsere erste Streamlit App")

st.title("This is the app title")        # groesste Ueberschrift (Seitentitel)
st.header("This is the header")          # Abschnitts-Ueberschrift
st.markdown("This is the markdown")      # Text mit Markdown-Formatierung (**fett**, *kursiv*, ...)
st.subheader("This is the subheader")    # kleinere Unter-Ueberschrift
st.caption("This is the caption")        # kleiner, grauer Hinweistext
st.code("x = 2021")                      # Code-Block mit Syntax-Hervorhebung
st.latex(r''' a+a r^1+a r^2+a r^3 ''')   # mathematische Formel (LaTeX)


st.checkbox("Ja")
st.button("click me")
st.radio("Wähle das Geschlecht", ["männlich", "weiblich", "divers"])


# --- Sidebar ---
# Alles im with-Block landet in der Seitenleiste links (unter dem Seitenmenü).
# Die Rückgabewerte der Widgets speichern wir in Variablen und nutzen sie unten im Hauptbereich.
with st.sidebar:
    st.header("Einstellungen")
    name = st.text_input("Dein Name", value="Gast")
    stadt = st.selectbox("Stadt", ["Berlin", "Hamburg", "München", "Köln"])
    anzahl = st.slider("Anzahl Datenpunkte", min_value=10, max_value=100, value=30)
    zeige_tabelle = st.toggle("Rohdaten anzeigen")
    st.divider()
    st.caption("Tipp: Jede Änderung hier lässt das Skript neu durchlaufen.")

# Alternative ohne with-Block:
# st.sidebar.header("Einstellungen")
# name = st.sidebar.text_input("Dein Name", value="Gast")

# --- Hauptbereich reagiert auf die Sidebar ---
st.divider()
st.header(f"Hallo {name}!")
st.write(f"Ausgewählte Stadt: **{stadt}**")

daten = pd.DataFrame({"Messwert": np.random.randn(anzahl).cumsum()})
st.line_chart(daten)

if zeige_tabelle:
    st.dataframe(daten)


# --- Altair: Diagramme mit voller Kontrolle ---
# st.line_chart & Co. sind schnell, aber kaum anpassbar. Mit Altair legst du
# selbst fest, welche Spalte auf welche Achse kommt, Farben, Tooltips usw.
st.divider()
st.header("Altair-Diagramm")

staedte = pd.DataFrame({
    "Stadt": ["Berlin", "Hamburg", "München", "Köln"],
    "Einwohner": [3.7, 1.9, 1.5, 1.1],             # in Mio. – Spaltennamen ohne Punkt/Klammern (s. u.)
    "lat": [52.52, 53.55, 48.14, 50.94],
    "lon": [13.40, 9.99, 11.58, 6.96],
})
staedte["auswahl"] = staedte["Stadt"] == stadt   # True für die Stadt aus der Sidebar

balken = (
    alt.Chart(staedte)
    .mark_bar()                                       # Diagrammtyp: Balken
    .encode(
        x=alt.X("Stadt:N", sort="-y", title=None),    # :N = nominal (Kategorien)
        # Achtung: Ein Punkt im Feldnamen ("Einwohner (Mio.)") bedeutet für Altair "verschachteltes Feld"
        # → Balken bleiben leer. Deshalb schlichter Spaltenname + Beschriftung über title.
        y=alt.Y("Einwohner:Q", title="Einwohner (Mio.)"),  # :Q = quantitativ (Zahlen)
        color=alt.condition(                          # ausgewählte Stadt farbig hervorheben
            alt.datum.auswahl, alt.value("orange"), alt.value("lightgray")
        ),
        tooltip=["Stadt", alt.Tooltip("Einwohner:Q", title="Einwohner (Mio.)")],        # Infos beim Drüberfahren mit der Maus
    )
    .properties(height=300)
)
st.altair_chart(balken, width="stretch")          # volle Breite

# --- st.map: Punkte auf einer Karte ---
# Erwartet einen DataFrame mit Spalten "lat"/"latitude" und "lon"/"longitude".
st.divider()
st.header("Karte")

st.subheader("Alle Städte")
staedte["radius_m"] = staedte["Einwohner"] * 15_000   # Punktradius wird in Metern angegeben
st.map(staedte, size="radius_m", color="#ff8c00")

st.subheader(f"Zufällige Punkte rund um {stadt}")
mitte = staedte[staedte["Stadt"] == stadt].iloc[0]
punkte = pd.DataFrame({
    # randn(anzahl) = Array mit `anzahl` Zufallszahlen (Mittel 0, Std.-Abw. 1, auch negativ)
    # * 0.02 Grad ≈ 2 km Standardabweichung → ca. 2/3 der Punkte liegen innerhalb ±2 km
    "lat": mitte["lat"] + np.random.randn(anzahl) * 0.02,
    "lon": mitte["lon"] + np.random.randn(anzahl) * 0.03,   # 0.03° Länge ≈ 2 km (Längengrade sind in DE schmaler)
})
st.map(punkte, zoom=11)

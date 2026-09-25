import hmac
import os

import pandas as pd
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter
from pydantic import BaseModel, Field

# Lokal: API-Keys aus der .env laden (sucht vom Startordner aus nach oben).
# In der Streamlit Cloud gibt es keine .env – dort werden die Secrets
# (Settings → Secrets) automatisch als Umgebungsvariablen gesetzt.
load_dotenv(find_dotenv(usecwd=True))

st.title("Structured Output")
st.caption("Das LLM antwortet nicht mit Fließtext, sondern mit JSON nach einem festen Schema.")

# --- Passwort-Sperre ---
# Die App ist öffentlich, jeder Aufruf kostet OpenRouter-Guthaben.
# Deshalb erst nach Eingabe des Passworts (APP_PASSWORD) weiter.
app_password = os.getenv("APP_PASSWORD")
if not app_password:
    st.error("Kein APP_PASSWORD konfiguriert – die Seite bleibt gesperrt.")
    st.stop()

if not st.session_state.get("eingeloggt", False):
    eingabe = st.text_input("Passwort", type="password")
    if eingabe and hmac.compare_digest(eingabe, app_password):   # Vergleich ohne Zeit-Leck
        st.session_state["eingeloggt"] = True
        st.rerun()
    elif eingabe:
        st.error("Falsches Passwort.")
    st.stop()                                                    # Rest der Seite nicht ausführen


# --- Ausgabeformate (aus chat_structured_output.py / chat_adressdata_generation.py) ---
class MyMovieOutput(BaseModel):
    title: str
    director: list[str] = Field(description="der Name des Regisseurs des Films", examples=["Cameron, James", "Spielberg, Steven"])
    actors: list[str] = Field(description="die Namen der Schauspieler des Films", examples=["DiCaprio, Leonardo", "Johansson, Scarlett"])
    genre: str = Field(description="das Genre des Films", examples=["Action", "Komödie", "Drama"])
    release_year: int = Field(description="das Erscheinungsjahr des Films", examples=[1997, 2001, 2010])
    box_office: float = Field(description="die weltweiten Einnahmen des Films an den Kinokassen in Millionen USD", examples=[100.5, 250.0, 75.3])

class MyMoviesOutput(BaseModel):
    entries: list[MyMovieOutput]

class DummyAddressDataEntry(BaseModel):
    first_name: str
    last_name: str
    street: str
    zipcode: str
    city: str

class DummyAddressData(BaseModel):
    entries: list[DummyAddressDataEntry]


# --- Aufgaben: Schema, System-Prompt und Eingabefeld je Modus ---
AUFGABEN = {
    "Filme": {
        "schema": MyMoviesOutput,
        "system": """
            Du bist ein Filmexperte und lieferst strukturierte Informationen zu den Top5 Filmen.
            Halte dich dabei exakt an die Formatanweisungen {format_instructions}.
            Der Nutzer beschreibt dir die Handlung der Filme, auf dessen Basis du die relevantesten Filme zurückgibst.
            Gehe dabei von den kommerziell erfolgreichsten Filmen aus.
        """,
        "user": "Handlung: {eingabe}",
        "label": "Handlung",
        "beispiel": "der Protagonist weicht Kugeln aus",
    },
    "Testadressen": {
        "schema": DummyAddressData,
        "system": """
            Du generierst genau {anzahl} Testdaten für eine Adressverwaltung.
            Halte dich dabei exakt an die Formatanweisungen {format_instructions}.
            Der Nutzer gibt dir ein Land vor und du erzeugst sinnvolle Daten hierfür.
            zipcode passend zu city und street.
        """,
        "user": "Land: {eingabe}",
        "label": "Land",        
        "beispiel": "Deutschland",
    },
}

# --- Sidebar: Modellwahl ---
with st.sidebar:
    st.header("Modell")
    model_name = st.selectbox("OpenRouter-Modell", ["google/gemini-3.8-flash", "deepseek/deepseek-v4.1-flash"])
    st.caption("Bewusst nur günstige Modelle – jeder Aufruf kostet Guthaben.")

# --- Eingabe ---
modus = st.segmented_control("Was soll generiert werden?", list(AUFGABEN), default="Filme")
if modus is None:                                                # Auswahl wurde abgewählt
    st.stop()
aufgabe = AUFGABEN[modus]

# st.form: Eingaben lösen erst beim Klick auf den Button einen Rerun aus –
# so entsteht nicht bei jedem Tastendruck ein (kostenpflichtiger) API-Aufruf.
with st.form("eingabe_form"):
    eingabe = st.text_input(aufgabe["label"], value=aufgabe["beispiel"])
    anzahl = None
    if modus == "Testadressen":                                  # nur hier ist die Anzahl wählbar
        anzahl = st.number_input("Anzahl Adressen", min_value=1, max_value=20, value=5, step=1)
    abgeschickt = st.form_submit_button("Generieren", type="primary")

# --- Chain bauen und aufrufen: prompt | model | parser ---
if abgeschickt:
    parser = JsonOutputParser(pydantic_object=aufgabe["schema"])
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", aufgabe["system"]),
        ("user", aufgabe["user"]),
    ]).partial(format_instructions=parser.get_format_instructions())
    model = ChatOpenRouter(model=model_name, temperature=0)     # Structured Output → temperature=0
    chain = prompt_template | model | parser

    with st.spinner(f"{model_name} denkt nach …"):
        try:
            # {anzahl} wird im Filme-Prompt nicht verwendet – überzählige Variablen ignoriert das Template
            daten = chain.invoke({"eingabe": eingabe, "anzahl": anzahl})
            st.session_state["ergebnis"] = {"modus": modus, "daten": daten, "anzahl": anzahl}
        except Exception as e:
            st.session_state.pop("ergebnis", None)
            st.error(f"Fehler beim Aufruf: {e}")

# --- Ausgabe: Ergebnis bleibt in session_state, auch wenn die Seite neu läuft ---
ergebnis = st.session_state.get("ergebnis")
if ergebnis and ergebnis["modus"] == modus:
    eintraege = ergebnis["daten"].get("entries", [])
    st.subheader(f"{len(eintraege)} Einträge")
    # LLMs verzählen sich gern – deshalb die gelieferte Anzahl prüfen
    if ergebnis["anzahl"] and len(eintraege) != ergebnis["anzahl"]:
        st.warning(f"Angefordert waren {ergebnis['anzahl']}, das Modell hat {len(eintraege)} geliefert.")
    st.dataframe(pd.DataFrame(eintraege), hide_index=True)
    with st.expander("Rohantwort (JSON)"):
        st.json(ergebnis["daten"])

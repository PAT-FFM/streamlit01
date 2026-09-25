import streamlit as st

# Einstiegspunkt der Multipage-App: hier wird nur festgelegt, welche Seiten es gibt.
# Starten mit:  uv run streamlit run streamlit/app.py

st.set_page_config(page_title="meine erste streamlit app", layout="wide")

# Jede Seite ist ein eigenes Skript – Pfad relativ zu dieser Datei
dashboard = st.Page("my_dashboard.py", title="Dashboard", icon="📊", default=True)

# Weitere Seiten einfach anlegen und in die Liste aufnehmen, z. B.:
documentation = st.Page("documentation.py", title="Documentation", icon="📁")

pg = st.navigation([dashboard,documentation])          # bei nur einer Seite blendet Streamlit das Menü aus
pg.run()                                 # führt die gerade ausgewählte Seite aus

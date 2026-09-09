# PPWR-Rollenprüfung – Streamlit App

Interaktive Ermittlung der PPWR-Rolle (Lieferant, Erzeuger, Hersteller, Importeur/Vertreiber als Erzeuger).
Quelle: IK-Mitteilung „Mitteilung zu den wichtigsten Rollen in der PPWR“ vom 13. März 2026.

## Lokal starten
```
streamlit run app.py
```
(Standard-Port 8501; bei Bedarf `--server.port 8520`)

## Veröffentlichung
- GitHub: https://github.com/IK-Coding2025/ppwr-rollenpruefung (Branch `main`)
- Streamlit Cloud: Auto-Deploy bei jedem Push auf `main`
- Öffentliche URL: https://ppwr-rollenpruefung.streamlit.app

## Design-Tokens
- IK-Blau: `#004996` (Titel, Pills, Akzente, Worthervorhebungen `.hl`)
- Ausgewählte Auswahl-Pille: blau mit weißer Schrift
- Ergebniskarten: Hintergrund `#E8F2FC`
- Schrift: Arial

## Dateien
- `app.py` – komplette App (Entscheidungsbäume in `TREES`)
- `logo.jpg` – IK-Logo (wird base64-eingebettet zentriert, 200 px)
- `.streamlit/config.toml` – Theme (primaryColor #004996)
- `requirements.txt` – `streamlit>=1.40,<2`

## Hinweise
- Frage-/Ergebnistexte sind Originalwortlaut aus den Entscheidungsbäumen der IK-Mitteilung – nicht frei umformulieren.
- Excel-Pendant: `..\Output\PPWR_Rollen_Logik.xlsx` (Generator: `C:\Users\l.mueller\create_ppwr_excel.py`)
- Statisches HTML-Pendant: `..\Output\PPWR-Rollen-Dashboard.html` (Generator: `C:\Users\l.mueller\create_ppwr_dashboard.py`)
- Achtung FileCloud-Sync: Der Dateiname `PPWR_Rollen_Dashboard.html` (mit Unterstrich) erzeugt Sync-Konflikte – daher HTML-Variante mit Bindestrich benennen.

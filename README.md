# 📱 ScreenTime Duo – Setup

## Schnellstart

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. App starten
streamlit run app.py
```

## CSV-Format

Jede Woche lädt jede Person **eine CSV-Datei** hoch. Das Format:

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `week` | Text | z.B. `2025-W03` |
| `date` | Text | z.B. `2025-01-20` |
| `total_screen_time_min` | Zahl | Gesamte Bildschirmzeit des Tages in Minuten |
| `app_name` | Text | App-Name (oder pseudonymisiert: App1, App2 …) |
| `app_time_min` | Zahl | Zeit für diese App an diesem Tag in Minuten |

**Wichtig:** Pro Tag und App eine Zeile → 3 Tage × 5 Apps = **15 Zeilen pro Woche**.

### Beispiel
```
week,date,total_screen_time_min,app_name,app_time_min
2025-W01,2025-01-06,320,Instagram,85
2025-W01,2025-01-06,320,YouTube,60
2025-W01,2025-01-06,320,WhatsApp,45
2025-W01,2025-01-06,320,TikTok,70
2025-W01,2025-01-06,320,Chrome,30
2025-W01,2025-01-07,280,Instagram,70
...
```

## Features / USP

| Feature | Beschreibung |
|---------|-------------|
| **Head-to-Head Radar** | Gemeinsame Apps direkt vergleichen |
| **Differenzdiagramm** | Wer hat in welcher Woche mehr Zeit verbraucht? |
| **Korrelationsanalyse** | Verhält sich die Bildschirmzeit beider Personen ähnlich? |
| **Wöchentlicher Schieberegler** | Zeitraum frei wählen |
| **Boxplot** | Streuung der Bildschirmzeit pro Woche |
| **Heatmap** | Muster über alle Tage auf einen Blick |
| **Pseudonymisierung** | App-Namen per Toggle anonymisieren |
| **Demo-Modus** | Ohne CSV sofort nutzbar |
| **CSV-Export** | Kombinierten Datensatz herunterladen |

## Projektstruktur

```
screentime_app/
├── app.py            ← Hauptanwendung
├── requirements.txt  ← Python-Abhängigkeiten
└── README.md         ← Diese Datei
```

import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = 'API-KEY'
URL = 'https://api.eflow.team/v1/networks/reporting/entity'
HEADERS = {
    'X-Eflow-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# Fonction pour demander une date avec vérification
def demander_date(message):
    while True:
        date_input = input(message).strip()
        if not date_input:
            return None
        try:
            return datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("Format invalide. Utilisez YYYY-MM-DD (ex : 2025-03-15).")

# Demande des dates à l'utilisateur
start_date = demander_date("Entrez  la date de début (YYYY-MM-DD) : ")
end_date = demander_date("Entrez la date de fin (YYYY-MM-DD) (laisser vide pour une seule journée) : ")

# Si end_date non fourni, on le prend égal à start_date
if not end_date:
    end_date = start_date

all_rows = []
current_date = start_date

while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")

    payload = {
        "timezone_id": 80,
        "currency_id": "USD",
        "from": date_str,
        "to": date_str,
        "columns": [
            {"column": "affiliate"},
            {"column": "offer"},
            {"column": "advertiser"}
        ],
        "usm_columns": [],
        "query": {
            "filters": [],
            "exclusions": [],
            "metric_filters": [],
            "user_metrics": [],
            "settings": {}
        }
    }

    response = requests.post(URL, headers=HEADERS, json=payload)
    data = response.json()

    for item in data.get("table", []):
        row_data = {
            "date": date_str,
            "affiliate_id": None,
            "affiliate_name": None,
            "offer_id": None,
            "offer_name": None,
            "advertiser_id": None,
            "advertiser_name": None,
        }

        for col in item.get("columns", []):
            if col["column_type"] == "affiliate":
                row_data["affiliate_id"] = col.get("id")
                row_data["affiliate_name"] = col.get("label")
            elif col["column_type"] == "offer":
                row_data["offer_id"] = col.get("id")
                row_data["offer_name"] = col.get("label")
            elif col["column_type"] == "advertiser":
                row_data["advertiser_id"] = col.get("id")
                row_data["advertiser_name"] = col.get("label")

        row_data.update(item.get("reporting", {}))
        all_rows.append(row_data)

    print(f"Données récupérées pour le {date_str}")
    current_date += timedelta(days=1)

# Export final
df = pd.DataFrame(all_rows)

# Convertir les floats .0 en entiers si applicable
for col in df.select_dtypes(include=["float"]):
    if all(df[col].dropna() == df[col].dropna().astype(int)):
        df[col] = df[col].astype("Int64")

df.to_csv("affiliate_offer_daily_report.csv", index=False)
print("Fichier CSV généré : affiliate_offer_daily_report.csv")

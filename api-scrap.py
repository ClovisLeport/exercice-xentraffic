import requests
import json
import matplotlib.pyplot as plt

API_KEY = 'PwnctAWJSj2c3Ul0xGnhZA'
URL = 'https://api.eflow.team/v1/networks/reporting/entity/table'

headers = {
    'X-Eflow-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# Dates de debut et de fin de l'echantillon 
startDate = "2024-10-04"
endDate = "2025-05-13"

# Nombre d'élements qui seront affichés dans les graphiques
numberOfelement = 10

# Paramètres de la requete
def get_profits_by(group_by: str, startDate: str, endDate: str):
    payload = {
        "from": startDate,
        "to": endDate,
        "timezone_id": 67,
        "currency_id": "USD",
        "columns": [
            {"column": group_by}
        ],
        "metrics": [
            {"metric": "profit"}
        ],
        "query": {
            "filters": [],
            "exclusions": [],
            "metric_filters": [],
            "user_metrics": [],
            "settings": {
                "include_summary": True,
                "include_report": True
            }
        }
    }

    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    
    profit_table = []
    for row in data.get("table", []):
        label = row["columns"][0]["label"]
        profit = row["reporting"].get("profit", 0)
        
        profit_table.append((label, profit))

    sorted_profits = sorted(profit_table, key=lambda x: x[1], reverse=True)
    return sorted_profits

def plot_barh_profits(profit_data, title):
    labels = [item[0] for item in profit_data[:numberOfelement]]
    profits = [item[1] for item in profit_data[:numberOfelement]]

    plt.figure(figsize=(12, 6))
    bars = plt.barh(labels, profits, color='skyblue')
    plt.xlabel("Profit (USD)")
    plt.title(f"Top {numberOfelement} {title} by Profit between {startDate} and {endDate}")
    plt.gca().invert_yaxis()

    max_profit = max(profits)
    plt.xlim(0, max_profit * 1.15)

    for bar in bars:
        width = bar.get_width()
        plt.text(width + max_profit * 0.01, bar.get_y() + bar.get_height() / 2,
                 f"{width:.2f}$", va='center')

    plt.tight_layout()
    plt.show()

def plot_pie_profits(profit_data, title):
    labels = [item[0] for item in profit_data[:10]]
    profits = [item[1] for item in profit_data[:10]]
    total = sum(profits)

    
    legend_labels = [
        f"{label}: {profit:.2f}$ ({(profit / total) * 100:.1f}%)"
        for label, profit in zip(labels, profits)
    ]

    plt.figure(figsize=(10, 10))
    wedges, texts = plt.pie(
        profits,
        labels=None, 
        startangle=140
    )

    plt.legend(wedges, legend_labels, title=title, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
    plt.title(f"Top {numberOfelement} {title} between {startDate} and {endDate}")
    plt.tight_layout()
    plt.show()

profits_by_advertiser = get_profits_by("advertiser", startDate, endDate)
profits_by_offer = get_profits_by("offer", startDate, endDate)
profits_by_affiliate = get_profits_by("affiliate", startDate, endDate)

plot_barh_profits(profits_by_advertiser, "Advertisers")
plot_barh_profits(profits_by_offer, "Offers")
plot_pie_profits(profits_by_affiliate, "Affiliates")

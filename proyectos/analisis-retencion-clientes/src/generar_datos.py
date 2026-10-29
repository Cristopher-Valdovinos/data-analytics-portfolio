"""Genera un conjunto de datos sintéticos reproducible para el proyecto."""
from pathlib import Path
import csv
import random

SEED = 20261028
N_CLIENTES = 1200
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "clientes.csv"


def main():
    rng = random.Random(SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    planes = ["Basico", "Estandar", "Premium"]
    pesos_plan = [0.45, 0.38, 0.17]
    rows = []

    for customer_id in range(1, N_CLIENTES + 1):
        plan = rng.choices(planes, weights=pesos_plan, k=1)[0]
        tenure = rng.randint(1, 60)
        monthly_fee = {"Basico": 12990, "Estandar": 21990, "Premium": 34990}[plan]
        monthly_fee += rng.choice([-1000, 0, 0, 0, 1000])
        support_tickets = min(rng.randint(0, 5) + (1 if tenure < 4 else 0), 8)
        payment_delay = rng.choices([0, 1, 2, 3, 4, 5], weights=[0.62, 0.16, 0.10, 0.06, 0.04, 0.02], k=1)[0]
        days_since_last_purchase = max(0, int(rng.gauss(18 + tenure * 0.15, 13)))

        # Regla probabilística sintética: solo crea una etiqueta de práctica.
        score = (
            -2.35
            + (0.75 if tenure <= 6 else 0)
            + support_tickets * 0.22
            + payment_delay * 0.28
            + (0.65 if days_since_last_purchase > 45 else 0)
            + (0.20 if plan == "Basico" else 0)
        )
        probability = 1 / (1 + (2.718281828 ** (-score)))
        churned = int(rng.random() < probability)

        rows.append({
            "customer_id": customer_id,
            "plan": plan,
            "tenure_months": tenure,
            "monthly_fee_clp": monthly_fee,
            "support_tickets_90d": support_tickets,
            "payment_delay_count_90d": payment_delay,
            "days_since_last_purchase": days_since_last_purchase,
            "churned": churned,
        })

    fields = list(rows[0].keys())
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Dataset creado: {OUTPUT}")
    print(f"Registros: {len(rows)} | Semilla: {SEED}")


if __name__ == "__main__":
    main()

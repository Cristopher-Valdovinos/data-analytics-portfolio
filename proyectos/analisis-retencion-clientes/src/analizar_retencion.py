"""Valida y analiza el dataset sintético de retención de clientes."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "clientes.csv"
OUTPUT_DIR = ROOT / "outputs"
EXPECTED_COLUMNS = {
    "customer_id", "plan", "tenure_months", "monthly_fee_clp",
    "support_tickets_90d", "payment_delay_count_90d",
    "days_since_last_purchase", "churned",
}


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError("No existe data/clientes.csv. Ejecuta primero: python src/generar_datos.py")

    df = pd.read_csv(DATA_FILE)
    missing_columns = EXPECTED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing_columns)}")
    if df["customer_id"].duplicated().any():
        raise ValueError("customer_id debe ser único.")
    if df[list(EXPECTED_COLUMNS)].isna().any().any():
        raise ValueError("Se detectaron valores nulos.")
    if not df["churned"].isin([0, 1]).all():
        raise ValueError("churned solo puede tomar valores 0 o 1.")
    if (df[["tenure_months", "monthly_fee_clp"]] < 0).any().any():
        raise ValueError("Antigüedad y cargo mensual no pueden ser negativos.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR = OUTPUT_DIR / "graficos"
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    total = len(df)
    churned = int(df["churned"].sum())
    churn_rate = churned / total if total else 0
    revenue_at_risk = int(df.loc[df["churned"].eq(1), "monthly_fee_clp"].sum())

    kpis = pd.DataFrame([{
        "clientes": total,
        "clientes_churn": churned,
        "tasa_churn_pct": round(churn_rate * 100, 2),
        "ingreso_mensual_asociado_churn_clp": revenue_at_risk,
        "cargo_mensual_promedio_clp": round(df["monthly_fee_clp"].mean(), 0),
    }])
    by_plan = (
        df.groupby("plan", as_index=False)
        .agg(clientes=("customer_id", "count"),
             clientes_churn=("churned", "sum"),
             ingreso_mensual_clp=("monthly_fee_clp", "sum"))
    )
    by_plan["tasa_churn_pct"] = (by_plan["clientes_churn"] / by_plan["clientes"] * 100).round(2)
    by_plan["ingreso_mensual_asociado_churn_clp"] = (
        df.assign(revenue_at_risk=df["monthly_fee_clp"] * df["churned"])
        .groupby("plan")["revenue_at_risk"].sum().reindex(by_plan["plan"]).to_numpy()
    )

    df["tenure_bucket"] = pd.cut(
        df["tenure_months"], bins=[0, 3, 6, 12, 24, 60],
        labels=["1-3 meses", "4-6 meses", "7-12 meses", "13-24 meses", "25-60 meses"],
        include_lowest=True,
    )
    by_tenure = (
        df.groupby("tenure_bucket", observed=False, as_index=False)
        .agg(clientes=("customer_id", "count"), clientes_churn=("churned", "sum"))
    )
    by_tenure["tasa_churn_pct"] = (
        by_tenure["clientes_churn"] / by_tenure["clientes"].where(by_tenure["clientes"] != 0) * 100
    ).round(2)

    # Segmentación adicional para revisar la asociación entre retrasos de pago y churn.
    df["payment_delay_bucket"] = pd.cut(
        df["payment_delay_count_90d"],
        bins=[-1, 0, 1, 99],
        labels=["0 retrasos", "1 retraso", "2+ retrasos"],
    )
    by_payment_delay = (
        df.groupby("payment_delay_bucket", observed=False, as_index=False)
        .agg(clientes=("customer_id", "count"), clientes_churn=("churned", "sum"))
    )
    by_payment_delay["tasa_churn_pct"] = (
        by_payment_delay["clientes_churn"]
        / by_payment_delay["clientes"].where(by_payment_delay["clientes"] != 0) * 100
    ).round(2)

    # Regla de priorización explicable; no es un modelo de machine learning.
    df["priority_score"] = (
        (df["support_tickets_90d"] >= 3).astype(int)
        + (df["payment_delay_count_90d"] >= 2).astype(int)
        + (df["days_since_last_purchase"] > 45).astype(int)
        + (df["tenure_months"] <= 6).astype(int)
    )
    df["priority_segment"] = pd.cut(
        df["priority_score"], bins=[-1, 1, 2, 4],
        labels=["Bajo", "Medio", "Alto"],
    )
    prioritized = df.sort_values(
        ["priority_score", "monthly_fee_clp"], ascending=[False, False]
    ).head(100)

    kpis.to_csv(OUTPUT_DIR / "kpis_generales.csv", index=False)
    by_plan.to_csv(OUTPUT_DIR / "churn_por_plan.csv", index=False)
    by_tenure.to_csv(OUTPUT_DIR / "churn_por_antiguedad.csv", index=False)
    by_payment_delay.to_csv(OUTPUT_DIR / "churn_por_retrasos_pago.csv", index=False)
    prioritized.to_csv(OUTPUT_DIR / "clientes_priorizados.csv", index=False)

    # Gráficos reproducibles para el README o una presentación de portafolio.
    fig, ax = plt.subplots(figsize=(8, 5))
    plan_plot = by_plan.sort_values("tasa_churn_pct", ascending=False)
    bars = ax.bar(plan_plot["plan"], plan_plot["tasa_churn_pct"])
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_title("Tasa de churn por plan")
    ax.set_xlabel("Plan")
    ax.set_ylabel("Tasa de churn (%)")
    ax.set_ylim(0, max(plan_plot["tasa_churn_pct"].max() * 1.18, 5))
    fig.tight_layout()
    fig.savefig(CHART_DIR / "churn_por_plan.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    tenure_plot = by_tenure.dropna(subset=["tasa_churn_pct"])
    bars = ax.bar(tenure_plot["tenure_bucket"].astype(str), tenure_plot["tasa_churn_pct"])
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_title("Tasa de churn por antigüedad")
    ax.set_xlabel("Antigüedad del cliente")
    ax.set_ylabel("Tasa de churn (%)")
    ax.tick_params(axis="x", rotation=20)
    ax.set_ylim(0, max(tenure_plot["tasa_churn_pct"].max() * 1.18, 5))
    fig.tight_layout()
    fig.savefig(CHART_DIR / "churn_por_antiguedad.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    delay_plot = by_payment_delay.dropna(subset=["tasa_churn_pct"])
    bars = ax.bar(delay_plot["payment_delay_bucket"].astype(str), delay_plot["tasa_churn_pct"])
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_title("Tasa de churn por retrasos de pago")
    ax.set_xlabel("Retrasos de pago en los últimos 90 días")
    ax.set_ylabel("Tasa de churn (%)")
    ax.set_ylim(0, max(delay_plot["tasa_churn_pct"].max() * 1.18, 5))
    fig.tight_layout()
    fig.savefig(CHART_DIR / "churn_por_retrasos_pago.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print("\n=== KPIs generales ===")
    print(kpis.to_string(index=False))
    print("\n=== Churn por plan ===")
    print(by_plan.to_string(index=False))
    print("\n=== Churn por antigüedad ===")
    print(by_tenure.to_string(index=False))
    print("\n=== Churn por retrasos de pago ===")
    print(by_payment_delay.to_string(index=False))
    print(f"\nResultados guardados en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

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
    prioritized = df.loc[df["priority_score"] > 0].sort_values(
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

    # Dashboard HTML local, sin servidor ni dependencias externas.
    kpi = kpis.iloc[0]
    dashboard_html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard | Retención de clientes</title>
<style>
:root {{ color-scheme: light; --ink: #172033; --muted: #5d687b; --line: #dce2ea; --paper: #f5f7fb; --card: #fff; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--paper); color: var(--ink); font: 16px/1.5 system-ui, -apple-system, Segoe UI, sans-serif; }}
main {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 48px; }}
header {{ margin-bottom: 24px; }}
h1 {{ margin: 0 0 8px; font-size: clamp(1.7rem, 4vw, 2.5rem); }}
h2 {{ font-size: 1.15rem; margin: 0 0 14px; }}
p {{ color: var(--muted); }}
.notice {{ padding: 12px 16px; border: 1px solid var(--line); background: #fff; border-radius: 12px; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin: 22px 0; }}
.card, section {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px; }}
.kpi-label {{ color: var(--muted); font-size: .9rem; }}
.kpi-value {{ font-size: clamp(1.5rem, 3vw, 2rem); font-weight: 700; letter-spacing: -.03em; }}
.charts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 16px; }}
img {{ display: block; width: 100%; height: auto; }}
.table-wrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: .92rem; }}
th, td {{ text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--line); }}
th {{ background: #f0f3f8; }}
section {{ margin-top: 16px; }}
footer {{ margin-top: 24px; font-size: .85rem; color: var(--muted); }}
</style>
</head>
<body><main>
<header><h1>Retención y riesgo de fuga de clientes</h1>
<p>Resumen descriptivo del escenario sintético de suscripción.</p></header>
<div class="notice"><strong>Nota metodológica:</strong> datos simulados; no representan clientes reales. La asociación no implica causalidad y los importes expuestos no son pérdidas futuras confirmadas.</div>
<div class="kpis">
<div class="card"><div class="kpi-label">Clientes analizados</div><div class="kpi-value">{int(kpi['clientes']):,}</div></div>
<div class="card"><div class="kpi-label">Clientes con churn</div><div class="kpi-value">{int(kpi['clientes_churn']):,}</div></div>
<div class="card"><div class="kpi-label">Tasa de churn</div><div class="kpi-value">{float(kpi['tasa_churn_pct']):.2f}%</div></div>
<div class="card"><div class="kpi-label">Cargo mensual asociado al churn</div><div class="kpi-value">${int(kpi['ingreso_mensual_asociado_churn_clp']):,} CLP</div></div>
</div>
<div class="charts">
<section><h2>Churn por plan</h2><img src="graficos/churn_por_plan.png" alt="Tasa de churn por plan"></section>
<section><h2>Churn por antigüedad</h2><img src="graficos/churn_por_antiguedad.png" alt="Tasa de churn por antigüedad"></section>
<section><h2>Churn por retrasos de pago</h2><img src="graficos/churn_por_retrasos_pago.png" alt="Tasa de churn por retrasos de pago"></section>
</div>
<section><h2>Resumen por plan</h2><div class="table-wrap">{by_plan.to_html(index=False, border=0, escape=True)}</div></section>
<section><h2>Resumen por antigüedad</h2><div class="table-wrap">{by_tenure.to_html(index=False, border=0, escape=True)}</div></section>
<section><h2>Resumen por retrasos de pago</h2><div class="table-wrap">{by_payment_delay.to_html(index=False, border=0, escape=True)}</div></section>
<footer>Generado automáticamente por Python y pandas. Escenario reproducible con semilla fija; revisar README para definiciones, limitaciones y pasos de ejecución.</footer>
</main></body></html>
"""
    (OUTPUT_DIR / "dashboard.html").write_text(dashboard_html, encoding="utf-8")

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

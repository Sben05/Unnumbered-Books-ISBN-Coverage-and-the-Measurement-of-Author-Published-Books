"""Figures for the measurement-led paper, using existing audited CSV outputs.

No model is fitted here. The forecast panel reconstructs model predictions as
observed outcome minus the saved forecast error in ml_counterfactual_gaps.csv.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "paper_pt"
BLUE = "#173b63"
RED = "#a52a2a"
GOLD = "#bb832d"
GRAY = "#64748b"


def setup():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })


def puzzle():
    t = pd.read_csv(OUT / "table1_four_sources.csv", index_col=0)
    t.index = t.index.astype(int)
    b = pd.read_csv(OUT / "natbib_isbn_by_ap_year.csv").set_index("pub_year")
    b.index = b.index.astype(int)

    fig, ax = plt.subplots(1, 2, figsize=(11.4, 4.0), gridspec_kw={"width_ratios": [1, 1.15]})
    yrs = np.arange(2013, 2020)
    agency = t.loc[yrs, "agency ISBNs to author-publishers (CERLALC)"]
    books = t.loc[yrs, "self-published books in national bibliography"]
    ax[0].plot(yrs, 100 * agency / agency.loc[2013], "o-", color=RED, lw=2.2,
               label="Agency author-publisher ISBNs")
    ax[0].plot(yrs, 100 * books / books.loc[2013], "s-", color=BLUE, lw=2.2,
               label="Bibliography self-published books")
    ax[0].axvline(2014.5, color=GRAY, linestyle=":", lw=1.2)
    ax[0].axhline(100, color="#d1d5db", lw=0.8)
    ax[0].set(title="A. Administrative series diverge", ylabel="Index (2013 = 100)",
              xlabel="Publication or registration year", xticks=yrs, ylim=(68, 145))
    ax[0].legend(loc="upper left", frameon=False, fontsize=8.2)

    yrs2 = np.arange(2005, 2020)
    ax[1].plot(yrs2, 100 * b.loc[yrs2, "ap_noisbn_share_of_ap"], "o-", color=RED,
               lw=2.2, ms=4, label="Self-published books")
    ax[1].plot(yrs2, 100 * b.loc[yrs2, "nonap_noisbn_share_of_nonap"], "s-", color=BLUE,
               lw=1.7, ms=3.5, label="Other books")
    ax[1].axvline(2014.5, color=GRAY, linestyle=":", lw=1.2)
    ax[1].set(title="B. ISBN absence within one bibliography", ylabel="Books without ISBN (%)",
              xlabel="Publication year", xlim=(2005, 2019), ylim=(0, 64))
    ax[1].set_xticks([2005, 2008, 2011, 2014, 2015, 2018])
    ax[1].legend(loc="upper right", frameon=False, fontsize=8.2)
    fig.tight_layout(w_pad=2)
    fig.savefig(OUT / "fig_reframe_puzzle.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def forecast():
    paths = pd.read_csv(OUT / "synthetic_control_paths.csv").set_index("y")
    gaps = pd.read_csv(OUT / "ml_counterfactual_gaps.csv", index_col=0)
    gaps.index = gaps.index.astype(int)
    invlogit = lambda z: 100 / (1 + np.exp(-z))
    actual = invlogit(paths.A_actual.loc[2005:2018])
    pred_logit = paths.A_actual.loc[2015:2018] - gaps.ENSEMBLE
    forecast_pct = invlogit(pred_logit)
    components = gaps.drop(columns="ENSEMBLE")
    comp_logit = pd.DataFrame({c: paths.A_actual.loc[2015:2018] - components[c]
                              for c in components.columns})
    comp_pct = invlogit(comp_logit)

    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.plot(actual.index, actual.values, "o-", color=BLUE, lw=2.3, ms=4.4,
            label="Observed Portugal")
    ax.plot(forecast_pct.index, forecast_pct.values, "s--", color=RED, lw=2.2, ms=5,
            label="Seven-model forecast")
    ax.fill_between(comp_pct.index, comp_pct.min(axis=1).values,
                    comp_pct.max(axis=1).values, color=RED, alpha=0.12,
                    label="Range across seven forecasts")
    ax.axvline(2014.5, color=GRAY, linestyle=":", lw=1.3)
    ax.set(title="Portugal's author-publisher share among ISBN-bearing books",
           ylabel="Author-as-publisher share of print ISBN records (%)",
           xlabel="Publication year", xlim=(2005, 2018), ylim=(0.5, 4.5))
    ax.set_xticks([2005, 2007, 2009, 2011, 2013, 2015, 2017, 2018])
    ax.legend(loc="upper left", frameon=False, fontsize=8.7)
    fig.tight_layout()
    fig.savefig(OUT / "fig_reframe_forecast.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    setup()
    puzzle()
    forecast()
    print("Wrote fig_reframe_puzzle.png and fig_reframe_forecast.png")

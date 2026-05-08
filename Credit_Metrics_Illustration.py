# /// script
# dependencies = [
#     "marimo",
#     "numpy==2.4.4",
#     "polars==1.40.1",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Introduction

    This notebook provides the workings of the examples as illustrated in the [CreditMetrics Technical Documentation](https://elischolar.library.yale.edu/cgi/viewcontent.cgi?article=1447&context=ypfs-documents).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calculating credit risk for a single exposure

    In the first example we calculate the credit risk arising from a single BBB rated bond with a 5-year maturity period.  The face value of the bond is taken to be $100 with annual coupons at 6% p.a.

    We are looking to derive the distribution of the bond's value in 1-years time allowing for defaults and down(up)ward revisions in its rating.  There are three steps in the calculation process.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 1: Transition probability over the 1-year time horizon

    We need a set of transition probabilities for each credit rating. The matrix provided in the CreditMetrics documentation is provided as follows and is derived from S&P data:
    """)
    return


@app.cell(hide_code=True)
def _(df_transition_prob):
    df_transition_prob
    return


@app.cell(hide_code=True)
def _(df_recovery_rates, mo, pl):
    mo.md(rf"""
    ### Step 2: Valuation at the end of the 1-year time horizon

    There are two cases to consider here:

    **Case A: The bond defaults**

    In this case we need to use recovery rate assumptions. CreditMetrics provides the below table split by seniority class.  The BBB bond falls under the category of Senior Unsecured.

    So, the mean value of the bond under default will come out to be ${df_recovery_rates.filter(pl.col("Seniority_Class") == "Senior Unsecured").select(pl.col("Mean")).item()}
    """)
    return


@app.cell(hide_code=True)
def _(df_recovery_rates):
    df_recovery_rates
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Case B: Credit rating change**

    In case of a rating change, the bond's value will need to be revalued using the changed rating's one-year forward zero curves.

    The CreditMetrics paper assumes that these curves will already be provided to us. These are shown in the table below.
    """)
    return


@app.cell(hide_code=True)
def _(df_one_year_fwd_zero_curves):
    df_one_year_fwd_zero_curves
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The possible one-year forward values for the BBB bond (plus coupon) are shown below. We have also tagged on the default rate value
    """)
    return


@app.cell
def _(df_one_year_fwd_zero_curves, df_recovery_rates, np, pl):
    spot_rates = (
        df_one_year_fwd_zero_curves.select(pl.exclude("Category")).to_numpy() / 100
    )

    discount_factors = (1 + spot_rates) ** -np.arange(1, 5)
    # Add a column of 1's for t=0
    discount_factors = np.column_stack([np.ones((7, 1)), discount_factors])

    bond_cashflows = np.array([6, 6, 6, 6, 106]).reshape((5, 1))

    terminal_bond_values = discount_factors @ bond_cashflows

    # Value of the bond under default state
    default_value = (
        df_recovery_rates.filter(pl.col("Seniority_Class") == "Senior Unsecured")
        .select("Mean")
        .item()
    )
    terminal_bond_values = np.append(terminal_bond_values.flatten(), default_value)

    terminal_bond_values
    return (terminal_bond_values,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: Credit risk estimation
    """)
    return


@app.cell(hide_code=True)
def _(df_transition_prob, np, pl, terminal_bond_values):
    transition_prob = (
        df_transition_prob.filter(pl.col("Initial_Rating") == "BBB")
        .select(pl.exclude("Initial_Rating"))
        .to_numpy()
        .flatten()
    )
    transition_prob = transition_prob / 100

    mean = np.sum(terminal_bond_values * transition_prob)
    variance = np.sum((terminal_bond_values - mean) ** 2 * transition_prob)

    {"mean": mean.round(2), "standard deviance": np.sqrt(variance).round(2)}
    return


@app.cell(hide_code=True)
def _(pl):
    df_transition_prob = pl.DataFrame(
        {
            "Initial_Rating": ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"],
            "After_1_year_AAA": [90.81, 0.7, 0.09, 0.02, 0.03, 0, 0.22],
            "After_1_year_AA": [8.33, 90.65, 2.27, 0.33, 0.14, 0.11, 0],
            "After_1_year_A": [0.68, 7.79, 91.05, 5.95, 0.67, 0.24, 0.22],
            "After_1_year_BBB": [0.06, 0.64, 5.52, 86.93, 7.73, 0.43, 1.3],
            "After_1_year_BB": [0.12, 0.06, 0.74, 5.3, 80.53, 6.48, 2.38],
            "After_1_year_B": [0.0, 0.14, 0.26, 1.17, 8.84, 83.46, 11.24],
            "After_1_year_CCC": [0.0, 0.02, 0.01, 0.12, 1.00, 4.07, 64.86],
            "After_1_year_Default": [0.0, 0.0, 0.06, 0.18, 1.06, 5.20, 19.79],
        }
    )
    return (df_transition_prob,)


@app.cell(hide_code=True)
def _(pl):
    df_recovery_rates = pl.DataFrame(
        {
            "Seniority_Class": [
                "Senior Secured",
                "Senior Unsecured",
                "Senior Subordinated",
                "Subordinated",
                "Junior Subordinated",
            ],
            "Mean": [53.8, 51.13, 38.52, 32.74, 17.09],
            "Standard_Deviation": [26.86, 24.45, 23.81, 20.18, 10.90],
        }
    )
    return (df_recovery_rates,)


@app.cell
def _(pl):
    df_one_year_fwd_zero_curves = pl.DataFrame(
        {
            "Category": ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"],
            "Year_1": [3.60, 3.65, 3.72, 4.1, 5.55, 6.05, 15.05],
            "Year_2": [4.17, 4.22, 4.32, 4.67, 6.02, 7.02, 15.02],
            "Year_3": [4.73, 4.78, 4.93, 5.25, 6.78, 8.03, 14.03],
            "Year_4": [5.12, 5.17, 5.32, 5.63, 7.27, 8.52, 13.52],
        }
    )
    return (df_one_year_fwd_zero_curves,)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import polars as pl
    import numpy as np

    return np, pl


if __name__ == "__main__":
    app.run()

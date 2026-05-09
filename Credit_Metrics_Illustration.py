# /// script
# dependencies = [
#     "marimo",
#     "numpy==2.4.4",
#     "polars==1.40.1",
#     "scipy==1.17.1",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.23.5"
app = marimo.App(width="columns")


@app.cell(column=0, hide_code=True)
def _(mo):
    mo.md(r"""
    # Part I: Risk Measurement Framework
    """)
    return


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
def _(df_one_year_fwd_zero_curves, df_recovery_rates, mo, np, pl):
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

    mo.ui.matrix(terminal_bond_values.reshape(1, -1), disabled=True, precision=2)
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
        .reshape(-1, 1)
    )
    transition_prob = transition_prob / 100

    mean = (terminal_bond_values @ transition_prob).item()
    variance = ((terminal_bond_values - mean) ** 2 @ transition_prob).item()

    {"mean": round(mean, 2), "standard deviance": round(np.sqrt(variance), 2)}
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calculating credit risk for a portfolio

    In this example, we will calculate the credit risk across a portfolio with two specific bonds:

    - Bond #1: BBB rated, senior unsecured, 6% annual coupon, five-year maturity.
    - Bond #2: A rated, senior unsecured, 5% annual coupon, three-year maturity.

    If we assume that the two bonds are completely independent, their joint transitional probabilities will simply be the product of their corresponding marginal probabilities. This is shown in the matrix below where the rows represent the rating transitions for Bond #1 (going from AAA to Default) and the columns for Bond #2.
    """)
    return


@app.cell(hide_code=True)
def _(credit_ratings, df_transition_prob, mo, pl):
    transition_prob_BBB = (
        df_transition_prob.filter(pl.col("Initial_Rating") == "BBB")
        .select(pl.exclude("Initial_Rating"))
        .to_numpy()
        .reshape(-1, 1)
    ) / 100

    transition_prob_A = (
        df_transition_prob.filter(pl.col("Initial_Rating") == "A")
        .select(pl.exclude("Initial_Rating"))
        .to_numpy()
        .reshape(1, -1)
    ) / 100

    mo.ui.matrix(
        (transition_prob_BBB @ transition_prob_A) * 100,
        disabled=True,
        precision=2,
        row_labels=credit_ratings,
        column_labels=credit_ratings,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The assumption of independence is too simplistic and rarely holds true in practice. So, we need to derive some kind of correlation between the different assets.

    The actual model to derive such correlated joint probability distributions will be covered later on. For this particular example, we will assume that the joint distribution (assuming a 30% asset correlation) is provided to us.
    """)
    return


@app.cell
def _(calculate_bond_values, credit_ratings, mo, np):
    bond_1_values = calculate_bond_values(bond_1=True)
    bond_2_values = calculate_bond_values(bond_1=False)

    bond_1_values_matrix = np.tile(bond_1_values.reshape(-1, 1), (1, 8))
    bond_2_values_matrix = np.tile(bond_2_values, (8, 1))

    bond_values_portfolio = bond_1_values_matrix + bond_2_values_matrix

    mo.ui.matrix(
        bond_values_portfolio,
        disabled=True,
        precision=2,
        row_labels=credit_ratings,
        column_labels=credit_ratings,
    )
    return


@app.cell(hide_code=True)
def _(df_one_year_fwd_zero_curves, df_recovery_rates, np, pl):
    def calculate_bond_values(bond_1: bool):
        spot_rates = (
            df_one_year_fwd_zero_curves.select(pl.exclude("Category")).to_numpy()
            / 100
        )

        discount_factors = (1 + spot_rates) ** -np.arange(1, 5)
        # Add a column of 1's for t=0
        discount_factors = np.column_stack([np.ones((7, 1)), discount_factors])

        if bond_1:
            bond_cashflows = np.array([6, 6, 6, 6, 106]).reshape((-1, 1))
        else:
            bond_cashflows = np.array([5, 5, 105, 0, 0]).reshape((-1, 1))

        terminal_bond_values = discount_factors @ bond_cashflows

        # Value of the bond under default state
        default_value = (
            df_recovery_rates.filter(
                pl.col("Seniority_Class") == "Senior Unsecured"
            )
            .select("Mean")
            .item()
        )
        terminal_bond_values = np.append(
            terminal_bond_values.flatten(), default_value
        )
        return terminal_bond_values

    return (calculate_bond_values,)


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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
def _():
    credit_ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "Default"]
    return (credit_ratings,)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import polars as pl
    import numpy as np
    from scipy.optimize import minimize
    from scipy.special import softmax

    np.set_printoptions(precision=4, suppress=True)
    return minimize, np, pl, softmax


@app.cell(column=1, hide_code=True)
def _(mo):
    mo.md(r"""
    # Part II: Model Parameters

    ## Notes

    The volatility of losses is termed as _unexpected_ losses.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Deriving the Annual Transition Matrix from Cumulative Default Rates

    Section 6.4.1 of the CreditMetrics Technical Document demonstrates that cumulative default rates can be closely replicated by a **single annual transition matrix** modelled as a **Markov process**.

    The key result: *"there exists some annual transition matrix which best replicates (in a least-squares sense) this default history."*

    If $M$ is the annual $8 \times 8$ transition matrix over the seven rating categories plus an absorbing default state, the cumulative default probability for rating $i$ at horizon $t$ years is:

    $$P(i_t = D \mid i_0) = [M^t]_{i, D}$$

    We choose $M$ (non-negative entries, rows summing to 1) to minimise the sum of squared differences between the modelled and observed cumulative default rates.

    The cumulative default rates data has been sourced from [Default and Recovery Rates of Corporate Bond Issuers, 1920-2004](https://www.bu.edu/econ/files/2015/01/Moodys_Default_1920-2004.pdf) paper (Exhibit 17).
    """)
    return


@app.cell(hide_code=True)
def _(np):
    markov_terms = np.arange(1, 16)  # Years 1-15 (complete)

    # Source: Moody's Special Comment 'Default and Recovery Rates of Corporate Bond
    # Issuers, 1920-2004' (January 2005), Exhibit 17. Ratings map as:
    # Aaa->AAA, Aa->AA, A->A, Baa->BBB, Ba->BB, B->B, Caa-C->CCC
    moody_cum_default_obs = (
        np.array(
            [
                [
                    0.00,
                    0.00,
                    0.02,
                    0.09,
                    0.19,
                    0.30,
                    0.41,
                    0.59,
                    0.77,
                    1.01,
                    1.22,
                    1.37,
                    1.57,
                    1.66,
                    1.70,
                ],
                [
                    0.06,
                    0.19,
                    0.32,
                    0.49,
                    0.78,
                    1.11,
                    1.48,
                    1.85,
                    2.20,
                    2.57,
                    3.01,
                    3.50,
                    3.98,
                    4.48,
                    4.87,
                ],
                [
                    0.08,
                    0.25,
                    0.54,
                    0.87,
                    1.22,
                    1.58,
                    1.98,
                    2.34,
                    2.76,
                    3.22,
                    3.71,
                    4.21,
                    4.65,
                    5.09,
                    5.56,
                ],
                [
                    0.31,
                    0.93,
                    1.69,
                    2.55,
                    3.40,
                    4.28,
                    5.12,
                    5.95,
                    6.83,
                    7.63,
                    8.42,
                    9.22,
                    10.00,
                    10.70,
                    11.32,
                ],
                [
                    1.39,
                    3.36,
                    5.48,
                    7.71,
                    9.93,
                    12.01,
                    13.84,
                    15.65,
                    17.25,
                    19.00,
                    20.60,
                    22.16,
                    23.72,
                    25.10,
                    26.31,
                ],
                [
                    4.56,
                    9.97,
                    15.24,
                    19.85,
                    23.80,
                    27.13,
                    30.16,
                    32.62,
                    34.74,
                    36.51,
                    38.24,
                    39.80,
                    41.23,
                    42.67,
                    43.92,
                ],
                [
                    15.07,
                    24.77,
                    31.82,
                    36.76,
                    40.50,
                    43.63,
                    45.85,
                    47.94,
                    49.89,
                    51.64,
                    53.63,
                    55.61,
                    57.33,
                    59.19,
                    60.94,
                ],
            ]
        )
        / 100
    )
    return markov_terms, moody_cum_default_obs


@app.cell(hide_code=True)
def _(credit_ratings, markov_terms, mo, moody_cum_default_obs):
    mo.vstack(
        [
            mo.md(
                """**Average cumulative default rates, 1920-2004 cohort (%)**"""
            ),
            mo.ui.matrix(
                moody_cum_default_obs * 100,
                disabled=True,
                precision=2,
                row_labels=credit_ratings[:-1],
                column_labels=[f"Yr {t}" for t in markov_terms],
            ),
        ]
    )
    return


@app.cell
def _(markov_terms, minimize, moody_cum_default_obs, np, softmax):
    _N_R, _N_S = 7, 8

    def _to_matrix(x):
        M = np.zeros((_N_S, _N_S))
        M[:_N_R] = softmax(x.reshape(_N_R, _N_S), axis=1)
        M[_N_R, _N_R] = 1.0  # default is absorbing
        return M

    def _cum_def(M, terms):
        Mt, res = np.eye(_N_S), {}
        for t in range(1, int(terms.max()) + 1):
            Mt = Mt @ M
            if t in terms: res[t] = Mt[:_N_R, _N_R]
        return np.column_stack([res[t] for t in terms])

    # Moody's Table 6.1 one-year matrix: starting point and regularisation target.
    # Without regularisation the optimizer is free to redistribute probability mass
    # among non-default states arbitrarily (cumulative defaults only constrain the
    # default column of M^t). Adding an L2 penalty towards M0 keeps the matrix
    # economically sensible (diagonal dominant, smooth migrations) at minimal cost
    # to the cumulative-default fit.
    _M0 = np.array([
        [93.40, 5.94, 0.64, 0.00, 0.02, 0.00, 0.00, 0.00],
        [ 1.61,90.55, 7.46, 0.26, 0.09, 0.01, 0.00, 0.02],
        [ 0.07, 2.28,92.44, 4.63, 0.45, 0.12, 0.01, 0.00],
        [ 0.05, 0.26, 5.51,88.48, 4.76, 0.71, 0.08, 0.15],
        [ 0.02, 0.05, 0.42, 5.16,86.91, 5.91, 0.24, 1.29],
        [ 0.00, 0.04, 0.13, 0.54, 6.35,84.22, 1.91, 6.81],
        [ 0.00, 0.00, 0.00, 0.62, 2.05, 4.08,69.20,24.06],
    ]) / 100
    _x0 = np.log(np.clip(_M0, 1e-6, None)).flatten()

    markov_reg_lambda = 0.01

    def _objective(x):
        M = _to_matrix(x)
        cum_err = np.sum((_cum_def(M, markov_terms) - moody_cum_default_obs) ** 2)
        reg = markov_reg_lambda * np.sum((M[:_N_R] - _M0) ** 2)
        return cum_err + reg

    _result = minimize(
        _objective, _x0, method='L-BFGS-B',
        options={'maxiter': 50000, 'ftol': 1e-16, 'gtol': 1e-12},
    )

    markov_fit_matrix = _to_matrix(_result.x)
    markov_cum_default_fit = _cum_def(markov_fit_matrix, markov_terms)
    # RMSE computed on cumulative-default fit only (excludes regularisation term)
    markov_fit_rmse = float(np.sqrt(
        np.sum((markov_cum_default_fit - moody_cum_default_obs) ** 2)
        / moody_cum_default_obs.size
    ))
    return markov_cum_default_fit, markov_fit_matrix


@app.cell(hide_code=True)
def _(mo):
    mo.md(rf"""
    ### Imputed Transition Matrix (Table 6.5)

    The matrix below is fitted to the Moody's cumulative default data (Table 6.4) via least-squares, with an L2 regularisation term penalising deviation from the Moody's historical one-year matrix. This mirrors the approach in Section 6.4.5 of the CreditMetrics document (_match historically tabulated transition matrix_), which adds the historical matrix as a soft constraint to recover economically sensible results (diagonal dominance, smooth migrations) that a pure cumulative-default fit cannot guarantee.
    """)
    return


@app.cell(hide_code=True)
def _(credit_ratings, markov_fit_matrix, mo):
    mo.ui.matrix(
        markov_fit_matrix[:7] * 100,
        disabled=True,
        precision=2,
        row_labels=credit_ratings[:-1],
        column_labels=credit_ratings,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Validation: Modelled vs Observed Cumulative Default Rates (Table 6.6)

    The two matrices below compare the observed Moody's rates (Table 6.4) against the rates
    implied by the fitted transition matrix. The close agreement confirms that a Markov process
    is a valid statistical model for credit rating migrations.
    """)
    return


@app.cell(hide_code=True)
def _(credit_ratings, markov_cum_default_fit, markov_terms, mo):
    mo.vstack(
        [
            mo.md("**Modelled cumulative default rates from fitted matrix (%)**"),
            mo.ui.matrix(
                markov_cum_default_fit * 100,
                disabled=True,
                precision=2,
                row_labels=credit_ratings[:-1],
                column_labels=[f"Year {t}" for t in markov_terms],
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(credit_ratings, markov_terms, mo, moody_cum_default_obs):
    mo.vstack(
        [
            mo.md("**Observed cumulative default rates (%)**"),
            mo.ui.matrix(
                moody_cum_default_obs * 100,
                disabled=True,
                precision=2,
                row_labels=credit_ratings[:-1],
                column_labels=[f"Year {t}" for t in markov_terms],
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()

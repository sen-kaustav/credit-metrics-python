# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This project implements the examples and methodology from the **CreditMetrics Technical Document** (JP Morgan, 1997) as an interactive marimo notebook. The PDF is at `CreditMetrics Technical Document.pdf`.

## Analysis Structure

The notebook (`Credit_Metrics_Illustration.py`) works through the document sequentially. Completed sections:

**Part I — Risk Measurement Framework**
- Single-exposure credit risk: transition probabilities, bond revaluation under each rating state (default recovery + forward curve repricing), and distribution statistics (mean, std deviation) for a BBB bond.
- Portfolio credit risk: joint transition probability matrix under independence assumption, and portfolio bond value matrix across all rating state combinations.

**Part II — Model Parameters**
- Deriving the annual transition matrix from cumulative default rates by fitting a Markov process via least-squares (scipy L-BFGS-B). The softmax parametrisation ensures rows are non-negative and sum to 1; default is an absorbing state.

## Data Sources

- **Transition matrix**: S&P one-year matrix from CreditMetrics paper (Table 6.2), hardcoded as `df_transition_prob`.
- **Forward zero curves**: Hardcoded from CreditMetrics paper (Table 1.2), used to reprice bonds after rating migrations.
- **Recovery rates**: Hardcoded from CreditMetrics paper by seniority class.
- **Cumulative default rates**: Moody's *"Default and Recovery Rates of Corporate Bond Issuers, 1920–2004"* (January 2005), Exhibit 17 — the full 15-year annual series for all seven rating categories (Aaa/Aa/A/Baa/Ba/B/Caa-C, equivalent to S&P AAA–CCC). This replaces the partial 8-point table in the paper.

## Key Implementation Choices

- **Marimo reactivity**: data cells define variables (e.g. `df_transition_prob`, `moody_cum_default_obs`) that are consumed downstream; display cells use `mo.ui.matrix` for interactive table views.
- **Softmax parametrisation**: transition matrix rows are parametrised as `softmax(logits)` so the optimiser operates in unconstrained logit space while guaranteeing valid probabilities.
- **Initialisation**: the Moody's historical one-year matrix (Table 6.1) is a good enough starting point that a single L-BFGS-B run converges without multi-start.
- **Private helpers**: optimisation helper functions and variables use a `_` prefix so marimo does not export them to the reactive graph.

## Environment

The project uses `uv` for environment management. Dependencies are declared inline in the notebook script header and in `.venv/`. Current dependencies: marimo, numpy, polars, scipy.

## Commands

```powershell
# Run the notebook in edit mode (opens browser)
uv run marimo edit Credit_Metrics_Illustration.py

# Run with inline script dependencies (no venv needed)
uv run Credit_Metrics_Illustration.py

# Run headless
uv run marimo run Credit_Metrics_Illustration.py
```

## Working with the Notebook

Use the `marimo-pair` skill (`.agents/skills/marimo-pair/`) to work inside a running notebook session.

On Windows, auto-discovery of running servers may fail; use `--url http://127.0.0.1:<port>` directly.

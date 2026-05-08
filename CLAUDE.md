# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A [Marimo](https://marimo.io/) notebook implementing illustrative examples from the [CreditMetrics Technical Documentation](https://elischolar.library.yale.edu/cgi/viewcontent.cgi?article=1447&context=ypfs-documents). The single notebook (`Credit_Metrics_Illustration.py`) walks through credit risk calculations for bond exposures: transition probability matrices, bond revaluation under rating changes and default, and credit risk estimation (mean/variance).

## Environment

The project uses `uv` for environment management. Dependencies are declared inline in the notebook script header (marimo, numpy==2.4.4, polars==1.40.1) and in `.venv/`.

## Commands

```powershell
# Run the notebook in edit mode (opens browser)
uv run marimo edit Credit_Metrics_Illustration.py

# Run with inline script dependencies (no venv needed)
uv run Credit_Metrics_Illustration.py

# Run headless
uv run marimo run Credit_Metrics_Illustration.py
```

## Architecture

`Credit_Metrics_Illustration.py` is a Marimo reactive notebook — cells form a dataflow graph where downstream cells re-execute automatically when their dependencies change. Cell execution order is determined by variable references, not file order.

Key data flows:
- Three static `pl.DataFrame` cells define the input tables: `df_transition_prob`, `df_recovery_rates`, `df_one_year_fwd_zero_curves`
- A computation cell derives `terminal_bond_values` (bond value under each rating outcome) using numpy matrix operations against the zero curves
- A final cell computes mean and standard deviation of the value distribution, weighted by transition probabilities

## Working with the Notebook

Use the `marimo-pair` skill (`.agents/skills/marimo-pair/`) to work inside a running notebook session. **Never edit `Credit_Metrics_Illustration.py` directly with `Edit`/`Write` while a marimo session is running** — the kernel will overwrite your changes on its next save. Use `ctx.edit_cell()` via the skill instead.

On Windows, auto-discovery of running servers may fail; use `--url http://127.0.0.1:<port>` directly.

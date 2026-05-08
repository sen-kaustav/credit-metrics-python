# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This project has been setup to implement the CreditMetrics Technical Document as a marimo notebook. The document is present in `CreditMetrics Technical Document.pdf`. 

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

## Working with the Notebook

Use the `marimo-pair` skill (`.agents/skills/marimo-pair/`) to work inside a running notebook session.

On Windows, auto-discovery of running servers may fail; use `--url http://127.0.0.1:<port>` directly.

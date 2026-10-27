# Project guidance

## Purpose

This is a data science learning project for predicting NFL player statistics and fantasy football outcomes. The first planned target is a player's weekly fantasy points using half-PPR scoring. Keep the work understandable and reproducible for someone learning the data and modeling workflow.

## Project setup

- Use Python 3.12 and `uv` for the project environment and dependencies.
- Put reusable Python code in `src/fantasy_analytics/` and exploratory work in `notebooks/`.
- Use `nflreadpy` for NFL data. Its weekly player statistics entry point is `load_player_stats(..., summary_level="week")`, which returns a Polars DataFrame.
- Keep setup and run instructions in `README.md`. Add dependencies to `pyproject.toml` when they are introduced.
- Do not commit downloaded datasets, local environments, notebook checkpoints, or generated model artifacts.
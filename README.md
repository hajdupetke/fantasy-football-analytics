# Fantasy football analytics

A Python learning project for exploring NFL data and, later, predicting weekly player fantasy points with half-PPR scoring. The first step is a reusable weekly player stats loader with a local Parquet cache. Scoring and modeling are future work.

## Set up

Install [uv](https://docs.astral.sh/uv/), then run from this project directory:

```bash
uv sync
```

The project uses Python 3.12. `uv` can install it if it is not already available. To start JupyterLab with the project environment:

```bash
uv run jupyter lab
```

Open `notebooks/01_data_exploration.ipynb` and select the project's `.venv` Python kernel. The notebook is an unexecuted example; running its data cell may download data.

## Download and use weekly stats

Prefetch one or more seasons from the command line:

```bash
uv run python -m fantasy_analytics.data 2024 2025
```

Use the same loader in a notebook or script:

```python
from fantasy_analytics.data import get_weekly_player_stats

stats = get_weekly_player_stats([2024, 2025])
print(stats.head())
```

The loader calls `nflreadpy.load_player_stats(season, summary_level="week")` for each season that is not cached. It saves one file per season under `data/raw/weekly_player_stats_<season>.parquet` and reads that file on later calls. Cached data stays as it was until you explicitly refresh it:

```bash
uv run python -m fantasy_analytics.data 2025 --refresh
```

In Python, use `get_weekly_player_stats(2025, refresh=True)`. A custom cache location can be passed as `cache_dir=...`. A failed refresh leaves the previous Parquet file in place. The `data/` directory is ignored by version control.

## Project layout

- `src/fantasy_analytics/`: reusable Python code
- `notebooks/`: exploratory notebooks
- `tests/`: offline tests for the data loader
- `data/raw/`: downloaded Parquet files, created on demand

Run the tests with `uv run pytest`.

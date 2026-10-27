"""Download weekly player statistics and cache them as Parquet files."""

import argparse
import os
import tempfile
from pathlib import Path

import nflreadpy
import polars as pl

DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[0] / "raw"


def get_weekly_player_stats(
    seasons: int | list[int],
    refresh: bool = False,
    cache_dir: str | Path | None = None,
) -> pl.DataFrame:
    """Load weekly player stats, downloading each uncached season once.

    Set ``refresh=True`` to replace existing cached seasons with fresh data.
    Requested seasons are returned in order, without duplicate seasons.
    """
    season_list = [seasons] if isinstance(seasons, int) else list(seasons)
    if not season_list or any(
        isinstance(season, bool) or not isinstance(season, int) or season <= 0
        for season in season_list
    ):
        raise ValueError("seasons must contain at least one positive integer")

    cache_path = Path(cache_dir) if cache_dir is not None else DEFAULT_CACHE_DIR
    frames = []
    for season in dict.fromkeys(season_list):
        path = cache_path / f"weekly_player_stats_{season}.parquet"
        if path.exists() and not refresh:
            frame = pl.read_parquet(path)
        else:
            frame = (
                nflreadpy
                .load_player_stats(season, summary_level="week")
                .with_columns((
                        pl.col("fantasy_points")
                        + pl.col("receptions") * 0.5
                    ).alias("fantasy_points_half_ppr")
                )
            )
            cache_path.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{path.stem}_", suffix=".parquet", dir=cache_path
            )
            os.close(descriptor)
            temporary_path = Path(temporary_name)
            try:
                frame.write_parquet(temporary_path)
                temporary_path.replace(path)
            finally:
                temporary_path.unlink(missing_ok=True)
        frames.append(frame)

    if len(frames) == 1:
        return frames[0]
    return pl.concat(frames, how="diagonal_relaxed")


def main() -> None:
    """Download or read one or more seasons from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seasons", type=int, nargs="+", help="NFL season years")
    parser.add_argument(
        "--refresh", action="store_true", help="download and replace cached files"
    )
    args = parser.parse_args()
    frame = get_weekly_player_stats(args.seasons, refresh=args.refresh)
    print(f"Loaded {frame.height:,} weekly player rows from {len(set(args.seasons))} season(s).")
    print(f"Parquet cache: {DEFAULT_CACHE_DIR}")


if __name__ == "__main__":
    main()

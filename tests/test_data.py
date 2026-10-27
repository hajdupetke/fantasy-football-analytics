from pathlib import Path

import polars as pl
import pytest

from fantasy_analytics.data import loader


def sample_frame(season: int, value: int = 1) -> pl.DataFrame:
    return pl.DataFrame({"season": [season], "week": [1], "value": [value]})


def test_cache_miss_downloads_and_saves_parquet(monkeypatch, tmp_path: Path) -> None:
    calls = []

    def download(season: int, summary_level: str) -> pl.DataFrame:
        calls.append((season, summary_level))
        return sample_frame(season)

    monkeypatch.setattr(loader.nflreadpy, "load_player_stats", download)

    result = loader.get_weekly_player_stats(2024, cache_dir=tmp_path)

    assert calls == [(2024, "week")]
    assert result.equals(sample_frame(2024))
    assert pl.read_parquet(tmp_path / "weekly_player_stats_2024.parquet").equals(result)


def test_cache_hit_does_not_download(monkeypatch, tmp_path: Path) -> None:
    cached = sample_frame(2024)
    cached.write_parquet(tmp_path / "weekly_player_stats_2024.parquet")

    def unexpected_download(*args, **kwargs) -> pl.DataFrame:
        raise AssertionError("cache hit should not download")

    monkeypatch.setattr(loader.nflreadpy, "load_player_stats", unexpected_download)

    assert loader.get_weekly_player_stats(2024, cache_dir=tmp_path).equals(cached)


def test_refresh_replaces_cached_season(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "weekly_player_stats_2024.parquet"
    sample_frame(2024).write_parquet(path)
    fresh = sample_frame(2024, value=2)
    monkeypatch.setattr(loader.nflreadpy, "load_player_stats", lambda *args, **kwargs: fresh)

    assert loader.get_weekly_player_stats(2024, refresh=True, cache_dir=tmp_path).equals(fresh)
    assert pl.read_parquet(path).equals(fresh)


def test_multiple_seasons_are_combined_in_requested_order(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        loader.nflreadpy,
        "load_player_stats",
        lambda season, summary_level: sample_frame(season),
    )

    result = loader.get_weekly_player_stats([2025, 2024, 2025], cache_dir=tmp_path)

    assert result["season"].to_list() == [2025, 2024]
    assert len(list(tmp_path.glob("*.parquet"))) == 2


def test_failed_refresh_preserves_previous_file(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "weekly_player_stats_2024.parquet"
    original = sample_frame(2024)
    original.write_parquet(path)

    def failed_download(*args, **kwargs) -> pl.DataFrame:
        raise RuntimeError("download failed")

    monkeypatch.setattr(loader.nflreadpy, "load_player_stats", failed_download)

    with pytest.raises(RuntimeError, match="download failed"):
        loader.get_weekly_player_stats(2024, refresh=True, cache_dir=tmp_path)

    assert pl.read_parquet(path).equals(original)
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("seasons", [[], 0, [2024, True], [2024, "2025"]])
def test_invalid_seasons_are_rejected(seasons, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="seasons must contain"):
        loader.get_weekly_player_stats(seasons, cache_dir=tmp_path)

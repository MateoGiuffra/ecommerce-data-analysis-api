import pandas as pd
from unittest.mock import MagicMock
from src.services.metrics.metrics_service import MetricsService
from src.repositories.metrics_repository import MetricsRepository
from src.services.cache_service import CacheService


def test_clean_and_convert_to_numeric():
    # Arrange
    repo_mock = MagicMock(spec=MetricsRepository)
    cache_mock = MagicMock(spec=CacheService)
    svc = MetricsService(repo_mock, cache_mock, cache_df_ttl_seconds=600)

    s = pd.Series(["1,000", "NaN", "inf", "-inf", "abc", None, 42])

    # Act
    out = svc._clean_and_convert_to_numeric(s)

    # Assert
    assert out.dtype == float
    assert list(out.fillna(0).round(6)) == [1000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 42.0]

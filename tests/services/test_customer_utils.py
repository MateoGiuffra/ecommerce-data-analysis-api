import pandas as pd
from unittest.mock import MagicMock
from src.services.metrics.customer_service import CustomerService
from src.repositories.metrics_repository import MetricsRepository
from src.services.cache_service import CacheService


def test_safe_qcut_all_identical():
    repo_mock = MagicMock(spec=MetricsRepository)
    cache_mock = MagicMock(spec=CacheService)
    svc = CustomerService(repo_mock, cache_mock, cache_df_ttl_seconds=600)

    series = pd.Series([1, 1, 1, 1])
    labels = [5, 4, 3, 2, 1]
    res = svc._safe_qcut(series, q=5, labels=labels)
    assert all(int(x) == labels[len(labels) // 2] for x in res)


def test_safe_qcut_few_unique():
    repo_mock = MagicMock(spec=MetricsRepository)
    cache_mock = MagicMock(spec=CacheService)
    svc = CustomerService(repo_mock, cache_mock, cache_df_ttl_seconds=600)

    series = pd.Series([1, 1, 2, 2, 3, 3])
    labels = [5, 4, 3, 2, 1]
    res = svc._safe_qcut(series, q=5, labels=labels)
    # Result length should match input
    assert len(res) == len(series)
    # Values should be in labels (or None for missing)
    assert all((x in labels) or (x is None) for x in res)


def test_safe_qcut_normal_distribution():
    repo_mock = MagicMock(spec=MetricsRepository)
    cache_mock = MagicMock(spec=CacheService)
    svc = CustomerService(repo_mock, cache_mock, cache_df_ttl_seconds=600)

    series = pd.Series(range(1, 101))
    labels = [5, 4, 3, 2, 1]
    res = svc._safe_qcut(series, q=5, labels=labels)
    assert len(res.unique()) <= len(labels)

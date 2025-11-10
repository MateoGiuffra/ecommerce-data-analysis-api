import pytest
from fastapi.testclient import TestClient
from src.main import app


class FakeCacheService:
    def __init__(self):
        self.cleared = False

    async def delete_cache(self):
        self.cleared = True


class FakeMetricsService:
    def __init__(self):
        self.warmed = False

    async def warm_up_dataframe_cache(self):
        self.warmed = True


def test_clear_cache_and_warmup(tmp_path):
    fake_cache = FakeCacheService()
    fake_metrics = FakeMetricsService()

    # override dependencies
    from src.dependencies.services_di import get_cache_service, get_metrics_service
    app.dependency_overrides[get_cache_service] = lambda: fake_cache
    app.dependency_overrides[get_metrics_service] = lambda: fake_metrics

    with TestClient(app) as client:
        resp = client.delete("/admin/cache")
        assert resp.status_code == 200
        assert resp.json().get("message") == "Cache cleared successfully"

        resp2 = client.post("/admin/tasks/warm-up-cache")
        assert resp2.status_code == 200
        assert resp2.json().get("message") == "Cache warmed up successfully"

    app.dependency_overrides.clear()

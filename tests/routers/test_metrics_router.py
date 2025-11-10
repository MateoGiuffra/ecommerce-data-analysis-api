from fastapi.testclient import TestClient
from src.main import app


class Dummy:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


class FakeMetricsService:
    async def get_kpi_summary(self):
        return Dummy({"total_revenue": 100.0, "total_products_sold": 5, "average_total_products_sold": 1.0})

    async def get_series(self, serie_type):
        return [Dummy({"period": "2025-01-01", "revenue": 10.0, "products_sold": 1, "growth_rate": 0.0})]

    async def get_top_countries(self, countries_params):
        return [Dummy({"country": "AR", "revenue": 50.0, "products_sold": 3})]

    async def get_top_country_by_name(self, country_name: str):
        return Dummy({"country": country_name, "revenue": 50.0, "products_sold": 3})

    async def get_page(self, page_params):
        return Dummy({"results": [], "page": 1, "limit": 10, "total_pages": 0, "total_results": 0})


def test_analysis_endpoints():
    from src.dependencies.services_di import get_metrics_service
    fake = FakeMetricsService()
    app.dependency_overrides[get_metrics_service] = lambda: fake

    with TestClient(app) as client:
        r = client.get("/analysis/kpi_summary")
        assert r.status_code == 200
        assert "total_revenue" in r.json()

        r2 = client.get("/analysis/series")
        assert r2.status_code == 200
        assert isinstance(r2.json(), list)

        r3 = client.get("/analysis/top_countries")
        assert r3.status_code == 200

        r4 = client.get("/analysis/top_countries/AR")
        assert r4.status_code == 200

        r5 = client.get("/analysis/page")
        assert r5.status_code == 200

    app.dependency_overrides.clear()

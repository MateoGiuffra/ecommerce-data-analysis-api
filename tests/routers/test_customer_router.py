from fastapi.testclient import TestClient
from src.main import app


class Dummy:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


class FakeCustomerService:
    async def get_rfm_analysis(self, max_score: int = 5):
        return [Dummy({"recency": 1, "frequency": 1, "monetary": 5.0, "total_spend": 5.0, "segment_name": "Champion"})]

    async def get_top_spenders(self, params):
        return [Dummy({"customer_id": "c1", "total_spent": 10.0, "total_sells": 1, "total_units_sold": 1})]


def test_customer_endpoints():
    from src.dependencies.services_di import get_customer_service
    fake = FakeCustomerService()
    app.dependency_overrides[get_customer_service] = lambda: fake

    with TestClient(app) as client:
        r = client.get("/metrics/customers/rfm")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        r2 = client.get("/metrics/customers/top-spenders")
        assert r2.status_code == 200

    app.dependency_overrides.clear()

from fastapi.testclient import TestClient
from src.main import app
from src.dependencies.services_di import get_customer_service
from src.schemas.metrics import RFMAnalysis, SegmentName
from src.schemas.pagination import PageResponse

class Dummy:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


class FakeCustomerService:
    async def get_rfm_analysis_page(self, page_params=None):
        item = RFMAnalysis(
            recency=3,
            frequency=2,
            monetary=4.0,
            total_spend=1797.24,
            segment_name=SegmentName.NEED_ATTENTION,
        )
        page = getattr(page_params, "page", 1) if page_params is not None else 1
        limit = getattr(page_params, "limit", 10) if page_params is not None else 10
        return PageResponse(
            results=[item],
            page=page,
            limit=limit,
            total_pages=1,
            total_results=1,
        )


def test_customer_endpoints():
    app.dependency_overrides[get_customer_service] = lambda: FakeCustomerService()
    with TestClient(app) as client:
        resp = client.get("/metrics/customers/rfm?page=1&limit=1")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "results" in data and isinstance(data["results"], list)
        assert len(data["results"]) == 1
        item = data["results"][0]
        assert item["recency"] == 3
        assert item["frequency"] == 2
        assert item["segment_name"] == "Need Atention" or item["segment_name"] == "Need Attention"
    app.dependency_overrides.clear()

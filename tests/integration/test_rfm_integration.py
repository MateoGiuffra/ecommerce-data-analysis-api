from fastapi.testclient import TestClient
from src.main import app
from src.dependencies.services_di import get_customer_service
from src.schemas.metrics import RFMAnalysis, SegmentName
from src.schemas.pagination import PageResponse


class FakeCustomerService:
    async def get_rfm_analysis_page(self, page_params=None):
        # Return a PageResponse-like payload with a single RFMAnalysis item
        page = getattr(page_params, "page", 1) if page_params is not None else 1
        limit = getattr(page_params, "limit", 10) if page_params is not None else 10
        item = RFMAnalysis(
            recency=1,
            frequency=1,
            monetary=5.0,
            total_spend=5.0,
            segment_name=SegmentName.CHAMPIONS,
        )
        return PageResponse(
            results=[item],
            page=page,
            limit=limit,
            total_pages=1,
            total_results=1,
        )


def test_rfm_endpoint_returns_expected_shape():
    # Override dependency to return deterministic data
    app.dependency_overrides[get_customer_service] = lambda: FakeCustomerService()

    with TestClient(app) as client:
        resp = client.get("/metrics/customers/rfm")
        assert resp.status_code == 200
        data = resp.json()

        # Now we expect a paginated response dict
        assert isinstance(data, dict)
        assert "results" in data and isinstance(data["results"], list)
        assert "page" in data and "limit" in data
        assert data["page"] == 1
        assert data["limit"] == 10
        assert data["total_pages"] == 1
        assert data["total_results"] == 1

        assert len(data["results"]) == 1
        item = data["results"][0]
        assert item["recency"] == 1
        assert item["frequency"] == 1
        assert float(item["monetary"]) == 5.0
        assert float(item["total_spend"]) == 5.0
        assert item["segment_name"] == "Champion"

    app.dependency_overrides.clear()

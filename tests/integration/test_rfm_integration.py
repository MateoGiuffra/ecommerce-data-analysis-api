from fastapi.testclient import TestClient
from src.main import app
from src.dependencies.services_di import get_customer_service
from src.schemas.metrics import RFMAnalysis, SegmentName


class FakeCustomerService:
    async def get_rfm_analysis(self, max_score: int = 5):
        # Return a single, simple RFMAnalysis model for integration-style test
        return [
            RFMAnalysis(
                recency=1,
                frequency=1,
                monetary=5.0,
                total_spend=5.0,
                segment_name=SegmentName.CHAMPIONS
            )
        ]


def test_rfm_endpoint_returns_expected_shape():
    # Override dependency to return deterministic data
    app.dependency_overrides[get_customer_service] = lambda: FakeCustomerService()

    with TestClient(app) as client:
        resp = client.get("/metrics/customers/rfm")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
    item = data[0]
    # Basic structural checks according to current RFMAnalysis schema
    assert item["recency"] == 1
    assert item["frequency"] == 1
    assert float(item["monetary"]) == 5.0
    assert float(item["total_spend"]) == 5.0
    # Enum serializes to its value (e.g. "Champion")
    assert item["segment_name"] == "Champion"

    app.dependency_overrides.clear()

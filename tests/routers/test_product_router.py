from fastapi.testclient import TestClient
from src.main import app


def test_product_router_no_endpoints():
    # product_router.py is currently empty; ensure requests to product paths return 404
    with TestClient(app) as client:
        r = client.get("/metrics/products")
        assert r.status_code in (404, 405)

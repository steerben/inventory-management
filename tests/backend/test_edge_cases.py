"""
Edge case tests for the backend API.

Covers behavior at boundaries: empty results, invalid input, case sensitivity,
filter combinations that yield nothing, CORS, and idempotency.
"""
import pytest


class TestFilterEdgeCases:
    """Filter behavior at the boundaries."""

    def test_unknown_warehouse_returns_empty_list(self, client):
        """Filtering by a warehouse that doesn't exist returns []."""
        response = client.get("/api/inventory?warehouse=Mars")
        assert response.status_code == 200
        assert response.json() == []

    def test_unknown_category_returns_empty_list(self, client):
        """Filtering by an unknown category returns []."""
        response = client.get("/api/orders?category=Fictional")
        assert response.status_code == 200
        assert response.json() == []

    def test_unknown_status_returns_empty_list(self, client):
        """Filtering by an unknown status returns []."""
        response = client.get("/api/orders?status=Cancelled")
        assert response.status_code == 200
        assert response.json() == []

    def test_warehouse_filter_is_case_sensitive(self, client):
        """Warehouse filter is exact-match (case-sensitive) — pins current behavior."""
        canonical = client.get("/api/inventory?warehouse=San Francisco").json()
        lowercase = client.get("/api/inventory?warehouse=san francisco").json()

        assert len(canonical) > 0
        assert lowercase == [], \
            "warehouse filter is case-sensitive in current implementation"

    def test_category_filter_is_case_insensitive(self, client):
        """Category filter normalizes to lowercase — pins current behavior."""
        cap = client.get("/api/inventory?category=Circuit Boards").json()
        low = client.get("/api/inventory?category=circuit boards").json()
        upper = client.get("/api/inventory?category=CIRCUIT BOARDS").json()

        assert len(cap) > 0
        assert len(cap) == len(low) == len(upper)

    def test_status_filter_is_case_insensitive(self, client):
        """Status filter normalizes to lowercase — pins current behavior."""
        cap = client.get("/api/orders?status=Delivered").json()
        low = client.get("/api/orders?status=delivered").json()

        assert len(cap) > 0
        assert len(cap) == len(low)

    def test_all_filter_equivalent_to_no_filter(self, client):
        """Passing 'all' for every filter is equivalent to passing none."""
        no_filter = client.get("/api/orders").json()
        all_filter = client.get(
            "/api/orders?warehouse=all&category=all&status=all&month=all"
        ).json()
        assert len(no_filter) == len(all_filter)

    def test_invalid_quarter_returns_all_orders(self, client):
        """Invalid quarter codes (Q5-2025) currently fall through — pins behavior."""
        all_orders = client.get("/api/orders").json()
        invalid_q = client.get("/api/orders?month=Q5-2025").json()
        assert len(invalid_q) == len(all_orders), \
            "Invalid quarter Q5-2025 currently no-ops the filter"

    def test_future_month_with_no_orders_returns_empty(self, client):
        """A month with no orders (2099-12) returns an empty list."""
        response = client.get("/api/orders?month=2099-12")
        assert response.status_code == 200
        assert response.json() == []


class TestDashboardEdgeCases:
    """Dashboard summary when filters yield zero items."""

    def test_dashboard_with_unknown_warehouse_returns_zeros(self, client):
        """Dashboard with no matching items returns zero values, not an error."""
        response = client.get("/api/dashboard/summary?warehouse=Mars")
        assert response.status_code == 200
        data = response.json()

        assert data["total_inventory_value"] == 0
        assert data["low_stock_items"] == 0
        assert data["pending_orders"] == 0
        assert data["total_orders_value"] == 0
        # total_backlog_items is global, not filtered — should remain populated
        assert data["total_backlog_items"] >= 0


class TestResourceLookupEdgeCases:
    """Behavior on /resource/{id} for unusual IDs."""

    def test_nonexistent_inventory_id_with_special_chars(self, client):
        """Special chars in ID should still 404 cleanly, not 500."""
        response = client.get("/api/inventory/%20%20")
        assert response.status_code == 404

    def test_nonexistent_order_id_with_long_string(self, client):
        """Very long ID returns 404, not an error."""
        long_id = "x" * 500
        response = client.get(f"/api/orders/{long_id}")
        assert response.status_code == 404


class TestIdempotency:
    """Repeated calls should return identical results."""

    def test_inventory_get_is_idempotent(self, client):
        """Calling /api/inventory twice returns the same data."""
        a = client.get("/api/inventory").json()
        b = client.get("/api/inventory").json()
        assert a == b

    def test_dashboard_summary_is_idempotent(self, client):
        """Dashboard summary is deterministic for same filter set."""
        a = client.get("/api/dashboard/summary?warehouse=Tokyo").json()
        b = client.get("/api/dashboard/summary?warehouse=Tokyo").json()
        assert a == b


class TestCORS:
    """CORS configuration sanity check."""

    def test_cors_allows_browser_origin(self, client):
        """Preflight-style request should include CORS allow-origin header."""
        response = client.get("/api/inventory", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") in ("*", "http://localhost:3000")


class TestLowStockBusinessRule:
    """
    Pin the business rule for what counts as 'low stock'.

    The current dashboard code uses `quantity_on_hand <= reorder_point`
    (at OR below the reorder point counts as low stock).

    There are at least three reasonable interpretations:
      1) `<=`  — at-or-below counts as low (CURRENT behavior).
                  Rationale: hitting the reorder point IS the trigger.
      2) `<`   — strictly below counts as low.
                  Rationale: hitting the reorder point is "just in time", not late.
      3) `<= reorder_point * 1.1` — soft buffer (10% margin).
                  Rationale: account for variability in lead time.

    Pinning this in a test prevents accidental drift if someone "fixes" the
    operator. The user should decide which interpretation reflects the product's
    intent and fill in test_low_stock_boundary_at_reorder_point below.
    """

    def test_low_stock_strictly_below_is_counted(self, client):
        """Items with quantity_on_hand strictly below reorder_point ARE low stock."""
        inventory = client.get("/api/inventory").json()
        strictly_below = [
            item for item in inventory
            if item["quantity_on_hand"] < item["reorder_point"]
        ]
        dashboard = client.get("/api/dashboard/summary").json()
        # low_stock count must include at least the strictly-below set
        assert dashboard["low_stock_items"] >= len(strictly_below)

    def test_low_stock_boundary_at_reorder_point(self, client):
        """
        TODO (user contribution — 5-10 lines):
        Pin the boundary behavior. The current implementation uses `<=`,
        so an item with quantity_on_hand == reorder_point IS counted as low stock.

        Write an assertion that locks in the team's chosen interpretation.
        Suggested approach:
          1. Compute `boundary_items` = items where quantity_on_hand == reorder_point
          2. Compute `below_items` = items where quantity_on_hand < reorder_point
          3. Assert that dashboard['low_stock_items'] equals one of:
             - len(boundary_items) + len(below_items)   # interpretation #1 (current)
             - len(below_items)                          # interpretation #2
             - <your custom formula>                     # interpretation #3
        """
        pytest.skip("Pending user decision: see docstring for the three interpretations.")

"""
Tests for reports API endpoints: /api/reports/quarterly and /api/reports/monthly-trends.

These endpoints had zero coverage before.
"""
import pytest


class TestQuarterlyReports:
    """Test suite for /api/reports/quarterly."""

    def test_get_quarterly_reports(self, client):
        """Test fetching quarterly reports."""
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_quarterly_reports_structure(self, client):
        """Test quarterly report row structure."""
        response = client.get("/api/reports/quarterly")
        data = response.json()

        required = {
            "quarter", "total_orders", "total_revenue",
            "delivered_orders", "avg_order_value", "fulfillment_rate"
        }
        for row in data:
            assert required.issubset(row.keys()), \
                f"Missing fields in quarterly row: {required - row.keys()}"

    def test_quarterly_reports_sorted_by_quarter(self, client):
        """Quarterly results should be sorted by quarter ascending."""
        response = client.get("/api/reports/quarterly")
        data = response.json()

        quarters = [row["quarter"] for row in data]
        assert quarters == sorted(quarters), \
            f"Quarters not sorted: {quarters}"

    def test_quarterly_fulfillment_rate_is_percentage(self, client):
        """Fulfillment rate should be a percentage between 0 and 100."""
        response = client.get("/api/reports/quarterly")
        data = response.json()

        for row in data:
            rate = row["fulfillment_rate"]
            assert 0 <= rate <= 100, \
                f"{row['quarter']}: fulfillment_rate {rate} out of range"

    def test_quarterly_avg_order_value_matches_revenue_div_orders(self, client):
        """avg_order_value should equal total_revenue / total_orders."""
        response = client.get("/api/reports/quarterly")
        data = response.json()

        for row in data:
            if row["total_orders"] > 0:
                expected_avg = row["total_revenue"] / row["total_orders"]
                assert abs(row["avg_order_value"] - expected_avg) < 0.01, \
                    f"{row['quarter']}: avg_order_value mismatch"

    def test_quarterly_delivered_count_not_exceed_total(self, client):
        """delivered_orders cannot exceed total_orders."""
        response = client.get("/api/reports/quarterly")
        data = response.json()

        for row in data:
            assert row["delivered_orders"] <= row["total_orders"], \
                f"{row['quarter']}: delivered ({row['delivered_orders']}) > total ({row['total_orders']})"

    def test_quarterly_reports_with_warehouse_filter(self, client):
        """Quarterly reports should respect warehouse filter."""
        unfiltered = client.get("/api/reports/quarterly").json()
        filtered = client.get("/api/reports/quarterly?warehouse=Tokyo").json()

        unfiltered_revenue = sum(r["total_revenue"] for r in unfiltered)
        filtered_revenue = sum(r["total_revenue"] for r in filtered)
        assert filtered_revenue <= unfiltered_revenue

    def test_quarterly_reports_single_month_filter_yields_one_quarter(self, client):
        """Filtering to month=2025-03 should yield only Q1-2025."""
        response = client.get("/api/reports/quarterly?month=2025-03")
        assert response.status_code == 200
        data = response.json()

        quarters = {row["quarter"] for row in data}
        assert quarters.issubset({"Q1-2025"}), \
            f"Expected only Q1-2025, got {quarters}"


class TestMonthlyTrends:
    """Test suite for /api/reports/monthly-trends."""

    def test_get_monthly_trends(self, client):
        """Test fetching monthly trends."""
        response = client.get("/api/reports/monthly-trends")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_monthly_trends_structure(self, client):
        """Test monthly trends row structure."""
        response = client.get("/api/reports/monthly-trends")
        data = response.json()

        required = {"month", "order_count", "revenue", "delivered_count"}
        for row in data:
            assert required.issubset(row.keys()), \
                f"Missing fields: {required - row.keys()}"

    def test_monthly_trends_sorted_ascending(self, client):
        """Monthly trends should be sorted by month ascending."""
        response = client.get("/api/reports/monthly-trends")
        data = response.json()
        months = [row["month"] for row in data]
        assert months == sorted(months)

    def test_monthly_trends_month_format(self, client):
        """Month strings should be in YYYY-MM format."""
        response = client.get("/api/reports/monthly-trends")
        data = response.json()

        for row in data:
            assert len(row["month"]) == 7
            assert row["month"][4] == "-"
            assert row["month"][:4].isdigit()
            assert row["month"][5:].isdigit()

    def test_monthly_trends_delivered_not_exceed_total(self, client):
        """delivered_count cannot exceed order_count."""
        response = client.get("/api/reports/monthly-trends")
        data = response.json()

        for row in data:
            assert row["delivered_count"] <= row["order_count"]

    def test_monthly_trends_revenue_matches_quarterly_aggregate(self, client):
        """Sum of monthly revenue should equal sum of quarterly revenue (same filters)."""
        monthly = client.get("/api/reports/monthly-trends").json()
        quarterly = client.get("/api/reports/quarterly").json()

        monthly_total = sum(row["revenue"] for row in monthly)
        quarterly_total = sum(row["total_revenue"] for row in quarterly)
        assert abs(monthly_total - quarterly_total) < 0.01, \
            f"Monthly total {monthly_total} != Quarterly total {quarterly_total}"

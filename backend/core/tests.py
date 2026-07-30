from django.test import SimpleTestCase
from django.urls import reverse


class RouteTests(SimpleTestCase):
    def test_dashboard_route_is_registered(self):
        self.assertEqual(reverse("dashboard-summary"), "/api/v1/dashboard/summary/")

    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "net-bank-api"})

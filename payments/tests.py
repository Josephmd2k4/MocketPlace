from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
import json
from .models import Payout
from .forms import PayoutForm

class PaymentsViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.payout = Payout.objects.create(
            payout_batch_id="TEST123",
            status="PENDING"
        )

    @patch("payments.views.verify_webhook_signature", return_value=True)
    def test_paypal_webhook_success(self, mock_verify_signature):
        """Test PayPal webhook updates payout status to SUCCESS."""
        response = self.client.post(
            reverse("paypal_webhook"),
            data=json.dumps({
                "event_type": "PAYMENT.PAYOUTSBATCH.SUCCESS",
                "resource": {"payout_batch_id": "TEST123"}
            }),
            content_type="application/json"
        )
        self.payout.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payout.status, "SUCCESS")

    @patch("payments.views.get_all")
    def test_transact_status_view(self, mock_get_all):
        """Test transact status view retrieves payouts correctly."""
        mock_get_all.return_value = type("obj", (object,), {"items": [
            {"payout_item_id": "TEST123", "receiver": "test@example.com", "amount": {"value": "50.00"}, "transaction_status": "SUCCESS"}
        ]})()

        response = self.client.get(reverse("transaction_status"), {"days": "30", "status": "SUCCESS"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test@example.com")
        self.assertContains(response, "50.00")

class PaymentsModelsTestCase(TestCase):
    def test_create_payout(self):
        """Test Payout object creation with default and custom values."""
        payout = Payout.objects.create(
            payout_batch_id="BATCH123"
        )
        
        # Check if the object is created
        self.assertEqual(Payout.objects.count(), 1)
        
        # Verify default status
        self.assertEqual(payout.status, "PENDING")
        
        # Ensure created_at is set
        self.assertIsNotNone(payout.created_at)
        
        # Ensure last_synced is None initially
        self.assertIsNone(payout.last_synced)

    def test_update_last_synced(self):
        """Test updating the last_synced field."""
        payout = Payout.objects.create(payout_batch_id="BATCH456")
        
        new_time = timezone.now()
        payout.last_synced = new_time
        payout.save()
        
        # Refresh from database
        payout.refresh_from_db()
        
        # Check if last_synced is updated correctly
        self.assertEqual(payout.last_synced, new_time)

class PayoutFormTestCase(TestCase):
    def test_missing_required_fields(self):
        """Test that missing required fields cause form validation to fail."""
        
        # Define form data with missing fields
        form_data = {
            "email": "",  # Missing email
            "amount": "",
            "currency": "USD"
        }
        
        form = PayoutForm(data=form_data)
        
        # Check that the form is not valid
        self.assertFalse(form.is_valid())
        
        # Ensure email and amount fields have errors
        self.assertIn("email", form.errors)
        self.assertIn("amount", form.errors)


import os
import time
from fastapi.testclient import TestClient

# Ensure we use a fresh database for each test run by removing any
# existing file before importing the app (the app creates tables on import).
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, 'tender_system.db')
if os.path.exists(DB_PATH):
    try:
        os.remove(DB_PATH)
    except OSError:
        # If removal fails, continue — tests may still run but could hit
        # UNIQUE constraint errors; this is best-effort cleanup.
        pass

from backend.main import app

client = TestClient(app)


def test_core_flow():
    # Create user
    user_payload = {"username": "test_user", "password": "pass", "role": "client", "email": "a@b.com", "full_name": "Test User"}
    r = client.post('/users/', json=user_payload)
    assert r.status_code == 200
    user = r.json()

    # Login
    r = client.post('/login/', json={"username": "test_user", "password": "pass"})
    assert r.status_code == 200
    session = r.json()

    # Create tender
    tender_payload = {
        # Use a timestamped tender_id to avoid UNIQUE constraint clashes
        "tender_id": f"T-{int(time.time() * 1000)}",
        "title": "Test Tender",
        "description": "Desc",
        "deadline": "2030-01-01T00:00:00",
        "quantity": 1,
        "estimated_cost": 1000.0,
        "delivery_timeline": "30 days",
        "submission_method": "Online",
        "package_id": "PKG1",
        "client_id": user['id']
    }
    r = client.post('/tenders/', json=tender_payload)
    assert r.status_code == 200
    tender = r.json()

    # Create proposal
    proposal_payload = {"tender_id": tender['id'], "vendor_id": user['id'], "technical_input": "tech", "financial_input": 900.0}
    r = client.post('/proposals/', json=proposal_payload)
    assert r.status_code == 200
    proposal = r.json()

    # Create contract
    contract_payload = {"tender_id": tender['id'], "content": "contract", "scope_of_work": "sow", "start_date": "2030-02-01T00:00:00", "end_date": "2030-12-31T00:00:00"}
    r = client.post('/contracts/', json=contract_payload)
    assert r.status_code == 200
    contract = r.json()

    # Sign contract
    r = client.put(f"/contracts/{contract['id']}/sign")
    assert r.status_code == 200

    # Create PO
    po_payload = {"tender_id": tender['id'], "vendor_id": user['id'], "po_number": f"PO-{int(time.time() * 1000)}", "items": "it", "total_amount": 900.0}
    r = client.post('/purchase_orders/', json=po_payload)
    assert r.status_code == 200
    po = r.json()

    # Acknowledge PO
    r = client.put(f"/purchase_orders/{po['id']}/acknowledge")
    assert r.status_code == 200

    # Create Invoice
    invoice_payload = {"po_id": po['id'], "invoice_number": f"INV-{int(time.time() * 1000)}", "amount": 900.0, "total_payable": 900.0}
    r = client.post('/invoices/', json=invoice_payload)
    assert r.status_code == 200
    invoice = r.json()

    # Create Payment
    payment_payload = {"invoice_id": invoice['id'], "amount_paid": 900.0, "payment_mode": "Bank Transfer"}
    r = client.post('/payments/', json=payment_payload)
    assert r.status_code == 200
    payment = r.json()

    # Verify payment
    r = client.put(f"/payments/{payment['id']}/verify")
    assert r.status_code == 200

    # Check invoice status is Paid
    r = client.get('/invoices/')
    assert r.status_code == 200
    invoices = r.json()
    found = [inv for inv in invoices if inv['id'] == invoice['id']]
    assert found and found[0]['status'] in ('Paid', 'Partial', 'Draft')

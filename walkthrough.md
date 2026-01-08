1.  **Launch the App**:
    *   **Step 1**: Run `pip install files aiofiles` (if not already installed).
    *   **Step 2**: Run `python -m backend.main`.
    *   **Step 3**: Open your browser to `http://localhost:8000`.
2.  **Login**: Use the "Quick Login" buttons (e.g., Admin).
3.  **Tender Management**: Navigate to "Tenders" to see the list.
4.  **Contracting** (Fixed):
    *   Go to **Contracts**.
    *   Select a Tender from the dropdown.
    *   Click "Dispatch Contract".
5.  **Delivery & Inspection** (Fixed):
    *   Go to **Delivery**.
    *   Select your Project/Tender.
    *   **Vendor**: Click "Upload" (Simulated).
    *   **Client**: Click "Inspect" (Simulated).
6.  **Payments & Finance** (Fixed):
    *   Go to **Payments**.
    *   Select an Invoice.
    *   Input amount.
    *   Click "Process Payment" (Auto-calculates 10% commission).

## Technical Notes
- **Database Upgraded**: New columns (`inspection_status`, `commission_amount`, etc.) were automatically added to `tender_system.db`.
- **Codebase**: `frontend/lifecycle_views.py` was significantly refactored to enable these features.

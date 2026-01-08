# Comprehensive User Journey Testing Guide

Follow these steps to verify the system across all roles. **Important**: Restart your server before testing.

## 1. Setup Data (Admin)
1.  **Login as `admin`** / `admin`.
2.  **Tenders**: Click "Add", fill details (Title: "Food Supply 2026", Budget: 100000), and **Save**.
3.  **Items**: (If needed for Orders) Verify items exist or add them in the Item Master (if implemented, otherwise use pre-seeded).

## 2. Vendor Journey (The Bidder)
1.  **Register** a new account with role **Vendor** (e.g., `v_smith`).
2.  **Login** as `v_smith`.
3.  **Dashboard**: Verify you see "Active Tenders" tile but **not** "Purchase Orders" tile (if restricted).
4.  **Tenders**: Verify you can see the "Food Supply 2026".
5.  **Contracts**: Verify the "Active Contracts" list is empty or shows "Pending" for you.

## 3. Technical Journey (The Inspector)
1.  **Login as `technical`** / `technical`.
2.  **Dashboard**: Verify you see "Active Tenders" and "Delivery" tiles.
3.  **Delivery**: 
    - Select "Project #1" (the one you created as Admin).
    - If milestones exist, they should stay "Pending".
    - *Note: Return to this step after the Vendor uploads proof.*

## 4. Finance Journey (The Payer)
1.  **Login as `finance`** / `finance`.
2.  **Dashboard**: Verify you see "Purchase Orders" and "Pending Bills" tiles.
3.  **Orders**: Select a Tender, add line items with the **Combo Box**, verify **Subtotal/Tax/Grand Total**, and click **Create Order**.
4.  **Payments**: Select an Invoice and click **Process** to record a payment. Verify it appears in the "Transaction History".

## 5. End-to-End Delivery Sync
1.  **Vendor (v_smith)**: Go to **Delivery**, select the project, and click **Upload Proof** for a milestone.
2.  **Technical**: Go to **Delivery**, select the project, click **Inspect** on that milestone. Select "Passed" and add remarks.
3.  **Admin**: Verify the milestone status is updated to **Completed** with remarks visible.

## 6. Security (Check Relevant Sections)
- Verify `finance` user **cannot** see the "Tenders" section.
- Verify `technical` user **cannot** see the "Payments" section.
- Verify `vendor` **cannot** click "Inspect" on milestones.

# System Analysis & Gap Report (Updated)

## 1. Documentation vs. Codebase Alignment
**Status**: `Report.md` vs `Codebase`
The report outlines a **General Order Supplies System** with 5 primary actors: Admin, Sales, Finance, Vendor, and Client.

### **Use Case 1: Identify & Monitor Tenders (Admin)**
*   **Requirement**: Admin monitors portals, identifies tenders.
*   **Codebase**: `TenderListView` exists.
*   **Gap**: No "monitoring" logic (e.g., scraping or external feeds). It's purely manual entry.
*   **Severity**: Low (Manual entry is acceptable MVP).

### **Use Case 2: Prepare & Submit Proposal (Admin/Sales)**
*   **Requirement**: Admin collects docs; Sales provides technical/pricing input.
*   **Codebase**: `Proposal` model exists. `TechnicalEvaluationView` exists.
*   **Gap**: The flow is disjointed. `TechnicalEvaluationView` allows scoring but arguably "preparing" a proposal should be a distinct step before evaluation.
*   **Critical Gap**: `Proposal` creation doesn't explicitly involve Sales providing inputs in a dedicated view; it's often combined or missing.

### **Use Case 3: Contract & Work Details (Admin/Sales)**
*   **Requirement**: Admin prepares contract; Sales forwards work details.
*   **Codebase**: `ContractManagementView` exists but is **broken**.
*   **Critical Bug**: Contract creation creates "orphan" records (`tender_id=0`). It does not link to the awarded Tender or Proposal.
*   **Gap**: "Forwarding work details" (Work Order generation) is partially handled by `ContractManagementView` but lacks a dedicated "Work Order" artifact distinct from the Contract.

### **Use Case 4: Delivery & Inspection (Sales/Vendor/Client)**
*   **Requirement**: Vendor delivers; Client inspects/signs challan; Vendor conducts quality checks.
*   **Codebase**: `DeliveryMilestoneView` exists but is **empty/hardcoded**.
*   **Critical Bug**: The view has `data = []`. No mechanism to record Delivery Challans or Inspection Notes.
*   **Gap**: No "Quality Check" or "Inspection" status fields in the `Milestone` or `Delivery` models (only basic `status`).

### **Use Case 5: Billing & Payment (Finance/Sales)**
*   **Requirement**: Finance prepares invoices; Sales submits final docs; Finance records payment; Sales receives profit (commission).
*   **Codebase**: `run_app.bat` launches a Finance Dashboard. `BillingInvoiceView` and `PaymentManagementView` exist.
*   **Critical Bug**: Invoices and Payments generate fake client-side IDs (`INV-random`, `TID-random`).
*   **Gap**: No field for "Commission" or "Profit" tracking for Sales department as requested in "Receive payment profit" use case.

## 2. Technical Quality & Principles
*   **Hardcoded Values**: `tax_amount` defaults to 18% in UI.
*   **Data Integrity**:
    *   `vendor_id` often defaults to `_vendors[0]` (first independent vendor in list) rather than the vendor associated with the specific Tender.
    *   No transactional atomicity (if `create_payment` fails, invoice status might still update in UI logic if not careful, though backend seems okay).
*   **Missing Interfaces**:
    *   No interface for **Sales Dept** to input "Pricing Input" separate from Admin's proposal capability.
    *   No interface for **Quality Checks** (Use Case: "Conduct quality checks").

## 3. Action Plan for Full Alignment
1.  **Refactor Contract Creation**: Enforce valid `tender_id` and `vendor_id` selection (linked to Winning Proposal).
2.  **Implement Delivery Module**: backend `GET /deliveries` and frontend table to manage Delivery Challans and Inspection status.
3.  **Fix Finance Data Integrity**: Move ID generation to backend. Link Invoices to specific POs and Tenders. Add "Commission/Profit" field to Payment/Invoice models.
4.  **Add "Quality/Inspection" Workflow**: Add `inspection_status` and `quality_remarks` to `Milestone`/`Delivery` models and update UI to allow Client/Vendor to update these.

## 4. Immediate Next Steps
*   **Fix Critical Bugs**: Contract `tender_id=0` and Delivery View `data=[]`.
*   **Align Usecases**: Add specific fields/views for "Quality Check" and "Profit Recording".

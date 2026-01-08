# System Enhancement Checklist

## 1. Foundation & Styles
- [x] **CSS Upgrade**: Implement "Windows 8" Tile styles and "Professional" color palette.
- [x] **Components**: Create standard CSS/HTML for:
    - [x] CRUD Toolbar (Add, Edit, Delete, Save, Cancel, Search, Help, Refresh).
    - [x] Navigation Bar (First, Prev, Next, Last).
    - [x] Transaction Grid (Table with input rows).
    - [x] Status/Feedback Bar.

## 2. Authentication & User Management
- [x] **Registration**: Form with Role Selection & **Image Upload** (Participant Image).
- [x] **Login**: Existing logic.

## 3. Dashboard (Windows 8 Style)
- [x] Implement Dynamic Tiles (Count of Tenders, Pending Actions, Revenue).
- [x] Role-based Tile visibility.

## 4. Tender Management (Single Interface)
- [x] **UI**: Form with all fields + **Image Placeholder** (3 marks).
- [x] **CRUD Logic**: Implement Add, Edit, Delete, Save, Cancel.
- [x] **Nav Logic**: Implement First/Prev/Next/Last traversal.
- [x] **Search**: Simple filter implementation (Mocked).

## 5. Order Generation (Transactional Interface)
- [x] **Data Model**: Create `Item` entity (Product Master) for Combo Box source.
- [x] **Master-Detail Layout**: Header (PO Details) + **Grid** (Items).
- [x] **Grid Features**:
    - [x] **Combo Box** in Item Column (loading from Item Master) (3 marks).
    - [x] Auto-calculation (Qty * Rate = Amount).
    - [x] **Totals**: Subtotal, Tax, Grand Total.
- [x] **Backend**: Handle JSON storage of line items.

## 5. Process & Flows
- [x] **Create Tender Modal**: Replace alert with working form.
- [x] **Delivery Section**:
    - [x] Grid View of Milestones.
    - [x] Upload/Inspect actions updating status real-time.

## 6. Reports
- [ ] **Transaction Report**: Printable view of the PO/Invoice with totals.

## 7. Documentation
- [x] **User Journey**: `user_journey.md` for testing.

## 8. Bug Fixes & Refinement
- [x] **Script Load Order**: Fixed `defer` issues in `dashboard.html`.
- [x] **Cache Busting**: Added versioning to static assets.
- [x] **Error Handling**: Improved registration/upload error reporting.

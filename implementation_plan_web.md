# Web Frontend Migration Plan

## Goal
Replace the desktop UI (PySide6) with a responsive, modern Web UI (HTML/CSS/JS) to improve stability and performance.

## Strategy
We will serve static files directly from the FastAPI backend. This avoids CORS issues and simplifies "installation" (just run the backend).

## Proposed Architecture
- **Backend API**: Existing `backend/main.py` (Unchanged logic, just adding file serving).
- **Frontend**:
    - `backend/static/index.html`: Login Page.
    - `backend/static/dashboard.html`: Main Dashboard (SPA-like navigation).
    - `backend/static/css/main.css`: Modern styling (Flexbox/Grid, clean aesthetics).
    - `backend/static/css/metro.css`: Windows 8 / Metro style definitions.
    - `backend/static/js/components.js`: CRUD Toolbar, Grid, Nav logic.
    - `backend/static/js/app.js`: Enhanced logic.

## Implementation Steps

### 1. Foundation & Components
- [ ] **CSS**: Create `metro.css` for tiles and `toolbar` classes.
- [ ] **Components**: Implement `renderToolbar(actions)` and `renderGrid(headers, rows)`.
- [ ] **Navigation**: Implement `navFirst()`, `navPrev()`, `navNext()`, `navLast()` logic in `api.js`.

### 2. Tender Module (Single Interface)
- [ ] **View**: Form with Image Placeholder (3 marks).
- [ ] **Toolbar**: Add, Edit, Delete, Save, Cancel, Search, Help.
- [ ] **Logic**: Full CRUD against `/tenders/` endpoint.

### 3. Order Module (Transactional Interface)
- [ ] **View**: Master-Detail (Header + Items Grid).
- [ ] **Grid**:
    - [ ] Combo Box for Item Selection (3 marks).
    - [ ] Qty, Rate, Amount (Auto-calc).
    - [ ] Add/Remove Row buttons.
- [ ] **Totals**: Subtotal, Tax (18%), Grand Total.
- [ ] **Backend**: Allow saving JSON `items` string.

### 4. Dashboards (Windows 8 Style)
- [ ] **Layout**: Grid of colorful tiles (Metro UI).
- [ ] **Dynamic Data**: Fetch real counts/amounts.

### 5. Delivery & Reporting
- [ ] **Delivery**: Grid view of milestones with "Upload"/"Inspect" buttons.
- [ ] **Reporting**: "Printable" view for POs.

## Verification
- Run `python -m backend.main`.
- Open `http://localhost:8000` in browser.
- Test End-to-End flow.

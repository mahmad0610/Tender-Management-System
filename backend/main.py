from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import os
from . import models, schemas, database
from .database import engine, get_db
from .upgrade_db import ensure_db_schema

# Create any missing tables first. Note: SQLAlchemy won't alter existing tables
# to add columns in SQLite; we'll run a small ensure_db_schema step after
# tables exist to add any missing columns (safe ADD COLUMN operations).
models.Base.metadata.create_all(bind=engine)

# Ensure simple DB schema fixes (add missing columns) after SQLAlchemy create_all
try:
    ensure_db_schema()
except Exception as e:
    # Print but do not stop startup; if migration fails the explicit error will
    # still show when a query referencing the missing column runs.
    print("DB schema ensure step failed:", e)

app = FastAPI(title="Tender Procurement System API")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve static files (HTML, CSS, JS)
static_path = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/dashboard")
async def dashboard():
    return FileResponse(os.path.join(static_path, "dashboard.html"))


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/users/", response_model=schemas.UserSchema)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # If the username already exists, return the existing user (idempotent)
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        return existing

    db_user = models.User(
        username=user.username, 
        password=user.password, 
        role=user.role, 
        email=user.email,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.UserSchema])
def get_users(role: str = None, db: Session = Depends(get_db)):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.all()

@app.post("/login/")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user.id, "username": user.username, "role": user.role, "full_name": user.full_name}

# Tender Endpoints
@app.post("/tenders/", response_model=schemas.TenderSchema)
def create_tender(tender: schemas.TenderCreate, db: Session = Depends(get_db)):
    db_tender = models.Tender(**tender.dict())
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    return db_tender

@app.get("/tenders/", response_model=List[schemas.TenderSchema])
def get_tenders(db: Session = Depends(get_db)):
    return db.query(models.Tender).all()

@app.get("/tenders/{tender_id}", response_model=schemas.TenderSchema)
def get_tender(tender_id: int, db: Session = Depends(get_db)):
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender

@app.put("/tenders/{tender_id}/status")
def update_tender_status(tender_id: int, status: models.TenderStatus, db: Session = Depends(get_db)):
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if not tender: raise HTTPException(404)
    tender.status = status
    db.commit()
    return {"message": "Tender status updated"}

# Proposal Endpoints
@app.post("/proposals/", response_model=schemas.ProposalSchema)
def create_proposal(proposal: schemas.ProposalCreate, db: Session = Depends(get_db)):
    db_proposal = models.Proposal(**proposal.dict())
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

@app.get("/proposals/", response_model=List[schemas.ProposalSchema])
def get_all_proposals(db: Session = Depends(get_db)):
    return db.query(models.Proposal).all()

@app.put("/proposals/{proposal_id}", response_model=schemas.ProposalSchema)
def update_proposal(proposal_id: int, update: schemas.ProposalUpdate, db: Session = Depends(get_db)):
    db_proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not db_proposal: raise HTTPException(404)
    for key, value in update.dict(exclude_unset=True).items():
        setattr(db_proposal, key, value)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

# Contract Endpoints
@app.post("/contracts/", response_model=schemas.ContractSchema)
def create_contract(contract: schemas.ContractCreate, db: Session = Depends(get_db)):
    db_contract = models.Contract(**contract.dict())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@app.get("/contracts/", response_model=List[schemas.ContractSchema])
def get_contracts(db: Session = Depends(get_db)):
    return db.query(models.Contract).all()


@app.put('/contracts/{contract_id}/sign')
def sign_contract(contract_id: int, signer: Optional[str] = None, db: Session = Depends(get_db)):
    c = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not c:
        raise HTTPException(404, 'Contract not found')
    c.status = 'Signed'
    c.signed_date = datetime.utcnow()
    db.commit()
    return {"message": "Contract signed", "contract_id": contract_id}


# Purchase Order Endpoints
@app.post("/purchase_orders/", response_model=schemas.POSchema)
def create_po(po: schemas.POCreate, db: Session = Depends(get_db)):
    po_data = po.dict()
    if not po_data.get('po_number'):
        import uuid
        po_data['po_number'] = f"PO-{str(uuid.uuid4())[:8].upper()}"
        
    db_po = models.PurchaseOrder(**po_data)
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po

@app.get("/purchase_orders/", response_model=List[schemas.POSchema])
def get_pos(db: Session = Depends(get_db)):
    return db.query(models.PurchaseOrder).all()


@app.put('/purchase_orders/{po_id}/acknowledge')
def acknowledge_po(po_id: int, db: Session = Depends(get_db)):
    po = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, 'PO not found')
    po.acknowledged = 1
    db.commit()
    return {"message": "PO acknowledged", "po_id": po_id}

# Invoice Endpoints
@app.post("/invoices/", response_model=schemas.InvoiceSchema)
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    inv_data = invoice.dict()
    if not inv_data.get('invoice_number'):
        import uuid
        inv_data['invoice_number'] = f"INV-{str(uuid.uuid4())[:8].upper()}"
        
    db_invoice = models.Invoice(**inv_data)
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@app.get('/invoices/', response_model=List[schemas.InvoiceSchema])
def list_invoices(db: Session = Depends(get_db)):
    return db.query(models.Invoice).all()

# Payment Endpoints
@app.post("/payments/", response_model=schemas.PaymentSchema)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    pay_data = payment.dict()
    if not pay_data.get('transaction_id'):
        import uuid
        pay_data['transaction_id'] = f"TXN-{str(uuid.uuid4())[:8].upper()}"
        
    db_payment = models.Payment(**pay_data)
    db.add(db_payment)
    # Update invoice status if fully paid (simple logic for now)
    invoice = db.query(models.Invoice).filter(models.Invoice.id == payment.invoice_id).first()
    if invoice:
        invoice.status = "Partial"
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.get("/payments/", response_model=List[schemas.PaymentSchema])
def get_payments(db: Session = Depends(get_db)):
    return db.query(models.Payment).all()

@app.put("/payments/{payment_id}/verify")
def verify_payment(payment_id: int, completion_date: Optional[datetime] = None, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment: raise HTTPException(404)
    payment.status = "Verified"
    payment.completion_date = completion_date or datetime.utcnow()
    
    # If verified, mark invoice as paid
    invoice = db.query(models.Invoice).filter(models.Invoice.id == payment.invoice_id).first()
    if invoice:
        invoice.status = "Paid"
    db.commit()
    return {"message": "Payment verified and completed"}

# Milestone Endpoints
@app.post("/milestones/", response_model=schemas.MilestoneSchema)
def create_milestone(milestone: schemas.MilestoneCreate, db: Session = Depends(get_db)):
    db_milestone = models.Milestone(**milestone.dict())
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

@app.get("/tenders/{tender_id}/milestones", response_model=List[schemas.MilestoneSchema])
def get_milestones(tender_id: int, db: Session = Depends(get_db)):
    return db.query(models.Milestone).filter(models.Milestone.tender_id == tender_id).all()


@app.put("/milestones/{milestone_id}", response_model=schemas.MilestoneSchema)
def update_milestone(milestone_id: int, update: schemas.MilestoneCreate, db: Session = Depends(get_db)):
    m = db.query(models.Milestone).filter(models.Milestone.id == milestone_id).first()
    if not m:
        raise HTTPException(404, "Milestone not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m


import shutil

@app.post('/upload/')
def upload_file(file: UploadFile = File(...)):
    """Uploads file to backend/static/uploads/ and returns relative URL."""
    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    os.makedirs(static_dir, exist_ok=True)
    
    file_path = os.path.join(static_dir, file.filename)
    with open(file_path, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/static/uploads/{file.filename}"}

@app.post("/register/", response_model=schemas.UserSchema)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = models.User(
        username=user.username,
        password=user.password, # In real app, hash this!
        role=user.role,
        email=user.email,
        full_name=user.full_name,
        profile_image=user.profile_image
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/items/", response_model=schemas.ItemSchema)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[schemas.ItemSchema])
def read_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

# Workflow & Tracking Endpoints (UC 9-10)
@app.post("/workflows/", response_model=schemas.WorkflowSchema)
def create_workflow(workflow: schemas.WorkflowBase, db: Session = Depends(get_db)):
    db_wf = models.ApprovalWorkflow(**workflow.dict())
    db.add(db_wf)
    db.commit()
    db.refresh(db_wf)
    return db_wf

@app.get("/workflows/{entity_type}/{entity_id}", response_model=schemas.WorkflowSchema)
def get_workflow(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    wf = db.query(models.ApprovalWorkflow).filter(
        models.ApprovalWorkflow.entity_type == entity_type,
        models.ApprovalWorkflow.entity_id == entity_id
    ).first()
    if not wf: raise HTTPException(404)
    return wf

@app.put("/workflows/{wf_id}")
def update_workflow(wf_id: int, next_step: str, status: str, db: Session = Depends(get_db)):
    wf = db.query(models.ApprovalWorkflow).filter(models.ApprovalWorkflow.id == wf_id).first()
    if not wf: raise HTTPException(404)
    wf.next_step = next_step
    wf.status = status
    db.commit()
    return {"message": "Workflow updated"}


# Audit logs endpoints
@app.post('/audit_logs/')
def create_audit_log(log: dict, db: Session = Depends(get_db)):
    # minimal implementation: expect keys user_id, action, entity_type, entity_id
    al = models.AuditLog(
        user_id=log.get('user_id'), action=log.get('action'), entity_type=log.get('entity_type'), entity_id=log.get('entity_id')
    )
    db.add(al)
    db.commit()
    db.refresh(al)
    return al


@app.get('/audit_logs/')
def list_audit_logs(db: Session = Depends(get_db)):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(100).all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

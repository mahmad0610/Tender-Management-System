from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum
from .database import Base
import datetime

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TECHNICAL = "technical"
    CLIENT = "client"
    VENDOR = "vendor"
    FINANCE = "finance"

class TenderStatus(str, enum.Enum):
    OPEN = "open"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    TECHNICAL_REVIEW = "technical_review"
    FINANCIAL_REVIEW = "financial_review"
    CLIENT_APPROVAL_PENDING = "client_approval_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONTRACT_SIGNED = "contract_signed"
    COMPLETED = "completed"
    CLOSED = "closed"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum(UserRole))
    email = Column(String)
    full_name = Column(String)
    profile_image = Column(String, nullable=True) # Uploaded image URL

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    unit = Column(String) # kg, ltr, pcs
    rate = Column(Float, default=0.0)
    description = Column(String)
    image_url = Column(String, nullable=True)

class Tender(Base):
    __tablename__ = "tenders"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    deadline = Column(DateTime)
    status = Column(Enum(TenderStatus), default=TenderStatus.OPEN)
    budget = Column(Float, default=0.0)
    quantity = Column(Integer, default=1)
    estimated_cost = Column(Float, default=0.0)
    delivery_timeline = Column(String) # e.g., "30 days"
    submission_method = Column(String) # e.g., "Online", "Manual"
    package_id = Column(String) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    client_id = Column(Integer, ForeignKey("users.id"))
    
    proposals = relationship("Proposal", back_populates="tender")
    contracts = relationship("Contract", back_populates="tender")
    purchase_orders = relationship("PurchaseOrder", back_populates="tender")

class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    vendor_id = Column(Integer, ForeignKey("users.id"))
    
    technical_input = Column(Text)
    technical_score = Column(Float, default=0.0)
    technical_remarks = Column(Text)
    
    financial_input = Column(Float) # Total cost proposed
    financial_remarks = Column(Text)
    margin_analysis = Column(Text)
    
    document_url = Column(String) # For simplicity, path to file
    
    version = Column(Integer, default=1)
    status = Column(String, default="Submitted") # Submitted, Under Review, Shortlisted, Approved, Rejected
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    integration_id = Column(String)
    feedback = Column(Text) 
    
    tender = relationship("Tender", back_populates="proposals")

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    content = Column(Text)
    scope_of_work = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String, default="Draft") # Draft, Signed, Active, Expired
    vetting_status = Column(String, default="Pending") # Pending, Vetted, Rejected 
    dispatch_id = Column(String)
    signed_date = Column(DateTime)
    
    tender = relationship("Tender", back_populates="contracts")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    vendor_id = Column(Integer, ForeignKey("users.id"))
    items = Column(Text) 
    total_amount = Column(Float)
    status = Column(String, default="Created") # Created, Confirmed, Completed
    approved_by = Column(String) # Finance/Technical User
    acknowledged = Column(Integer, default=0) # 0: No, 1:
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tender = relationship("Tender", back_populates="purchase_orders")
    invoices = relationship("Invoice", back_populates="purchase_order")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    amount = Column(Float)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_payable = Column(Float)
    status = Column(String, default="Draft") # Draft, Issued, Pending, Partial, Paid
    issuance_id = Column(String) #
    audit_flag = Column(Integer, default=0) 
    verification_date = Column(DateTime) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    purchase_order = relationship("PurchaseOrder", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    amount_paid = Column(Float)
    payment_mode = Column(String) # Bank Transfer, Cheque, Online
    transaction_id = Column(String)
    transfer_id = Column(String) # 
    proof_id = Column(String) 
    payment_date = Column(DateTime, default=datetime.datetime.utcnow)
    completion_date = Column(DateTime)
    commission_amount = Column(Float, default=0.0) # Profit/Commission for Sales Dept
    status = Column(String, default="Pending") # Pending, Verified, Failed
    
    invoice = relationship("Invoice", back_populates="payments")

class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="Pending") # Pending, In Progress, Completed
    proof_url = Column(String)
    delivery_id = Column(String) 
    note_id = Column(String) 
    transmission_id = Column(String)
    transmission_method = Column(String)
    
    # New fields for UC conformance
    inspection_status = Column(String, default="Pending") # Pending, Passed, Failed
    quality_remarks = Column(Text)
    signed_challan_id = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String) # Tender, Proposal, Invoice, etc.
    entity_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, index=True)
    entity_type = Column(String) # Proposal, Tender
    entity_id = Column(Integer)
    status = Column(String)
    next_step = Column(String) 
    response_time = Column(Float) 
    notification_sent = Column(Integer, default=0) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


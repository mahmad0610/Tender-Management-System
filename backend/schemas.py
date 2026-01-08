from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from .models import UserRole, TenderStatus

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    profile_image: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserSchema(UserBase):
    id: int
    class Config:
        orm_mode = True

class ItemBase(BaseModel):
    name: str
    unit: str
    rate: float
    description: Optional[str] = None
    image_url: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemSchema(ItemBase):
    id: int
    class Config:
        orm_mode = True

class TenderBase(BaseModel):
    title: str
    description: str
    budget: float
    deadline: date
    status: str = "open"
    image_url: Optional[str] = None # Added for placeholder1
    estimated_cost: float = 0.0
    delivery_timeline: str
    submission_method: Optional[str] = None
    package_id: Optional[str] = None

class TenderCreate(TenderBase):
    tender_id: str
    client_id: int
    
class TenderSchema(TenderBase):
    id: int
    tender_id: str
    status: TenderStatus
    created_at: datetime
    class Config:
        from_attributes = True

class ProposalBase(BaseModel):
    tender_id: int
    vendor_id: int
    technical_input: str
    financial_input: float
    document_url: Optional[str] = None
    integration_id: Optional[str] = None
    feedback: Optional[str] = None

class ProposalCreate(ProposalBase):
    pass

class ProposalUpdate(BaseModel):
    technical_score: Optional[float] = None
    technical_remarks: Optional[str] = None
    financial_remarks: Optional[str] = None
    margin_analysis: Optional[str] = None
    status: Optional[str] = None

class ProposalSchema(ProposalBase):
    id: int
    status: str
    version: int
    technical_score: float
    technical_remarks: Optional[str]
    financial_remarks: Optional[str]
    margin_analysis: Optional[str]
    integration_id: Optional[str]
    feedback: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class ContractBase(BaseModel):
    tender_id: int
    content: str
    scope_of_work: str
    start_date: datetime
    end_date: datetime
    status: str = "Draft"
    vetting_status: str = "Pending"
    dispatch_id: Optional[str] = None

class ContractCreate(ContractBase):
    pass

class ContractSchema(ContractBase):
    id: int
    vetting_status: str
    dispatch_id: Optional[str]
    signed_date: Optional[datetime]
    class Config:
        from_attributes = True

class POBase(BaseModel):
    tender_id: int
    vendor_id: int
    po_number: str
    items: str
    total_amount: float
    status: str = "Created"
    approved_by: Optional[str] = None
    acknowledged: int = 0

class POCreate(POBase):
    po_number: Optional[str] = None

class POSchema(POBase):
    id: int
    approved_by: Optional[str]
    acknowledged: int
    created_at: datetime
    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    po_id: int
    invoice_number: Optional[str] = None # Made optional for base, or keep mandatory in Read?
    amount: float
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    total_payable: float
    issuance_id: Optional[str] = None
    audit_flag: int = 0
    verification_date: Optional[datetime] = None

class InvoiceCreate(InvoiceBase):
    invoice_number: Optional[str] = None

class InvoiceSchema(InvoiceBase):
    id: int
    invoice_number: str # Mandatory in read
    status: str
    issuance_id: Optional[str]
    audit_flag: int
    verification_date: Optional[datetime]
    created_at: datetime
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    invoice_id: int
    amount_paid: float
    payment_mode: str
    transaction_id: Optional[str] = None
    commission_amount: float = 0.0

class PaymentCreate(PaymentBase):
    pass

class PaymentSchema(PaymentBase):
    id: int
    payment_date: datetime
    status: str
    class Config:
        from_attributes = True

class MilestoneBase(BaseModel):
    tender_id: int
    title: str
    description: str
    status: str = "Pending"
    delivery_id: Optional[str] = None
    note_id: Optional[str] = None
    transmission_id: Optional[str] = None
    transmission_method: Optional[str] = None
    inspection_status: str = "Pending"
    quality_remarks: Optional[str] = None
    signed_challan_id: Optional[str] = None

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneSchema(MilestoneBase):
    id: int
    completion_date: Optional[datetime]
    proof_url: Optional[str]
    delivery_id: Optional[str]
    note_id: Optional[str]
    transmission_id: Optional[str]
    transmission_method: Optional[str]
    class Config:
        from_attributes = True

class WorkflowBase(BaseModel):
    workflow_id: str
    entity_type: str
    entity_id: int
    status: str
    next_step: Optional[str]
    response_time: Optional[float]
    notification_sent: int = 0

class WorkflowSchema(WorkflowBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str


from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import PaymentType, TransactionStatus


# ---------- Endpoint 1: contracts ----------
class ContractCreate(BaseModel):
    engineer_name: str = Field(min_length=1, max_length=120)
    client_name: str = Field(min_length=1, max_length=200)
    project_location: str = Field(min_length=1, max_length=200)
    milestone_title: str = Field(min_length=1, max_length=200)
    milestone_budget_ugx: int = Field(gt=0)

    @field_validator("project_location")
    @classmethod
    def location_must_be_luweero(cls, v: str) -> str:
        if "luweero" not in v.lower():
            raise ValueError('project_location must contain the word "Luweero"')
        return v


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    engineer_name: str
    client_name: str
    project_location: str
    milestone_title: str
    milestone_budget_ugx: int
    status: str
    created_at: datetime


# ---------- Endpoint 2: store orders ----------
class OrderItemIn(BaseModel):
    product_id: int
    product_name: str = Field(min_length=1, max_length=200)
    quantity: int = Field(gt=0)
    unit_price_ugx: int = Field(gt=0)


class OrderCreate(BaseModel):
    contractor_id: int
    delivery_site_location: str = Field(min_length=1, max_length=200)
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    quantity: int
    unit_price_ugx: int
    line_total_ugx: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contractor_id: int
    delivery_site_location: str
    total_ugx: int
    status: str
    created_at: datetime
    items: list[OrderItemOut]


# ---------- Endpoint 3: webhook ----------
class WebhookPayload(BaseModel):
    transaction_reference: str = Field(min_length=1, max_length=100)
    payment_type: PaymentType
    reference_id: int
    transaction_status: TransactionStatus


class WebhookResult(BaseModel):
    received: bool = True
    transaction_reference: str
    payment_type: str
    reference_id: int
    new_status: str | None = None
    detail: str


# ---------- Endpoint 4: profile ----------
class UserProfileOut(BaseModel):
    user_id: int
    name: str
    role: str
    is_identity_verified_by_laboremus: bool
    is_credentials_verified_by_verify_ug: bool
    cloud_storage_blueprint_url: str | None

from pydantic import BaseModel


class CreateOrderIn(BaseModel):
    product_id: str


class CreateOrderOut(BaseModel):
    order_id: str
    amount: int  # paise
    currency: str
    key_id: str


class VerifyIn(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class VerifyOut(BaseModel):
    verified: bool

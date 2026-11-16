import razorpay
from razorpay.errors import SignatureVerificationError

from app.config import settings

client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def create_order(amount_inr: int, receipt: str, notes: dict) -> dict:
    return client.order.create(
        {
            "amount": amount_inr * 100,  # paise
            "currency": "INR",
            "receipt": receipt,
            "notes": notes,
        }
    )


def verify_payment(order_id: str, payment_id: str, signature: str) -> bool:
    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
        return True
    except SignatureVerificationError:
        return False


def verify_webhook(raw_body: str, signature: str) -> bool:
    try:
        client.utility.verify_webhook_signature(
            raw_body, signature, settings.razorpay_webhook_secret
        )
        return True
    except SignatureVerificationError:
        return False

import json
import logging
import uuid

from fastapi import APIRouter, Header, HTTPException, Request

from app import database as db
from app.catalog import PRODUCTS
from app.config import settings
from app.schemas import CreateOrderIn, CreateOrderOut, VerifyIn, VerifyOut
from app.services import razorpay_service as rzp

router = APIRouter(prefix="/api/payments", tags=["payments"])
log = logging.getLogger("payments")


@router.post("/orders", response_model=CreateOrderOut)
def create_order(body: CreateOrderIn):
    product = PRODUCTS.get(body.product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    receipt = f"rcpt_{uuid.uuid4().hex[:12]}"
    order = rzp.create_order(
        product["price"],
        receipt=receipt,
        notes={"product_id": product["id"]},
    )

    # DB me order save karo (status=created)
    db.save_order(
        order_id=order["id"],
        product_id=product["id"],
        amount=order["amount"],
        currency=order["currency"],
        receipt=receipt,
        status="created",
    )

    return CreateOrderOut(
        order_id=order["id"],
        amount=order["amount"],
        currency=order["currency"],
        key_id=settings.razorpay_key_id,  # public key, frontend ke liye safe
    )


@router.post("/verify", response_model=VerifyOut)
def verify(body: VerifyIn):
    ok = rzp.verify_payment(
        body.razorpay_order_id, body.razorpay_payment_id, body.razorpay_signature
    )
    if not ok:
        raise HTTPException(400, "Invalid payment signature")

    # Idempotent update: mark order as paid
    db.mark_order_paid(body.razorpay_order_id, body.razorpay_payment_id)
    return VerifyOut(verified=True)


@router.post("/webhook")
async def webhook(request: Request, x_razorpay_signature: str = Header(...)):
    raw = (await request.body()).decode()  # raw body zaroori hai
    if not rzp.verify_webhook(raw, x_razorpay_signature):
        log.warning("Webhook signature verification failed")
        raise HTTPException(400, "Invalid webhook signature")

    event = json.loads(raw)
    event_type = event.get("event")
    log.info("Received Razorpay webhook event: %s", event_type)

    if event_type == "payment.captured":
        payment = event["payload"]["payment"]["entity"]
        order_id = payment.get("order_id")
        payment_id = payment.get("id")
        if order_id and payment_id:
            # Idempotent update -> order "paid"
            result = db.mark_order_paid(order_id, payment_id)
            log.info(
                "Webhook processed payment.captured: order=%s payment=%s already_paid=%s",
                order_id,
                payment_id,
                result.get("already_paid", False),
            )
        else:
            log.warning(
                "payment.captured event missing order_id or payment_id: %s",
                payment,
            )

    elif event_type in ("refund.processed", "refund.created"):
        refund = event["payload"]["refund"]["entity"]
        payment_id = refund.get("payment_id")
        refund_id = refund.get("id")
        if payment_id and refund_id:
            db.mark_order_refunded(payment_id, refund_id)
            log.info(
                "Webhook processed refund: payment=%s refund=%s",
                payment_id,
                refund_id,
            )

    return {"status": "ok"}


@router.get("/orders")
def get_orders():
    """Returns recent orders from database (useful for audit and debugging)"""
    return db.list_orders()


@router.get("/orders/{order_id}")
def get_order_by_id(order_id: str):
    """Returns order details by Razorpay order ID"""
    order = db.get_order(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order

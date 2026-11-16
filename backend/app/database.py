import logging
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

log = logging.getLogger("database")


def get_db_path() -> str:
    from app.config import settings

    return settings.database_path


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    dirname = os.path.dirname(db_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'INR',
                    receipt TEXT,
                    status TEXT NOT NULL DEFAULT 'created',
                    payment_id TEXT,
                    refund_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_orders_payment_id ON orders(payment_id)"
            )
        log.info("Database initialized successfully at %s", get_db_path())
    finally:
        conn.close()


def save_order(
    order_id: str,
    product_id: str,
    amount: int,
    currency: str = "INR",
    receipt: str = "",
    status: str = "created",
) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO orders (order_id, product_id, amount, currency, receipt, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    product_id=excluded.product_id,
                    amount=excluded.amount,
                    currency=excluded.currency,
                    receipt=excluded.receipt,
                    updated_at=excluded.updated_at
            """,
                (order_id, product_id, amount, currency, receipt, status, now, now),
            )
        log.info(
            "Order saved to DB: order_id=%s, amount=%s, status=%s",
            order_id,
            amount,
            status,
        )
        return get_order(order_id)
    finally:
        conn.close()


def mark_order_paid(order_id: str, payment_id: str) -> Dict[str, Any]:
    """
    Idempotent update for payment:
    If order is already 'paid' with this payment_id, do not duplicate actions.
    If order doesn't exist yet, insert a paid record.
    """
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()

            if row:
                order = dict(row)
                if order["status"] == "paid" and order["payment_id"] == payment_id:
                    log.info(
                        "Idempotent skip: Order %s is already marked 'paid' with payment %s.",
                        order_id,
                        payment_id,
                    )
                    return {"order": order, "already_paid": True}

                cursor.execute(
                    """
                    UPDATE orders
                    SET status = 'paid', payment_id = ?, updated_at = ?
                    WHERE order_id = ?
                """,
                    (payment_id, now, order_id),
                )
                log.info(
                    "Order %s updated to 'paid' with payment_id %s.",
                    order_id,
                    payment_id,
                )
                order["status"] = "paid"
                order["payment_id"] = payment_id
                order["updated_at"] = now
                return {"order": order, "already_paid": False}
            else:
                log.warning(
                    "Order %s not found in DB during mark_order_paid; creating record as paid.",
                    order_id,
                )
                cursor.execute(
                    """
                    INSERT INTO orders (order_id, product_id, amount, currency, receipt, status, payment_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        order_id,
                        "unknown",
                        0,
                        "INR",
                        "",
                        "paid",
                        payment_id,
                        now,
                        now,
                    ),
                )
                return {
                    "order": {
                        "order_id": order_id,
                        "status": "paid",
                        "payment_id": payment_id,
                    },
                    "already_paid": False,
                }
    finally:
        conn.close()


def mark_order_refunded(payment_id: str, refund_id: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM orders WHERE payment_id = ?", (payment_id,)
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    """
                    UPDATE orders
                    SET status = 'refunded', refund_id = ?, updated_at = ?
                    WHERE payment_id = ?
                """,
                    (refund_id, now, payment_id),
                )
                log.info(
                    "Order with payment %s marked as 'refunded' (refund_id=%s).",
                    payment_id,
                    refund_id,
                )
                return {"success": True, "order_id": row["order_id"]}
            else:
                log.warning(
                    "No order found with payment_id %s to mark refunded.",
                    payment_id,
                )
                return {"success": False}
    finally:
        conn.close()


def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_orders(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

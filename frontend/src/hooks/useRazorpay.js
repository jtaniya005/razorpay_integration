import { useCallback } from "react";

const SRC = "https://checkout.razorpay.com/v1/checkout.js";

function loadScript() {
  return new Promise((resolve, reject) => {
    if (window.Razorpay) return resolve();
    const s = document.createElement("script");
    s.src = SRC;
    s.onload = resolve;
    s.onerror = () => reject(new Error("Razorpay script load nahi hua"));
    document.body.appendChild(s);
  });
}

export default function useRazorpay() {
  return useCallback(async ({ order, name, description, onSuccess, onDismiss }) => {
    await loadScript();
    const rzp = new window.Razorpay({
      key: order.key_id,
      amount: order.amount,
      currency: order.currency,
      order_id: order.order_id,
      name,
      description,
      handler: onSuccess, // {razorpay_payment_id, razorpay_order_id, razorpay_signature}
      modal: { ondismiss: onDismiss },
      theme: { color: "#1d4ed8" },
    });
    rzp.open();
  }, []);
}

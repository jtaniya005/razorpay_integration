const rawBase = import.meta.env.VITE_API_BASE_URL || "";
const BASE = rawBase.replace(/\/+$/, "");

async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || "Request failed");
  return res.json();
}

export const getProducts = () => request("/api/products");
export const createOrder = (productId) =>
  request("/api/payments/orders", { method: "POST", body: JSON.stringify({ product_id: productId }) });
export const verifyPayment = (payload) =>
  request("/api/payments/verify", { method: "POST", body: JSON.stringify(payload) });
export const getOrders = () => request("/api/payments/orders");

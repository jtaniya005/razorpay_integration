import { useEffect, useState } from "react";
import { createOrder, getProducts, verifyPayment } from "./api";
import useRazorpay from "./hooks/useRazorpay";
import ProductCard from "./components/ProductCard";

export default function App() {
  const [products, setProducts] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [status, setStatus] = useState(null); // {type: "ok"|"error", text}
  const openCheckout = useRazorpay();

  useEffect(() => {
    getProducts().then(setProducts).catch((e) => setStatus({ type: "error", text: e.message }));
  }, []);

  async function handleBuy(product) {
    setStatus(null);
    setBusyId(product.id);
    try {
      const order = await createOrder(product.id);
      await openCheckout({
        order,
        name: "Demo Store",
        description: product.name,
        onDismiss: () => setBusyId(null),
        onSuccess: async (response) => {
          try {
            await verifyPayment(response);
            setStatus({ type: "ok", text: `Payment received for ${product.name}. ID: ${response.razorpay_payment_id}` });
          } catch (e) {
            setStatus({ type: "error", text: e.message });
          } finally {
            setBusyId(null);
          }
        },
      });
    } catch (e) {
      setStatus({ type: "error", text: e.message });
      setBusyId(null);
    }
  }

  return (
    <main>
      <header>
        <h1>Demo Store</h1>
        <p>Test mode: card 4111 1111 1111 1111, any future expiry, any CVV.</p>
      </header>
      {status && <div className={`status ${status.type}`} role="status">{status.text}</div>}
      <section className="list">
        {products.length === 0 && !status && <p>Loading products…</p>}
        {products.map((p) => (
          <ProductCard key={p.id} product={p} busy={busyId === p.id} onBuy={handleBuy} />
        ))}
      </section>
    </main>
  );
}

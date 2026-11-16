import { useEffect, useState } from "react";
import { createOrder, getProducts, verifyPayment } from "./api";
import useRazorpay from "./hooks/useRazorpay";
import ProductCard from "./components/ProductCard";

export default function App() {
  const [products, setProducts] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [status, setStatus] = useState(null); // {type: "ok"|"error", title, text, paymentId}
  const openCheckout = useRazorpay();

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((e) =>
        setStatus({
          type: "error",
          title: "Connection Notice",
          text: e.message,
        })
      );
  }, []);

  async function handleBuy(product) {
    setStatus(null);
    setBusyId(product.id);
    try {
      const order = await createOrder(product.id);
      await openCheckout({
        order,
        name: "Lumina Store",
        description: product.name,
        onDismiss: () => setBusyId(null),
        onSuccess: async (response) => {
          try {
            await verifyPayment(response);
            setStatus({
              type: "ok",
              title: "Payment Successful!",
              text: `Your transaction for "${product.name}" has been completed and verified.`,
              paymentId: response.razorpay_payment_id,
            });
          } catch (e) {
            setStatus({
              type: "error",
              title: "Verification Notice",
              text: e.message,
            });
          } finally {
            setBusyId(null);
          }
        },
      });
    } catch (e) {
      setStatus({
        type: "error",
        title: "Checkout Error",
        text: e.message,
      });
      setBusyId(null);
    }
  }

  return (
    <div className="store-wrapper">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="brand">
            <span className="brand-icon">✦</span>
            <span className="brand-name">LUMINA</span>
            <span className="brand-sub">STUDIO</span>
          </div>
          <div className="nav-badges">
            <div className="trust-pill">
              <span className="pulse-dot"></span>
              <span>Razorpay Verified</span>
            </div>
            <div className="secure-pill">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              <span>256-Bit SSL</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <div className="hero-content">
          <span className="hero-pill">Official 2026 Collection</span>
          <h1 className="hero-title">Crafted for Everyday Living</h1>
          <p className="hero-subtitle">
            Thoughtfully engineered essentials combining timeless design, premium materials, and instant seamless checkout.
          </p>

          <div className="features-strip">
            <div className="feature-item">
              <span className="feature-icon">⚡</span>
              <span>Instant UPI & Card Checkout</span>
            </div>
            <div className="feature-divider"></div>
            <div className="feature-item">
              <span className="feature-icon">🛡️</span>
              <span>100% Buyer Protection</span>
            </div>
            <div className="feature-divider"></div>
            <div className="feature-item">
              <span className="feature-icon">↩️</span>
              <span>Instant Dashboard Refunds</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {status && (
          <div className={`status-banner ${status.type}`} role="alert">
            <div className="status-icon">
              {status.type === "ok" ? "✓" : "!"}
            </div>
            <div className="status-body">
              <h3 className="status-title">{status.title}</h3>
              <p className="status-desc">{status.text}</p>
              {status.paymentId && (
                <div className="payment-receipt-badge">
                  <span>Payment ID:</span> <code>{status.paymentId}</code>
                </div>
              )}
            </div>
            <button className="status-close" onClick={() => setStatus(null)} aria-label="Close alert">
              ×
            </button>
          </div>
        )}

        <div className="section-header">
          <div>
            <h2 className="section-title">Curated Catalog</h2>
            <p className="section-sub">Select an item below to experience seamless checkout</p>
          </div>
          <span className="catalog-count">{products.length} Products</span>
        </div>

        <section className="product-grid">
          {products.length === 0 && !status && (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading curated collection…</p>
            </div>
          )}
          {products.map((p) => (
            <ProductCard
              key={p.id}
              product={p}
              busy={busyId === p.id}
              onBuy={handleBuy}
            />
          ))}
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-top">
            <div className="footer-brand">
              <div className="brand">
                <span className="brand-icon">✦</span>
                <span className="brand-name">LUMINA</span>
              </div>
              <p className="footer-desc">
                Elevating daily routines with curated design and modern payment experiences.
              </p>
            </div>
            <div className="footer-badges">
              <span className="payment-logo">UPI</span>
              <span className="payment-logo">RuPay</span>
              <span className="payment-logo">VISA</span>
              <span className="payment-logo">Mastercard</span>
              <span className="payment-logo">NetBanking</span>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2026 Lumina Lifestyle Essentials. Powered by Razorpay Payment Gateway.</p>
            <div className="footer-links">
              <span>Privacy Policy</span>
              <span>Terms of Service</span>
              <span>Instant Refunds</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

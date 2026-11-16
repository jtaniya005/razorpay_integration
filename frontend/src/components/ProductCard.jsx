export default function ProductCard({ product, busy, onBuy }) {
  const emoji = product.emoji || "✨";
  const tag = product.tag || "Popular";
  const rating = product.rating || "4.9";

  return (
    <article className="product-card">
      <div className="product-media">
        <div className="product-emoji">{emoji}</div>
        <span className="product-tag">{tag}</span>
      </div>

      <div className="product-info">
        <div className="product-rating">
          <span className="stars">★★★★★</span>
          <span className="rating-score">{rating}</span>
        </div>
        <h2 className="product-name">{product.name}</h2>
        <p className="product-blurb">{product.blurb}</p>
      </div>

      <div className="product-footer">
        <div className="product-price">
          <span className="currency">₹</span>
          <span className="amount">{product.price.toLocaleString("en-IN")}</span>
        </div>
        <button
          className={`pay-button ${busy ? "busy" : ""}`}
          disabled={busy}
          onClick={() => onBuy(product)}
        >
          {busy ? (
            <>
              <span className="spinner"></span> Processing…
            </>
          ) : (
            <>
              <span>Instant Pay</span>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </>
          )}
        </button>
      </div>
    </article>
  );
}

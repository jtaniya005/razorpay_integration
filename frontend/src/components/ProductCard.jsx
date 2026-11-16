export default function ProductCard({ product, busy, onBuy }) {
  return (
    <article className="item">
      <div>
        <h2>{product.name}</h2>
        <p>{product.blurb}</p>
      </div>
      <div className="buy">
        <strong>₹{product.price.toLocaleString("en-IN")}</strong>
        <button disabled={busy} onClick={() => onBuy(product)}>
          {busy ? "Opening…" : "Pay now"}
        </button>
      </div>
    </article>
  );
}

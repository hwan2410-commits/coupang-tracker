import { useState } from "react";

export default function ProductCard({ product }) {
  const [imgError, setImgError] = useState(false);
  const formatPrice = (p) => p?.toLocaleString("ko-KR") + "원";

  const showImg = product.image_url && !imgError;

  return (
    <a
      href={product.product_url}
      target="_blank"
      rel="noopener noreferrer"
      className="bg-white rounded-xl border border-gray-200 hover:shadow-lg transition-shadow flex flex-col overflow-hidden group"
    >
      {/* 이미지 영역 */}
      <div className="relative bg-gray-50 flex items-center justify-center overflow-hidden" style={{ height: "180px" }}>
        {showImg ? (
          <img
            src={product.image_url}
            alt={product.name}
            style={{ width: "100%", height: "100%", objectFit: "contain", padding: "8px" }}
            onError={() => setImgError(true)}
          />
        ) : (
          <div style={{ fontSize: "3rem", color: "#d1d5db" }}>🛍️</div>
        )}
        <span className="absolute top-2 right-2 bg-blue-100 text-blue-700 text-xs px-1.5 py-0.5 rounded">
          {product.category_name}
        </span>
      </div>

      {/* 정보 영역 */}
      <div className="p-3 flex flex-col gap-2 flex-1">
        <p className="text-sm text-gray-800 leading-snug" style={{ minHeight: "3.2em" }}>
          {product.name}
        </p>
        <div>
          <span className="text-base font-bold text-red-600">{formatPrice(product.price)}</span>
        </div>
        {product.rating && (
          <div className="flex items-center gap-1 text-xs text-gray-400">
            <span className="text-yellow-400">★</span>
            <span>{product.rating}</span>
            {product.review_count > 0 && <span>({product.review_count.toLocaleString()})</span>}
          </div>
        )}
      </div>
    </a>
  );
}

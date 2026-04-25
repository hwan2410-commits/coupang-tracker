import { useState, useEffect, useCallback } from "react";
import CategorySidebar from "./components/CategorySidebar";
import ProductCard from "./components/ProductCard";

const API = import.meta.env.VITE_API_URL ?? "/api";

export default function App() {
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [sort, setSort] = useState("price");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchCategories = async () => {
    const res = await fetch(`${API}/categories`);
    const data = await res.json();
    setCategories(data);
  };

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ sort, limit: selectedCategory ? 60 : 400 });
      if (selectedCategory) params.set("category_id", selectedCategory);
      const res = await fetch(`${API}/products?${params}`);
      const data = await res.json();
      setProducts(data);
      if (data.length > 0) setLastUpdated(data[0].updated_at);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, sort]);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleRefresh = async () => {
    setRefreshing(true);
    const params = new URLSearchParams();
    if (selectedCategory) params.set("category_id", selectedCategory);
    await fetch(`${API}/refresh?${params}`, { method: "POST" });
    setTimeout(async () => {
      await fetchProducts();
      setRefreshing(false);
    }, 5000);
  };

  const selectedName = selectedCategory
    ? categories.find((c) => c.id === selectedCategory)?.name
    : "전체";

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" style={{ textAlign: "left" }}>
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🛒</span>
          <div>
            <h1 className="text-xl font-bold text-gray-900" style={{ margin: 0, fontSize: "1.25rem", letterSpacing: "normal" }}>
              최저가 트래커
            </h1>
            <p className="text-xs text-gray-400">다나와 카테고리별 최저가 상품 모음</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-700"
          >
            <option value="price">낮은 가격순</option>
            <option value="discount">높은 할인순</option>
          </select>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="text-sm bg-red-500 hover:bg-red-600 disabled:bg-gray-300 text-white px-4 py-1.5 rounded-lg font-medium transition-colors"
          >
            {refreshing ? "갱신 중..." : "새로고침"}
          </button>
        </div>
      </header>

      <div className="flex flex-1">
        <CategorySidebar
          categories={categories}
          selected={selectedCategory}
          onSelect={setSelectedCategory}
        />

        <main className="flex-1 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-800" style={{ margin: 0, fontSize: "1.125rem" }}>
              {selectedName}
              <span className="text-sm font-normal text-gray-400 ml-2">({products.length}개)</span>
            </h2>
            {lastUpdated && (
              <span className="text-xs text-gray-400">
                업데이트: {new Date(lastUpdated).toLocaleString("ko-KR")}
              </span>
            )}
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="text-4xl mb-3">⏳</div>
                <p className="text-gray-500 text-sm">상품 불러오는 중...</p>
              </div>
            </div>
          ) : products.length === 0 ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="text-5xl mb-3">📦</div>
                <p className="text-gray-500 text-sm">상품이 없습니다. 새로고침을 눌러주세요.</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {products.map((product) => (
                <ProductCard key={`${product.category_id}-${product.id}`} product={product} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

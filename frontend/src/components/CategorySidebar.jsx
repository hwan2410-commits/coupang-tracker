export default function CategorySidebar({ categories, selected, onSelect, loading }) {
  return (
    <aside className="w-48 shrink-0 bg-white border-r border-gray-200 min-h-screen">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-sm font-bold text-gray-700">카테고리</h2>
      </div>
      <ul>
        <li>
          <button
            onClick={() => onSelect(null)}
            className={`w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-gray-50 ${
              selected === null ? "bg-red-50 text-red-600 font-semibold border-r-2 border-red-500" : "text-gray-700"
            }`}
          >
            전체
          </button>
        </li>
        {categories.map((cat) => (
          <li key={cat.id}>
            <button
              onClick={() => onSelect(cat.id)}
              className={`w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-gray-50 ${
                selected === cat.id ? "bg-red-50 text-red-600 font-semibold border-r-2 border-red-500" : "text-gray-700"
              }`}
            >
              {cat.name}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}

import aiosqlite
import json
from datetime import datetime

DB_PATH = "products.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id TEXT NOT NULL,
                category_name TEXT NOT NULL,
                product_id TEXT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                original_price INTEGER,
                discount_rate INTEGER,
                image_url TEXT,
                product_url TEXT,
                rating REAL,
                review_count INTEGER,
                updated_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scrape_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id TEXT,
                status TEXT,
                message TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()

async def save_products(category_id: str, category_name: str, products: list):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE category_id = ?", (category_id,))
        now = datetime.now().isoformat()
        for p in products:
            await db.execute("""
                INSERT INTO products
                (category_id, category_name, product_id, name, price, original_price,
                 discount_rate, image_url, product_url, rating, review_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category_id, category_name, p.get("product_id"), p["name"],
                p["price"], p.get("original_price"), p.get("discount_rate"),
                p.get("image_url"), p.get("product_url"), p.get("rating"),
                p.get("review_count"), now
            ))
        await db.execute(
            "INSERT INTO scrape_log (category_id, status, message, created_at) VALUES (?, ?, ?, ?)",
            (category_id, "success", f"{len(products)}개 상품 저장", now)
        )
        await db.commit()

async def get_products(category_id: str = None, limit: int = 50, sort: str = "price"):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        sort_col = "price" if sort == "price" else "discount_rate DESC" if sort == "discount" else "price"
        if category_id:
            cursor = await db.execute(
                f"SELECT * FROM products WHERE category_id = ? ORDER BY {sort_col} LIMIT ?",
                (category_id, limit)
            )
        else:
            cursor = await db.execute(
                f"SELECT * FROM products ORDER BY {sort_col} LIMIT ?",
                (limit,)
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_last_updated(category_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT MAX(updated_at) FROM products WHERE category_id = ?",
            (category_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

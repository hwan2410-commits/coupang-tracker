import asyncio
import sys
import os

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import httpx

from database import init_db, save_products, get_products, get_last_updated
from scraper import scrape_category, CATEGORIES

scheduler = AsyncIOScheduler()

async def refresh_category(category_id: str, category_name: str):
    print(f"[스크래핑 시작] {category_name}")
    products = await scrape_category(category_id)
    if products:
        await save_products(category_id, category_name, products)
        print(f"[완료] {category_name}: {len(products)}개 저장")
    else:
        print(f"[실패] {category_name}: 상품 없음")

async def refresh_all():
    for cat in CATEGORIES:
        await refresh_category(cat["id"], cat["name"])
        await asyncio.sleep(3)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler.add_job(refresh_all, "interval", hours=1, id="refresh_all")
    scheduler.start()
    asyncio.create_task(refresh_all())
    yield
    scheduler.shutdown()

app = FastAPI(title="쿠팡 최저가 트래커", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/categories")
async def list_categories():
    result = []
    for cat in CATEGORIES:
        last_updated = await get_last_updated(cat["id"])
        result.append({
            "id": cat["id"],
            "name": cat["name"],
            "last_updated": last_updated,
        })
    return result

@app.get("/products")
async def list_products(
    category_id: str = Query(None),
    sort: str = Query("price"),
    limit: int = Query(60, le=500),
):
    products = await get_products(category_id=category_id, limit=limit, sort=sort)
    return products

@app.post("/refresh")
async def manual_refresh(background_tasks: BackgroundTasks, category_id: str = Query(None)):
    if category_id:
        cat = next((c for c in CATEGORIES if c["id"] == category_id), None)
        if cat:
            background_tasks.add_task(refresh_category, cat["id"], cat["name"])
            return {"message": f"{cat['name']} 갱신 시작"}
        return {"message": "카테고리를 찾을 수 없음"}
    background_tasks.add_task(refresh_all)
    return {"message": "전체 카테고리 갱신 시작"}

@app.get("/proxy-image")
async def proxy_image(url: str = Query(...)):
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            r = await client.get(url, headers={
                "Referer": "https://www.danawa.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            })
            content_type = r.headers.get("content-type", "image/jpeg")
            return Response(content=r.content, media_type=content_type, headers={"Cache-Control": "public, max-age=3600"})
    except Exception as e:
        print(f"[proxy-image 오류] {e}")
        return Response(status_code=404)

@app.get("/health")
async def health():
    return {"status": "ok"}

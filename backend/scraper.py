import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from playwright.sync_api import sync_playwright

CATEGORIES = [
    {"id": "food",     "name": "식품",       "query": "라면 과자 음료 식품"},
    {"id": "fashion",  "name": "패션의류",   "query": "티셔츠 청바지 원피스"},
    {"id": "digital",  "name": "가전/디지털", "query": "노트북 스마트폰 이어폰"},
    {"id": "living",   "name": "생활용품",   "query": "세제 휴지 치약 생활용품"},
    {"id": "beauty",   "name": "뷰티/화장품", "query": "스킨 로션 마스크팩 화장품"},
    {"id": "kitchen",  "name": "주방용품",   "query": "냄비 프라이팬 주방용품"},
    {"id": "sports",   "name": "스포츠/레저", "query": "운동화 요가매트 스포츠"},
    {"id": "baby",     "name": "출산/육아",  "query": "기저귀 분유 유아용품"},
    {"id": "pet",      "name": "반려동물",   "query": "강아지사료 고양이사료 펫"},
    {"id": "health",   "name": "건강/의료",  "query": "비타민 영양제 건강식품"},
]

_executor = ThreadPoolExecutor(max_workers=1)

def pcode_to_img(pcode: str) -> str:
    if not pcode or len(pcode) < 4:
        return ""
    last3 = pcode[-3:].zfill(3)
    mid3 = pcode[-6:-3].zfill(3) if len(pcode) >= 6 else pcode[:-3].zfill(3)
    return f"https://img.danawa.com/prod_img/500000/{last3}/{mid3}/img/{pcode}_1.jpg"

def parse_price(text: str) -> int:
    if not text:
        return 0
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else 0

def _sync_scrape(category_id: str, query: str, max_products: int = 40) -> list:
    url = f"https://search.danawa.com/dsearch.php?query={quote(query)}&sort=priceAsc&page=1"
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1280, "height": 3000},
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)

            items = page.query_selector_all("li.prod_item")

            for item in items[:max_products]:
                try:
                    # 스크롤로 lazy load 트리거
                    item.scroll_into_view_if_needed()
                    page.wait_for_timeout(150)

                    name_el = item.query_selector(".prod_name a")
                    name = name_el.inner_text().strip() if name_el else ""

                    # 가격: 다나와 최저가 그대로
                    price_el = item.query_selector(".price_sect strong, .price_sect a strong, .lowest_price strong")
                    price_text = price_el.inner_text().strip() if price_el else ""
                    price = parse_price(price_text)

                    # 이미지: src 우선, data-* 속성 fallback
                    img_el = item.query_selector("img")
                    image_url = ""
                    if img_el:
                        for attr in ["src", "data-src", "data-original", "data-lazy"]:
                            val = img_el.get_attribute(attr) or ""
                            if val and "noImg" not in val and "noData" not in val and val != "":
                                image_url = val
                                break
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url

                    link_el = item.query_selector(".prod_name a")
                    product_url = link_el.get_attribute("href") if link_el else ""

                    # pcode 추출 후 이미지 URL 직접 생성
                    pcode_match = re.search(r"pcode=(\d+)", product_url or "")
                    pcode = pcode_match.group(1) if pcode_match else ""
                    image_url = pcode_to_img(pcode) if pcode else image_url

                    review_el = item.query_selector(".star_total_count, .cnt_opinion")
                    review_text = review_el.inner_text().strip() if review_el else ""
                    review_count = parse_price(review_text)

                    rating_el = item.query_selector(".star_point, .point")
                    rating_text = rating_el.inner_text().strip() if rating_el else ""
                    try:
                        rating = float(rating_text) if rating_text else None
                    except ValueError:
                        rating = None

                    if name and price > 0:
                        products.append({
                            "product_id": re.search(r"pcode=(\d+)", product_url or "").group(1) if product_url and "pcode=" in product_url else "",
                            "name": name,
                            "price": price,
                            "original_price": price,
                            "discount_rate": 0,
                            "image_url": image_url,
                            "product_url": product_url,
                            "rating": rating,
                            "review_count": review_count,
                        })
                except Exception:
                    continue

        except Exception as e:
            print(f"스크래핑 오류 [{category_id}]: {e}")
        finally:
            browser.close()

    return products

async def scrape_category(category_id: str, max_products: int = 40) -> list:
    cat = next((c for c in CATEGORIES if c["id"] == category_id), None)
    if not cat:
        return []
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _sync_scrape, category_id, cat["query"], max_products)

import asyncio
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
import base64
from jinja2 import Environment, BaseLoader

app = FastAPI()
env = Environment(loader=BaseLoader())


INDEX_HTML = """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Playwright Crawler</title></head>
  <body>
    <h1>Playwright Crawler</h1>
    <form method="post" action="/">
      <label>URL: <input name="url" value="https://news.ycombinator.com" /></label>
      <button type="submit">Crawl (UI)</button>
    </form>
    <p>Use the JSON API at <code>/api/crawl</code> with payload <code>{"url":"https://example.com"}</code></p>
  </body>
</html>
"""


class CrawlRequest(BaseModel):
    url: str


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(INDEX_HTML)


@app.post("/api/crawl")
async def api_crawl(req: CrawlRequest):
    try:
        result = await crawl_url(req.url)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def crawl_url(url: str) -> dict:
    """Crawl the given URL with Playwright and return a JSON-serializable dict.

    Returned dict: { url, page_title, screenshot_base64, links }
    """
    if not url.startswith("http"):
        url = "https://" + url

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--single-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ],
        )
        page = await browser.new_page()
        try:
            await page.goto(url)
            screenshot = await page.screenshot()
            page_title = await page.title()

            links_and_texts = await page.evaluate(
                """() => {
                const anchors = document.querySelectorAll('a');
                return Array.from(anchors).map(anchor => ({ href: anchor.href, text: (anchor.textContent||'').trim() }));
            }"""
            )
            links = [ {"href": l.get('href'), "text": l.get('text')} for l in links_and_texts ]
        finally:
            await browser.close()

    screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')

    return {
        "url": url,
        "page_title": page_title,
        "screenshot_base64": screenshot_base64,
        "links": links,
    }

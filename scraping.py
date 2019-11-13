from bs4 import BeautifulSoup as Soup
from aiohttp import web
import aiohttp
import json
import asyncio


routes = web.RouteTableDef()

lock = asyncio.Lock()
links = []

mutex = asyncio.Lock()
found = {}

@routes.get("/response")
async def index(request):
    body = json.dumps(found)
    return web.json_response(found)

async def pushlink(url):
    async with lock:
        if len(links) > 500 or url in links:
            return False
        links.append(url)
    return True

async def addfound(url, text):
    async with mutex:
        if not url in found:
            found[url] = []
        found[url].append(text)

async def gettext(session, url):
    try:
        async with session.get(url, timeout=5) as res:
            return await res.text()
    except:
        return

async def fetch(session, url, keywords):
    print(url)
    text = await gettext(session, url)
    if text is None:
        return

    soup = Soup(text, "html.parser")
    for e in soup.find("body").find_all(['p','h1']):
        text = e.get_text().lower()
        for key in keywords:
            if text.find(key) >= 0:
                await addfound(url, text)
    fetches = []
    for a in soup.find("body").find_all('a', class_="heroPickerIconLink"):
        href = a.get("href")
        if href is None or len(href) == 1:
            continue

        if href.split("?")[0].endswith((".png", ".jpg", ".mp4", ".css")):
            continue
        
        if href.startswith("?"):
            continue

        if href.startswith("/"):
            href = url + href
        if href.startswith("http") and await pushlink(href):
            fetches.append(asyncio.ensure_future(fetch(session, href, keywords)))
    await asyncio.gather(*fetches)
    
async def main():
    async with aiohttp.ClientSession() as session:
        await fetch(session, "http://www.dota2.com/heroes/", ["drow ranger", "slark", "windranger"])
 
if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    asyncio.gather(main())
    web.run_app(app)
    print(found)

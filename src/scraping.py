from bs4 import BeautifulSoup as Soup
import aiohttp
import json
import asyncio

async def pushlink(url, links, lock):
  async with lock:
    if len(links) > 150 or (url in links):
      return False
    links.append(url)
    print(url)
  return True

async def gettext(session, url):
  try:
    async with aiohttp.request('GET', url) as res:
      if res.status == 200:
        return await res.text()
  except Exception as e:
    print(e)
    return

def contains (text, keywords):
  for k in keywords:
    if isinstance(k, list) and all([x in text for x in k.split()]):
      return True

    if k in text:
      return True

  return False

async def fetch(ws, session, url, keywords, links=None, lock=None):
  if links is None:
    links = []
    lock = asyncio.Lock()
  
  text = await gettext(session, url)
  if text is None:
      return

  soup = Soup(text, "html.parser")
  for e in soup.find("body").find_all('p'):
      text = e.get_text().lower()
      if contains(text, keywords):
        await ws.send_json({"message":"response", "data": {
          "url":url,
          "text": text}
        })
  
  fetches = []
  for a in soup.find("body").find_all('a', href=True):
      href = a.get("href")
      if href is None or len(href) < 4:
        continue

      if "?" in href:
        continue

      if not contains(href, keywords):
        continue

      if href.endswith((".png", ".jpg", ".mp4", ".css")):
        continue

      if href.startswith("/"):
          href = url + href

      if href.startswith("http") and await pushlink(href, links, lock):
          fetches.append(asyncio.ensure_future(fetch(ws, session, href, keywords, links, lock)))
  await asyncio.gather(*fetches)
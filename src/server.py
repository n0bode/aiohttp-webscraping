import asyncio
import json
from aiohttp import web, ClientSession, request
from os import path
from scraping import fetch

PATH = path.dirname(__file__)
routes = web.RouteTableDef()
SESSION = None

@routes.get("/")
async def index(request):
  return web.FileResponse(f'{PATH}/../public/index.html')

@routes.get("/communication.js")
async def js(request):
  return web.FileResponse(f'{PATH}/../public/communication.js')

@routes.get("/ws")
async def ws(request):
  ws = web.WebSocketResponse()
  await ws.prepare(request)
  async for msg in ws:
    data = json.loads(msg.data)
    print(data)
    if data["message"] == "request":
      await fetch(ws, SESSION, data["data"]["url"], data["data"]["keywords"])
      await ws.close()
      print("CLOSE")
  return ws

if __name__ == "__main__":
  app = web.Application()
  app.add_routes(routes)
  web.run_app(app)

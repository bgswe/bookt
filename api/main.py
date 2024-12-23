import asyncio
from contextlib import asynccontextmanager

# import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# from api.routers import authentication
from api.luminis.database import database
from api.luminis.router import luminis_router
from api.routers.commands import command_router
from api.routers.queries import query_router

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()  # type: ignore


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="api/static"), name="static")

# app.include_router(authentication.router)
app.include_router(command_router)
app.include_router(query_router)
app.include_router(luminis_router)


@app.get("/health")
def health():
    print("health endpoint")

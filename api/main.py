import asyncio

# import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from api.routers import authentication
from api.routers.commands import command_router
from api.routers.queries import query_router

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(authentication.router)

app.include_router(command_router)
app.include_router(query_router)


@app.get("/health")
def health():
    print("health endpoint")

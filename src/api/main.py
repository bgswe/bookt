import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import accounts, authentication

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
# app.include_router(accounts.query_router)
app.include_router(accounts.command_router)

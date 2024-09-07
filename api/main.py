import asyncio
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import accounts, authentication
from api.settings import settings

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     pool = await asyncpg.create_pool(
#         host=settings.database_host,
#         database=settings.database_name,
#         user=settings.database_user,
#         port=settings.database_port,
#         password=settings.database_password,
#     )
#     app.state.pool = pool

#     yield

#     pool.close()


# app = FastAPI(lifespan=lifespan)
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


@app.get("/health")
def health():
    print("health endpoint")

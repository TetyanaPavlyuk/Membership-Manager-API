from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers.healthcheck import healthcheck_router
from app.routers.users import user_router


class Server:
    def __init__(self):
        self.app = FastAPI()

        self.app.include_router(healthcheck_router)
        self.app.include_router(user_router)

        origins = settings.parse_origins
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


server = Server()

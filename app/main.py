from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.exceptions.handlers import add_exception_handlers
from app.routers import (
    healthcheck_router,
    user_router,
    auth_router,
    company_router,
    invitation_router,
    request_router,
    membership_router,
)


class Server:
    def __init__(self):
        self.app = FastAPI()

        self.app.include_router(healthcheck_router)
        self.app.include_router(user_router)
        self.app.include_router(auth_router)
        self.app.include_router(company_router)
        self.app.include_router(invitation_router)
        self.app.include_router(request_router)
        self.app.include_router(membership_router)

        origins = settings.parse_origins
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        add_exception_handlers(self.app)


server = Server()

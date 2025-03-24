from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.exceptions import (
    ItemsListException,
    ItemNotFoundException,
    ItemDetailException,
    ItemAlreadyExistException,
    ItemCreateException,
    ItemUpdateException,
    ItemDeleteException,
)
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

        self.add_exception_handlers()

    def add_exception_handlers(self):
        @self.app.exception_handler(ItemsListException)
        async def items_list_exception_handler(request, exc: ItemsListException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.message}
            )

        @self.app.exception_handler(ItemNotFoundException)
        async def item_not_found_exception_handler(request, exc: ItemNotFoundException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.message}
            )

        @self.app.exception_handler(ItemDetailException)
        async def item_detail_exception_handler(request, exc: ItemDetailException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.message}
            )

        @self.app.exception_handler(ItemAlreadyExistException)
        async def item_already_exist_exception_handler(
            request, exc: ItemAlreadyExistException
        ):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.message}
            )

        @self.app.exception_handler(ItemCreateException)
        async def item_create_exception_handler(request, exc: ItemCreateException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.message}
            )

        @self.app.exception_handler(ItemUpdateException)
        async def item_update_exception_handler(request, exc: ItemUpdateException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.message}
            )

        @self.app.exception_handler(ItemDeleteException)
        async def item_delete_exception_handler(request, exc: ItemDeleteException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.message}
            )


server = Server()

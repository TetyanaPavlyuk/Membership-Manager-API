from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import (
    ItemsListException,
    ItemNotFoundException,
    ItemDetailException,
    ItemAlreadyExistException,
    ItemCreateException,
    ItemUpdateException,
    ItemDeleteException,
    ItemException,
    ExpiredTokenException,
    InvalidTokenException,
    UnauthorizedException,
    RegisterException,
    LoginException,
    InvalidTokenFormatException,
    GetCurrentUserException,
)


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(ItemsListException)
    async def items_list_exception_handler(request, exc: ItemsListException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ItemNotFoundException)
    async def item_not_found_exception_handler(request, exc: ItemNotFoundException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ItemDetailException)
    async def item_detail_exception_handler(request, exc: ItemDetailException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ItemAlreadyExistException)
    async def item_already_exist_exception_handler(
        request, exc: ItemAlreadyExistException
    ):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ItemCreateException)
    async def item_create_exception_handler(request, exc: ItemCreateException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ItemUpdateException)
    async def item_update_exception_handler(request, exc: ItemUpdateException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ItemDeleteException)
    async def item_delete_exception_handler(request, exc: ItemDeleteException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ItemException)
    async def item_exception_handler(request, exc: ItemException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(ExpiredTokenException)
    async def expired_token_exception_handler(request, exc: ExpiredTokenException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(InvalidTokenException)
    async def invalid_token_exception_handler(request, exc: InvalidTokenException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(request, exc: UnauthorizedException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(RegisterException)
    async def register_exception_handler(request, exc: RegisterException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(LoginException)
    async def login_exception_handler(request, exc: LoginException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(InvalidTokenFormatException)
    async def invalid_token_format_exception_handler(
        request, exc: InvalidTokenFormatException
    ):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(GetCurrentUserException)
    async def get_current_user_exception_handler(request, exc: GetCurrentUserException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

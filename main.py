import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from backend.controller.controller import router
from backend.database.sqlite_database import Session, create_tables
from backend.domain.carts.cart_service import CartService
from backend.domain.categories.category_service import CategoryService
from backend.domain.products.product_service import ProductService
from backend.domain.products_from_carts.product_from_cart_service import (
    ProductFromCartService,
)
from backend.domain.users.user_service import UserService
from backend.dummy_json_api.dummy_json_api import DummyJSONApi


def create_app() -> FastAPI:
    app = FastAPI()

    # Initialize the app state
    app.state = type("State", (), {})()

    api: DummyJSONApi = DummyJSONApi()

    db_session = Session()

    create_tables()

    user_service: UserService = UserService(api, db_session)
    product_from_cart_service: ProductFromCartService = ProductFromCartService(
        db_session
    )
    cart_service: CartService = CartService(api, db_session, product_from_cart_service)
    product_service: ProductService = ProductService(api, db_session)
    category_service: CategoryService = CategoryService(db_session)

    app.state.user_service = user_service
    app.state.cart_service = cart_service
    app.state.product_service = product_service
    app.state.product_from_cart_service = product_from_cart_service
    app.state.category_service = category_service

    user_service.process_users()
    cart_service.process_carts()
    product_service.process_products()

    app.include_router(router=router, prefix="/api")

    # add root redirect to /docs
    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        return RedirectResponse(url="/docs")

    return app


my_app = create_app()


if __name__ == "__main__":
    uvicorn.run(my_app, host="127.0.0.1", port=8000)

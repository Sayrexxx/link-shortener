from fastapi import FastAPI
from app.core.error_handlers import setup_exception_handlers
from app.core.config import settings
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url='/docs'
)

setup_exception_handlers(app)

templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=404
        )
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=exc.status_code
    )

@app.get("/", include_in_schema=False)
async def home_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "csrf_token": request.state.csrf
        }
    )

@app.middleware("http")
async def add_csrf_token(request: Request, call_next):
    request.state.csrf = "generate_secure_token_here"  # В реальном проекте использовать безопасную генерацию
    response = await call_next(request)
    return response

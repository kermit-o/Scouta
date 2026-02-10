from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.web.public_blog import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/", include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

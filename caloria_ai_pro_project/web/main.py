from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.db import init_db, get_rings_for_user

app = FastAPI(title="Caloria AI Pro Web")

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Caloria AI Pro",
        },
    )


@app.get("/dashboard/{telegram_id}", response_class=HTMLResponse)
async def dashboard(request: Request, telegram_id: int):
    try:
        calories_ring, protein_ring, activity_ring = await get_rings_for_user(
            telegram_id=telegram_id
        )
    except Exception as exc:  # демонстрационный перехват
        raise HTTPException(status_code=500, detail=str(exc))

    rings = {
        "calories": calories_ring,
        "protein": protein_ring,
        "activity": activity_ring,
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "telegram_id": telegram_id,
            "rings": rings,
        },
    )

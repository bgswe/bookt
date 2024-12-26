from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.luminis.events_model import get_event_list, get_unique_event_types

luminis_router = APIRouter(prefix="/luminis", tags=["Luminis"])

templates = Jinja2Templates(directory="api/luminis/templates")


@luminis_router.get("", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={
            "events": await get_event_list(),
            "types": await get_unique_event_types(),
        },
    )

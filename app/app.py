from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from .models import Base, Message
from .tasks import process_message

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/loaderio-a059a2b166f59859ceaad4f9e1a017e6/")
async def verify():
    token = "loaderio-a059a2b166f59859ceaad4f9e1a017e6"
    return Response(content=token, media_type="text/plain")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request, db: Session = Depends(get_db)):
    messages = db.query(Message).all()
    print(messages)
    return templates.TemplateResponse(
        "index.html", {"request": request, "messages": messages}
    )


@app.get("/sync-form", response_class=HTMLResponse)
async def get_sync_form(request: Request):
    return templates.TemplateResponse(
        "form.html", {"request": request, "title": "Sync form"}
    )


@app.post("/sync-form", response_class=HTMLResponse)
async def post_sync_form(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    content = form_data.get("content")

    if not content:
        return templates.TemplateResponse(
            "form.html",
            {
                "request": request,
                "error": "Content is required!",
                "content": content,
                "title": "Sync form",
            },
        )

    message = Message(content=content)
    db.add(message)
    db.commit()

    messages = db.query(Message).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "messages": messages}
    )


@app.get("/async-form", response_class=HTMLResponse)
async def get_async_form(request: Request):
    return templates.TemplateResponse(
        "form.html", {"request": request, "title": "Async form"}
    )


@app.post("/async-form", response_class=HTMLResponse)
async def post_async_form(request: Request):
    form_data = await request.form()
    content = form_data.get("content")

    if not content:
        return templates.TemplateResponse(
            "form.html",
            {
                "request": request,
                "error": "Content is required!",
                "content": content,
                "title": "Async form",
            },
        )

    task = process_message.apply_async(args=[content], queue="default")

    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

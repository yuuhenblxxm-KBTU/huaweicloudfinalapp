import os
import random
import string
import time

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Link
from schemas import LinkCreate, LinkResponse

app = FastAPI()


def get_allowed_origins() -> list[str]:
    origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1")
    origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
    return origins or ["http://localhost", "http://127.0.0.1"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables_with_retry():
    max_attempts = 10
    delay_seconds = 2

    for attempt in range(1, max_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def to_link_response(link: Link, is_custom: bool = False) -> LinkResponse:
    return LinkResponse(
        id=link.id,
        original_url=link.original_url,
        short_code=link.short_code,
        is_custom=is_custom,
        created_at=link.created_at,
    )


def infer_is_custom_code(code: str) -> bool:
    # Generated codes are currently 6 alphanumeric chars.
    # If format differs, we treat it as a custom alias.
    return not (len(code) == 6 and code.isalnum())


@app.post("/api/shorten", response_model=LinkResponse)
def shorten_url(link: LinkCreate, db: Session = Depends(get_db)):
    is_custom = bool(link.custom_code)
    code = link.custom_code or generate_code()
    while not link.custom_code and db.query(Link).filter(Link.short_code == code).first():
        code = generate_code()

    if link.custom_code and db.query(Link).filter(Link.short_code == code).first():
        raise HTTPException(status_code=409, detail="Custom code is already in use")

    db_link = Link(original_url=link.original_url, short_code=code)
    db.add(db_link)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Short code is already in use")
    db.refresh(db_link)
    return to_link_response(db_link, is_custom=is_custom)


@app.get("/api/links", response_model=list[LinkResponse])
def get_links(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    rows = db.query(Link).order_by(Link.created_at.desc()).offset(offset).limit(limit).all()
    return [to_link_response(row, is_custom=infer_is_custom_code(row.short_code)) for row in rows]


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "up"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=link.original_url)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random
import string

from database import engine, get_db, Base
from models import Link
from schemas import LinkCreate, LinkResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/api/shorten", response_model=LinkResponse)
def shorten_url(link: LinkCreate, db: Session = Depends(get_db)):
    code = generate_code()
    while db.query(Link).filter(Link.short_code == code).first():
        code = generate_code()
    db_link = Link(original_url=link.original_url, short_code=code)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

@app.get("/api/links", response_model=list[LinkResponse])
def get_links(db: Session = Depends(get_db)):
    return db.query(Link).order_by(Link.created_at.desc()).all()

@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=link.original_url)
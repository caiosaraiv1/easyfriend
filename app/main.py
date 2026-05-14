"""
app/main.py
Ponto de entrada da API EasyFriend.
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db, engine
from models.db_models import Base
from routes.radar import router as radar_router

# Cria as tabelas no banco se ainda não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EasyFriend", version="0.2.0")

# Registra os routers
from routes.radar import router as radar_router
app.include_router(radar_router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Verifica se a API e o banco estão funcionando."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status, "versao": "0.2.0"}

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
from routes.agenda import router as agenda_router
from routes.chat import router as chat_router
from routes.apadrinhamento import router as apadrinhamento_router
from routes.auth import router as auth_router

# Cria as tabelas no banco se ainda não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EasyFriend", version="0.2.0")

# Registra os routers
app.include_router(auth_router)
app.include_router(radar_router)
app.include_router(agenda_router)
app.include_router(chat_router)
app.include_router(apadrinhamento_router)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Verifica se a API e o banco estão funcionando."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status, "versao": "0.2.0"}

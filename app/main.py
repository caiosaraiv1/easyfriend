"""
app/main.py
Ponto de entrada da API EasyFriend.
"""

import logging
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text

from logging_config import setup_logging
from database import get_db, engine
from models.db_models import Base
from routes.radar import router as radar_router
from routes.agenda import router as agenda_router
from routes.chat import router as chat_router
from routes.apadrinhamento import router as apadrinhamento_router
from routes.auth import router as auth_router

# Inicializa logging antes de tudo
setup_logging()
logger = logging.getLogger(__name__)

# Cria as tabelas no banco se ainda não existirem
Base.metadata.create_all(bind=engine)
logger.info("Tabelas verificadas/criadas no banco.")

app = FastAPI(title="EasyFriend", version="0.2.0")

# Middleware: loga cada requisição recebida
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f">> {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"<< {request.method} {request.url.path} - {response.status_code}")
    return response

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
        logger.debug("Health check: banco OK.")
    except Exception as e:
        db_status = "error"
        logger.error(f"Health check: banco com erro — {e}")
    return {"status": "ok", "db": db_status, "versao": "0.2.0"}

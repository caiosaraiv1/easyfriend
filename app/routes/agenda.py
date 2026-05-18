"""
app/routes/agenda.py
Endpoints da Agenda Cultural — chamados pelo app iOS.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.repositorios_CRUD import EventoRepo
from patterns.strategy import (
    BuscaContext,
    Consulta,
    BuscaPorTipoEvento,
    BuscaPorIdioma,
    criterio_para_strategy,
)
from patterns.observer import (
    EventoSubject,
    Evento as EventoObs,
    PushNotifier,
    EmailNotifier,
    BadgeNotifier,
)

router = APIRouter(prefix="/agenda", tags=["Agenda"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class EventoCreate(BaseModel):
    titulo: str
    tipo: str
    idioma: str
    lat: float = 0.0
    lon: float = 0.0
    data_evento: datetime


# ---------------------------------------------------------------------------
# Helper — formata evento para o iOS
# ---------------------------------------------------------------------------

def _formatar_evento(e) -> dict:
    return {
        "id": e.id,
        "titulo": e.titulo,
        "tipo": e.tipo,
        "descricao": e.titulo,          # placeholder
        "local": "São Paulo",           # placeholder
        "data_inicio": e.data_evento.isoformat() if e.data_evento else None,
        "interessados": 0,              # placeholder
        "idioma": e.idioma,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/eventos")
def listar_eventos(
    criterio: str = "tipo",
    valor: str = "gastronomia",
    db: Session = Depends(get_db),
):
    """
    Lista eventos filtrados pelo critério escolhido no iOS.
    Demonstra a Strategy: BuscaPorTipoEvento ou BuscaPorIdioma
    sem nenhum if/else no service.
    """
    todos = EventoRepo.listar(db)

    # Converte para dataclass da Strategy
    from patterns.strategy import Evento as EventoStrategy
    eventos_strategy = [
        EventoStrategy(
            id=e.id,
            titulo=e.titulo,
            tipo=e.tipo,
            idioma=e.idioma,
            lat=e.lat,
            lon=e.lon,
        )
        for e in todos
    ]

    try:
        ctx = BuscaContext(criterio_para_strategy(criterio))
        resultado = ctx.executar(Consulta(valor=valor), eventos_strategy)
        ids_filtrados = {e.id for e in resultado.itens}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    eventos_filtrados = [e for e in todos if e.id in ids_filtrados]
    return [_formatar_evento(e) for e in eventos_filtrados]


@router.post("/eventos", status_code=201)
def criar_evento(body: EventoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo evento na agenda.
    """
    evento = EventoRepo.criar(db, {
        "titulo": body.titulo,
        "tipo": body.tipo,
        "idioma": body.idioma,
        "lat": body.lat,
        "lon": body.lon,
        "data_evento": body.data_evento,
    })
    return _formatar_evento(evento)

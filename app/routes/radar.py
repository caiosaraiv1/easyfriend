"""
app/routes/radar.py
Endpoints do Radar — chamados pelo app iOS.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from services.radar_service import RadarService

router = APIRouter(prefix="/radar", tags=["Radar"])


# ---------------------------------------------------------------------------
# Schemas de entrada
# ---------------------------------------------------------------------------

class MatchCreate(BaseModel):
    usuario_a_id: int
    usuario_b_id: int
    criterio: str = "idioma"   # idioma | proximidade | pais_origem | tipo


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/matches", status_code=201)
def criar_match(body: MatchCreate, db: Session = Depends(get_db)):
    """
    Cria um match entre dois usuários.
    Demonstra o Observer: PushNotifier e EmailNotifier aparecem no terminal.
    """
    service = RadarService(db)
    try:
        return service.criar_match(
            usuario_a_id=body.usuario_a_id,
            usuario_b_id=body.usuario_b_id,
            criterio=body.criterio,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/matches")
def buscar_matches(
    criterio: str = "idioma",
    valor: str = "pt",
    lat: float = 0.0,
    lon: float = 0.0,
    raio_km: float = 10.0,
    db: Session = Depends(get_db),
):
    """
    Busca usuários pelo critério escolhido na tela do iOS.
    Demonstra a Strategy: troca o filtro sem alterar nenhuma classe existente.
    """
    service = RadarService(db)
    try:
        usuarios = service.buscar_usuarios(
            criterio=criterio, valor=valor,
            lat=lat, lon=lon, raio_km=raio_km,
        )
        return [
            {"id": u.id, "nome": u.nome, "idioma": u.idioma, "pais_origem": u.pais_origem}
            for u in usuarios
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
app/routes/radar.py
Endpoints do Radar — chamados pelo app iOS.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from patterns.strategy import _haversine_km

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
    Retorna JSON enriquecido com coordenadas e raio de privacidade
    para o mapa (MapCircle) do iOS.
    Demonstra a Strategy: troca o filtro sem alterar nenhuma classe existente.
    """
    service = RadarService(db)
    try:
        usuarios = service.buscar_usuarios(
            criterio=criterio, valor=valor,
            lat=lat, lon=lon, raio_km=raio_km,
        )

        resultado = []
        for u in usuarios:
            distancia = round(_haversine_km(lat, lon, u.lat, u.lon), 2)
            raio_privacidade_metros = round(300.0 + (distancia * 100), 2)

            resultado.append({
                "id": u.id,
                "usuario": {
                    "id": u.id,
                    "nome": u.nome,
                    "idade": 25,            # placeholder até ter coluna no schema
                    "pais_origem": u.pais_origem,
                    "idiomas": [u.idioma],
                    "interesses": [],       # placeholder
                    "email": None,
                },
                "coordenada_lat": u.lat,
                "coordenada_lon": u.lon,
                "raio_privacidade_metros": round(300.0 + (distancia * 100), 2),
                "distancia_km": distancia,
                "criado_em": "2026-05-18T00:00:00Z",
            })

        return resultado

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

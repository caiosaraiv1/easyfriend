"""
app/routes/agenda.py
Endpoints da Agenda Cultural — chamados pelo app iOS.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.agenda_service import AgendaService

router = APIRouter(prefix="/agenda", tags=["Agenda"])


@router.get("/eventos")
def buscar_eventos(
    criterio: str = "tipo",
    valor: str = "gastronomia",
    lat: float = 0.0,
    lon: float = 0.0,
    raio_km: float = 10.0,
    db: Session = Depends(get_db),
):
    """
    Busca eventos pelo critério escolhido na tela do iOS.
    Demonstra a Strategy: troca o filtro sem alterar nenhuma classe existente.

    Exemplos:
      GET /agenda/eventos?criterio=tipo&valor=gastronomia
      GET /agenda/eventos?criterio=idioma&valor=pt
    """
    service = AgendaService(db)
    try:
        eventos = service.buscar_eventos(
            criterio=criterio, valor=valor,
            lat=lat, lon=lon, raio_km=raio_km,
        )
        return [
            {
                "id": e.id,
                "titulo": e.titulo,
                "tipo": e.tipo,
                "idioma": e.idioma,
            }
            for e in eventos
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

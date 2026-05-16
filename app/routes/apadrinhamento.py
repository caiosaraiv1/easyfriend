"""
app/routes/apadrinhamento.py
Endpoints de Apadrinhamento — M4-03.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from services.apadrinhamento_service import ApadrinhamentoService

router = APIRouter(prefix="/apadrinhamento", tags=["Apadrinhamento"])


class SolicitacaoCreate(BaseModel):
    padrinho_id: int
    afilhado_id: int


@router.post("/solicitar", status_code=201)
def solicitar(body: SolicitacaoCreate, db: Session = Depends(get_db)):
    """Cria uma solicitação de apadrinhamento com status 'pendente'."""
    service = ApadrinhamentoService(db)
    try:
        return service.solicitar(
            padrinho_id=body.padrinho_id,
            afilhado_id=body.afilhado_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{apadrinhamento_id}/aceitar")
def aceitar(apadrinhamento_id: int, db: Session = Depends(get_db)):
    """
    Aceita uma solicitação e aciona o Observer.
    O afilhado é notificado via push, e-mail e badge.
    """
    service = ApadrinhamentoService(db)
    try:
        return service.aceitar(apadrinhamento_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

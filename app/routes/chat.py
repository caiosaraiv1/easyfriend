"""
app/routes/chat.py
Endpoints de Chat — M4-02.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


class MensagemCreate(BaseModel):
    remetente_id: int
    destinatario_id: int
    conteudo: str


@router.post("/mensagens", status_code=201)
def enviar_mensagem(body: MensagemCreate, db: Session = Depends(get_db)):
    """
    Envia uma mensagem e aciona o Observer.
    PushNotifier e EmailNotifier aparecem no terminal.
    """
    service = ChatService(db)
    try:
        return service.enviar_mensagem(
            remetente_id=body.remetente_id,
            destinatario_id=body.destinatario_id,
            conteudo=body.conteudo,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/mensagens/{mensagem_id}")
def buscar_mensagem(mensagem_id: int, db: Session = Depends(get_db)):
    """Retorna uma mensagem pelo ID."""
    service = ChatService(db)
    try:
        return service.buscar_mensagem(mensagem_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/conversa")
def listar_conversa(
    usuario_id_1: int,
    usuario_id_2: int,
    db: Session = Depends(get_db),
):
    """Retorna o histórico de mensagens entre dois usuários."""
    service = ChatService(db)
    return service.listar_conversa(usuario_id_1, usuario_id_2)

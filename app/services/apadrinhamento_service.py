"""
app/services/apadrinhamento_service.py
ApadrinhamentoService — gerencia solicitações de mentoria entre usuários.

Observer é acionado no PATCH /{id}/aceitar, notificando o afilhado
que sua solicitação foi aceita.
"""

from sqlalchemy.orm import Session

from patterns.observer import (
    EventoSubject,
    Evento as EventoObs,
    PushNotifier,
    EmailNotifier,
    BadgeNotifier,
)
from models.repositorios_CRUD import UsuarioRepo
from models.db_models import Apadrinhamento


class ApadrinhamentoService(EventoSubject):

    def __init__(self, db: Session) -> None:
        super().__init__()
        self.db = db

        self.inscrever(PushNotifier())
        self.inscrever(EmailNotifier())
        self.inscrever(BadgeNotifier())

    def solicitar(self, padrinho_id: int, afilhado_id: int) -> dict:
        """Cria uma solicitação de apadrinhamento com status 'pendente'."""
        padrinho = UsuarioRepo.buscar_por_id(self.db, padrinho_id)
        afilhado = UsuarioRepo.buscar_por_id(self.db, afilhado_id)

        if not padrinho:
            raise ValueError(f"Padrinho com id={padrinho_id} não encontrado.")
        if not afilhado:
            raise ValueError(f"Afilhado com id={afilhado_id} não encontrado.")

        apadrinhamento = Apadrinhamento(
            padrinho_id=padrinho_id,
            afilhado_id=afilhado_id,
            status="pendente",
        )
        self.db.add(apadrinhamento)
        self.db.commit()
        self.db.refresh(apadrinhamento)

        return {
            "apadrinhamento_id": apadrinhamento.id,
            "padrinho":          padrinho.nome,
            "afilhado":          afilhado.nome,
            "status":            apadrinhamento.status,
        }

    def aceitar(self, apadrinhamento_id: int) -> dict:
        """
        Atualiza status para 'aceito' e dispara o Observer,
        notificando o afilhado que foi aceito.
        """
        apadrinhamento = self.db.query(Apadrinhamento).filter(
            Apadrinhamento.id == apadrinhamento_id
        ).first()

        if not apadrinhamento:
            raise ValueError(f"Apadrinhamento com id={apadrinhamento_id} não encontrado.")

        apadrinhamento.status = "aceito"
        self.db.commit()
        self.db.refresh(apadrinhamento)

        afilhado = UsuarioRepo.buscar_por_id(self.db, apadrinhamento.afilhado_id)
        padrinho = UsuarioRepo.buscar_por_id(self.db, apadrinhamento.padrinho_id)

        # Observer acionado ao aceitar — notifica o afilhado
        evento = EventoObs(
            tipo="apadrinhamento_aceito",
            payload={
                "apadrinhamento_id": apadrinhamento.id,
                "usuario_id":        afilhado.id,
                "email":             afilhado.email,
                "padrinho":          padrinho.nome,
            },
        )
        self.notificar(evento)

        return {
            "apadrinhamento_id": apadrinhamento.id,
            "padrinho":          padrinho.nome,
            "afilhado":          afilhado.nome,
            "status":            apadrinhamento.status,
        }

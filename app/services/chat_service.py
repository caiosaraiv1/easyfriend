"""
app/services/chat_service.py
ChatService — gerencia o envio e recebimento de mensagens.

Implementa EventoSubject (Observer): ao receber uma mensagem,
notifica todos os observers inscritos (PushNotifier, EmailNotifier, BadgeNotifier).
"""

from sqlalchemy.orm import Session

from patterns.observer import (
    EventoSubject,
    Evento as EventoObs,
    PushNotifier,
    EmailNotifier,
    BadgeNotifier,
)
from models.repositorios_CRUD import MensagemRepo, UsuarioRepo


class ChatService(EventoSubject):
    """
    Serviço de Chat.
    Herda EventoSubject para chamar self.notificar(evento)
    sempre que uma mensagem for enviada.
    """

    def __init__(self, db: Session) -> None:
        super().__init__()
        self.db = db

        # Registra os observers — mesma abordagem do RadarService
        self.inscrever(PushNotifier())
        self.inscrever(EmailNotifier())
        self.inscrever(BadgeNotifier())

    def enviar_mensagem(self, remetente_id: int, destinatario_id: int, conteudo: str) -> dict:
        """
        Persiste a mensagem no banco e dispara o Observer para notificar
        o destinatário via push, e-mail e badge.
        """
        remetente    = UsuarioRepo.buscar_por_id(self.db, remetente_id)
        destinatario = UsuarioRepo.buscar_por_id(self.db, destinatario_id)

        if not remetente:
            raise ValueError(f"Remetente com id={remetente_id} não encontrado.")
        if not destinatario:
            raise ValueError(f"Destinatário com id={destinatario_id} não encontrado.")

        mensagem = MensagemRepo.criar(self.db, {
            "remetente_id":    remetente_id,
            "destinatario_id": destinatario_id,
            "conteudo":        conteudo,
        })

        # Monta evento e notifica observers — padrão Observer em ação
        evento = EventoObs(
            tipo="mensagem_recebida",
            payload={
                "mensagem_id":   mensagem.id,
                "usuario_id":    destinatario.id,
                "email":         destinatario.email,
                "de":            remetente.nome,
                "preview":       conteudo[:50],
            },
        )
        self.notificar(evento)  # PushNotifier, EmailNotifier e BadgeNotifier acionados aqui

        return {
            "mensagem_id":    mensagem.id,
            "remetente":      remetente.nome,
            "destinatario":   destinatario.nome,
            "conteudo":       conteudo,
        }

    def buscar_mensagem(self, mensagem_id: int) -> dict:
        """Retorna uma mensagem pelo ID."""
        mensagem = MensagemRepo.buscar_por_id(self.db, mensagem_id)
        if not mensagem:
            raise ValueError(f"Mensagem com id={mensagem_id} não encontrada.")
        return {
            "mensagem_id":    mensagem.id,
            "remetente_id":   mensagem.remetente_id,
            "destinatario_id": mensagem.destinatario_id,
            "conteudo":       mensagem.conteudo,
            "created_at":     mensagem.created_at.isoformat(),
        }

    def listar_conversa(self, usuario_id_1: int, usuario_id_2: int) -> list[dict]:
        """Retorna o histórico de mensagens entre dois usuários."""
        mensagens = MensagemRepo.listar_conversa(self.db, usuario_id_1, usuario_id_2)
        return [
            {
                "mensagem_id":    m.id,
                "remetente_id":   m.remetente_id,
                "destinatario_id": m.destinatario_id,
                "conteudo":       m.conteudo,
                "created_at":     m.created_at.isoformat(),
            }
            for m in mensagens
        ]

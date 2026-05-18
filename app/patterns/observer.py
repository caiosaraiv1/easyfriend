"""
patterns/observer.py
EasyFriend – Padrão Observer
Desacopla a geração de eventos (match, mensagem) dos canais de notificação.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Estrutura de evento
# ---------------------------------------------------------------------------

@dataclass
class Evento:
    """Transporta os dados de um evento gerado pelo sistema."""
    tipo: str          # ex: "match_criado", "mensagem_recebida"
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return f"[{self.timestamp.isoformat()}] {self.tipo} → {self.payload}"


# ---------------------------------------------------------------------------
# Interfaces (contratos)
# ---------------------------------------------------------------------------

class NotificacaoObserver(ABC):
    """
    Interface Observer.
    Todo canal de saída (push, e-mail, badge…) deve implementar `atualizar`.
    """

    @abstractmethod
    def atualizar(self, evento: Evento) -> None:
        """Recebe e processa um evento publicado pelo Subject."""


class EventoSubject(ABC):
    """
    Interface Subject.
    Qualquer serviço que gere eventos (RadarService, ChatService…)
    deve herdar desta classe e chamar `self.notificar(evento)` no momento certo.
    """

    def __init__(self) -> None:
        self._observers: list[NotificacaoObserver] = []

    def inscrever(self, obs: NotificacaoObserver) -> None:
        """Registra um observer para receber eventos futuros."""
        if obs not in self._observers:
            self._observers.append(obs)

    def remover(self, obs: NotificacaoObserver) -> None:
        """Remove um observer previamente registrado."""
        self._observers.remove(obs)

    def notificar(self, evento: Evento) -> None:
        """Dispara `atualizar` em todos os observers registrados."""
        for obs in self._observers:
            obs.atualizar(evento)


# ---------------------------------------------------------------------------
# Observers concretos
# ---------------------------------------------------------------------------

class PushNotifier(NotificacaoObserver):
    """
    Observador concreto: simula envio de notificação push.
    Em produção substituiria por chamada à APNs/FCM.
    """

    def atualizar(self, evento: Evento) -> None:
        usuario_id = evento.payload.get("usuario_id", "?")
        print(f"[PushNotifier] 📲  Push enviado → usuário {usuario_id} | evento: {evento.tipo}")


class EmailNotifier(NotificacaoObserver):
    """
    Observador concreto: simula envio de e-mail.
    Em produção substituiria por chamada ao SendGrid/SES.
    """

    def atualizar(self, evento: Evento) -> None:
        email = evento.payload.get("email", "sem-email@easyfriend.app")
        print(f"[EmailNotifier] ✉️   E-mail enviado → {email} | evento: {evento.tipo}")


class BadgeNotifier(NotificacaoObserver):
    """
    Observador concreto: incrementa o contador de notificações não lidas.
    Em produção faria UPDATE no BD (tabela notificacoes ou usuarios).
    """

    def __init__(self) -> None:
        self._contadores: dict[str, int] = {}  # usuario_id → contagem

    def atualizar(self, evento: Evento) -> None:
        usuario_id = str(evento.payload.get("usuario_id", "desconhecido"))
        self._contadores[usuario_id] = self._contadores.get(usuario_id, 0) + 1
        count = self._contadores[usuario_id]
        print(f"[BadgeNotifier] 🔴  Badge atualizado → usuário {usuario_id} | total não lidas: {count}")

    def contador(self, usuario_id: str) -> int:
        return self._contadores.get(usuario_id, 0)


# ---------------------------------------------------------------------------
# Demo rápida (python -m patterns.observer)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from dataclasses import dataclass as _dc

    # Simula um RadarService disparando um match
    class _RadarDemo(EventoSubject):
        def criar_match(self, usuario_id: int, email: str, outro_id: int) -> None:
            evento = Evento(
                tipo="match_criado",
                payload={"usuario_id": usuario_id, "email": email, "outro_usuario_id": outro_id},
            )
            print(f"\n🟢 Match detectado entre usuário {usuario_id} e {outro_id}. Notificando observers…\n")
            self.notificar(evento)

    radar = _RadarDemo()
    radar.inscrever(PushNotifier())
    radar.inscrever(EmailNotifier())
    radar.inscrever(BadgeNotifier())

    radar.criar_match(usuario_id=1, email="alice@example.com", outro_id=2)
    radar.criar_match(usuario_id=1, email="alice@example.com", outro_id=3)

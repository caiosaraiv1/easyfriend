"""
app/services/agenda_service.py
AgendaService — filtra eventos da Agenda Cultural.

Usa BuscaContext (Strategy): filtra eventos pelo critério escolhido
na tela do iOS, sem nenhum if/else espalhado.
"""

from sqlalchemy.orm import Session

from patterns.strategy import (
    BuscaContext,
    Consulta,
    Evento as EventoStrategy,
    criterio_para_strategy,
)
from models.repositorios_CRUD import EventoRepo


class AgendaService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_eventos(self, criterio: str, valor: str,
                       lat: float = 0.0, lon: float = 0.0,
                       raio_km: float = 10.0) -> list[EventoStrategy]:
        """
        Busca eventos aplicando a estratégia escolhida pelo usuário na tela.
        Nenhum if/else aqui — BuscaContext delega para a estratégia correta.
        """
        todos = EventoRepo.listar(self.db)

        # Converte models do banco para dataclass da Strategy
        eventos_strategy = [
            EventoStrategy(
                id=e.id,
                titulo=e.titulo,
                tipo=e.tipo,
                idioma=e.idioma,
                lat=e.lat or 0.0,
                lon=e.lon or 0.0,
            )
            for e in todos
        ]

        ctx = BuscaContext(criterio_para_strategy(criterio))
        consulta = Consulta(valor=valor, lat=lat, lon=lon, raio_km=raio_km)
        resultado = ctx.executar(consulta, eventos_strategy)
        return resultado.itens

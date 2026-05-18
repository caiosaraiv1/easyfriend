"""
app/services/radar_service.py
RadarService — coração do Radar do EasyFriend.

Implementa EventoSubject (Observer): ao detectar um match, notifica
todos os observers inscritos (PushNotifier, EmailNotifier, BadgeNotifier).

Usa BuscaContext (Strategy): filtra usuários pelo critério escolhido
na tela do iOS, sem nenhum if/else espalhado.
"""

from sqlalchemy.orm import Session

from patterns.observer import (
    EventoSubject,
    Evento as EventoObs,
    PushNotifier,
    EmailNotifier,
    BadgeNotifier,
)
from patterns.strategy import (
    BuscaContext,
    Consulta,
    Usuario as UsuarioStrategy,
    criterio_para_strategy,
)
from models.repositorios_CRUD import MatchRepo, UsuarioRepo


class RadarService(EventoSubject):
    """
    Serviço do Radar.
    Herda EventoSubject para poder chamar self.notificar(evento)
    sempre que um match for criado.
    """

    def __init__(self, db: Session) -> None:
        super().__init__()
        self.db = db

        # Registra os observers na inicialização do serviço
        self.inscrever(PushNotifier())
        self.inscrever(EmailNotifier())
        self.inscrever(BadgeNotifier())

    # ------------------------------------------------------------------
    # Busca com Strategy
    # ------------------------------------------------------------------

    def buscar_usuarios(self, criterio: str, valor: str,
                        lat: float = 0.0, lon: float = 0.0,
                        raio_km: float = 10.0) -> list[UsuarioStrategy]:
        """
        Busca usuários aplicando a estratégia escolhida pelo usuário na tela.
        Nenhum if/else aqui — BuscaContext delega para a estratégia correta.
        """
        todos = UsuarioRepo.listar(self.db)

        # Converte models do banco para dataclass da Strategy
        usuarios_strategy = [
            UsuarioStrategy(
                id=u.id,
                nome=u.nome,
                idioma=u.idioma,
                pais_origem=u.pais_origem,
                lat=u.lat or 0.0,
                lon=u.lon or 0.0,
            )
            for u in todos
        ]

        ctx = BuscaContext(criterio_para_strategy(criterio))
        consulta = Consulta(valor=valor, lat=lat, lon=lon, raio_km=raio_km)
        resultado = ctx.executar(consulta, usuarios_strategy)
        return resultado.itens

    # ------------------------------------------------------------------
    # Criação de match com Observer
    # ------------------------------------------------------------------

    def criar_match(self, usuario_a_id: int, usuario_b_id: int,
                    criterio: str = "idioma") -> dict:
        """
        Cria um match no banco e dispara o Observer para todos os canais
        de notificação inscritos (push, e-mail, badge).
        """
        repo_u = UsuarioRepo
        repo_m = MatchRepo

        usuario_a = UsuarioRepo.buscar_por_id(self.db, usuario_a_id)
        usuario_b = UsuarioRepo.buscar_por_id(self.db, usuario_b_id)

        if not usuario_a or not usuario_b:
            raise ValueError("Um ou ambos os usuários não foram encontrados.")

        # Persiste o match no banco
        match = MatchRepo.criar(self.db, {
            "usuario_id_1": usuario_a_id,
            "usuario_id_2": usuario_b_id,
            "status": "pendente"
        })

        # Monta o evento e notifica todos os observers — padrão Observer
        evento = EventoObs(
            tipo="match_criado",
            payload={
                "match_id":    match.id,
                "usuario_id":  usuario_a.id,
                "email":       usuario_a.email,
                "outro_usuario": usuario_b.nome,
                "criterio":    criterio,
            },
        )
        self.notificar(evento)  # PushNotifier, EmailNotifier e BadgeNotifier são acionados aqui

        return {
            "match_id":   match.id,
            "usuario_a":  usuario_a.nome,
            "usuario_b":  usuario_b.nome,
            "criterio":   criterio,
        }

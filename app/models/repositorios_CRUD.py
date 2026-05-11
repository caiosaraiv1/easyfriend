# =============================================================
# EasyFriend - Repositórios CRUD
# Scrabgadun - Grupo 5 | Mackenzie | Engenharia de Software
# M3-04: UsuarioRepo, EventoRepo, MatchRepo, MensagemRepo
# =============================================================
#
# Como usar (exemplo no M1 - RadarService):
#   from app.models.repositorios import UsuarioRepo, MatchRepo
#   usuarios = UsuarioRepo.listar(db)
#   match    = MatchRepo.criar(db, {"usuario_id_1": 1, "usuario_id_2": 3})
#
# Todos os métodos recebem `db` como primeiro argumento.
# O `db` é a sessão do SQLAlchemy — vem do FastAPI via injeção
# de dependência (responsabilidade do M1 configurar).
# =============================================================

from sqlalchemy.orm import Session
from app.models.db_models import Usuario, Evento, Match, Mensagem, Apadrinhamento


# =============================================================
# USUARIO REPO
# Gerencia a tabela `usuarios`
# Usado por: RadarService (Strategy), AuthService (login)
# =============================================================
class UsuarioRepo:

    @staticmethod
    def criar(db: Session, dados: dict) -> Usuario:
        """
        Insere um novo usuário no banco.

        Exemplo:
            usuario = UsuarioRepo.criar(db, {
                "nome": "Carlos Silva",
                "email": "carlos@email.com",
                "senha_hash": "hash_aqui",
                "idioma": "pt",
                "pais_origem": "Brasil",
                "lat": -23.5505,
                "lon": -46.6333
            })
        """
        usuario = Usuario(**dados)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def buscar_por_id(db: Session, usuario_id: int) -> Usuario | None:
        """
        Retorna o usuário pelo ID ou None se não existir.

        Exemplo:
            usuario = UsuarioRepo.buscar_por_id(db, 1)
        """
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    @staticmethod
    def buscar_por_email(db: Session, email: str) -> Usuario | None:
        """
        Retorna o usuário pelo e-mail (usado no login/auth).

        Exemplo:
            usuario = UsuarioRepo.buscar_por_email(db, "carlos@email.com")
        """
        return db.query(Usuario).filter(Usuario.email == email).first()

    @staticmethod
    def listar(db: Session) -> list[Usuario]:
        """
        Retorna todos os usuários cadastrados.
        Usado pelo RadarService para aplicar o padrão Strategy.

        Exemplo:
            usuarios = UsuarioRepo.listar(db)
        """
        return db.query(Usuario).all()

    @staticmethod
    def atualizar(db: Session, usuario_id: int, dados: dict) -> Usuario | None:
        """
        Atualiza campos de um usuário existente.
        Retorna o usuário atualizado ou None se não encontrar.

        Exemplo:
            usuario = UsuarioRepo.atualizar(db, 1, {"idioma": "en", "lat": -23.56})
        """
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return None
        for campo, valor in dados.items():
            setattr(usuario, campo, valor)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def deletar(db: Session, usuario_id: int) -> bool:
        """
        Remove um usuário do banco. Retorna True se deletou, False se não achou.

        Exemplo:
            sucesso = UsuarioRepo.deletar(db, 1)
        """
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return False
        db.delete(usuario)
        db.commit()
        return True


# =============================================================
# EVENTO REPO
# Gerencia a tabela `eventos`
# Usado por: AgendaService (Strategy - BuscaPorTipoEvento,
#            BuscaPorIdioma)
# =============================================================
class EventoRepo:

    @staticmethod
    def criar(db: Session, dados: dict) -> Evento:
        """
        Insere um novo evento no banco.

        Exemplo:
            evento = EventoRepo.criar(db, {
                "titulo": "Show de Música Latina",
                "tipo": "musica",
                "idioma": "es",
                "lat": -23.56,
                "lon": -46.65,
                "data_evento": "2026-05-20 19:00:00"
            })
        """
        evento = Evento(**dados)
        db.add(evento)
        db.commit()
        db.refresh(evento)
        return evento

    @staticmethod
    def buscar_por_id(db: Session, evento_id: int) -> Evento | None:
        """
        Retorna o evento pelo ID ou None se não existir.

        Exemplo:
            evento = EventoRepo.buscar_por_id(db, 1)
        """
        return db.query(Evento).filter(Evento.id == evento_id).first()

    @staticmethod
    def listar(db: Session) -> list[Evento]:
        """
        Retorna todos os eventos cadastrados.
        Usado pelo AgendaService para aplicar o padrão Strategy.

        Exemplo:
            eventos = EventoRepo.listar(db)
        """
        return db.query(Evento).all()

    @staticmethod
    def listar_por_tipo(db: Session, tipo: str) -> list[Evento]:
        """
        Retorna eventos filtrados por tipo.
        Atalho direto para BuscaPorTipoEvento sem Strategy.

        Exemplo:
            eventos = EventoRepo.listar_por_tipo(db, "musica")
        """
        return db.query(Evento).filter(Evento.tipo == tipo).all()

    @staticmethod
    def listar_por_idioma(db: Session, idioma: str) -> list[Evento]:
        """
        Retorna eventos filtrados por idioma.
        Atalho direto para BuscaPorIdioma sem Strategy.

        Exemplo:
            eventos = EventoRepo.listar_por_idioma(db, "pt")
        """
        return db.query(Evento).filter(Evento.idioma == idioma).all()

    @staticmethod
    def atualizar(db: Session, evento_id: int, dados: dict) -> Evento | None:
        """
        Atualiza campos de um evento existente.
        Retorna o evento atualizado ou None se não encontrar.

        Exemplo:
            evento = EventoRepo.atualizar(db, 1, {"tipo": "arte"})
        """
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            return None
        for campo, valor in dados.items():
            setattr(evento, campo, valor)
        db.commit()
        db.refresh(evento)
        return evento

    @staticmethod
    def deletar(db: Session, evento_id: int) -> bool:
        """
        Remove um evento do banco. Retorna True se deletou, False se não achou.

        Exemplo:
            sucesso = EventoRepo.deletar(db, 1)
        """
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            return False
        db.delete(evento)
        db.commit()
        return True


# =============================================================
# MATCH REPO
# Gerencia a tabela `matches`
# Usado por: RadarService — ao criar match, aciona Observer (M1)
# =============================================================
class MatchRepo:

    @staticmethod
    def criar(db: Session, dados: dict) -> Match:
        """
        Insere um novo match no banco.
        Após chamar esse método, o RadarService aciona o Observer.

        Exemplo:
            match = MatchRepo.criar(db, {
                "usuario_id_1": 1,
                "usuario_id_2": 3,
                "status": "pendente"
            })
        """
        match = Match(**dados)
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def buscar_por_id(db: Session, match_id: int) -> Match | None:
        """
        Retorna o match pelo ID ou None se não existir.

        Exemplo:
            match = MatchRepo.buscar_por_id(db, 1)
        """
        return db.query(Match).filter(Match.id == match_id).first()

    @staticmethod
    def listar(db: Session) -> list[Match]:
        """
        Retorna todos os matches cadastrados.

        Exemplo:
            matches = MatchRepo.listar(db)
        """
        return db.query(Match).all()

    @staticmethod
    def listar_por_usuario(db: Session, usuario_id: int) -> list[Match]:
        """
        Retorna todos os matches de um usuário específico
        (tanto como usuario_id_1 quanto usuario_id_2).

        Exemplo:
            matches = MatchRepo.listar_por_usuario(db, 1)
        """
        return db.query(Match).filter(
            (Match.usuario_id_1 == usuario_id) |
            (Match.usuario_id_2 == usuario_id)
        ).all()

    @staticmethod
    def atualizar(db: Session, match_id: int, dados: dict) -> Match | None:
        """
        Atualiza campos de um match existente.
        Usado pelo M4 no endpoint PATCH /radar/matches/{id}/aceitar.

        Exemplo:
            match = MatchRepo.atualizar(db, 1, {"status": "aceito"})
        """
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return None
        for campo, valor in dados.items():
            setattr(match, campo, valor)
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def deletar(db: Session, match_id: int) -> bool:
        """
        Remove um match do banco. Retorna True se deletou, False se não achou.

        Exemplo:
            sucesso = MatchRepo.deletar(db, 1)
        """
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return False
        db.delete(match)
        db.commit()
        return True


# =============================================================
# MENSAGEM REPO
# Gerencia a tabela `mensagens`
# Usado por: ChatService — ao criar mensagem, aciona Observer (M1)
# =============================================================
class MensagemRepo:

    @staticmethod
    def criar(db: Session, dados: dict) -> Mensagem:
        """
        Insere uma nova mensagem no banco.
        Após chamar esse método, o ChatService aciona o Observer.

        Exemplo:
            mensagem = MensagemRepo.criar(db, {
                "remetente_id": 1,
                "destinatario_id": 3,
                "conteudo": "Olá, tudo bem?"
            })
        """
        mensagem = Mensagem(**dados)
        db.add(mensagem)
        db.commit()
        db.refresh(mensagem)
        return mensagem

    @staticmethod
    def buscar_por_id(db: Session, mensagem_id: int) -> Mensagem | None:
        """
        Retorna a mensagem pelo ID ou None se não existir.

        Exemplo:
            mensagem = MensagemRepo.buscar_por_id(db, 1)
        """
        return db.query(Mensagem).filter(Mensagem.id == mensagem_id).first()

    @staticmethod
    def listar(db: Session) -> list[Mensagem]:
        """
        Retorna todas as mensagens cadastradas.

        Exemplo:
            mensagens = MensagemRepo.listar(db)
        """
        return db.query(Mensagem).all()

    @staticmethod
    def listar_conversa(db: Session, usuario_id_1: int, usuario_id_2: int) -> list[Mensagem]:
        """
        Retorna todas as mensagens trocadas entre dois usuários,
        ordenadas por data (mais antigas primeiro).
        Usado pelo ChatService para carregar histórico.

        Exemplo:
            conversa = MensagemRepo.listar_conversa(db, 1, 3)
        """
        return db.query(Mensagem).filter(
            ((Mensagem.remetente_id == usuario_id_1) & (Mensagem.destinatario_id == usuario_id_2)) |
            ((Mensagem.remetente_id == usuario_id_2) & (Mensagem.destinatario_id == usuario_id_1))
        ).order_by(Mensagem.created_at.asc()).all()

    @staticmethod
    def atualizar(db: Session, mensagem_id: int, dados: dict) -> Mensagem | None:
        """
        Atualiza campos de uma mensagem existente.

        Exemplo:
            mensagem = MensagemRepo.atualizar(db, 1, {"conteudo": "Texto editado"})
        """
        mensagem = db.query(Mensagem).filter(Mensagem.id == mensagem_id).first()
        if not mensagem:
            return None
        for campo, valor in dados.items():
            setattr(mensagem, campo, valor)
        db.commit()
        db.refresh(mensagem)
        return mensagem

    @staticmethod
    def deletar(db: Session, mensagem_id: int) -> bool:
        """
        Remove uma mensagem do banco. Retorna True se deletou, False se não achou.

        Exemplo:
            sucesso = MensagemRepo.deletar(db, 1)
        """
        mensagem = db.query(Mensagem).filter(Mensagem.id == mensagem_id).first()
        if not mensagem:
            return False
        db.delete(mensagem)
        db.commit()
        return True

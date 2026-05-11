# =============================================================
# EasyFriend - SQLAlchemy ORM Models
# Scrabgadun - Grupo 5 | Mackenzie | Engenharia de Software
# M3-03: Mapeamento das tabelas do banco para classes Python
# =============================================================

from sqlalchemy import (
    Column, Integer, String, Text,
    Double, TIMESTAMP, ForeignKey, UniqueConstraint, CheckConstraint,
    func, create_engine
)
from sqlalchemy.orm import declarative_base, relationship
import os

# =============================================================
# BASE E CONEXÃO
# O DATABASE_URL vem do .env (configurado pelo M5 no Docker)
# Exemplo: postgresql://postgres:postgres@db:5432/easyfriend
# =============================================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/easyfriend")

engine = create_engine(DATABASE_URL)

# Base é a classe pai de todos os models
Base = declarative_base()


# =============================================================
# MODEL: Usuario
# Corresponde à tabela `usuarios` do schema.sql
# Colunas idioma, pais_origem, lat e lon são usadas pelo
# padrão Strategy no RadarService (M1)
# =============================================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id          = Column(Integer,   primary_key=True, autoincrement=True)
    nome        = Column(String(100),  nullable=False)
    email       = Column(String(255),  nullable=False, unique=True)
    senha_hash  = Column(String(255),  nullable=False)
    idioma      = Column(String(50),   nullable=False)   # ex: "pt", "es", "fr"
    pais_origem = Column(String(100),  nullable=False)   # ex: "Brasil", "Venezuela"
    lat         = Column(Double,       nullable=False, default=0.0)
    lon         = Column(Double,       nullable=False, default=0.0)
    created_at  = Column(TIMESTAMP,    nullable=False, server_default=func.now())

    # Relacionamentos — permitem navegar entre objetos no Python
    # ex: usuario.matches_enviados para ver todos os matches do usuário
    matches_enviados     = relationship("Match",         foreign_keys="Match.usuario_id_1",  back_populates="usuario1")
    matches_recebidos    = relationship("Match",         foreign_keys="Match.usuario_id_2",  back_populates="usuario2")
    mensagens_enviadas   = relationship("Mensagem",      foreign_keys="Mensagem.remetente_id",    back_populates="remetente")
    mensagens_recebidas  = relationship("Mensagem",      foreign_keys="Mensagem.destinatario_id", back_populates="destinatario")
    apadrinhamentos_como_padrinho = relationship("Apadrinhamento", foreign_keys="Apadrinhamento.padrinho_id", back_populates="padrinho")
    apadrinhamentos_como_afilhado = relationship("Apadrinhamento", foreign_keys="Apadrinhamento.afilhado_id", back_populates="afilhado")

    def __repr__(self):
        return f"<Usuario id={self.id} nome='{self.nome}' idioma='{self.idioma}' pais='{self.pais_origem}'>"


# =============================================================
# MODEL: Match
# Corresponde à tabela `matches` do schema.sql
# Criado pelo RadarService — aciona o padrão Observer (M1)
# =============================================================
class Match(Base):
    __tablename__ = "matches"

    id           = Column(Integer,    primary_key=True, autoincrement=True)
    usuario_id_1 = Column(Integer,    ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    usuario_id_2 = Column(Integer,    ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    status       = Column(String(20), nullable=False, default="pendente")  # pendente | aceito | recusado
    created_at   = Column(TIMESTAMP,  nullable=False, server_default=func.now())

    __table_args__ = (
        # Impede match duplicado entre o mesmo par
        UniqueConstraint("usuario_id_1", "usuario_id_2", name="uq_match_par"),
        # Impede match consigo mesmo
        CheckConstraint("usuario_id_1 <> usuario_id_2", name="chk_match_diferente"),
    )

    # Relacionamentos
    usuario1 = relationship("Usuario", foreign_keys=[usuario_id_1], back_populates="matches_enviados")
    usuario2 = relationship("Usuario", foreign_keys=[usuario_id_2], back_populates="matches_recebidos")

    def __repr__(self):
        return f"<Match id={self.id} u1={self.usuario_id_1} u2={self.usuario_id_2} status='{self.status}'>"


# =============================================================
# MODEL: Evento
# Corresponde à tabela `eventos` do schema.sql
# Filtrado pelo padrão Strategy no AgendaService (M1):
# BuscaPorTipoEvento usa `tipo`, BuscaPorIdioma usa `idioma`
# =============================================================
class Evento(Base):
    __tablename__ = "eventos"

    id          = Column(Integer,    primary_key=True, autoincrement=True)
    titulo      = Column(String(200), nullable=False)
    tipo        = Column(String(100), nullable=False)  # ex: "gastronomia", "musica", "arte"
    idioma      = Column(String(50),  nullable=False)  # idioma principal do evento
    lat         = Column(Double,      nullable=False, default=0.0)
    lon         = Column(Double,      nullable=False, default=0.0)
    data_evento = Column(TIMESTAMP,   nullable=False)
    created_at  = Column(TIMESTAMP,   nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Evento id={self.id} titulo='{self.titulo}' tipo='{self.tipo}'>"


# =============================================================
# MODEL: Mensagem
# Corresponde à tabela `mensagens` do schema.sql
# ChatService aciona o padrão Observer ao inserir aqui (M1)
# =============================================================
class Mensagem(Base):
    __tablename__ = "mensagens"

    id              = Column(Integer,   primary_key=True, autoincrement=True)
    remetente_id    = Column(Integer,   ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    destinatario_id = Column(Integer,   ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    conteudo        = Column(Text,      nullable=False)
    created_at      = Column(TIMESTAMP, nullable=False, server_default=func.now())

    __table_args__ = (
        # Impede mensagem para si mesmo
        CheckConstraint("remetente_id <> destinatario_id", name="chk_msg_diferente"),
    )

    # Relacionamentos
    remetente    = relationship("Usuario", foreign_keys=[remetente_id],    back_populates="mensagens_enviadas")
    destinatario = relationship("Usuario", foreign_keys=[destinatario_id], back_populates="mensagens_recebidas")

    def __repr__(self):
        return f"<Mensagem id={self.id} de={self.remetente_id} para={self.destinatario_id}>"


# =============================================================
# MODEL: Apadrinhamento
# Corresponde à tabela `apadrinhamentos` do schema.sql
# Observer é acionado no PATCH /{id}/aceitar (M4-03)
# =============================================================
class Apadrinhamento(Base):
    __tablename__ = "apadrinhamentos"

    id          = Column(Integer,    primary_key=True, autoincrement=True)
    padrinho_id = Column(Integer,    ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    afilhado_id = Column(Integer,    ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    status      = Column(String(20), nullable=False, default="pendente")  # pendente | aceito | recusado
    created_at  = Column(TIMESTAMP,  nullable=False, server_default=func.now())

    __table_args__ = (
        # Impede solicitação duplicada entre o mesmo par
        UniqueConstraint("padrinho_id", "afilhado_id", name="uq_apadrinhamento_par"),
        # Impede apadrinhar a si mesmo
        CheckConstraint("padrinho_id <> afilhado_id", name="chk_apadrinhamento_diferente"),
    )

    # Relacionamentos
    padrinho = relationship("Usuario", foreign_keys=[padrinho_id], back_populates="apadrinhamentos_como_padrinho")
    afilhado = relationship("Usuario", foreign_keys=[afilhado_id], back_populates="apadrinhamentos_como_afilhado")

    def __repr__(self):
        return f"<Apadrinhamento id={self.id} padrinho={self.padrinho_id} afilhado={self.afilhado_id} status='{self.status}'>"

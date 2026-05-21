"""
tests/test_services.py
Testes de integração para Services e Repositórios CRUD do EasyFriend.
Usa SQLite em memória — sem necessidade de PostgreSQL rodando.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Banco em memória com SQLite
DATABASE_URL = "sqlite:///:memory:"

# Precisamos reconfigurar o engine antes de importar os models
import os
os.environ["DATABASE_URL"] = DATABASE_URL

from models.db_models import Base, Usuario, Evento, Match, Mensagem, Apadrinhamento
from models.repositorios_CRUD import (
    UsuarioRepo, EventoRepo, MatchRepo, MensagemRepo
)
from services.radar_service import RadarService
from services.chat_service import ChatService
from services.agenda_service import AgendaService
from services.apadrinhamento_service import ApadrinhamentoService


# -----------------------------------------------------------------------
# Setup: engine SQLite em memória + tabelas
# -----------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SQLite não suporta CHECK CONSTRAINTS por padrão — habilitar
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Base.metadata.create_all(bind=engine)

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Sessão isolada por teste — rollback ao final."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSession(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# -----------------------------------------------------------------------
# Fixtures de dados reutilizáveis
# -----------------------------------------------------------------------

@pytest.fixture
def usuario_alice(db):
    return UsuarioRepo.criar(db, {
        "nome": "Alice",
        "email": "alice@easyfriend.app",
        "senha_hash": "hash_alice",
        "idioma": "ja",
        "pais_origem": "Japão",
        "lat": -23.550,
        "lon": -46.633,
    })


@pytest.fixture
def usuario_carlos(db):
    return UsuarioRepo.criar(db, {
        "nome": "Carlos",
        "email": "carlos@easyfriend.app",
        "senha_hash": "hash_carlos",
        "idioma": "pt",
        "pais_origem": "Brasil",
        "lat": -23.560,
        "lon": -46.640,
    })


@pytest.fixture
def evento_sushi(db):
    return EventoRepo.criar(db, {
        "titulo": "Festival de Sushi",
        "tipo": "gastronomia",
        "idioma": "ja",
        "lat": -23.550,
        "lon": -46.633,
        "data_evento": datetime(2026, 6, 10, 18, 0, 0),
    })


# =======================================================================
# REPOSITÓRIOS CRUD
# =======================================================================

class TestUsuarioRepo:

    def test_criar_usuario(self, db):
        u = UsuarioRepo.criar(db, {
            "nome": "Bob",
            "email": "bob@test.com",
            "senha_hash": "hash",
            "idioma": "en",
            "pais_origem": "EUA",
            "lat": 0.0, "lon": 0.0,
        })
        assert u.id is not None
        assert u.nome == "Bob"

    def test_buscar_por_id_existente(self, db, usuario_alice):
        encontrado = UsuarioRepo.buscar_por_id(db, usuario_alice.id)
        assert encontrado is not None
        assert encontrado.nome == "Alice"

    def test_buscar_por_id_inexistente(self, db):
        assert UsuarioRepo.buscar_por_id(db, 9999) is None

    def test_buscar_por_email(self, db, usuario_alice):
        encontrado = UsuarioRepo.buscar_por_email(db, "alice@easyfriend.app")
        assert encontrado is not None
        assert encontrado.id == usuario_alice.id

    def test_buscar_por_email_inexistente(self, db):
        assert UsuarioRepo.buscar_por_email(db, "nao@existe.com") is None

    def test_listar_usuarios(self, db, usuario_alice, usuario_carlos):
        todos = UsuarioRepo.listar(db)
        ids = [u.id for u in todos]
        assert usuario_alice.id in ids
        assert usuario_carlos.id in ids

    def test_atualizar_usuario(self, db, usuario_alice):
        atualizado = UsuarioRepo.atualizar(db, usuario_alice.id, {"idioma": "en"})
        assert atualizado.idioma == "en"

    def test_atualizar_usuario_inexistente(self, db):
        assert UsuarioRepo.atualizar(db, 9999, {"idioma": "en"}) is None

    def test_deletar_usuario(self, db, usuario_alice):
        assert UsuarioRepo.deletar(db, usuario_alice.id) is True
        assert UsuarioRepo.buscar_por_id(db, usuario_alice.id) is None

    def test_deletar_usuario_inexistente(self, db):
        assert UsuarioRepo.deletar(db, 9999) is False


class TestEventoRepo:

    def test_criar_evento(self, db):
        e = EventoRepo.criar(db, {
            "titulo": "Show de Jazz",
            "tipo": "musica",
            "idioma": "en",
            "lat": -23.548, "lon": -46.638,
            "data_evento": datetime(2026, 7, 1, 20, 0, 0),
        })
        assert e.id is not None
        assert e.titulo == "Show de Jazz"

    def test_buscar_por_id(self, db, evento_sushi):
        encontrado = EventoRepo.buscar_por_id(db, evento_sushi.id)
        assert encontrado is not None
        assert encontrado.titulo == "Festival de Sushi"

    def test_buscar_por_id_inexistente(self, db):
        assert EventoRepo.buscar_por_id(db, 9999) is None

    def test_listar_por_tipo(self, db, evento_sushi):
        EventoRepo.criar(db, {
            "titulo": "Show de Jazz",
            "tipo": "musica",
            "idioma": "en",
            "lat": 0.0, "lon": 0.0,
            "data_evento": datetime(2026, 7, 1),
        })
        gastronomia = EventoRepo.listar_por_tipo(db, "gastronomia")
        assert all(e.tipo == "gastronomia" for e in gastronomia)
        assert any(e.titulo == "Festival de Sushi" for e in gastronomia)

    def test_listar_por_idioma(self, db, evento_sushi):
        japoneses = EventoRepo.listar_por_idioma(db, "ja")
        assert all(e.idioma == "ja" for e in japoneses)

    def test_atualizar_evento(self, db, evento_sushi):
        atualizado = EventoRepo.atualizar(db, evento_sushi.id, {"tipo": "arte"})
        assert atualizado.tipo == "arte"

    def test_deletar_evento(self, db, evento_sushi):
        assert EventoRepo.deletar(db, evento_sushi.id) is True
        assert EventoRepo.buscar_por_id(db, evento_sushi.id) is None

    def test_deletar_evento_inexistente(self, db):
        assert EventoRepo.deletar(db, 9999) is False


class TestMatchRepo:

    def test_criar_match(self, db, usuario_alice, usuario_carlos):
        m = MatchRepo.criar(db, {
            "usuario_id_1": usuario_alice.id,
            "usuario_id_2": usuario_carlos.id,
            "status": "pendente",
        })
        assert m.id is not None
        assert m.status == "pendente"

    def test_buscar_match_por_id(self, db, usuario_alice, usuario_carlos):
        m = MatchRepo.criar(db, {
            "usuario_id_1": usuario_alice.id,
            "usuario_id_2": usuario_carlos.id,
        })
        encontrado = MatchRepo.buscar_por_id(db, m.id)
        assert encontrado is not None

    def test_listar_por_usuario(self, db, usuario_alice, usuario_carlos):
        MatchRepo.criar(db, {
            "usuario_id_1": usuario_alice.id,
            "usuario_id_2": usuario_carlos.id,
        })
        matches = MatchRepo.listar_por_usuario(db, usuario_alice.id)
        assert len(matches) >= 1

    def test_atualizar_status_match(self, db, usuario_alice, usuario_carlos):
        m = MatchRepo.criar(db, {
            "usuario_id_1": usuario_alice.id,
            "usuario_id_2": usuario_carlos.id,
        })
        atualizado = MatchRepo.atualizar(db, m.id, {"status": "aceito"})
        assert atualizado.status == "aceito"

    def test_deletar_match(self, db, usuario_alice, usuario_carlos):
        m = MatchRepo.criar(db, {
            "usuario_id_1": usuario_alice.id,
            "usuario_id_2": usuario_carlos.id,
        })
        assert MatchRepo.deletar(db, m.id) is True


class TestMensagemRepo:

    def test_criar_mensagem(self, db, usuario_alice, usuario_carlos):
        msg = MensagemRepo.criar(db, {
            "remetente_id": usuario_alice.id,
            "destinatario_id": usuario_carlos.id,
            "conteudo": "Olá Carlos!",
        })
        assert msg.id is not None
        assert msg.conteudo == "Olá Carlos!"

    def test_listar_conversa_bidirecional(self, db, usuario_alice, usuario_carlos):
        MensagemRepo.criar(db, {
            "remetente_id": usuario_alice.id,
            "destinatario_id": usuario_carlos.id,
            "conteudo": "Oi!",
        })
        MensagemRepo.criar(db, {
            "remetente_id": usuario_carlos.id,
            "destinatario_id": usuario_alice.id,
            "conteudo": "Tudo bem?",
        })
        conversa = MensagemRepo.listar_conversa(db, usuario_alice.id, usuario_carlos.id)
        assert len(conversa) == 2

    def test_deletar_mensagem(self, db, usuario_alice, usuario_carlos):
        msg = MensagemRepo.criar(db, {
            "remetente_id": usuario_alice.id,
            "destinatario_id": usuario_carlos.id,
            "conteudo": "Deletar isso",
        })
        assert MensagemRepo.deletar(db, msg.id) is True
        assert MensagemRepo.buscar_por_id(db, msg.id) is None


# =======================================================================
# SERVICES
# =======================================================================

class TestRadarService:

    def test_buscar_usuarios_por_idioma(self, db, usuario_alice, usuario_carlos):
        service = RadarService(db)
        resultado = service.buscar_usuarios(criterio="idioma", valor="ja")
        ids = [u.id for u in resultado]
        assert usuario_alice.id in ids
        assert usuario_carlos.id not in ids

    def test_buscar_usuarios_por_pais(self, db, usuario_alice, usuario_carlos):
        service = RadarService(db)
        resultado = service.buscar_usuarios(criterio="pais_origem", valor="Brasil")
        ids = [u.id for u in resultado]
        assert usuario_carlos.id in ids
        assert usuario_alice.id not in ids

    def test_buscar_usuarios_por_proximidade(self, db, usuario_alice, usuario_carlos):
        service = RadarService(db)
        resultado = service.buscar_usuarios(
            criterio="proximidade", valor="",
            lat=-23.550, lon=-46.633, raio_km=5
        )
        # alice e carlos estão próximos, devem aparecer
        assert len(resultado) >= 1

    def test_criar_match_dispara_observer(self, db, usuario_alice, usuario_carlos, capsys):
        service = RadarService(db)
        resultado = service.criar_match(usuario_alice.id, usuario_carlos.id)
        assert resultado["match_id"] is not None
        assert resultado["usuario_a"] == "Alice"
        assert resultado["usuario_b"] == "Carlos"
        saida = capsys.readouterr().out
        assert "PushNotifier" in saida
        assert "EmailNotifier" in saida

    def test_criar_match_usuario_inexistente(self, db, usuario_alice):
        service = RadarService(db)
        with pytest.raises(ValueError):
            service.criar_match(usuario_alice.id, 9999)

    def test_criterio_invalido_lanca_erro(self, db, usuario_alice):
        service = RadarService(db)
        with pytest.raises(ValueError):
            service.buscar_usuarios(criterio="criterio_invalido", valor="x")


class TestChatService:

    def test_enviar_mensagem(self, db, usuario_alice, usuario_carlos):
        service = ChatService(db)
        resultado = service.enviar_mensagem(
            remetente_id=usuario_alice.id,
            destinatario_id=usuario_carlos.id,
            conteudo="Olá, Carlos!"
        )
        assert resultado["mensagem_id"] is not None
        assert resultado["remetente"] == "Alice"
        assert resultado["destinatario"] == "Carlos"

    def test_enviar_mensagem_dispara_observer(self, db, usuario_alice, usuario_carlos, capsys):
        service = ChatService(db)
        service.enviar_mensagem(usuario_alice.id, usuario_carlos.id, "Oi!")
        saida = capsys.readouterr().out
        assert "PushNotifier" in saida

    def test_enviar_mensagem_remetente_inexistente(self, db, usuario_carlos):
        service = ChatService(db)
        with pytest.raises(ValueError):
            service.enviar_mensagem(9999, usuario_carlos.id, "Oi")

    def test_enviar_mensagem_destinatario_inexistente(self, db, usuario_alice):
        service = ChatService(db)
        with pytest.raises(ValueError):
            service.enviar_mensagem(usuario_alice.id, 9999, "Oi")

    def test_listar_conversa(self, db, usuario_alice, usuario_carlos):
        service = ChatService(db)
        service.enviar_mensagem(usuario_alice.id, usuario_carlos.id, "Mensagem 1")
        service.enviar_mensagem(usuario_carlos.id, usuario_alice.id, "Mensagem 2")
        conversa = service.listar_conversa(usuario_alice.id, usuario_carlos.id)
        assert len(conversa) == 2

    def test_buscar_mensagem_inexistente(self, db):
        service = ChatService(db)
        with pytest.raises(ValueError):
            service.buscar_mensagem(9999)


class TestAgendaService:

    def test_buscar_eventos_por_tipo(self, db, evento_sushi):
        EventoRepo.criar(db, {
            "titulo": "Show de Jazz",
            "tipo": "musica",
            "idioma": "en",
            "lat": 0.0, "lon": 0.0,
            "data_evento": datetime(2026, 7, 1),
        })
        service = AgendaService(db)
        resultado = service.buscar_eventos(criterio="tipo", valor="gastronomia")
        assert all(e.tipo == "gastronomia" for e in resultado)
        assert len(resultado) >= 1

    def test_buscar_eventos_por_idioma(self, db, evento_sushi):
        service = AgendaService(db)
        resultado = service.buscar_eventos(criterio="idioma", valor="ja")
        assert all(e.idioma == "ja" for e in resultado)

    def test_buscar_eventos_sem_resultado(self, db):
        service = AgendaService(db)
        resultado = service.buscar_eventos(criterio="tipo", valor="tipo_inexistente")
        assert resultado == []

    def test_criterio_invalido_lanca_erro(self, db):
        service = AgendaService(db)
        with pytest.raises(ValueError):
            service.buscar_eventos(criterio="xyz", valor="qualquer")


class TestApadrinhamentoService:

    def test_solicitar_apadrinhamento(self, db, usuario_alice, usuario_carlos):
        service = ApadrinhamentoService(db)
        resultado = service.solicitar(
            padrinho_id=usuario_alice.id,
            afilhado_id=usuario_carlos.id,
        )
        assert resultado["apadrinhamento_id"] is not None
        assert resultado["status"] == "pendente"
        assert resultado["padrinho"] == "Alice"
        assert resultado["afilhado"] == "Carlos"

    def test_aceitar_apadrinhamento_dispara_observer(self, db, usuario_alice, usuario_carlos, capsys):
        service = ApadrinhamentoService(db)
        sol = service.solicitar(usuario_alice.id, usuario_carlos.id)
        service.aceitar(sol["apadrinhamento_id"])
        saida = capsys.readouterr().out
        assert "PushNotifier" in saida
        assert "EmailNotifier" in saida

    def test_aceitar_atualiza_status(self, db, usuario_alice, usuario_carlos):
        service = ApadrinhamentoService(db)
        sol = service.solicitar(usuario_alice.id, usuario_carlos.id)
        resultado = service.aceitar(sol["apadrinhamento_id"])
        assert resultado["status"] == "aceito"

    def test_solicitar_padrinho_inexistente(self, db, usuario_carlos):
        service = ApadrinhamentoService(db)
        with pytest.raises(ValueError):
            service.solicitar(9999, usuario_carlos.id)

    def test_solicitar_afilhado_inexistente(self, db, usuario_alice):
        service = ApadrinhamentoService(db)
        with pytest.raises(ValueError):
            service.solicitar(usuario_alice.id, 9999)

    def test_aceitar_apadrinhamento_inexistente(self, db):
        service = ApadrinhamentoService(db)
        with pytest.raises(ValueError):
            service.aceitar(9999)

"""
tests/test_routes.py
Testes de API (HTTP) para todas as rotas do EasyFriend.
Usa FastAPI TestClient + SQLite em arquivo temporário — sem PostgreSQL.
"""

import os
import pytest
from datetime import datetime

os.environ["DATABASE_URL"] = "sqlite:///./test_routes.db"

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

TEST_DB = "sqlite:///./test_routes.db"
test_engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})

@event.listens_for(test_engine, "connect")
def set_pragma(dbapi_conn, _):
    c = dbapi_conn.cursor(); c.execute("PRAGMA foreign_keys=ON"); c.close()

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Injeta engine de teste antes de importar a app
import database as _db
_db.engine = test_engine
_db.SessionLocal = TestingSession

from models.db_models import Base
from models.repositorios_CRUD import UsuarioRepo, EventoRepo
from database import get_db
from main import app
from fastapi.testclient import TestClient

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, raise_server_exceptions=True)


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------

@pytest.fixture(autouse=True)
def limpar_banco():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def alice():
    db = TestingSession()
    u = UsuarioRepo.criar(db, {
        "nome": "Alice", "email": "alice@test.com", "senha_hash": "senha123",
        "idioma": "ja", "pais_origem": "Japão", "lat": -23.550, "lon": -46.633,
    })
    db.close()
    return u


@pytest.fixture
def carlos():
    db = TestingSession()
    u = UsuarioRepo.criar(db, {
        "nome": "Carlos", "email": "carlos@test.com", "senha_hash": "senha123",
        "idioma": "pt", "pais_origem": "Brasil", "lat": -23.560, "lon": -46.640,
    })
    db.close()
    return u


@pytest.fixture
def evento_gastronomia():
    db = TestingSession()
    e = EventoRepo.criar(db, {
        "titulo": "Festival de Sushi", "tipo": "gastronomia", "idioma": "ja",
        "lat": -23.550, "lon": -46.633, "data_evento": datetime(2026, 6, 10, 18, 0, 0),
    })
    db.close()
    return e


# =======================================================================
# HEALTH
# =======================================================================

class TestHealth:

    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["versao"] == "0.2.0"


# =======================================================================
# AUTH
# =======================================================================

class TestAuth:

    def test_login_sucesso(self, alice):
        r = client.post("/auth/login", data={"username": "alice@test.com", "password": "senha123"})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["nome"] == "Alice"

    def test_login_senha_errada(self, alice):
        r = client.post("/auth/login", data={"username": "alice@test.com", "password": "errada"})
        assert r.status_code == 401

    def test_login_usuario_inexistente(self):
        r = client.post("/auth/login", data={"username": "nao@existe.com", "password": "x"})
        assert r.status_code == 401

    def test_me_com_token_valido(self, alice):
        token = client.post("/auth/login", data={"username": "alice@test.com", "password": "senha123"}).json()["access_token"]
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["nome"] == "Alice"

    def test_me_sem_token(self):
        assert client.get("/auth/me").status_code == 401

    def test_me_token_invalido(self):
        assert client.get("/auth/me", headers={"Authorization": "Bearer invalido"}).status_code == 401


# =======================================================================
# RADAR
# =======================================================================

class TestRadar:

    def test_criar_match_201(self, alice, carlos):
        r = client.post("/radar/matches", json={"usuario_a_id": alice.id, "usuario_b_id": carlos.id, "criterio": "idioma"})
        assert r.status_code == 201
        assert r.json()["usuario_a"] == "Alice"
        assert r.json()["usuario_b"] == "Carlos"

    def test_criar_match_usuario_inexistente_404(self, alice):
        r = client.post("/radar/matches", json={"usuario_a_id": alice.id, "usuario_b_id": 9999, "criterio": "idioma"})
        assert r.status_code == 404

    def test_criar_match_duplicado_409(self, alice, carlos):
        payload = {"usuario_a_id": alice.id, "usuario_b_id": carlos.id, "criterio": "idioma"}
        client.post("/radar/matches", json=payload)
        r = client.post("/radar/matches", json=payload)
        assert r.status_code == 409

    def test_buscar_matches_por_idioma(self, alice, carlos):
        r = client.get("/radar/matches", params={"criterio": "idioma", "valor": "ja"})
        assert r.status_code == 200
        ids = [item["id"] for item in r.json()]
        assert alice.id in ids
        assert carlos.id not in ids

    def test_buscar_matches_por_pais(self, alice, carlos):
        r = client.get("/radar/matches", params={"criterio": "pais_origem", "valor": "Brasil"})
        assert r.status_code == 200
        assert carlos.id in [item["id"] for item in r.json()]

    def test_buscar_matches_criterio_invalido_400(self):
        r = client.get("/radar/matches", params={"criterio": "invalido", "valor": "x"})
        assert r.status_code == 400

    def test_buscar_matches_retorna_estrutura_correta(self, alice):
        r = client.get("/radar/matches", params={"criterio": "idioma", "valor": "ja"})
        assert r.status_code == 200
        item = r.json()[0]
        for campo in ["coordenada_lat", "coordenada_lon", "raio_privacidade_metros", "distancia_km"]:
            assert campo in item


# =======================================================================
# CHAT
# =======================================================================

class TestChat:

    def test_enviar_mensagem_201(self, alice, carlos):
        r = client.post("/chat/mensagens", json={"remetente_id": alice.id, "destinatario_id": carlos.id, "conteudo": "Oi!"})
        assert r.status_code == 201
        assert r.json()["remetente"] == "Alice"
        assert r.json()["destinatario"] == "Carlos"

    def test_enviar_mensagem_remetente_inexistente_404(self, carlos):
        r = client.post("/chat/mensagens", json={"remetente_id": 9999, "destinatario_id": carlos.id, "conteudo": "Oi"})
        assert r.status_code == 404

    def test_enviar_mensagem_destinatario_inexistente_404(self, alice):
        r = client.post("/chat/mensagens", json={"remetente_id": alice.id, "destinatario_id": 9999, "conteudo": "Oi"})
        assert r.status_code == 404

    def test_buscar_mensagem_por_id(self, alice, carlos):
        criada = client.post("/chat/mensagens", json={"remetente_id": alice.id, "destinatario_id": carlos.id, "conteudo": "Teste"}).json()
        r = client.get(f"/chat/mensagens/{criada['mensagem_id']}")
        assert r.status_code == 200
        assert r.json()["conteudo"] == "Teste"

    def test_buscar_mensagem_inexistente_404(self):
        assert client.get("/chat/mensagens/9999").status_code == 404

    def test_listar_conversa(self, alice, carlos):
        client.post("/chat/mensagens", json={"remetente_id": alice.id, "destinatario_id": carlos.id, "conteudo": "Oi"})
        client.post("/chat/mensagens", json={"remetente_id": carlos.id, "destinatario_id": alice.id, "conteudo": "Oi também"})
        r = client.get("/chat/conversa", params={"usuario_id_1": alice.id, "usuario_id_2": carlos.id})
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_listar_conversa_vazia(self, alice, carlos):
        r = client.get("/chat/conversa", params={"usuario_id_1": alice.id, "usuario_id_2": carlos.id})
        assert r.status_code == 200
        assert r.json() == []


# =======================================================================
# AGENDA
# =======================================================================

class TestAgenda:

    def test_criar_evento_201(self):
        r = client.post("/agenda/eventos", json={
            "titulo": "Show de Jazz", "tipo": "musica", "idioma": "en",
            "lat": -23.548, "lon": -46.638, "data_evento": "2026-07-01T20:00:00",
        })
        assert r.status_code == 201
        assert r.json()["titulo"] == "Show de Jazz"

    def test_listar_eventos_por_tipo(self, evento_gastronomia):
        r = client.get("/agenda/eventos", params={"criterio": "tipo", "valor": "gastronomia"})
        assert r.status_code == 200
        assert len(r.json()) >= 1
        assert all(e["tipo"] == "gastronomia" for e in r.json())

    def test_listar_eventos_por_idioma(self, evento_gastronomia):
        r = client.get("/agenda/eventos", params={"criterio": "idioma", "valor": "ja"})
        assert r.status_code == 200
        assert all(e["idioma"] == "ja" for e in r.json())

    def test_listar_eventos_sem_resultado(self):
        r = client.get("/agenda/eventos", params={"criterio": "tipo", "valor": "tipo_inexistente"})
        assert r.status_code == 200
        assert r.json() == []

    def test_listar_eventos_criterio_invalido_400(self):
        r = client.get("/agenda/eventos", params={"criterio": "invalido", "valor": "x"})
        assert r.status_code == 400

    def test_evento_retorna_campos_corretos(self):
        r = client.post("/agenda/eventos", json={
            "titulo": "Arte", "tipo": "arte", "idioma": "pt",
            "lat": 0.0, "lon": 0.0, "data_evento": "2026-08-15T10:00:00",
        })
        for campo in ["id", "titulo", "tipo", "idioma", "data_inicio"]:
            assert campo in r.json()


# =======================================================================
# APADRINHAMENTO
# =======================================================================

class TestApadrinhamento:

    def test_solicitar_apadrinhamento_201(self, alice, carlos):
        r = client.post("/apadrinhamento/solicitar", json={"padrinho_id": alice.id, "afilhado_id": carlos.id})
        assert r.status_code == 201
        assert r.json()["status"] == "pendente"
        assert r.json()["padrinho"] == "Alice"

    def test_solicitar_padrinho_inexistente_404(self, carlos):
        r = client.post("/apadrinhamento/solicitar", json={"padrinho_id": 9999, "afilhado_id": carlos.id})
        assert r.status_code == 404

    def test_solicitar_afilhado_inexistente_404(self, alice):
        r = client.post("/apadrinhamento/solicitar", json={"padrinho_id": alice.id, "afilhado_id": 9999})
        assert r.status_code == 404

    def test_aceitar_apadrinhamento(self, alice, carlos):
        sol = client.post("/apadrinhamento/solicitar", json={"padrinho_id": alice.id, "afilhado_id": carlos.id}).json()
        r = client.patch(f"/apadrinhamento/{sol['apadrinhamento_id']}/aceitar")
        assert r.status_code == 200
        assert r.json()["status"] == "aceito"

    def test_aceitar_apadrinhamento_inexistente_404(self):
        assert client.patch("/apadrinhamento/9999/aceitar").status_code == 404

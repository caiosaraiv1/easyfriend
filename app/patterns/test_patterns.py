"""
tests/test_patterns.py
Smoke tests dos padrões Observer e Strategy.
Rodar com: pytest -v
"""

import pytest
from patterns.observer import (
    Evento, EventoSubject,
    PushNotifier, EmailNotifier, BadgeNotifier,
)
from patterns.strategy import (
    Usuario, Evento as EventoAgenda, Consulta,
    BuscaContext,
    BuscaPorIdioma, BuscaPorProximidade,
    BuscaPorTipoEvento, BuscaPorPaisOrigem,
    criterio_para_strategy,
)


# ---------------------------------------------------------------------------
# Fixtures compartilhadas
# ---------------------------------------------------------------------------

@pytest.fixture
def usuarios():
    return [
        Usuario(1, "Alice",  "ja", "Japão",  lat=-23.550, lon=-46.633),
        Usuario(2, "Carlos", "pt", "Brasil", lat=-23.560, lon=-46.640),
        Usuario(3, "Bob",    "en", "EUA",    lat=-23.548, lon=-46.638),
        Usuario(4, "Sakura", "ja", "Japão",  lat=-23.552, lon=-46.631),
        Usuario(5, "Maria",  "pt", "Brasil", lat=-24.000, lon=-47.000),  # longe
    ]

@pytest.fixture
def eventos():
    return [
        EventoAgenda(1, "Festival de Sushi",     "gastronomia", "ja", -23.550, -46.633),
        EventoAgenda(2, "Feira Brasileira",       "gastronomia", "pt", -23.560, -46.640),
        EventoAgenda(3, "Show de Jazz",           "musica",      "en", -23.548, -46.638),
        EventoAgenda(4, "Concerto de J-Pop",      "musica",      "ja", -24.000, -47.000),
    ]


# ===========================================================================
# OBSERVER
# ===========================================================================

class _SubjectConcreto(EventoSubject):
    """Subject mínimo para os testes — simula RadarService ou ChatService."""
    def publicar(self, tipo: str, payload: dict):
        self.notificar(Evento(tipo=tipo, payload=payload))


def test_push_notifier_nao_lanca_excecao(capsys):
    """PushNotifier deve imprimir sem lançar erro."""
    notifier = PushNotifier()
    evento = Evento(tipo="match_criado", payload={"usuario_id": 1, "email": "a@b.com"})
    notifier.atualizar(evento)
    saida = capsys.readouterr().out
    assert "PushNotifier" in saida


def test_email_notifier_nao_lanca_excecao(capsys):
    """EmailNotifier deve imprimir sem lançar erro."""
    notifier = EmailNotifier()
    evento = Evento(tipo="match_criado", payload={"usuario_id": 1, "email": "a@b.com"})
    notifier.atualizar(evento)
    saida = capsys.readouterr().out
    assert "EmailNotifier" in saida


def test_badge_notifier_incrementa_contador():
    """BadgeNotifier deve incrementar o contador a cada evento."""
    notifier = BadgeNotifier()
    evento = Evento(tipo="match_criado", payload={"usuario_id": 42})
    notifier.atualizar(evento)
    notifier.atualizar(evento)
    assert notifier.contador("42") == 2


def test_todos_observers_sao_notificados(capsys):
    """Ao publicar um evento, todos os observers inscritos devem ser acionados."""
    subject = _SubjectConcreto()
    push  = PushNotifier()
    email = EmailNotifier()
    badge = BadgeNotifier()

    subject.inscrever(push)
    subject.inscrever(email)
    subject.inscrever(badge)

    subject.publicar("match_criado", {"usuario_id": 1, "email": "alice@easyfriend.app"})

    saida = capsys.readouterr().out
    assert "PushNotifier"  in saida
    assert "EmailNotifier" in saida
    assert "BadgeNotifier" in saida


def test_remover_observer_nao_recebe_mais(capsys):
    """Observer removido não deve receber eventos futuros."""
    subject = _SubjectConcreto()
    push = PushNotifier()

    subject.inscrever(push)
    subject.remover(push)
    subject.publicar("match_criado", {"usuario_id": 1})

    saida = capsys.readouterr().out
    assert "PushNotifier" not in saida


def test_sem_observers_nao_lanca_excecao():
    """Notificar sem nenhum observer inscrito não deve lançar erro."""
    subject = _SubjectConcreto()
    subject.publicar("match_criado", {"usuario_id": 1})  # não deve explodir


# ===========================================================================
# STRATEGY
# ===========================================================================

def test_busca_por_idioma(usuarios):
    """Deve retornar apenas usuários com idioma 'ja'."""
    ctx = BuscaContext(BuscaPorIdioma())
    resultado = ctx.executar(Consulta(valor="ja"), usuarios)
    assert len(resultado.itens) == 2
    assert all(u.idioma == "ja" for u in resultado.itens)
    assert resultado.criterio_usado == "idioma"


def test_busca_por_pais_origem(usuarios):
    """Deve retornar apenas usuários do Brasil."""
    ctx = BuscaContext(BuscaPorPaisOrigem())
    resultado = ctx.executar(Consulta(valor="Brasil"), usuarios)
    assert len(resultado.itens) == 2
    assert all(u.pais_origem == "Brasil" for u in resultado.itens)


def test_busca_por_proximidade_inclui_proximos(usuarios):
    """Usuários dentro do raio devem aparecer; os de fora não."""
    ctx = BuscaContext(BuscaPorProximidade())
    # Maria está em -24.000, -47.000 — longe demais para raio de 5 km
    resultado = ctx.executar(Consulta(valor="", lat=-23.550, lon=-46.633, raio_km=5), usuarios)
    ids = [u.id for u in resultado.itens]
    assert 5 not in ids          # Maria deve ficar de fora
    assert len(resultado.itens) >= 1


def test_busca_por_tipo_evento(eventos):
    """Deve retornar apenas eventos do tipo 'gastronomia'."""
    ctx = BuscaContext(BuscaPorTipoEvento())
    resultado = ctx.executar(Consulta(valor="gastronomia"), eventos)
    assert len(resultado.itens) == 2
    assert all(e.tipo == "gastronomia" for e in resultado.itens)
    assert resultado.criterio_usado == "tipo_evento"


def test_trocar_criterio_em_runtime(usuarios):
    """BuscaContext deve trocar de estratégia sem alterar nenhuma classe existente."""
    ctx = BuscaContext(BuscaPorIdioma())
    r1 = ctx.executar(Consulta(valor="ja"), usuarios)

    ctx.definir_criterio(BuscaPorPaisOrigem())
    r2 = ctx.executar(Consulta(valor="Brasil"), usuarios)

    assert r1.criterio_usado == "idioma"
    assert r2.criterio_usado == "pais_origem"
    assert r1.itens != r2.itens


def test_criterio_para_strategy_valido():
    """criterio_para_strategy deve retornar a estratégia correta pelo nome."""
    assert isinstance(criterio_para_strategy("idioma"),      BuscaPorIdioma)
    assert isinstance(criterio_para_strategy("proximidade"), BuscaPorProximidade)
    assert isinstance(criterio_para_strategy("tipo"),        BuscaPorTipoEvento)
    assert isinstance(criterio_para_strategy("pais_origem"), BuscaPorPaisOrigem)


def test_criterio_para_strategy_invalido():
    """Critério inexistente deve lançar ValueError."""
    with pytest.raises(ValueError):
        criterio_para_strategy("criterio_que_nao_existe")


def test_context_sem_criterio_lanca_erro():
    """Executar BuscaContext sem definir critério deve lançar RuntimeError."""
    ctx = BuscaContext()
    with pytest.raises(RuntimeError):
        ctx.executar(Consulta(valor="pt"), [])

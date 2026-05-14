"""
patterns/strategy.py
EasyFriend – Padrão Strategy
Permite trocar o critério de busca em tempo de execução, sem if/else nos services.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2
from typing import Any


# ---------------------------------------------------------------------------
# Estruturas de dados simples
# ---------------------------------------------------------------------------

@dataclass
class Usuario:
    id: int
    nome: str
    idioma: str        # ex: "pt", "en", "ja"
    pais_origem: str   # ex: "Brasil", "Japão"
    lat: float         # latitude
    lon: float         # longitude


@dataclass
class Evento:
    id: int
    titulo: str
    tipo: str          # ex: "gastronomia", "musica", "esporte"
    idioma: str        # idioma predominante do evento
    lat: float
    lon: float


@dataclass
class Consulta:
    """Parâmetros que o cliente (iOS) envia ao escolher um filtro."""
    valor: str          # valor principal do filtro (ex: idioma, tipo, país)
    lat: float = 0.0    # coordenadas do usuário solicitante
    lon: float = 0.0
    raio_km: float = 10.0


@dataclass
class Resultado:
    itens: list[Any]
    criterio_usado: str

    def __str__(self) -> str:
        nomes = [getattr(i, "nome", None) or getattr(i, "titulo", str(i)) for i in self.itens]
        return f"[{self.criterio_usado}] {len(self.itens)} resultado(s): {nomes}"


# ---------------------------------------------------------------------------
# Interface Strategy
# ---------------------------------------------------------------------------

class CriterioBuscaStrategy(ABC):
    """
    Interface Strategy.
    Toda estratégia de busca implementa um único método: `aplicar`.
    """

    @abstractmethod
    def aplicar(self, consulta: Consulta, dados: list[Any]) -> Resultado:
        """
        Filtra `dados` de acordo com a lógica desta estratégia.

        Args:
            consulta: parâmetros vindos da tela do usuário.
            dados:    lista de Usuario ou Evento a ser filtrada.

        Returns:
            Resultado com os itens correspondentes e o nome do critério.
        """


# ---------------------------------------------------------------------------
# Estratégias concretas
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em km entre dois pontos geográficos (fórmula de Haversine)."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


class BuscaPorProximidade(CriterioBuscaStrategy):
    """
    Filtra usuários ou eventos dentro de `consulta.raio_km` km
    a partir das coordenadas do solicitante.
    """

    def aplicar(self, consulta: Consulta, dados: list[Any]) -> Resultado:
        filtrados = [
            item for item in dados
            if _haversine_km(consulta.lat, consulta.lon, item.lat, item.lon) <= consulta.raio_km
        ]
        return Resultado(itens=filtrados, criterio_usado="proximidade")


class BuscaPorIdioma(CriterioBuscaStrategy):
    """Filtra pelo idioma falado pelo usuário (ou do evento)."""

    def aplicar(self, consulta: Consulta, dados: list[Any]) -> Resultado:
        filtrados = [item for item in dados if item.idioma.lower() == consulta.valor.lower()]
        return Resultado(itens=filtrados, criterio_usado="idioma")


class BuscaPorTipoEvento(CriterioBuscaStrategy):
    """Filtra eventos da Agenda pela categoria (gastronomia, música, esporte…)."""

    def aplicar(self, consulta: Consulta, dados: list[Any]) -> Resultado:
        filtrados = [item for item in dados if item.tipo.lower() == consulta.valor.lower()]
        return Resultado(itens=filtrados, criterio_usado="tipo_evento")


class BuscaPorPaisOrigem(CriterioBuscaStrategy):
    """Filtra usuários pelo país de origem."""

    def aplicar(self, consulta: Consulta, dados: list[Any]) -> Resultado:
        filtrados = [
            item for item in dados
            if item.pais_origem.lower() == consulta.valor.lower()
        ]
        return Resultado(itens=filtrados, criterio_usado="pais_origem")


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------

class BuscaContext:
    """
    Mantém a estratégia ativa e delega a execução a ela.
    O service chama `definir_criterio` quando o usuário troca o filtro na tela;
    depois chama `executar` — sem nenhum if/else espalhado no código.
    """

    def __init__(self, criterio: CriterioBuscaStrategy | None = None) -> None:
        self._criterio: CriterioBuscaStrategy | None = criterio

    def definir_criterio(self, criterio: CriterioBuscaStrategy) -> None:
        """Troca a estratégia em tempo de execução."""
        self._criterio = criterio

    def executar(self, consulta: Consulta, dados: list[Any]) -> Resultado:
        """Delega a filtragem à estratégia atual."""
        if self._criterio is None:
            raise RuntimeError("Nenhum critério de busca definido em BuscaContext.")
        return self._criterio.aplicar(consulta, dados)


# ---------------------------------------------------------------------------
# Mapeamento nome → estratégia (usado pelos endpoints FastAPI)
# ---------------------------------------------------------------------------

CRITERIOS: dict[str, CriterioBuscaStrategy] = {
    "proximidade": BuscaPorProximidade(),
    "idioma":      BuscaPorIdioma(),
    "tipo":        BuscaPorTipoEvento(),
    "pais_origem": BuscaPorPaisOrigem(),
}


def criterio_para_strategy(nome: str) -> CriterioBuscaStrategy:
    """
    Converte o parâmetro de query string em uma instância de estratégia.
    Lança ValueError se o critério não existir, evitando if/else nos services.
    """
    try:
        return CRITERIOS[nome.lower()]
    except KeyError:
        raise ValueError(f"Critério desconhecido: '{nome}'. Opções: {list(CRITERIOS)}")


# ---------------------------------------------------------------------------
# Demo rápida (python -m patterns.strategy)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    usuarios = [
        Usuario(1, "Alice",   "pt", "Brasil", lat=-23.55, lon=-46.63),
        Usuario(2, "Kenji",   "ja", "Japão",  lat=-23.56, lon=-46.64),
        Usuario(3, "Bob",     "en", "EUA",    lat=-23.60, lon=-46.70),
        Usuario(4, "Sakura",  "ja", "Japão",  lat=-23.58, lon=-46.65),
        Usuario(5, "Carlos",  "pt", "Brasil", lat=-24.00, lon=-47.00),
    ]

    eventos = [
        Evento(1, "Festival de Sushi",    "gastronomia", "ja", -23.55, -46.63),
        Evento(2, "Show de Jazz",          "musica",      "en", -23.56, -46.64),
        Evento(3, "Feira Brasileira",      "gastronomia", "pt", -23.57, -46.65),
        Evento(4, "Concerto de J-Pop",     "musica",      "ja", -24.00, -47.00),
    ]

    ctx = BuscaContext()

    print("=== Por idioma (ja) ===")
    ctx.definir_criterio(BuscaPorIdioma())
    print(ctx.executar(Consulta(valor="ja"), usuarios))

    print("\n=== Por país de origem (Brasil) ===")
    ctx.definir_criterio(BuscaPorPaisOrigem())
    print(ctx.executar(Consulta(valor="Brasil"), usuarios))

    print("\n=== Por proximidade (raio 5 km a partir de -23.55, -46.63) ===")
    ctx.definir_criterio(BuscaPorProximidade())
    print(ctx.executar(Consulta(valor="", lat=-23.55, lon=-46.63, raio_km=5), usuarios))

    print("\n=== Por tipo de evento (gastronomia) ===")
    ctx.definir_criterio(BuscaPorTipoEvento())
    print(ctx.executar(Consulta(valor="gastronomia"), eventos))

    print("\n=== Usando criterio_para_strategy('idioma') ===")
    ctx.definir_criterio(criterio_para_strategy("idioma"))
    print(ctx.executar(Consulta(valor="pt"), usuarios))
